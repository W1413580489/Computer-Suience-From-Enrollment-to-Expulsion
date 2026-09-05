# -*- coding: utf-8 -*-
"""
AI Teaching Engine - 独立 FastAPI 应用

接口：
  - GET  /api/ai/config       返回可用的课程/项目/任务列表 + 模型配置（供测试页）
  - POST /api/ai/teach        核心辅导接口（BYOK + DeepSeek JSON 模式 + Pydantic 校验）
  - GET  /api/ai/health       健康检查

V1 独立运行在 8099 端口，不托管静态资源（测试页为独立 HTML，可本地直接打开）。
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from schemas import (AISession, DebuggerState, DebugPhase, Evidence, EvidenceType, Mode, ReviewRequest, TeachRequest)
from course_data import get_project, list_projects, get_task, get_rubrics, list_courses
from context_builder import build_context
from prompts import build_system_prompt, route_behavior, BEHAVIOR_LABELS
from llm_client import LLMClient, DEFAULT_MODEL, DEFAULT_BASE_URL, EngineError, ProviderError
from response_validator import validate
from code_evidence import build_code_evidence
from review import build_review_system_prompt, collect_evidence, evidence_precheck, evidence_text
import logs as logs_mod
import hint as hint_mod

app = FastAPI(title="AI Teaching Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

TZ = timezone(timedelta(hours=8))

# 会话缓存（进程内存，V1 够用；跨设备不持久）
_sessions: dict[str, "AISession"] = {}

# V1.5 Sprint 2：Evidence Store（进程内存，重启丢失）
_evidence_store: dict[str, list[Evidence]] = {}  # task_id -> [Evidence]


def store_evidence(ev: Evidence) -> None:
    key = ev.task_id
    if key not in _evidence_store:
        _evidence_store[key] = []
    _evidence_store[key].append(ev)


def get_evidence(task_id: str, rubric_id: str | None = None) -> list[Evidence]:
    evs = _evidence_store.get(task_id, [])
    if rubric_id:
        evs = [e for e in evs if e.rubric_id == rubric_id]
    return evs


def _now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Sprint 4：Debugger 多轮取证状态机
# ---------------------------------------------------------------------------
_PHASE_DESC = {
    DebugPhase.symptom: "收集症状",
    DebugPhase.evidence: "要求并等待学生提供证据",
    DebugPhase.narrow: "缩小排查范围",
    DebugPhase.verify: "请学生验证假设",
    DebugPhase.locate: "定位具体问题",
    DebugPhase.explain: "解释根因",
    DebugPhase.done: "已定位完成",
}


def render_debug_progress(ds: "DebuggerState") -> str:
    """把上一轮取证进度渲染成注入 Prompt 的文本。"""
    if ds.rounds == 0:
        return "首次进入调试，从收集症状开始。"
    lines = [f"已进行 {ds.rounds} 轮调试，当前阶段：{_PHASE_DESC.get(ds.phase, ds.phase.value)}。"]
    if ds.last_diagnostic_question:
        lines.append(f"你上一轮要求学生确认：{ds.last_diagnostic_question}")
    if ds.last_suspected_cause:
        lines.append(f"你上一轮怀疑的根因：{ds.last_suspected_cause}")
    lines.append(
        "请基于上述进度继续推进：若学生已回应上一条诊断问题，就据此推进下一步；"
        "不要原样重复上一轮的诊断问题，不要在没有新证据时反复要求同一条证据。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 系统错误隔离：上下文注入 + 错误分类漏斗
# ---------------------------------------------------------------------------
def system_error_note(sess: "AISession") -> str:
    """上一轮发生系统内部错误时，向本轮 Prompt 注入隔离声明，防止模型把系统故障
    归因为学生项目问题（配合 CORE_POLICY 铁律 7，属于上下文层的结构化隔离）。"""
    if not sess.last_system_error:
        return ""
    return (
        "\n\n【系统状态·重要】上一轮对话中出现了系统内部错误（"
        f"{sess.last_system_error}）。这是本平台/模型服务的故障，不是学生项目的问题。"
        "评审与辅导只能依据学生提交的真实证据（代码、部署地址、自述、CI 结论）；"
        "严禁把该系统错误当作学生项目的失败原因或“联调未通过”的证据。"
    )


def llm_error_response(e: Exception, review: bool = False) -> JSONResponse:
    """错误分类漏斗：所有 LLM 链路异常在此统一归类，系统错误永不进入学生评审结果。
    review=True 时返回评审链专用的 REVIEW_UNAVAILABLE 语义。"""
    if isinstance(e, PermissionError):
        return JSONResponse({"ok": False, "error": {"code": "KEY_INVALID", "message": str(e)}}, status_code=401)
    if isinstance(e, TimeoutError):
        return JSONResponse({"ok": False, "error": {"code": "RATE_LIMITED", "message": str(e)}}, status_code=429)
    if isinstance(e, EngineError):
        return JSONResponse({"ok": False, "error": {
            "code": "REVIEW_UNAVAILABLE" if review else "ENGINE_ERROR",
            "message": f"平台内部错误：{e}（系统故障，与你提交的项目无关）"}}, status_code=500)
    # ProviderError 及其它服务商侧故障
    return JSONResponse({"ok": False, "error": {
        "code": "REVIEW_UNAVAILABLE" if review else "PROVIDER_DOWN",
        "message": f"模型服务暂时不可用：{e}（系统故障，与你提交的项目无关，请稍后重试）"}}, status_code=502)


def update_debugger_state(ds: "DebuggerState", resp) -> "DebuggerState":
    """根据本轮 Debugger 输出更新取证状态（阶段推进）。"""
    ds.rounds += 1
    if resp.diagnostic_question:
        ds.last_diagnostic_question = resp.diagnostic_question
    if resp.suspected_cause:
        cause = resp.suspected_cause
        ds.last_suspected_cause = cause
        # 有了明确的怀疑根因 → 进入验证阶段；仍模糊则停留在取证
        if not any(mark in cause for mark in ("未确定", "尚不", "无法", "需要根据")):
            ds.phase = DebugPhase.verify
        elif ds.phase in (DebugPhase.symptom,):
            ds.phase = DebugPhase.evidence
    elif ds.phase == DebugPhase.symptom:
        ds.phase = DebugPhase.evidence
    return ds


# ---------------------------------------------------------------------------
# 模式链建议：指导中发现完成信号 → 建议提交验收（两模式闭环，切换不删对话）
# ---------------------------------------------------------------------------
_COMPLETION_SIGNALS = ["完成", "做好", "做完了", "提交", "验收", "跑通", "跑通了", "可以通过", "通过了"]


def compute_mode_advice(mode: str, req, task) -> dict | None:
    """确定性规则：仅指导模式触发——学生表达完成信号时建议提交验收。
    验收未通过 → 回指导，由前端在评审卡后给出提示，不在此重复。"""
    if mode != "tutor":
        return None
    ui = req.user_input or ""
    if not any(k in ui for k in _COMPLETION_SIGNALS):
        return None

    proj = get_project(req.project_id)
    stage_title = {s.id: s.title for s in proj.stages}

    def adv(m, reason, t):
        d = {"mode": m, "reason": reason,
             "task_id": t.id if t else None, "task_title": t.title if t else None}
        if t:
            d["task_stage_title"] = stage_title.get(t.stage_id, "")
            d["moving_task"] = False
        return d

    return adv("reviewer", "看起来完成了，切到「验收」对照标准逐条评审打分", task)


# ---------------------------------------------------------------------------
# 配置接口
# ---------------------------------------------------------------------------
@app.get("/api/ai/health")
async def health():
    return {"ok": True, "data": {
        "status": "up",
        "engine": "ai-teaching-engine",
        "model": DEFAULT_MODEL,
        "base_url": DEFAULT_BASE_URL,
    }}


@app.get("/api/ai/config")
async def config():
    return {"ok": True, "data": {
        "models": [
            {"model": "deepseek-v4-flash", "label": "DeepSeek V4 Flash（快速）"},
            {"model": "deepseek-v4-pro", "label": "DeepSeek V4 Pro（更稳）"},
        ],
        "modes": [m.value for m in Mode],
        "hint_levels": {str(k): v for k, v in {
            0: "仅引导", 1: "提示方向", 2: "思路步骤",
            3: "具体做法", 4: "答案片段", 5: "完整方案",
        }.items()},
        "courses": list_courses(),
        "projects": list_projects(),
    }}


# ---------------------------------------------------------------------------
# 核心辅导接口
# ---------------------------------------------------------------------------
@app.post("/api/ai/teach")
async def teach(req: TeachRequest, request: Request):
    # 校验参数
    if not req.task_id:
        return JSONResponse({"ok": False, "error": {"code": "NO_TASK", "message": "请先选择一个任务"}}, status_code=400)
    if not req.api_key:
        return JSONResponse({"ok": False, "error": {"code": "NO_API_KEY", "message": "需要提供 DeepSeek API Key（BYOK）"}}, status_code=400)
    if not req.user_input.strip():
        return JSONResponse({"ok": False, "error": {"code": "EMPTY_INPUT", "message": "请输入你要问的内容"}}, status_code=400)

    mode = req.mode.value if isinstance(req.mode, Mode) else req.mode
    task = get_task(req.task_id)
    if not task:
        return JSONResponse({"ok": False, "error": {"code": "BAD_TASK", "message": "任务不存在"}}, status_code=404)

    # 学生状态
    student = req.student
    if student is None:
        from schemas import Student
        student = Student(session_id=req.session_id or "anon")

    # 会话（单一连续对话流：会话身份 = 学生 + 任务；模式只是请求参数，切换不丢历史）
    sid = student.session_id or "anon"
    skey = f"{sid}:{req.task_id}"
    sess = _sessions.get(skey)
    if not sess or sess.task_id != req.task_id:
        sess = AISession(session_id=sid, student_id=sid,
                         task_id=req.task_id, mode=req.mode,
                         attempt_count=student.attempt_count.get(req.task_id, 0))
        _sessions[skey] = sess
    sess.mode = req.mode  # 记录最近一次使用的模式（不影响会话身份）

    # 指导模式内部行为路由（拆解/推进/调试，用户无感；调试状态机挂在行为上）
    behavior = ""
    if mode == "tutor":
        behavior = route_behavior(req.user_input, sess)

    # 组装上下文
    ctx = build_context(req, student)
    ctx.behavior = behavior

    # 调试行为：多轮取证状态注入（跨轮避免重复提问、逐步收敛）
    if behavior == "debug":
        if sess.debug_state is None:
            sess.debug_state = DebuggerState()
        ctx.debug_progress = render_debug_progress(sess.debug_state)

    # V2/V1.5 代码证据：若提供了 GitHub 仓库链接，拉取并注入（失败不阻塞主流程）
    evidence_status = {"status": "none"}
    if req.repo_url:
        cc = task.code_context if task else None
        ev = await build_code_evidence(req.repo_url, task_id=req.task_id, code_context=cc)
        if ev["ok"]:
            ctx.code_evidence = ev["evidence_text"]
            evidence_status = {
                "status": "ok", "repo": ev["repo"], "file_count": ev["file_count"],
                "key_files": [k["path"] for k in ev["key_files"]],
            }
        else:
            evidence_status = {"status": "error", "code": ev["code"],
                               "error": ev["error"], "repo": req.repo_url}

    # 组装 Prompt（含系统错误隔离声明：上一轮若有系统故障，本轮注入隔离说明）
    system_prompt = build_system_prompt(ctx, mode) + system_error_note(sess)

    history = (req.history or [])
    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-6:]:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": req.user_input})

    # 调用 LLM
    client = LLMClient(req.api_key, req.base_url, req.model)
    start_ts = time.time()
    try:
        resp = await client.teach(messages, req.mode)
    except (PermissionError, TimeoutError, EngineError, RuntimeError) as e:
        # 错误分类漏斗：系统错误记入会话标记（下一轮注入隔离声明），绝不进入学生评审结果
        if not isinstance(e, PermissionError):
            sess.last_system_error = str(e)[:200]
        return llm_error_response(e)
    sess.last_system_error = None  # 本轮调用成功，清除上一轮的系统错误标记

    # 教学质量控制：Generate → Validate → Regenerate（V1.5：最多重试 2 次）
    MAX_RETRIES = 2
    ok, issues = validate(resp, ctx)
    for _retry in range(MAX_RETRIES):
        if ok:
            break
        fix_prompt = (
            "你的上一次回答未通过教学质量控制，检测到以下违规：\n"
            + "\n".join(f"- {i}" for i in issues)
            + "\n\n请重新输出一份修正后的 JSON：必须补齐缺失的模式字段，并严格遵守当前模式的流程"
              "与提示等级（不要过早给完整答案、不要直接给出完整修复代码、不要编造运行结果）。只输出 JSON。"
        )
        retry_messages = messages + [
            {"role": "assistant", "content": resp.model_dump_json()},
            {"role": "user", "content": fix_prompt},
        ]
        try:
            resp_retry = await client.teach(retry_messages, req.mode)
            ok_retry, issues_retry = validate(resp_retry, ctx)
            # 只在改善时采纳
            if ok_retry or len(issues_retry) < len(issues):
                resp, issues, ok = resp_retry, issues_retry, ok_retry
        except Exception:
            break

    # 记录会话 & 更新 hint level
    sess.hint_level = ctx.hint_level
    sess.history.append({"role": "user", "content": req.user_input})
    sess.history.append({"role": "assistant", "content": resp.message})

    # 调试行为：更新取证状态机
    debug_state_info = {}
    if behavior == "debug" and sess.debug_state is not None:
        sess.debug_state = update_debugger_state(sess.debug_state, resp)
        debug_state_info = {
            "rounds": sess.debug_state.rounds,
            "phase": sess.debug_state.phase.value,
            "phase_desc": _PHASE_DESC.get(sess.debug_state.phase, sess.debug_state.phase.value),
            "last_diagnostic_question": sess.debug_state.last_diagnostic_question,
        }

    # 结构化为日志（AI Evaluation 的数据基础）
    mode_advice = compute_mode_advice(mode, req, task)
    logs_mod.log_event(
        type="teach",
        session_id=sid,
        student_id=sid,
        project_id=req.project_id,
        task_id=req.task_id,
        mode=mode,
        behavior=behavior or None,
        attempt_count=student.attempt_count.get(req.task_id, 0),
        hint_level=ctx.hint_level,
        user_message=req.user_input[:500],
        ai_response=resp.message[:800],
        next_action=(resp.next_action or (mode_advice.get("mode") if mode_advice else None)),
        accepted_by_user=None,
        task_completed=False,  # 完成判定只来自验收链（/api/ai/review）
        quality_warnings=issues,
        repo_used=bool(req.repo_url),
    )

    return {
        "ok": True,
        "data": {
            "mode": mode,
            "message": resp.message,
            "next_action": resp.next_action,
            "hints_used": resp.hints_used if resp.hints_used else min(ctx.hint_level, 5),
            # 分模式结构化字段
            "hint_level": resp.hint_level,
            "hint": resp.hint,
            "leading_question": resp.leading_question,
            "current_step": resp.current_step,
            "suspected_cause": resp.suspected_cause,
            "verify_steps": resp.verify_steps,
            "diagnostic_question": resp.diagnostic_question,
            # 指导模式内部行为标签（用户无感，仅展示）
            "behavior": behavior,
            "behavior_label": BEHAVIOR_LABELS.get(behavior, ""),
            # 代码证据状态（V2）
            "evidence": evidence_status,
            # Sprint 4：Debugger 取证状态机（前端展示轮次/阶段）
            "debug_state": debug_state_info,
            # 模式链建议（推荐下一个辅导模式）
            "mode_advice": mode_advice,
            # 元信息
            "task_id": req.task_id,
            "material_sources": len(ctx.material),
            "source_url": ctx.source_url,
            "hint_level_desc": hint_mod.describe(ctx.hint_level),
            "quality_warnings": issues,
            "latency_ms": int((time.time() - start_ts) * 1000),
            "session_id": sid,
        },
    }


@app.post("/api/ai/feedback")
async def feedback(request: Request):
    """记录学生对最近一次辅导回答的满意度（accepted_by_user）。"""
    body = await request.json()
    session_id = body.get("session_id") or ""
    task_id = body.get("task_id") or ""
    accepted = bool(body.get("accepted"))
    hit = logs_mod.set_accepted(session_id, task_id, accepted)
    if not hit:
        return JSONResponse({"ok": False, "error": {"code": "NOT_FOUND", "message": "未找到匹配的辅导记录"}}, status_code=404)
    logs_mod.log_event(type="feedback", session_id=session_id, task_id=task_id, accepted=accepted)
    return {"ok": True, "data": {"accepted": accepted}}


@app.get("/api/ai/stats")
async def stats():
    """AI Evaluation：从事件日志聚合教学指标。"""
    return {"ok": True, "data": logs_mod.compute_stats()}


@app.post("/api/ai/review")
async def review(req: ReviewRequest, request: Request):
    """评审链（Sprint 5）：Submission → Evidence Collector → Rubric → Reviewer → Evaluation。"""
    if not req.task_id:
        return JSONResponse({"ok": False, "error": {"code": "NO_TASK", "message": "请先选择一个任务"}}, status_code=400)
    if not req.api_key:
        return JSONResponse({"ok": False, "error": {"code": "NO_API_KEY", "message": "需要提供 DeepSeek API Key（BYOK）"}}, status_code=400)

    task = get_task(req.task_id)
    if not task:
        return JSONResponse({"ok": False, "error": {"code": "BAD_TASK", "message": "任务不存在"}}, status_code=404)
    rubrics = get_rubrics(req.task_id)
    if not rubrics:
        return JSONResponse({"ok": False, "error": {"code": "NO_RUBRIC", "message": "该任务没有验收标准"}}, status_code=404)

    sub = req.submission or None
    repo_url = None
    if sub and sub.github_url:
        repo_url = sub.github_url
    elif req.repo_url:
        repo_url = req.repo_url

    # Evidence Collector：优先拉取 GitHub 代码证据（失败不阻塞，其它证据照常）
    repo_code_text = ""
    evidence_status = {"status": "none"}
    ci_status = {"status": "none"}
    if repo_url:
        cc = task.code_context if task else None
        ev = await build_code_evidence(repo_url, task_id=req.task_id, code_context=cc)
        if ev["ok"]:
            repo_code_text = ev["evidence_text"]
            evidence_status = {"status": "ok", "repo": ev["repo"], "file_count": ev["file_count"]}
            if ev.get("ci"):
                ci = ev["ci"]
                ci_status = {
                    "status": "ok" if ci.get("ok") else "error",
                    "has_ci": ci.get("has_ci", False) if ci.get("ok") else False,
                    "workflows": ci.get("workflows", []),
                    "error": ci.get("error", "") if not ci.get("ok") else "",
                    "code": ci.get("code", "") if not ci.get("ok") else "",
                }
        else:
            evidence_status = {"status": "error", "code": ev["code"], "error": ev["error"]}

    available = collect_evidence(sub, repo_code_text)

    # V1.5 Sprint 2：Evidence 硬约束预检
    precheck = evidence_precheck(rubrics, available)
    forced_results = precheck["forced_needs_review"]
    passable_rubrics = precheck["passable_rubrics"]

    # 如果所有 Rubric 都缺关键证据，直接返回 NEED_REVIEW，不走 LLM
    if not passable_rubrics:
        all_criteria = [
            {"rubric_id": fr["rubric_id"], "status": "NEED_REVIEW",
             "evidence": "", "reason": fr["reason"]}
            for fr in forced_results
        ]
        return {
            "ok": True,
            "data": {
                "task_id": req.task_id,
                "evidence": evidence_status,
                "ci": ci_status,
                "evaluation": {
                    "status": "NEED_REVIEW",
                    "score": 0,
                    "criteria": all_criteria,
                    "next_step": "请补充以下证据后重新提交：" + "；".join(
                        f"{fr['rubric_id']} 需要 {', '.join(fr['missing'])}" for fr in forced_results
                    ),
                },
                "score": 0,
                "status": "NEED_REVIEW",
                "passed": False,
                "latency_ms": 0,
                "session_id": req.session_id or "review",
            },
        }

    # 有可判定的 Rubric：构建 Prompt（仅包含 passable rubrics 的上下文提示）
    system_prompt = build_review_system_prompt(task, passable_rubrics, available)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": (
            "请根据上面给出的 Rubric 和学生已提交的证据，逐条客观评审，严格只输出符合 Evaluation 结构的 JSON。"
        )},
    ]

    client = LLMClient(req.api_key, req.base_url, req.model)
    start_ts = time.time()
    try:
        evaluation = await client.review(messages)
    except (PermissionError, TimeoutError, EngineError, RuntimeError) as e:
        # 错误分类漏斗：评审链任何系统故障 → REVIEW_UNAVAILABLE，绝不写入学生 Evaluation
        return llm_error_response(e, review=True)

    score = int(evaluation.score)
    status = evaluation.status.value

    # V1.5 Sprint 2：合并硬约束的 NEED_REVIEW 结果
    if forced_results:
        from schemas import ReviewCriterion, ReviewStatus
        for fr in forced_results:
            evaluation.criteria.append(ReviewCriterion(
                rubric_id=fr["rubric_id"],
                status=ReviewStatus.NEED_REVIEW,
                evidence="",
                reason=fr["reason"],
            ))
        # 有 NEED_REVIEW 强制项时，总状态不能是 PASS
        if status == "PASS":
            status = "NEED_REVIEW"
            evaluation.status = ReviewStatus.NEED_REVIEW
    # Sprint 6：评审事件日志
    logs_mod.log_event(
        type="review",
        session_id=req.session_id or "review",
        student_id=req.session_id or "review",
        project_id=req.project_id,
        task_id=req.task_id,
        mode="reviewer",
        attempt_count=0,
        hint_level=0,
        user_message="",
        ai_response="",
        next_action="",
        accepted_by_user=None,
        task_completed=status == "PASS",
        review_status=status,
        review_score=score,
        repo_used=bool(repo_url),
    )
    return {
        "ok": True,
        "data": {
            "task_id": req.task_id,
            "evidence": evidence_status,
            "ci": ci_status,
            "evaluation": evaluation.model_dump(),
            "score": score,
            "status": status,
            "passed": status == "PASS",
            "latency_ms": int((time.time() - start_ts) * 1000),
            "session_id": req.session_id or "review",
        },
    }


# ---------------------------------------------------------------------------
# V1.5 Sprint 1：Task-aware Code Retrieval 接口
# ---------------------------------------------------------------------------
class CodeRetrieveRequest(BaseModel):
    """POST /api/github/retrieve 请求体。"""
    repo_url: str
    task_id: str = ""
    api_key: str = ""
    base_url: str | None = None
    model: str | None = None


@app.post("/api/github/retrieve")
async def code_retrieve(req: CodeRetrieveRequest):
    """按 Task 检索相关代码，返回候选文件 + AI 筛选结果。"""
    if not req.repo_url:
        return JSONResponse({"ok": False, "error": {"code": "NO_REPO", "message": "请提供 GitHub 仓库链接"}}, status_code=400)

    task = get_task(req.task_id) if req.task_id else None
    cc = task.code_context if task else None
    client = LLMClient(req.api_key, req.base_url, req.model) if req.api_key else None

    ev = await build_code_evidence(req.repo_url, task_id=req.task_id, code_context=cc, client=client)
    if not ev["ok"]:
        return JSONResponse({"ok": False, "error": {"code": ev.get("code", "UNKNOWN"), "message": ev.get("error", "拉取失败")}}, status_code=400)

    # 提取候选文件列表（含评分和 AI 筛选理由）
    files = []
    for kf in ev.get("key_files", []):
        files.append({
            "path": kf["path"],
            "relevance": kf.get("relevance", 0.0),
            "reason": kf.get("reason", ""),
            "truncated": kf.get("truncated", False),
        })

    return {
        "ok": True,
        "data": {
            "task_id": req.task_id,
            "repo": ev["repo"],
            "default_branch": ev["default_branch"],
            "file_count": ev["file_count"],
            "files": files,
            "ci": ev.get("ci", {}),
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8099, reload=False)