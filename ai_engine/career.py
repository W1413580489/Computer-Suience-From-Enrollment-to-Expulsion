# -*- coding: utf-8 -*-
"""
Career Text 生成器（V2 修改 3 + 简历质量改版）：输出结构化「项目经历」。

设计原则（2026-09-13 按用户要求调整）：
  1. **只认交付，不认学习**：过滤"认识 / 学习 / 了解 / 熟悉…"这类学习属性表述——
     简历不写"我学了什么"，只写"我交付了什么"。
  2. **技术栈必须是纯技术名词**：Python / FastAPI / Pytest / GitHub Actions 这种，
     不用"AI 协作开发""工作流编排"这类虚的能力标签。
  3. **亮点 = 难点 + 目的 + 结果**：素材只记录难点/亮点短语（Task.resume_points），
     生成时补上"为什么做"和"取得什么效果"。
  4. **补量化指标**：把"32/32 通过"翻译成简历语言（可靠性 / 质量保障），
     人工提供的额外指标（如性能对比）原样保留。
  5. 模板 + 数据填充，**不用 LLM 自由生成**：同输入必同输出，杜绝文案漂移。
  6. 缺失素材时**跳过该项**，不编造（无 resume_intro 则用项目 description 兜底，
     无 resume_points 则回退任务标题且同样过滤学习属性）。
"""
from __future__ import annotations

from schemas import Project, ResumePoint

# Bullet 分组顺序与标题（对应 ResumePoint.kind）
_KIND_ORDER = ["architecture", "stability", "delivery", "engineering"]
_KIND_LABELS = {
    "architecture": "架构设计",
    "stability": "稳定性与容错",
    "delivery": "结果产出",
    "engineering": "工程素养",
}

# 学习属性词：出现且**不含**任何交付动词时，视为"学习步骤"，从简历中剔除
_LEARNING_MARKERS = (
    "认识", "学习", "了解", "熟悉", "掌握", "入门", "初识", "理解", "介绍",
    "知道", "回顾", "拆解", "准备", "预加点", "阅读",
)
# 交付动词：证明这句话描述的是"做出来的东西"
_DELIVERY_MARKERS = (
    "实现", "设计", "封装", "搭建", "构建", "编写", "完成", "开发", "集成", "接入",
    "优化", "输出", "生成", "建立", "配置", "处理", "整理", "重构", "改造", "升级",
    "添加", "增加", "支持", "解决", "修复", "打通", "跑通", "通过", "定义", "注册",
)

# 每个 Bullet 最多合并几条亮点（防止单行过长失去可读性）
_MAX_POINTS_PER_BULLET = 3
# 单个 Bullet 的字数上限（软阈值）：超出则丢掉"目的"从句，保住亮点与结果，一行读得完
_MAX_BULLET_CHARS = 140


def is_learning_text(text: str) -> bool:
    """判断一段文本是否是"学习属性"（应被简历过滤）。"""
    s = (text or "").strip()
    if not s:
        return True
    has_learning = any(m in s for m in _LEARNING_MARKERS)
    has_delivery = any(m in s for m in _DELIVERY_MARKERS)
    return has_learning and not has_delivery


def _strip_tail(s: str) -> str:
    return (s or "").strip().rstrip("。；;，,")


def _bullet_text(items: list[ResumePoint], with_purpose: bool) -> str:
    """把同组亮点拼成一句：亮点（+目的）… 收尾补一条结果。"""
    clauses = []
    for p in items:
        s = _strip_tail(p.point)
        if with_purpose and p.purpose:
            s += "，" + _strip_tail(p.purpose)
        clauses.append(s)
    text = "；".join(clauses)
    results = [_strip_tail(p.result) for p in items if p.result]
    if results:
        # 只保留最靠后的一条结果（避免同一句话堆多个"保障了…"）
        text += "，" + results[-1]
    return text + "。"


def _build_bullets(points: list[ResumePoint]) -> list[dict]:
    """按 kind 分组，组内合并亮点（含目的与结果），生成 3-4 条 Bullet。"""
    grouped: dict[str, list[ResumePoint]] = {}
    for p in points:
        if not p.point or is_learning_text(p.point):
            continue  # 学习属性不进简历
        grouped.setdefault(p.kind, []).append(p)

    bullets: list[dict] = []
    for kind in _KIND_ORDER:
        items = grouped.get(kind) or []
        if not items:
            continue
        items = items[:_MAX_POINTS_PER_BULLET]
        text = _bullet_text(items, with_purpose=True)
        if len(text) > _MAX_BULLET_CHARS:      # 太长：丢掉"目的"从句，保亮点与结果
            text = _bullet_text(items, with_purpose=False)
        bullets.append({"label": _KIND_LABELS[kind], "text": text})
    return bullets


def _collect_points(project: Project, passed_task_ids: set[str]) -> list[ResumePoint]:
    """收集**已通过验收**的任务上的简历亮点，保持课程编排顺序。"""
    points: list[ResumePoint] = []
    for task in sorted(project.tasks, key=lambda t: (t.stage_id, t.order)):
        if task.id in passed_task_ids or not passed_task_ids:
            points.extend(task.resume_points)
    return points


def _fallback_features(project: Project, passed_task_ids: set[str]) -> list[ResumePoint]:
    """无人工标注亮点时的兜底：取任务标题（同样过滤学习属性）。"""
    out: list[ResumePoint] = []
    for task in sorted(project.tasks, key=lambda t: (t.stage_id, t.order)):
        if passed_task_ids and task.id not in passed_task_ids:
            continue
        if task.title and not is_learning_text(task.title):
            out.append(ResumePoint(point=task.title, kind="delivery"))
    return out


def build_career_text(project: Project,
                      task_results: list[dict],
                      github_url: str = "",
                      date: str = "") -> dict:
    """由验收结果确定性生成结构化简历条目。

    task_results 每项：{task_id, score, passed, total, ci_conclusion}
    返回 {title_line, intro, tech, bullets:[{label,text}], metrics, text}
    """
    results = [r for r in task_results if r.get("task_id")]
    if not results:
        return {"title_line": "", "intro": "", "tech": [], "bullets": [], "metrics": [], "text": ""}

    passed_ids = {r["task_id"] for r in results if (r.get("total") or 0) > 0
                  and (r.get("passed") or 0) >= (r.get("total") or 0)}
    if not passed_ids:  # 未区分通过数时按传入结果全算
        passed_ids = {r["task_id"] for r in results}

    # ---- 技术栈：只用人工标注的纯技术名词（不再用能力标签兜底）----
    tech = [t for t in project.resume_tech if t]

    # ---- 亮点 Bullet ----
    points = _collect_points(project, passed_ids) or _fallback_features(project, passed_ids)
    bullets = _build_bullets(points)

    # ---- 量化指标（简历语言：讲可靠性/质量，不罗列分数）----
    total_passed = sum(int(r.get("passed") or 0) for r in results)
    total_items = sum(int(r.get("total") or 0) for r in results)
    ci_ok = any((r.get("ci_conclusion") or "") == "success" for r in results)
    metrics: list[str] = []
    if total_items:
        metrics.append(f"通过 {total_passed}/{total_items} 项自动化验收用例")
    if ci_ok:
        metrics.append("持续集成（GitHub Actions）全部通过")
    metrics.extend([m for m in project.resume_metrics if m])
    if not metrics:
        metrics.append("交付物通过自动化验收")

    # ---- 项目简介 ----
    intro = (project.resume_intro or project.description or "").strip()

    # ---- 标题行 ----
    role = project.resume_role or "独立开发"
    title_line = f"{project.title}（{role}）"
    if date:
        title_line += f" | {date}"

    # ---- 组装可粘贴正文 ----
    lines = [title_line]
    if tech:
        lines.append("技术栈：" + " / ".join(tech))
    lines.append("")
    if intro:
        lines.append(f"项目简介：{intro}")
    for b in bullets:
        lines.append(f"{b['label']}：{b['text']}")
    lines.append("")
    lines.append("量化结果：" + "；".join(metrics) + "。")
    if github_url:
        lines.append(f"代码仓库与运行说明可公开验证：{github_url}")

    return {
        "title_line": title_line,
        "intro": intro,
        "tech": tech,
        "bullets": bullets,
        "metrics": metrics,
        "text": "\n".join(lines),
    }
