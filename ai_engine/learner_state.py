# -*- coding: utf-8 -*-
"""P5：Learner State（技能四态 + 学习缺口）——纯读侧聚合，不新增表、不新增写入。

依据：《AI 项目导师执行方案修正意见》§14 / §15

四态（刻意不做 Mastery 分数——系统现有证据不足以支撑"掌握度 87"这种精确数值）：

    UNSEEN     没有任何相关学习/项目证据
    EXPOSED    在课程/导师中接触过（该任务有过对话会话）
    PRACTICED  实际完成过对应任务或练习（该任务提交并产生了评审记录）
    EVIDENCED  项目验收中产生了与该技能相关的有效证据（该任务最新评审 PASS）

硬原则：**EVIDENCED ≠ MASTERED**——技能过关与理论缺口可以并存，
因此 Learner State 同时返回 skill_state 与 learning_gaps，而不是一个分数。

数据来源全部是已有真相源（不新增实体，可重复计算、无双重计数）：
    - 技能归属     ：Task.skill（course_data 课程配置）
    - EXPOSED      ：sessions 表（student_id, task_id）
    - PRACTICED/EVIDENCED：evaluations 表（每份提交一行；review_results 只是幂等缓存）
    - Learning Gap ：evaluations.criteria_json 里的 learning_gaps（theory 未达标）

学习缺口不会因一次失败被永久标记为"不懂"：同一 (任务, rubric) 的最新一次评审
不再报该缺口时，标记 resolved（保留历史与首见时间）。
"""
from __future__ import annotations

import hashlib
import json

from course_data import _PROJECT_BUILDERS, get_project
from store import store as db

# 四态（值即对外契约，前端按字符串消费）
UNSEEN = "UNSEEN"
EXPOSED = "EXPOSED"
PRACTICED = "PRACTICED"
EVIDENCED = "EVIDENCED"

_LEVEL = {UNSEEN: 0, EXPOSED: 1, PRACTICED: 2, EVIDENCED: 3}


def _confidence(occurrences: int) -> str:
    """离散置信度（不做机器学习）：同一缺口在几次不同提交中被复现。"""
    if occurrences >= 3:
        return "high"
    if occurrences == 2:
        return "medium"
    return "low"


def task_skill_map() -> dict[str, str]:
    """task_id → skill_key（取自课程配置，不硬编码）。"""
    out: dict[str, str] = {}
    for pid in _PROJECT_BUILDERS:
        proj = get_project(pid)
        if not proj:
            continue
        for t in proj.tasks:
            if t.skill:
                out[t.id] = t.skill.value
    return out


def _load_gaps(row: dict) -> list[dict]:
    try:
        ev = json.loads(row.get("criteria_json") or "{}")
    except json.JSONDecodeError:
        return []
    if not isinstance(ev, dict):
        return []
    gaps = ev.get("learning_gaps")
    return [g for g in gaps if isinstance(g, dict)] if isinstance(gaps, list) else []


def compute_learner_state(student_id: str) -> dict:
    """聚合该学生的技能四态与学习缺口（只读、可重复调用）。

    状态取该技能下所有任务的**最高态**：只要有一个任务的验收通过，该技能即 EVIDENCED；
    若该任务后续评审未通过，其自身贡献回落到 PRACTICED（以最新证据为准）。
    """
    s2t = task_skill_map()
    exposed = set(db.list_session_task_ids(student_id))
    evals = db.list_student_evaluations(student_id)

    latest: dict[str, dict] = {}
    for row in evals:
        latest[row["task_id"]] = row

    state_of: dict[str, str] = {}
    tasks_of: dict[str, list[str]] = {}
    for tid, skill in s2t.items():
        tasks_of.setdefault(skill, []).append(tid)
        row = latest.get(tid)
        if row is not None:
            level = EVIDENCED if bool(row["passed"]) else PRACTICED
        elif tid in exposed:
            level = EXPOSED
        else:
            level = UNSEEN
        if _LEVEL[level] > _LEVEL.get(state_of.get(skill, UNSEEN), 0):
            state_of[skill] = level

    skills = [{
        "skill_key": skill,
        "state": state_of.get(skill, UNSEEN),
        "task_count": len(tids),
    } for skill, tids in tasks_of.items()]
    skills.sort(key=lambda s: (-_LEVEL[s["state"]], s["skill_key"]))

    # ---- Learning Gap：按 (任务, rubric) 归并，去重依据是"提交"（evaluations 一行一份提交）----
    # 新旧判定用行序（evals 已按 created_at, rowid 升序）而非 created_at——
    # created_at 只到秒，同秒内两次提交用时间比较会判定不出"已解决"。
    gaps: dict[tuple[str, str], dict] = {}
    gap_idx: dict[tuple[str, str], int] = {}
    latest_idx: dict[str, int] = {}
    for idx, row in enumerate(evals):
        latest_idx[row["task_id"]] = idx
        for g in _load_gaps(row):
            rid = g.get("rubric_id") or ""
            key = (row["task_id"], rid)
            gap_idx[key] = idx
            item = gaps.get(key)
            if item is None:
                gaps[key] = {
                    "gap_id": hashlib.sha1(
                        f"{student_id}:{row['task_id']}:{rid}".encode("utf-8")).hexdigest()[:12],
                    "skill_key": s2t.get(row["task_id"], ""),
                    "source_task": row["task_id"],
                    "rubric_id": rid,
                    "reason": g.get("reason") or "",
                    "occurrences": 1,
                    "confidence": "low",
                    "resolved": False,
                    "first_seen_at": row["created_at"],
                    "last_seen_at": row["created_at"],
                    "resolved_at": "",
                }
            else:
                item["occurrences"] += 1
                item["last_seen_at"] = row["created_at"]
                if g.get("reason"):
                    item["reason"] = g["reason"]

    # 已解决：该任务"最新一次提交"不再报这条缺口 → 标记 resolved（保留历史，不永久标记"不懂"）
    for key, item in gaps.items():
        tid = key[0]
        if gap_idx.get(key, -1) < latest_idx.get(tid, -1):
            item["resolved"] = True
            item["resolved_at"] = latest[tid]["created_at"]
        item["confidence"] = _confidence(item["occurrences"])

    gap_list = list(gaps.values())
    gap_list.sort(key=lambda g: g["last_seen_at"], reverse=True)
    gap_list.sort(key=lambda g: 1 if g["resolved"] else 0)  # 稳定排序 → 未解决在前

    return {
        "student_id": student_id,
        "skills": skills,
        "learning_gaps": gap_list,
        "counts": {
            "skills_evidenced": sum(1 for s in skills if s["state"] == EVIDENCED),
            "skills_practiced": sum(1 for s in skills if s["state"] == PRACTICED),
            "skills_exposed": sum(1 for s in skills if s["state"] == EXPOSED),
            "gaps_open": sum(1 for g in gap_list if not g["resolved"]),
            "gaps_total": len(gap_list),
        },
    }