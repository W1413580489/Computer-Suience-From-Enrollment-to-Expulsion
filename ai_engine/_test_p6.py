# -*- coding: utf-8 -*-
"""P6 场景验证：项目记录（简历服务端历史 + 项目复盘）。

覆盖：
  [A] 读侧取数：latest_project_evaluations 取"每任务最新一次评审"（行序定序，非 created_at）
      list_project_submissions 关联出提交事件 + 其评审结论
  [B] 简历历史结果：与前端 CareerTaskResult 同构（passed/total 取自 acceptance criteria）
      且带 status / ci_conclusion（服务端真相源）
  [C] 项目复盘：时间线 / 每任务尝试与通过统计 / GitHub revision 变更文件（纯 SQLite，零 LLM）
  [D] 端点 /api/ai/project_record：缺 student_id→400，项目不存在→404，正常→results+completed_tasks
      +retro+project_state+learner_state
  [E] 兼容与迁移：save_evaluation 新增 ci_conclusion 列（轻量列迁移）；旧调用（不传该参数）不破坏
用独立临时库跑，不触碰 data/engine.db，不触网。
"""
import json
import os
import tempfile

TMP = tempfile.mkdtemp()
os.environ["XKZ_DB_PATH"] = os.path.join(TMP, "p6.db")

from schemas import ReviewStatus, Submission                        # noqa: E402
from store import store as db                                       # noqa: E402
import student_record as sr                                         # noqa: E402

PID = "project_chatbot"
SID = "stu_p6"


def _sub(sub_id: str, task_id: str, head_sha: str = "", parent: str = "", revision: str = ""):
    db.save_submission(Submission(id=sub_id, student_id=SID, task_id=task_id, project_id=PID,
                                  head_sha=head_sha, parent_submission_id=parent,
                                  revision_json=revision))


def _crit(*statuses: str) -> dict:
    return {"criteria": [{"rubric_id": f"rb_{i}", "status": s} for i, s in enumerate(statuses)]}


# ---- 造数：task_backend 两版提交（先 FAIL 后 PASS），task_setup 一版 PASS ----
_sub("s1", "task_backend", head_sha="sha_a")
db.save_evaluation(submission_id="s1", student_id=SID, task_id="task_backend", project_id=PID,
                   status="FAIL", score=50, passed=False, head_sha="sha_a",
                   criteria=_crit("FAIL", "PASS"))

_rev = json.dumps({"status": "ahead", "files_changed": 2, "files": [
    {"filename": "app.py"}, {"filename": "main.py"}]}, ensure_ascii=False)
_sub("s2", "task_backend", head_sha="sha_b", parent="s1", revision=_rev)
db.save_evaluation(submission_id="s2", student_id=SID, task_id="task_backend", project_id=PID,
                   status="PASS", score=100, passed=True, ci_conclusion="success",
                   head_sha="sha_b", revision_json=_rev,
                   criteria=_crit("PASS", "PASS"))

_sub("s3", "task_setup", head_sha="sha_x")
db.save_evaluation(submission_id="s3", student_id=SID, task_id="task_setup", project_id=PID,
                   status="PASS", score=100, passed=True,
                   criteria=_crit("PASS", "PASS", "PASS"))

# ---- A. 读侧取数 ----
evals = {r["task_id"]: r for r in db.latest_project_evaluations(SID, PID)}
assert set(evals) == {"task_backend", "task_setup"}, evals.keys()
assert evals["task_backend"]["head_sha"] == "sha_b", "每任务只保留最新一次评审"
assert evals["task_backend"]["status"] == "PASS"
assert evals["task_backend"]["ci_conclusion"] == "success"
assert db.latest_project_evaluations(SID, "no_such_project") == []
assert db.latest_project_evaluations("", PID) == []

subs = db.list_project_submissions(SID, PID)
assert [s["submission_id"] for s in subs] == ["s1", "s2", "s3"], subs
assert subs[1]["status"] == "PASS" and subs[1]["parent_submission_id"] == "s1"
print("[A] latest_project_evaluations 取最新一次评审；list_project_submissions 关联出提交+评审")

# ---- B. 简历历史结果（服务端真相源） ----
results = {r["task_id"]: r for r in sr.build_career_results(SID, PID)}
b = results["task_backend"]
assert b == {"task_id": "task_backend", "score": 100, "passed": 2, "total": 2,
             "ci_conclusion": "success", "status": "PASS"}, b
s = results["task_setup"]
assert s["passed"] == 3 and s["total"] == 3 and s["status"] == "PASS", s
assert sr.build_career_results("nobody", PID) == []
# 确定性：同输入重复调用结果一致
assert sr.build_career_results(SID, PID) == sr.build_career_results(SID, PID)
print("[B] build_career_results 与前端 CareerTaskResult 同构（含 status / ci_conclusion）")

# ---- C. 项目复盘 ----
retro = sr.build_project_retro(SID, PID)
assert retro["source"] == "sqlite" and retro["project_title"]
t = retro["totals"]
assert t == {"submissions": 3, "tasks_attempted": 2, "tasks_passed": 2,
             "passed_attempts": 2, "failed_attempts": 1, "need_review_attempts": 0}, t
tl = {x["submission_id"]: x for x in retro["timeline"]}
assert tl["s2"]["changed_files"] == ["app.py", "main.py"] and tl["s2"]["files_changed"] == 2
assert tl["s2"]["is_revision"] is True and tl["s1"]["is_revision"] is False
assert tl["s1"]["status"] == "FAIL" and tl["s1"]["task_title"]
bt = next(x for x in retro["tasks"] if x["task_id"] == "task_backend")
assert bt["attempts"] == 2 and bt["passed_attempts"] == 1 and bt["failed_attempts"] == 1
assert bt["passed"] is True and bt["latest_status"] == "PASS" and bt["first_submitted_at"]
assert sr.build_project_retro("nobody", PID)["totals"]["submissions"] == 0
assert sr.build_project_retro("nobody", "no_such_project") is None
print("[C] 项目复盘：时间线 / 尝试与通过统计 / GitHub 变更文件（零 LLM）")

# ---- D. 端点 ----
from fastapi.testclient import TestClient  # noqa: E402

import app as engine_app                   # noqa: E402

client = TestClient(engine_app.app)
assert client.get("/api/ai/project_record").status_code == 400                     # 缺 student_id
assert client.get("/api/ai/project_record",
                  params={"student_id": SID, "project_id": "nope"}).status_code == 404
r = client.get("/api/ai/project_record", params={"student_id": SID, "project_id": PID})
assert r.status_code == 200, r.text
d = r.json()["data"]
assert d["source"] == "server" and d["project_id"] == PID
assert {x["task_id"] for x in d["results"]} == {"task_backend", "task_setup"}
assert set(d["completed_tasks"]) == {"task_backend", "task_setup"}
assert d["retro"]["totals"]["submissions"] == 3
assert d["project_state"] and d["project_state"]["state"] in {
    "NOT_STARTED", "IN_PROGRESS", "COMPLETED", "BLOCKED"}
assert d["learner_state"] and "counts" in d["learner_state"]
print("[D] /api/ai/project_record：400 / 404 / 正常三态；results+retro+project_state+learner_state")

# ---- E. 兼容与迁移 ----
assert "ci_conclusion" in {r["name"] for r in db._fetchall("PRAGMA table_info(evaluations)")}
# 旧调用（不传 ci_conclusion）仍可写入，默认空串
db.save_evaluation(submission_id="s9", student_id="stu_legacy", task_id="task_setup",
                   project_id=PID, status="PASS", score=100, passed=True,
                   criteria={"criteria": [{"rubric_id": "r", "status": ReviewStatus.PASS}]})
assert db.latest_project_evaluations("stu_legacy", PID)[0]["ci_conclusion"] == ""
# _ci_conclusion 归并口径
assert engine_app._ci_conclusion([{"conclusion": "success"}]) == "success"
assert engine_app._ci_conclusion([{"conclusion": "failure"}]) == "failure"
assert engine_app._ci_conclusion([]) == ""
print("[E] ci_conclusion 轻量列迁移可用；旧调用兼容；_ci_conclusion 口径正确")

print("ALL P6 TESTS PASSED")