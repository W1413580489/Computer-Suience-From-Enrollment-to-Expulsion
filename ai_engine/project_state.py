# -*- coding: utf-8 -*-
"""P4：Project State / Task Blocked Reason（服务层聚合，不新增数据库实体）。

依据：《AI 项目导师执行方案修正意见》§12 / §13

设计原则：
  - Project State 是【计算值】而非新真相源：由任务评审历史（evaluations 表）
    + 项目任务配置（Task.completion_required / Task.depends_on）聚合得出，
    第一版不新增复杂数据库实体。
  - 项目完成判定只认 completion_required 的 Task：
      全部必做 Task 达到 PASS → COMPLETED
      必做任务未配置（空集）→ 不做完成判定（completion_defined=False），
      避免"空必做集"使项目瞬间 COMPLETED。
  - Task Dependency 非常克制：只回答"能不能自然进入下一阶段"，输出 blocked_reason
    供前端提示，不做强制门禁、不做 DAG 引擎（零基础学生需要探索自由）。
"""
from __future__ import annotations

from course_data import get_project, get_task
from schemas import Project, ReviewStatus, Task
from store import store as db

# Project State（§12 状态机）
NOT_STARTED = "NOT_STARTED"
IN_PROGRESS = "IN_PROGRESS"
COMPLETED = "COMPLETED"
BLOCKED = "BLOCKED"

NOT_EVALUATED = "NOT_EVALUATED"


def _pass(status: str | None) -> bool:
    return (status or "") == ReviewStatus.PASS.value


def _dep_label(task_id: str) -> str:
    t = get_task(task_id)
    return f"{t.title}（{task_id}）" if t else task_id


def _missing_deps(task: Task, statuses: dict[str, str]) -> list[str]:
    """未满足的前置任务（前置的"最新一次评审"非 PASS 即视为未满足）。"""
    return [d for d in task.depends_on if not _pass(statuses.get(d))]


def _reason(missing: list[str]) -> str:
    return "建议先完成前置任务：" + "、".join(_dep_label(d) for d in missing) + "。"


def task_blocked_reason(student_id: str, task_id: str) -> dict | None:
    """某个任务是否被前置任务挡住（仅提示，不阻断）。

    None  = 无前置 或 前置已达标 → 可以自然进入；
    dict  = {"task_id","blocked","reason","missing"} → 前端据此提示"建议先完成 X"。
    """
    task = get_task(task_id)
    if not task or not task.depends_on:
        return None
    evals = db.latest_evaluations(student_id, list(task.depends_on))
    statuses = {tid: (row.get("status") or "") for tid, row in evals.items()}
    missing = _missing_deps(task, statuses)
    if not missing:
        return None
    return {
        "task_id": task_id,
        "blocked": True,
        "reason": _reason(missing),
        "missing": missing,
    }


def compute_project_state(student_id: str, project_id: str) -> dict | None:
    """聚合项目状态（项目不存在返回 None）。只读，可重复调用。"""
    project: Project | None = get_project(project_id)
    if not project:
        return None

    required = [t for t in project.tasks if t.completion_required]
    # 依赖任务也要纳入查询：依赖可能是跨项目的（如 c3_t08 → c3_t07），
    # 只查本项目任务会让跨项目依赖永远判为"未满足"。
    dep_ids = [d for t in project.tasks for d in t.depends_on]
    evals = db.latest_evaluations(student_id, [t.id for t in project.tasks] + dep_ids)
    statuses = {tid: (row.get("status") or "") for tid, row in evals.items()}

    required_tasks = [{
        "task_id": t.id,
        "title": t.title,
        "status": statuses.get(t.id) or NOT_EVALUATED,
        "passed": _pass(statuses.get(t.id)),
    } for t in required]

    blocked_tasks = []
    for t in required:
        if _pass(statuses.get(t.id)):
            continue
        missing = _missing_deps(t, statuses)
        if missing:
            blocked_tasks.append({
                "task_id": t.id, "title": t.title,
                "reason": _reason(missing), "missing": missing,
            })
    blocked_ids = {b["task_id"] for b in blocked_tasks}

    passed_count = sum(1 for r in required_tasks if r["passed"])
    completion_defined = bool(required)
    # "已开始"信号：项目内任一任务（含非必做的准备/铺垫任务）有评审记录
    started = any(statuses.get(t.id) for t in project.tasks)

    if completion_defined and passed_count == len(required):
        state = COMPLETED
    elif not started:
        state = NOT_STARTED
    elif any(not r["passed"] and r["task_id"] not in blocked_ids for r in required_tasks):
        # 还有"无未满足前置"的必做任务可做 → 进行中
        state = IN_PROGRESS
    elif blocked_tasks:
        state = BLOCKED
    else:
        state = IN_PROGRESS

    # 下一步建议：第一个"未通过且未被前置挡住"的必做任务
    next_task = next(
        ({"task_id": r["task_id"], "title": r["title"]}
         for r in required_tasks if not r["passed"] and r["task_id"] not in blocked_ids),
        None)

    return {
        "project_id": project.id,
        "project_title": project.title,
        "student_id": student_id,
        "state": state,
        "completion_defined": completion_defined,
        "required_total": len(required),
        "required_passed": passed_count,
        "required_tasks": required_tasks,
        "blocked_tasks": blocked_tasks,
        "next_task": next_task,
    }