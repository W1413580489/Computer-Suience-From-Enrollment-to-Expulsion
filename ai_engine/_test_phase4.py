# -*- coding: utf-8 -*-
"""
阶段 4 验收测试：简历生成质量改版。

覆盖：
  T4.1 学习属性过滤（认识/学习/了解… 不进简历；含交付动词则保留）
  T4.2 技术栈必须是纯技术名词（不出现"AI 协作开发""工作流编排"等能力标签）
  T4.3 亮点 = 难点 + 目的 + 结果；按 架构设计/稳定性与容错/结果产出/工程素养 分组
  T4.4 量化指标（验收用例数 + CI）；标题行含角色与日期
  T4.5 只统计已通过任务；确定性（同输入同输出）；异常分支（空结果 400 / 项目 404）
运行：python _test_phase4.py
"""
import json

from fastapi.testclient import TestClient

import app as app_mod
from career import build_career_text, is_learning_text
from course_data import get_project

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


print("== T4.1 学习属性过滤 ==")
check("「认识 Agent 与项目骨架」判定为学习内容", is_learning_text("认识 Agent 与项目骨架"))
check("「拆解任务与准备环境」判定为学习内容", is_learning_text("拆解任务与准备环境"))
check("「学习 XXX」判定为学习内容", is_learning_text("学习 FastAPI 基础"))
check("「搭建工程骨架」不算学习（含交付动词）", not is_learning_text("搭建工程骨架"))
check("「实现 POST /chat 接口」不算学习", not is_learning_text("实现 POST /chat 接口"))
check("「设计 max_steps 上限与安全退出」不算学习", not is_learning_text("设计 max_steps 上限与安全退出"))

print("== T4.2/T4.3/T4.4 课程 02 生成结果质量 ==")
client = TestClient(app_mod.app)
tasks = [
    ("c2t01", 100, 3, 3), ("c2t02", 100, 4, 4), ("c2t03", 100, 4, 4),
    ("c2t04", 92, 3, 3), ("c2t05", 100, 3, 3), ("c2t06", 100, 3, 3),
    ("c2t07", 100, 4, 4), ("c2t08", 100, 4, 4), ("c2t09", 92, 4, 4),
]
results = [{"task_id": t, "score": s, "passed": p, "total": tot,
            "ci_conclusion": "success" if t in ("c2t03", "c2t08") else ""}
           for t, s, p, tot in tasks]

r = client.post("/api/career/text", json={
    "project_id": "project_agent", "results": results,
    "github_url": "https://github.com/u/github-repo-agent", "date": "2026.09",
})
check("接口 200", r.status_code == 200 and r.json()["ok"])
d = r.json()["data"]

# 技术栈纯名词
tech = d["tech"]
check("技术栈含 Python", "Python" in tech, str(tech))
check("技术栈含 OpenAI 兼容 API（Function Calling）", any("Function Calling" in t for t in tech), str(tech))
check("技术栈含 Pytest", "Pytest" in tech, str(tech))
check("技术栈含 GitHub Actions", "GitHub Actions" in tech, str(tech))
VAGUE = ("协作开发", "工作流编排", "全栈项目开发", "AI 辅助开发", "环境配置", "调试排错")
check("技术栈无虚词（能力标签）", not any(v in "".join(tech) for v in VAGUE), str(tech))

# Bullet 分组与内容
labels = [b["label"] for b in d["bullets"]]
check("包含架构设计 Bullet", "架构设计" in labels, str(labels))
check("包含稳定性与容错 Bullet", "稳定性与容错" in labels, str(labels))
check("包含结果产出 Bullet", "结果产出" in labels, str(labels))
check("包含工程素养 Bullet", "工程素养" in labels, str(labels))
check("Bullet 数量 3~4 条", 3 <= len(d["bullets"]) <= 4, str(labels))

arch = next(b["text"] for b in d["bullets"] if b["label"] == "架构设计")
stab = next(b["text"] for b in d["bullets"] if b["label"] == "稳定性与容错")
check("架构 Bullet 提 Function Calling / Agent Loop", "Agent Loop" in arch, arch)
check("架构 Bullet 提 JSON Schema 工具注册表", "JSON Schema" in arch, arch)
check("架构 Bullet 保留多步循环亮点", "多步" in arch or "多步调用" in arch, arch)
check("稳定性 Bullet 含限流重试", "限流" in stab and "重试" in stab, stab)
check("稳定性 Bullet 含 max_steps 安全退出", "max_steps" in stab, stab)
check("稳定性 Bullet 补上目的（避免被平台封禁）", "封禁" in stab, stab)
check("稳定性 Bullet 补上结果（保障/避免…）", ("保障" in stab or "避免" in stab), stab)
check("Bullet 长度可控（每条 ≤ 190 字）", all(len(b["text"]) <= 190 for b in d["bullets"]),
      str([len(b["text"]) for b in d["bullets"]]))
purposes_present = any("避免" in b["text"] or "让" in b["text"] for b in d["bullets"])
check("至少有一条 Bullet 带目的从句", purposes_present)
all_text = "".join(b["text"] for b in d["bullets"])
check("Bullet 中无学习属性词", not any(w in all_text for w in ("认识", "学习", "了解", "入门")), all_text)
check("Bullet 中无课程目录式标题（如 max_steps 与安全退出）", "max_steps 与安全退出" not in all_text)

# 量化与标题
metrics = d["metrics"]
check("量化含验收用例数 32/32", any("32/32" in m for m in metrics), str(metrics))
check("量化含 GitHub Actions", any("GitHub Actions" in m for m in metrics), str(metrics))
check("量化不罗列平均分", not any("平均验收分" in m for m in metrics), str(metrics))
check("标题行含项目名与角色", d["title_line"].startswith("GitHub 项目分析 Agent（独立开发）"), d["title_line"])
check("标题行含日期", "2026.09" in d["title_line"], d["title_line"])
check("text 含技术栈独立行", "技术栈：Python" in d["text"], d["text"][:120])
check("text 含项目简介", "项目简介：" in d["text"])
check("text 含仓库链接", "https://github.com/u/github-repo-agent" in d["text"])
print("  ---- 生成结果预览 ----")
for line in d["text"].split("\n"):
    print("   ", line)

print("== T4.5 只统计已通过任务 + 确定性 ==")
partial = [{"task_id": "c2t01", "score": 100, "passed": 3, "total": 3, "ci_conclusion": ""},
           {"task_id": "c2t02", "score": 100, "passed": 4, "total": 4, "ci_conclusion": ""}]
r2 = client.post("/api/career/text", json={"project_id": "project_agent", "results": partial})
d2 = r2.json()["data"]
labels2 = [b["label"] for b in d2["bullets"]]
check("仅通过 2 个任务时只出现对应分组", set(labels2) <= {"架构设计", "工程素养"}, str(labels2))
check("未通过任务的亮点不入简历（无稳定性 Bullet）", "稳定性与容错" not in labels2, str(labels2))
check("量化按已通过任务统计 7/7", any("7/7" in m for m in d2["metrics"]), str(d2["metrics"]))

r3 = client.post("/api/career/text", json={
    "project_id": "project_agent", "results": results, "github_url": "https://github.com/u/github-repo-agent",
    "date": "2026.09"})
check("同输入两次输出完全一致（零漂移）", r3.json()["data"]["text"] == d["text"])

r4 = client.post("/api/career/text", json={"project_id": "project_chatbot", "results": [
    {"task_id": "task_backend", "score": 100, "passed": 4, "total": 4, "ci_conclusion": "success"}]})
d4 = r4.json()["data"]
check("课程 01 也能生成（技术栈纯名词）",
      "FastAPI" in d4["tech"] and not any(v in "".join(d4["tech"]) for v in VAGUE), str(d4["tech"]))
check("课程 01 Bullet 含安全设计（Key 仅在服务端）",
      "服务端" in "".join(b["text"] for b in d4["bullets"]), str(d4["bullets"]))

r5 = client.post("/api/career/text", json={"project_id": "project_agent", "results": []})
check("空结果 → 400", r5.status_code == 400)
r6 = client.post("/api/career/text", json={"project_id": "nope", "results": partial})
check("项目不存在 → 404", r6.status_code == 404)

print()
if FAIL_LINES:
    print(f"FAILED: {len(FAIL_LINES)} 项未通过 → {FAIL_LINES}")
    raise SystemExit(1)
print(f"ALL PASSED: {PASS_COUNT} checks")
