# -*- coding: utf-8 -*-
"""P4 场景验证：Project State（状态机聚合）+ completion_required / depends_on。

覆盖：
  [A] 配置生效与一致性（必做任务白名单、depends_on 合法性、无 typo）
  [B] latest_evaluations 归并（同任务多次评审取最新）
  [C] compute_project_state 四态（NOT_STARTED / IN_PROGRESS / COMPLETED / BLOCKED）
      + theory FAIL 不阻断项目完成（P1 语义与 P4 聚合衔接）
  [D] task_blocked_reason（仅提示，不阻断）
  [E] 缓存隔离：blocked_reason / project_state 必须在 save_review_result 之后挂
用独立临时库跑，不触碰 data/engine.db，不触网。
"""
import os
import re
import tempfile

TMP = tempfile.mkdtemp()
os.environ["XKZ_DB_PATH"] = os.path.join(TMP, "p4.db")

from course_data import get_project, get_task, _PROJECT_BUILDERS, _P4_REQUIRED, _P4_DEPENDS_ON  # noqa: E402
from project_state import (BLOCKED, COMPLETED, IN_PROGRESS, NOT_STARTED,  # noqa: E402
                           compute_project_state, task_blocked_reason)
from review import compute_evaluation                                    # noqa: E402
from schemas import EvaluationRole, ReviewCriterion, ReviewStatus, Rubric  # noqa: E402
from store import store as db                                            # noqa: E402

# ---- A. 配置生效与一致性 ----
all_task_ids = set()
for pid in _PROJECT_BUILDERS:
    all_task_ids |= {t.id for t in get_project(pid).tasks}

assert _P4_REQUIRED <= all_task_ids, ("白名单含不存在的 task_id", _P4_REQUIRED - all_task_ids)
for _t, _deps in _P4_DEPENDS_ON.items():
    assert _t in all_task_ids, ("depends_on 主体不存在", _t)
    assert set(_deps) <= all_task_ids, ("depends_on 前置不存在", _t, _deps)

assert len(_P4_REQUIRED) == 20, len(_P4_REQUIRED)
assert {t.id for t in get_project("project_chatbot").tasks if t.completion_required} == \
       {"task_backend", "task_frontend", "task_link"}
assert {t.id for t in get_project("project_agent").tasks if t.completion_required} == \
       {"c2t02", "c2t03", "c2t04", "c2t05", "c2t06", "c2t07", "c2t08", "c2t09"}
assert sum(1 for t in get_project("project_mcp_build").tasks if t.completion_required) == 4
assert sum(1 for t in get_project("project_mcp_test").tasks if t.completion_required) == 5
# 默认 False：准备/铺垫/提交验收类任务不纳入必做
assert get_task("task_setup").completion_required is False
assert get_task("task_review").completion_required is False
assert get_task("c3_t03").completion_required is False
assert get_task("task_link").depends_on == ["task_backend", "task_frontend"]
assert get_task("c3_t08").depends_on == ["c3_t07"]  # 跨项目依赖
assert get_task("task_backend").depends_on == []
assert get_project("project_chatbot") is get_project("project_chatbot")  # 缓存后配置只应用一次
print("[A] P4 配置生效：20 个必做任务白名单 / depends_on 全部指向真实 task / 默认 False 未被误改")

# ---- B. latest_evaluations 归并（同任务多次评审 → 取最新）----
db.save_evaluation(submission_id="b_1", student_id="stu1", task_id="task_backend",
                   status="FAIL", score=10, passed=False)
db.save_evaluation(submission_id="b_2", student_id="stu1", task_id="task_backend",
                   status="PASS", score=100, passed=True)
m = db.latest_evaluations("stu1", ["task_backend", "task_frontend"])
assert m["task_backend"]["status"] == "PASS" and m["task_backend"]["passed"] is True, m
assert "task_frontend" not in m
assert db.latest_evaluations("", ["task_backend"]) == {}
assert db.latest_evaluations("stu1", []) == {}
print("[B] latest_evaluations 同任务多次评审取最新；空 student/空任务列表安全返回")

# ---- C. compute_project_state 四态 ----
assert compute_project_state("fresh", "no_such_project") is None

st = compute_project_state("fresh", "project_chatbot")
assert st["state"] == NOT_STARTED, st
assert st["completion_defined"] is True and st["required_total"] == 3 and st["required_passed"] == 0
assert st["next_task"] == {"task_id": "task_backend", "title": "写后端接口"}, st["next_task"]

# 部分通过 → IN_PROGRESS；未满足前置的必做任务进 blocked_tasks
db.save_evaluation(submission_id="c_1", student_id="stu2", task_id="task_backend",
                   status="PASS", score=100, passed=True)
st = compute_project_state("stu2", "project_chatbot")
assert st["state"] == IN_PROGRESS, st
assert st["required_passed"] == 1
assert st["next_task"]["task_id"] == "task_frontend"
assert [b["task_id"] for b in st["blocked_tasks"]] == ["task_link"], st["blocked_tasks"]
assert st["blocked_tasks"][0]["missing"] == ["task_frontend"]

# 全部必做 PASS → COMPLETED（task_review 非必做，不参与判定）
for _tid in ("task_frontend", "task_link"):
    db.save_evaluation(submission_id=f"c_{_tid}", student_id="stu2", task_id=_tid,
                       status="PASS", score=100, passed=True)
st = compute_project_state("stu2", "project_chatbot")
assert st["state"] == COMPLETED, st
assert st["required_passed"] == 3 and st["blocked_tasks"] == [] and st["next_task"] is None
print("[C1] NOT_STARTED → IN_PROGRESS → COMPLETED（只认必做任务）")

# theory FAIL 不阻断项目完成（compute_evaluation 判定 PASS → 项目聚合为 COMPLETED）
_rubrics = [
    Rubric(id="r_acc", evaluation_role=EvaluationRole.acceptance, weight=2),
    Rubric(id="r_thy", evaluation_role=EvaluationRole.theory, weight=1),
    Rubric(id="r_ref", evaluation_role=EvaluationRole.reflection, weight=1),
]
_crit = [
    ReviewCriterion(rubric_id="r_acc", status=ReviewStatus.PASS, evidence="code", reason="交付达标"),
    ReviewCriterion(rubric_id="r_thy", status=ReviewStatus.FAIL, evidence="description", reason="未讲清原理"),
    ReviewCriterion(rubric_id="r_ref", status=ReviewStatus.FAIL, evidence="description", reason="未写复盘"),
]
_ev = compute_evaluation(_crit, _rubrics, next_step="")
assert _ev.status.value == "PASS" and _ev.learning_gaps, _ev.model_dump()
for _tid in ("c3_t08", "c3_t09", "c3_t10", "c3_t11", "c3_t12"):
    db.save_evaluation(submission_id=f"c2_{_tid}", student_id="stu3", task_id=_tid,
                       status="PASS", score=100, passed=True)
st = compute_project_state("stu3", "project_mcp_test")
assert st["state"] == COMPLETED, st
print("[C2] theory/reflection FAIL 不影响项目完成（acceptance 全 PASS → COMPLETED）")

# ---- D. 状态机 BLOCKED（跨项目前置未满足）----
db.save_evaluation(submission_id="d_08", student_id="stu4", task_id="c3_t08",
                   status="FAIL", score=20, passed=False)
st = compute_project_state("stu4", "project_mcp_test")
assert st["state"] == BLOCKED, st
assert any(b["task_id"] == "c3_t08" and b["missing"] == ["c3_t07"] for b in st["blocked_tasks"])
# 未开始优先于 BLOCKED（新生打开 project_mcp_test 不应当头 BLOCKED）
assert compute_project_state("fresh", "project_mcp_test")["state"] == NOT_STARTED
# 补上跨项目前置 → 重新可做
db.save_evaluation(submission_id="d_07", student_id="stu4", task_id="c3_t07",
                   status="PASS", score=100, passed=True)
st = compute_project_state("stu4", "project_mcp_test")
assert st["state"] == IN_PROGRESS, st
assert st["next_task"]["task_id"] == "c3_t08"
print("[D] BLOCKED：跨项目前置未满足且已开始 → BLOCKED；补上前置后回到 IN_PROGRESS")

# ---- E. task_blocked_reason（仅提示，不阻断）----
assert task_blocked_reason("fresh", "task_backend") is None      # 无前置
assert task_blocked_reason("fresh", "no_such_task") is None      # 任务不存在
r = task_blocked_reason("fresh", "task_link")
assert r and r["blocked"] is True
assert set(r["missing"]) == {"task_backend", "task_frontend"}
assert "建议先完成前置任务" in r["reason"] and "写后端接口" in r["reason"]
assert task_blocked_reason("stu2", "task_link") is None          # 前置已 PASS
print("[E] task_blocked_reason 正常：无前置→None；前置未满足→可读 reason；满足后→None")

# ---- F. 缓存隔离：学生态必须在 save_review_result 之后挂 ----
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py"), encoding="utf-8").read()
assert src.count("attach_student_state(") == 4, src.count("attach_student_state(")  # 1 定义 + 3 调用
# 两条非缓存路径：save_review_result 紧接其后才是挂学生态
_pairs = re.findall(
    r"save_review_result\([^\n]*\n(?:[^\n]*\n){0,4}?\s*attach_student_state\(", src)
assert len(_pairs) == 2, len(_pairs)
# 缓存命中路径：只挂学生态，绝不回写缓存
_hit = src[src.index("if hit is not None:"):]
_hit = _hit[:_hit.index('return {"ok": True, "data": data}')]
assert "save_review_result" not in _hit and "attach_student_state" in _hit
print("[F] 缓存隔离：blocked_reason / project_state 在 save_review_result 之后挂，不进幂等缓存")

print("ALL P4 TESTS PASSED")