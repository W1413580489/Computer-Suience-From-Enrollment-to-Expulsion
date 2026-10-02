# -*- coding: utf-8 -*-
"""P5 场景验证：Learner State（技能四态）+ Learning Gap 生命周期。

覆盖：
  [A] 技能归属来自课程配置；空学生 → 全部 UNSEEN；重复调用确定性
  [B] 四态推进 UNSEEN → EXPOSED → PRACTICED → EVIDENCED（数据源：sessions / evaluations）
  [C] Learning Gap 生命周期：首见 → 复现（置信度升级）→ 不再报则 resolved；重复提交不重复计数
  [D] EVIDENCED ≠ MASTERED：技能已取证与理论缺口并存（§14.2 硬原则）
  [E] 端点与接线（/api/ai/learner_state；learner_state 走 attach_student_state 的缓存后挂载）
用独立临时库跑，不触碰 data/engine.db，不触网。
"""
import os
import tempfile

TMP = tempfile.mkdtemp()
os.environ["XKZ_DB_PATH"] = os.path.join(TMP, "p5.db")

from learner_state import (EXPOSED, EVIDENCED, PRACTICED, UNSEEN,  # noqa: E402
                           compute_learner_state, task_skill_map)
from schemas import AISession, Mode, SkillKey                        # noqa: E402
from store import store as db                                       # noqa: E402


def skill_state(state: dict, key: str) -> str:
    return next(s["state"] for s in state["skills"] if s["skill_key"] == key)


# ---- A. 技能归属 + 空态 ----
s2t = task_skill_map()
assert s2t, "课程配置里没有任何 Task.skill"
assert all(v in {k.value for k in SkillKey} for v in s2t.values()), "出现非法 skill 值"
assert s2t["task_backend"] == "project_dev" and s2t["task_frontend"] == "vibe_coding"
assert s2t["task_setup"] == "env_setup"

st = compute_learner_state("nobody")
assert st["skills"] and all(s["state"] == UNSEEN for s in st["skills"])
assert st["learning_gaps"] == []
assert st["counts"] == {"skills_evidenced": 0, "skills_practiced": 0,
                        "skills_exposed": 0, "gaps_open": 0, "gaps_total": 0}, st["counts"]
assert compute_learner_state("nobody") == compute_learner_state("nobody")  # 确定性
print("[A] 技能归属取自课程配置；空学生全部 UNSEEN；重复调用结果一致")

# ---- B. 四态推进 ----
sid = "stu_exp"
db.save_session(AISession(session_id="sess_b1", student_id=sid,
                          task_id="task_backend", mode=Mode.tutor))
assert skill_state(compute_learner_state(sid), "project_dev") == EXPOSED

db.save_evaluation(submission_id="b_1", student_id=sid, task_id="task_backend",
                   status="FAIL", score=40, passed=False)
st = compute_learner_state(sid)
assert skill_state(st, "project_dev") == PRACTICED, st["skills"]
assert skill_state(st, "vibe_coding") == UNSEEN  # 其他技能不受影响

db.save_evaluation(submission_id="b_2", student_id=sid, task_id="task_backend",
                   status="PASS", score=100, passed=True)
assert skill_state(compute_learner_state(sid), "project_dev") == EVIDENCED
# 只提交、未对话也能到 PRACTICED（PRACTICED 不依赖 EXPOSED）
db.save_evaluation(submission_id="b_3", student_id="stu_prac", task_id="task_frontend",
                   status="NEED_REVIEW", score=0, passed=False)
assert skill_state(compute_learner_state("stu_prac"), "vibe_coding") == PRACTICED
print("[B] UNSEEN → EXPOSED → PRACTICED → EVIDENCED 四态按真实数据推进")

# ---- C/D. Learning Gap 生命周期 + EVIDENCED 与缺口并存 ----
sid3 = "stu_gap"


def _ev(sub: str, task: str, status: str, gaps: list[dict]):
    db.save_evaluation(submission_id=sub, student_id=sid3, task_id=task, status=status,
                       score=100 if status == "PASS" else 0,
                       passed=(status == "PASS"), criteria={"learning_gaps": gaps})


_ev("c_1", "task_setup", "PASS", [{"rubric_id": "rb_setup_1", "reason": "没讲清前后端各自职责"}])
st = compute_learner_state(sid3)
assert st["counts"]["gaps_total"] == 1 and st["counts"]["gaps_open"] == 1, st["counts"]
g = st["learning_gaps"][0]
assert g["resolved"] is False and g["occurrences"] == 1 and g["confidence"] == "low"
assert g["skill_key"] == "env_setup" and g["source_task"] == "task_setup"
assert g["rubric_id"] == "rb_setup_1" and len(g["gap_id"]) == 12
assert g["first_seen_at"] == g["last_seen_at"] and g["resolved_at"] == ""
# §14.2 硬原则：技能已 EVIDENCED，理论缺口同时存在（EVIDENCED ≠ MASTERED）
assert skill_state(st, "env_setup") == EVIDENCED

# 同一提交重复写（INSERT OR REPLACE）不重复计数，也不升级置信度
_ev("c_1", "task_setup", "PASS", [{"rubric_id": "rb_setup_1", "reason": "没讲清前后端各自职责"}])
assert compute_learner_state(sid3)["learning_gaps"][0]["occurrences"] == 1

# 第二次提交仍报同一缺口 → occurrences=2 / medium，reason 取最新
_ev("c_2", "task_setup", "PASS", [{"rubric_id": "rb_setup_1", "reason": "还是没讲清职责边界"}])
g = compute_learner_state(sid3)["learning_gaps"][0]
assert g["occurrences"] == 2 and g["confidence"] == "medium", g
assert g["reason"] == "还是没讲清职责边界"

# 第三次提交不再报该缺口 → resolved（不因一次失败永久标记"不懂"），历史保留
_ev("c_3", "task_setup", "PASS", [])
st = compute_learner_state(sid3)
g = st["learning_gaps"][0]
assert g["resolved"] is True and g["resolved_at"], g
assert st["counts"]["gaps_open"] == 0 and st["counts"]["gaps_total"] == 1
assert compute_learner_state(sid3) == st  # 幂等
print("[C] Learning Gap：首见 low → 复现 medium → 不再报则 resolved；重复提交不重复计数")
print("[D] EVIDENCED 与 learning_gap 并存（技能过关 ≠ 理论掌握）")

# ---- E. 端点与接线 ----
from fastapi.testclient import TestClient  # noqa: E402

import app as engine_app                  # noqa: E402

client = TestClient(engine_app.app)
r = client.get("/api/ai/learner_state", params={"student_id": sid3})
assert r.status_code == 200, r.text
d = r.json()["data"]
assert d["student_id"] == sid3 and d["counts"]["gaps_total"] == 1
assert client.get("/api/ai/learner_state").status_code == 400  # 缺 student_id

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py"), encoding="utf-8").read()
assert src.count("attach_student_state(") == 4        # 1 定义 + 3 调用（P4 次序断言仍成立）
_block = src[src.index("def attach_student_state("):]
_block = _block[:_block.index("\n\n\n")]
assert "blocked_reason" in _block and "project_state" in _block and "learner_state" in _block
print("[E] /api/ai/learner_state 可用；learner_state 与 P4 学生态同走缓存后挂载")

print("ALL P5 TESTS PASSED")