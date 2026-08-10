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
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
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
        model = req_model or "deepseek-chat"
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
        f"[来源{i + 1}]（{r.get('section_path', r['section'])}）: {r['text']}" for i, r in enumerate(results)
    )

    # ---- 组装消息（§7.2，多轮最多 6 轮 FR-QA-05）----
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
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
            return FileResponse(file)
        return FileResponse(config.FRONTEND_DIST / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
