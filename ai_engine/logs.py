# -*- coding: utf-8 -*-
"""
结构化事件日志 + AI Evaluation 统计（Sprint 6）。

对齐规格书「V1 最重要的日志」：不只存聊天，还要存可分析的字段——
  student_id / project_id / task_id / mode
  attempt_count / hint_level
  user_message / ai_response / next_action / accepted_by_user
  task_completed / review_status

统计用途：哪些任务最卡？哪个 Hint Level 最有效？AI 是否过早给答案？完成后分率？
"""
from __future__ import annotations

import json
import threading
import time
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR.parent / "data" / "logs"
EVENTS_FILE = LOGS_DIR / "session_events.jsonl"

_lock = threading.Lock()


def log_event(event: dict | None = None, **kw) -> None:
    """追加一条事件日志（线程安全）。key 字段可经 kwargs 传入。"""
    ev = dict(event or {})
    ev.update(kw)
    ev.setdefault("ts", round(time.time(), 3))
    with _lock:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")


def read_events(limit: int = 5000) -> list[dict]:
    if not EVENTS_FILE.exists():
        return []
    events = []
    with open(EVENTS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events[-limit:]


def set_accepted(session_id: str, task_id: str, accepted: bool) -> bool:
    """就地更新该会话+任务最近一条 teach 事件的 accepted_by_user。返回是否命中。"""
    if not EVENTS_FILE.exists():
        return False
    lines = []
    hit = False
    with _lock:
        with open(EVENTS_FILE, encoding="utf-8") as f:
            lines = f.readlines()
        # 从后往前找最近一条匹配的 teach 事件
        for i in range(len(lines) - 1, -1, -1):
            try:
                ev = json.loads(lines[i])
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "teach" and ev.get("session_id") == session_id and ev.get("task_id") == task_id:
                ev["accepted_by_user"] = bool(accepted)
                lines[i] = json.dumps(ev, ensure_ascii=False) + "\n"
                hit = True
                break
        if hit:
            with open(EVENTS_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
    return hit


def compute_stats(events: list[dict] | None = None) -> dict:
    """从事件日志聚合 AI Evaluation 指标。"""
    events = events if events is not None else read_events()
    teach = [e for e in events if e.get("type") == "teach"]
    reviews = [e for e in events if e.get("type") == "review"]

    # 各任务尝试量（哪些最容易卡 → 卡住的=尝试多但未完成）
    per_task_attempts = Counter(e["task_id"] for e in teach if e.get("task_id"))

    # Hint 分布
    hint_hist = Counter(e.get("hint_level", 0) for e in teach)

    # 质控警告计数（AI 是否过早给答案）
    early_answers = 0
    total_issues = 0
    for e in teach:
        w = e.get("quality_warnings") or []
        total_issues += len(w)
        if any("过早" in i or "完整代码" in i or "具体代码" in i for i in w):
            early_answers += 1

    # 完成情况
    completed_tasks = {e["task_id"] for e in reviews if e.get("task_completed")}
    reviewed_tasks = {e["task_id"] for e in reviews}

    mode_hist = Counter(e.get("mode") for e in teach)

    # 各任务卡住程度：尝试数 >= 3 且未在 review 中通过
    blocked = {}
    for tid, n in per_task_attempts.items():
        blocked[tid] = n >= 3 and tid not in completed_tasks

    return {
        "total_teach_calls": len(teach),
        "total_reviews": len(reviews),
        "per_task_attempts": dict(per_task_attempts),
        "completed_tasks": sorted(completed_tasks),
        "reviewed_tasks": sorted(reviewed_tasks),
        "task_completion_rate": round(len(completed_tasks) / len(reviewed_tasks), 3) if reviewed_tasks else 0.0,
        "hint_distribution": {str(k): v for k, v in sorted(hint_hist.items(), key=lambda x: int(x[0]))},
        "mode_distribution": dict(mode_hist),
        "early_answer_warnings": early_answers,
        "total_quality_warnings": total_issues,
        "probably_blocked_tasks": {k: v for k, v in blocked.items() if v},
        "log_file_count": len(teach) + len(reviews),
    }