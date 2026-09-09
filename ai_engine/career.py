# -*- coding: utf-8 -*-
"""
Career Text 生成器（V2 修改 3）：只生成一段 100~200 字的"项目经历描述"。

设计要点（方案 5.1）：
  - 模板 + 数据填充，**不用 LLM 自由生成**——同输入必同输出，杜绝文案漂移；
  - 不做完整简历导出 / 作品集页 / PDF（明确不做清单）；
  - 输入：project_id + 各任务验收结果（score / 通过数 / CI 结论）+ GitHub 链接；
  - 模板字段：项目名 / 技术栈（任务 skill）/ 核心功能（任务标题）/
    量化结果（验收通过数 + CI 结论）/ 可验证证据（GitHub 链接）。
"""
from __future__ import annotations

from schemas import SkillKey

# SkillKey -> 简历可读的技术/能力名
SKILL_LABELS: dict[str, str] = {
    "git": "Git 版本管理",
    "prompt": "提示词工程",
    "env_setup": "环境配置",
    "debug": "调试排错",
    "prd": "需求分析",
    "ui_design": "界面设计",
    "vibe_coding": "AI 辅助开发",
    "project_dev": "全栈项目开发",
    "ai_assisted": "AI 协作开发",
    "workflow": "工作流编排",
    "deployment": "部署上线",
    "rag": "RAG 知识库",
    "paper_writing": "论文写作",
}

# 常见项目的技术栈兜底描述（按 project_id；未命中则用技能标签）
_PROJECT_TECH = {
    "project_chatbot": "FastAPI 后端 + 原生前端 + DeepSeek API",
}


def build_career_text(project_id: str,
                      project_title: str,
                      task_results: list[dict],
                      github_url: str = "",
                      skills: list[str] | None = None) -> dict:
    """由验收结果确定性生成一段简历描述。

    task_results 每项：{task_id, task_title, score, passed, total, ci_conclusion}
    返回 {"text": 一段话, "bullets": {"tech": [...], "features": [...], "metrics": [...]}}。
    """
    results = [r for r in task_results if r.get("task_id")]
    if not results:
        return {"text": "", "bullets": {"tech": [], "features": [], "metrics": []}}

    # 技术栈：优先用任务 skill 标签，无则用项目兜底描述
    tech: list[str] = []
    for s in skills or []:
        label = SKILL_LABELS.get(s)
        if label and label not in tech:
            tech.append(label)
    if not tech:
        tech = list(_PROJECT_TECH.get(project_id, []))

    # 核心功能：各任务标题（去重保序）
    features: list[str] = []
    for r in results:
        t = (r.get("task_title") or "").strip()
        if t and t not in features:
            features.append(t)

    # 量化结果：验收通过数 + 平均分 + CI 结论
    total_passed = sum(int(r.get("passed") or 0) for r in results)
    total_items = sum(int(r.get("total") or 0) for r in results)
    scores = [int(r["score"]) for r in results if r.get("score") is not None]
    avg_score = round(sum(scores) / len(scores)) if scores else 0
    ci_ok = any((r.get("ci_conclusion") or "") == "success" for r in results)
    ci_text = "GitHub Actions 测试通过" if ci_ok else ""

    metrics = [f"自动验收通过 {total_passed}/{total_items} 项"]
    if scores:
        metrics.append(f"平均验收分 {avg_score}")
    if ci_ok:
        metrics.append(ci_text)

    # —— 组装正文（100~200 字目标）——
    feature_text = "、".join(features[:4])
    tech_text = "、".join(tech[:4]) if tech else "前后端 Web 开发"
    sent1 = f"独立完成「{project_title}」项目：{feature_text}。"
    sent2 = f"技术栈为{tech_text}。"
    sent3 = f"项目通过 {total_passed}/{total_items} 项自动验收"
    if ci_ok:
        sent3 += "，GitHub Actions 测试通过"
    sent3 += "。"
    sent4 = f"代码仓库与运行说明可公开验证（{github_url}）。" if github_url else "运行说明与验收记录可复核。"

    text = sent1 + sent2 + sent3 + sent4
    return {"text": text, "bullets": {"tech": tech, "features": features, "metrics": metrics}}
