# -*- coding: utf-8 -*-
"""
阶段 2 验收测试（V2 修改版）：新增能力。

覆盖：
  T2.1 快照 hash —— 同输入同 hash，输入变化 hash 变化
  T2.2 幂等缓存 —— 同 task+快照第二次评审零 LLM 调用且 cached=True；证据变化后缓存失效
  T2.3 Career Text —— 同输入同输出；量化/技术栈/功能齐全；空结果 400
  T2.4 质检陪练 —— task_review 返回 2 题；接口独立不触评审链
  T2.5 README 启动命令 —— detect_run_cmd 纯函数 + 评审链 runtime 证据注入
运行：python _test_phase2.py（无外部 LLM 依赖）
"""
import json

from fastapi.testclient import TestClient

import app as app_mod
from code_evidence import detect_run_cmd
from review import snapshot_evidence
from schemas import ReviewLLMOutput

PASS_COUNT = 0
FAIL_LINES = []


def check(name: str, cond: bool, detail: str = ""):
    global PASS_COUNT
    if cond:
        PASS_COUNT += 1
        print(f"  ✓ {name}")
    else:
        FAIL_LINES.append(name)
        print(f"  ✕ {name}  {detail}")


print("== T2.1 证据快照 hash ==")
ev_a = {"code": "POST /chat 存在", "runtime": "uvicorn main:app 启动"}
ev_b = {"code": "POST /chat 存在", "runtime": "换了证据文本"}
ci = [{"name": "tests", "dimension": "test", "conclusion": "success"}]
h1 = snapshot_evidence(ev_a, ci, task_id="task_review")
h2 = snapshot_evidence(dict(reversed(list(ev_a.items()))), list(reversed(ci)), task_id="task_review")
check("同输入（键序无关）→ 同 hash", h1 == h2, f"{h1} vs {h2}")
check("证据变化 → hash 变化", snapshot_evidence(ev_b, ci, task_id="task_review") != h1)
check("CI 结论变化 → hash 变化",
      snapshot_evidence(ev_a, [{"name": "tests", "dimension": "test", "conclusion": "failure"}], task_id="task_review") != h1)
check("task 变化 → hash 变化", snapshot_evidence(ev_a, ci, task_id="task_link") != h1)

print("== T2.2/T2.5 幂等缓存 + README 证据（端到端 mock） ==")
client = TestClient(app_mod.app)
CALLS = {"n": 0}
FIXED = {"criteria": [
    {"rubric_id": "rb_review_1", "status": "PASS", "evidence": "README 启动命令", "reason": "本地可复现运行说明"},
    {"rubric_id": "rb_review_2", "status": "PASS", "evidence": "code", "reason": "ok"},
    {"rubric_id": "rb_review_3", "status": "PASS", "evidence": "code", "reason": "ok"},
    {"rubric_id": "rb_review_4", "status": "PASS", "evidence": "description", "reason": "ok"},
], "next_step": "无"}


async def fake_code_evidence(repo_url, task_id="", code_context=None, client=None):
    return {"ok": True, "repo": "u/r", "default_branch": "main", "file_count": 3,
            "key_files": [], "evidence_text": "GITHUB-REPO: u/r\n===== README.md =====\nuvicorn main:app --port 8000 启动",
            "readme_run_cmd": "uvicorn main:app --port 8000 启动",
            "ci": {"ok": True, "has_ci": True, "runs_count": 1, "text": "[CI]",
                   "workflows": [{"name": "tests", "dimension": "test", "conclusion": "success",
                                  "status": "completed", "url": ""}]}}


async def fake_review(self, messages):
    CALLS["n"] += 1
    return ReviewLLMOutput.model_validate(FIXED)


def do_review(session_id):
    body = {
        "session_id": session_id, "task_id": "task_review", "project_id": "project_chatbot",
        "submission": {"github_url": "https://github.com/u/r", "deployment_url": "",
                       "code": "x", "description": "自述"},
        "api_key": "sk-test",
    }
    r = client.post("/api/ai/review", json=body)
    assert r.status_code == 200, r.text
    return r.json()["data"]


orig_review, orig_ev = app_mod.LLMClient.review, app_mod.build_code_evidence
app_mod.LLMClient.review = fake_review
app_mod.build_code_evidence = fake_code_evidence
app_mod._REVIEW_CACHE.clear()
try:
    d1 = do_review("t_p2_a")
    n1 = CALLS["n"]
    d2 = do_review("t_p2_a")
    check("第一次评审消耗 LLM", n1 == 1, f"n={n1}")
    check("第二次同快照评审零 LLM（幂等缓存命中）", CALLS["n"] == n1, f"n={CALLS['n']}")
    check("缓存命中带 cached 标记", d2.get("cached") is True)
    check("两次评分一致", d1["score"] == d2["score"] and d1["status"] == d2["status"])
    check("响应带 snapshot_hash", bool(d1.get("snapshot_hash")))

    # 证据变化 → 快照变化 → 缓存失效，重新调 LLM
    body_changed = {
        "session_id": "t_p2_a", "task_id": "task_review", "project_id": "project_chatbot",
        "submission": {"github_url": "https://github.com/u/r", "deployment_url": "",
                       "code": "x", "description": "自述（已补充更完整的数据流说明）"},
        "api_key": "sk-test",
    }
    r = client.post("/api/ai/review", json=body_changed)
    d3 = r.json()["data"]
    check("证据变化 → 缓存失效重新评审", CALLS["n"] == n1 + 1 and not d3.get("cached"))

    # T2.5：README 启动命令注入 runtime 证据 → rb_review_1（runtime）不再 NEED_REVIEW
    crit_map = {c["rubric_id"]: c["status"] for c in d1["evaluation"]["criteria"]}
    check("rb_review_1（runtime）通过 README 证据可判定", "rb_review_1" in crit_map, str(crit_map))
finally:
    app_mod.LLMClient.review, app_mod.build_code_evidence = orig_review, orig_ev
    app_mod._REVIEW_CACHE.clear()

print("== T2.3 Career Text ==")
res = [{"task_id": "task_backend", "score": 100, "passed": 4, "total": 4, "ci_conclusion": "success"},
       {"task_id": "task_frontend", "score": 100, "passed": 3, "total": 3, "ci_conclusion": ""},
       {"task_id": "task_review", "score": 100, "passed": 4, "total": 4, "ci_conclusion": "success"}]
r = client.post("/api/career/text", json={"project_id": "project_chatbot", "results": res,
                                          "github_url": "https://github.com/u/r"})
j = r.json()
check("career/text 200", r.status_code == 200 and j["ok"])
t1 = j["data"]["text"]
check("包含项目名", "套壳聊天机器人" in t1, t1)
check("包含量化结果（4+3+4=11/11）", "11/11" in t1, t1)
check("包含 CI 结论", "GitHub Actions" in t1)
check("包含 GitHub 链接", "github.com/u/r" in t1)
# 2026-09-13 改版：结构化简历（标题行 / 技术栈独立行 / Bullet / 量化）
d1 = j["data"]
check("标题行含角色", "（独立开发）" in d1["title_line"], d1["title_line"])
check("text 含技术栈独立行", "技术栈：" in t1)
check("技术栈为纯技术名词（含 FastAPI）", "FastAPI" in d1["tech"], str(d1["tech"]))
check("Bullet 为结构化列表", d1["bullets"] and all("label" in b and "text" in b for b in d1["bullets"]),
      str(d1["bullets"])[:120])
check("量化指标为列表", isinstance(d1["metrics"], list) and d1["metrics"], str(d1["metrics"]))
r2 = client.post("/api/career/text", json={"project_id": "project_chatbot", "results": res,
                                           "github_url": "https://github.com/u/r"})
check("同输入同输出（零漂移）", r2.json()["data"]["text"] == t1)
r3 = client.post("/api/career/text", json={"project_id": "project_chatbot", "results": []})
check("空结果 → 400", r3.status_code == 400)

print("== T2.4 质检陪练接口 ==")
r = client.get("/api/ai/interview?task_id=task_review")
j = r.json()
check("interview 200", r.status_code == 200 and j["ok"])
qs = j["data"]["questions"]
check("task_review 配 2 题", len(qs) == 2, f"n={len(qs)}")
check("题型覆盖 explain/transfer", {q["type"] for q in qs} == {"explain", "transfer"})
check("每题含 answer_anchor", all(q.get("answer_anchor") for q in qs))
r = client.get("/api/ai/interview?task_id=task_setup")
check("无标注任务返回空列表", r.json()["data"]["questions"] == [])
r = client.get("/api/ai/interview")
check("缺 task_id → 400", r.status_code == 400)

print("== T2.5 detect_run_cmd 纯函数 ==")
check("uvicorn 命中", detect_run_cmd("先安装依赖\n然后 uvicorn main:app --port 8000 启动") != "")
check("npm run 命中", detect_run_cmd("npm run dev 即可") != "")
check("docker compose 命中", detect_run_cmd("docker compose up -d") != "")
check("无命令返回空", detect_run_cmd("这个项目做完了，很好用") == "")
check("空文本返回空", detect_run_cmd("") == "")

print()
if FAIL_LINES:
    print(f"FAILED: {len(FAIL_LINES)} 项未通过 → {FAIL_LINES}")
    raise SystemExit(1)
print(f"ALL PASSED: {PASS_COUNT} checks")
