# -*- coding: utf-8 -*-
"""
Response Validator V1.6：AI 输出质量控制。

检查项（V1.6 两模式改造：角色检查按"内部行为"而非模式）：
  1. Hint Compliance     — hint_level 低时不过早给答案/代码
  2. Role Compliance     — 按内部行为（拆解/推进/调试）检查必备字段
  3. Context Compliance  — 回复是否偏离当前任务
  4. Learning Compliance — 学生还没尝试，AI 直接完成任务？
  5. Safety / Integrity  — AI 编造运行结果/断言根因？

每项检查返回 violation 对象：{type, severity, reason}
"""
from __future__ import annotations

from schemas import AiResponse, TeachContext

# 出现即视为"过早给答案"的信号词
ANSWER_SIGNALS = ["答案是", "完整代码", "最终答案", "这样做就可", "给你代码", "修好了，代码如下"]
# 出现即视为"给出完整代码"的信号
CODE_SIGNALS = ["def ", "function ", "```", "import ", "const "]
# 编造运行结果的信号
FABRICATION_SIGNALS = ["我已经测试", "运行结果如下", "实际运行输出", "我帮你跑了一下", "测试通过了"]
# 直接替学生完成的信号
COMPLETION_SIGNALS = ["这是完整的项目", "这是最终的", "把这段代码复制", "全部代码如下"]


def validate(resp: AiResponse, ctx: TeachContext) -> tuple[bool, list[str]]:
    """返回 (是否通过, 问题列表)。不通过时上层应提示模型修正。"""
    issues: list[str] = []
    behavior = getattr(ctx, "behavior", "") or ""

    # ============ 1. Hint Compliance ============
    if ctx.hint_level <= 1:
        low_hl = any(s in (resp.hint or "") or s in resp.message for s in ANSWER_SIGNALS)
        has_code = any(s in (resp.hint or "") for s in CODE_SIGNALS)
        if low_hl:
            issues.append(f"[hint_compliance] 当前提示等级 {ctx.hint_level}，不应过早给出完整答案")
        if has_code:
            issues.append(f"[hint_compliance] 当前提示等级 {ctx.hint_level}，不应给出具体代码/完整片段")

    # ============ 2. Role Compliance（按内部行为） ============
    if behavior == "debug":
        # 调试行为应引导学生定位问题，不应直接给完整修复代码
        if resp.hint and any(s in resp.hint for s in CODE_SIGNALS):
            issues.append("[role_compliance] 调试行为禁止直接给出修复代码，应让学生用 verify_steps 自行确认根因")
        if not resp.suspected_cause:
            issues.append("[role_compliance] 调试行为必须给出 suspected_cause")
        if not resp.verify_steps:
            issues.append("[role_compliance] 调试行为必须给出 verify_steps 让学生验证根因")
        if not resp.diagnostic_question:
            issues.append("[role_compliance] 调试行为必须给出 diagnostic_question 以确认报错位置")
    elif behavior == "advance":
        if not resp.current_step:
            issues.append("[role_compliance] 推进行为必须给出 current_step，明确学生当前只需做哪一步")
    elif behavior == "decompose":
        if not resp.hint:
            issues.append("[role_compliance] 拆解行为必须给出 hint（引导方向）")

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

    # ============ 4. Learning Compliance ============
    # 学生还没充分尝试（提示等级低），AI 直接给出完整解决方案
    if ctx.hint_level <= 2:
        if any(s in resp.message for s in COMPLETION_SIGNALS):
            issues.append("[learning_compliance] 学生尚未充分尝试，AI 不应直接给出完整项目代码")

    # ============ 5. Safety / Integrity ============
    # AI 编造运行结果
    if any(s in resp.message for s in FABRICATION_SIGNALS):
        issues.append("[safety] AI 不得编造运行结果，应让学生自行验证")
    # 调试行为编造诊断结论
    if behavior == "debug" and resp.suspected_cause:
        if any(s in resp.suspected_cause for s in ["已确认", "确定是", "一定是"]):
            issues.append("[safety] 调试行为不应在未让学生验证前就断定根因")

    # ============ 回复长度兜底 ============
    if len(resp.message.strip()) < 10:
        issues.append("回复过短，缺少实质引导")

    return (not issues, issues)
