# -*- coding: utf-8 -*-
"""
阶段 7 验收测试：课程 03 的验收地基（报告类证据 + GitHub Issues）。

覆盖：
  T7.1 报告类文件（TEST_REPORT.md 等）在关键文件拉取中优先于 README
  T7.2 报告类文件行数上限放宽（250），普通文件仍 120
  T7.3 报告在 GitHub 证据文本里被打上标记（供评审识别）
  T7.4 从证据文本里抽出报告正文 / Issue 记录
  T7.5 collect_evidence 登记 report / issue 两种证据
  T7.6 report / issue 不作硬门槛（缺了不阻塞判定）
  T7.7 Issues 拉取：过滤 PR、条数上限、空列表、404、限流
  T7.8 评审 Prompt 含课程 03 的报告核对规则与 Issue 用法

运行：python _test_phase7.py（不调真实模型与 GitHub，HTTP 全 mock）
"""
import asyncio
from unittest.mock import patch

import code_evidence as ce
import review as review_mod
from schemas import EvidenceType, Rubric, Submission

PASS = 0
FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = ""):
    global PASS
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAILS.append(name)
        print(f"  ✕ {name}  {detail}")


print("== T7.1 报告类文件优先被选中 ==")
PATHS = ["README.md", "requirements.txt", "main.py", "config.py",
         "TEST_REPORT.md", "tests/test_capture.py"]
picked = ce._pick_key_files(PATHS, [])
check("报告排第一位", picked[0] == "TEST_REPORT.md", str(picked))
check("README 仍被选中", "README.md" in picked, str(picked))
check("自动补上测试文件", any(p.lower().split("/")[-1].startswith("test_") for p in picked), str(picked))
check("不超过文件数上限", len(picked) <= ce.KEY_FILES_MAX, str(len(picked)))

print("== T7.2 报告类行数上限放宽 ==")
check("报告类 = 250 行", ce._lines_cap_for("TEST_REPORT.md") == 250, str(ce._lines_cap_for("TEST_REPORT.md")))
check("普通文件 = 120 行", ce._lines_cap_for("README.md") == 120)
check("子目录下的报告也识别", ce._is_report_file("docs/BUGS.md") is True)
check("普通文件不误判", ce._is_report_file("README.md") is False)

print("== T7.3 报告在证据文本里被打标 ==")
EVID = ce._assemble("u", "r", "main", PATHS, [
    {"path": "TEST_REPORT.md", "content": "| 场景 | 实际结果 |\n| 保存决定 | ✓ |", "truncated": False},
    {"path": "README.md", "content": "# hi", "truncated": False},
])
check("含报告标记", review_mod._REPORT_TAG in EVID, EVID[:100])
check("报告正文在证据里", "| 保存决定 | ✓ |" in EVID)

print("== T7.4 报告 / Issue 抽取 ==")
FAKE_REPO = ("GITHUB-REPO: u/r\n\n===== " + review_mod._REPORT_TAG
             + " TEST_REPORT.md =====\n| 场景 | 实际结果 |\n| 保存决定 | ✓ 决定(90%) |\n\n===== main.py =====\nprint(1)")
sec = review_mod.extract_report_section(FAKE_REPO)
check("抽出报告正文（不含文件名头）", "保存决定" in sec and not sec.startswith("TEST_REPORT"), sec[:60])
check("抽到下一个文件为止", "print(1)" not in sec, sec[-40:])

FAKE_ISSUES = ("GITHUB-REPO: u/r\n\n===== main.py =====\nprint(1)\n\n"
               "[GitHub Issues] 共 1 条：\n## #7 分类不准  [open] 2026-09-16\n复现：输入「可以考虑加缓存」被当成 commitment")
isc = review_mod.extract_issues_section(FAKE_ISSUES)
check("抽出 Issue 记录", "#7" in isc and "复现" in isc, isc[:60])
check("无标记时返回空", review_mod.extract_issues_section("nothing here") == "")

print("== T7.5 collect_evidence 登记 report / issue ==")
ev = review_mod.collect_evidence(Submission(task_id="t"), FAKE_REPO + "\n\n" + FAKE_ISSUES.split("\n\n", 2)[-1])
check("登记了 report 证据", "report" in ev, str(list(ev)))
check("登记了 issue 证据", "issue" in ev, str(list(ev)))
check("证据类型枚举含 report / issue",
      EvidenceType.REPORT.value == "report" and EvidenceType.ISSUE.value == "issue")
check("报告内容进入了 report 证据", "保存决定" in ev.get("report", ""), ev.get("report", "")[:60])

print("== T7.6 report / issue 不作硬门槛 ==")
pre_report = review_mod.evidence_precheck(
    [Rubric(id="x1", task_id="t", criterion="c", required_evidence=["report"], weight=1)], ev)
check("只要求 report 时不强制 NEED_REVIEW", pre_report["all_passable"],
      str(pre_report["forced_needs_review"]))
pre_code = review_mod.evidence_precheck(
    [Rubric(id="x2", task_id="t", criterion="c", required_evidence=["code"], weight=1)], ev)
check("要求 code 且有代码证据 → 可判定", pre_code["all_passable"], str(pre_code["forced_needs_review"]))
pre_missing = review_mod.evidence_precheck(
    [Rubric(id="x3", task_id="t", criterion="c", required_evidence=["runtime"], weight=1)],
    {"code": "x"})
check("缺 runtime 仍会卡住（正常的硬门槛没被破坏）", not pre_missing["all_passable"],
      str(pre_missing["forced_needs_review"]))

print("== T7.7 Issues 拉取（HTTP mock） ==")
RESP: dict = {"status": 200, "payload": []}


class FakeResp:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload

    def json(self):
        return self._payload


class FakeClient:
    def __init__(self, *a, **k):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def get(self, url, headers=None):
        return FakeResp(RESP["status"], RESP["payload"])


async def _run_issues():
    with patch.object(ce.httpx, "AsyncClient", FakeClient):
        return await ce.fetch_issues_evidence("u", "r")


RESP["status"] = 200
RESP["payload"] = [
    {"number": 7, "title": "分类不准", "body": "复现步骤…", "state": "open",
     "created_at": "2026-09-16T10:00:00Z", "labels": [{"name": "bug"}]},
    {"number": 8, "title": "这条是 PR，应被过滤", "body": "", "state": "open",
     "created_at": "2026-09-16T10:00:00Z", "pull_request": {"url": "x"}},
] + [{"number": i, "title": f"issue{i}", "body": "b", "state": "closed",
      "created_at": "2026-09-16T10:00:00Z"} for i in range(9, 20)]
res = asyncio.run(_run_issues())
check("拉取成功", res["ok"] is True, str(res)[:80])
check("PR 被过滤掉", all(it["number"] != 8 for it in res["items"]),
      str([it["number"] for it in res["items"]]))
check("最多取 5 条", len(res["items"]) == 5, str(len(res["items"])))
check("文本含编号与标签", "#7" in res["text"] and "bug" in res["text"], res["text"][:80])

RESP["payload"] = []
res = asyncio.run(_run_issues())
check("无 Issue → 明确说明", res["ok"] and res["count"] == 0 and "暂无" in res["text"], res["text"][:40])

RESP["status"], RESP["payload"] = 404, {}
res = asyncio.run(_run_issues())
check("404 → ISSUES_DISABLED", res["ok"] is False and res["code"] == "ISSUES_DISABLED", str(res)[:80])

RESP["status"], RESP["payload"] = 403, {}
res = asyncio.run(_run_issues())
check("403 → RATE_LIMITED", res["ok"] is False and res["code"] == "RATE_LIMITED", str(res)[:80])

print("== T7.8 评审 Prompt 含课程 03 规则 ==")
from course_data import get_rubrics, get_task  # noqa: E402

PROMPT = review_mod.build_review_system_prompt(get_task("task_review"), get_rubrics("task_review"), ev)
check("含「测试报告的核对规则」", "测试报告的核对规则" in PROMPT)
check("含「实际结果笼统不足以判 PASS」", "不足以判 PASS" in PROMPT)
check("含「报告不能替代代码/CI」", "不能替代" in PROMPT)
check("含「Issue 证据的用法」", "Issue 证据的用法" in PROMPT)
check("含「Issue 存在 ≠ 已修复」", "不能" in PROMPT and "修复必须看代码改动" in PROMPT)

print()
print(f"通过 {PASS} 项")
if FAILS:
    print(f"失败 {len(FAILS)} 项：")
    for n in FAILS:
        print(f"  - {n}")
    raise SystemExit(1)
print("全部通过 ✓")
