# -*- coding: utf-8 -*-
"""
Response Validator V1.5：AI 输出质量控制。

6 项检查（对齐飞书文档 V1.5 要求）：
  1. Role Compliance    — 当前 mode 是 debugger，AI 有没有真的在 debug？
  2. Hint Compliance     — hint_level=1 却给了完整代码？
  3. Context Compliance  — 当前 Task 是"删除 Todo"，AI 却在讲 React Router？
  4. Evidence Compliance  — reviewer 没有测试证据却判 PASS？
  5. Learning Compliance — 学生还没尝试，AI 直接完成任务？
  6. Safety / Integrity  — AI 编造运行结果/代码/项目状态？

每项检查返回 violation 对象：
  {type, severity, reason}
"""
from __future__ import annotations

import re

from schemas import AiResponse, TeachContext

# 出现即视为"过早给答案"的信号词
ANSWER_SIGNALS = ["答案是", "完整代码", "最终答案", "这样做就可", "给你代码", "修好了，代码如下"]
# 出现即视为"给出完整代码"的信号
CODE_SIGNALS = ["def ", "function ", "```", "import ", "const "]
# 编造运行结果的信号
FABRICATION_SIGNALS = ["我已经测试", "运行结果如下", "实际运行输出", "我帮你跑了一下", "测试通过了"]
# 直接替学生完成的信号
COMPLETION_SIGNALS = ["这是完整的项目", "这是最终的", "把这段代码复制", "全部代码如下"]
# Reviewer 把"系统内部错误"当成学生项目问题的信号（护栏；主机制是 CORE_POLICY 铁律 7 + 错误隔离）
SYSTEM_ERROR_SIGNALS = [
    "模型调用", "模型服务", "模型服务错误", "服务错误", "服务异常",
    "http 400", "http 401", "http 429", "http 5", "provider",
    "接口报错", "后端调用.*返回 http", "api 调用失败",
]


def validate(resp: AiResponse, ctx: TeachContext) -> tuple[bool, list[str]]:
    """返回 (是否通过, 问题列表)。不通过时上层应提示模型修正。"""
    issues: list[str] = []
    mode = resp.mode.value

    # ============ 1. Hint Compliance ============
    if ctx.hint_level <= 1:
        low_hl = any(s in (resp.hint or "") or s in resp.message for s in ANSWER_SIGNALS)
        has_code = any(s in (resp.hint or "") for s in CODE_SIGNALS)
        if low_hl:
            issues.append(f"[hint_compliance] 当前提示等级 {ctx.hint_level}，不应过早给出完整答案")
        if has_code:
            issues.append(f"[hint_compliance] 当前提示等级 {ctx.hint_level}，不应给出具体代码/完整片段")

    # ============ 2. Role Compliance ============
    if mode == "debugger":
        # Debugger 应该在定位问题，不应直接给完整修复代码
        if resp.hint and any(s in resp.hint for s in CODE_SIGNALS):
            issues.append("[role_compliance] debugger 模式禁止直接给出修复代码，应让学生用 verify_steps 自行确认根因")
        if not resp.suspected_cause:
            issues.append("[role_compliance] debugger 模式必须给出 suspected_cause")
        if not resp.verify_steps:
            issues.append("[role_compliance] debugger 模式必须给出 verify_steps 让学生验证根因")
        if not resp.diagnostic_question:
            issues.append("[role_compliance] debugger 模式必须给出 diagnostic_question 以确认报错位置")
    elif mode == "coach":
        if not resp.current_step:
            issues.append("[role_compliance] coach 模式必须给出 current_step，明确学生当前只需做哪一步")
    elif mode == "tutor":
        if not resp.hint:
            issues.append("[role_compliance] tutor 模式必须给出 hint（引导方向）")

    # ============ 3. Context Compliance ============
    # 检查回复是否严重偏离当前任务
    task_title = ctx.task_title or ""
    if task_title and len(resp.message) > 100:
        # 简单启发：回复中不包含任务关键词且篇幅长
        task_words = [w for w in task_title.replace("：", " ").replace("(", " ").split() if len(w) > 1]
        msg_lower = resp.message.lower()
        if task_words and not any(w.lower() in msg_lower for w in task_words):
            # 允许通用引导，但如果是讲解完全不相关的技术栈则视为离题
            if any(kw in msg_lower for kw in ["react router", "vue router", "nginx 配置", "docker compose"]):
                issues.append(f"[context_compliance] 当前任务是「{task_title}」，但回复疑似在讲其他技术")

    # ============ 4. Evidence Compliance ============
    if mode == "reviewer":
        if resp.score is None or resp.passed is None:
            issues.append("[evidence_compliance] reviewer 模式必须给出 score 和 passed")
        if resp.score is not None:
            if not (0 <= resp.score <= 100):
                issues.append(f"[evidence_compliance] reviewer 评分必须在 0-100 之间，当前为 {resp.score}")
            elif resp.passed is True and resp.score < 60:
                issues.append(f"[evidence_compliance] 评分为 {resp.score}，与 passed=true 矛盾，评分过低")
            elif resp.passed is False and resp.score >= 85:
                issues.append(f"[evidence_compliance] 评分为 {resp.score}，与 passed=false 矛盾，评分过高")
        # Reviewer 判 PASS 但消息中提到"缺少证据"或"未提供"
        if resp.passed is True and resp.evaluation:
            eval_lower = resp.evaluation.lower()
            if any(kw in eval_lower for kw in ["缺少", "未提供", "缺失", "无法确认"]):
                issues.append("[evidence_compliance] reviewer 判定 PASS 但评审意见提到证据缺失，存在矛盾")

    # ============ 5. Learning Compliance ============
    # 学生还没尝试（attempt_count=0），AI 直接给出完整解决方案
    if mode in ("tutor", "coach") and ctx.hint_level <= 2:
        if any(s in resp.message for s in COMPLETION_SIGNALS):
            issues.append("[learning_compliance] 学生尚未充分尝试，AI 不应直接给出完整项目代码")

    # ============ 6. Safety / Integrity ============
    # AI 编造运行结果
    if any(s in resp.message for s in FABRICATION_SIGNALS):
        # 只在非 reviewer 模式下检查（reviewer 可以引用 CI 证据）
        if mode != "reviewer":
            issues.append("[safety] AI 不得编造运行结果，应让学生自行验证")
    # Debugger 编造诊断结论
    if mode == "debugger" and resp.suspected_cause:
        if any(s in resp.suspected_cause for s in ["已确认", "确定是", "一定是"]):
            issues.append("[safety] debugger 不应在未让学生验证前就断定根因")

    # ============ 7. System Error Isolation（护栏） ============
    # Reviewer 严禁把系统内部错误（模型服务/HTTP/平台故障）当成学生项目的问题。
    # 命中即判违规 → 上层触发重试；重试后仍命中 → 上层强制降级（不作为学生判定依据）。
    if mode == "reviewer":
        combined = f"{resp.evaluation or ''} {resp.message or ''}".lower()
        if any(re.search(s, combined) for s in SYSTEM_ERROR_SIGNALS):
            issues.append(
                "[system_error_isolation] 评审意见引用了系统内部错误（模型服务/HTTP/平台故障）——"
                "这属于系统故障，不是学生项目的证据，不得作为学生项目的判定依据")

    # ============ 回复长度兜底 ============
    if len(resp.message.strip()) < 10:
        issues.append("回复过短，缺少实质引导")

    return (not issues, issues)
