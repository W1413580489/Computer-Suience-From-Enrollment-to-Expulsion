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


# ---------------------------------------------------------------------------
# 课程 02：GitHub 项目分析 Agent（第一份标准样板，数据驱动）
# ---------------------------------------------------------------------------
def _agent_project() -> Project:
    # ---- Stage 1：认识 Agent ----
    task_intro = Task(
        id="c2t01",
        title="认识 Agent 与项目骨架",
        stage_id="c2_stage1",
        order=1,
        objective="说清 Agent 与普通聊天机器人的区别（是否调用工具/是否多步/是否自主决策），搭好课程项目骨架（agent.py、tools.py、.env、requirements.txt），CLI 能运行并打印问候。开始前先完成前置教程：申请 GitHub Token（教程见攻略页与飞书链接：https://tralis2671.feishu.cn/wiki/Urq6w7wOiiAFe4kzGnmciPxYnCd）。",
        steps=[
            "读前置教程（飞书链接见上），申请 GitHub Token 并放入 .env（课程第一天完成）",
            "建项目文件夹与虚拟环境，安装 openai、httpx、python-dotenv",
            "在 .env 放置所选 LLM API 的 Key（沿用上一课 BYOK 习惯）",
            "写 agent.py：读入用户问题 → 调用所选 LLM API → 打印回答",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t01_1", "rb_c2t01_2", "rb_c2t01_3"],
        skill=SkillKey.ai_assisted,
        chunk_key="GitHub 项目分析 Agent > T01 认识 Agent 与项目骨架",
        code_context=CodeContext(
            keywords=["agent", "openai", "deepseek", "dotenv", "cli"],
            likelyFiles=["agent", "main"],
            searchPatterns=["OpenAI\\(", "chat\\.completions"],
        ),
    )
    task_min_loop = Task(
        id="c2t02",
        title="最小 Agent Loop（单工具）",
        stage_id="c2_stage1",
        order=2,
        objective="给 Agent 一个内置工具（如 get_current_time），用 tools 参数声明 JSON Schema，实现'模型决定调用 → 执行 → 结果回传 → 模型回答'的最小闭环，并开始用 --trace 输出执行轨迹。",
        steps=[
            "用 tools 参数向所选 LLM API 声明工具的 JSON Schema",
            "检查响应中的 tool_calls：没有就直接回答并结束",
            "有则本地执行工具，把结果以 role=tool 消息回传",
            "再次调用模型拿到最终回答；加 --trace 参数输出 agent_trace.json",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t02_1", "rb_c2t02_2", "rb_c2t02_3", "rb_c2t02_4"],
        skill=SkillKey.workflow,
        chunk_key="GitHub 项目分析 Agent > T02 最小 Agent Loop",
        code_context=CodeContext(
            keywords=["tool_calls", "tools", "function", "loop", "role"],
            likelyFiles=["agent"],
            searchPatterns=["tool_calls", "tools\\s*=", "role.*tool"],
        ),
    )

    # ---- Stage 2：接入 GitHub 工具 ----
    task_client = Task(
        id="c2t03",
        title="GitHub API Client 与 Token 限流",
        stage_id="c2_stage2",
        order=1,
        objective="封装 GitHubClient：自动带 Token 请求头；区分 401/403+限流/404 三种错误；限流按 Retry-After 退避一次重试；错误以结构化形式返回，不静默吞掉。",
        steps=[
            "建 github_client.py，封装 get(url)：自动加 Authorization: Bearer 头",
            "区分处理 401（Token 无效）、403+X-RateLimit-Remaining:0（限流，退避一次重试）、404（不存在）",
            "错误以 {ok:false, code:..., error:...} 结构返回给调用方",
            "写 3 个单元测试（mock HTTP 响应）覆盖三种分支",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t03_1", "rb_c2t03_2", "rb_c2t03_3", "rb_c2t03_4"],
        skill=SkillKey.project_dev,
        chunk_key="GitHub 项目分析 Agent > T03 GitHub API Client 与 Token 限流",
        code_context=CodeContext(
            keywords=["github", "token", "rate", "403", "authorization", "retry"],
            likelyFiles=["github_client", "api_client", "github"],
            searchPatterns=["Authorization", "X-RateLimit", "403", "retry"],
        ),
    )
    task_repo_tools = Task(
        id="c2t04",
        title="仓库信息与文件树工具",
        stage_id="c2_stage2",
        order=2,
        objective="基于 GitHubClient 实现两个只读工具：get_repo_info（语言/star/描述/默认分支）与 get_file_tree（递归文件树，只留文件、前 200 项截断并注明），各配单元测试。",
        steps=[
            "get_repo_info：调 /repos/{owner}/{repo}，抽取关键字段为紧凑文本",
            "get_file_tree：调 /git/trees/{branch}?recursive=1，过滤目录只留文件，超 200 项截断",
            "各写 1-2 个单测（mock 响应）",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t04_1", "rb_c2t04_2", "rb_c2t04_3"],
        skill=SkillKey.project_dev,
        chunk_key="GitHub 项目分析 Agent > T04 仓库信息与文件树工具",
        code_context=CodeContext(
            keywords=["repos", "git/trees", "file tree", "repo info"],
            likelyFiles=["tools", "github_client"],
            searchPatterns=["repos/", "git/trees", "def get_repo", "def get_file_tree"],
        ),
    )
    task_content_tool = Task(
        id="c2t05",
        title="文件内容工具与大小保护",
        stage_id="c2_stage2",
        order=3,
        objective="实现 get_file_content(owner/repo, path)：Contents API 拉取并 base64 解码，超 200 行截断标注；对不存在/二进制/空文件给出友好返回；单测覆盖三条路径。",
        steps=[
            "调 Contents API 拉取文件，base64 解码",
            "行数超 200 截断，追加'已截断'标注",
            "异常路径：文件不存在、二进制文件、空文件",
            "单测覆盖 正常/截断/不存在 三条路径",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t05_1", "rb_c2t05_2", "rb_c2t05_3"],
        skill=SkillKey.project_dev,
        chunk_key="GitHub 项目分析 Agent > T05 文件内容工具与大小保护",
        code_context=CodeContext(
            keywords=["contents", "base64", "truncate", "file content"],
            likelyFiles=["tools"],
            searchPatterns=["contents/", "b64decode", "truncat"],
        ),
    )

    # ---- Stage 3：工具驱动执行 ----
    task_registry = Task(
        id="c2t06",
        title="工具注册与 Schema 设计",
        stage_id="c2_stage3",
        order=1,
        objective="建立统一工具注册表（TOOL_MAP + JSON Schema 列表），让 T02 的 Loop 能看到全部三个 GitHub 工具，并用三类提问验证模型选对工具。",
        steps=[
            "每个工具写规范 Schema：名称、用途描述（描述是写给模型看的！）、参数类型",
            "建注册表：名字 → (函数, Schema)，Loop 只认注册表",
            "用三类提问（'这个仓库是什么语言'/'列出文件结构'/'看看 main.py 内容'）验证模型选对工具，Trace 留档",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t06_1", "rb_c2t06_2", "rb_c2t06_3"],
        skill=SkillKey.workflow,
        chunk_key="GitHub 项目分析 Agent > T06 工具注册与 Schema",
        code_context=CodeContext(
            keywords=["tool map", "schema", "register", "description"],
            likelyFiles=["tools", "agent"],
            searchPatterns=["TOOL_MAP", "\"type\": \"function\"", "description"],
        ),
    )
    task_multi_loop = Task(
        id="c2t07",
        title="多步 Agent Loop（结果驱动决策）",
        stage_id="c2_stage3",
        order=2,
        objective="把单次调用升级为 while 循环：工具结果回传后模型可继续要求调用其他工具，直到认为信息足够才输出最终回答；每步写入 trace。演示'分析一个仓库'出现至少 2 次连续工具调用。",
        steps=[
            "把单次调用改成 while 循环：有 tool_calls 就执行回传并继续",
            "每一步写入 trace（step/tool_name/arguments/result_summary/timestamp）",
            "用'分析某个公开仓库的项目结构'类任务演示多步行为",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t07_1", "rb_c2t07_2", "rb_c2t07_3", "rb_c2t07_4"],
        skill=SkillKey.workflow,
        chunk_key="GitHub 项目分析 Agent > T07 多步 Agent Loop",
        code_context=CodeContext(
            keywords=["while", "multi step", "trace", "tool_calls"],
            likelyFiles=["agent"],
            searchPatterns=["while", "tool_calls", "trace"],
        ),
    )
    task_safety = Task(
        id="c2t08",
        title="max_steps 与安全退出",
        stage_id="c2_stage3",
        order=3,
        objective="给 Loop 加 max_steps 上限（默认 10）、工具执行异常捕获（错误回传模型让它自行调整）与步数耗尽后的安全退出，trace 记录 stop_reason；单测证明不会死循环。",
        steps=[
            "用 for step in range(max_steps) 替代裸 while",
            "工具执行包 try/except：异常以文本回传模型，trace 记录失败",
            "步数耗尽 → 写入 stop_reason:max_steps_reached，输出已收集的部分结果",
            "单测：mock 连续失败的工具，验证不会死循环",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t08_1", "rb_c2t08_2", "rb_c2t08_3", "rb_c2t08_4"],
        skill=SkillKey.workflow,
        chunk_key="GitHub 项目分析 Agent > T08 max_steps 与安全退出",
        code_context=CodeContext(
            keywords=["max_steps", "stop_reason", "exception", "safety"],
            likelyFiles=["agent"],
            searchPatterns=["max_steps", "stop_reason", "except"],
        ),
    )

    # ---- Stage 4：完成项目 ----
    task_report = Task(
        id="c2t09",
        title="带证据的项目分析报告",
        stage_id="c2_stage4",
        order=1,
        objective="CLI 输入仓库地址与分析需求，Agent 自主调用工具收集信息，生成 report.md（概况/结构/关键文件/结论建议），每个结论引用实际工具调用结果（[见 trace step N]），全程 --trace 运行。",
        steps=[
            "设计报告结构：概况 / 结构分析 / 关键文件解读 / 结论与建议",
            "报告中的事实必须来自工具调用结果，引用 step 编号",
            "全程 --trace 运行，agent_trace.json 与 report.md 一并提交",
        ],
        evidence_required="code",
        rubric_ids=["rb_c2t09_1", "rb_c2t09_2", "rb_c2t09_3", "rb_c2t09_4"],
        skill=SkillKey.project_dev,
        chunk_key="GitHub 项目分析 Agent > T09 带证据的分析报告",
        code_context=CodeContext(
            keywords=["report", "markdown", "evidence", "引用"],
            likelyFiles=["agent", "report"],
            searchPatterns=["report\\.md", "trace", "step"],
        ),
    )

    # ---- Rubrics（判据全部可客观判定；不出现具体厂商名，统一'所选 LLM API'）----
    rubric_c2t01 = [
        Rubric(id="rb_c2t01_1", task_id="c2t01", criterion="项目骨架齐全且 CLI 可运行",
               description="agent.py/tools.py/.env/requirements.txt 齐备，CLI 运行打印回答",
               required_evidence=["code"], pass_condition="文件齐全且能运行", weight=2),
        Rubric(id="rb_c2t01_2", task_id="c2t01", criterion="能说清 Agent 与聊天机器人至少两条区别",
               description="区别围绕：是否调用工具/是否多步/是否自主决策",
               required_evidence=["description"], pass_condition="自述含至少两条要点", weight=1),
        Rubric(id="rb_c2t01_3", task_id="c2t01", criterion="GitHub Token 已配置且源码无硬编码",
               description=".env 存在，.gitignore 包含 .env，源码无 ghp_ 明文",
               required_evidence=["code"], pass_condition="grep 无明文 Token 且 .env 存在", weight=2),
    ]
    rubric_c2t02 = [
        Rubric(id="rb_c2t02_1", task_id="c2t02", criterion="工具以 JSON Schema 声明且被模型接收",
               description="tools 参数存在且结构正确",
               required_evidence=["code"], pass_condition="代码含规范的 tools 声明", weight=2),
        Rubric(id="rb_c2t02_2", task_id="c2t02", criterion="存在工具结果回传逻辑（role=tool）",
               description="工具结果作为消息回传给模型",
               required_evidence=["code"], pass_condition="代码含回传逻辑", weight=2),
        Rubric(id="rb_c2t02_3", task_id="c2t02", criterion="能演示一次完整闭环运行",
               description="问时间类问题得到正确回答",
               required_evidence=["code", "runtime"], pass_condition="有运行演示或输出截图/文本", weight=2),
        Rubric(id="rb_c2t02_4", task_id="c2t02", criterion="能解释'为什么结果要回传给模型而不是直接打印'",
               description="理解回传后模型才能基于结果作答",
               required_evidence=["description"], pass_condition="自述正确", weight=1),
    ]
    rubric_c2t03 = [
        Rubric(id="rb_c2t03_1", task_id="c2t03", criterion="Token 从环境变量读取，源码与提交记录无硬编码",
               description="os.getenv 读取，.gitignore 包含 .env",
               required_evidence=["code"], pass_condition="grep 无明文 Token", weight=2),
        Rubric(id="rb_c2t03_2", task_id="c2t03", criterion="401/403/404 三种错误有区分处理且信息可读",
               description="分支齐全，错误信息结构化",
               required_evidence=["code"], pass_condition="单测覆盖三分支", weight=2),
        Rubric(id="rb_c2t03_3", task_id="c2t03", criterion="限流时有退避重试且不会无限重试",
               description="读 Retry-After/X-RateLimit 头，退避一次",
               required_evidence=["code"], pass_condition="单测 mock 限流响应验证", weight=2),
        Rubric(id="rb_c2t03_4", task_id="c2t03", criterion="能解释 Token 泄露的风险与处理方式",
               description="风险：他人可冒充身份操作；处理：Revoke 并重新生成",
               required_evidence=["description"], pass_condition="自述含 Revoke", weight=1),
    ]
    rubric_c2t04 = [
        Rubric(id="rb_c2t04_1", task_id="c2t04", criterion="两个工具存在且经统一的 GitHubClient",
               description="不直接裸调 httpx",
               required_evidence=["code"], pass_condition="统一走 Client", weight=2),
        Rubric(id="rb_c2t04_2", task_id="c2t04", criterion="文件树有截断保护（超 200 项）",
               description="截断并注明总数",
               required_evidence=["code"], pass_condition="单测覆盖超长列表", weight=2),
        Rubric(id="rb_c2t04_3", task_id="c2t04", criterion="对真实公开仓库能取回数据",
               description="演示输出仓库元信息与文件树",
               required_evidence=["code", "runtime"], pass_condition="有真实运行输出", weight=1),
    ]
    rubric_c2t05 = [
        Rubric(id="rb_c2t05_1", task_id="c2t05", criterion="文件内容工具可用且经统一 Client",
               description="Contents API 拉取并 base64 解码",
               required_evidence=["code"], pass_condition="实现正确", weight=2),
        Rubric(id="rb_c2t05_2", task_id="c2t05", criterion="截断与异常路径齐全（超行/不存在/二进制/空）",
               description="三条异常路径都有友好返回",
               required_evidence=["code"], pass_condition="单测覆盖", weight=2),
        Rubric(id="rb_c2t05_3", task_id="c2t05", criterion="能说清'为什么要截断'",
               description="上下文是有限资源",
               required_evidence=["description"], pass_condition="自述提到上下文限制", weight=1),
    ]
    rubric_c2t06 = [
        Rubric(id="rb_c2t06_1", task_id="c2t06", criterion="三个工具全部经注册表暴露给模型",
               description="无散落的硬编码工具调用",
               required_evidence=["code"], pass_condition="注册表统一管理", weight=2),
        Rubric(id="rb_c2t06_2", task_id="c2t06", criterion="工具描述清晰，三类提问均选中正确工具",
               description="描述是写给模型看的",
               required_evidence=["code", "runtime"], pass_condition="Trace 显示选对工具", weight=2),
        Rubric(id="rb_c2t06_3", task_id="c2t06", criterion="能说清新增一个工具需要做几步",
               description="写函数→写 Schema→注册",
               required_evidence=["description"], pass_condition="自述完整", weight=1),
    ]
    rubric_c2t07 = [
        Rubric(id="rb_c2t07_1", task_id="c2t07", criterion="复杂分析任务中出现 ≥2 次连续工具调用",
               description="多步行为真实发生",
               required_evidence=["code", "trace"], pass_condition="Trace 可见多步", weight=2),
        Rubric(id="rb_c2t07_2", task_id="c2t07", criterion="后续调用依赖前序结果",
               description="参数与上一步结果相关",
               required_evidence=["trace"], pass_condition="Trace 参数体现关联", weight=2),
        Rubric(id="rb_c2t07_3", task_id="c2t07", criterion="trace 文件结构符合约定字段",
               description="step/tool_name/arguments/result_summary/timestamp",
               required_evidence=["code", "trace"], pass_condition="agent_trace.json 字段齐全", weight=2),
        Rubric(id="rb_c2t07_4", task_id="c2t07", criterion="能讲清'多步'与'一问一答'的本质区别",
               description="状态在循环中累积",
               required_evidence=["description"], pass_condition="自述正确", weight=1),
    ]
    rubric_c2t08 = [
        Rubric(id="rb_c2t08_1", task_id="c2t08", criterion="存在可配置的 max_steps 上限",
               description="默认 10，可调",
               required_evidence=["code"], pass_condition="代码含上限逻辑", weight=2),
        Rubric(id="rb_c2t08_2", task_id="c2t08", criterion="工具异常不终止 Agent，错误回传模型",
               description="try/except 后错误信息回传",
               required_evidence=["code"], pass_condition="单测 mock 失败验证", weight=2),
        Rubric(id="rb_c2t08_3", task_id="c2t08", criterion="超限安全退出且 trace 记录 stop_reason",
               description="max_steps_reached",
               required_evidence=["code", "trace"], pass_condition="CI 或 Trace 验证", weight=2),
        Rubric(id="rb_c2t08_4", task_id="c2t08", criterion="能说出不设上限的两个后果",
               description="token 消耗失控 + 死循环",
               required_evidence=["description"], pass_condition="自述完整", weight=1),
    ]
    rubric_c2t09 = [
        Rubric(id="rb_c2t09_1", task_id="c2t09", criterion="report.md 存在且结构完整（概况/结构/关键文件/结论）",
               description="Markdown 报告",
               required_evidence=["code", "runtime"], pass_condition="结构四部分齐全", weight=2),
        Rubric(id="rb_c2t09_2", task_id="c2t09", criterion="关键结论可追溯到 trace 步骤",
               description="引用格式 [见 trace step N]，抽查 3 条",
               required_evidence=["trace"], pass_condition="引用与 trace 一致", weight=2),
        Rubric(id="rb_c2t09_3", task_id="c2t09", criterion="trace 显示 Agent 自主完成 ≥3 步且含多种工具",
               description="多工具组合调用",
               required_evidence=["trace"], pass_condition="Trace 满足", weight=2),
        Rubric(id="rb_c2t09_4", task_id="c2t09", criterion="报告内容与所选仓库真实对应",
               description="抽查仓库实际信息与报告结论一致",
               required_evidence=["trace", "description"], pass_condition="抽查无捏造", weight=1),
    ]

    stage1 = Stage(id="c2_stage1", title="① 认识 Agent", order=1,
                   objective="理解 Agent 与聊天机器人的差别，完成第一个最小工具调用闭环", tasks=["c2t01", "c2t02"])
    stage2 = Stage(id="c2_stage2", title="② 接入 GitHub 工具", order=2,
                   objective="实现 GitHub Client 与三个只读工具，处理好 Token 与限流", tasks=["c2t03", "c2t04", "c2t05"])
    stage3 = Stage(id="c2_stage3", title="③ 工具驱动执行", order=3,
                   objective="注册工具、建立多步 Loop、加上安全退出", tasks=["c2t06", "c2t07", "c2t08"])
    stage4 = Stage(id="c2_stage4", title="④ 完成项目", order=4,
                   objective="综合调用工具，生成带证据的项目分析报告", tasks=["c2t09"])

    return Project(
        id="project_agent",
        title="GitHub 项目分析 Agent",
        description="做一个会读 GitHub 仓库、自主选择工具、多步执行并输出带证据分析报告的 CLI 智能体。前置：已完成《套壳聊天机器人》。",
        stages=[stage1, stage2, stage3, stage4],
        tasks=[task_intro, task_min_loop, task_client, task_repo_tools, task_content_tool,
               task_registry, task_multi_loop, task_safety, task_report],
        rubrics=[*rubric_c2t01, *rubric_c2t02, *rubric_c2t03, *rubric_c2t04, *rubric_c2t05,
                 *rubric_c2t06, *rubric_c2t07, *rubric_c2t08, *rubric_c2t09],
    )


# ---------------------------------------------------------------------------
# 课程注册表与快速查找（多课程数据驱动，task_id 全局唯一）
# ---------------------------------------------------------------------------
_PROJECT_BUILDERS = {
    "project_chatbot": _chatbot_project,
    "project_agent": _agent_project,
}
_COURSES: dict[str, dict] = {
    "course_001": {
        "title": "AI 微项目实战（套壳聊天机器人）",
        "description": "十几分钟完成一个套壳聊天机器人，体验'前端→后端→大模型 API'最小闭环。",
        "projects": ["project_chatbot"],
    },
    "course_002": {
        "title": "Agent 实战（GitHub 项目分析）",
        "description": "做一个会调用工具、多步执行、输出带证据报告的 CLI Agent。前置：已完成套壳聊天机器人。",
        "projects": ["project_agent"],
    },
}
_project_cache: dict[str, Project] = {}


def get_course(course_id: str = "course_001") -> Course | None:
    info = _COURSES.get(course_id)
    if not info:
        return None
    return Course(id=course_id, title=info["title"],
                  description=info["description"], projects=list(info["projects"]))


def _project_summary(proj: Project) -> dict:
    return {
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
    }


def list_courses() -> list[dict]:
    """供前端课程选择器：课程列表 + 每门课的项目（含完整 stage/task 结构）。"""
    out = []
    for cid, info in _COURSES.items():
        projs = []
        for pid in info["projects"]:
            p = get_project(pid)
            if p:
                projs.append(_project_summary(p))
        out.append({"course_id": cid, "title": info["title"],
                    "description": info["description"], "projects": projs})
    return out


def get_project(project_id: str = "project_chatbot") -> Project | None:
    if project_id not in _PROJECT_BUILDERS:
        return None
    if project_id not in _project_cache:
        _project_cache[project_id] = _PROJECT_BUILDERS[project_id]()
    return _project_cache[project_id]


def get_task(task_id: str) -> Task | None:
    for pid in _PROJECT_BUILDERS:
        proj = get_project(pid)
        t = next((t for t in proj.tasks if t.id == task_id), None)
        if t:
            return t
    return None


def get_stage(stage_id: str) -> Stage | None:
    for pid in _PROJECT_BUILDERS:
        proj = get_project(pid)
        s = next((s for s in proj.stages if s.id == stage_id), None)
        if s:
            return s
    return None


def get_rubrics(task_id: str) -> list[Rubric]:
    for pid in _PROJECT_BUILDERS:
        proj = get_project(pid)
        if any(t.id == task_id for t in proj.tasks):
            return [r for r in proj.rubrics if r.id in
                    next(t.rubric_ids for t in proj.tasks if t.id == task_id)]
    return []


def list_projects(project_id: str | None = None) -> list[dict]:
    """供测试页面前端选择项目。project_id 为空时返回全部课程的项目。"""
    pids = [project_id] if project_id else list(_PROJECT_BUILDERS.keys())
    out = []
    for pid in pids:
        proj = get_project(pid)
        if not proj:
            continue
        out.append(_project_summary(proj))
    return out