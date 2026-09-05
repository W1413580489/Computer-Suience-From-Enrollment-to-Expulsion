# 课程 02《GitHub 项目分析 Agent》内容草稿 V2

## 本文档怎么用（三种去向）

| 本文的哪部分 | 去哪里 |
|---|---|
| **学生前置教程**（Token 申请） | 独立文档《course02-前置教程-GitHubToken申请》，发飞书/攻略页，学生先读再做 |
| 各任务的目标/步骤/提示策略/CodeContext/Rubric | 转录为 `course_data.py` 课程数据（T01-T09） |
| 各任务的**教材章节**（每个任务标 chunk_key） | `data/raw/course02_github_agent.md` → chunker → AI 检索材料 |

> 全文通用约定：成品为 **CLI 应用**；报告输出 `report.md`；LLM 兼容 OpenAI 接口（默认示例 DeepSeek，学生可换其他 OpenAI 兼容 API，验收一律写「所选 LLM API」）；前置假设：学生已完成《套壳聊天机器人》课（会 Python/FastAPI/httpx/uvicorn/CORS、Git 基础、BYOK）。

### Trace 输出约定（全课统一，T02 起生效）

CLI 支持 `--trace`，输出 `agent_trace.json`，每步记录 6 个字段：
`step`（第几步）/ `tool_name`（调用了哪个工具）/ `arguments`（参数）/ `result_summary`（结果摘要，别塞全文）/ `timestamp` / 结束时追加 `stop_reason`（`completed` / `max_steps_reached` / `error`）。

验收链靠它**客观判断"Agent 是否真的自主调用工具并循环"**——这不是可选项，是整门课的验收核心。

---

# Stage 1 认识 Agent

> **本阶段一句话**：让学生从"一问一答的聊天机器人"跨到"能动手调用工具的 Agent"，先体会差别，再做出第一个最小闭环。
> 前置：学生能讲清聊天机器人前后端数据流。
> **课程第一天动作**：发放前置教程飞书链接（https://tralis2671.feishu.cn/wiki/Urq6w7wOiiAFe4kzGnmciPxYnCd ），要求学生在开始 T01 前完成 Token 申请并配置 `.env`。

## T01 Agent 与聊天机器人的区别 + 项目骨架

- **chunk_key**：`course02_github_agent/task01_agent_intro` ｜ Skill：ai_assisted
- **完成标准**：项目骨架能跑（CLI 问候）；学生能说清两条区别；`.env` 配好且源码无硬编码 Key。
- **objective**：搭好项目骨架（`agent.py` / `tools.py` / `.env` / `requirements.txt`），CLI 能运行打印问候，并能说清 Agent 与聊天机器人的区别。
- **steps**：
  1. 建文件夹 + 虚拟环境，装 `openai`、`httpx`、`python-dotenv`
  2. `.env` 放所选 LLM 的 Key（沿用上一课的 BYOK 习惯）
  3. 写 `agent.py`：读输入 → 调 LLM → 打印回答（把上一课后端逻辑搬进 CLI）
  4. 按《前置教程：申请 GitHub Token》（飞书链接见上）申请 Token 并配置 `.env`（课程第一天就完成，后续任务不再卡这里）
- **卡住怎么办（L0-L5）**：
  - L0-L1 只反问/点方向："你觉得聊天机器人和 Agent 差在哪一步？""差在能不能'动手做事'"。
  - L2 给三点区别的思考框架（工具 / 多步 / 自主决策）。
  - L3 给项目骨架的文件清单，不给内容。
  - L4 给 `agent.py` 骨架代码（不含密钥读取细节）。
  - L5 给可直接运行的完整最小文件。
- **代码检索线索**：keywords `agent, openai, deepseek, dotenv, cli` ｜ likelyFiles `agent, main` ｜ searchPatterns `OpenAI\(, chat\.completions`
- **Rubric**：
  1. 骨架齐全且 CLI 可运行（证据：代码｜可运行打印问候｜w2）
  2. 说清 ≥2 条区别（证据：描述｜自述含"工具/多步/自主"｜w1）
  3. 源码无硬编码 Key（证据：代码｜grep 无明文｜w2）
- **CI**：无（概念+环境任务）

## T02 最小 Agent Loop（单工具）

- **chunk_key**：`course02_github_agent/task02_minimal_loop` ｜ Skill：workflow
- **完成标准**：内置工具（如 `get_current_time`）走完"模型决定调用 → 执行 → 结果回传 → 模型回答"闭环；trace 文件开始留档。
- **objective**：用 `tools` 参数声明一个工具，实现最小闭环，理解这就是 Agent Loop。
- **steps**：
  1. 用 `tools` 参数向所选 LLM 声明工具的 JSON Schema
  2. 检查响应的 `tool_calls`：无 → 直接回答结束；有 → 下一步
  3. 执行工具，结果以 `role=tool` 消息回传
  4. 再次调用模型取最终回答；打印每次对话轮次；加 `--trace`
- **卡住怎么办（L0-L5）**：L0-L1 "模型自己知道现在几点吗？"→点出"给它工具、让它开口要"；L2 给四步闭环图；L3 给 `tools` 参数结构与 `tool_calls` 字段说明；L4 给单次工具调用关键代码；L5 给完整可运行 Loop。
- **代码检索线索**：keywords `tool_calls, tools, function, loop, role` ｜ likelyFiles `agent` ｜ searchPatterns `tool_calls, tools\s*=, role.*tool`
- **Rubric**：
  1. 工具以 Schema 声明且被模型接收（证据：代码｜`tools` 参数存在｜w2）
  2. 结果回传逻辑存在（证据：代码｜`role=tool`｜w2）
  3. 演示一次完整闭环（证据：运行｜问时间得到正确回答｜w2）
  4. 能解释"为什么结果要回传而不是直接打印"（证据：描述｜w1）
- **CI**：无（首次接触 Loop，真人演示）；Trace 从本任务开始输出

---

# Stage 2 接入 GitHub 工具

> **本阶段一句话**：给 Agent 装三件套——会带 Token 调 GitHub、能看仓库信息/文件树、能读关键文件，且每件都带单测。
> 前置：T02 的 Loop 骨架可跑；学生已读完前置教程并拿到 Token。

## T03 GitHub API Client（Token / 限流 / 错误处理）

- **chunk_key**：`course02_github_agent/task03_github_client` ｜ Skill：project_dev
- **完成标准**：一个带 Token、能区分 401/403/404、限流会退避一次重试的 Client；Token 不进源码。
- **objective**：封装 `GitHubClient`：自动带 Token 请求头；区分 401/403+限流/404；限流按 `Retry-After` 退避一次重试；错误结构化返回，不静默吞掉。
- **steps**：1. 建 `github_client.py` 封装 `get()`，自动加 `Authorization: Bearer` → 2. 区分 401（Token 错）/ 403+`X-RateLimit-Remaining:0`（限流→退避重试一次）/ 404（不存在）→ 3. 返回 `{"ok":false,"code":...,"error":...}` → 4. 写 3 个单测（mock HTTP 响应）。
- **卡住怎么办（L0-L5）**：L0-L1 "上一课 403 你怎么处理的？"→"响应头里其实写着余量"；L2 给三分支处理框架；L3 给退避重试伪代码；L4 给带 mock 的单测示例；L5 给完整 Client。
- **代码检索线索**：keywords `github, token, rate, 403, authorization, retry` ｜ likelyFiles `github_client, api_client, github` ｜ searchPatterns `Authorization, X-RateLimit, 403, retry`
- **Rubric**：
  1. Token 从环境变量读，源码与提交无硬编码（证据：代码+CI｜grep 检查｜w2）
  2. 401/403/404 三分支有区分、信息可读（证据：代码+CI｜单测覆盖｜w2）
  3. 限流退避且不无限重试（证据：代码+CI｜mock 限流响应单测｜w2）
  4. 能说清 Token 泄露风险与补救（证据：描述｜自述含 Revoke｜w1）
- **CI**：✓（pytest mock 三分支+退避）

## T04 仓库信息 + 文件树工具

- **chunk_key**：`course02_github_agent/task04_repo_tools` ｜ Skill：project_dev
- **完成标准**：两个只读工具 `get_repo_info` / `get_file_tree`，走统一 Client，输出 Agent 可读文本，文件树有截断保护。
- **objective**：基于 Client 实现 `get_repo_info`（语言/star/描述/默认分支）与 `get_file_tree`（递归树，取文件、过滤目录、前 200 项截断）。
- **steps**：1. `get_repo_info` → `/repos/{owner}/{repo}` 抽关键字段 → 2. `get_file_tree` → `/git/trees/{branch}?recursive=1`，只留文件、超 200 截断并注明 → 3. 各写 1-2 个单测。
- **卡住怎么办（L0-L5）**：L0-L1 "分析仓库先想知道什么？"→"元信息 + 长什么样"；L2 给两工具输入输出设计；L3 给 REST 端点和关键字段名；L4 给其中一个实现；L5 给两个完整实现。
- **代码检索线索**：keywords `repos, git/trees, file tree, repo info` ｜ likelyFiles `tools, github_client` ｜ searchPatterns `repos/, git/trees, def get_repo, def get_file_tree`
- **Rubric**：
  1. 两工具经统一 Client（证据：代码｜不裸调 httpx｜w2）
  2. 文件树有截断保护（证据：代码+CI｜单测超长列表｜w2）
  3. 对真实公开仓库可取回数据（证据：运行｜演示输出｜w1）
- **CI**：✓（mock 单测）

## T05 文件内容工具 + 大小保护

- **chunk_key**：`course02_github_agent/task05_content_tool` ｜ Skill：project_dev
- **完成标准**：`get_file_content` 能读文件、超 200 行截断、对二进制/空/不存在给友好提示。
- **objective**：实现 `get_file_content(owner/repo, path)`：Contents API 拉取 → base64 解码 → 超行数截断标注 → 异常（不存在/二进制/空）给友好返回。
- **steps**：1. Contents API + base64 解码 → 2. 截断逻辑 + "已截断"标注 → 3. 三条异常路径 → 4. 单测覆盖 正常/截断/不存在。
- **卡住怎么办（L0-L5）**：L0-L1 "5 万行全塞给模型会怎样？"→"上下文是有限资源"；L2 给截断策略；L3 给 Contents API 与 base64 要点；L4 给截断函数代码；L5 给完整实现。
- **代码检索线索**：keywords `contents, base64, truncate, file content` ｜ likelyFiles `tools` ｜ searchPatterns `contents/, b64decode, truncat`
- **Rubric**：
  1. 工具可用且经统一 Client（证据：代码｜w2）
  2. 截断与异常路径齐全（证据：代码+CI｜三条路径单测｜w2）
  3. 能说清"为什么截断"（证据：描述｜提到上下文有限｜w1）
- **CI**：✓（三条路径）

---

# Stage 3 工具驱动执行

> **本阶段一句话**：把"会三件工具"升级成"会自己用工具干活"——注册表让模型选对工具、结果驱动它连续调用、出问题能安全停下。
> 前置：三个工具可用且带单测；Loop 骨架存在。

## T06 工具注册与 Schema

- **chunk_key**：`course02_github_agent/task06_tool_registry` ｜ Skill：workflow
- **完成标准**：三个工具全经注册表暴露；三类提问均选对工具；新增工具只改一处。
- **objective**：建统一注册表（`TOOL_MAP` + Schema 列表），Loop 只认注册表。
- **steps**：1. 每个工具写规范 Schema（名称/用途描述——**描述是写给模型看的**/参数）→ 2. 建注册表 → 3. 用三类提问（"什么语言"/"文件结构"/"看 main.py"）验证选对工具。
- **卡住怎么办（L0-L5）**：L0-L1 "模型怎么知道你有哪些工具？"→"描述是它的眼睛"；L2 给注册表结构；L3 给一个工具完整 Schema 示例；L4 给注册表代码；L5 给完整注册表。
- **代码检索线索**：keywords `tool map, schema, register, description` ｜ likelyFiles `tools, agent` ｜ searchPatterns `TOOL_MAP, "type": "function", description`
- **Rubric**：
  1. 三工具全经注册表（证据：代码｜无散落硬编码｜w2）
  2. 描述清晰、三类提问均选对（证据：运行+Trace｜三次演示｜w2）
  3. 能说清"新增一个工具要做几步"（证据：描述｜w1）
- **CI**：无（行为靠 Trace 验证）；三次演示 Trace 留档

## T07 多步 Agent Loop

- **chunk_key**：`course02_github_agent/task07_multi_step` ｜ Skill：workflow
- **完成标准**：一次复杂分析出现 ≥2 次连续工具调用，且后续调用依赖前序结果；trace 完整。
- **objective**：Loop 升级为 `while`：有 `tool_calls` 就执行回传继续，直到模型认为信息足够才输出最终回答。
- **steps**：1. 单次改循环（有 tool_calls 就回传继续）→ 2. 每步写 trace（6 字段）→ 3. 用"分析 XX 仓库结构"类任务演示多步行为。
- **卡住怎么办（L0-L5）**：L0-L1 "看结构要先信息→树→内容，一次够吗？"→"结果喂回去让它接着想"；L2 给循环状态图；L3 给循环改造要点；L4 给 trace 写入代码；L5 给完整多步 Loop。
- **代码检索线索**：keywords `while, multi step, trace, tool_calls` ｜ likelyFiles `agent` ｜ searchPatterns `while, tool_calls, trace`
- **Rubric**：
  1. 复杂任务出现 ≥2 次连续调用（证据：Trace｜w2）
  2. 后续调用依赖前序结果（证据：Trace｜参数与上一步相关｜w2）
  3. trace 字段符合约定（证据：代码+运行｜agent_trace.json｜w2）
  4. 能讲清多步 vs 一问一答的本质（证据：描述｜w1）
- **CI**：无（依赖真实 LLM 行为；trace 写入函数归 T08 测）

## T08 max_steps 与安全退出

- **chunk_key**：`course02_github_agent/task08_safety` ｜ Skill：workflow
- **完成标准**：`max_steps`（默认 10）、工具异常回传不炸 Agent、超限安全退出且 `stop_reason` 记录；单测证明不会死循环。
- **objective**：给 Loop 加步数上限、异常捕获（错误回传模型让它调整）、超限安全退出。
- **steps**：1. `for step in range(max_steps)` 替代裸 while → 2. 工具执行 try/except，异常以文本回传、trace 记失败 → 3. 超限写 `stop_reason:max_steps_reached` 并输出已收集结果 → 4. 单测 mock 连续失败，验证不死循环。
- **卡住怎么办（L0-L5）**：L0-L1 "死循环会怎样？你的钱包呢？"→"上限=预算"；L2 给三种退出条件清单；L3 给 max_steps 改造点；L4 给异常回传代码；L5 给完整安全 Loop。
- **代码检索线索**：keywords `max_steps, stop_reason, exception, safety` ｜ likelyFiles `agent` ｜ searchPatterns `max_steps, stop_reason, except`
- **Rubric**：
  1. 有可配置 max_steps 上限（证据：代码｜w2）
  2. 工具异常不终止、错误回传（证据：代码+CI｜mock 失败｜w2）
  3. 超限安全退出 + trace 记 stop_reason（证据：Trace+CI｜w2）
  4. 能说出不设上限的两个后果（证据：描述｜消耗+死循环｜w1）
- **CI**：✓（mock 永远失败的工具 → max_steps 生效；trace schema 校验）

---

# Stage 4 完成项目

> **本阶段一句话**：把学到的全部串成最终交付物——一个能分析任何公开仓库、输出带证据报告的 CLI Agent。

## T09 带证据的项目分析报告

- **chunk_key**：`course02_github_agent/task09_report` ｜ Skill：project_dev
- **完成标准**：`report.md` 结构完整、每个结论可追溯到 trace 步骤、trace 显示多步自主调用、README 可复现。
- **objective**：CLI 输入仓库地址+分析需求，Agent 自主调用工具，输出 `report.md`（概况/结构/关键文件/结论建议），结论引用实际工具调用结果。
- **steps**：1. 定报告结构 → 2. 结论引用 trace 步骤编号（如 `[见 trace step 3]`）→ 3. 全程 `--trace`，`agent_trace.json` + `report.md` 一起提交 → 4. README 写清运行方式与配置说明。
- **卡住怎么办（L0-L5）**：L0-L1 "报告每个结论，读者怎么验证？"→"给出证据出处"；L2 给报告结构建议；L3 给引用格式约定；L4 给报告生成代码要点；L5 给完整实现。
- **代码检索线索**：keywords `report, markdown, evidence, 引用` ｜ likelyFiles `agent, report` ｜ searchPatterns `report\.md, trace, step`
- **Rubric**：
  1. report.md 存在且结构完整（证据：运行+报告｜w2）
  2. 关键结论可追溯到 trace（证据：Trace+报告｜抽查 3 条引用｜w2）
  3. trace 显示 ≥3 步且含多种工具（证据：Trace｜w2）
  4. 报告内容与所选仓库真实对应（证据：运行+报告｜抽查仓库实际信息与报告结论一致｜w1）
  > 原"README 可复现"一条按决策移除——验收目的是证明学生完成了项目与学习，不追求他人复现。
- **CI**：✓（report 结构校验 + trace schema 校验）

---

## 附录 A：CI Workflow 统一设计

`.github/workflows/ci.yml`：`python 3.11` → `pip install -r requirements.txt -r requirements-dev.txt` → `pytest -v`。规则：
- **单测一律 mock，不真调 GitHub / LLM API**（快、稳定、不吃额度）
- `GITHUB_TOKEN` 经 GitHub Actions secrets 注入（只给真正需要集成测试的环节，本课程不需要）
- pytest 结果 conclusion 由现有验收链读取，映射到对应 Rubric

## 附录 B：八类内容 → 引擎字段对照

| 本文内容 | 去向 |
|---|---|
| objective / steps / 前置假设 | `Task.objective / steps` |
| code_context | `Task.code_context` |
| Rubric 表 | `Rubric.criterion / required_evidence / pass_condition / weight` |
| 教材章节（chunk_key 标注处） | `data/raw/course02_github_agent.md` → chunker |
| 前置教程 | 独立文档《course02-前置教程-GitHubToken申请》→ 飞书/攻略页 |
| Skill 标签 | `Task.skill` |
| Trace 约定 | `EvidenceType.TRACE`（工程项：新增枚举） |
| Stage 编排 | `Stage.*` |

## 附录 C：已确认决策（2026-09-05）

1. **Token 申请时机**：课程第一天（T01 期间）即完成，前置教程飞书链接随课程发放：https://tralis2671.feishu.cn/wiki/Urq6w7wOiiAFe4kzGnmciPxYnCd
2. **报告引用格式**：接受 `[见 trace step N]`
3. **T09 README**：不强求可复现，Rubric 第 4 条改为"报告内容与所选仓库真实对应"
