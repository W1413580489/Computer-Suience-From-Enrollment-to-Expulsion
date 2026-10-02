# -*- coding: utf-8 -*-
"""
XKZ-Agent 后端 API 网关（M2）
- POST /api/ask          提问（SSE 流式，BYOK 转发，平台 Key 兜底 + IP 限额）
- POST /api/verify       测试用户 Key 有效性
- POST /api/feedback     点赞/点踩反馈
- GET  /api/hot_questions 高频问题
- GET  /api/health       健康检查
- GET  /api/nav_config   导航配置
- GET  /api/news         校园动态
- GET  /api/changelog    更新日志
- /*                   前端静态资源（frontend/dist，SPA fallback）

安全约束（§2.3）：用户 Key 只用于本次转发，不写日志、不落盘；问答日志只记脱敏信息。
"""
import hashlib
import json
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

import config
import ratelimit
from retrieval import Retriever

app = FastAPI(title="XKZ-Agent API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

TZ = timezone(timedelta(hours=8))


# ---------- 数据读取工具 ----------
def _read_json(path: Path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _append_log(record: dict):
    """脱敏日志：不含问题原文、不含 Key（FR-FB-03 / §2.3）。"""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.ANSWERS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _q_hash(question: str) -> str:
    return hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()[:16]


def _now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


# ---------- 请求模型 ----------
class AskRequest(BaseModel):
    question: str
    session_id: str | None = None
    history: list[dict] | None = None
    api_key: str | None = None
    provider: str | None = "deepseek"
    base_url: str | None = None
    model: str | None = None


class VerifyRequest(BaseModel):
    api_key: str
    provider: str | None = "deepseek"
    base_url: str | None = None
    model: str | None = None


class FeedbackRequest(BaseModel):
    q_hash: str
    feedback: str            # up | down
    reason: str | None = None
    session_id: str | None = None


# ---------- 服务商解析 ----------
def _resolve_upstream(req_provider: str | None, req_base_url: str | None,
                      req_model: str | None, api_key: str | None):
    """返回 (base_url, model, key, use_platform_key)。自定义 base_url 优先。"""
    provider = (req_provider or "deepseek").lower()
    if req_base_url:  # custom
        base_url = req_base_url.rstrip("/")
        model = req_model or "deepseek-flash"
    else:
        preset = config.PROVIDERS.get(provider, config.PROVIDERS["deepseek"])
        base_url = preset["base_url"]
        model = req_model or preset["model"]
    if api_key:
        return base_url, model, api_key, False
    return config.PLATFORM_BASE_URL, config.PLATFORM_MODEL, config.PLATFORM_API_KEY, True


# ---------- SSE ----------
def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


# 复用连接、降低每次请求的 DNS/TLS 开销
_http_client = None
def _get_http():
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=config.REQUEST_TIMEOUT, write=10.0, pool=5.0),
            limits=httpx.Limits(max_keepalive_connections=4, max_connections=10),
        )
    return _http_client


@app.on_event("startup")
async def startup():
    """预热检索器（BM25 初始化 ~600ms，提前完成避免首个请求等待）。"""
    Retriever.get()
    print(f"Retriever ready ({Retriever.chunk_count()} chunks)")


# ---------- 接口 ----------
@app.get("/api/health")
async def health():
    return {"ok": True, "data": {
        "status": "up",
        "chunks": Retriever.chunk_count(),
        "platform_key_configured": bool(config.PLATFORM_API_KEY),
    }}


@app.get("/api/nav_config")
async def nav_config():
    return _read_json(config.NAV_CONFIG_FILE, {})


@app.get("/api/changelog")
async def changelog():
    return {"ok": True, "data": _read_json(config.CHANGELOG_FILE, [])}


@app.get("/api/hot_questions")
async def hot_questions():
    return {"ok": True, "data": _read_json(config.HOT_QUESTIONS_FILE, [])}


@app.get("/api/glossary")
async def glossary():
    return _read_json(config.GLOSSARY_FILE, {})


@app.post("/api/verify")
async def verify(req: VerifyRequest):
    provider = (req.provider or "deepseek").lower()
    if req.base_url:
        base_url = req.base_url.rstrip("/")
    else:
        base_url = config.PROVIDERS.get(provider, config.PROVIDERS["deepseek"])["base_url"]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {req.api_key}"},
            )
        if r.status_code == 200:
            model = req.model or config.PROVIDERS.get(provider, {}).get("model", "")
            return {"ok": True, "data": {"valid": True, "model": model}}
        if r.status_code in (401, 403):
            return {"ok": True, "data": {"valid": False, "message": "Key 无效或已过期"}}
        return {"ok": True, "data": {"valid": False, "message": f"服务商返回 HTTP {r.status_code}"}}
    except httpx.RequestError as e:
        return {"ok": False, "error": {"code": "PROVIDER_DOWN", "message": f"无法连接服务商：{type(e).__name__}"}}


@app.post("/api/feedback")
async def feedback(req: FeedbackRequest):
    if req.feedback not in ("up", "down"):
        return JSONResponse({"ok": False, "error": {"code": "BAD_FEEDBACK", "message": "feedback 必须为 up|down"}}, status_code=400)
    _append_log({
        "type": "feedback",
        "ts": _now(),
        "q_hash": req.q_hash,
        "feedback": req.feedback,
        "reason": req.reason,
        "session_id": req.session_id,
    })
    return {"ok": True}


@app.post("/api/ask")
async def ask(req: AskRequest, request: Request):
    question = (req.question or "").strip()
    if not question:
        return JSONResponse({"ok": False, "error": {"code": "EMPTY_QUESTION", "message": "问题不能为空"}}, status_code=400)

    use_byok = bool(req.api_key)
    ip = ratelimit.get_client_ip(request)

    # FR-BY-IP-08：带 api_key 的请求豁免全部 IP 限额
    if not use_byok:
        if not config.PLATFORM_API_KEY:
            return JSONResponse({"ok": False, "error": {
                "code": "NO_PLATFORM_KEY",
                "message": "平台免费额度未开放（服务端未配置兜底 Key），请在设置页填入自己的 API Key 使用",
            }}, status_code=503)
        allowed, reason = ratelimit.check_and_count(ip)
        if not allowed:
            return JSONResponse({"ok": False, "error": {"code": "RATE_LIMITED", "message": reason}}, status_code=429)

    # ---- 检索（FR-RT / FR-QA-03）----
    retriever = Retriever.get()
    results = retriever.search(question)
    # v3: 动态 System Prompt —— 根据意图分类追加风格指令
    intent = retriever.classify_intent(question)
    system_prompt = config.SYSTEM_PROMPT + config.INTENT_PROMPTS.get(intent, "")
    if not retriever.is_relevant(question, results):
        async def no_content():
            yield _sse({"type": "start"})
            yield _sse({"type": "error", "code": "NO_CONTENT",
                        "message": "资料库未覆盖该问题，建议咨询学长学姐或学校官方渠道"})
            yield _sse({"type": "done"})
        return StreamingResponse(no_content(), media_type="text/event-stream")

    citations = [
        {"id": i + 1, "title": r.get("section_path", f"{r['doc']}-{r['section']}"),
         "url": r["source_url"],
         "excerpt": r["text"].split("\n")[0][:80]}
        for i, r in enumerate(results)
    ]

    ref_block = "\n".join(
        f"[来源{i + 1}]（{r.get('section_path', r['section'])}）: {r['text']}"
        + (f"\n[来源{i + 1}上下文] {r['parent_context']}" if r.get("parent_context") else "")
        for i, r in enumerate(results)
    )

    # ---- 组装消息（§7.2，多轮最多 6 轮 FR-QA-05）----
    messages = [{"role": "system", "content": system_prompt}]
    history = (req.history or [])[-config.MAX_HISTORY_ROUNDS * 2:]
    for h in history:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": f"<参考资料>\n{ref_block}\n</参考资料>\n\n问题：{question}"})

    base_url, model, key, use_platform = _resolve_upstream(
        req.provider, req.base_url, req.model, req.api_key)

    start_ts = time.time()
    hit_docs = sorted({r["doc"] for r in results})

    async def stream():
        tokens_in = tokens_out = 0
        yielded_error = False
        try:
            yield _sse({"type": "start"})
            yield _sse({"type": "citations", "citations": citations})
            client = _get_http()
            async with client.stream(
                    "POST",
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": model, "messages": messages, "stream": True,
                          "stream_options": {"include_usage": True}},
                ) as resp:
                    if resp.status_code in (401, 403):
                        yielded_error = True
                        yield _sse({"type": "error", "code": "KEY_INVALID",
                                    "message": "Key 失效，请到设置页更新或切换为免费模式"})
                        return
                    if resp.status_code == 429:
                        yielded_error = True
                        yield _sse({"type": "error", "code": "PROVIDER_RATE_LIMITED",
                                    "message": "服务商限流，请稍后再试"})
                        return
                    if resp.status_code != 200:
                        yielded_error = True
                        yield _sse({"type": "error", "code": "PROVIDER_DOWN",
                                    "message": f"模型服务暂时不可用（HTTP {resp.status_code}），请稍后再试"})
                        return
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
                        usage = data.get("usage")
                        if usage:
                            tokens_in = usage.get("prompt_tokens", tokens_in)
                            tokens_out = usage.get("completion_tokens", tokens_out)
                        for choice in data.get("choices", []):
                            delta = choice.get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield _sse({"type": "token", "content": content})
            yield _sse({"type": "done", "usage": {"tokens_in": tokens_in, "tokens_out": tokens_out}})
        except httpx.RequestError:
            yielded_error = True
            yield _sse({"type": "error", "code": "PROVIDER_DOWN",
                        "message": "无法连接模型服务，请检查网络或稍后再试"})
        finally:
            # 脱敏日志：只记 hash / 耗时 / 命中文档 / 是否平台 Key（FR-FB-03）
            _append_log({
                "type": "ask",
                "ts": _now(),
                "q_hash": _q_hash(question),
                "latency_ms": int((time.time() - start_ts) * 1000),
                "hit_docs": hit_docs,
                "use_platform_key": use_platform,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "error": yielded_error,
                "session_id": req.session_id,
            })

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


# ---------- 前端静态托管（SPA fallback）----------
# SEO：前端是单份 index.html 的 SPA，若所有路由都返回同一份 head 信号，
# 搜索引擎会把 /faq、/about 等 URL 视作首页副本，canonical 也会指向首页。
# 这里按路由改写 head 中的 canonical / title / description / og:*，
# 让每个 URL 自带自指的规范化信号（前端结构与用户所见完全不变）。
SITE_ORIGIN = "https://jnuxky.xyz"
DEFAULT_TITLE = "信科院智能助手｜暨南大学 AI 教学与学习助手"
DEFAULT_DESC = (
    "信科院智能助手：暨南大学信科院学生王叔发起的学习与 AI 工具站，"
    "内置校园 RAG 问答与 AI 项目制导师教学引擎，大学发展路线图攻略。"
)

# path -> (title, description)
ROUTE_SEO = {
    "/": (DEFAULT_TITLE, DEFAULT_DESC),
    "/guides": (
        "攻略｜信科院智能助手",
        "暨南大学信科院成长攻略合集：常用链接、新生指南、大学政策简解、学生组织、学术与就业发展规划、竞赛指导。",
    ),
    "/roadmap": (
        "成长路线图｜信科院智能助手",
        "大学四年成长路线图：从入学到毕业的关键节点、学业规划与能力积累路径。",
    ),
    "/teach": (
        "AI 项目制教学｜信科院智能助手三门课程",
        "AI 项目制导师：套壳聊天机器人、GitHub 项目分析 Agent、MCP 项目记忆服务三门课程，教你从零把 AI 用进真实项目。",
    ),
    "/chat": (
        "校园问答｜信科院智能助手",
        "基于暨南大学信科院学习指南知识库的智能问答，覆盖选课、绩点、保研、竞赛、校园生活等常见问题。",
    ),
    "/appendix": (
        "附录｜信科院智能助手",
        "资源集合库：竞赛战队、学习笔记、工具教程与同学共创的补充文档索引。",
    ),
    "/glossary": (
        "黑话辞典｜信科院智能助手",
        "校园术语百科：绩点、综测、保研、选课等暨南大学校园黑话速查。",
    ),
    "/quest": (
        "新手任务｜信科院智能助手",
        "新手任务清单：跟着步骤完成入学准备与校园系统上手。",
    ),
    "/resources": (
        "资源中心｜信科院智能助手",
        "常用网站与学习资源汇总：教务系统、图书馆、校园网等入口。",
    ),
    "/calendar": (
        "校历｜信科院智能助手",
        "暨南大学校历：学期起止、考试周与假期安排。",
    ),
    "/changelog": (
        "更新日志｜信科院智能助手",
        "信科院智能助手更新日志：功能迭代与内容更新记录。",
    ),
    "/about": (
        "关于信科院智能助手｜创建者王叔与项目说明",
        "关于信科院智能助手：由暨南大学信息科学技术学院学生「王叔」独立开发维护的学习与 AI 工具站，非学校官方平台。",
    ),
    "/faq": (
        "常见问题｜信科院智能助手是谁做的、怎么用",
        "信科院智能助手常见问题：网站是什么、谁创建了它、王叔是谁、有哪些课程、谁可以使用、是否收费、是否为学校官方平台。",
    ),
    "/thanks": (
        "鸣谢｜信科院智能助手",
        "贡献者档案馆：感谢为信科院智能助手提供文档、经验与内容的同学与前辈。",
    ),
}

# ---------- 结构化数据（按路由注入）----------
# Google / Bing 都要求结构化数据真实代表页面可见内容，而不再依赖全站共用一份图。
# 因此 index.html 里不再写死 WebSite + Organization + Course×3 + FAQPage，
# 改为只声明「本路由页面上确有对应内容」的实体：
#     /        → WebSite + Organization（含 founder 王叔）
#     /teach   → WebSite + Course×3（课程总览页）
#     /faq     → WebSite + FAQPage（问答正文即页面可见的 9 问 9 答）
#     /about   → WebSite + ProfilePage（页面主体即创建者王叔介绍）
# 其余页面只带站点级 WebSite。
KNOWN_ROUTES = set(ROUTE_SEO) | {"/splash", "/login"}

LD_WEBSITE = {
    "@type": "WebSite",
    "name": "信科院智能助手",
    "alternateName": "XKZ-Agent",
    "url": SITE_ORIGIN + "/",
    "inLanguage": "zh-CN",
    "description": DEFAULT_DESC,
}

# 实体消歧：向搜索引擎声明「信科院智能助手」「王叔」在站外的等价身份
GITHUB_PROFILE = "https://github.com/W1413580489"
GITHUB_REPO = GITHUB_PROFILE + "/Computer-Suience-From-Enrollment-to-Expulsion"

LD_ORGANIZATION = {
    "@type": "Organization",
    "name": "信科院智能助手",
    "url": SITE_ORIGIN + "/",
    "sameAs": [GITHUB_REPO],
    "founder": {
        "@type": "Person",
        "name": "王叔",
        "jobTitle": "创建者与维护者",
        "url": SITE_ORIGIN + "/about",
        "sameAs": [GITHUB_PROFILE],
    },
    "description": "由暨南大学信息科学技术学院学生创建的开放式学习社区，非学校官方平台。",
}

LD_COURSES = [
    {
        "@type": "Course",
        "name": "课程 01 · 套壳聊天机器人",
        "description": "从零搭建一个可对话的聊天机器人，掌握 API 调用与提示词工程入门。",
        "provider": {"@type": "Organization", "name": "信科院智能助手", "url": SITE_ORIGIN + "/"},
        "url": SITE_ORIGIN + "/teach",
    },
    {
        "@type": "Course",
        "name": "课程 02 · GitHub 项目分析 Agent",
        "description": "构建能够分析 GitHub 项目的 Agent，把第一段项目经历写进简历。",
        "provider": {"@type": "Organization", "name": "信科院智能助手", "url": SITE_ORIGIN + "/"},
        "url": SITE_ORIGIN + "/teach",
    },
    {
        "@type": "Course",
        "name": "课程 03 · MCP 项目记忆服务",
        "description": "基于 MCP 打造带记忆的项目服务，体验真实工程项目开发流程。",
        "provider": {"@type": "Organization", "name": "信科院智能助手", "url": SITE_ORIGIN + "/"},
        "url": SITE_ORIGIN + "/teach",
    },
]

# 答案文案与 FaqView.vue 的可见正文逐句对齐，避免「标记了页面上没有的内容」
LD_FAQ = {
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "信科院智能助手是什么？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "信科院智能助手：暨南大学信科院学生王叔发起的学习与 AI 工具站，内置校园 RAG 问答与 AI 项目制导师教学引擎，大学发展路线图攻略。",
            },
        },
        {
            "@type": "Question",
            "name": "谁创建了信科院智能助手？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "信科院智能助手由暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生「王叔」创建并维护，是非学校官方的学生发起项目。",
            },
        },
        {
            "@type": "Question",
            "name": "王叔是谁？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "「王叔」是信科院智能助手（jnuxky.xyz）的创建者与维护者，暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生。他最初为解答同学的疑问写了一部学习指南，因同学反馈「文字太多、翻不动」，又在此基础上做了 RAG 知识库问答助手和 AI 项目导师，陆续开放给全校同学使用。",
            },
        },
        {
            "@type": "Question",
            "name": "王叔和信科院智能助手是什么关系？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "王叔是信科院智能助手的创建者和主要内容贡献者：他发起了这个网站、撰写了站内的学习指南，并主导 RAG 问答助手与 AI 项目制教学的开发与维护。",
            },
        },
        {
            "@type": "Question",
            "name": "有哪些课程？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "目前开设三门 AI 项目制课程，把「怎么教 AI 写代码」变成可以对照标准、被逐条评审的练手课程：课程 01 · 套壳聊天机器人：从零搭建一个可对话的聊天机器人，掌握 API 调用与提示词工程入门。课程 02 · GitHub 项目分析 Agent：构建能够分析 GitHub 项目的 Agent，把第一段项目经历写进简历。课程 03 · MCP 项目记忆服务：基于 MCP 打造带记忆的项目服务，体验真实工程项目开发流程。",
            },
        },
        {
            "@type": "Question",
            "name": "谁可以使用？",
            "acceptedAnswer": {"@type": "Answer", "text": "面向暨南大学同学的开放式学习社区，全校同学均可免费使用。"},
        },
        {
            "@type": "Question",
            "name": "收费吗？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "免费。支持自带大模型 API Key（BYOK）免费提问，未配置 Key 的用户每日享有限量免费额度。受服务器资源限制，免费额度有限，建议配置自己的 API Key 以获得更稳定完整的体验。",
            },
        },
        {
            "@type": "Question",
            "name": "这是学校官方平台吗？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "不是。平台非学校官方，是面向暨南大学同学的开放式学习社区，网站文档与功能均由学生独立开发维护，贡献者名单见网站「鸣谢」页。",
            },
        },
        {
            "@type": "Question",
            "name": "网站主要服务什么人？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "信科院智能助手主要服务暨南大学在校学生，为他们提供计算机学习指南、AI 工具与项目制教学内容；站内内容开放，其他院校同学同样可以参考。",
            },
        },
    ],
}

LD_PROFILE = {
    "@type": "ProfilePage",
    "name": "关于信科院智能助手",
    "url": SITE_ORIGIN + "/about",
    "mainEntity": {
        "@type": "Person",
        "name": "王叔",
        "url": SITE_ORIGIN + "/about",
        "jobTitle": "信科院智能助手创建者与维护者",
        "sameAs": [GITHUB_PROFILE],
        "affiliation": {"@type": "Organization", "name": "暨南大学信息科学技术学院"},
        "description": "王叔，暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生，信科院智能助手（jnuxky.xyz）的创建者与维护者。",
    },
}

ROUTE_JSONLD = {
    "/": [LD_ORGANIZATION],
    "/teach": LD_COURSES,
    "/faq": [LD_FAQ],
    "/about": [LD_PROFILE],
}

# ---------- 静态正文直出（按路由替换）----------
# index.html 的 <div id="app"> 内有一段静态正文，供爬虫在 JS 执行前直接读取。
# 但若所有路由都返回同一段正文，而 <head> 的 title/description 各不相同，
# 搜索引擎会判定「元数据与可见内容不一致」，把其余页面当作首页的近重复副本
# （实测：/teach、/faq 长期停留在「已发现未抓取」）。
# 这里按路由替换两个 XKZ_STATIC 标记之间的正文，保证 head 说什么、body 就有什么。
# 正文内容取自 LD_COURSES / LD_FAQ 等同一份数据源，避免两处文案漂移。
_STATIC_RE = re.compile(r"<!--XKZ_STATIC_BEGIN-->.*?<!--XKZ_STATIC_END-->", re.S)

_ST_LEAD = "margin:0 0 10px;font-size:13px;letter-spacing:0.22em;color:#ffd93d;"
_ST_H1 = "margin:0 0 14px;font-size:30px;line-height:1.35;font-weight:900;"
_ST_P = "margin:0 0 26px;max-width:720px;font-size:15px;line-height:1.9;color:#a8a8a8;"
_ST_CELL = "padding:18px;background:#16171b;border:1px solid #4c4c4c;border-left:3px solid #ffd93d;"


def _static_shell(inner: str) -> str:
    """包一层与 index.html 静态块同观感（zzz 夜间）的容器，并保留替换标记。"""
    return (
        "<!--XKZ_STATIC_BEGIN-->"
        '<div style="min-height:100vh;box-sizing:border-box;padding:56px 20px;'
        "font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif;"
        "color:#f5f5f5;"
        "background:radial-gradient(1200px 620px at 50% -12%,rgba(255,217,61,0.09),transparent 60%),#101114;"
        '"><div style="max-width:960px;margin:0 auto">'
        + inner
        + "</div></div><!--XKZ_STATIC_END-->"
    )


def _static_lead(route: str) -> str:
    """H1 + 概述段落，直接复用该路由的 SEO 标题与描述，确保与 head 完全一致。"""
    title, desc = ROUTE_SEO.get(route, (DEFAULT_TITLE, DEFAULT_DESC))
    return (
        f'<p style="{_ST_LEAD}">INFO SYSTEM · JNU 信科院智能助手</p>'
        f'<h1 style="{_ST_H1}">{title}</h1>'
        f'<p style="{_ST_P}">{desc}</p>'
    )


_STATIC_LINKS = (
    '<p style="margin:10px 0 0;font-size:13px;color:#7a7a7a">'
    '<a href="/" style="color:#00f0ff">首页</a><span style="margin:0 8px">·</span>'
    '<a href="/teach" style="color:#00f0ff">AI 项目制教学</a><span style="margin:0 8px">·</span>'
    '<a href="/faq" style="color:#00f0ff">常见问题</a><span style="margin:0 8px">·</span>'
    '<a href="/about" style="color:#00f0ff">关于我们</a><span style="margin:0 8px">·</span>'
    "本站为面向暨南大学同学的开放式学习社区，非学校官方平台。</p>"
)


def _static_cards(items: list) -> str:
    """items: [(小标签, 标题, 说明)] → 卡片栅格。"""
    cells = "".join(
        f'<div style="{_ST_CELL}">'
        f'<div style="font-size:12px;letter-spacing:0.1em;color:#ffd93d">{label}</div>'
        f'<div style="margin-top:6px;font-size:15px;font-weight:700">{heading}</div>'
        f'<div style="margin-top:8px;font-size:13px;line-height:1.7;color:#a8a8a8">{body}</div>'
        "</div>"
        for label, heading, body in items
    )
    return (
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px">'
        + cells
        + "</div>"
    )


def _static_teach() -> str:
    items = []
    for course in LD_COURSES:
        label, _, heading = course["name"].partition(" · ")
        items.append((label, heading, course["description"]))
    return _static_shell(
        _static_lead("/teach")
        + _static_cards(items)
        + '<p style="margin:22px 0 0;font-size:13px;line-height:1.9;color:#a8a8a8">'
        "信科院智能助手目前开设三门 AI 项目制课程：套壳聊天机器人、GitHub 项目分析 Agent、MCP 项目记忆服务。</p>"
        + _STATIC_LINKS
    )


def _static_faq() -> str:
    rows = "".join(
        '<div style="padding:16px 18px;background:#16171b;border:1px solid #4c4c4c;'
        'border-left:3px solid #ffd93d;margin-bottom:12px">'
        f'<div style="font-size:14px;font-weight:700;color:#ffd93d">{q["name"]}</div>'
        f'<div style="margin-top:8px;font-size:13px;line-height:1.9;color:#a8a8a8">{q["acceptedAnswer"]["text"]}</div>'
        "</div>"
        for q in LD_FAQ["mainEntity"]
    )
    return _static_shell(_static_lead("/faq") + rows + _STATIC_LINKS)


_ABOUT_FACTS = (
    ("站名", "信科院智能助手（项目代号 XKZ-Agent）"),
    ("创建者", "王叔 · 暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生"),
    ("网站性质", "由学生发起并独立维护的非官方学习与 AI 工具站"),
    ("主要内容", "学生指南、校园 RAG 问答、AI 工具、AI 项目制教学与项目实践"),
    ("服务对象", "暨南大学在校同学（信科院为主）"),
    ("官网", '<a href="https://jnuxky.xyz/" style="color:#00f0ff">https://jnuxky.xyz/</a>'),
    ("开源仓库", f'<a href="{GITHUB_REPO}" style="color:#00f0ff">GitHub · 信科院智能助手源码与文档</a>'),
)


def _static_about() -> str:
    rows = "".join(
        '<div style="font-size:13px;line-height:1.9;color:#a8a8a8">'
        f'<span style="color:#ffd93d;font-weight:700">{key}</span>　{value}</div>'
        for key, value in _ABOUT_FACTS
    )
    return _static_shell(
        _static_lead("/about")
        + '<div style="padding:18px 20px;background:#16171b;border:1px solid #4c4c4c;border-left:3px solid #ffd93d">'
        '<div style="font-size:15px;font-weight:700;color:#ffd93d;margin-bottom:10px">本站身份卡</div>'
        + rows
        + "</div>"
        + '<p style="margin:16px 0 0;font-size:13px;line-height:1.9;color:#a8a8a8">'
        "王叔，暨南大学信息科学技术学院计算机科学与技术专业 2022 级学生，信科院智能助手（jnuxky.xyz）的创建者与维护者。"
        "网站文档与功能均由学生独立开发维护，贡献者名单见网站「鸣谢」页。</p>"
        + _STATIC_LINKS
    )


def _static_generic(route: str) -> str:
    """其余已知路由：标题 + 描述 + 站内导航，避免与首页正文逐字重复。"""
    return _static_shell(_static_lead(route) + _STATIC_LINKS)


# 首页保持 index.html 自带的那段（含课程卡片），作为静态托管的兜底
ROUTE_STATIC_BODY = {"/teach": _static_teach(), "/faq": _static_faq(), "/about": _static_about()}
ROUTE_STATIC_BODY.update(
    {r: _static_generic(r) for r in ROUTE_SEO if r not in ("/", "/teach", "/faq", "/about")}
)

# 未知路由的极简 404 页：真实 404 状态码，不加载 SPA，
# 避免 /abc、/test123 这类路径被搜索引擎当成「200 的首页副本」。
NOT_FOUND_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="noindex" />
    <meta name="theme-color" content="#0A0A0A" />
    <title>页面不存在｜信科院智能助手</title>
  </head>
  <body style="margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:radial-gradient(1200px 620px at 50% -12%,rgba(255,217,61,0.09),transparent 60%),#101114;color:#f5f5f5;font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif;">
    <div style="max-width:520px;padding:40px 24px;text-align:center;">
      <p style="margin:0;font-size:13px;letter-spacing:0.2em;color:#ffd93d;">ERROR 404 · NOT FOUND</p>
      <h1 style="margin:14px 0 12px;font-size:26px;font-weight:900;">页面不存在</h1>
      <p style="margin:0 0 22px;font-size:14px;line-height:1.9;color:#a8a8a8;">
        该地址没有对应内容，可能已移动或从未存在。<br />本站为面向暨南大学同学的开放式学习社区，非学校官方平台。
      </p>
      <p style="margin:0;font-size:14px;">
        <a href="/" style="color:#00f0ff;">返回首页</a>
        <span style="margin:0 10px;color:#4c4c4c;">·</span>
        <a href="/faq" style="color:#00f0ff;">常见问题</a>
      </p>
    </div>
  </body>
</html>
"""


def _jsonld_block(route: str) -> str:
    """该路由对应的结构化数据图：站点级 WebSite + 本页可见内容对应的实体。"""
    graph = [LD_WEBSITE, *ROUTE_JSONLD.get(route, ())]
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return f'    <script type="application/ld+json">{payload}</script>'


# 逐个标签替换：index.html 中 description / og:description 是多行写法，
# 用 \s+ 匹配缩进换行，仅替换第一个命中项。
_SEO_SUBS = (
    (re.compile(r"<title>.*?</title>", re.S), "<title>{title}</title>"),
    (
        re.compile(r'<meta\s+name="description"\s+content="[^"]*"\s*/?>'),
        '<meta name="description" content="{desc}" />',
    ),
    (
        re.compile(r'<meta\s+property="og:title"\s+content="[^"]*"\s*/?>'),
        '<meta property="og:title" content="{title}" />',
    ),
    (
        re.compile(r'<meta\s+property="og:description"\s+content="[^"]*"\s*/?>'),
        '<meta property="og:description" content="{desc}" />',
    ),
    (
        re.compile(r'<meta\s+property="og:url"\s+content="[^"]*"\s*/?>'),
        '<meta property="og:url" content="{canonical}" />',
    ),
    (
        re.compile(r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>'),
        '<link rel="canonical" href="{canonical}" />',
    ),
)


def _normalize_route(request_path: str) -> str:
    """/faq/ 与 /faq 视为同一路由；根路径归一为 /。"""
    return "/" + request_path.strip("/")


def _inject_seo(html: str, route: str) -> str:
    hit = ROUTE_SEO.get(route)
    # /splash、/login 不对外收录，且不参与 SEO 注入；其余未命中路由表的路径
    # 已在 spa() 里直接返回 404，这里保留首页默认信号仅作兜底。
    title, desc = hit or (DEFAULT_TITLE, DEFAULT_DESC)
    canonical = SITE_ORIGIN + (route if hit else "/")
    values = {"title": title, "desc": desc, "canonical": canonical}
    for pattern, template in _SEO_SUBS:
        html = pattern.sub(template.format(**values), html, count=1)
    # 结构化数据同样按路由注入，只声明本页可见内容对应的实体
    html = html.replace("</head>", _jsonld_block(route) + "\n  </head>", 1)
    # 静态正文也按路由替换：head 的 title/description 必须与 body 可见正文一致，
    # 否则各路由的正文逐字相同，会被搜索引擎当作首页的近重复副本。
    body = ROUTE_STATIC_BODY.get(route)
    if body:
        html = _STATIC_RE.sub(lambda _m: body, html, count=1)
    return html


if config.FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/assets", StaticFiles(directory=config.FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        # 未匹配的 /api/* 返回 404 而不是 SPA 页面
        if full_path.startswith("api/"):
            return JSONResponse({"ok": False, "error": {"code": "NOT_FOUND", "message": "接口不存在"}}, status_code=404)
        file = config.FRONTEND_DIST / full_path
        if full_path and file.is_file():
            # dist 根下的非哈希文件（manifest.json 等）：允许短缓存
            return FileResponse(file, headers={"Cache-Control": "no-cache"})
        route = _normalize_route(full_path)
        # 未知路由返回真实 404：否则 /abc、/test123 这类路径会全部以 200 渲染首页，
        # 在搜索引擎侧形成大量「伪页面 / soft 404」。
        if route not in KNOWN_ROUTES:
            return HTMLResponse(NOT_FOUND_HTML, status_code=404, headers={"Cache-Control": "no-cache"})
        # SPA 入口：必须禁止缓存——发版后浏览器要立刻拿到新壳，
        # 否则旧 index.html 引用已被删除的旧 JS，或继续跑旧逻辑
        html = _inject_seo(
            (config.FRONTEND_DIST / "index.html").read_text(encoding="utf-8"),
            route,
        )
        return HTMLResponse(html, headers={"Cache-Control": "no-cache"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
