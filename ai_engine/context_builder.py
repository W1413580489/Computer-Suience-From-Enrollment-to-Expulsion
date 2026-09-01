# -*- coding: utf-8 -*-
"""
Context Builder：根据学生当前任务，从课程结构 + chunks.jsonl 组装教学上下文。

工作方式：
  1. 根据 task.chunk_key 的 section_path 前缀，从 RAG 数据库检索相关 chunk 文本
  2. 组装任务目标 / 操作步骤 / 验收标准，连同检索到的材料一起注入 Prompt
"""
from __future__ import annotations

from schemas import Student, TeachContext, TeachRequest
from course_data import get_project, get_rubrics, get_stage, get_task
from course_data import chunks_by_section_path
from hint import calculate_hint_level


def _retrieve_material(chunk_key: str, student: Student, task_id: str) -> list[str]:
    """按 section_path 前缀检索 chunk，取前 N 条作为参考资料。"""
    if not chunk_key:
        return []
    hits = chunks_by_section_path(chunk_key)
    # 优先匹配最精确前缀：去掉文件夹层级干扰
    strict = [c for c in hits if chunk_key in c.get("section_path", "")]
    pool = strict or hits
    texts = []
    seen = set()
    for c in pool:
        t = c.get("text", "").strip()
        if t and t[:40] not in seen:
            seen.add(t[:40])
            texts.append(f"[{c.get('section','')}] {t}")
        if len(texts) >= 6:
            break
    return texts


def build_context(req: TeachRequest, student: Student) -> TeachContext:
    """组装教学上下文。hint_level 由尝试次数推导。"""
    task = get_task(req.task_id) if req.task_id else None
    stage = get_stage(task.stage_id) if task else None
    project = get_project(req.project_id)

    hint_level = calculate_hint_level(
        attempt_count=student.attempt_count.get(req.task_id, 0),
        user_requested_answer=("答案" in req.user_input or "告诉我怎么做" in req.user_input),
    )

    material = []
    if task:
        material = _retrieve_material(task.chunk_key, student, task.id)

    ctx = TeachContext(
        course_title=req.course_id,
        project_title=project.title,
        stage_title=stage.title if stage else "",
        task_title=task.title if task else "(未选择任务)",
        task_objective=task.objective if task else "",
        task_steps=task.steps if task else [],
        rubric_criteria=[r.criterion for r in get_rubrics(req.task_id)],
        material=material,
        hint_level=hint_level,
        skill=task.skill.value if task and task.skill else None,
        source_url=task.source_url if task else "",
        task_id=req.task_id,
    )
    return ctx