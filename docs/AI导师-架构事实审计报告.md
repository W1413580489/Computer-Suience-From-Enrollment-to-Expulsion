# 《AI 导师项目架构事实审计报告》

> 审计对象：`tralis/xkz-agent/`（线上域名 jnuxky.xyz）
> 审计日期：2026-09-29
> 审计方式：仅阅读仓库内实际存在的代码 / 配置 / 数据库 DDL / Prompt / 测试 / 部署文件；**不修改任何代码**。
> 证据基准：仓库工作副本 `d:\Assistant\tralis\xkz-agent\`（下文路径均为相对仓库根目录）。

---

## 0. 审计方法与状态定义

### 0.1 证据规则

1. 只承认「仓库里能跑/能读到的代码」为证据。`README.md`、`docs/*.md`、`ai_engine/PROJECT_OVERVIEW.md`、`ai_engine/BUG_REPORT.md`、代码注释中的自我描述**一律不作为"已实现"的依据**，仅在下文明确标注为「文档声称」时引用。
2. 每条结论后附（文件路径 : 行号 / 类名 / 函数名 / 接口名 / 配置项）。
3. 全文区分 **【事实】**（代码里确实有什么）与 **【判断】**（这说明了什么）。

### 0.2 五态定义（全文统一使用）

| 标记 | 含义 |
|---|---|
| ✅ 已实现 | 有完整代码路径，且被主流程调用 |
| 🟡 部分实现 | 有代码，但能力不完整 / 只在局部路径生效 / 有硬边界 |
| 🔴 代码存在但未接入主流程 | 代码/模型/枚举存在，但主流程不会走到，或产出被丢弃 |
| ⏳ 规划中但尚未实现 | 有数据结构预留位/注释标记，无执行逻辑 |
| ❌ 完全不存在 | 全仓库检索不到任何相关实现 |

### 0.3 一个必须先讲清的架构前提

**【事实】** 本仓库不是一个单体应用，而是**两个互相独立、不共享进程与代码的 FastAPI 应用**：

| 应用 | 入口 | 端口 | 职责 |
|---|---|---|---|
| 校园问答站 | `backend/main.py`（715 行） | 8000 | 校园 RAG 问答（`/api/ask` SSE）+ 静态站 + SEO 注入 |
| AI 项目导师引擎 | `ai_engine/app.py`（767 行） | 8099 | `/api/ai/*` 全部辅导与验收能力 |

- 端口证据：`ai_engine/app.py:870` `uvicorn.run("app:app", host="0.0.0.0", port=8099, reload=False)`；`xkz-agent.conf:31` `proxy_pass http://127.0.0.1:8000;`。
- 二者**没有任何 Python 层互相 import**：`ai_engine/` 是独立包（`ai_engine/__init__.py` 仅 1 行），`backend/` 不引用 `ai_engine`。
- 两套 RAG 是**不同的实现**：`backend/retrieval.py` 是完整混合检索（BM25+向量+RRF+重排）；`ai_engine` 侧只有 `section_path` 子串匹配（见 §6）。**这是本报告最重要的架构事实之一。**

**【事实·仓库与线上不一致】** 仓库内的 Nginx 配置 `xkz-agent.conf` **只包含** `location /` → 127.0.0.1:8000，**不含任何 `/api/ai/` 反代规则**。但 `ai_engine/BUG_REPORT.md:32` 声称「Nginx `/api/ai/` 反代到 8099 已配置」。前端在开发态靠 `frontend/vite.config.ts:15-22` 的 Vite proxy（`/api/ai`→8099、`/api`→8099）访问引擎。

**【判断】** 若不做 `/api/ai/` 反代，生产环境的前端请求会落到 `backend/main.py`，而该文件**没有** `/api/ai/*` 路由，会被 `@app.get("/{full_path:path}")`（`backend/main.py:790`）的 SPA fallback 处理并返回 404/首页。因此 AI 导师功能在生产是否可用，**完全依赖仓库之外（服务器上）的 Nginx 配置**，仓库不可自证。这一点在交接给另一个 AI 时必须显式说明。

---

## 1. 项目总体架构

### 1.1 真实数据流与控制流

**【事实】** 以 AI 导师（本项目重点）为准，实际数据流如下（与用户模板给的链路不同，按代码修正）：

```
用户输入
 → Vue 前端 TeachView.vue（fetch /api/ai/teach，BYOK 携带 api_key/base_url/model）
 → [Nginx（仓库外配置）] → ai_engine/app.py: teach()
   → 会话恢复: store.get_session(skey)   skey = f"{session_id}:{task_id}"   (SQLite sessions 表)
   → [可选] vision.analyze_images()  读图（fail-open，图片不落盘）
   → 行为路由: prompts.route_behavior()  确定性关键词路由 → decompose/advance/debug
   → 上下文组装: context_builder.build_context()
        → course_data.get_task/get_project/get_stage/get_rubrics   （硬编码 Python 数据）
        → course_data.chunks_by_section_path(task.chunk_key)       （chunks.jsonl 子串匹配，非向量检索）
        → hint.calculate_hint_level(attempt_count)
   → [可选] code_evidence.build_code_evidence(repo_url)            （GitHub REST API 只读拉取）
   → 组装 messages（system + 最近 12 轮历史 + 本轮输入）
   → llm_client.LLMClient.teach() → httpx POST {base_url}/chat/completions
   → response_validator.validate() 不通过则「重生成」最多 2 次
   → store.save_session() + logs.log_event()
 → 返回 JSON（message / next_action / hint / behavior / evidence / visual / debug_state / mode_advice）

验收链（独立入口）: POST /api/ai/review
 → build_code_evidence → collect_evidence → snapshot_evidence(sha256)
 → 失败熔断查询 → 成功幂等缓存查询
 → evidence_precheck（硬约束）→ ci_direct_verdict（CI 直判）
 → llm_client.review()（仅逐条 criteria）→ compute_evaluation()（后端算 score/status）
 → store.save_review_result() → 返回 evaluation
```

**没有出现的环节**：Tool Calling、Agent 循环、Subagent、Sandbox 执行、长期记忆检索、Learner Model 更新。

### 1.2 技术栈清单（逐项给证据）

| 项 | 事实 | 证据 |
|---|---|---|
| 前端 | Vue 3 + Pinia + Vue Router + Vite + TypeScript | `frontend/src/main.ts`、`frontend/src/router/index.ts`、`frontend/vite.config.ts`、`frontend/src/stores/*.ts` |
| 后端（校园站） | FastAPI + httpx + SSE | `backend/main.py`（`from fastapi import FastAPI`，`_sse()`，`StreamingResponse`） |
| 后端（导师引擎） | FastAPI + Pydantic v2 + httpx + 标准库 sqlite3 | `ai_engine/app.py:38`、`ai_engine/schemas.py`、`ai_engine/store.py:19` |
| 数据库 | SQLite（WAL），单库 `data/engine.db` | `ai_engine/store.py:78-83`（`PRAGMA journal_mode=WAL`）；`default_db_path()` 支持 `XKZ_DB_PATH` |
| 缓存 | 进程内 dict 三级缓存：代码证据 TTL 300s、视觉 TTL 1800s、检索 query 缓存 | `ai_engine/code_evidence.py:56` `CACHE_TTL = 300`；`ai_engine/vision.py` `CACHE_TTL=1800`；`backend/retrieval.py` `search()` 内 1 小时 query 缓存 |
| 消息队列 | ❌ 完全不存在 | 全仓库无 celery / redis / kafka / rabbitmq / zmq / nats（Grep `redis|celery|kafka|rabbitmq|pika|zmq|nats|aioredis|boto3` 于 `*.py` = 0 命中） |
| LLM Provider | OpenAI 兼容 `/chat/completions`；默认 DeepSeek（`https://api.deepseek.com`，`deepseek-flash`）；BYOK 可传 base_url 覆盖任意兼容服务商 | `ai_engine/llm_client.py:27-28`、`llm_client.py:161-164`、`llm_client.py:191-196` |
| Embedding | **仅存在于 `backend/`**：`BAAI/bge-small-zh-v1.5`（512 维，FP32） | `backend/embedding.py` `EmbeddingService`；`backend/config.py` |
| Vector DB | ❌ 完全不存在（无 faiss/chroma/milvus/qdrant/pgvector） | Grep 上述库名 = 0 命中；向量以 `data/embedding_cache.npy` 全量内存驻留 |
| RAG | 两套：`backend/retrieval.py` 完整混合检索；`ai_engine` 仅 `section_path` 子串匹配 | 见 §6 |
| Agent Framework | ❌ 完全不存在（无 langchain / langgraph / crewai / autogen / llama_index） | Grep = 0 命中；`ai_engine/app.py` 手写过程式编排 |
| MCP | ❌ 引擎侧不存在。MCP 只作为**课程 03 的教学内容**出现 | `ai_engine/course03_data.py:9,58`、`docs/课程03-素材/starter/server.py:12`（学生要写的 server 模板）；引擎自身无 MCP client |
| 文件存储 | 本地磁盘（JSONL 日志、`chunks.jsonl`、`engine.db`、`embedding_cache.npy`）；**不存用户上传图片** | `ai_engine/logs.py:22-23`；`ai_engine/schemas.py:181-190` `VisualImage` 生命周期=请求级 |
| GitHub 集成 | GitHub REST API 只读（元信息 / git trees / contents / actions / issues），可选 `GITHUB_TOKEN` | `ai_engine/code_evidence.py`（`GITHUB_API`、`_repo_default_branch`、`_fetch_tree`、`_fetch_file_content`、`fetch_ci_evidence`、`fetch_issues_evidence`） |
| Sandbox / Code Execution | ❌ 完全不存在 | Grep `subprocess|Popen|os.system|exec\(` 于 `ai_engine/*.py`：仅命中 `docker` 字符串（RUN_CMD_PATTERN 关键词）与 SQLite `_exec`，无任何执行调用 |
| 部署 | Nginx（80→443 跳转；443→127.0.0.1:8000，SSE 友好）+ pm2 托管（据 `BUG_REPORT.md`，仓库内无 pm2 配置文件可验证） | `xkz-agent.conf`；仓库内**无** `ecosystem.config.js` / `Dockerfile` / CI 配置 |
| 主要第三方服务 | DeepSeek（默认 LLM）、GitHub REST API | `llm_client.py:27`、`code_evidence.py:23` |
| 主要第三方服务（校园站） | 多 Provider 预设：deepseek / qwen / kimi / zhipu | `backend/config.py` providers 配置 |

---

## 2. Repository 目录结构

**【事实】** 全仓库 `.py/.vue/.ts` 文件清单（已排除 node_modules / dist / __pycache__，行数为实测）：

```
tralis/xkz-agent/
├── README.md                     # 不与代码强绑定，本报告不采信其功能声明
├── xkz-agent.conf                # Nginx 站点配置（见 §1.3 不一致说明）
├── .gitignore
│
├── ai_engine/                    # ★ AI 项目导师引擎（独立 FastAPI，:8099）
│   ├── app.py            (767)   # 引擎主入口：全部 HTTP 端点 + teach/review 编排
│   ├── schemas.py        (332)   # Pydantic v2 全部数据模型
│   ├── review.py         (369)   # 验收链：证据收集/预检/CI 直判/聚合/system prompt
│   ├── code_evidence.py  (516)   # GitHub 证据管线 + Task-aware 代码检索 + CI + Issues
│   ├── llm_client.py     (289)   # LLM 调用/JSON 容错/语义校验/重生成/纯文本兜底
│   ├── prompts.py        (187)   # CORE_POLICY + 模式 Prompt + 行为路由 + system prompt 组装
│   ├── store.py          (310)   # SQLite：sessions/review_results/review_failures/evidence
│   ├── vision.py         (344)   # 运行截图视觉证据（白名单 + fail-open，不落盘）
│   ├── career.py         (159)   # 简历文本生成（零 LLM，模板+数据填充）
│   ├── course_data.py    (761)   # 课程/项目/阶段/任务/Rubric 硬编码数据 + 检索封装
│   ├── course03_data.py  (537)   # 课程 03（MCP 客户端/服务端）项目数据
│   ├── context_builder.py (57)   # 教学上下文组装（依赖 course_data + hint）
│   ├── response_validator.py (78)# AI 输出质量校验（关键词规则）
│   ├── hint.py            (42)   # Hint Level 0-5 状态推导
│   ├── logs.py           (106)   # JSONL 事件日志 + stats 聚合
│   ├── requirements.txt
│   ├── testpage.html             # 独立测试页
│   ├── PROJECT_OVERVIEW.md / BUG_REPORT.md   # 自述文档（不采信为证据）
│   ├── _test_phase1..8.py / _test_evidence.py / _test_v11_fix.py / _check_py311.py
│   └── __init__.py         (1)
│
├── backend/                      # 校园问答站（独立 FastAPI，:8000）
│   ├── main.py           (715)   # 校园问答 API（/api/ask SSE）+ SEO/SPA 注入 + JSON-LD
│   ├── retrieval.py      (435)   # 完整混合检索：5 路召回 + RRF 融合 + 意图加权 + 重排
│   ├── embedding.py      (135)   # bge-small-zh-v1.5 嵌入 + bge-reranker-base（默认关闭）
│   ├── config.py         (118)   # 全部环境变量配置 + 校园问答 System Prompt
│   └── ratelimit.py       (63)   # 限流（30/日、5/分）
│
├── scripts/
│   ├── chunker.py        (248)   # 知识库分块器 v3（结构化语义分块）
│   ├── retrieve.py       (161)   # 检索调试 CLI
│   ├── build_nav_config.py (92)
│   └── indexnow_push.py   (75)   # IndexNow 推送
│
├── data/
│   ├── chunks.jsonl              # RAG 语料（两套检索共用）
│   ├── docs_manifest.csv         # 26 篇文档元数据（id/标题/类别/URL/子类别）
│   ├── engine.db                 # SQLite（会话/评审缓存/熔断/证据）
│   ├── embedding_cache.npy       # 向量缓存（仅 backend 用）
│   ├── nav_config.json / changelog.json / hot_questions.json / glossary.json
│   ├── raw/                      # 原始 Markdown 源
│   └── logs/session_events.jsonl # 结构化事件日志
│
├── docs/
│   ├── 课程03-完整设计.md / 上下文持久化与JSON容错-方案设计.md / 2026年9月进度汇总.md
│   └── 课程03-素材/（starter/server.py、TEST_REPORT-模板.md、Issue-模板…、学生版-客户端接入指南.md）
│
└── frontend/                     # Vue 3 + Vite + TS
    ├── vite.config.ts     (24)   # dev proxy：/api/ai 与 /api → 127.0.0.1:8099
    ├── public/                   # SEO 文件（robots.txt/sitemap.xml/站长验证/IndexNow key）
    └── src/
        ├── router/index.ts (66)  # 16 个路由
        ├── stores/               # chatStore/settingsStore/userStore/themeStore/achievementStore/navStore/uiStore
        ├── views/                # TeachView(1891) LoginView(1280) ThanksView(664) QuestView(616) CalendarView(474)
        ├── components/           # hud/ chat/ home/ settings/ roadmap/ nav/ quest/ login/ common/ list/
        ├── composables/          # useBgImage/useMarkdown/useAiMarkdown/useQuest/useViewport
        └── data/                 # achievements/questData/roadmapData/gradeContent（静态内容）
```

**关键目录依赖关系**

| 目录 | 作用 | 依赖 | 被谁依赖 |
|---|---|---|---|
| `ai_engine/` | AI 导师全部能力 | `data/*`（只读语料 + SQLite）、GitHub API、LLM API | 前端 TeachView（经 Nginx/代理） |
| `backend/` | 校园问答 + 站点宿主 | `data/chunks.jsonl`、`embedding_cache.npy`、LLM API | 前端全部页面 |
| `scripts/` | 离线数据构建 | `data/raw/*.md` | 人工执行，不被运行时调用 |
| `data/` | 语料 + 持久化 | — | 两套后端 |
| `frontend/` | UI | 两个后端 API | 用户 |

**【判断】** 目录结构上，`ai_engine/` 是一个**自洽的、可独立运行的垂直功能模块**，与校园问答站零耦合。这既是优点（可单独抽出），也是缺点（两套 RAG、两套配置、两套日志，见 §19）。

---

## 3. 系统模块地图

**【事实】** 按用户给定清单逐一核查（状态 + 证据）：

| 模块 | 状态 | 证据 / 说明 |
|---|---|---|
| 用户 / 身份 | 🟡 部分实现 | 导师侧无账号体系：`session_id` 由前端随机生成（`TeachView.vue:395` `'s_' + Math.random()...`），服务端只当字符串用（`app.py:244`）。校园站有 `POST /api/verify`（`backend/main.py:163`）用于学生身份验证，但与导师引擎不共享。 |
| Session | ✅ 已实现 | `ai_engine/store.py` `sessions` 表 + `get_session/save_session/session_history`；会话键 `f"{session_id}:{task_id}"`（`app.py:245`）。 |
| Chat | ✅ 已实现 | `POST /api/ai/teach`；历史存 `sessions.history_json`；`GET /api/ai/session_history` 支持刷新后恢复（`app.py:479`）。 |
| Agent | 🟡 部分实现 | **无 Agent 框架**。只有过程式编排函数 `teach()`/`review()`（`app.py:221/494`）。 |
| Orchestrator | 🟡 部分实现 | 编排逻辑硬编码在 `app.py` 的两个 handler 内，无独立 orchestrator 类、无状态机引擎。 |
| Tool | ❌ 完全不存在 | 无 Tool Registry、无 Tool Schema、LLM 请求体无 `tools` 字段（`llm_client.py:177-185` 仅 model/messages/temperature/max_tokens/response_format）。GitHub 调用是普通 Python 函数，不暴露给模型。 |
| RAG | 🟡（导师侧）/ ✅（校园侧） | 导师侧 `course_data.chunks_by_section_path()` 子串匹配；校园侧 `backend/retrieval.py` 完整混合检索。 |
| Knowledge Base | ✅ 已实现 | `data/chunks.jsonl` + `data/docs_manifest.csv`（26 篇）；无多租户隔离、无版本管理。 |
| Memory | 🟡 部分实现 | 仅对话历史 + 调试状态；无长期记忆、无摘要（`store.py:202` `summary_json` 恒为 `None`）。 |
| Course | ✅ 已实现 | `course_data.py` + `course03_data.py` 硬编码 3 门课程。 |
| Learning Path | 🟡 部分实现 | 有 `Stage.order` / `Task.order` 与 `get_next_task()`（`course_data.py:776`）；无自适应路径、无先修依赖校验。 |
| Task | ✅ 已实现 | `schemas.Task`；实测 26 个任务定义（`course_data.py` 14 + `course03_data.py` 12）。 |
| Project | ✅ 已实现 | `schemas.Project`；4 个项目：`project_chatbot`、`project_agent`、`project_mcp_build`、`project_mcp_test`。 |
| GitHub | 🟡 部分实现 | 只读 REST API；默认分支；无 clone / 无索引 / 无增量。详见 §8。 |
| Code Analysis | 🟡 部分实现 | 仅「文件级选优 + LLM 阅读」（`rank_candidate_files` / `ai_relevance_filter`）；无 AST、无静态分析、无依赖图。 |
| Code Execution | ❌ 完全不存在 | 见 §9。 |
| Evaluation | ✅ 已实现 | `review.compute_evaluation()` 后端确定性聚合（`review.py:230`）。 |
| Rubric | ✅ 已实现 | `schemas.Rubric`；实测 81 条（`course_data.py` 49 + `course03_data.py` 32），含 `weight` / `required_evidence` / `pass_condition`。 |
| Progress | 🟡 部分实现 | 进度在前端 `localStorage['xkz_ai_student'].completed_tasks`（`TeachView.vue:1135-1136` 仅在 review PASS 时 push）；服务端只有日志聚合（`logs.compute_stats()`），**无 Progress 数据表**。 |
| Mastery | ❌ 完全不存在 | `schemas.SkillKey`（13 项）+ `Student.skills` 字段存在，但 `skills` 全仓库**只有初始化 `{}`，无任何写入/读取路径**（`TeachView.vue:395,1310` 初始化为空，`ai_engine` 侧不持久化）。 |
| Question / Quiz | 🟡 部分实现 | 有 `InterviewQuestion`（面试自检题）与 `GET /api/ai/interview`；**无练习题/测验/题库/自动判题**。 |
| Report | 🟡 部分实现 | 验收返回 `evaluation` + `next_step` 即"验收报告"；无独立报告生成/导出模块。课程 03 要求学生手写 `TEST_REPORT.md`，由 `review.extract_report_section()` 解析（`review.py:32`）。 |
| Resume | 🟡 部分实现 | `POST /api/career/text` + `career.py`（**零 LLM**，模板填充）。详见 §13。 |
| Interview | 🟡 部分实现 | `GET /api/ai/interview` 返回课程作者手写的题（`app.py:815` `"ai_generated": False`）；无追问、无自动评分。 |
| Logging | ✅ 已实现 | `ai_engine/logs.py` JSONL 事件日志（teach/review/feedback/vision 四类事件）。 |
| Monitoring | 🟡 部分实现 | `GET /api/ai/stats`（`logs.compute_stats()`）+ `GET /api/ai/health`；无指标上报、无告警、无 tracing。 |

---

## 4. Agent 架构

**【事实】**

- **Agent Framework**：❌ 无。全仓库无 langchain / langgraph / crewai / autogen / llama_index（Grep = 0 命中）。
- **入口**：`ai_engine/app.py:221` `async def teach()` 与 `app.py:494` `async def review()`。
- **任务规划**：不是模型规划，而是**确定性关键词路由** `prompts.route_behavior(user_input, sess)`（`prompts.py:113-131`）：
  1. 调试状态未收尾且未表达"已解决" → `debug`
  2. 命中 `DEBUG_SIGNALS`（约 30 个报错关键词，`prompts.py:104`）→ `debug`
  3. 会话无历史 → `decompose`
  4. 其余 → `advance`
  该行为决定注入哪段 `BEHAVIOR_PROMPTS`（`prompts.py:78-100`）。
- **Tool Calling**：❌ 不存在。LLM 只返回 JSON 文本；请求体无 `tools`/`tool_choice`（`llm_client.py:177-185`）。
- **上下文构建**：`context_builder.build_context()`（`context_builder.py:37`）——任务元数据 + 6 条以内语料 + hint level + 可选代码证据 + 调试进度。
- **多轮循环**：只有**一轮请求 + 最多 2 次"重生成"**（`app.py:353-375`，`MAX_RETRIES=2`，`llm_client.py:30`）。重生成是"输出质量不合格 → 让模型重写 JSON"，**不是** ReAct / 工具循环。
- **状态保存**：`store.save_session()`（`store.py:179`）——history / hint_level / debug_state / last_system_error / attempt_count。
- **多 Agent / Subagent / Handoff**：❌ 均不存在。
- **Workflow / State Machine**：🟡 唯一的状态机是 **Debugger 六段流程**（`schemas.DebugPhase`: symptom→evidence→narrow→verify→locate→explain→done；推进逻辑在 `app.py:128-143` `update_debugger_state()`）。它是**软状态机**：依赖模型返回的 `suspected_cause` 文本是否含"未确定/尚不/无法"来决定是否进入 `verify`（`app.py:137`），并非严格迁移表。
- **长任务 / 恢复执行**：❌ 无。请求-响应同步；无任务队列、无断点续跑。
- **Streaming**：❌ 导师引擎**不支持**流式（`llm_client.py:172` 注释明确"不流式，便于结构化校验"；`_call()` 用 `httpx.post` 非 stream）。流式只存在于校园站的 `/api/ask`（`backend/main.py:201`）。
- **Human-in-the-loop**：❌ 无审批/中断/接管机制。最接近的是"重生成"自动纠偏，属自动流程而非人工介入。
- **Prompt 位置**：
  - 通用铁律 + 模式 Prompt + 行为 Prompt + 行为路由：`ai_engine/prompts.py`
  - 验收专用 System Prompt：`ai_engine/review.py:330` `build_review_system_prompt()`
  - 代码检索二次筛选 Prompt：`ai_engine/code_evidence.py:433`
  - 视觉分析 Prompt：`ai_engine/vision.py`
  - 校园问答 Prompt + 意图 Prompt：`backend/config.py`
- **System Prompt 组织方式**：`build_system_prompt(ctx, mode)`（`prompts.py:134`）用 f-string 拼接 7 段：`CORE_POLICY` → 任务上下文 → 代码证据块 → 调试进度块 → 教学材料 → Hint 等级表 → 模式块 → 行为块 → 输出格式硬性要求。`app.py:323` 在其后再拼 `system_error_note()`（系统错误隔离声明）。
- **Tool Schema / Tool Registry**：❌ 不存在。

**【判断】** 这是"**单次 LLM 调用 + 结构化输出校验 + 确定性前后处理**"的架构，不是 Agent 架构。它的"智能"集中在**输入侧**（证据组装、行为路由、上下文裁剪）和**输出侧**（Pydantic 校验、语义校验、后端聚合、兜底），而**不是**在模型自主决策上。用 Agent 框架做横向对比时，应把本项目归类为 **"Deterministic Pipeline + LLM-as-a-Component"**，而非 Agentic System。

### 4.1 一处必须指出的设计-代码不一致

**【事实】**
- `prompts.py:66-68`（`MODE_PROMPTS["reviewer"]`）与 `prompts.py:179`（`build_system_prompt` 的 reviewer 分支）仍要求模型输出 `evaluation`、`score(0-100)`、`passed(bool)`。
- 但真正的验收入口 `/api/ai/review` 使用的是 `review.build_review_system_prompt()`，其输出契约明确写了"**不要输出总分 status/score**，你只负责逐条 criteria 与 next_step"（`review.py:426-434`）。
- `schemas.ReviewLLMOutput`（`schemas.py:316`）只含 `criteria` + `next_step`，**没有** `score`/`status` 字段；`AiResponse`（`schemas.py:332`）也没有 `score`/`passed` 字段。

**【判断】** `prompts.py` 的 reviewer 分支是**遗留路径**。它仍可被走到，因为：`app.py:231-233` 的 `/api/ai/teach` 接受 `mode="reviewer"`；而前端 `TeachView.vue:416` 的 `mode` 初值为 `'tutor'`，却会在 `TeachView.vue:1331` `mode.value = adv.mode` 被后端 `mode_advice` 改成 `'reviewer'`（`app.py:172` `compute_mode_advice` 返回 `mode="reviewer"`），此后 `TeachView.vue:890` 会把 `mode:'reviewer'` 发给 `/api/ai/teach`。
→ 结果：**走 teach 通道的"验收模式"会让模型输出 score/passed，但这些字段在 Pydantic 校验时被静默丢弃**，与 V2「LLM 不决定 score/status」的治理目标直接冲突。真正生效的验收只有 `/api/ai/review`。这属于 **🔴 代码存在但未接入（正确）主流程 + 设计不一致**。

---

## 5. LLM 与模型层

**【事实】**

- **模型**：`DEFAULT_MODEL = "deepseek-flash"`（`llm_client.py:28`，注释：2026-09 DeepSeek 将 V4 Flash/Pro 合并为 V4.1-Flash）。`/api/ai/config` 只暴露这一个模型（`app.py:191-194`）。
- **Provider 抽象**：**没有 provider 抽象层**。只有一个 `LLMClient` 类，本质是"OpenAI 兼容 HTTP 客户端"：`base_url` 可被 BYOK 覆盖（`llm_client.py:163`），因此"支持切换服务商"是**靠请求参数透传实现的间接能力**，而非多 Provider 适配器。
- **模型切换**：🟡 请求级：`TeachRequest.model` / `ReviewRequest.model` / `req.base_url` 可覆盖（`schemas.py:371,386`）。前端与导航「API 配置」共用 `xkz_settings_v1`（`app.py:197` `config_source`）。
- **不同模型负责不同任务**：❌ 不存在。行为级差异只体现在 `max_tokens`，不体现在模型。
- **Embedding**：导师引擎**不使用任何 embedding**。仅校园站使用 `BAAI/bge-small-zh-v1.5`（`backend/embedding.py`）。
- **Reranker**：🟡 存在但**默认关闭**：`backend/embedding.py` `RerankerService`（`BAAI/bge-reranker-base`），由 `XKZ_RERANK_ENABLED` 控制，默认 `"0"`（`backend/config.py`）。**导师引擎无 reranker。**
- **Token / Context 管理**：
  - 历史窗口：`history[-12:]`（`app.py:330`），全量历史来自 SQLite。
  - 字符预算裁剪：`_trim(messages, HISTORY_CHAR_LIMIT=6000)`（`llm_client.py:32,85`），**system message 永不裁剪**。
  - 行为级 `max_tokens`：`MAX_TOKENS_BY_BEHAVIOR = {decompose:3500, advance:1500, debug:2500}`（`llm_client.py:35-39`），兜底 `DEFAULT_TEACH_MAX_TOKENS=2048`，评审 `REVIEW_MAX_TOKENS=3000`（`llm_client.py:40-41`）。
  - 截断处理：`finish_reason == "length"` → **拒绝 repair 结果，加倍 max_tokens 重新完整生成**（`llm_client.py:233-244`、`284-289`）。
- **模型 fallback**：🟡 有两类，均非"换模型"：
  1. **JSON 模式降级**：HTTP 400 且响应含 `response_format` → 关闭 json_object 重试一次（`llm_client.py:199-202`）。
  2. **纯文本兜底**：teach 全部重试失败后，用 `json_mode=False` 再调一次，直接把纯文本给学生（`llm_client.py:270` 后的绝对兜底；`app.py:342-349` 前置于此）。
- **LLM 调用记录**：🟡 有，但只记业务字段：`logs.log_event()` 记 `task_id/mode/behavior/hint_level/user_message[:500]/ai_response[:800]/quality_warnings/...`（`app.py:401-418`）。**不记** prompt 全文、不记 model 名、不记 token 数。
- **Token / Cost 计算**：❌ 完全不存在。全仓库无 `usage` / `prompt_tokens` / `completion_tokens` 读取，无成本统计。

**【判断】** 模型层是"**单 Provider + 单模型 + 参数化覆盖**"的最简形态。它把工程复杂度全部投在了**输出可靠性**上（JSON 容错 + 语义校验 + 重生成 + 兜底），而不是模型编排或多模型路由上。这种取舍对本项目（零基础学生 + BYOK 成本敏感 + 必须结构化渲染）是合理的，但意味着**任何"按任务选模型/按难度升级模型"的能力都需要新增抽象**。

### 5.1 JSON 可靠性链（本项目在 LLM 层的核心资产）

**【事实】** 四级防线，全部在 `ai_engine/llm_client.py`：

1. `_validate_request()`（`:73`）——发送前本地拦截服务商硬约束（如 DeepSeek `json_object` 要求 prompt 含 "json" 字样）。
2. `_extract_json()`（`:107`）——剥离 ``` 围栏 → 取首个 `{` 到末个 `}` → `json_repair` 容错修复。
3. `_semantic_validate_review()`（`:132`）——**严格语义校验**：criteria 非空、`rubric_id` 必须属于送审白名单、`evidence`/`reason` 非空、逐条覆盖完整。repair 出来的值不得直接当正式评审。
4. 重生成 / 纯文本兜底——校验失败把错误回传模型重试（`MAX_RETRIES=2`），最终降级为纯文本。

**【判断】** 这是本项目最成熟、最可复用的工程资产（与课程无关、与 DeepTutor 之类底座不冲突），属于应当保留的模块（见 §22）。

---

## 6. RAG / Knowledge Base

### 6.1 导师引擎侧的"RAG"（事实：不是向量检索）

**【事实】** 文档进入导师引擎的链路与用户模板给的链路**不一致**：

```
data/raw/*.md
 → scripts/chunker.py 离线分块（结构化语义分块）
 → data/chunks.jsonl（含 id/doc/section/section_path/category/text/source_url/chunk_size）
 → 运行时：context_builder._retrieve_material(task.chunk_key)
      → course_data.chunks_by_section_path(chunk_key)   ← 对 section_path 做**子串匹配**
      → 取前 6 条，按 text[:40] 去重
 → 拼接进 System Prompt 的【教学材料】段
```

**没有** Embedding、**没有** 向量索引、**没有** BM25、**没有** Rerank、**没有** Hybrid Search、**没有** Context 压缩。

- Chunk 策略（离线）：`scripts/chunker.py:18-20` `CHUNK_MAX=600` / `CHUNK_MIN=30` / `CHUNK_OVERLAP=80`；按 Markdown 标题层级切分并保留 `section_path` 层级串（`chunker.py:128-132`），跨章节时重置重叠（`chunker.py:209`）。
- Metadata：`chunker.make_chunk()` 产出 `id/doc/section/section_path/category(子类别)/source_url/updated_at/chunk_size`（`chunker.py:170-183`）。
- 检索入口：`course_data.chunks_by_section_path(keyword)`（`course_data.py:57`）+ `chunks_by_doc()`（`:51`），基于 `load_chunks()` 的 `lru_cache` 全量载入（`:35`）。
- 语料规模：`data/chunks.jsonl`；文档清单 `data/docs_manifest.csv` 共 **26 篇**（home ×1 / guide ×15 / appendix ×11 类别分布，子类别 nav/policy/experience/tool/org/life）。
- 支持的文件：仅**离线 Markdown**（`data/raw/*.md`）。**不支持**运行时上传、不支持 PDF/Word/网页/代码仓库导入。
- Knowledge Base 隔离：❌ 无。全站共享一份语料，无用户级/项目级/课程级命名空间。
- 增量更新：🟡 需人工重跑 `scripts/chunker.py` 并（校园站）删除 `data/embedding_cache.npy` 重建缓存。无增量索引。
- GitHub Repository / Web / 代码仓库作为知识库：❌ 都不支持（GitHub 只作为**学生作品证据**，不是知识源，见 §8）。

### 6.2 校园问答站的 RAG（事实：完整混合检索）

**【事实】** `backend/retrieval.py` 的 `Retriever.search()`（`:341`）实现了完整的 5 路召回 + 融合：

| 环节 | 实现 | 位置 |
|---|---|---|
| 中文分词 | jieba + ~70 条校园自定义词典 + 停用词 | `retrieval.py:38-83` |
| 查询归一/扩展 | 同义词表 `_SYNONYMS`、`_normalize_query`、`_expand_query` | `retrieval.py:84-123` |
| 意图分类 | policy / tool / org / life / experience / auto | `retrieval.py:180` `classify_intent()` |
| 召回 1 | BM25（rank_bm25） | `_bm25_recall()` `:269` |
| 召回 2 | 标题精确匹配 | `_title_match_recall()` `:275` |
| 召回 3 | section_path 匹配 | `_section_path_recall()` `:293` |
| 召回 4 | 关键词重叠 | `_keyword_overlap_recall()` `:310` |
| 召回 5 | 向量召回（bge-small-zh-v1.5） | `_vector_recall()` `:257` |
| 融合 | **加权 RRF** | `_fuse_results()` `:328` |
| 重排 | 意图加权（1.3×/0.8×）→ 文档去重 → 可选 BGE reranker → 父级上下文扩展 | `search()` `:341-460` |
| 缓存 | 1 小时 query 结果缓存 | `search()` 内 |

- 相关性判定：`is_relevant()`（`:461`）；语料统计：`chunk_count()`（`:484`）。
- 嵌入服务：`backend/embedding.py` `EmbeddingService`（均值池化 + L2 归一 + query 前缀），向量缓存 `data/embedding_cache.npy`。
- Hybrid Search：✅（BM25 + 向量 + RRF）。
- GraphRAG：❌ 不存在。Reranking：🟡 有代码、默认禁用（`config.RERANK_ENABLED="0"`，防 1.8G 内存 OOM）。

**【判断】** 项目里**存在一套工业级 RAG，但它服务于校园问答，不服务于 AI 导师**。AI 导师的"教学材料"注入是**基于 `chunk_key` 的定向切片**——这在设计上有其合理性（课程作者已手工标注任务该读哪一节，无需语义检索），但代价是：**任务与语料的关联完全依赖人工标注 `Task.chunk_key`**，一旦标注缺失（`context_builder.py:20` `if not chunk_key: return []`）或 `section_path` 改名，教学材料即静默为空。这是一个**脆弱耦合点**（见 §19）。

---

## 7. Memory

**【事实】** 逐项核查：

| 类型 | 状态 | 证据 |
|---|---|---|
| Conversation Memory | ✅ 已实现 | `sessions.history_json` 全量历史（`store.py:95,168`）；每轮 `sess.history.append()`（`app.py:382-383`）；注入时取最近 12 轮（`app.py:330`）；前端 `localStorage['xkz_chat_v1']` 作为显示缓存（`TeachView.vue:955-958`）。 |
| 调试状态记忆 | ✅ 已实现 | `sessions.debug_state_json` ← `DebuggerState`（rounds/phase/last_diagnostic_question/last_suspected_cause），跨轮注入（`store.py:171-175`、`app.py:300-303`、`app.py:386-394`）。 |
| 系统错误记忆 | ✅ 已实现 | `sessions.last_system_error`，下一轮注入隔离声明后清除（`app.py:347-350`、`app.py:98-108`）。 |
| User Memory | ❌ 完全不存在 | 无用户画像、无偏好记忆。`Student.name` 恒为"匿名学生"（`TeachView.vue:395`）。 |
| Project Memory（学习者的项目记忆） | ❌ 完全不存在 | 无"学生项目历史状态"存储；每次 review 都重新拉取 GitHub 现状，不保存仓库快照。 |
| Learner Memory / Learning Memory | ❌ 完全不存在 | `Student.skills` 是空壳（见 §12）。 |
| 长期记忆摘要（rolling summary） | ⏳ 预留字段但未实现 | `sessions.summary_json` 字段存在，但 `save_session()` 恒写入 `None`，注释"V1 不做 LLM 摘要，留空"（`store.py:97,202`）。 |
| Memory 写入位置 | — | `store.save_session()`（`store.py:179`） |
| Memory 检索位置 | — | `store.get_session()`（`store.py:156`）、`session_history()`（`store.py:207`） |
| Memory 是否结构化 | 🟡 部分 | history 是"角色+文本"列表（无实体/无标签）；debug_state 是结构化对象（唯一结构化记忆）。 |
| Memory 生命周期 | 🟡 部分 | 会话表无 TTL，永久保留；`lazy_cleanup()` 只清理评审缓存与熔断，**不动 sessions**（`store.py:313-336`）。 |
| Memory Graph | ❌ 完全不存在 | — |

**【判断】** 本项目只有**会话内短期记忆**（对话历史 + 调试状态机 + 系统错误标记）。**没有任何跨会话、跨任务的长期记忆**。`history[-12:]` + `_trim(6000 字符)` 意味着**长对话会静默丢失早期上下文**，且没有摘要补偿——这是 §19 中列出的技术债之一。把本项目的 "Memory" 与 DeepTutor/LeafTutor 的 L1/L2/L3 可检视记忆对比时，必须明确：**本项目在这一维度上是空白**。

---

## 8. GitHub / 项目代码理解能力

**【事实】** 全部实现集中在 `ai_engine/code_evidence.py`（516 行）。

| 问题 | 答案 | 证据 |
|---|---|---|
| 如何接收仓库？ | 请求体字符串字段：`TeachRequest.repo_url` / `ReviewRequest.repo_url` / `Submission.github_url` | `schemas.py:367,382,217` |
| GitHub Authentication | **可选静态 Token**：读环境变量 `GITHUB_TOKEN`，存在则加 `Authorization: Bearer`，否则匿名（60 次/小时） | `code_evidence.py:113-115` |
| Clone / Pull | ❌ **完全不 clone**。全部走 REST API | 无 git 调用；`_fetch_file_content()` 走 Contents API（`:203`） |
| Branch 处理 | 只用**仓库默认分支**（`_repo_default_branch()` `:126`），**不可指定** | — |
| Commit 读取 | ❌ 不存在。仅读 Actions 运行结论（`fetch_ci_evidence()` `:307`），不读 commit 元数据 | — |
| File Tree | `GET /repos/{o}/{r}/git/trees/{branch}?recursive=1`，过滤 `_SKIP_DIRS`（node_modules/dist/.git/venv…） | `_fetch_tree()` `:134`、`_filter_structure()` `:147`、`_SKIP_DIRS` `:59` |
| Code Search | 🟡 无代码内容搜索。替代方案是**路径/文件名启发式打分** + 可选 LLM 二次筛选 | `rank_candidate_files()` `:376`（文件名 0.5/0.3 + 关键词 0.1 + 路径权重）、`ai_relevance_filter()` `:420` |
| Code Chunk | 🟡 非语义分块：**整文件按行截断**（默认 120 行，报告类文件 250 行） | `FILE_LINES_MAX=120`、`REPORT_LINES_MAX=250`、`_lines_cap_for()` `:160` |
| Repository 索引 | ❌ **不建立任何持久索引**。结果只做 300 秒进程内 TTL 缓存（`_cache`，`CACHE_TTL=300` `:56`） | `build_code_evidence()` `:466-470` |
| 增量同步 | ❌ 不存在 | — |
| 指定 commit/branch | ❌ 不支持 | — |
| 项目快照保存 | 🟡 **不保存仓库内容**，但保存**证据快照哈希**：`snapshot_evidence()` 对证据文本+CI 结论+task_id 做 sha256[:16]（`review.py:133`），用于幂等缓存键 | — |
| AI 如何知道学生项目当前状态 | 每次请求**实时拉取**：文件树（前 200 条）+ 最多 10 个关键文件正文 + CI 结论 + 最多 5 条 Issue，拼成 ≤20000 字符的证据文本注入 Prompt | `_assemble()` `:572`、`EVIDENCE_CHAR_CAP=20000` `:55` |

**关键文件选取优先级（事实）**：报告类（`_KEY_REPORT`，含 `test_report.md/tests_report/bug_report/issues/retro…`）> README > 依赖清单 > 主入口 > 配置 > tests 目录下最多 2 个测试文件（`_pick_key_files()` `:171-196`）。

**两条并行路径（事实）**：
- 有 `Task.code_context`（课程作者标注 `keywords/likelyFiles/searchPatterns`，`schemas.CodeContext`）→ 走 Task-aware 打分（可选 AI 二次筛选）取前 5（`:484-510`）。
- 无 `code_context` → 回退固定优先级选取（`:511-516`）。

**证据类型扩展**：
- CI：`fetch_ci_evidence()` 拉 Actions 工作流 + 最近 20 次运行，按工作流名映射维度 build/test/lint/runtime（`_CI_DIMENSION` `:230`）。
- Issues：`fetch_issues_evidence()` 拉最多 5 条 Issue（过滤 PR），供课程 03「发现问题」类验收项（`:249`）。
- Trace：仅当证据文本含字符串 `agent_trace.json` 时登记一条 `trace` 证据（`review.py:76-77`）——**只做字面检测，不解析内容**。

**【判断】** 这是"**API 只读 + 启发式选文件 + LLM 阅读**"的轻量代码理解方案。它的能力上限是"**看到学生写没写、结构对不对**"，能力边界很明确：
- 不能证明"跑没跑通"（项目自己在 `review.py:358` 明确承认，只能靠 CI/部署/自述三选一）；
- 不能做跨文件静态分析（无 AST、无调用图、无依赖解析）；
- 默认分支 + 300 秒缓存 + 20000 字符上限，意味着**多分支/大仓库/长文件场景会丢失信息**；
- 无 commit 快照，因此**无法回答"学生在某次验收之后改了什么"**——这是与"项目制导师"目标（演进式提交、复盘）之间的一个实质性缺口（见 §20）。

---

## 9. Code Execution / Sandbox

**【事实·不存在性证明】**
- Grep `subprocess|Popen|os.system|exec\(|shutil.which` 于全部 `*.py`：命中项仅为
  - `ai_engine/code_evidence.py:27` `RUN_CMD_PATTERN`（正则，用于从 README/自述里**识别**启动命令行文本）
  - `ai_engine/store.py` 的 `_exec()`（SQLite execute 封装）
  - `scripts/chunker.py` 的 `re.compile`
  → **无任何进程创建、无容器编排、无代码求值**。
- 无 Dockerfile、无 docker-compose、无 k8s 清单（仓库根目录仅 `README.md`、`xkz-agent.conf`、`.gitignore` + 6 个目录）。
- 无 Judge0 / Piston / E2B / Firecracker 等沙箱服务依赖（`ai_engine/requirements.txt` 无相关包）。

**【判断】** 逐项回答用户清单：

| 问题 | 结论 |
|---|---|
| 是否可以执行学生代码 | ❌ 不能 |
| 支持哪些语言 | — |
| 怎么启动 | — |
| Docker / Sandbox / VM / subprocess | ❌ 全无 |
| 权限隔离 / 网络隔离 / CPU / Memory / Time 限制 | ❌ 全无 |
| 如何获取 stdout / stderr | ❌ 不获取 |
| 如何判断执行失败 | ❌ 不判断 |
| 如何运行测试 | ❌ 不运行。测试执行**外包给学生的 GitHub Actions** |
| 是否存在测试生成 | ❌ 不存在 |
| 是否存在自动 Debug | 🟡 仅"教学式引导调试"：Debugger 六段状态机 + `verify_steps` 让学生**自己去跑**（`prompts.py:92-99`），不是自动调试 |

### 9.1 关键区分：执行代码 vs 用执行结果验收

**【事实】** 本项目把"执行"这件事**转移给了外部系统**：
- `fetch_ci_evidence()` 读取 GitHub Actions 的运行结论（`conclusion`），并标注为"system 判定，权威"（`code_evidence.py:357`）。
- `review.ci_direct_verdict()` 把 CI 结论**在代码层直接映射**为 Rubric 的 PASS/FAIL，**不经过 LLM**（`review.py:272-324`）。
- CI 维度 → 证据类型映射：`build/test/runtime`（`_CI_DIM_TO_EVIDENCE` `review.py:265-269`）；含语义判定的 `description`/`code` 一律不直判，留给 LLM（`review.py:284`）。

**【判断】** 明确回答用户的问题：
- "能够执行代码" → **❌ 完全不具备**。
- "能够把代码执行结果作为项目验收证据" → **✅ 部分具备，但执行者是学生自己的 GitHub Actions，不是本系统**。

这是一个**重要的架构判断**：本项目用"**借用学生仓库的 CI 作为可信执行者**"来规避自建沙箱。这带来了显著优势（零基础设施成本、零安全风险、结论由 GitHub 这一第三方权威出具），也带来硬约束（**没有 CI 的仓库，运行/测试类验收项永久无法自动判定**，只能落到 NEED_REVIEW 或学生自述）。

---

## 10. 项目制学习能力（严格审计）

**【事实】** 逐项标记（证据均为 `ai_engine/schemas.py` + `course_data.py` / `course03_data.py`）：

| 模块 | 状态 | 证据 / 说明 |
|---|---|---|
| Project | ✅ 已实现 | `schemas.Project`（id/title/description/stages/tasks/rubrics/source_url + resume_* 素材）；4 个项目（`_PROJECT_BUILDERS` `course_data.py:684`；`COURSE_003.projects` `course03_data.py:28`） |
| Milestone（阶段） | ✅ 已实现 | `schemas.Stage`（id/title/order/objective/tasks）；实测 12 个 Stage（course_data 7 + course03_data 5） |
| Task | ✅ 已实现 | `schemas.Task`；实测 26 个 |
| Dependency（任务依赖） | ❌ 完全不存在 | 只有 `order` 排序，无 `depends_on` / 先修校验；`get_next_task()` 仅按 `(stage_id, order)` 取下一个（`course_data.py:776`） |
| Learning Objective | ✅ 已实现 | `Task.objective`（文字目标）+ `Stage.objective` |
| Deliverable | 🟡 部分实现 | 有 `Task.evidence_required`（Literal: code/code+test/test/url/screenshot/none，`schemas.py:151`）与 `Rubric.required_evidence`，但**无独立 Deliverable 对象**，也无交付物清单/附件管理 |
| Submission | 🟡 部分实现 | `schemas.Submission`（github_url / deployment_url / code / description），**仅在 `/api/ai/review` 请求体内存在，不落库**（`store.py` 无 submission 表） |
| Acceptance Criteria | ✅ 已实现 | `schemas.Rubric.criterion/description/pass_condition` |
| Rubric | ✅ 已实现 | 81 条，含 `weight`（默认 1）与 `required_evidence` |
| Evidence | 🟡 部分实现 | 运行时把证据归一到内存 dict（`review.collect_evidence()` `:64`，9 种类型）；DB 有 `evidence` 表与 `add_evidence/list_evidence`（`store.py:282-308`）——但**主流程从不调用 `add_evidence`**（`app.py:54` 定义了 `store_evidence()` 包装函数，`app.py` 内**无任何调用点**）→ **Evidence Store 是空表** |
| Evaluation | ✅ 已实现 | `ReviewEvaluation` + `compute_evaluation()` |
| Revision（修订） | 🟡 部分实现 | 有 `next_step` 指引 + `attempt_count` 计次 + 允许重复提交（同 task 可反复 review）；**无修订记录、无版本对比、无 diff 提示** |
| Re-submission | ✅ 已实现 | 重新 POST `/api/ai/review` 即可；`snapshot_hash` 变化即视为新提交并重新评审（`app.py:584`） |
| Completion Gate | 🟡 部分实现 | **门禁存在但只作用于前端展示**：`status == "PASS"` 才 push 到 `completed_tasks`（`TeachView.vue:1135`）、才返回 `next_task`（`app.py:740-745`）。**后端不阻止学生继续学下一个任务**——`/api/ai/teach` 对未通过任务的任务照常响应（`app.py:232` 只校验 task 是否存在）。 |

**【判断】** 本项目已经具备"**课程 → 项目 → 阶段 → 任务 → Rubric → 提交 → 验收**"这条主轴，且这条主轴是**真实可跑通**的（不是空壳）。缺口在三点：
1. **无依赖/门禁的强约束**（可跳任务，服务端不拦）；
2. **Submissions / Evidence 不落库**（无法构建学生提交历史与证据档案）；
3. **无 Deliverable 对象与版本管理**（无法做"同一交付物的多轮演进"）。

---

## 11. 自动验收系统

**【事实】** 这是全项目最完整的一条链路，逐项核查：

| 检查项 | 状态 | 证据 |
|---|---|---|
| 自动测试 | ❌ 本系统不跑测试 | 见 §9；测试执行外包给学生的 GitHub Actions |
| 静态分析 | ❌ 不存在 | 无 AST/linter/复杂度分析调用 |
| LLM Code Review | ✅ 已实现 | `llm_client.review()` + `review.build_review_system_prompt()`（`review.py:330`） |
| Rubric | ✅ 已实现 | 81 条，逐条判定并要求 `evidence` + `reason` |
| 硬性通过条件 | ✅ 已实现 | ① `evidence_precheck()`：`required_evidence` 缺一即强制 NEED_REVIEW，**不走 LLM**（`review.py:177-224`）；② `_semantic_validate_review()`：rubric_id 越界 / 缺字段即重试（`llm_client.py:132`） |
| 软性评分 | ✅ 已实现 | `score = round(Σ通过条目weight / Σ全部weight × 100)`，**后端计算**（`review.py:239-253`） |
| Evidence | 🟡 部分实现 | 运行时证据归一 ✅；Evidence 持久化表 🔴 未接入 |
| PASS / FAIL / NEED_REVIEW | ✅ 已实现 | `ReviewStatus`（`schemas.py:289`）；判定优先级 **FAIL > NEED_REVIEW > PASS**（`review.py:254-259`） |
| 验收报告 | 🟡 部分实现 | 返回 `evaluation{status,score,criteria[],next_step}` 即为报告（`app.py:735`）；无独立导出/持久化报告，前端只在会话内展示 |
| 重新提交流程 | ✅ 已实现 | 再次 POST `/review`；同证据（`snapshot_hash` 相同 + 同 model + 同版本）→ 命中幂等缓存直接返回（`app.py:596-601`），**不重复烧 LLM 额度** |
| CI 直判（零 LLM 判定） | ✅ 已实现 | `ci_direct_verdict()`（`review.py:272`）：结论必须**同向且仅为 success/failure** 才直判；混合结论/其它状态返回 None 交 LLM |
| 失败熔断 | ✅ 已实现 | 同 key 5 分钟内复用失败结论，不再调 LLM（`app.py:588-593`，`FAILURE_TTL=300` `store.py:37`） |
| 幂等缓存版本化 | ✅ 已实现 | key = `task_id:snapshot_hash:rubric_version:prompt_version:engine_version:model`（`store.py:62`）；版本常量需**手工 bump**（`store.py:29-32`） |
| 系统错误隔离 | ✅ 已实现 | 任何 LLM/Provider 异常 → `REVIEW_UNAVAILABLE`，**绝不写入学生 Evaluation**（`app.py:111-125`、`:678-683`） |
| 视觉证据（截图） | 🟡 部分实现 | `vision.analyze_images()` 只在模型白名单内生效；**永远不是硬门槛**（`optional_bonus` 排除 visual，`review.py:196`）；`visual_check="supported"` 只作可选增强 |
| 零 LLM 快路径 | ✅ 已实现 | 所有 Rubric 都缺证据且无 CI 直判 → 直接返回 NEED_REVIEW，**零 LLM 调用**（`app.py:624-655`） |

### 11.1 核心问题：系统真能判断项目完成吗？

**【事实·代码级回答】**
判定"完成"的**唯一**入口是 `POST /api/ai/review` → `passed = (status == "PASS")`（`app.py:738`）。而 `status == "PASS"` 的**充要条件**（`review.py:239-259`）是：

1. 该任务**每一条** Rubric 都有 `criteria` 结果（缺证据的会被 `evidence_precheck` 先变成 NEED_REVIEW）；
2. 每一条的 `status` 都不是 FAIL；
3. 每一条的 `status` 都不是 NEED_REVIEW（即全部 PASS）；
4. 每一条 PASS 的来源要么是 **CI 直判**（GitHub Actions 同向 success），要么是 **LLM 逐条判定 PASS**。

**【判断】**
- **能判断，但强依赖外部证据链。** 对于有 CI 的任务，系统能做到"**非 AI 的、可复现的**自动验收"（CI success → Rubric PASS，`:316-319`），这是本项目验收设计中最有价值的部分。
- **对没有 CI 的仓库，运行/测试类验收项无法由系统本身确证**，只能退化为"LLM 读代码 + 学生自述"，并在缺证据时一律 NEED_REVIEW。这是**设计上的诚实**（宁可拒绝判 PASS 也不放水），但也意味着**验收强度随手写质量波动极大**。
- **前端"完成"按钮（`TeachView.vue:239`）不是完成判定**：它只是 `mode_advice.mode === 'reviewer'` 时显示的"去提交验收"入口。真正的判定在后端；`task_completed` 字段只在 review 事件中由 `status == "PASS"` 写入（`app.py:721`），teach 事件恒为 `False`（`app.py:415`，注释明确"完成判定只来自验收链"）。**这一点用户判断正确，代码与注释一致。**

---

## 12. Learner Model / Mastery

**【事实·逐项核查】**

| 问题 | 状态 | 证据 |
|---|---|---|
| 是否记录学生技能掌握程度 | ❌ 不存在 | `schemas.SkillKey`（13 项技能枚举）+ `Student.skills: dict[SkillKey,int]` 定义存在；但全仓库对 `skills` 只有**初始化**（`TeachView.vue:395,1310` 均写 `{}`），**无任何赋值/累加/读取代码**。`ai_engine` 侧不持久化 skills（`store.py` sessions 表无启列）。→ **空壳字段** |
| 是否有知识点状态 | ❌ 不存在 | 无知识点模型、无掌握度、无错题本 |
| 是否有能力状态 | ❌ 不存在 | 同上 |
| 是否可以跨课程累计 | ❌ 不存在 | 无跨课程聚合结构 |
| 是否可据验收结果更新学习状态 | 🟡 仅前端 + 仅"是否完成" | review PASS → `student.completed_tasks.push(task_id)`（`TeachView.vue:1135-1136`），存 `localStorage['xkz_ai_student']`；**不更新 skills、不更新任何能力值** |
| 是否存在弱项识别 | 🟡 仅运维视角 | `logs.compute_stats()` 的 `probably_blocked_tasks`（尝试≥3 且未通过，`logs.py:109-111`）是**运营侧卡点统计**，不是发给学生的个人弱项诊断 |
| 是否存在复习机制 | ❌ 不存在 | — |
| 是否存在推荐下一任务 | 🟡 简单线性 | `get_next_task()` 按 `(stage_id, order)` 取下一个（`course_data.py:776`）；review PASS 时返回 `next_task`（`app.py:740-745`）；**前端选择"高亮+提示卡，不自动切换"**（注释 `app.py:739`） |

**三类 Mastery 的结论**：

| 类型 | 状态 | 说明 |
|---|---|---|
| Knowledge Mastery | ❌ 不存在 | 无知识点粒度模型 |
| Project Mastery | 🟡 弱 | 只有"任务是否 PASS"的布尔集合，且存在前端 localStorage，无分数/无时间/无演进 |
| Skill Mastery | ❌ 不存在 | `SkillKey` 枚举与 `Task.skill` 字段存在（`schemas.py:153`，课程作者标注了每任务关联技能），**但没有任何代码消费它做聚合** |

**【判断】** `Task.skill` + `SkillKey` + `Student.skills` 这一组数据结构**是"技能掌握度"设计的完整半成品**：数据标注齐全（课程作者已为任务标注 skill），但**聚合、存储、回写、消费四个环节全部缺失**。这是本项目离"Learner Model"最近的地方，也是**投入产出比最高的待补模块**（见 §20、§22）。

此外，`student.completed_tasks` 存 localStorage 意味着：**换设备/清缓存 = 学习进度丢失**（`session_id` 也是前端随机生成的 `s_xxxxxxxx`，`TeachView.vue:395`）。项目自己在 `session_history` 接口注释里承认 localStorage 只做"显示缓存"（`app.py:483-485`），但**进度本身没有服务端真相源**——这是一个明确的设计-实现落差。

---

## 13. 简历与面试能力

### 13.1 简历（Resume）

**【事实】**
- 入口：`POST /api/career/text`（`app.py:773`），请求体 `CareerTextRequest{project_id, results[], github_url, date}`（`app.py:766`）。
- 实现：`ai_engine/career.py` `build_career_text()`（`:120`）——**零 LLM**，纯模板 + 数据填充（设计原则注释 `career.py:14`「同输入必同输出，杜绝文案漂移」）。
- 数据来源（**关键**）：
  - `Project.resume_intro / resume_role / resume_tech / resume_metrics`——**课程作者手工标注**（`schemas.py:93-97`）；
  - `Task.resume_points: list[ResumePoint]`（`point/purpose/result/kind`）——**课程作者手工标注**（`schemas.py:100-111,158`）；实测标注量 29 条（`InterviewQuestion(` / `ResumePoint(` 合计：course_data 17 + course03_data 12）。
  - 验收结果 `results[]`（`task_id/score/passed/total/ci_conclusion`）来自前端存的 review 返回值。
- 输出：`{title_line, intro, tech[], bullets[{label,text}], metrics[], text}`。
- 过滤规则：`is_learning_text()`（`career.py:49`）——含"学习/了解/熟悉/掌握…"且**不含**交付动词的句子一律剔除（`_LEARNING_MARKERS` / `_DELIVERY_MARKERS` `career.py:32-41`）。
- 量化：`通过 N/M 项自动化验收用例`、`持续集成（GitHub Actions）全部通过`（`career.py:150-156`）。
- 兜底：无 `resume_points` → 回退任务标题（剔除学习属性）（`_fallback_features()` `:109`）。

**【判断】** 简历能力**已实现且产出稳定**，但它本质是"**课程作者预写素材 + 验收结果数字**的确定性模板拼装"。它能生成：
- ✅ 项目经历、✅ 技术栈、✅ 量化成果、✅ 可粘贴正文。
但**不能**生成：
- ❌ 项目贡献的深度分析（如"你负责了哪一层"）——`resume_role` 由课程作者写死（默认"独立开发"）；
- ❌ 学生个体差异化的表述——同一项目同一组验收结果 → **所有人的简历文字完全相同**。这是模板化设计的必然结果（也是刻意为之）。
- ❌ 跨项目合并简历（`build_career_text` 一次只处理一个 `project`）。

### 13.2 面试（Interview）

**【事实】**
- 入口：`GET /api/ai/interview?task_id=`（`app.py:804`）。
- 返回：`task.interview_questions`（`schemas.InterviewQuestion{id, question, answer_anchor, hint, type: explain|debug|transfer}`），`ai_generated: False`（`app.py:815`）——**全部由课程作者手写**。
- 硬边界（代码注释 + 实现一致）：**不判分、不进评审链、不写 Evidence Store、不写评审日志字段**（`app.py:801-803`）。
- 面试题类型：解释 / 调试 / 变式（`schemas.py:139`）。

**【判断】** 逐项回答用户清单：

| 能力 | 状态 | 来源 |
|---|---|---|
| 项目经历 | ✅ | 课程作者标注 + 验收结果模板 |
| 技术栈 | ✅ | `Project.resume_tech`（人工） |
| 项目贡献 | 🟡 | 仅 `resume_role`（人工写死） |
| 可量化成果 | ✅ | 验收通过数 + CI 结论 |
| 面试题 | ✅ | 课程作者手写 `InterviewQuestion` |
| 项目追问 | ❌ | 不存在（题目是一次性返回的静态列表，无追问） |
| 技术原理题 | 🟡 | `InterviewQuestion.type` 含 `explain`，但内容由课程作者决定，非系统生成 |
| 项目复盘 | ❌ | 不存在 |

**结论：简历 ≠ AI 生成，面试题 ≠ AI 生成。两者都是"课程作者的静态内容 + 确定性模板"，与模型无关。**

---

## 14. 数据模型

### 14.1 持久化模型（SQLite，唯一真相源）

**【事实】** `ai_engine/store.py:_create_tables()`（`:86-136`）建 4 张表：

| 表 | 用途 | 关键字段 | 关联对象 |
|---|---|---|---|
| `sessions` | 会话真相源（PK = `session_key`） | `session_key`(PK), `session_id`, `student_id`, `task_id`, `mode`, `hint_level`, `history_json`, `debug_state_json`, `summary_json`(**恒 NULL**), `last_system_error`, `attempt_count`(TEXT), `created_at`, `updated_at` | 无外键；`session_key = session_id:task_id` |
| `review_results` | 评审成功幂等缓存 | `id`(PK autoinc), `task_id`, `snapshot_hash`, `rubric_version`, `prompt_version`, `engine_version`, `model`, `response_json`, `created_at`；唯一索引 `uq_review_result_key`（6 列联合） | 无外键；由 `snapshot_evidence()` 哈希定位 |
| `review_failures` | 评审失败熔断 | `review_key`(PK), `retry_after`(float), `error`, `created_at` | 与 review_results 共用 key 生成器 `_KV.fields()` |
| `evidence` | 证据存储（**主流程未接入**） | `id`(PK), `task_id`, `rubric_id`, `type`, `source`, `content`, `confidence`, `created_at`；索引 `idx_evidence_task` | 无外键 |

工程参数：`journal_mode=WAL`、`busy_timeout=30000`、`synchronous=NORMAL`、单写连接 + `threading.Lock`（`store.py:68,78-83,138-141`）。清理策略：`lazy_cleanup()` 删过期熔断、删 >90 天评审结果、每任务保留最近 200 条（`store.py:313-333`）；**sessions 永不清理**。

### 14.2 业务模型（Pydantic，**不持久化**，全部硬编码在 Python 里）

**【事实】** `ai_engine/schemas.py`：

| 模型 | 行号 | 说明 | 持久化 |
|---|---|---|---|
| `Student` | :64 | `session_id / name / skills{} / completed_tasks[] / attempt_count{} / timestamp` | ❌ 仅前端 localStorage `xkz_ai_student` |
| `Course` | :76 | `id/title/description/projects[]` | ❌ 硬编码 |
| `Project` | :84 | `id/title/description/stages[]/tasks[]/rubrics[]/source_url` + `resume_intro/resume_role/resume_tech/resume_metrics` | ❌ 硬编码 |
| `Stage` | :114 | `id/title/order/objective/tasks[]` | ❌ 硬编码 |
| `Task` | :142 | `id/title/stage_id/order/objective/steps[]/hints{}/evidence_required/rubric_ids[]/skill/source_url/chunk_key/code_context/interview_questions[]/resume_points[]` | ❌ 硬编码 |
| `Rubric` | :161 | `id/task_id/criterion/description/required_evidence[]/pass_condition/weight/visual_check/visual_pass_condition` | ❌ 硬编码 |
| `CodeContext` | :123 | `keywords[]/likelyFiles[]/searchPatterns[]` | ❌ 硬编码 |
| `ResumePoint` | :100 | `point/purpose/result/kind` | ❌ 硬编码 |
| `InterviewQuestion` | :130 | `id/question/answer_anchor/hint/type` | ❌ 硬编码 |
| `Submission` | :208 | `id/task_id/student_id/github_url/deployment_url/code/description/submitted_at` | ❌ **不落库** |
| `Evidence` / `EvidenceType` | :225,:238 | 10 种证据类型（CODE/CI/RUNTIME/VISUAL/GITHUB/DESCRIPTION/MANUAL/TRACE/REPORT/ISSUE） | 🟡 表存在但主流程未写 |
| `AISession` | :250 | 会话对象（对应 sessions 表） | ✅ |
| `DebuggerState` / `DebugPhase` | :277,:266 | 调试状态机 | ✅（JSON 列） |
| `VisualEvidence` / `VisualImage` | :181,:192 | 视觉证据（原图不保留） | ❌ 请求级 |
| `ReviewStatus` / `ReviewCriterion` / `ReviewEvaluation` / `ReviewLLMOutput` | :289-323 | 评审模型（LLM 输出**不含** score/status） | 🟡（作为 response_json 一部分） |
| `AiResponse` | :332 | LLM 结构化输出（无条件字段 + 按行为条件字段） | ❌ |
| `TeachRequest` / `ReviewRequest` / `TeachContext` | :358,:376,:389 | 请求/上下文 | ❌ |

### 14.3 用户点名的实体核查

| 实体 | 结论 | 证据 |
|---|---|---|
| User | ❌ 无表无模型 | 只有 `session_id` 字符串（前端生成） |
| Session | ✅ | `sessions` 表 + `AISession` |
| Message | 🟡 | 无独立表；作为 `sessions.history_json` 数组元素（`{role, content}`） |
| Project | 🟡 | 有模型，无表（硬编码） |
| Task | 🟡 | 有模型，无表（硬编码） |
| Course | 🟡 | 有模型，无表（硬编码） |
| Knowledge | 🟡 | 无表；`data/chunks.jsonl` 文件 + `docs_manifest.csv` |
| Submission | ❌ | 有模型（`schemas.py:208`），**无表** |
| Evaluation | 🟡 | 无表；作为 `review_results.response_json` 内嵌 |
| Evidence | 🔴 | 有表 + 有模型 + 有 `add_evidence()`，**主流程无调用点** |
| Skill | ❌ | 仅 `SkillKey` 枚举 + `Task.skill` 标注 |
| Mastery | ❌ | 无表无模型无逻辑 |
| Memory | 🟡 | 只有会话记忆，见 §7 |

**【判断】** 数据模型的本质是：**"配置即代码"（课程/项目/任务/Rubric 全在 Python 里硬编码）+ "状态入 SQLite"（会话/评审缓存）**。优点是零迁移、零 ORM、改课程只改代码；代价是**课程内容与引擎代码强耦合**（加一门课 = 改 Python 文件 + 重新部署），且**学习者数据（Submission/Evidence/Mastery）没有落点**。

---

## 15. API

**【事实】** 核心 API 清单（省略 health/config 之外的细节）：

### 15.1 AI 导师引擎（`ai_engine/app.py`，:8099）

| Method | Path | 请求 | 响应（关键字段） | Handler | 依赖 |
|---|---|---|---|---|---|
| GET | `/api/ai/health` | — | `status/model/base_url` | `app.py:178` `health()` | — |
| GET | `/api/ai/config` | — | `models/vision_models/modes/hint_levels/courses/projects` | `app.py:188` `config()` | `course_data.list_courses/list_projects`、`vision.VISION_WHITELIST` |
| POST | `/api/ai/teach` | `TeachRequest` | `message/next_action/hints_used/hint_level/hint/current_step/suspected_cause/verify_steps/diagnostic_question/behavior/evidence/visual/debug_state/mode_advice/quality_warnings/latency_ms` | `app.py:221` `teach()` | `route_behavior`→`build_context`→`build_code_evidence`→`LLMClient.teach`→`validate`→`store.save_session`→`logs.log_event` |
| POST | `/api/ai/feedback` | `{session_id,task_id,accepted}` | `{accepted}` | `app.py:459` `feedback()` | `logs.set_accepted` |
| GET | `/api/ai/stats` | — | `total_teach_calls/task_completion_rate/hint_distribution/early_answer_warnings/probably_blocked_tasks/…` | `app.py:473` `stats()` | `logs.compute_stats` |
| GET | `/api/ai/session_history` | `?session_key=` | `history[]/hint_level/debug_state/last_system_error` | `app.py:479` | `store.session_history` |
| POST | `/api/ai/review` | `ReviewRequest` | `evaluation{status,score,criteria[],next_step}/score/status/passed/next_task/evidence/ci/visual/snapshot_hash/latency_ms` | `app.py:494` `review()` | 见 §11 全链路 |
| POST | `/api/career/text` | `CareerTextRequest` | `title_line/intro/tech/bullets/metrics/text` | `app.py:773` | `career.build_career_text`（零 LLM） |
| GET | `/api/ai/interview` | `?task_id=` | `questions[]/ai_generated` | `app.py:804` | `course_data.get_task` |
| POST | `/api/github/retrieve` | `CodeRetrieveRequest` | `files[{path,relevance,reason,truncated}]/ci/default_branch/file_count` | `app.py:831` | `code_evidence.build_code_evidence` |

**统一响应包络**：`{"ok": true, "data": {...}}` / `{"ok": false, "error": {"code","message"}}`。
**错误码**：`NO_TASK / NO_API_KEY / EMPTY_INPUT / BAD_TASK / NO_RUBRIC / NO_SESSION / NOT_FOUND / BAD_PROJECT / NO_RESULTS / NO_REPO / KEY_INVALID / RATE_LIMITED / ENGINE_ERROR / PROVIDER_DOWN / REVIEW_UNAVAILABLE`（`app.py:111-125` 等）。

### 15.2 校园站（`backend/main.py`，:8000）

| Method | Path | 说明 | 行号 |
|---|---|---|---|
| GET | `/api/health` | 健康检查 | `:134` |
| GET | `/api/nav_config` | 导航配置 | `:143` |
| GET | `/api/changelog` | 更新日志 | `:148` |
| GET | `/api/hot_questions` | 热门问题 | `:153` |
| GET | `/api/glossary` | 术语表 | `:158` |
| POST | `/api/verify` | 学生身份验证 | `:163` |
| POST | `/api/feedback` | 反馈 | `:186` |
| POST | `/api/ask` | **校园 RAG 问答（SSE 流式）** | `:201` |
| GET | `/{full_path:path}` | SPA fallback + 路由级 SEO 注入 + 真实 404 | `:790` |

**【判断】** API 设计的一致性较好（统一包络、统一错误漏斗、错误码语义化）。值得注意的是 `/api/ai/review` 与 `/api/ai/teach` 是**完全独立的两条链**，不共享服务层；`/api/career/text` 与 `/api/ai/interview` 又是两条**零 LLM 的旁路**。这使引擎内部形成了 4 条并行的能力通道，没有统一的 Service 层抽象（见 §19）。

---

## 16. 前端（仅功能结构）

**【事实】** Vue 3 + Vite + TS。路由 16 条（`frontend/src/router/index.ts:7-25`）：`/splash /login / /guides /appendix /about /faq /changelog /glossary /quest /roadmap /teach /resources /calendar /chat /thanks`（+ catch-all 重定向首页）。

**与 AI 导师相关的核心页面：`TeachView.vue`（1891 行）**

- **状态（ref）**：`courses/courseId/views(select|tutor)/projects/projectId/stages/mode/taskId/chat/history/student/shots(≤2 张、≤800KB)/stats`。
- **API 调用点**：`/api/ai/config`（:758）、`/api/ai/teach`（:899）、`/api/ai/session_history`（:1000）、`/api/ai/review`（:1123）、`/api/career/text`（:1191）、`/api/ai/interview`（:1208）、`/api/ai/feedback`（:1286）、`/api/ai/stats`（:1301）。
- **localStorage 键**：
  - `xkz_ai_student`（学生状态：session_id/skills/completed_tasks/attempt_count）— `:385,860,1310`
  - `xkz_ai_repo`（GitHub 仓库链接）— `:387,547`
  - `xkz_ai_api_key`（legacy BYOK key，兼容旧版）— `:386,423`
  - `xkz_teach_sel`（课程/任务选择）— `:406,411`
  - `xkz_teach_side`、`xkz_teach_tasks`（侧栏/任务清单折叠态）— `:529,841`
  - `xkz_chat_v1`（对话历史，按 `course|project|task` 结构化，每任务 ≤40 条 `CHAT_MAX_MSGS`）— `:955-972`
  - 简历结果缓存 `CAREER_KEY` — `:1165-1174`
- **学习进度展示**：`doneCount`（`completed_tasks.length`，:622）、`attemptedCount`（:623）、`currentStage`、`blockedTasks`、`hintDist` 等 computed；任务清单支持折叠（:837-841）。
- **提交与验收**：`doReview()` → POST `/api/ai/review`；PASS 时 push `completed_tasks` 并展示"下一任务"提示卡（:1135-1145）。
- **GitHub**：仓库链接输入框 + 随 teach/review 请求携带 `repo_url`。
- **视觉**：`shots` 仅存页面内存，**不写 localStorage**（:431 注释）。
- **聊天恢复**：`session_history` 优先（服务端真相源），localStorage 降级为显示缓存（:1000-1007）。
- **模式链**：`mode.value = adv.mode`（:1331）由后端 `mode_advice` 驱动。

**其他页面**：`ChatView`（校园问答）、`HomeView/GuidesView/AppendixView/GlossaryView/ResourceView/CalendarView/ChangelogView/FaqView/AboutView/ThanksView`（内容页）、`QuestView`（任务/成就，独立体系 `questData.ts`，与 AI 导师无关）、`RoadmapView`（发展路线图，静态数据 `roadmapData.ts`）、`LoginView/SplashScreen`（身份）。

**Store**：`chatStore`（校园问答会话，`MAX_HISTORY_ROUNDS=6`）、`settingsStore`（`xkz_settings_v1`，BYOK：provider/base_url/model/key）、`userStore`（`xkz_user`）、`themeStore`（`data-theme` = `zzz`/`ak`）、`achievementStore`、`navStore`、`uiStore`。

**【判断】**
- 前端承担了**本应由后端承担的状态**：学习进度、已通过任务、学生身份、技能字段，全部在 localStorage。这直接导致 §12 的问题（换设备即丢失）。
- `xkz_ai_api_key`（legacy）与 `settingsStore.xkz_settings_v1`（新）**双轨并存**，代码里仍读 legacy 做迁移（`:423`）。
- 前端有 **mode 链**（tutor↔reviewer）的隐式状态机，与后端的 `compute_mode_advice` 关键字规则耦合；这条链会把 `mode='reviewer'` 发给 `/api/ai/teach`，触发 §4.1 的不一致。

---

## 17. 当前系统真实能力矩阵

| 能力 | 状态 | 证据 | 完成程度 | 备注 |
|---|---|---|---|---|
| AI Chat | ✅ 已实现 | `app.py:221` `/api/ai/teach`；`store` 会话持久化；校验+重生成+纯文本兜底 | 90% | 无流式 |
| RAG | 🟡 部分实现 | 导师侧 `context_builder.py:17` + `course_data.chunks_by_section_path()`（**子串匹配**）；校园侧 `backend/retrieval.py`（完整混合检索） | 导师侧 25% / 校园侧 90% | **两套实现，导师侧无向量检索** |
| Memory | 🟡 部分实现 | `sessions.history_json` + `debug_state_json`；`summary_json` 恒 NULL（`store.py:202`） | 30% | 仅会话内短期记忆；无长期/用户/学习者记忆 |
| GitHub | 🟡 部分实现 | `code_evidence.py` 全链路（trees/contents/actions/issues） | 55% | 只读、仅默认分支、无 clone/索引/commit 快照 |
| Code Analysis | 🟡 部分实现 | `rank_candidate_files()` `:376` + `ai_relevance_filter()` `:420` + LLM 读文件 | 30% | 无 AST/静态分析 |
| Code Execution | ❌ 完全不存在 | §9 不存在性证明 | 0% | 执行外包给学生的 GitHub Actions |
| Project | ✅ 已实现 | `schemas.Project`；4 个项目 | 85% | 硬编码，无 DB |
| Task | ✅ 已实现 | `schemas.Task`；26 个任务 | 85% | 无依赖关系 |
| Rubric | ✅ 已实现 | `schemas.Rubric`；81 条，含 weight/required_evidence | 85% | 硬编码 |
| Evaluation | ✅ 已实现 | `review.compute_evaluation()`（后端算分）+ CI 直判 + 硬约束预检 + 幂等缓存 + 熔断 | 80% | 强依赖外部证据 |
| Evidence | 🔴 代码存在但未接入主流程 | `store.add_evidence/list_evidence` 存在；`app.py:54 store_evidence()` 无调用点 | 运行时 70% / 持久化 0% | Evidence Store 是空表 |
| Mastery | ❌ 完全不存在 | `SkillKey` + `Student.skills` 全仓库只有初始化 `{}` | 5% | 空壳字段 |
| Resume | ✅ 已实现 | `app.py:773` + `career.py`（零 LLM 模板） | 70% | 同项目同结果 → 无个体差异 |
| Interview | 🟡 部分实现 | `app.py:804`；`ai_generated: False`（课程作者手写） | 35% | 静态题库；无追问/无评分 |

---

## 18. 当前 AI 导师完整执行链（实例走查）

设：学生选 `course_003 / project_mcp_build / task_xxx`。

| # | 步骤 | 状态 | 代码级说明 |
|---|---|---|---|
| 1 | 学生选择一个项目 | ✅ 已实现 | `TeachView.vue:758` GET `/api/ai/config` 拉课程/项目/任务；选择结果存 `xkz_teach_sel` |
| 2 | 开始学习（发起对话） | ✅ 已实现 | POST `/api/ai/teach`（`TeachView.vue:899`），携带 `session_id/student/mode/attempt_count/api_key` |
| 3 | AI 拆解 | ✅ 已实现 | `route_behavior` 首问 → `decompose`；注入 `BEHAVIOR_PROMPTS['decompose']`，要求输出 `hint_level/hint/leading_question`（`prompts.py:78-84`） |
| 4 | 学生开发（多轮推进/调试） | ✅ 已实现 | `advance`（要求 `current_step`）/ `debug`（六段状态机 + `verify_steps`）；跨轮状态存 `debug_state_json` |
| 5 | 学生把代码推到 GitHub | 🟡 系统外 | 系统不 clone、不校验 push；只接受仓库 URL 字符串 |
| 6 | AI 读取代码 | 🟡 部分实现 | `build_code_evidence()`：若无 `Task.code_context` 则按固定优先级取 ≤10 文件、每文件 ≤120 行；仅默认分支；结果 ≤20000 字符 |
| 7 | 测试 | 🔴 不由本系统执行 | 只能读学生仓库的 GitHub Actions 结论（`fetch_ci_evidence()`）；无 CI 则此项为空 |
| 8 | 验收 | ✅ 已实现 | POST `/api/ai/review`：证据归一 → 快照 → 熔断/幂等查询 → 硬约束预检 → CI 直判 → LLM 逐条判定 → 后端聚合 score/status |
| 9 | 修复 | 🟡 部分实现 | 返回 `next_step` + 每条 `reason`；学生改完重新提交；**无"这次比上次改了什么"的对比** |
| 10 | 再次验收 | ✅ 已实现 | 证据变化 → `snapshot_hash` 变化 → 重新评审；证据不变 → 命中幂等缓存（不重复烧额度） |
| 11 | 项目完成 | 🟡 部分实现 | 单任务 `status==PASS` → 前端 `completed_tasks.push`；**无"项目级完成"判定**（无"全部任务 PASS"聚合门禁，后端无 Project 级状态） |
| 12 | 生成学习记录 | 🟡 部分实现 | 后端只有 `GET /api/ai/stats` 聚合统计（运营视角）+ 事件日志；**无面向学生的"学习记录"实体** |
| 13 | 生成简历 | ✅ 已实现 | POST `/api/career/text`（零 LLM 模板，需前端传入 results） |
| 14 | 生成面试材料 | 🟡 部分实现 | GET `/api/ai/interview`（静态题库，需该任务有作者标注） |

**【判断】** 用户设想的 14 步里：
- **完全实现（6 步）**：1、2、3、4、8、10、13（其中 4 已含推进/调试状态机）
- **部分实现（5 步）**：6、9、11、12、14
- **完全不存在（1 步）**：7（本系统执行测试）
- **系统外/人工（1 步）**：5

---

## 19. 当前架构中的问题（仅基于代码）

### 19.1 重复模块

1. **两套 RAG、两套语料读取、两套配置**：`backend/retrieval.py`（435 行，完整混合检索）与 `ai_engine/context_builder.py` + `course_data.chunks_by_section_path()`（子串匹配）读**同一个** `data/chunks.jsonl`，但不共享任何代码。→ 任一侧的改进都无法惠及另一侧。
2. **两套 BYOK 配置源**：`frontend/src/stores/settingsStore.ts`（`xkz_settings_v1`）与 `TeachView.vue:386` 的 legacy `xkz_ai_api_key`，代码仍在做 legacy 兼容读取（`:423`）。
3. **两套"技能/成就"体系**：`schemas.SkillKey` + `Task.skill`（AI 导师，未消费）与 `frontend/src/data/questData.ts` + `useQuest.ts` 的 `skills`（任务/成就页，独立体系），命名冲突且互不相通。

### 19.2 耦合

4. **课程内容与引擎代码同文件**：3 门课程 / 4 个项目 / 12 阶段 / 26 任务 / 81 Rubric 全部硬编码在 `course_data.py`(761) 与 `course03_data.py`(537) 里。**新增课程 = 改 Python + 重新部署**。
5. **任务与语料靠字符串约定耦合**：`Task.chunk_key` → `section_path` 子串匹配（`context_builder.py:20-34`）。标注缺失或 `section_path` 改名 → **教学材料静默变空**，无告警、无兜底（除了"暂无检索到教学材料"的一句提示）。
6. **前端 mode 状态机与后端关键字规则耦合**：`compute_mode_advice()`（`app.py:152`）靠 `_COMPLETION_SIGNALS` 关键词表驱动前端 `mode.value`，再把 `mode='reviewer'` 回传给 `/api/ai/teach`（见 §4.1）。
7. **`app.py` 单文件承担 4 条能力通道**（teach / review / career / interview），767 行内混有编排、错误分类、状态机推进、日志、Prompt 拼装，**无 Service 层**。

### 19.3 空壳模块

8. **`students.skills`**：`Student.skills` 与 13 项 `SkillKey` 全仓库只有初始化 `{}`（`TeachView.vue:395,1310`），无任何写入/读取。
9. **`evidence` 表 + `store.add_evidence()`**：`app.py:54` 的 `store_evidence()` 包装函数**零调用点**；`get_evidence()`（`app.py:58`）也零调用点。→ Evidence Store 从建表至今为空。
10. **`sessions.summary_json`**：字段在建表语句里，`save_session()` 恒写 `None`（`store.py:202`）。
11. **`prompts.MODE_PROMPTS["reviewer"]` + `build_system_prompt` 的 reviewer 分支**：被真实验收链绕开（真实链用 `review.build_review_system_prompt`），只在 `/api/ai/teach?mode=reviewer` 时生效，产出 `score/passed` 被 Pydantic 静默丢弃。
12. **`Task.evidence_required` 的 `"screenshot"` 取值**：枚举里保留，但 `CORE_POLICY` 铁律 6 明文"**禁止要求学生提供截图**"（`prompts.py:38`），`evidence_precheck` 也把 `visual` 列为可选增强（`review.py:196`）。→ 枚举值与策略相矛盾。

### 19.4 设计与实现不一致

13. **§4.1 的 reviewer Prompt 双份且语义相反**（一份要求出 score，一份禁止出 score）。
14. **§1.3 的部署配置**：仓库 `xkz-agent.conf` 无 `/api/ai/` 反代，线上是否有仅靠 `BUG_REPORT.md` 声称。
15. **Vite dev proxy 的 `/api` → 8099**（`vite.config.ts:19-22`）：这条规则会把校园站的 `/api/ask`、`/api/verify` 也指向 8099 引擎，而引擎没有这些路由。→ **开发环境下校园问答不可用**（生产因 Nginx 不同而正常）。
16. **学习进度无服务端真相源**：`session_history` 注释说 SQLite 是"真相源"（`app.py:483-485`），但**进度**（completed_tasks）只在 localStorage；即"对话有真相源，进度没有"。
17. **`TeachRequest` 默认值过期**：`project_id: str = "project_xie_xiu"`（`schemas.py:363`），但 `_PROJECT_BUILDERS` 里只有 `project_chatbot / project_agent`（`course_data.py:684-686`）+ course03 的 2 个。→ 默认值指向一个不存在的项目。

### 19.5 技术债务 / 瓶颈

18. **无 token/cost 记账**：BYOK 模式下学生自付，系统不记录用量（§5）。
19. **历史窗口硬截断**：`history[-12:]` + `_trim(6000)`，无摘要 → 长任务对话会丢失早期关键上下文（§7）。
20. **全量语料加载**：`course_data.load_chunks()` 用 `lru_cache` 全量读 `chunks.jsonl` 进内存（`course_data.py:35`）；`backend/retrieval.py` 还额外常驻 `embedding_cache.npy`。→ 语料增长后内存线性上升（服务器仅 1.8G，已因 OOM 禁用 reranker）。
21. **SQLite 单进程单写连接**（`store.py:68`）：`uvicorn` 单 worker 下可用，但**无法水平扩容**；一旦多 worker/多实例，`review_results` 幂等性与 `sessions` 一致性都会出问题。
22. **`review_results` 版本常量需人工 bump**（`store.py:29-32`）：改了 Rubric 或 Prompt 却忘记改版本号 → 学生拿到**旧规则的缓存评审结果**（静默错误）。
23. **无 CI/CD 与容器化**：仓库无 Dockerfile、无 GitHub Actions、无 pm2 配置；部署依赖人工 scp（`BUG_REPORT.md` 印证）。
24. **测试资产是脚本不是测试**：`_test_phase1..8.py`、`_test_evidence.py`、`_test_v11_fix.py` 是自定义断言脚本（`_test_phase2.py:160` 形如 `check(...)`），**无 pytest 结构、无 CI 执行**。

### 19.6 最影响项目价值的缺口（判断）

按"对'项目制 AI 导师'这个产品主张的伤害程度"排序：

1. **Learner Model 完全缺失**（§12）——没有掌握度，就没有"因材施教"、"弱项识别"、"复习"、"个性化路径"。这三个词目前都无法在代码里找到对应实现。
2. **Submission / Evidence 不落库**（§10、§14）——没有提交历史，就无法做"我上次改了什么"、"这门课我一共提交了多少次"、"我的证据档案"，也无法支撑项目复盘。
3. **没有项目级完成判定与门禁**（§10）——只有任务级 PASS，没有"项目是否完成"的聚合与约束，产品叙事上"完成一个项目"没有代码支撑。
4. **没有代码执行能力**（§9）——"AI 导师能验证你的项目真的跑起来了"这一主张，实际是"借用学生自己的 CI"。

---

## 20. 与"项目制 AI 导师"目标的差距

目标架构（用户给定）：`Project → Milestone → Task → Student Submission → Evidence → Evaluation → Revision → Acceptance → Learner Model → Resume / Interview`

| 层 | 当前支持程度 | 证据 |
|---|---|---|
| Project | ✅ 完整 | `schemas.Project` + 4 个硬编码项目 |
| Milestone | ✅ 完整 | `schemas.Stage` + 12 个阶段（含 `order`/`objective`） |
| Task | ✅ 完整 | `schemas.Task` + 26 个任务（含 objective/steps/code_context/skill） |
| Student Submission | 🟡 部分 | `schemas.Submission` 存在，**不落库**；仅 review 请求体内临时使用 |
| Evidence | 🟡 部分 | 运行时归一完整（9 类，含 CI/report/issue/trace/visual）；**持久化表未接入**；快照哈希可复现 |
| Evaluation | ✅ 完整 | 后端聚合 + CI 直判 + 硬约束 + 幂等 + 熔断 + 错误隔离 |
| Revision | 🟡 部分 | 有 `next_step` 与 `attempt_count`；**无版本、无 diff、无修订历史** |
| Acceptance | 🟡 部分 | 任务级 PASS 严格可判；**无项目级完成聚合、无门禁阻断** |
| Learner Model | ❌ 缺失 | §12：`skills` 空壳、无知识点、无弱项、无复习 |
| Resume / Interview | 🟡 部分 | Resume ✅（但模板化、同质化）；Interview 🟡（静态题库，无追问/评分） |

**【判断】** 这条链在前 4 层（Project→Milestone→Task）是**真实落地**的，中段（Submission→Evidence→Evaluation）**有一条可跑的窄通路但不持久**，后段（Acceptance→Learner Model→Resume/Interview）**要么缺聚合、要么缺实体**。若要补齐，缺口从大到小是：**Learner Model > Submission/Evidence 持久化 > 项目级 Acceptance 聚合 > Revision 版本化**。

---

## 21. 可以被 DeepTutor 替代的模块（假定采用 DeepTutor 为底座）

> 说明：本节**不评价 DeepTutor 本身**，仅按"当前项目这部分代码是否是可被通用底座覆盖的通用能力"给出 A/B/C/D 分级。
> A = 可直接替代（通用能力，无本项目特定语义）
> B = 可通过 Adapter 接入（接口能对上，需写适配层）
> C = 不应该替代（替换会丢掉本项目核心语义，或风险大于收益）
> D = 当前项目特有（通用底座不提供，必须自留）

| 模块 | 分级 | 理由（基于当前代码） |
|---|---|---|
| Agent Runtime | **A** | 本项目**没有** Agent Runtime（`app.py:221/494` 是过程式函数，无循环/无规划/无工具）。引入 DeepTutor 的 runtime 是"从 0 到 1"，替换成本≈0。 |
| Tool Registry | **A** | 本项目没有 Tool Registry（`llm_client.py:177-185` 无 `tools` 字段）。完全空缺，可直接用底座能力。 |
| RAG | **B**（导师侧）/ **A**（校园侧） | 导师侧是 `chunk_key` 定向切片，语义特定的地方只在"课程作者标注哪节该读"；检索机制本身是通用的（子串匹配），可由底座的检索替换（B）。校园侧 `backend/retrieval.py` 是完整通用混合检索，也属通用能力（A），但它是**另一个应用**，与导师引擎无关。 |
| Memory | **A** | 本项目只有 `sessions.history_json`（原始对话数组）+ `debug_state_json`。若底座提供 L1/L2/L3 记忆，本项目的"记忆"可直接被吸收。 |
| Session | **B** | `sessions` 表与 `session_key = session_id:task_id` 语义很薄（会话即"学生×任务"），可用 Adapter 映射到底座会话（B）。唯一需要保留的是 `debug_state` / `last_system_error` 的语义。 |
| Knowledge Base | **A** | 26 篇语料 + `docs_manifest.csv` 是**纯数据**，与实现解耦，直接迁移即可。 |
| GitHub | **B** | 通用部分（trees / contents / actions / issues 拉取）底座可能已覆盖；但**本项目特有的语义**是"哪些文件算关键证据"（`_KEY_REPORT` 优先级、`_lines_cap_for`、报告类文件打标 `_REPORT_TAG`）以及"CI 直接映射 Rubric"——这些要作为 Adapter 逻辑保留。 |
| Sandbox | **A** | 本项目**完全没有** Sandbox。若底座提供执行能力，是净增，无替换成本。但注意：**引入执行会改变验收语义**（从"CI 权威"变成"自执行"，需重新设计证据可信度）。 |
| Learning Path | **C** | 本项目"路径"不是算法，而是**课程作者编排的 Stage/Task 顺序**。用底座的自适应路径替换会破坏课程设计意图。应为 C（可考虑 Hybrid：底座提供推荐，课程顺序仍然权威）。 |
| Mastery | **B** | 本项目 Mastery 是空壳（`Student.skills`），但**数据标注已就绪**（`Task.skill` + 13 项 `SkillKey`）。用底座 Mastery 需先把标注映射过去 → B（Adapter）。 |
| Quiz | **A** | 本项目无 Quiz / 无题库 / 无判题（只有静态 `InterviewQuestion`，且明确"不判分"）。完全空缺，可直接替代。 |
| MCP | **D** | 本项目**引擎不使用 MCP**；MCP 只作为课程 03 的**教学内容**（`course03_data.py:9`、`docs/课程03-素材/starter/server.py`）。这部分属"课程内容资产"，与底座能力无关，不应替代。 |
| Subagent | **A** | 本项目无 Subagent / 无 Handoff。完全空缺。 |

---

## 22. 本项目真正不可替代的核心

**【事实·逐个核实"是否真的拥有"】**

| 能力 | 是否真实拥有 | 代码依据 | 性质 |
|---|---|---|---|
| **Rubric-driven 逐条验收 + 后端算分** | ✅ 真实拥有 | `review.py:230 compute_evaluation()`、`app.py:691-705`（LLM 只出 criteria，score/status 由代码聚合） | **领域资产** |
| **CI 结论直判（system 权威证据绕过 LLM）** | ✅ 真实拥有 | `review.py:272 ci_direct_verdict()`；`code_evidence.py:307 fetch_ci_evidence()` | **领域资产（较独特）** |
| **证据优先 + 硬约束预检（缺证据强制 NEED_REVIEW，零 LLM）** | ✅ 真实拥有 | `review.py:177 evidence_precheck()`、`app.py:624-655` | **领域资产** |
| **提示等级 + 角色/行为分离的"不替学生做"约束** | ✅ 真实拥有 | `prompts.py:16-23,78-100`、`response_validator.py`、`hint.py` | **领域资产** |
| **"只认交付不认学习"的简历过滤规则** | ✅ 真实拥有 | `career.py:32-56 _LEARNING_MARKERS/_DELIVERY_MARKERS` | **领域资产（小但有观点）** |
| **系统错误隔离（错误永不污染学生评价）** | ✅ 真实拥有 | `app.py:98-125,344-350`、`prompts.py:39` 铁律 7 | **工程资产** |
| **JSON 四级容错链 + 纯文本兜底** | ✅ 真实拥有 | `llm_client.py:73/107/132`、`app.py:353-375` | **工程资产（通用性强）** |
| **幂等评审缓存 + 失败熔断（保护学生 BYOK 额度）** | ✅ 真实拥有 | `store.py:232-277`、`app.py:588-601` | **工程资产** |
| **Debugger 六段状态机（软）** | 🟡 拥有但不坚硬 | `app.py:128-143`、`schemas.DebugPhase` | 领域资产（实现偏弱） |
| **课程内容本身（3 课 / 4 项目 / 26 任务 / 81 Rubric / 面试题 / 简历素材）** | ✅ 真实拥有 | `course_data.py`、`course03_data.py`（约 1298 行硬编码数据） | **内容资产（真正的护城河候选）** |
| **校园 RAG 混合检索** | ✅ 真实拥有（另一个应用） | `backend/retrieval.py` + `backend/embedding.py` | 通用能力（非独特） |
| **Agent / Tool / Sandbox / MCP / Subagent** | ❌ 不拥有 | §4、§9、§21 | 空白 |

**【判断·逐类归位】**

- **真正拥有的、且属于领域语义（可形成壁垒）**：
  1. **"证据 → 逐条 Rubric → 后端聚合"的验收协议**（含 CI 直判、硬约束预检、错误隔离、幂等熔断）。它把"AI 评价学生作品"这个不确定过程，改写为"**先证据齐备、再逐条判定、由代码定分**"的可复现过程。这套协议是代码里真实存在的、且与"项目制教学"的场景强绑定的。
  2. **"不替学生做"的约束体系**（Hint 0-5 + 行为路由 + `response_validator` 的 5 类违规检测）。
  3. **课程内容资产**：1298 行硬编码的课程/任务/Rubric/面试题/简历素材——这是**人工教学设计**，不是通用 AI 能力，也是任何底座都替代不了的部分。
- **只是普通 AI 应用能力**（不具备壁垒）：JSON 容错、LLM 调用封装、SSE 问答、SEO 注入、混合检索、前端展示。
- **可能形成长期产品壁垒的**：第 1 点（验收协议）+ 第 3 点（课程内容），**前提是先把 §19.6 的三个缺口补上**（Learner Model / 提交落库 / 项目级门禁）。否则"验收协议"只停在一个任务的闭环上，无法沉淀为学生成长档案。
- **目前只是产品设想、尚未落地**（禁止说"有潜力"）：
  - ❌ "因材施教 / 个性化学习路径"——无 Learner Model，无推荐算法。
  - ❌ "技能掌握度 / 弱项识别 / 复习机制"——`skills` 空壳。
  - ❌ "AI 验证你的项目真的跑起来了"——无执行能力，依赖学生自己的 CI。
  - ❌ "项目复盘 / 迭代演进"——无提交历史、无 diff。
  - ❌ "AI 生成简历 / AI 生成面试题"——两者都是**零 LLM 的模板/静态内容**，与"AI 生成"无关。

---

## 23. 最终结论

**1. 当前项目如果从零开始，是否值得继续独立开发？**

**【判断】** 值得，但**理由不是"架构先进"，而是"内容 + 验收协议"这两项真实资产**。代码层面的架构是"过程式脚本 + 硬编码数据 + 单进程 SQLite"，任何一个有经验的工程师都能重写；但 `course_data.py` / `course03_data.py` 里 1298 行人工教学设计与 `review.py` 里那套证据驱动的验收协议，是**重写成本很高、且需要教学经验才能产出**的东西。
同时必须承认：如果从零开始，**没有任何理由重复开发 Agent / Tool / Sandbox / MCP / Memory 这些本项目根本没用上的东西**（现在也确实没开发，这是优点）。

**2. DeepTutor 是否可以直接替代当前项目？**

**【判断】** **不能直接替代。**
- DeepTutor 一类底座能覆盖的是本项目的**空集**（§21 里全是 A/B：Agent Runtime、Tool Registry、Memory、Quiz、Sandbox 等本项目本就没有）。
- 本项目的**核心差异化部分（Rubric 逐条验收协议、CI 直判、课程内容、简历过滤规则）在底座里没有对应物**，属 C/D。
- 更关键的是：本项目的两个"真正被使用"的能力恰恰都在**通用底座之外**——一是"课程作者编排好的任务与 Rubric"，二是"把学生的 GitHub 产出当作证据来判"。所以答案是"**底座可换掉外壳，换不掉内核**"。

**3. 哪些模块应该停止重复开发？**

**【判断】** 基于代码现状，以下模块**不应再投入**（它们本就不存在，不要为了"看起来完整"去补）：
- 自建 Agent Runtime / Tool Registry / Subagent / Handoff；
- 自建 Sandbox / 代码执行（若需要，走"借学生 CI + 底座执行"两条外部路径，不要自建）；
- 自建 MCP client（MCP 在本项目里是**教学内容**，不是运行时能力）；
- 自建通用 Vector DB / 检索引擎（校园侧已有一套够用的 `backend/retrieval.py`，导师侧根本不需要向量检索）；
- 自建长文本 Memory/摘要（`summary_json` 字段留着但不写，是正确决定；不要为了填字段去写一个劣质的摘要器）。

**4. 如果采用 DeepTutor 作为底座，当前项目应该保留什么？**

**【判断】** 按"必须保留 / 可适配 / 可丢弃"三档：

- **必须原样保留（C/D 类）**：
  1. `ai_engine/review.py` 整条验收协议（`evidence_precheck` / `ci_direct_verdict` / `compute_evaluation` / `build_review_system_prompt`）；
  2. `ai_engine/course_data.py` + `course03_data.py` 全部课程内容（含 Rubric、`code_context`、`interview_questions`、`resume_points`）；
  3. `ai_engine/career.py` 的简历过滤规则；
  4. `ai_engine/prompts.py` 的"不替学生做"约束体系（Hint 表 + 行为 Prompt）+ `response_validator.py`；
  5. `ai_engine/app.py` 的**系统错误隔离**与**错误分类漏斗**（`llm_error_response`）。
- **可通过 Adapter 接入（B 类）**：
  6. Session 语义（`session_id:task_id` + `debug_state` + `last_system_error`）→ 映射到底座会话；
  7. `Task.skill` + `SkillKey` 标注 → 映射到底座 Mastery 的输入；
  8. GitHub 证据的"关键文件优先级"与"报告类文件打标"逻辑 → 作为底座的 evidence adapter。
- **可以丢弃（A 类）**：
  9. `chunks_by_section_path()` 子串检索（换成底座检索，但**必须保留 `Task.chunk_key` 这个人工标注**）；
  10. `store.py` 的 `sessions` / `review_results` / `review_failures`（幂等与熔断是通用的，但注意：**幂等语义必须在新底座上重新实现**，不能假设底座自带）；
  11. `logs.py` 的 JSONL 日志与 `stats` 聚合。

---

## 24. 文件索引（本报告引用过的关键文件）

> 相对仓库根 `tralis/xkz-agent/`。按"另一个 AI 继续深挖"的优先顺序排列。

**AI 导师引擎 — 核心（必读）**

| 路径 | 作用 | 本报告涉及章节 |
|---|---|---|
| `ai_engine/app.py` | 引擎主入口：全部 HTTP 端点 + teach/review 编排 + 错误分类漏斗 + 调试状态推进 + mode 建议 | §1,§4,§5,§8,§10,§11,§15,§18 |
| `ai_engine/review.py` | 验收链：证据收集 / 硬约束预检 / CI 直判 / 后端聚合 / 验收 System Prompt | §1,§11,§20,§22 |
| `ai_engine/code_evidence.py` | GitHub 证据管线：trees/contents/actions/issues + Task-aware 代码检索 | §8,§11,§21 |
| `ai_engine/schemas.py` | 全部 Pydantic 数据模型（含 `ReviewLLMOutput` 无 score/status 的设计） | §4.1,§10,§12,§14 |
| `ai_engine/store.py` | SQLite：4 张表 + 幂等缓存 + 失败熔断 + 版本化 key + 惰性清理 | §7,§11,§14,§19 |
| `ai_engine/llm_client.py` | LLM 调用 / JSON 四级容错 / 语义校验 / 截断重生成 / 纯文本兜底 / 行为级 max_tokens | §5,§5.1 |
| `ai_engine/prompts.py` | CORE_POLICY + MODE_PROMPTS（**含 reviewer 遗留矛盾**）+ BEHAVIOR_PROMPTS + `route_behavior` + system prompt 组装 | §4,§4.1,§19.3 |
| `ai_engine/context_builder.py` | 教学上下文组装（`chunk_key` → `section_path` 子串匹配，**非向量检索**） | §6.1,§19.2 |
| `ai_engine/course_data.py` | 课程/项目/阶段/任务/Rubric 硬编码数据 + 检索封装（761 行） | §2,§3,§10,§14,§22 |
| `ai_engine/course03_data.py` | 课程 03（MCP）项目数据（537 行，含 MCP 教学素材） | §3,§21 |
| `ai_engine/vision.py` | 运行截图视觉证据（白名单 + fail-open + 不落盘） | §5,§11 |
| `ai_engine/career.py` | 简历文本生成（零 LLM，学习属性过滤） | §13.1,§22 |
| `ai_engine/response_validator.py` | AI 输出质量校验（5 类关键词规则） | §4,§22 |
| `ai_engine/hint.py` | Hint Level 0-5 推导 | §4,§22 |
| `ai_engine/logs.py` | JSONL 事件日志 + `compute_stats()` 聚合 | §3,§5,§12 |
| `ai_engine/requirements.txt` | 引擎依赖（可验证"无 langchain/无沙箱 SDK"） | §1,§9 |
| `ai_engine/_test_phase1..8.py`、`_test_evidence.py`、`_test_v11_fix.py` | 自定义断言测试脚本（非 pytest） | §19.5 |
| `ai_engine/BUG_REPORT.md`、`PROJECT_OVERVIEW.md` | **自述文档**：仅用于印证"仓库配置与线上不一致" | §0.3,§1.3 |

**校园问答站（另一个应用）**

| 路径 | 作用 | 章节 |
|---|---|---|
| `backend/main.py` | 校园问答 API（`/api/ask` SSE）+ SEO/JSON-LD 注入 + SPA 404 | §1,§15.2 |
| `backend/retrieval.py` | 完整混合检索：5 路召回 + RRF 融合 + 意图加权 + 重排 | §6.2,§21 |
| `backend/embedding.py` | bge-small-zh-v1.5 嵌入 + bge-reranker-base（默认关闭） | §1,§5,§6.2 |
| `backend/config.py` | 环境变量配置 + 校园问答 Prompt + 多 Provider 预设 | §1,§5,§6.2 |
| `backend/ratelimit.py` | 限流 | §1 |

**数据 / 脚本 / 部署**

| 路径 | 作用 | 章节 |
|---|---|---|
| `data/chunks.jsonl` | RAG 语料（两套检索共用） | §6.1,§14.3 |
| `data/docs_manifest.csv` | 26 篇文档元数据（id/标题/类别/URL/子类别） | §2,§6.1 |
| `data/engine.db` | SQLite 实例（sessions/review_results/review_failures/evidence） | §14.1 |
| `data/logs/session_events.jsonl` | 结构化事件日志 | §3,§5 |
| `scripts/chunker.py` | 知识库分块器 v3（600/30/80 + 标题层级 + 重叠） | §6.1 |
| `xkz-agent.conf` | Nginx 配置（**无 `/api/ai/` 反代 → 与线上不一致**） | §0.3,§1.3,§19.4 |
| `frontend/vite.config.ts` | dev proxy（`/api/ai`→8099、`/api`→8099） | §1.3,§19.4 |

**前端（AI 导师相关）**

| 路径 | 作用 | 章节 |
|---|---|---|
| `frontend/src/views/TeachView.vue` | AI 导师全部 UI + 状态 + 8 个 API 调用 + localStorage 键 | §16,§12,§19 |
| `frontend/src/router/index.ts` | 16 条路由 | §16 |
| `frontend/src/stores/settingsStore.ts` | BYOK 配置（`xkz_settings_v1`） | §5,§16,§19.1 |
| `frontend/src/stores/chatStore.ts` | 校园问答会话（`MAX_HISTORY_ROUNDS=6`） | §16 |
| `frontend/src/data/questData.ts`、`composables/useQuest.ts` | 独立的"任务/成就/技能"体系（与 `SkillKey` 同名不同源） | §19.1 |

---

## 附录 A：五态汇总速查

**❌ 完全不存在**：Agent Framework、Tool Registry / Tool Calling、Subagent / Handoff、Sandbox / Code Execution、消息队列、Redis/Celery、Vector DB、MCP（运行时）、Learner Model / Mastery / 知识点 / 弱项识别 / 复习、Knowledge Point、Quiz / 题库 / 自动判题、项目复盘、提交版本 diff、跨项目合并简历、Token/Cost 记账、Gantt/依赖图、容器化、CI/CD 流水线。

**🔴 代码存在但未接入主流程**：`evidence` 表 + `store.add_evidence()`（`app.py:54` 零调用）；`sessions.summary_json`（恒 NULL）；`prompts.MODE_PROMPTS["reviewer"]` + `build_system_prompt` reviewer 分支（被 `review.build_review_system_prompt` 绕开）；`Task.evidence_required` 的 `"screenshot"` 取值（与铁律 6 冲突）。

**⏳ 预留未实现**：`Student.skills`（有初始化无写入）；`summary_json`（有列无值）；`SkillKey` 聚合逻辑。

**🟡 部分实现**：RAG（导师侧子串匹配 / 校园侧混合检索）、Memory（仅会话内）、GitHub（只读 + 仅默认分支 + 无索引）、Code Analysis（无 AST）、Submission（不落库）、Revision（无版本）、Acceptance（无项目级聚合）、Interview（静态题库）、Progress（localStorage）、Monitoring（仅 stats/health）。

**✅ 已实现**：`/api/ai/teach` 全链路、`/api/ai/review` 验收协议（硬约束 + CI 直判 + 后端算分 + 幂等 + 熔断 + 错误隔离）、Session 持久化、Debug 六段状态机、Hint 0-5、简历模板生成、事件日志、课程/项目/阶段/任务/Rubric 数据体系、校园 RAG 问答、SEO/JSON-LD 注入。