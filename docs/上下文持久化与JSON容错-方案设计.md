# AI 导师：JSON 容错与上下文持久化 方案设计

> 版本：v1.1（2026-09-22）· 已按评审意见修订
> 范围：① 修复「模型连续 N 次输出非法 JSON」一类报错；② 解决 API 模式下上下文丢失与评审结果丢失。
> 目标读者：开发者（实现与评审用）。

## 0. 版本修订记录（本次采纳的评审意见）

| # | 评审意见 | 裁决 | 修订处 |
|---|----------|------|--------|
| ① | review_cache TTL 600s 不足以防"重启后重复评审烧钱" | 采纳：成功永久幂等 + 失败短期熔断 | §5、§3.2 |
| ④ | cache_key 只含 task_id+snapshot_hash，改规则后旧缓存命中 | 采纳：key 增加 rubric/prompt/engine/model 版本 | §3.2、§5 |
| ⑤ | JSON 解析优先级：JSON mode 第一，repair 第二 | 采纳（代码已如此，规范为显式优先级） | §2.2 |
| ⑥ | review 不得过度依赖 repair；repair 后必须严格语义校验 | 采纳（修复校验缺口：现有 `weight_of.get(id,1)` 静默容忍未知 rubric_id） | §2.2、§2.5 |
| ⑦ | 不做"续写残缺 JSON"为通用机制 | 采纳：终极解 = 避免截断；续写仅实验性 | §2.3 |
| ⑧ | max_tokens 不要全局写死，按行为分级 | 采纳：行为级配置表 | §2.2 |
| ⑨ | SQLite 作为会话真相源，前端只发 session_key+input | 采纳（补充必要配套：新增 GET 会话历史接口） | §4 |
| ⑩⑪ | 摘要按阈值触发；V1 不做 LLM 摘要，先结构化状态注入 | 采纳 | §4 |
| ⑫ | 删除"内存→SQLite 启动迁移"死代码 | 采纳 | §3.3 |
| ⑬ | 明确"不加"清单（Redis/PG/…），SQLite 非瓶颈 | 采纳 | §7 |

---

## 1. 背景与问题

### 1.1 线上 Bug（学生端可见）

学生收到错误横幅：

> 平台内部错误：模型连续 2 次输出非法 JSON：Expecting ',' delimiter: line 1 column 431 (char 430)（系统故障，与你提交的项目无关）

触发链路（已确认）：
1. [llm_client.py `_call`](file:///d:/Assistant/tralis/xkz-agent/ai_engine/llm_client.py#L113-L146) 调模型，未设置 `max_tokens`，依赖服务商默认输出上限；
2. 模型输出在 char 430 附近被截断（或结构性缺逗号）→ 非合法 JSON；
3. [_extract_json](file:///d:/Assistant/tralis/xkz-agent/ai_engine/llm_client.py#L85-L100) `json.loads` 抛 `JSONDecodeError`；
4. [重试循环](file:///d:/Assistant/tralis/xkz-agent/ai_engine/llm_client.py#L157-L192) 以「同一路径原样重跑」方式回传重试 → 截断型错误必然二次失败；
5. 抛 `EngineError` → [app.py `llm_error_response`](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py#L129-L132) 返回 500。

已确认的正确设计（**保留不动**）：错误分类漏斗（EngineError 永不进入学生评审结果）、文案与项目隔离声明。

### 1.2 上下文丢失（3 个瓶颈）

| # | 位置 | 现状 | 后果 |
|---|------|------|------|
| C1 | LLM 可见窗口 | 前端 `history.slice(-6)` → 后端 `history[-6:]` + `_trim` 6000 字 | 约 3 轮后前文对模型不可见 |
| C2 | 服务端状态 | `_sessions`/`_evidence_store`/`_REVIEW_CACHE` 全在进程内存 | 重启即失：调试轮次、hint 等级清零；**评审结果丢失 → 重复评审重复烧学生 API 额** |
| C3 | 前端持久化 | localStorage `xkz_chat_v1`（40 条/任务） | 换设备/清缓存丢失；本期不涉跨设备，降级为显示缓存 |

---

## 2. 选型结论（已确认决策）

| 决策点 | 结论 |
|--------|------|
| 存储 | **SQLite 落 ECS 系统盘**（`/opt/xkz-agent/data/engine.db`；本地开发 `data/engine.db`）。几十名学生纯文本量级几十 MB，系统盘足够；**不购买云数据库/数据盘** |
| 评审缓存 | **成功结果永久幂等（版本化 key）+ 失败结果 5 分钟熔断**，双表落 SQLite |
| 会话真相源 | **服务端 SQLite**（前端仅发 session_key + input + 附件） |
| 上下文窗口 | V1：SQLite 全量历史 + 最近 10~12 轮原文 + **结构化会话状态注入**；V1.1：阈值触发的 LLM 滚动摘要 |
| 前端 localStorage | 降级为显示缓存（刷新渲染用），非上下文真相源 |

---

## 3. Part A：JSON 输出容错加固（Bug 修复）

### A.1 目标

- 学生端几乎不再看到「模型连续 N 次输出非法 JSON」500；
- 模型输出异常时也能给学生可用的辅导回答（**teach 绝对兜底**）；
- **hard 边界不变**：LLM 只输出逐条判定；score/status 由代码聚合。

### A.2 运行时解析优先级（规范化）

```
                 LLM 调用
                  │
      JSON mode (response_format=json_object) 尽力开启
      （服务商 400 拒绝时才降级为纯提示词约束）
                  │
             正常 json.loads
                  │失败
        json-repair 修补（第二防线，不作为第一防线）
                  │
             Schema 校验（Pydantic）
                  │
        ┌─────────┴─────────┐
      teach 宽松          review 严格
        │                语义校验（见 A.5）未过 → 丢弃修补值，走重试/降级
      可用则返回           绝不把 repair 修补当正式评审
```

### A.3 `_call`：行为级 `max_tokens` + `finish_reason` + 空 content 兼容

- 新增行为级输出上限配置（数值为初始建议，按实测调优）：

| 行为/链 | 建议 max_tokens |
|---------|----------------|
| teach / advance | 1500 |
| teach / debug | 2500 |
| review | 3000 |
| teach / decompose | 3500 |

> 实现：`LLMClient(..., max_tokens=None)` -> 每次调用按行为传入（`behavior` 在 [app.py L301-302](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py#L301-L302) 可得），**不设全局写死常数**。

- 读取 `finish_reason`，`"length"` 明确标记截断（即使 JSON mode 也会截断）；
- `message.content is None`（推理型服务商把正文放 `reasoning_content`）→ 取后者；仍空则抛 `ProviderError`（不裸奔 AttributeError 出漏斗）。

### A.4 截断/畸形处理（不做"续写"为核心机制）

优先级（按有效度排序）：
1. **避免截断**：上述 max_tokens + JSON mode + 精简字段（A.6）；
2. **repair**：`_extract_json` 失败后尝试 `json-repair`（纯 Python，无编译依赖，适配 1.8G 内存）；
3. **完整重新请求**：截断（finish_reason=length）或 repair 后校验仍失败 → 原样重发一次完整 JSON 请求（可小幅上调该行为 max_tokens）。**不**默认采用「assistant=半截 JSON + user=继续」的续写方案（不同服务商行为不一致，仅标注为实验性选项）。

> 重试次数：仍然最多 2 轮（`MAX_RETRIES=2`），避免无限烧学生额度。

### A.5 teach / review 风险分级

- **teach（宽松）**：repair 后 Pydantic 校验通过即可返回——最多损失一次回答格式。
- **review（严格）**：repair 后除 Pydantic 外必须过**语义校验**（新增，当前缺口）：
  - `criteria` 非空；
  - 每条 `rubric_id` 必须存在于本任务的 `get_rubrics(task_id)`（现状 [review.py L239-245](file:///d:/Assistant/tralis/xkz-agent/ai_engine/review.py#L239-L245) `weight_of.get(id,1)` 会**静默**把未知 id 当 weight=1，必须改为校验拒绝）；
  - `status` 枚举合法（Pydantic 保证）、`evidence`/`reason` 非空；
  - 参考所有送审 Rubric 应被覆盖（不得漏判）。
  - 任一不满足 → 丢弃该轮结果，走 A.4-③ 重请求；两次均失败 → `REVIEW_UNAVAILABLE`（见 A.7）。

### A.6 精简输出契约（源头减负）

- prompts 按行为只要求必要字段；`message` ≤300 字指令；`verify_steps` ≤5 条。

### A.7 绝对兜底

- **teach**：第 2 轮仍失败 → 最后宽松一次「只输出纯文本回复，不要 JSON」→ 服务端包装为 `AiResponse(mode, message=text)` 返回 200，学生永远拿到回答；
- **review**：不编造判定，返回 `REVIEW_UNAVAILABLE`；但**失败入 `review_failures` 熔断 5 分钟**（同一 key 短时内不再重调 LLM 烧额）。

依赖：`pip install json-repair`。

---

## 4. Part B：数据持久化（SQLite）

### B.1 新增模块 `ai_engine/store.py`

SQLite 读写封装 + 建表 + 惰性清理。DB 路径环境变量可覆盖（服务器 `/opt/xkz-agent/data/engine.db`，开发 `data/engine.db`）。

### B.2 表结构

```sql
-- 会话（真相源；替代进程内存 _sessions）
CREATE TABLE sessions (
  session_key      TEXT PRIMARY KEY,      -- sid:task_id
  session_id       TEXT NOT NULL,
  student_id       TEXT NOT NULL,
  task_id          TEXT NOT NULL,
  mode             TEXT NOT NULL,
  hint_level       INTEGER DEFAULT 0,
  history_json     TEXT DEFAULT '[]',
  debug_state_json TEXT,
  summary_json     TEXT,                  -- V1.1 滚动摘要；V1 留空
  last_system_error TEXT,
  attempt_count    JSON,                  -- 后端逐步接管（V1 仍接受前端传入）
  created_at       TEXT NOT NULL,
  updated_at       TEXT NOT NULL
);

-- 评审成功结果（永久幂等；版本化 key）
CREATE TABLE review_results (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id        TEXT NOT NULL,
  snapshot_hash  TEXT NOT NULL,
  rubric_version TEXT NOT NULL,           -- 评审规则版本（改 Rubric 数据时手动 bump）
  prompt_version TEXT NOT NULL,           -- Review Prompt 版本
  engine_version TEXT NOT NULL,           -- 聚合/Key 算法版本
  model          TEXT NOT NULL,           -- 评审时所用模型
  response_json  TEXT NOT NULL,
  created_at     TEXT NOT NULL
);
CREATE UNIQUE INDEX uq_review_result_key ON review_results(
  task_id, snapshot_hash, rubric_version, prompt_version, engine_version, model);

-- 评审失败熔断（短期；5 分钟）
CREATE TABLE review_failures (
  review_key  TEXT PRIMARY KEY,           -- 同上 6 字段拼得（可散列）
  retry_after REAL NOT NULL,              -- unix 秒；过期惰性删除
  error       TEXT,
  created_at  TEXT NOT NULL
);

-- Evidence Store（替代进程内存 _evidence_store）
CREATE TABLE evidence (
  id TEXT PRIMARY KEY, task_id TEXT NOT NULL, rubric_id TEXT DEFAULT '',
  type TEXT NOT NULL, source TEXT DEFAULT '', content TEXT DEFAULT '',
  confidence REAL DEFAULT 1.0, created_at TEXT NOT NULL
);
CREATE INDEX idx_evidence_task ON evidence(task_id, rubric_id);
```

> 说明：review_results 为"永久"但有软保留（惰性清理 >90 天 / 每任务保留最近 N 条），防无限增长；review_failures 按 `retry_after` 惰性清理。

### B.3 迁移策略（删除原"启动内存迁移"）

- 内存 dict 重启后本就为空，「内存→SQLite 启动迁移」是死代码，**去掉**；
- 改为：**启动只建表**，随后把 `_sessions[key]` / `_REVIEW_CACHE` / `_evidence_store` 的读写逐步替换为 `store.get_session / store.save_session / store.get_review / store.save_review / store.evidence.add / store.evidence.list`；
- 可选：SQLite 之上保留小内存缓存作快路径（不必须）。

---

## 5. Part D：评审结果防丢 / 防重复烧钱

- **成功**：`review_results`（版本化 key）→ **永久复用**；缓存命中时**重建 resp**（刷新 `session_id`/`latency_ms`/`cached` 标记，不整体复用旧 session_id）。
- **失败**：`review_failures`（5 分钟熔断）→ 同 key 短时内直接复用失败结论，不再调 LLM。
- `logs.py` 事件日志（JSONL 落盘）维持现状不变。
- 关键语义：snapshot_hash 已覆盖证据文本 + CI 结论 + 任务 id（[review.py L133-148](file:///d:/Assistant/tralis/xkz-agent/ai_engine/review.py#L133-L148)），学生代码/证据变化 → hash 变化 → 必然重新评审；**规则版本（rubric/prompt/engine）变化 → key 变化 → 必然重新评审**（解决"改了规则还被旧缓存命中"）。

---

## 6. Part C：会话真相源 + 上下文窗口

### C.1 架构（V1 起）

```
  Browser               FastAPI                 SQLite（真相源）
   │  │                     │                        │
   │  └─ session_key + input + attachments (history 可选回退) ─► teach()
   │                        │ 读全量历史 / debug_state / hint / 【结构化状态】
   │                        ▼                        │
   │                   组装上下文 → LLM              │
   │                        │                        │
   │ ◄──── 响应 ──────────  ┴───────────────── 写回 history/summary ──►
   │
   └─ GET /api/ai/session_history?session_key=…  （刷新恢复显示）
```

- **前端只信任本地缓存用于即时渲染**；服务端 SQLite 为上下文真相源，`req.history` 仅在 store 无记录（首次）时作初始化回退；
- **新增 `GET /api/ai/session_history`**（评审意见 ⑨ 的必要配套——否则浏览器刷新/清理后无历史可展示，这是原意见遗漏的点）；
- 前端 localStorage 保留为显示缓存，不再承载上下文正确性。

### C.2 上下文组装（V1，无 LLM 摘要）

```
[system 角色+任务上下文+行为路由]
[system 【任务状态】当前任务/目标/已完成步骤（结构化，来源 SQLite sessions）]
[system 【学生状态】卡点/提示等级/调试轮次/上一轮诊断问题（结构化注入）]
+ 最近 10~12 轮原文（服务端从 SQLite 读取，窗口按字符预算 _trim 6000 兜底）
+ 读图结果(若有) + 本次 user_input
```

- 结构化状态已具备注入基础（`hint_level`、`render_debug_progress`、`system_error_note`），无需 LLM 即可恢复关键跨轮记忆；
- 窗口：后端 `history[-12:]`，前端 `slice(-6)` → `slice(-20)`（显式宽松，服务端为准）。

### C.3 V1.1 滚动摘要（阈值触发，非固定轮次）

- 触发条件：该会话**原文累积超阈值**（如 > 8000 字符，与 `_trim` 6000 预算配合），而非"每 6 轮固定"；
- 摘要内容：只压缩事实（卡点、已给提示等级、调试进度、任务进度），≤300 字，存 `sessions.summary_json`；
- 请求组装：摘要（若有）替代窗口外的旧原文；
- 成本：每阈值触发 1 次 LLM 调用，记**学生自己的 API Key**；失败静默跳过（退回纯窗口模式）；
- **V1 不实现**（降低首版上线风险与成本）。

---

## 7. 风险与边界

- **1.8G 内存明确不引入**：PostgreSQL / Redis / MongoDB / Elasticsearch / 向量数据库 / 本地 LLM / Redis Session / Celery 集群 / 独立摘要模型 / 大型内存 LRU。主要延迟与成本在 LLM API，SQLite 几十 KB 文本读写不是瓶颈。
- json-repair 自动补值风险：review 链路以 A.5 语义校验拒绝修补值，绝不当正式评审。
- 会话身份 = `sid:task_id`（sid 仍由前端生成）；**跨设备真正接续需要登录级学生身份**，超出本期范围（记入后续）。
- 滚动摘要只做事实压缩，**永不参与判定**；评审判定输入永远是 snapshot + Evidence。
- 隐私：SQLite 只存文本（对话/摘要/评审结果），存图/存 base64 策略维持不变。
- 数据增长：几十学生规模可忽略；review_results 软保留 + 惰性清理兜底。

---

## 8. 实施顺序

| 步骤 | 内容 | 文件 | 风险 |
|------|------|------|------|
| 1 | 行为级 max_tokens + finish_reason + content=None 兼容 | llm_client.py | 低 |
| 2 | json-repair 第二防线 + review 语义校验（A.5） | llm_client.py / app.py / schemas.py | 中（评审链需回归） |
| 3 | teach 纯文本兜底 + review 失败熔断表 | llm_client.py / app.py | 低 |
| 4 | SQLite store 模块：sessions / evidence / review_results / review_failures | 新增 store.py、app.py | 中 |
| 5 | 会话真相源改造 + GET session_history + 前端 slice(-20) | app.py / TeachView.vue | 中 |
| 6 | 输出契约精简 | prompts.py | 低 |
| 7（V1.1）| 阈值触发的 LLM 滚动摘要 | app.py / prompts.py | 中 |

步骤 1-3 可独立先行止血。

---

## 9. 验收清单

- [ ] 学生端不再出现「模型连续 N 次输出非法 JSON」横幅（截断/畸形/未知 rubric_id 均验证）
- [ ] 服务重启后：同 task+快照+版本 的评审**直接命中永久缓存**，不重复调 LLM、不重复烧额
- [ ] 修改 review prompt/rubric（bump 版本）后：同快照**重新评审**（旧缓存不命中）
- [ ] 服务重启后：调试轮次、hint 等级恢复；对话超过 3 轮后模型仍能引用前文
- [ ] 浏览器刷新后：对话仍完整显示（session_history 接口）
- [ ] review 语义校验拒绝无效 rubric_id / 空 criteria（不再静默接受）
- [ ] 正常 DeepSeek 路径回归（辅导/验收/调试）+ 双主题前端无回归