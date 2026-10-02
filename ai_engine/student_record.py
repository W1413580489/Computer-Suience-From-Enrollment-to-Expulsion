# -*- coding: utf-8 -*-
"""P6：项目记录（简历历史结果 + 项目复盘）——从 SQLite 真相源派生，零 LLM 依赖。

依据：《AI 项目导师执行方案修正意见》§16（简历 / 面试 / 复盘）

设计原则：
  - 简历：不改动既有 `career.build_career_text` 的确定性模板，只补一个"服务端历史结果"
    取数口——前端把它作为 `/api/career/text` 的可选输入（服务端优先，localStorage 兜底），
    避免一次接口失败导致整个简历模块为空。
  - 项目复盘：数据全部来自 `submissions` / `evaluations`（含评审时已落库的 GitHub revision
    摘要），不新增 LLM 调用；同输入必同输出，可重复调用。
"""
from __future__ import annotations

import json

from course_data import get_project
from store import store as db


def _criteria_stats(criteria_json: str) -> tuple[int, int]:
    """从 `evaluation.model_dump()` 里取 acceptance criteria 的 (通过数, 总数)。

    口径与前端评审卡一致：`criteria` 只含 acceptance 角色，逐条按 status == PASS 计数。
    """
    try:
        ev = json.loads(criteria_json or "{}")
    except json.JSONDecodeError:
        return 0, 0
    criteria = ev.get("criteria") if isinstance(ev, dict) else None
    if not isinstance(criteria, list):
        return 0, 0
    items = [c for c in criteria if isinstance(c, dict)]
    passed = sum(1 for c in items if c.get("status") == "PASS")
    return passed, len(items)


def build_career_results(student_id: str, project_id: str) -> list[dict]:
    """本项目"每个任务最新一次评审"的结果（与前端 `CareerTaskResult` 同构）。

    字段：{task_id, score, passed, total, ci_conclusion, status}
      - passed/total：acceptance criteria 的通过数 / 总数（供 build_career_text 判定通过）
      - ci_conclusion：该次提交的 CI 结论（success / failure / ''）
      - status：该任务最新评审状态（前端据此更新"已完成任务"的服务端口径）
    """
    rows = db.latest_project_evaluations(student_id, project_id)
    out: list[dict] = []
    for r in rows:
        passed, total = _criteria_stats(r.get("criteria_json") or "")
        tid = r.get("task_id") or ""
        if not tid:
            continue
        out.append({
            "task_id": tid,
            "score": int(r.get("score") or 0),
            "passed": passed,
            "total": total,
            "ci_conclusion": r.get("ci_conclusion") or "",
            "status": r.get("status") or "NEED_REVIEW",
        })
    return out


def _revision_files(revision_json: str) -> tuple[list[str], int]:
    """解析 GitHub compare 摘要 → (变更文件名列表, 变更文件总数)。"""
    try:
        rev = json.loads(revision_json or "{}")
    except json.JSONDecodeError:
        return [], 0
    if not isinstance(rev, dict):
        return [], 0
    files = rev.get("files")
    names = [str(f.get("filename") or "") for f in files if isinstance(f, dict)] if isinstance(files, list) else []
    names = [n for n in names if n]
    total = int(rev.get("files_changed") or len(names) or 0)
    return names, total


def build_project_retro(student_id: str, project_id: str) -> dict | None:
    """项目复盘：提交时间线 + 每任务尝试/通过统计（纯确定性数据，零 LLM）。

    项目不存在返回 None。无任何提交时返回 totals 全 0 的结构（前端据此不展示复盘区）。
    """
    project = get_project(project_id)
    if not project:
        return None
    titles = {t.id: t.title for t in project.tasks}
    subs = db.list_project_submissions(student_id, project_id)

    timeline: list[dict] = []
    per_task: dict[str, dict] = {}
    for s in subs:
        tid = s.get("task_id") or ""
        status = s.get("status") or "NOT_EVALUATED"
        score = int(s.get("score") or 0)
        head_sha = s.get("eval_head_sha") or s.get("sub_head_sha") or ""
        names, files_changed = _revision_files(
            s.get("eval_revision_json") or s.get("sub_revision_json") or "")
        timeline.append({
            "submission_id": s.get("submission_id") or "",
            "task_id": tid,
            "task_title": titles.get(tid, tid),
            "submitted_at": s.get("submitted_at") or "",
            "head_sha": head_sha,
            "status": status,
            "score": score,
            "changed_files": names,
            "files_changed": files_changed,
            "is_revision": bool(s.get("parent_submission_id")),
        })

        agg = per_task.setdefault(tid, {
            "task_id": tid, "title": titles.get(tid, tid),
            "attempts": 0, "passed_attempts": 0, "failed_attempts": 0,
            "latest_status": "", "latest_score": 0, "passed": False,
            "first_submitted_at": "", "last_submitted_at": "",
        })
        agg["attempts"] += 1
        if status == "PASS":
            agg["passed_attempts"] += 1
        elif status == "FAIL":
            agg["failed_attempts"] += 1
        agg["latest_status"] = status
        agg["latest_score"] = score
        agg["passed"] = status == "PASS"
        if not agg["first_submitted_at"]:
            agg["first_submitted_at"] = s.get("submitted_at") or ""
        agg["last_submitted_at"] = s.get("submitted_at") or ""

    tasks = sorted(per_task.values(), key=lambda t: (t["first_submitted_at"], t["task_id"]))
    return {
        "project_id": project.id,
        "project_title": project.title,
        "source": "sqlite",
        "totals": {
            "submissions": len(timeline),
            "tasks_attempted": len(tasks),
            "tasks_passed": sum(1 for t in tasks if t["passed"]),
            "passed_attempts": sum(1 for s in timeline if s["status"] == "PASS"),
            "failed_attempts": sum(1 for s in timeline if s["status"] == "FAIL"),
            "need_review_attempts": sum(1 for s in timeline if s["status"] == "NEED_REVIEW"),
        },
        "tasks": tasks,
        "timeline": timeline,
    }