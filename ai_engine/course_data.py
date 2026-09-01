# -*- coding: utf-8 -*-
"""
课程数据加载：复用现有 RAG 数据库 chunks.jsonl。

邪修学习指南（appendix03）的章节结构映射为：
  Project: 邪修学习指南
    Stage 1: 大一如何零基础做项目？  (第一节 克隆复现 / 第二节 重建项目 / 第三节 项目开发 三节)
      Task 1: 克隆复现
      Task 2: 重建项目
      Task 3: 项目开发（PRD -> 增删改 -> 视觉方案 -> Vibe Coding -> 改 Bug）
    Stage 2: 论文怎么写？
      Task 4: 论文写作全流程（预准备 -> 进行中 -> 修正 -> 持续进行 -> 补缺）

每个 Task 通过 chunk_key 关联 chunks.jsonl 中对应章节，AI 辅导时检索这些 chunk
作为参考资料注入 Prompt。验收标准（Rubric）取材于各节 "验收标准"。
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from schemas import (CodeContext, Course, Project, Rubric, SkillKey, Stage, Task)

BASE_DIR = Path(__file__).resolve().parent          # ai_engine/
ROOT_DIR = BASE_DIR.parent                          # xkz-agent/
DATA_DIR = ROOT_DIR / "data"
CHUNKS_FILE = DATA_DIR / "chunks.jsonl"


# ---------------------------------------------------------------------------
# Chunk 加载
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_chunks() -> list[dict]:
    """加载现有 RAG 数据库。字段含 id/doc/section/section_path/category/text/source_url。"""
    if not CHUNKS_FILE.exists():
        return []
    chunks = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    chunks.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return chunks


def chunks_by_doc(doc_keyword: str) -> list[dict]:
    """按文档标题关键字筛选 chunk（邪修学习指南的 doc 为 '学习指南(权限观看)'）。"""
    chunks = load_chunks()
    return [c for c in chunks if doc_keyword in c.get("doc", "")]


def chunks_by_section_path(keyword: str) -> list[dict]:
    """在整库中按 section_path 前缀匹配检索（用于跨文档补充材料）。"""
    chunks = load_chunks()
    return [c for c in chunks if keyword in c.get("section_path", "")]


# ---------------------------------------------------------------------------
# 课程结构：套壳聊天机器人（微项目，十几分钟可完成）
# ---------------------------------------------------------------------------
def _chatbot_project() -> Project:
    # ---- Stage 1：拆解与准备（对应 Tutor 拆解）----
    task_setup = Task(
        id="task_setup",
        title="拆解任务与准备环境",
        stage_id="stage_setup",
        order=1,
        objective="把'做一个聊天机器人'拆成可执行的小块：前端页面 + 后端接口，并装好环境和准备 API Key。",
        steps=[
            "说清目标：网页 + 后端接口，把消息转发给 DeepSeek，再把回答显示出来",
            "确认环境：装好 Python，能跑 python --version",
            "准备一个 DeepSeek API Key（BYOK，用你自己的）",
            "建项目文件夹，理清'前端负责什么、后端负责什么'",
        ],
        evidence_required="none",
        rubric_ids=["rb_setup_1", "rb_setup_2", "rb_setup_3"],
        skill=SkillKey.env_setup,
        chunk_key="套壳聊天机器人实战 > 前置准备",
        code_context=CodeContext(
            keywords=["python", "version", "api key", "deepseek", "项目结构", "前端", "后端"],
            likelyFiles=[],
            searchPatterns=[],
        ),
    )

    # ---- Stage 2：开发（对应 Coach 推进 / Debugger 调错）----
    task_backend = Task(
        id="task_backend",
        title="写后端接口",
        stage_id="stage_dev",
        order=1,
        objective="用 FastAPI 写一个 POST /chat 接口：接收消息→转发 DeepSeek→返回回答，能 uvicorn 启动。",
        steps=[
            "建 main.py，定义 POST /chat 接口，接收 {message}",
            "用 httpx 带自己的 Key 转发给 DeepSeek /chat/completions",
            "把返回的 choices[0].message.content 抽出来作为 {reply}",
            "打开 CORS，用 uvicorn main:app --reload --port 8000 启动成功",
        ],
        evidence_required="code",
        rubric_ids=["rb_backend_1", "rb_backend_2", "rb_backend_3", "rb_backend_4"],
        skill=SkillKey.project_dev,
        chunk_key="套壳聊天机器人实战 > 后端接口",
        code_context=CodeContext(
            keywords=["post", "chat", "fastapi", "deepseek", "httpx", "cors", "uvicorn", "message", "reply"],
            likelyFiles=["main", "app", "server", "requirements"],
            searchPatterns=["@app\\.post", "httpx", "chat/completions", "choices\\[0\\]"],
        ),
    )
    task_frontend = Task(
        id="task_frontend",
        title="写前端页面",
        stage_id="stage_dev",
        order=2,
        objective="用一个独立的 index.html 做出聊天界面：输入框 + 消息列表 + 发送按钮，点击发送用 fetch 把消息 POST 给后端。",
        steps=[
            "建 index.html，做出输入框、消息列表、发送按钮",
            "点发送后把输入内容 POST 到后端的 /chat",
            "把后端返回的 reply 显示到消息列表，并自动滚动到底部",
        ],
        evidence_required="code",
        rubric_ids=["rb_frontend_1", "rb_frontend_2", "rb_frontend_3"],
        skill=SkillKey.vibe_coding,
        chunk_key="套壳聊天机器人实战 > 前端页面",
        code_context=CodeContext(
            keywords=["fetch", "input", "button", "send", "message", "reply", "chat", "滚动", "scroll"],
            likelyFiles=["index", "app", "style"],
            searchPatterns=["fetch\\(", "addEventListener", "onclick", "scrollTop"],
        ),
    )
    task_link = Task(
        id="task_link",
        title="联调跑通",
        stage_id="stage_dev",
        order=3,
        objective="把前后端连起来：启动后端、打开页面，输入问题能看到机器人回答，消息能滚动。",
        steps=[
            "启动后端（uvicorn main:app --port 8000），确认端口在监听",
            "用浏览器打开 index.html，输入问题点发送",
            "看到机器人回答即联调成功；报错按'后端端口→前端地址→CORS'三步排查",
        ],
        evidence_required="test",
        rubric_ids=["rb_link_1", "rb_link_2", "rb_link_3"],
        skill=SkillKey.project_dev,
        chunk_key="套壳聊天机器人实战 > 联调与验收",
        code_context=CodeContext(
            keywords=["cors", "port", "8000", "uvicorn", "fetch", "localhost", "error", "报错"],
            likelyFiles=["main", "index", "config"],
            searchPatterns=["cors", "uvicorn", "fetch\\(", "localhost"],
        ),
    )

    # ---- Stage 3：验收（对应 Reviewer 评审）----
    task_review = Task(
        id="task_review",
        title="提交成果验收",
        stage_id="stage_accept",
        order=1,
        objective="对照验收标准逐条自查并提交成果，让 AI 评审打分。",
        steps=[
            "逐条对照验收标准自查：能问答、消息能滚动、Key 只在后端",
            "把页面运行效果/代码发给 AI，说明前后端各自做了什么",
            "根据评审意见补缺后再次提交",
        ],
        evidence_required="code",
        rubric_ids=["rb_review_1", "rb_review_2", "rb_review_3", "rb_review_4"],
        skill=SkillKey.project_dev,
        chunk_key="套壳聊天机器人实战 > 联调与验收",
        code_context=CodeContext(
            keywords=["post", "chat", "fetch", "cors", "api key", "key", "滚动", "scroll"],
            likelyFiles=["main", "index", "requirements"],
            searchPatterns=["@app\\.post", "fetch\\(", "cors", "scrollTop"],
        ),
    )

    # ---- Rubrics（每条 criterion 独立一个 Rubric 对象，支撑逐条评审打分）----
    # —— task_setup：拆解与准备（证据：自述说明 none）——
    rubric_setup = [
        Rubric(id="rb_setup_1", task_id="task_setup", criterion="能说清项目由哪几部分组成（前端+后端）",
               description="能讲清前端负责展示和发送、后端负责转发 DeepSeek",
               required_evidence=["description"], pass_condition="能准确说出前后端各自职责", weight=1),
        Rubric(id="rb_setup_2", task_id="task_setup", criterion="Python 环境就绪，能跑 python --version",
               description="本机已装 Python，能正常执行版本命令",
               required_evidence=["description"], pass_condition="能贴出版本命令输出或说明已装好", weight=1),
        Rubric(id="rb_setup_3", task_id="task_setup", criterion="已准备一个可用的 DeepSeek API Key",
               description="学生自己持有可用的 API Key",
               required_evidence=["description"], pass_condition="确认 Key 由学生自己持有且未贴出明文", weight=1),
    ]
    # —— task_backend：写后端接口（证据：code / runtime）——
    rubric_backend = [
        Rubric(id="rb_backend_1", task_id="task_backend", criterion="有 POST /chat 接口，接收 message 返回 reply",
               description="FastAPI 定义了 /chat 接口，输入输出结构正确",
               required_evidence=["code"], pass_condition="代码中存在 POST /chat，能接收 message 并返回 reply", weight=1),
        Rubric(id="rb_backend_2", task_id="task_backend", criterion="转发时带上自己的 API Key 调用 DeepSeek",
               description="用 httpx 调用 /chat/completions，Key 未硬编码暴露",
               required_evidence=["code"], pass_condition="请求含有 Key 字段且来源非硬编码前端", weight=1),
        Rubric(id="rb_backend_3", task_id="task_backend", criterion="能 uvicorn 启动且接口可被调用返回回答",
               description="服务启动成功，请求能收到回答",
               required_evidence=["code", "runtime"], pass_condition="有启动成功的运行证据或可复现命令", weight=1),
        Rubric(id="rb_backend_4", task_id="task_backend", criterion="能解释每段代码的作用（接口/转发/取回答）",
               description="学生理解并讲清自己写的代码",
               required_evidence=["description"], pass_condition="能自述接口、转发、取回答逻辑", weight=1),
    ]
    # —— task_frontend：写前端页面（证据：code / runtime）——
    rubric_frontend = [
        Rubric(id="rb_frontend_1", task_id="task_frontend", criterion="页面有输入框、消息列表、发送按钮并能点击",
               description="聊天界面元素齐全，发送入口可用",
               required_evidence=["code"], pass_condition="代码含上述元素", weight=1),
        Rubric(id="rb_frontend_2", task_id="task_frontend", criterion="发送后 fetch 把消息 POST 给后端并显示回答",
               description="前端调用后端 /chat 并渲染返回内容",
               required_evidence=["code", "runtime"], pass_condition="fetch 请求存在且能收到并显示回答", weight=1),
        Rubric(id="rb_frontend_3", task_id="task_frontend", criterion="消息多了能滚动，最新消息在最下",
               description="消息列表自动滚动到底部",
               required_evidence=["code"], pass_condition="代码含滚动逻辑", weight=1),
    ]
    # —— task_link：联调跑通（证据：runtime / test）——
    rubric_link = [
        Rubric(id="rb_link_1", task_id="task_link", criterion="前后端联通：页面能收到机器人回答",
               description="输入问题能在页面看到机器人回复",
               required_evidence=["runtime", "test"], pass_condition="有实际运行的联通证据", weight=1),
        Rubric(id="rb_link_2", task_id="task_link", criterion="报错能按后端端口→前端地址→CORS 正确排查",
               description="遇到报错能按三步排查定位",
               required_evidence=["description", "runtime"], pass_condition="能描述排查过程或已解决的报错", weight=1),
        Rubric(id="rb_link_3", task_id="task_link", criterion="API Key 未出现在前端页面里",
               description="Key 只存在于后端，前端不泄露",
               required_evidence=["code"], pass_condition="前端代码中无明文 Key", weight=2),
    ]
    # —— task_review：提交验收（证据：runtime / deployment / description）——
    rubric_review = [
        Rubric(id="rb_review_1", task_id="task_review", criterion="能正常问答：输入问题看到机器人回答",
               description="核心功能可用",
               required_evidence=["runtime", "deployment"], pass_condition="有运行/部署证据", weight=2),
        Rubric(id="rb_review_2", task_id="task_review", criterion="消息能滚动，最新消息在最下方",
               description="列表滚动正常",
               required_evidence=["code"], pass_condition="代码含滚动逻辑或自述佐证", weight=1),
        Rubric(id="rb_review_3", task_id="task_review", criterion="API Key 只在后端代码，未硬编码进前端",
               description="安全要求",
               required_evidence=["code"], pass_condition="代码证据显示 Key 未暴露前端", weight=1),
        Rubric(id="rb_review_4", task_id="task_review", criterion="能讲清前端→后端→DeepSeek→前端完整数据流向",
               description="理解整体架构",
               required_evidence=["description"], pass_condition="能清晰自述数据流向", weight=1),
    ]

    stage_setup = Stage(
        id="stage_setup", title="① 拆解与准备", order=1,
        objective="用 Tutor 把任务拆成可执行的小块，准备好环境",
        tasks=["task_setup"],
    )
    stage_dev = Stage(
        id="stage_dev", title="② 开发与联调", order=2,
        objective="用 Coach 推进、Debugger 调错，把前后端写出来并跑通",
        tasks=["task_backend", "task_frontend", "task_link"],
    )
    stage_accept = Stage(
        id="stage_accept", title="③ 提交验收", order=3,
        objective="用 Reviewer 对照验收标准评审打分",
        tasks=["task_review"],
    )

    return Project(
        id="project_chatbot",
        title="套壳聊天机器人",
        description="十几分钟做一个'网页 + 后端转发 DeepSeek'的最小聊天机器人，体验前后端到 AI API 的最小闭环。",
        stages=[stage_setup, stage_dev, stage_accept],
        tasks=[task_setup, task_backend, task_frontend, task_link, task_review],
        rubrics=[*rubric_setup, *rubric_backend, *rubric_frontend, *rubric_link, *rubric_review],
    )


def default_course() -> Course:
    proj = _chatbot_project()
    return Course(
        id="course_001",
        title="AI 微项目实战（套壳聊天机器人）",
        description="十几分钟完成一个套壳聊天机器人，体验'前端→后端→大模型 API'最小闭环。",
        projects=[proj.id],
    )


# ---------------------------------------------------------------------------
# 快速查找
# ---------------------------------------------------------------------------
_project_cache: Project | None = None


def get_course(course_id: str = "course_001") -> Course:
    course = default_course()
    return course


def get_project(project_id: str = "project_chatbot") -> Project:
    global _project_cache
    if _project_cache is None:
        _project_cache = _chatbot_project()
    return _project_cache


def get_task(task_id: str) -> Task | None:
    proj = get_project()
    return next((t for t in proj.tasks if t.id == task_id), None)


def get_stage(stage_id: str) -> Stage | None:
    proj = get_project()
    return next((s for s in proj.stages if s.id == stage_id), None)


def get_rubrics(task_id: str) -> list[Rubric]:
    proj = get_project()
    task = get_task(task_id)
    if not task:
        return []
    return [r for r in proj.rubrics if r.id in task.rubric_ids]


def list_projects() -> list[dict]:
    """供测试页面前端选择项目。"""
    proj = get_project()
    return [{
        "project_id": proj.id,
        "title": proj.title,
        "description": proj.description,
        "stages": [{
            "stage_id": s.id, "title": s.title, "objective": s.objective,
            "tasks": [{
                "task_id": t.id, "title": t.title, "objective": t.objective,
                "skill": t.skill.value if t.skill else None,
            } for t in proj.tasks if t.stage_id == s.id],
        } for s in proj.stages],
    }]