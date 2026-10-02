# -*- coding: utf-8 -*-
"""P3 场景验证：Revision 演进（GitHub compare → 仅入 submissions/evaluations 行）。

覆盖：新库建列、老库补列迁移、revision_json 落库/回读、compare 守卫（不发网络请求）。
用独立临时库跑，不触碰 data/engine.db。
"""
import asyncio
import json
import os
import sqlite3
import tempfile

TMP = tempfile.mkdtemp()
os.environ["XKZ_DB_PATH"] = os.path.join(TMP, "p3_new.db")

from store import Store                                   # noqa: E402
from schemas import Submission                            # noqa: E402
from code_evidence import compare_revisions               # noqa: E402

# ---- A. 新库：revision_json 列存在 ----
db = Store()
for tbl in ("submissions", "evaluations"):
    cols = {r["name"] for r in db._fetchall(f"PRAGMA table_info({tbl})")}
    assert "revision_json" in cols, (tbl, cols)
print("[A] 新库 submissions/evaluations 均含 revision_json 列")

# ---- B. 老库补列迁移（模拟 P2 已建表、无 revision_json）----
old_path = os.path.join(TMP, "p3_legacy.db")
c = sqlite3.connect(old_path)
c.execute("CREATE TABLE submissions (id TEXT PRIMARY KEY, student_id TEXT, task_id TEXT, "
          "project_id TEXT, github_url TEXT, deployment_url TEXT, code TEXT, description TEXT, "
          "head_sha TEXT, parent_submission_id TEXT, submitted_at TEXT)")
c.execute("CREATE TABLE evaluations (submission_id TEXT PRIMARY KEY, student_id TEXT, task_id TEXT, "
          "status TEXT, created_at TEXT)")
c.commit()
c.close()
legacy = Store(old_path)
for tbl in ("submissions", "evaluations"):
    cols = {r["name"] for r in legacy._fetchall(f"PRAGMA table_info({tbl})")}
    assert "revision_json" in cols, (tbl, cols)
print("[B] 老库启动时自动补列 revision_json（ALTER TABLE），不重建表")

# ---- C. revision_json 落库 / 回读 ----
rev = {"base_sha": "sha_a", "head_sha": "sha_b", "status": "ahead", "ahead_by": 2,
       "total_commits": 2, "files_changed": 1, "additions": 30, "deletions": 4,
       "files": [{"filename": "main.py", "status": "modified", "additions": 30, "deletions": 4}],
       "truncated": False, "parent_submission_id": "subP"}
s = Submission(id="subC", task_id="c3_t08", student_id="u_1", project_id="project_agent",
               github_url="https://github.com/a/b", head_sha="sha_b",
               parent_submission_id="subP", revision_json=json.dumps(rev, ensure_ascii=False))
db.save_submission(s)
back = db.latest_submission("u_1", "c3_t08")
assert json.loads(back["revision_json"])["files_changed"] == 1, back["revision_json"]
db.save_evaluation(submission_id="subC", student_id="u_1", task_id="c3_t08",
                   status="PASS", score=100, passed=True, head_sha="sha_b",
                   revision_json=s.revision_json, criteria={"status": "PASS"})
raw = db._fetchone("SELECT revision_json FROM evaluations WHERE submission_id='subC'")
assert json.loads(raw["revision_json"])["ahead_by"] == 2, raw["revision_json"]
print("[C] revision_json 在 submissions / evaluations 均可落库并回读")

# ---- D. compare 守卫（不触发网络请求）----
async def _guards():
    assert await compare_revisions("https://github.com/a/b", "same", "same") == {}
    assert await compare_revisions("https://github.com/a/b", "", "x") == {}
    assert await compare_revisions("https://github.com/a/b", "x", "") == {}
    assert await compare_revisions("not-a-url", "a", "b") == {}
asyncio.run(_guards())
print("[D] compare_revisions 守卫正常（同 sha / 空 sha / 非法 URL 直接返回空，不发请求）")

# ---- E. 修订信息不进证据文本（因而进不了缓存 key）----
from review import evidence_text, snapshot_evidence           # noqa: E402
avail = {"code": "代码证据文本", "runtime": "npm run dev"}
h1 = snapshot_evidence(avail, [], task_id="c3_t08")
h2 = snapshot_evidence(avail, [], task_id="c3_t08")
assert h1 == h2
assert "revision" not in evidence_text(avail) and "sha_b" not in evidence_text(avail)
print("[E] 证据文本/快照不含 revision 与 sha（缓存 key 不受修订影响）")

print("ALL P3 TESTS PASSED")