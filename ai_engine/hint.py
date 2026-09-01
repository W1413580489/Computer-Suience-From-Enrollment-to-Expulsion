# -*- coding: utf-8 -*-
"""
Hint Level 状态机：根据尝试次数与是否直接索要答案，逐步提升提示程度。

映射（规格书 V1 定义）：
  0 不提示（仅反问/引导方向）
  1 提示方向/关键点
  2 给出思路步骤
  3 给出具体做法
  4 给出关键代码/答案片段
  5 直接给出解决方案
"""
from __future__ import annotations


def calculate_hint_level(attempt_count: int, user_requested_answer: bool = False) -> int:
    """计算当前应启用的 Hint Level（对齐规格书 V1 定义）。

    attempt_count: 学生对同一任务尝试失败的次数（前端 onSubmit 递增）。
    user_requested_answer: 学生是否明确说"给我答案 / 直接告诉我怎么做"。
    规则：直接索要答案 + 尝试>=4 → 5；其余按尝试次数 4→3→2→1 逐级提升。
    """
    if user_requested_answer and attempt_count >= 4:
        return 5
    if attempt_count >= 4:
        return 4
    if attempt_count >= 3:
        return 3
    if attempt_count >= 2:
        return 2
    if attempt_count >= 1:
        return 1
    return 0


def next_hint_level(current: int) -> int:
    """当一次引导未奏效时，升一级（上限 5）。"""
    return min(current + 1, 5)


def describe(level: int) -> str:
    desc = {
        0: "不提示，仅反问/引导方向",
        1: "提示方向/关键点",
        2: "给出思路步骤",
        3: "给出具体做法",
        4: "给出关键代码/答案片段",
        5: "直接给出解决方案",
    }
    return desc.get(level, "未知")