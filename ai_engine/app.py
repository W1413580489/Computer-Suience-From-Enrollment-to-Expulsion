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
import hashlib
import time
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from schemas import (AISession, DebuggerState, DebugPhase, Evidence, EvidenceType, Mode, ReviewCriterion, ReviewRequest, ReviewStatus, Submission, TeachRequest)
from course_data import get_project, list_projects, get_task, get_rubrics, list_courses, get_next_task, get_stage
from context_builder import build_context
from prompts import build_system_prompt, route_behavior, BEHAVIOR_LABELS
from llm_client import (LLMClient, DEFAULT_MODEL, DEFAULT_BASE_URL, EngineError, ProviderError,
                        MAX_TOKENS_BY_BEHAVIOR, DEFAULT_TEACH_MAX_TOKENS, REVIEW_MAX_TOKENS)
from response_validator import validate
from code_evidence import build_code_evidence, compare_revisions
from career import build_career_text
import vision as vision_mod
from review import build_review_system_prompt, ci_direct_verdict, collect_evidence, compute_evaluation, evidence_precheck, evidence_text, snapshot_evidence
from pydantic import Field
import logs as logs_mod
import hint as hint_mod
import project_state as project_state_mod
import learner_state as learner_state_mod
import student_record as student_record_mod

app = FastAPI(title="AI Teaching Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

TZ = timezone(timedelta(hours=8))

# v1.1：会话/评审/证据持久化（SQLite 为真相源；替代原进程内存 dict，重启不丢）
# 评审版本常量（rubric/prompt/engine）由 store 内部维护；改规则需在 store.py 手动 bump
from store import store as db


def store_evidence(ev: Evidence) -> None:
    db.add_evidence(ev)


def get_evidence(task_id: str, rubric_id: str | None = None) -> list[Evidence]:
    return db.list_evidence(task_id, rubric_id=rubric_id)


# P2：把本次可用证据落库（evidence 表成为共享真相源，不再只是进程内存 dict）。
# 幂等：id 由 task_id + snapshot_hash + 证据类型派生 → 同一快照重复写只覆盖、不新增。
EVIDENCE_ROW_CHAR_CAP = 4000
# 证据文本类型 → EvidenceType 语义映射（url=仓库链接、deployment 属运行证据）
_EVIDENCE_TYPE_ALIAS = {"url": EvidenceType.GITHUB, "deployment": EvidenceType.RUNTIME}


def persist_evidence(task_id: str, available: dict[str, str], snapshot_hash: str) -> None:
    for typ, text in available.items():
        eid = hashlib.sha1(f"{task_id}:{snapshot_hash}:{typ}".encode("utf-8")).hexdigest()[:12]
        etype = _EVIDENCE_TYPE_ALIAS.get(typ)
        if etype is None:
            try:
                etype = EvidenceType(typ)
            except ValueError:
                etype = EvidenceType.MANUAL
        store_evidence(Evidence(id=eid, task_id=task_id, type=etype, source=typ,
                                content=(text or "")[:EVIDENCE_ROW_CHAR_CAP]))


def _now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def _ci_conclusion(ci_workflows) -> str:
    """P6：把本次 CI 工作流结论归并为简历口径（success / failure / ''）。

    与前端 build_career_text 的 ci 指标口径一致：任一工作流 conclusion=success → success。
    """
    flows = ci_workflows or []
    if any((w.get("conclusion") or "").lower() == "success" for w in flows):
        return "success"
    has_conclusion = any((w.get("conclusion") or "") for w in flows)
    return "failure" if has_conclusion else ""


# ---------------------------------------------------------------------------
# P4：Project State / Task Blocked Reason
# ---------------------------------------------------------------------------
def attach_student_state(data: dict, student_id: str, task_id: str, project_id: str) -> dict:
    """把"随学生变化"的状态挂到评审响应上（blocked_reason + project_state + learner_state）。

    硬约束：必须在 db.save_review_result() 之后调用——这些字段是学生态计算结果，
    一旦写进幂等缓存，后续同一提交的缓存命中会返回陈旧的学生状态。
    """
    data["blocked_reason"] = project_state_mod.task_blocked_reason(student_id, task_id)
    data["project_state"] = project_state_mod.compute_project_state(student_id, project_id)
    # P5：Learner State（技能四态 + 学习缺口）——EVIDENCED ≠ MASTERED，两者并存返回
    data["learner_state"] = learner_state_mod.compute_learner_state(student_id)
    return data


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

    return adv("reviewer", "看起来完成了，点「提交验收」对照标准逐条评审打分", task)


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
            # 2026-09：DeepSeek 将 V4 Flash / V4 Pro 合并为 V4.1-Flash，官方模型名 deepseek-flash
            {"model": "deepseek-flash", "label": "DeepSeek V4.1（默认）"},
        ],
        # 导师页与导航「API 配置」共用同一份 BYOK 设置（服务商/BaseURL/模型/Key），
        # 此处仅作默认展示；实际生效值由前端 settingsStore（xkz_settings_v1）请求时携带
        "config_source": "xkz_settings_v1",
        # V2.1：已验证支持图片输入的模型白名单（前端据此决定是否允许上传运行截图）
        "vision_models": sorted(vision_mod.VISION_WHITELIST),
        "modes": [m.value for m in Mode],
        "hint_levels": {str(k): v for k, v in {
            0: "仅引导", 1: "提示方向", 2: "思路步骤",
            3: "具体做法", 4: "答案片段", 5: "完整方案",
        }.items()},
        "courses": list_courses(),
        "projects": list_projects(),
    }}


@app.get("/api/ai/project_state")
async def project_state(student_id: str = "", project_id: str = "project_chatbot"):
    """P4：项目状态只读聚合（服务端优先；前端可用它替代本地推算）。

    状态：NOT_STARTED / IN_PROGRESS / COMPLETED / BLOCKED
    完成判定只认 completion_required 的 Task（全部 PASS → COMPLETED）。
    """
    if not student_id:
        return JSONResponse({"ok": False, "error": {
            "code": "NO_STUDENT", "message": "需要提供 student_id"}}, status_code=400)
    st = project_state_mod.compute_project_state(student_id, project_id)
    if st is None:
        return JSONResponse({"ok": False, "error": {
            "code": "BAD_PROJECT", "message": "项目不存在"}}, status_code=404)
    return {"ok": True, "data": st}


@app.get("/api/ai/learner_state")
async def learner_state(student_id: str = ""):
    """P5：学生技能四态 + 学习缺口（只读聚合，可重复调用）。

    四态：UNSEEN / EXPOSED / PRACTICED / EVIDENCED。
    EVIDENCED 表示"产生了与技能相关的有效交付证据"，**不等于 MASTERED**——
    因此同时返回 learning_gaps（theory 未达标产生的学习缺口）。
    """
    if not student_id:
        return JSONResponse({"ok": False, "error": {
            "code": "NO_STUDENT", "message": "需要提供 student_id"}}, status_code=400)
    return {"ok": True, "data": learner_state_mod.compute_learner_state(student_id)}


@app.get("/api/ai/project_record")
async def project_record(student_id: str = "", project_id: str = "project_chatbot"):
    """P6：项目记录（简历历史结果 + 项目复盘 + 项目/学生状态）——服务端真相源，零 LLM。

    数据全部来自 submissions / evaluations / 课程配置，不调用模型。
    前端采用"服务端优先 + localStorage 兜底"：本接口不可用时回退本地缓存，
    不会因一次接口失败清空整个简历或进度模块。
    """
    if not student_id:
        return JSONResponse({"ok": False, "error": {
            "code": "NO_STUDENT", "message": "需要提供 student_id"}}, status_code=400)
    project = get_project(project_id)
    if not project:
        return JSONResponse({"ok": False, "error": {
            "code": "BAD_PROJECT", "message": "项目不存在"}}, status_code=404)
    results = student_record_mod.build_career_results(student_id, project_id)
    return {"ok": True, "data": {
        "project_id": project.id,
        "source": "server",
        "results": results,
        "completed_tasks": [r["task_id"] for r in results if r["status"] == "PASS"],
        "retro": student_record_mod.build_project_retro(student_id, project_id),
        "project_state": project_state_mod.compute_project_state(student_id, project_id),
        "learner_state": learner_state_mod.compute_learner_state(student_id),
    }}


# ---------------------------------------------------------------------------
# 核心辅导接口
# ---------------------------------------------------------------------------
def _visual_note(ev) -> str:
    """对话附图要点：写入前端对话历史，让后续追问仍能引用图片内容（不含图片本身）。"""
    if ev is None or ev.status != "ok" or not ev.facts:
        return ""
    body = "；".join(ev.facts[:4])[:400]
    return f"[此前学生贴了 {ev.count} 张截图，图中可见：{body}]"


@app.post("/api/ai/teach")
async def teach(req: TeachRequest, request: Request):
    # 校验参数
    if not req.task_id:
        return JSONResponse({"ok": False, "error": {"code": "NO_TASK", "message": "请先选择一个任务"}}, status_code=400)
    if not req.api_key:
        return JSONResponse({"ok": False, "error": {"code": "NO_API_KEY", "message": "需要提供 DeepSeek API Key（BYOK）"}}, status_code=400)
    if not req.user_input.strip() and not req.visual_images:
        return JSONResponse({"ok": False, "error": {"code": "EMPTY_INPUT", "message": "请输入你要问的内容，或贴一张截图"}}, status_code=400)

    mode = req.mode.value if isinstance(req.mode, Mode) else req.mode
    task = get_task(req.task_id)
    if not task:
        return JSONResponse({"ok": False, "error": {"code": "BAD_TASK", "message": "任务不存在"}}, status_code=404)

    # 学生状态
    student = req.student
    if student is None:
        from schemas import Student
        student = Student(session_id=req.session_id or "anon")

    # P2 身份分离：student_id = 稳定身份（跨会话归属到"人"）；session_id = 纯会话标识（决定对话历史分档）
    student_id = student.student_id or student.session_id or req.session_id or "anon"
    sid = student.session_id or req.session_id or "anon"
    db.upsert_student(student_id, student.name)

    # 会话（单一连续对话流：会话身份 = 会话 + 任务；模式只是请求参数，切换不丢历史）
    # v1.1：真相源是 SQLite sessions 表；req.history 仅当首次（库中无记录）时作初始化回退
    skey = f"{sid}:{req.task_id}"
    sess = db.get_session(skey)
    if not sess or sess.task_id != req.task_id:
        sess = AISession(session_id=sid, student_id=student_id,
                         task_id=req.task_id, mode=req.mode,
                         attempt_count=student.attempt_count.get(req.task_id, 0))
        if req.history:  # 首次请求：用前端历史初始化（此后以库中为准）
            sess.history = list(req.history)
    sess.mode = req.mode  # 记录最近一次使用的模式（不影响会话身份）

    # V2.2 对话附图：先读图（转录图中内容），结果同时用于行为路由与对话。
    # 任何失败（模型不支持/超时/繁忙/格式问题）只跳过图片，普通对话完全不受影响（fail-open）。
    visual_evidence = None
    visual_text = ""
    if req.visual_images:
        visual_evidence = await vision_mod.analyze_images(
            req.visual_images,
            task_title=task.title,
            task_objective=task.objective,
            visual_conditions=[],
            model=req.model or DEFAULT_MODEL,
            api_key=req.api_key,
            base_url=req.base_url,
            provider="custom" if req.base_url else "deepseek",
            purpose="chat",
            user_question=req.user_input,
        )
        visual_text = vision_mod.render_chat_visual_text(visual_evidence)
        # 只记元数据（数量/字节/耗时/错误码），绝不记录图片内容或 base64
        logs_mod.log_event(
            type="vision",
            session_id=sid,
            task_id=req.task_id,
            project_id=req.project_id,
            vision_purpose="chat",
            vision_status=visual_evidence.status,
            vision_code=visual_evidence.code,
            image_count=visual_evidence.count,
            image_bytes=visual_evidence.bytes,
            vision_model=visual_evidence.model,
            vision_cached=visual_evidence.cached,
            vision_ms=visual_evidence.latency_ms,
        )

    # 指导模式内部行为路由（拆解/推进/调试，用户无感；调试状态机挂在行为上）
    # 有图片时把读图结果一起纳入判断：贴报错截图 → 直接进入调试行为
    behavior = ""
    if mode == "tutor":
        behavior = route_behavior((req.user_input + "\n" + visual_text).strip() or "（学生发来一张图片）", sess)

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

    db.lazy_cleanup()  # 惰性清理（幂等、低开销）

    # 组装 Prompt（含系统错误隔离声明：上一轮若有系统故障，本轮注入隔离说明）
    system_prompt = build_system_prompt(ctx, mode) + system_error_note(sess)

    # v1.1：上下文真相源 = 服务端会话全量历史（sess.history 由 SQLite 恢复）；
    # 窗口最近 12 轮原文（显式宽松，随 _trim 6000 字预算兜底）
    full_history = sess.history or []
    history = list(full_history)
    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-12:]:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    # 图片本身不进对话（只进"读图结果"）；学生只贴图没打字时用占位问句，保证消息非空
    if visual_text:
        messages.append({"role": "user", "content": visual_text})
    messages.append({"role": "user", "content": req.user_input.strip() or "请看上面的图片。"})

    # 调用 LLM（v1.1：按指导行为传入输出上限，杜绝输出被服务商默认额度截断）
    client = LLMClient(req.api_key, req.base_url, req.model)
    teach_tokens = MAX_TOKENS_BY_BEHAVIOR.get(behavior, DEFAULT_TEACH_MAX_TOKENS)
    start_ts = time.time()
    try:
        resp = await client.teach(messages, req.mode, max_tokens=teach_tokens)
    except (PermissionError, TimeoutError, EngineError, RuntimeError) as e:
        # 错误分类漏斗：系统错误记入会话标记（下一轮注入隔离声明），绝不进入学生评审结果
        if not isinstance(e, PermissionError):
            sess.last_system_error = str(e)[:200]
            db.save_session(sess)  # v1.1：持久化隔离标记，重启后仍能在下一轮注入
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
            resp_retry = await client.teach(retry_messages, req.mode, max_tokens=teach_tokens)
            ok_retry, issues_retry = validate(resp_retry, ctx)
            # 只在改善时采纳
            if ok_retry or len(issues_retry) < len(issues):
                resp, issues, ok = resp_retry, issues_retry, ok_retry
        except Exception:
            break

    # 记录会话 & 更新 hint level
    sess.hint_level = ctx.hint_level
    hist_user = req.user_input
    if visual_evidence is not None and visual_evidence.status == "ok":
        hist_user = f"[附 {visual_evidence.count} 张图片] {req.user_input}".strip()
    sess.history.append({"role": "user", "content": hist_user})
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

    # v1.1：会话持久化（历史 + hint + 调试状态 + 尝试次数，SQLite 真相源）
    db.save_session(sess)

    # 结构化为日志（AI Evaluation 的数据基础）
    mode_advice = compute_mode_advice(mode, req, task)
    logs_mod.log_event(
        type="teach",
        session_id=sid,
        student_id=student_id,
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
            # V2.2 对话附图：状态（供前端提示）+ 要点（供前端写入对话历史，让后续追问仍能引用图片内容）
            "visual": visual_evidence.model_dump() if visual_evidence else None,
            "visual_note": _visual_note(visual_evidence),
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
            # P4：任务前置提示（仅提示，不阻断；无前置或已满足时为 None）
            "blocked_reason": project_state_mod.task_blocked_reason(student_id, req.task_id),
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


@app.get("/api/ai/session_history")
async def session_history(session_key: str = ""):
    """返回某会话的完整历史 + 结构化状态（调试轮次/hint 等级）。

    v1.1 配套（评审意见 ⑨ 的必要补充）：浏览器刷新/清理 localStorage 后，
    前端据此恢复对话显示（真相源仍是 SQLite，本地缓存只做即时渲染）。
    """
    if not session_key:
        return JSONResponse({"ok": False, "error": {"code": "NO_SESSION", "message": "缺少 session_key"}}, status_code=400)
    data = db.session_history(session_key)
    if data is None:
        return {"ok": True, "data": None}  # 首次对话/无历史：前端保持空状态
    return {"ok": True, "data": data}


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
    readme_run_cmd = ""
    repo_head_sha = ""   # P2：仓库 HEAD（只入 submissions/evaluations，不进快照/缓存 key）
    if repo_url:
        cc = task.code_context if task else None
        ev = await build_code_evidence(repo_url, task_id=req.task_id, code_context=cc)
        if ev["ok"]:
            repo_code_text = ev["evidence_text"]
            evidence_status = {"status": "ok", "repo": ev["repo"], "file_count": ev["file_count"]}
            readme_run_cmd = ev.get("readme_run_cmd", "")
            repo_head_sha = ev.get("head_sha", "") or ""
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

    # V2.1 视觉证据：仅当模型在 Vision 白名单内且学生上传了截图时才分析；
    # 任何失败（不支持/超时/繁忙/格式问题）都只跳过视觉，普通验收不受影响（fail-open）。
    visual_evidence = None
    if req.visual_images:
        visual_conditions = [r.visual_pass_condition for r in rubrics
                             if getattr(r, "visual_check", "none") == "supported"
                             and r.visual_pass_condition]
        visual_evidence = await vision_mod.analyze_images(
            req.visual_images,
            task_title=task.title,
            task_objective=task.objective,
            visual_conditions=visual_conditions,
            model=req.model or DEFAULT_MODEL,
            api_key=req.api_key,
            base_url=req.base_url,
            provider="custom" if req.base_url else "deepseek",
        )
        # 只记录元数据（数量/字节/耗时/错误码），绝不记录图片内容或 base64
        logs_mod.log_event(
            type="vision",
            session_id=req.session_id or "review",
            task_id=req.task_id,
            project_id=req.project_id,
            vision_status=visual_evidence.status,
            vision_code=visual_evidence.code,
            image_count=visual_evidence.count,
            image_bytes=visual_evidence.bytes,
            vision_model=visual_evidence.model,
            vision_cached=visual_evidence.cached,
            vision_ms=visual_evidence.latency_ms,
        )

    available = collect_evidence(sub, repo_code_text, visual=visual_evidence)

    # V2 · T2.5：README 启动命令 → runtime 证据（本地可复现运行说明；自述优先级更高）
    if "runtime" not in available and readme_run_cmd:
        available["runtime"] = f"README 启动命令（本地可复现运行说明）：{readme_run_cmd}"

    # V2 修改 6 · L4/L5：证据快照冻结 + 幂等缓存（同 task + 同快照 + 同版本 → 直接复用评审结果）
    db.lazy_cleanup()  # v1.1：惰性清理（幂等、低开销）
    ci_workflows = []
    if ci_status.get("status") == "ok" and ci_status.get("workflows"):
        ci_workflows = ci_status["workflows"]
    model_used = req.model or DEFAULT_MODEL
    snapshot_hash = snapshot_evidence(available, ci_workflows, task_id=req.task_id)
    # 版本化 key（_review_cache_key）：rubric/prompt/engine 任一 bump → key 变化 → 必然重新评审

    # P2：稳定学生身份（空则回退 session_id，兼容未升级前端）+ 学生档案 upsert
    student_id = req.student_id or (sub.student_id if sub else "") or req.session_id or "anon"
    db.upsert_student(student_id)

    # P2：本次提交落库（独立历史事件）——head_sha / parent 只入 submissions 行，绝不进快照与缓存 key
    submission = sub or Submission(task_id=req.task_id)
    submission.task_id = req.task_id
    submission.project_id = req.project_id
    submission.student_id = student_id
    submission.head_sha = repo_head_sha
    prev_sub = db.latest_submission(student_id, req.task_id)
    if prev_sub and prev_sub["id"] != submission.id:
        submission.parent_submission_id = prev_sub["id"]

    # P3：修订演进（GitHub compare）——仅当"上一版 HEAD ≠ 本次 HEAD"时才多一次请求。
    # 结果只写入 submissions / evaluations 行，绝不进 evidence_text 与 review 缓存 key。
    revision = {}
    if (prev_sub and prev_sub["head_sha"] and repo_head_sha
            and prev_sub["head_sha"] != repo_head_sha):
        revision = await compare_revisions(repo_url, prev_sub["head_sha"], repo_head_sha)
        if revision:
            revision["parent_submission_id"] = submission.parent_submission_id
    submission.revision_json = json.dumps(revision, ensure_ascii=False) if revision else ""

    db.save_submission(submission)

    # P2：证据落库（幂等；evidence 表成为共享真相源，评审链不再只依赖内存 dict）
    persist_evidence(req.task_id, available, snapshot_hash)

    def _record_eval(status: str, score: int, passed: bool, criteria: dict,
                     ci_conclusion: str = "") -> None:
        """评审历史落库（与 review_results 幂等缓存分离；缓存命中也要记，因为提交是真实事件）。"""
        db.save_evaluation(submission_id=submission.id, student_id=student_id,
                           task_id=req.task_id, project_id=req.project_id,
                           snapshot_hash=snapshot_hash, model=model_used, status=status,
                           score=score, passed=passed, head_sha=submission.head_sha,
                           revision_json=submission.revision_json, ci_conclusion=ci_conclusion,
                           criteria=criteria if isinstance(criteria, dict) else {})

    # v1.1 失败熔断：同 key 5 分钟内直接复用失败结论，不再调 LLM 烧学生额度
    breaker_error = db.get_review_failure(req.task_id, snapshot_hash, model_used)
    if breaker_error:
        return JSONResponse({"ok": False, "error": {
            "code": "REVIEW_UNAVAILABLE",
            "message": f"评审服务暂时不可用（短暂熔断，请 5 分钟后再试）：{breaker_error}"
                      "（系统故障，与你提交的项目无关）"}}, status_code=500)

    # v1.1 成功幂等：版本化 key 命中 → 重建 resp（刷新 session_id，不整体复用旧 session_id）
    hit = db.get_review_result(req.task_id, snapshot_hash, model_used)
    if hit is not None:
        data = dict(hit.get("data") or {})
        data.update({"cached": True, "snapshot_hash": snapshot_hash,
                     "session_id": req.session_id or "review", "latency_ms": 0})
        # P2：缓存命中同样记一行评审历史（归属本次提交；缓存只负责"同输入同输出"）
        _record_eval(str(data.get("status") or "NEED_REVIEW"), int(data.get("score") or 0),
                     bool(data.get("passed")),
                     data.get("evaluation") if isinstance(data.get("evaluation"), dict) else {},
                     ci_conclusion=_ci_conclusion(ci_workflows))
        # P4：学生态在缓存之后挂（缓存里不含 blocked_reason / project_state）
        attach_student_state(data, student_id, req.task_id, req.project_id)
        return {"ok": True, "data": data}

    # V1.5 Sprint 2：Evidence 硬约束预检（修改 1：deployment 不再是硬性证据）
    precheck = evidence_precheck(rubrics, available)
    forced_results = precheck["forced_needs_review"]
    passable_rubrics = precheck["passable_rubrics"]

    # CI 结论直判分流（V2 修改 6 · L3）：system 判定的 CI 结论在代码层直接映射，
    # 对应 Rubric 不送 LLM；全部 Rubric 都能直判/预检时整条评审零 LLM 调用
    direct_criteria: list[ReviewCriterion] = []
    llm_rubrics = []
    for r in passable_rubrics:
        verdict = ci_direct_verdict(r, ci_workflows) if ci_workflows else None
        if verdict:
            direct_criteria.append(ReviewCriterion(
                rubric_id=r.id, status=verdict["status"],
                evidence=verdict["evidence"],
                reason="CI 结论直判（system 权威证据，非 AI 判定）",
            ))
        else:
            llm_rubrics.append(r)

    # 所有 Rubric 都缺证据且无 CI 直判项：直接返回 NEED_REVIEW，不走 LLM
    if not direct_criteria and not llm_rubrics:
        all_criteria = [
            {"rubric_id": fr["rubric_id"], "status": "NEED_REVIEW",
             "evidence": "", "reason": fr["reason"]}
            for fr in forced_results
        ]
        resp = {
            "ok": True,
            "data": {
                "task_id": req.task_id,
                "evidence": evidence_status,
                "ci": ci_status,
                "visual": visual_evidence.model_dump() if visual_evidence else None,
                "snapshot_hash": snapshot_hash,
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
        # v1.1：确定性 NEED_REVIEW 结果也写入幂等缓存（重启后仍复用，避免重复预检/重复拉取）
        # 注意：save 先执行（json.dumps 在调用时序列化），之后才挂学生态，缓存里不含 blocked_reason
        db.save_review_result(req.task_id, snapshot_hash, model_used, resp)
        _record_eval("NEED_REVIEW", 0, False, resp["data"]["evaluation"],
                     ci_conclusion=_ci_conclusion(ci_workflows))
        attach_student_state(resp["data"], student_id, req.task_id, req.project_id)
        return resp

    start_ts = time.time()
    llm_criteria: list[ReviewCriterion] = []
    next_step = ""
    if llm_rubrics:
        # 有需要 LLM 语义判定的 Rubric：构建 Prompt（仅包含送审的 rubrics）
        system_prompt = build_review_system_prompt(task, llm_rubrics, available)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                "请根据上面给出的 Rubric 和学生已提交的证据，逐条客观评审，"
                "严格只输出符合 criteria/next_step 结构的 JSON（不要输出总分 status/score）。"
            )},
        ]
        client = LLMClient(req.api_key, req.base_url, req.model)
        try:
            # v1.1：评审链严格模式——语义校验（rubric_id 必须属于送审清单、逐条覆盖、evidence/reason 非空）
            llm_out = await client.review(
                messages,
                max_tokens=REVIEW_MAX_TOKENS,
                allowed_rubric_ids=[r.id for r in llm_rubrics],
            )
        except (PermissionError, TimeoutError, EngineError, RuntimeError) as e:
            # 错误分类漏斗：评审链任何系统故障 → REVIEW_UNAVAILABLE，绝不写入学生 Evaluation；
            # v1.1：非 Key 类故障写入熔断表（同 key 5 分钟不再重调 LLM）
            if not isinstance(e, PermissionError):
                db.save_review_failure(req.task_id, snapshot_hash, model_used, str(e))
            return llm_error_response(e, review=True)
        llm_criteria = llm_out.criteria
        next_step = llm_out.next_step
    else:
        next_step = ""

    # V2 修改 6（L1/L2）：合并 CI 直判 + LLM 逐条判定 + 硬约束 NEED_REVIEW，
    # score/status 全部由代码聚合，LLM 输出不再决定总分
    all_criteria = direct_criteria + llm_criteria
    for fr in forced_results:
        all_criteria.append(ReviewCriterion(
            rubric_id=fr["rubric_id"],
            status=ReviewStatus.NEED_REVIEW,
            evidence="",
            reason=fr["reason"],
        ))
    if not next_step and forced_results:
        next_step = "请补充以下证据后重新提交：" + "；".join(
            f"{fr['rubric_id']} 需要 {', '.join(fr['missing'])}" for fr in forced_results
        )
    evaluation = compute_evaluation(all_criteria, rubrics, next_step=next_step)
    score = int(evaluation.score)
    status = evaluation.status.value

    # Sprint 6：评审事件日志（L5 缓存命中时不会走到这里——重复评审不重复记日志）
    logs_mod.log_event(
        type="review",
        session_id=req.session_id or "review",
        student_id=student_id,
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

    resp = {
        "ok": True,
        "data": {
            "task_id": req.task_id,
            "evidence": evidence_status,
            "ci": ci_status,
            "visual": visual_evidence.model_dump() if visual_evidence else None,
            "snapshot_hash": snapshot_hash,
            "evaluation": evaluation.model_dump(),
            "score": score,
            "status": status,
            "passed": status == "PASS",
            # PASS 时的下一任务建议（按课程编排顺序；选 B：前端高亮+提示卡，不自动切换）
            "next_task": (
                (lambda nt: {"task_id": nt.id, "title": nt.title,
                             "stage_title": (get_stage(nt.stage_id).title if get_stage(nt.stage_id) else "")}
                 )(get_next_task(req.task_id))
                if status == "PASS" and get_next_task(req.task_id) else None
            ),
            "latency_ms": int((time.time() - start_ts) * 1000),
            "session_id": req.session_id or "review",
        },
    }
    # L5：写入幂等缓存（v1.1：SQLite 永久幂等，版本化 key；重启不丢，杜绝重复评审烧学生额度）
    db.save_review_result(req.task_id, snapshot_hash, model_used, resp)
    # P2：评审历史落库（与幂等缓存分离；同一提交重复评审覆盖同一行）
    _record_eval(status, score, status == "PASS", evaluation.model_dump(),
                 ci_conclusion=_ci_conclusion(ci_workflows))
    # P4：学生态必须在 save_review_result 之后挂（不污染幂等缓存）
    attach_student_state(resp["data"], student_id, req.task_id, req.project_id)
    return resp


# ---------------------------------------------------------------------------
# V2 修改 3：Career Text 生成器（一段简历描述，模板填充，不用 LLM）
# ---------------------------------------------------------------------------
class CareerTaskResult(BaseModel):
    task_id: str
    score: int | None = None
    passed: int = 0
    total: int = 0
    ci_conclusion: str = ""     # "success" | "failure" | ""


class CareerTextRequest(BaseModel):
    project_id: str = "project_chatbot"
    results: list[CareerTaskResult] = Field(default_factory=list)
    github_url: str = ""
    date: str = ""     # 简历标题行日期（YYYY.MM）；留空则由服务端按当前月份生成


@app.post("/api/career/text")
async def career_text(req: CareerTextRequest):
    """由验收结果确定性生成结构化项目经历（同输入同输出，零 LLM）。

    输出结构（2026-09-13 改版）：title_line / intro / tech / bullets / metrics / text
      - tech 只含纯技术名词（课程作者标注）
      - bullets 按 架构设计 / 稳定性与容错 / 结果产出 / 工程素养 分组，仅取已通过任务
      - 学习属性表述（认识/学习/了解…）一律不进简历
    """
    project = get_project(req.project_id)
    if not project:
        return JSONResponse({"ok": False, "error": {"code": "BAD_PROJECT", "message": "项目不存在"}}, status_code=404)
    if not req.results:
        return JSONResponse({"ok": False, "error": {"code": "NO_RESULTS", "message": "暂无验收结果，先完成验收"}}, status_code=400)

    results = [{
        "task_id": r.task_id,
        "score": r.score,
        "passed": r.passed,
        "total": r.total,
        "ci_conclusion": r.ci_conclusion,
    } for r in req.results]
    date = req.date or datetime.now(TZ).strftime("%Y.%m")
    out = build_career_text(project, results, github_url=req.github_url, date=date)
    return {"ok": True, "data": out}


# ---------------------------------------------------------------------------
# V2 修改 2：质检陪练（面试自检）——独立接口，硬边界：不判分、不进评审链、
# 不写 Evidence Store、不写评审日志字段
# ---------------------------------------------------------------------------
@app.get("/api/ai/interview")
async def interview(task_id: str = ""):
    """返回任务配套的面试自检题（课程作者标注；无标注则空列表，前端不展示）。"""
    if not task_id:
        return JSONResponse({"ok": False, "error": {"code": "NO_TASK", "message": "请先选择一个任务"}}, status_code=400)
    task = get_task(task_id)
    if not task:
        return JSONResponse({"ok": False, "error": {"code": "BAD_TASK", "message": "任务不存在"}}, status_code=404)
    return {"ok": True, "data": {
        "task_id": task_id,
        "questions": [q.model_dump() for q in task.interview_questions],
        "ai_generated": False,  # 试点阶段全部为课程作者标注
    }}


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