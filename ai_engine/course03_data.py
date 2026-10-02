# -*- coding: utf-8 -*-
"""课程 03《从接手MCP开始的牛马生活》课程数据。

结构：一个课程（course_003）→ 两个项目
  project_mcp_build · 做出你的第一个 MCP Server      （T01–T07，Stage 1–2）
  project_mcp_test  · 把自己的工具当产品测试与迭代    （T08–T12，Stage 3–5）

设计依据：docs/课程03-完整设计.md
技术栈：Python 官方 mcp SDK（2.x 起 v1 的 FastMCP 已改名 MCPServer）
验收证据：全部走 GitHub（代码 / CI / 报告文件 / Issues），平台不建表单、不建数据库
"""
from schemas import (
    CodeContext,
    InterviewQuestion,
    Project,
    ResumePoint,
    Rubric,
    SkillKey,
    Stage,
    Task,
)

# 课程元信息（由 course_data 注册进 _COURSES）
COURSE_003 = {
    "title": "从接手MCP开始的牛马生活",
    "description": "接手一个已经做了一半的 AI 工具，用 Python 把它做成真正能用的 MCP Server；"
                   "然后自己当第一个真实用户去测试它、提 Issue、修好、做回归。",
    "projects": ["project_mcp_build", "project_mcp_test"],
    "img": "/courses/mcp.webp",
    "img_pos": "center 30%",
}


# ---------------------------------------------------------------------------
# 项目一：做出你的第一个 MCP Server
# ---------------------------------------------------------------------------
def build_project_mcp_build() -> Project:
    # ===================== Stage 1：让它先跑起来 =====================
    stage1 = Stage(
        id="c3_stage1", title="① 让它先跑起来", order=1,
        objective="装好环境、跑通官方最小示例、接进自己的 AI 客户端，并读懂前作的设计意图",
        tasks=["c3_t01", "c3_t02", "c3_t03"],
    )
    stage2 = Stage(
        id="c3_stage2", title="② 做出核心功能", order=2,
        objective="把「跨会话项目记忆」落成代码：数据结构、存储、自然语言归类、MCP 工具，并交付 v0.1",
        tasks=["c3_t04", "c3_t05", "c3_t06", "c3_t07"],
    )

    # ---- T01 环境准备与官方最小示例 ----
    task_t01 = Task(
        id="c3_t01", title="环境准备与官方最小示例", stage_id="c3_stage1", order=1,
        objective="在本机装好 Python 3.11+ 与官方 mcp 包，写一个约 10 行的最小 MCP server 并成功启动，"
                  "确认自己装的是官方包而不是同名的第三方框架。",
        steps=[
            "建项目目录与虚拟环境（python -m venv .venv），激活后 pip install mcp",
            "确认包来源：pip show mcp，看清是官方 Python SDK",
            "写最小 server：创建 MCPServer 实例 + 一个 add 工具（mcp 2.x 起 v1 的 FastMCP 已改名 MCPServer）",
            "在终端启动它，把启动输出留在手边（这就是本任务的运行证据）",
        ],
        evidence_required="code",
        rubric_ids=["rb_c3t01_1", "rb_c3t01_2"],
        skill=SkillKey.env_setup,
        chunk_key="课程03 > T01 环境准备与官方最小示例",
        code_context=CodeContext(
            keywords=["mcp", "mcpserver", "fastmcp", "tool", "venv"],
            likelyFiles=["server", "main", "requirements"],
            searchPatterns=["MCPServer\\(", "@\\w+\\.tool", "mcp\\.run"],
        ),
    )

    # ---- T02 接入你的 AI 客户端 ----
    task_t02 = Task(
        id="c3_t02", title="接入你的 AI 客户端", stage_id="c3_stage1", order=2,
        objective="把最小 server 配进自己的 AI 编程工具（Trae / Cursor / Claude Code / VS Code），"
                  "在客户端里看到工具并成功调用一次。",
        steps=[
            "先在终端手动跑通启动命令（配置里的 command+args 必须等价于它）",
            "按客户端要求写配置：command 指向解释器，args 指向 server 文件，路径用绝对路径",
            "重启客户端，在 MCP 列表里找到它，确认状态为已连接",
            "在对话里让 AI 调用一次工具，把工具清单与调用返回留下来",
        ],
        evidence_required="code",
        rubric_ids=["rb_c3t02_1", "rb_c3t02_2"],
        skill=SkillKey.project_dev,
        chunk_key="课程03 > T02 接入 AI 客户端",
        code_context=CodeContext(
            keywords=["mcpServers", "command", "args", "stdio", "config"],
            likelyFiles=["mcp", "config", "settings"],
            searchPatterns=["mcpServers", "\"command\"", "stdio"],
        ),
    )

    # ---- T03 读懂前作 ----
    task_t03 = Task(
        id="c3_t03", title="读懂前作：它到底解决什么问题", stage_id="c3_stage1", order=3,
        objective="阅读前作（TypeScript 版实现）的说明文档与类型定义，说清三件事：MCP 的三类能力分别是什么、"
                  "这个工具解决的真实痛点、它对外暴露了哪些能力。",
        steps=[
            "读前作的 README 与集成文档，列出它对外提供的能力清单",
            "读它的类型定义，看它把「记忆」抽象成了哪几类、有哪些状态",
            "用自己的话写一份不超过 300 字的设计理解笔记（这是本任务交付物）",
        ],
        evidence_required="none",
        rubric_ids=["rb_c3t03_1", "rb_c3t03_2"],
        skill=SkillKey.ai_assisted,
        chunk_key="课程03 > T03 读懂前作",
    )

    # ---- T04 Memory Schema 与 SQLite 存储 ----
    task_t04 = Task(
        id="c3_t04", title="Memory Schema 与 SQLite 存储", stage_id="c3_stage2", order=4,
        objective="定义记忆的数据结构与状态机，用 Python 标准库 sqlite3 落库（建表 + 索引 + 可重复执行的迁移），"
                  "能用一条查询把写入的记录查出来。",
        steps=[
            "定义记忆类型（想法/计划/决定/承诺/问题/约束）与状态、以及状态之间允许的迁移关系",
            "写建表语句与索引，用 IF NOT EXISTS 保证重复执行不报错（幂等迁移）",
            "实现增删查改，写一条记录，再用 SELECT 查出来并留下输出",
            "为状态迁移加校验：非法迁移返回可读原因，而不是抛异常",
        ],
        evidence_required="code",
        rubric_ids=["rb_c3t04_1", "rb_c3t04_2", "rb_c3t04_3"],
        skill=SkillKey.project_dev,
        chunk_key="课程03 > T04 Memory Schema 与 SQLite 存储",
        code_context=CodeContext(
            keywords=["sqlite3", "schema", "status", "kind", "commitment", "migrate"],
            likelyFiles=["storage", "db", "models", "types"],
            searchPatterns=["sqlite3\\.connect", "CREATE TABLE", "validate"],
        ),
        resume_points=[
            ResumePoint(point="定义 6 类记忆与状态机，并对非法状态迁移做校验",
                        purpose="避免状态乱跳导致记忆库不可信",
                        result="保障了记忆数据的一致性", kind="architecture"),
            ResumePoint(point="把建表与迁移写成幂等脚本（IF NOT EXISTS）",
                        purpose="让老库能平滑升级、重复执行不炸",
                        result="保障了可重复初始化与部署", kind="stability"),
        ],
    )

    # ---- T05 自然语言 Capture ----
    task_t05 = Task(
        id="c3_t05", title="自然语言 Capture：把一句话归类", stage_id="c3_stage2", order=5,
        objective="实现一句话自动归类：判断它属于哪种记忆类型、给出置信度；置信度低或本身模糊的，"
                  "标记为「需人工确认」而不是直接定论。",
        steps=[
            "写规则表：每种类型对应的语言信号（正则）+ 权重",
            "由权重算出置信度，设定阈值；低于阈值或天生模糊的类型标为需确认",
            "跑至少 3 句话（含 1 句模糊表达），把分类结果与置信度留下",
            "对判错的样例做一次调整并说明改了什么（为下一项目的测试埋点）",
        ],
        evidence_required="code",
        rubric_ids=["rb_c3t05_1", "rb_c3t05_2", "rb_c3t05_3"],
        skill=SkillKey.project_dev,
        chunk_key="课程03 > T05 自然语言 Capture",
        code_context=CodeContext(
            keywords=["classify", "confidence", "kind", "decision", "plan", "re"],
            likelyFiles=["capture", "classify", "rules"],
            searchPatterns=["re\\.compile", "confidence", "threshold"],
        ),
        resume_points=[
            ResumePoint(point="用规则 + 置信度阈值归类自然语言，低置信交人工确认",
                        purpose="避免把随口一说当成正式承诺",
                        result="减少了误记与脏数据", kind="architecture"),
        ],
    )

    # ---- T06 暴露成 MCP 工具 ----
    task_t06 = Task(
        id="c3_t06", title="把功能暴露成 MCP 工具", stage_id="c3_stage2", order=6,
        objective="用装饰器把已完成的能力包装成至少 4 个 MCP 工具，并为每个工具写清用途说明，"
                  "让 AI 能自己判断什么时候该调用哪个。",
        steps=[
            "把「记录 / 查询 / 更新状态 / 恢复上下文」四类能力各包一个工具",
            "给每个工具写清 description：它做什么、什么时候该用（AI 靠这段文字选工具）",
            "在客户端里确认工具清单，并演示一次自然对话中 AI 选对了工具",
        ],
        evidence_required="code",
        rubric_ids=["rb_c3t06_1", "rb_c3t06_2", "rb_c3t06_3"],
        skill=SkillKey.project_dev,
        chunk_key="课程03 > T06 暴露成 MCP 工具",
        code_context=CodeContext(
            keywords=["tool", "mcp", "description", "schema"],
            likelyFiles=["server", "main", "tools"],
            searchPatterns=["@\\w+\\.tool", "MCPServer\\(", "docstring"],
        ),
        resume_points=[
            ResumePoint(point="把记忆能力包装为 MCP 工具，并为每个工具写清用途说明",
                        purpose="让 AI 能自主判断何时调用哪个工具",
                        result="工具被正确选中的比例提升", kind="delivery"),
        ],
        interview_questions=[
            InterviewQuestion(
                id="iq_c3t06_1",
                question="面试官问：MCP 的 tools、resources、prompts 三者有什么区别？你的项目为什么主要用 tools？",
                answer_anchor="tools 是模型主动调用、可能有副作用的动作（如写入一条记忆）；resources 是客户端按需拉取的只读数据；prompts 是用户主动触发的模板。"
                              "本项目要做的是「记录 / 查询 / 更新」这类有副作用或有参数的动作，所以用 tools。",
                hint="从「谁发起调用」和「有没有副作用」两个角度区分。",
                type="explain",
            ),
            InterviewQuestion(
                id="iq_c3t06_2",
                question="排查题：客户端里看不到你的工具，你会按什么顺序排查？",
                answer_anchor="先看客户端配置的 command/args 能否在终端手动跑通 → 再看客户端 MCP 日志里 server 的启动报错 → "
                              "核对解释器路径（venv 里的 python）与依赖装在哪个环境 → 最后确认传输方式是 stdio。",
                hint="从「代码本身没问题」这个前提往外推：先证明 server 能跑，再查客户端怎么启动它。",
                type="debug",
            ),
        ],
    )

    # ---- T07 测试与交付 v0.1 ----
    task_t07 = Task(
        id="c3_t07", title="测试与交付 v0.1", stage_id="c3_stage2", order=7,
        objective="为核心逻辑写可重复运行的测试，补上 README 与运行说明，交付一个别人照着做就能跑起来的 v0.1。",
        steps=[
            "为「分类 / 状态迁移 / 存储读写」三类逻辑各写测试",
            "连跑两次测试，确认结果一致（第一次通过、第二次也通过）",
            "写 README：安装、配置、启动、测试四步齐全",
            "把代码推到 GitHub（后续验收与 Issue 都基于它）",
        ],
        evidence_required="code+test",
        rubric_ids=["rb_c3t07_1", "rb_c3t07_2", "rb_c3t07_3"],
        skill=SkillKey.project_dev,
        chunk_key="课程03 > T07 测试与交付 v0.1",
        code_context=CodeContext(
            keywords=["test", "assert", "pytest", "unittest", "readme"],
            likelyFiles=["test_", "conftest", "readme"],
            searchPatterns=["def test_", "assert ", "python -m pytest"],
        ),
        resume_points=[
            ResumePoint(point="为核心逻辑写了可重复运行的测试（覆盖分类/状态迁移/存储）",
                        purpose="避免测试因为残留数据而只能跑一次",
                        result="测试可稳定复现，为后续回归打好基础", kind="engineering"),
        ],
    )

    rubrics = [
        # T01
        Rubric(id="rb_c3t01_1", task_id="c3_t01", criterion="依赖安装正确（官方 mcp 包）",
               description="依赖清单里是官方 Python SDK，而不是同名的第三方框架",
               required_evidence=["code", "runtime"],
               pass_condition="依赖文件里写明官方 mcp 包，且贴出安装命令的输出", weight=1),
        Rubric(id="rb_c3t01_2", task_id="c3_t01", criterion="最小 server 能成功启动",
               description="写好最小 server 并启动，无报错",
               required_evidence=["runtime"],
               pass_condition="贴出启动输出（stdio 模式），无 traceback", weight=1),
        # T02
        Rubric(id="rb_c3t02_1", task_id="c3_t02", criterion="客户端配置正确",
               description="配置片段的 command/args 指向正确的解释器与 server 文件",
               required_evidence=["code", "runtime"],
               pass_condition="配置片段完整，路径为绝对路径且与本地实际一致", weight=2),
        Rubric(id="rb_c3t02_2", task_id="c3_t02", criterion="工具在客户端可见且可调用",
               description="客户端里能看到工具清单，并成功调用一次",
               required_evidence=["runtime"],
               pass_condition="贴出工具清单（或 tools/list 输出）与一次调用的返回文本", weight=2),
        # T03
        Rubric(id="rb_c3t03_1", evaluation_role="theory", task_id="c3_t03", criterion="能说清 MCP 的三类能力",
               description="正确区分 tools / resources / prompts，并指出前作用了哪些",
               required_evidence=["description"],
               pass_condition="三类能力的区别说得准确，且指明前作对外暴露的能力", weight=1),
        Rubric(id="rb_c3t03_2", evaluation_role="theory", task_id="c3_t03", criterion="能说清要解决的真实痛点",
               description="讲的是「跨会话遗忘项目上下文」这类具体问题，而不是空泛表述",
               required_evidence=["description"],
               pass_condition="痛点具体、能对应到一次真实的使用场景", weight=2),
        # T04
        Rubric(id="rb_c3t04_1", task_id="c3_t04", criterion="数据结构覆盖必要字段与状态",
               description="包含内容/类型/状态/时间戳字段，状态之间有明确的合法迁移关系",
               required_evidence=["code"],
               pass_condition="字段齐全；存在状态迁移校验逻辑，非法迁移有明确处理", weight=2),
        Rubric(id="rb_c3t04_2", task_id="c3_t04", criterion="数据真的落库（可查证）",
               description="写入的记录能从数据库查出来",
               required_evidence=["runtime"],
               pass_condition="贴出 SELECT 查询输出，能看到刚写入的记录与其字段值", weight=2),
        Rubric(id="rb_c3t04_3", task_id="c3_t04", criterion="建表与迁移可重复执行",
               description="初始化脚本幂等，重复执行不报错",
               required_evidence=["code"],
               pass_condition="连续执行两次初始化都不报错（代码可看出幂等写法）", weight=1),
        # T05
        Rubric(id="rb_c3t05_1", task_id="c3_t05", criterion="能区分至少 4 种记忆类型",
               description="不同类型的一句话被正确区分",
               required_evidence=["code", "runtime"],
               pass_condition="贴出的分类结果里，至少 4 种类型被正确区分", weight=2),
        Rubric(id="rb_c3t05_2", task_id="c3_t05", criterion="置信度机制存在且可见",
               description="有置信度计算，输出里能看到具体数值",
               required_evidence=["code", "runtime"],
               pass_condition="代码里有置信度计算；运行输出带置信度数值", weight=2),
        Rubric(id="rb_c3t05_3", task_id="c3_t05", criterion="模糊输入不会被强行定论",
               description="模糊表达被标记为需人工确认，而不是落库为确定结论",
               required_evidence=["runtime"],
               pass_condition="贴出的结果里，模糊语句被标为需确认（含触发的原因/信号）", weight=2),
        # T06
        Rubric(id="rb_c3t06_1", task_id="c3_t06", criterion="工具数量与覆盖度达标",
               description="至少 4 个工具，覆盖记录/查询/更新状态/恢复上下文",
               required_evidence=["code", "runtime"],
               pass_condition="工具数 ≥4，且四类能力都有对应工具", weight=2),
        Rubric(id="rb_c3t06_2", task_id="c3_t06", criterion="工具说明清晰可用",
               description="每个工具有明确的用途说明，能据以判断何时调用",
               required_evidence=["code"],
               pass_condition="每个工具的说明写明「做什么 + 何时用」，不是空描述", weight=2),
        Rubric(id="rb_c3t06_3", task_id="c3_t06", criterion="AI 能正确选中工具",
               description="在自然对话中 AI 选对了工具",
               required_evidence=["runtime"],
               pass_condition="贴出一次对话记录，能看出 AI 选中了恰当的工具", weight=1),
        # T07
        Rubric(id="rb_c3t07_1", task_id="c3_t07", criterion="测试可重复运行",
               description="连续两次运行测试都通过，不受上次运行残留数据影响",
               required_evidence=["runtime"],
               pass_condition="贴出两次运行测试的输出，结果一致且都通过", weight=2),
        Rubric(id="rb_c3t07_2", task_id="c3_t07", criterion="测试覆盖核心逻辑",
               description="覆盖分类、状态迁移、存储读写三类",
               required_evidence=["code"],
               pass_condition="测试文件里三类逻辑都有对应用例", weight=2),
        Rubric(id="rb_c3t07_3", task_id="c3_t07", criterion="README 含完整运行说明",
               description="他人照做能跑起来",
               required_evidence=["code"],
               pass_condition="安装/配置/启动/测试四步齐全，命令可直接复制执行", weight=1),
    ]

    return Project(
        id="project_mcp_build",
        title="做出你的第一个 MCP Server",
        description="从课程提供的最小骨架出发，用 Python 官方 SDK 做出一个能跨会话记住「决定 / 承诺 / 问题」的 MCP 服务，"
                    "并把它接进你自己的 AI 客户端。",
        stages=[stage1, stage2],
        tasks=[task_t01, task_t02, task_t03, task_t04, task_t05, task_t06, task_t07],
        rubrics=rubrics,
        resume_intro="用 Python 与官方 MCP SDK 实现一个跨会话的项目记忆服务：把对话中的决定、承诺、问题结构化为可检索记录，"
                     "经 SQLite 持久化后暴露为一组 MCP 工具，供 AI 客户端在后续会话中调用。",
        resume_role="独立开发",
        resume_tech=["Python", "MCP（Model Context Protocol）", "官方 mcp SDK", "SQLite",
                     "JSON-RPC", "stdio", "单元测试"],
        resume_metrics=["暴露 4 个以上 MCP 工具，覆盖记录/查询/状态更新/上下文恢复"],
    )


# ---------------------------------------------------------------------------
# 项目二：把自己的工具当产品测试与迭代
# ---------------------------------------------------------------------------
def build_project_mcp_test() -> Project:
    stage3 = Stage(
        id="c3_stage3", title="③ 真实使用测试", order=1,
        objective="把它当日常工具用起来（跨至少两个自然日），设计测试用例并产出测试报告",
        tasks=["c3_t08", "c3_t09"],
    )
    stage4 = Stage(
        id="c3_stage4", title="④ 提 Issue / 产品反馈", order=2,
        objective="把测试中发现的问题真的提成 GitHub Issue（含设计合理性反馈）",
        tasks=["c3_t10"],
    )
    stage5 = Stage(
        id="c3_stage5", title="⑤ 修复与回归", order=3,
        objective="自己定位、修改、补测试、跑通，并交付最终版与项目复盘",
        tasks=["c3_t11", "c3_t12"],
    )

    # ---- T08 装进真实工作流 ----
    task_t08 = Task(
        id="c3_t08", title="把它装进你的真实工作流", stage_id="c3_stage3", order=1,
        objective="把这个 MCP 当日常工具用起来，跨至少两个自然日，至少产生 5 条记忆记录、完成至少 1 次跨会话的上下文恢复，"
                  "并如实记录用起来不顺手的地方。",
        steps=[
            "把它接到你每天真的会用的 AI 客户端里（不是演示用的临时窗口）",
            "在真实任务里用它记录决定、承诺与问题（至少 5 条）",
            "关掉会话、第二天重新开始，调用一次上下文恢复，把返回内容留下",
            "每隔一段时间导出一次数据库，留下时间跨度证据",
        ],
        evidence_required="none",
        rubric_ids=["rb_c3t08_1", "rb_c3t08_2", "rb_c3t08_3"],
        skill=SkillKey.project_dev,
        chunk_key="课程03 > T08 装进真实工作流",
        resume_points=[
            ResumePoint(point="用数据库导出与时间戳作为「真实使用过」的客观证据",
                        purpose="避免测试结论无法核对",
                        result="让使用过程可审计、可复现", kind="engineering"),
        ],
    )

    # ---- T09 测试用例与报告 ----
    task_t09 = Task(
        id="c3_t09", title="设计测试用例并产出测试报告", stage_id="c3_stage3", order=2,
        objective="设计至少 5 条测试用例并逐条执行，把结果写进仓库根目录的 TEST_REPORT.md；"
                  "四类场景（正常路径 / 异常路径 / 跨会话 / 模糊语言）都要覆盖，「实际结果」必须是具体文本。",
        steps=[
            "按四类场景设计用例：正常路径、异常路径、跨会话、模糊语言",
            "逐条执行，如实记录预期与实际（报错原文、工具返回原文、数据库输出）",
            "把结果写进仓库根目录 TEST_REPORT.md（模板见课程素材）",
            "补一节「本次没覆盖到什么」——如实写比假装完整更专业",
        ],
        evidence_required="none",
        rubric_ids=["rb_c3t09_1", "rb_c3t09_2", "rb_c3t09_3"],
        skill=SkillKey.debug,
        chunk_key="课程03 > T09 测试用例与报告",
        code_context=CodeContext(
            keywords=["test_report", "测试", "expected", "actual", "case"],
            likelyFiles=["test_report", "test-report", "report"],
            searchPatterns=["TEST_REPORT", "实际结果", "预期结果"],
        ),
        resume_points=[
            ResumePoint(point="设计 5 条以上测试用例，覆盖正常/异常/跨会话/模糊语言四类场景",
                        purpose="避免只测顺利路径漏掉真实问题",
                        result="提升了问题发现率", kind="engineering"),
        ],
    )

    # ---- T10 提 Issue ----
    task_t10 = Task(
        id="c3_t10", title="把发现的问题写成 GitHub Issue", stage_id="c3_stage4", order=1,
        objective="把测试中发现的问题真的提成 GitHub Issue（不是只写在报告里）：标题 + 复现步骤 + 预期与实际对比；"
                  "也欢迎提「产品反馈」型 Issue，指出设计不合理的地方。",
        steps=[
            "在仓库 Issues 里新建 Issue（绿色 New issue 按钮）",
            "标题写清「什么坏了 / 哪里不合理」；正文写复现步骤与预期-实际对比",
            "报错原文整段贴上去，不要只写「报错了」",
            "给 Issue 编号记下来——测试报告与后续修复都要引用它",
        ],
        evidence_required="url",
        rubric_ids=["rb_c3t10_1", "rb_c3t10_2", "rb_c3t10_3"],
        skill=SkillKey.git,
        chunk_key="课程03 > T10 提 Issue",
    )

    # ---- T11 修复与回归 ----
    task_t11 = Task(
        id="c3_t11", title="定位、修复、加回归测试", stage_id="c3_stage5", order=1,
        objective="针对自己提的 Issue 完成一次完整闭环：定位原因 → 改代码 → 补测试 → 跑通 → 提交时引用 Issue 编号。",
        steps=[
            "复现问题，缩小范围，写清根因（不是「改了就好了」）",
            "改代码，并在 commit 信息里引用 Issue 编号",
            "补一个能防回归的测试（以后这个问题再出现会被测试拦住）",
            "跑全部测试，确认新问题修好且没有引入新问题",
        ],
        evidence_required="code+test",
        rubric_ids=["rb_c3t11_1", "rb_c3t11_2", "rb_c3t11_3"],
        skill=SkillKey.debug,
        chunk_key="课程03 > T11 修复与回归",
        code_context=CodeContext(
            keywords=["fix", "issue", "regression", "test"],
            likelyFiles=["test_", "capture", "storage"],
            searchPatterns=["def test_", "#\\d+", "fixed"],
        ),
        resume_points=[
            ResumePoint(point="提交结构化 Issue 并完成修复与回归测试（引用 Issue 编号形成闭环）",
                        purpose="让「发现的问题」都能被验证修好",
                        result="保障了修复不引入新的回归问题", kind="stability"),
        ],
        interview_questions=[
            InterviewQuestion(
                id="iq_c3t11_1",
                question="面试官问：你说修好了这个问题，凭什么让人相信没有引入新问题？",
                answer_anchor="两点：一是补了针对该问题的回归测试（问题再出现时测试会失败），二是跑全量测试并给出通过结果；"
                              "如果接了 CI，GitHub Actions 的结论就是第三方可验证的证据。",
                hint="从「怎么证明」这个角度回答：不是我说好了，而是有测试和 CI 能证明。",
                type="explain",
            ),
            InterviewQuestion(
                id="iq_c3t11_2",
                question="变式题：如果这个问题只在跨会话时出现，你会怎么定位？",
                answer_anchor="先确认状态是否真的持久化了（查数据库表里的记录与时间戳）→ 再看读取路径是否按预期查询（是否受状态过滤影响）→ "
                              "如果是缓存或内存态导致，检查是否有进程内状态没落到库里。",
                hint="跨会话问题的核心是「哪些东西只在内存里、哪些真的落库了」。",
                type="transfer",
            ),
        ],
    )

    # ---- T12 交付与复盘 ----
    task_t12 = Task(
        id="c3_t12", title="交付最终版与项目复盘", stage_id="c3_stage5", order=2,
        objective="更新 README（运行说明 + 版本变更），写一段能进简历的项目经历，并复盘「我改了什么、为什么」。",
        steps=[
            "更新 README：安装/配置/运行/测试四步，外加一节变更记录",
            "写一段 100~200 字的项目经历描述（只写交付了什么，不写学了什么）",
            "复盘：具体问题 → 定位过程 → 修复手段 → 验证结果",
        ],
        evidence_required="code",
        rubric_ids=["rb_c3t12_1", "rb_c3t12_2"],
        skill=SkillKey.project_dev,
        chunk_key="课程03 > T12 交付与复盘",
    )

    rubrics = [
        # T08
        Rubric(id="rb_c3t08_1", evaluation_role="reflection", task_id="c3_t08", criterion="确实持续使用过（跨 ≥2 个自然日）",
               description="数据库导出显示至少 5 条记录，且创建时间跨至少两个自然日",
               required_evidence=["runtime"],
               pass_condition="贴出数据库导出：记录数 ≥5，最早与最晚记录日期不同", weight=2),
        Rubric(id="rb_c3t08_2", task_id="c3_t08", criterion="跨会话恢复真的发生过",
               description="至少完成一次跨会话的上下文恢复",
               required_evidence=["runtime"],
               pass_condition="贴出一次恢复类工具的真实返回内容", weight=2),
        Rubric(id="rb_c3t08_3", evaluation_role="reflection", task_id="c3_t08", criterion="记录了真实体感",
               description="写出至少 1 处用起来不顺手的地方，具体到操作",
               required_evidence=["description"],
               pass_condition="说的是具体操作场景，不是「感觉还行」这类空话", weight=1),
        # T09
        Rubric(id="rb_c3t09_1", task_id="c3_t09", criterion="报告结构完整、覆盖四类场景",
               description="仓库根目录存在测试报告，用例 ≥5 条，四类场景齐全",
               required_evidence=["report"],
               pass_condition="报告在仓库根目录，≥5 条用例，正常/异常/跨会话/模糊语言都有", weight=2),
        Rubric(id="rb_c3t09_2", task_id="c3_t09", criterion="「实际结果」具体可核对",
               description="实际结果栏是具体文本（报错原文/工具返回/数据库输出），不是笼统结论",
               required_evidence=["report"],
               pass_condition="多数用例的实际结果含可核对的原文；只写「正常/OK」的不计入", weight=2),
        Rubric(id="rb_c3t09_3", task_id="c3_t09", criterion="测试边界有交代",
               description="说明本次没覆盖到什么、为什么",
               required_evidence=["report"],
               pass_condition="有一节如实说明未覆盖范围，而不是留白或声称「全覆盖」", weight=1),
        # T10
        Rubric(id="rb_c3t10_1", task_id="c3_t10", criterion="Issue 真的创建了",
               description="仓库 Issues 里有实际创建的 Issue",
               required_evidence=["issue"],
               pass_condition="给出可访问的 Issue 编号或链接，且内容与测试报告对应", weight=2),
        Rubric(id="rb_c3t10_2", task_id="c3_t10", criterion="含可复现步骤与预期/实际对比",
               description="他人照做能复现，且写明了预期与实际",
               required_evidence=["issue"],
               pass_condition="有编号步骤；有预期与实际两段；报错原文被完整贴上", weight=2),
        Rubric(id="rb_c3t10_3", evaluation_role="reflection", task_id="c3_t10", criterion="不止步于 Bug",
               description="至少一条涉及设计合理性的反馈（或说明为何没有）",
               required_evidence=["issue"],
               pass_condition="有产品反馈型 Issue，或在报告里说明「只发现 Bug、未发现设计问题」的理由", weight=1),
        # T11
        Rubric(id="rb_c3t11_1", task_id="c3_t11", criterion="有针对性改动",
               description="提交记录引用 Issue 编号，改动与该问题对应",
               required_evidence=["code"],
               pass_condition="commit 信息里能看到 Issue 编号，改动的文件与问题范围相符", weight=2),
        Rubric(id="rb_c3t11_2", task_id="c3_t11", criterion="补了防回归的测试",
               description="新增或修改了覆盖该问题的测试",
               required_evidence=["code"],
               pass_condition="能指出新增的测试用例，且它与修复的问题直接相关", weight=2),
        Rubric(id="rb_c3t11_3", task_id="c3_t11", criterion="回归通过",
               description="修复后全部测试通过，没有引入新问题",
               required_evidence=["ci", "runtime"],
               pass_condition="GitHub Actions 结论为成功；没有 CI 时给出完整本地测试输出", weight=2),
        # T12
        Rubric(id="rb_c3t12_1", task_id="c3_t12", criterion="README 可复现",
               description="安装/配置/运行/测试四步齐全，他人照做能跑起来",
               required_evidence=["code"],
               pass_condition="四步齐全，命令可直接复制执行", weight=1),
        Rubric(id="rb_c3t12_2", evaluation_role="theory", task_id="c3_t12", criterion="能讲清「我改了什么、为什么」",
               description="复盘含具体问题、定位过程、修复手段与验证结果",
               required_evidence=["description"],
               pass_condition="四段齐全且具体，能看出真实的排查过程", weight=2),
    ]

    return Project(
        id="project_mcp_test",
        title="把自己的工具当产品测试与迭代",
        description="把它当真实产品用起来：设计测试用例、产出测试报告、把问题提成 GitHub Issue，"
                    "然后自己定位、修复、补回归测试，走完一次完整的问题闭环。",
        stages=[stage3, stage4, stage5],
        tasks=[task_t08, task_t09, task_t10, task_t11, task_t12],
        rubrics=rubrics,
        resume_intro="作为该 MCP 服务的第一位真实用户，在跨会话的真实工作场景中持续使用并设计测试用例，"
                     "发现分类与状态管理问题后提交 Issue、完成代码修复与回归验证。",
        resume_role="独立开发 / Beta 测试",
        resume_tech=["Python", "MCP", "SQLite", "测试用例设计", "GitHub Issues",
                     "GitHub Actions", "Git", "回归测试"],
        resume_metrics=["测试用例覆盖 4 类场景（正常/异常/跨会话/模糊语言）",
                        "完成「发现问题 → 提 Issue → 修复 → 回归」完整闭环"],
    )
