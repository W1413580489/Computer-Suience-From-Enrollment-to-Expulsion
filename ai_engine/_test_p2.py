# -*- coding: utf-8 -*-
"""P2 场景验证：students / submissions / evaluations 三表 + 幂等 evidence 写入。

用独立临时库跑，不触碰 data/engine.db。
"""
import os
import tempfile

os.environ["XKZ_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "p2_test.db")

from store import Store                      # noqa: E402
from schemas import Evidence, EvidenceType, Submission   # noqa: E402

db = Store()
tables = {r["name"] for r in db._fetchall(
    "SELECT name FROM sqlite_master WHERE type='table'")}
assert {"students", "submissions", "evaluations"} <= tables, tables
print("[1] 三表已建:", sorted({"students", "submissions", "evaluations"}))

# 学生 upsert：显式 name 建档/更新；name=None 只保证存在、不覆盖
db.upsert_student("u_abc", "王叔")
db.upsert_student("u_abc", "王叔2")
db.upsert_student("u_abc")               # 评审链式调用：不得覆盖已存姓名
row = db._fetchone("SELECT name FROM students WHERE student_id=?", ("u_abc",))
assert row["name"] == "王叔2", row["name"]
assert db._fetchone("SELECT COUNT(*) AS c FROM students")["c"] == 1
print("[2] students upsert 幂等 + 更新且不被 None 覆盖:", row["name"])

# 提交历史：两次提交（带 head_sha），latest 取最新
s1 = Submission(id="sub1", task_id="c3_t08", student_id="u_abc", project_id="project_agent",
                github_url="https://github.com/a/b", head_sha="sha_aaa")
s2 = Submission(id="sub2", task_id="c3_t08", student_id="u_abc", project_id="project_agent",
                github_url="https://github.com/a/b", head_sha="sha_bbb",
                parent_submission_id="sub1")
db.save_submission(s1)
db.save_submission(s2)
db.save_submission(s2)  # 重复写同一 id 不新增
lst = db.list_submissions("u_abc", "c3_t08")
assert len(lst) == 2, len(lst)
assert db.latest_submission("u_abc", "c3_t08")["id"] == "sub2"
assert len(db.list_submissions("u_abc", "c3_t08")) == 2
print("[3] submissions 历史:", [r["id"] for r in lst], "latest=head", db.latest_submission("u_abc", "c3_t08")["head_sha"])
assert db.latest_submission("u_xxx", "c3_t08") is None
print("[3b] 无提交返回 None")

# 评审历史：同 submission 覆盖、不同 submission 新增（与幂等缓存分离）
db.save_evaluation(submission_id="sub1", student_id="u_abc", task_id="c3_t08",
                   project_id="project_agent", snapshot_hash="h1", model="deepseek-flash",
                   status="FAIL", score=40, passed=False, head_sha="sha_aaa",
                   criteria={"status": "FAIL"})
db.save_evaluation(submission_id="sub1", student_id="u_abc", task_id="c3_t08",
                   project_id="project_agent", snapshot_hash="h1b", model="deepseek-flash",
                   status="PASS", score=100, passed=True, head_sha="sha_aaa",
                   criteria={"status": "PASS"})
db.save_evaluation(submission_id="sub2", student_id="u_abc", task_id="c3_t08",
                   project_id="project_agent", snapshot_hash="h2", model="deepseek-flash",
                   status="PASS", score=100, passed=True, head_sha="sha_bbb",
                   criteria={"status": "PASS"})
evs = db.list_evaluations("u_abc", "c3_t08")
assert len(evs) == 2, evs            # sub1 覆盖、sub2 新增
assert db._fetchone("SELECT status FROM evaluations WHERE submission_id='sub1'")["status"] == "PASS"
print("[4] evaluations 历史:", [(e["submission_id"], e["status"], e["score"]) for e in evs])

# evidence 幂等：同 id 重复写只覆盖
db.add_evidence(Evidence(id="e1", task_id="c3_t08", type=EvidenceType.CODE,
                         source="code", content="v1"))
db.add_evidence(Evidence(id="e1", task_id="c3_t08", type=EvidenceType.CODE,
                         source="code", content="v2"))
got = db.list_evidence("c3_t08")
assert len(got) == 1 and got[0].content == "v2", got
print("[5] evidence 幂等写入:", len(got), got[0].content)

# 缓存表不受影响
assert db.get_review_result("c3_t08", "h1", "deepseek-flash") is None
print("[6] review_results 缓存表独立，未被误写")

# P2 交付项：接通 evidence 表写入（幂等 + 类型语义映射 url→github）
import app as ai_app   # noqa: E402
avail = {"code": "代码证据文本", "url": "https://github.com/a/b", "runtime": "npm run dev"}
ai_app.persist_evidence("c3_t08", avail, "snapX")
ai_app.persist_evidence("c3_t08", avail, "snapX")   # 同快照重复写：只覆盖、不新增
mapped = {e.source: e.type.value for e in db.list_evidence("c3_t08") if e.id != "e1"}
assert mapped == {"code": "code", "url": "github", "runtime": "runtime"}, mapped
print("[7] persist_evidence 幂等 + 类型映射:", mapped)

print("ALL P2 STORE TESTS PASSED")