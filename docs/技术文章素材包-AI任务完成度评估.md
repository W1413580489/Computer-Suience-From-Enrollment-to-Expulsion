# 技术文章事实素材包

> 用途：为 CSDN 文章《AI Agent 任务完成度如何评估？从 Response Evaluation 到 Deliverable Evaluation》提供**可验证的事实素材**。
>
> 本文**不是文章**，不含文学化表达，不做宣传性描述。
>
> 取证范围：`d:\Assistant\tralis\xkz-agent\`（AI Tutor Engine）
> 取证方式：代码阅读 + 本地 SQLite 查询 + 测试脚本阅读
> 取证时间：2026-10-03

---

# A. 项目事实

## A0. 取证可信度声明（先看这一条）

| 事实 | 状态 |
| --- | --- |
| 本地 `data/engine.db` 存在但**所有业务表 0 行**（sessions / review_results / evidence / students / submissions / evaluations 全空） | 已核实 |
| 生产库位于服务器 `/opt/xkz-agent/data/engine.db`，**本次无法访问** | 已核实 |
| 因此本文的「真实案例」**不是生产日志回放**，而是「代码路径 + 测试夹具 + 课程数据」三者拼出的**可复现样例** | 必须如实标注 |

**给文章的措辞约束**：案例可写"系统在以下输入下会走这条路径"，**不可**写成"某位学生提交后系统判定为……"这类叙事。

## A1. 技术栈（与本文相关的部分）

| 层 | 技术 | 位置 |
| --- | --- | --- |
| 语言 | Python 3.11+ | `ai_engine/` |
| Web 框架 | FastAPI（独立服务，默认 8099/8000 端口） | [app.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py) |
| 数据校验 | Pydantic v2 | [schemas.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/schemas.py) |
| 存储 | SQLite（WAL 模式，单写连接，`busy_timeout=30000`） | [store.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/store.py) |
| HTTP 客户端 | httpx（异步，`connect=10s / read=60s`） | `llm_client.py` / `code_evidence.py` |
| LLM 接入 | OpenAI 兼容 `chat/completions`，`response_format={"type":"json_object"}`；BYOK（每请求带用户自己的 key） | [llm_client.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/llm_client.py) |
| 默认模型 | `deepseek-flash`（DeepSeek V4.1-Flash），base_url `https://api.deepseek.com` | `llm_client.py` L27-28 |
| 外部数据源 | GitHub REST API（仓库树 / 文件内容 / Actions runs / Issues） | [code_evidence.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/code_evidence.py) |
| 可选视觉 | 视觉模型分析运行截图，只回事实文本，不留原图 | `vision.py` + [app.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py#L658-L688) |
| 前端 | Vue 3 + TypeScript + Vite | `frontend/src/views/TeachView.vue` |
| 课程数据 | **Python 代码**（Pydantic 对象），非 JSON/YAML/Markdown/数据库表 | [course_data.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/course_data.py) / [course03_data.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/course03_data.py) |

## A2. 与本文直接相关的核心模块清单

| 模块 | 文件 | 在评估链路中的角色 |
| --- | --- | --- |
| 数据契约 | `schemas.py` | 定义 `Rubric` / `EvaluationRole` / `ReviewStatus` / `EvidenceType` / `ReviewCriterion` / `ReviewEvaluation` / `Submission` |
| 课程定义 | `course_data.py`、`course03_data.py` | 定义 Task 与 Rubric（验收标准的来源） |
| 证据采集 | `code_evidence.py` | GitHub → 代码/CI/Issue 证据文本 |
| 评审链 | `review.py` | 预检 / CI 直判 / 聚合 / Reviewer Prompt / 快照 |
| 编排层 | `app.py` `POST /api/ai/review` | 串联整条链，落库，挂学生态 |
| 持久化 | `store.py` | 幂等缓存 / 失败熔断 / Evidence Store / evaluations |
| 完成度聚合 | `project_state.py`、`learner_state.py`、`student_record.py`、`career.py` | Task → Project 完成度、技能状态、复盘、简历 |
| LLM 客户端 | `llm_client.py` | JSON 模式 + Pydantic 校验 + 语义校验 + 重试 + 兜底 |
| 视觉证据 | `vision.py` | 截图 → 事实文本（fail-open） |

## A3. 实现状态分类（本文最关键的一张表）

### 已实现（有代码、有测试、可运行）

| 能力 | 证据 |
| --- | --- |
| 逐条 Rubric 判定（PASS/FAIL/NEED_REVIEW） | `review.build_review_system_prompt` + `LLMClient.review` |
| 证据类型体系（11 种） | `EvidenceType` 枚举 + `collect_evidence()` |
| 证据硬门槛预检（缺证据 → 不调 LLM 直接 NEED_REVIEW） | `evidence_precheck()`，`_test_phase7.py` T7.6 验证 |
| CI 结论代码层直判（不经 LLM） | `ci_direct_verdict()` |
| code 层加权聚合 score/status（LLM 不产出总分） | `compute_evaluation()` |
| 证据快照 + 版本化幂等缓存 | `snapshot_evidence()` + `store._KV.fields()` |
| 评审失败 5 分钟熔断 | `store.save_review_failure` / `get_review_failure`，`FAILURE_TTL=300` |
| 验收角色分离（acceptance / theory / reflection） | `EvaluationRole` + `compute_evaluation` 三分桶 |
| Project State 完成度（只认 completion_required 全 PASS） | `project_state.compute_project_state()`（见 `_test_p4.py`） |
| Learner State 四态 + Learning Gap | `learner_state.py`（见 `_test_p5.py`） |
| 报告类证据（仓库内 TEST_REPORT.md 等） | `code_evidence._KEY_REPORT` + `review.extract_report_section` |
| GitHub Issue 证据（过滤 PR、最多 5 条） | `code_evidence.fetch_issues_evidence`，`_test_phase7.py` T7.7 |
| 视觉证据（可选、fail-open、不评美观） | `vision.py` + `review.format_visual_evidence` |
| Revision 演进（GitHub compare，只入 submissions/evaluations） | `app.py` L719-727 |
| 简历素材只取「已通过验收」任务 | `career.build_career_text` 的 `_collect_points` |
| JSON 容错（json-repair 第二防线 + 截断重请求 + 纯文本兜底） | `_test_v11_fix.py` T1/T3/T4 |

### 部分实现

| 能力 | 现状 | 缺什么 |
| --- | --- | --- |
| 「执行」证据 | 只能拿到①学生自述里的启动命令 ②CI 结论 ③部署地址 | **引擎自己不执行学生代码**；无沙箱、无内建测试运行器 |
| 视觉验收 | 有完整链路，但依赖模型在 Vision 白名单内 + 学生主动上传 | 未接入课程；当前所有课程 Rubric 的 `visual_check` 均为 `none` |
| Task 级字段 | `Task.evidence_required`、`Task.hints` 已建模、课程数据已填 | **引擎代码 0 处读取**（见 G1） |
| Mode | `Mode` 枚举含 `tutor/coach/debugger` | `MODE_PROMPTS` 实际只剩 `tutor`；调试能力内化为 behavior |
| 幂等缓存粒度 | 快照含"全部证据文本 + CI 结论 + task_id" | 不含 `head_sha`；若两个 commit 的关键文件内容一致，会命中同一缓存 |

### 设计中（有设计迹象，无实现代码）

| 能力 | 迹象 |
| --- | --- |
| 课程级难度/前置依赖 | `Course` 无 `difficulty` / `prerequisite` 字段；仅文档层面讨论过 |
| 文学/人文类技能标签 | `SkillKey` 13 项全为计算机类；无扩展提交 |

### 尚未实现（不要写进文章）

| 能力 | 说明 |
| --- | --- |
| 沙箱执行 / 自动跑测试 | 引擎从不执行学生代码 |
| 静态分析（AST / lint / 类型检查） | 无 |
| 多 Agent 协作 / 规划器 / 反思循环 | 只有单次 LLM 调用（+最多 2 次重试） |
| 自动修复学生代码 | 明确禁止（导师铁律 5、评审铁律 4） |
| 评估质量指标（准确率/精确率/召回率/F1） | 无标注集、无基准测试、无混淆矩阵 |
| 形式化验证 / 定理证明 | 无 |
| 自动判分完全无人工 | 存在 NEED_REVIEW 第三态，需学生补证 |
| 跨课程前置校验 | 无课程级依赖 |

---

# B. 核心架构

## B1. 真实数据流（与文章标题的六个环节对应）

文章想用 `Task → Requirement → Execution → Evidence → Evaluation → Acceptance`。**真实情况如下**，其中「Execution」这一段与常见想象不同，必须按真实写。

```text
① Task（任务）
   get_task(task_id)  →  Task{id,title,objective,steps,rubric_ids,code_context,chunk_key}
   来源：course_data.py / course03_data.py 的 Pydantic 对象
   ※ 不落库。课程是代码常量，进程内缓存 _project_cache。

② Requirement（要求）
   get_rubrics(task_id)  →  [Rubric{criterion,description,required_evidence,
                                   pass_condition,weight,evaluation_role,visual_check}]
   ※ 这是「验收要求」的唯一载体。Task 上没有任何独立的 requirement/acceptance 字段。

③ Execution（执行）—— ★ 引擎不参与 ★
   学生在本机/GitHub 上完成工作。引擎：
     - 不提供沙箱，不运行学生代码，不执行测试
     - 对「能否运行」的判定只能依赖三条外部线索：
         ① 学生自述/README 里的启动命令（detect_run_cmd 正则）
         ② GitHub Actions 的 conclusion（build/test/runtime 维度）
         ③ 学生自愿提供的在线部署地址
   ※ 这是全链路最大的证据弱点，也是最主要的误判来源（见 F2、G2）。

④ Evidence（证据）
   code_evidence.build_code_evidence(repo_url, task_id, code_context)
     → { ok, repo, default_branch, head_sha, file_count, key_files,
         evidence_text, readme_run_cmd, ci, issues }
     实现细节：GitHub tree API 取全量路径 → _pick_key_files 排序取 ≤10 个
               （报告类 > README > 依赖 > 主入口 > 配置，再补 ≤2 个 test_*.py）
               单文件 ≤120 行，报告类 ≤250 行，总上限 20000 字符
   review.collect_evidence(submission, evidence_text, visual)
     → { code, runtime, test, url, description, visual, report, issue, deployment, trace }
   ※ 归一化为「证据类型 → 文本」字典，供后续所有环节消费。

⑤ Evaluation（评估）—— 四道闸门，见 B2 ——
   evidence_precheck  →  ci_direct_verdict  →  LLM Reviewer  →  compute_evaluation

⑥ Acceptance（验收结论）
   status(PASS/FAIL/NEED_REVIEW) + score(0-100) + criteria[]
   → 落 evaluations 表（每份提交一行，真相源）
   → 同时写 review_results 幂等缓存（同输入同输出的缓存层，非真相源）
   → project_state.compute_project_state() 聚合 → Project: NOT_STARTED/IN_PROGRESS/COMPLETED/BLOCKED
```

**与文章预期的两处偏差（必须写明）：**

1. **没有"内建执行"环节**。Execution 由学生在引擎之外完成，引擎只采集"执行的痕迹"。
2. **Requirement 不独立存在**。它完全由 Rubric 承载，`Task` 上还有两个同名字段（`evidence_required` / `hints`）但引擎不读。

## B2. 四道闸门（评估环节的内部结构）

```text
闸门 1  evidence_precheck(rubrics, available)                     【确定性·可复现】
        仅 acceptance 角色参与；
        needed = required_evidence − {deployment, visual, report, issue}
        missing = needed − present − {description}
        missing 非空 → 该 Rubric 强制 NEED_REVIEW，且不进 LLM

闸门 2  ci_direct_verdict(rubric, ci_workflows)                   【确定性·可复现】
        仅 acceptance；needed 含 description 或 code → 放弃直判
        conclusion 集合 == {"success"} → PASS
        conclusion 集合 == {"failure"} → FAIL
        其它（混合/startup_failure/neutral/cancelled/timed_out）→ 不直判

闸门 3  LLMClient.review(...)                                     【AI 主观】
        只接收"通过闸门1且未被闸门2直判"的 Rubric
        输出：{criteria:[{rubric_id,status,evidence,reason}], next_step}
        硬约束：只输出逐条判定，禁止输出总分

闸门 4  compute_evaluation(criteria, rubrics, next_step)          【确定性·可复现】
        acceptance 桶 → score = round(Σ通过weight / Σacceptance weight × 100)
                        status：有 FAIL → FAIL；否则有 NEED_REVIEW → NEED_REVIEW；否则 PASS
        theory 桶     → 未 PASS 的进 learning_gaps，永不改 status
        reflection 桶 → 全部进 reflection，永不改 status
```

**关键设计事实（可作为文章核心论点）：**

- **LLM 无权决定总分。** `ReviewLLMOutput` 的字段只有 `criteria` 和 `next_step`——schema 里根本没有 `score`/`status`。
- **全链路可以零 LLM 调用地得出 PASS/FAIL**：当所有 Rubric 都被闸门 2 直判时（`app.py` L776-785），评审不产生任何模型调用。
- **全链路可以零 LLM 调用地得出 NEED_REVIEW**：当所有 Rubric 都缺证据时（`app.py` L788-823），直接返回并写入缓存。

## B3. 前后端链路

```text
前端 TeachView.vue
  ├─ onMounted → GET /api/ai/config   → 课程/项目/阶段/任务（全数据驱动）
  ├─ 提交验收 → POST /api/ai/review   → 渲染评审卡（status/score/criteria/next_step）
  └─ PASS 时 → student.completed_tasks.push(task_id) → localStorage
```

---

# C. Evaluation 相关代码位置

## C1. 验收核心（`ai_engine/review.py`）

| 符号 | 行号 | 职责 | 确定性 |
| --- | --- | --- | --- |
| `_role(r)` | L24-26 | 取 Rubric 的 `evaluation_role`，缺省兼容为 `acceptance` | ✅ |
| `_REPORT_TAG` | L33 | `"【学生测试报告/问题记录】"`，报告证据的标记串 | — |
| `extract_report_section()` | L37-52 | 从证据文本抽报告正文，上限 2500 字 | ✅ |
| `extract_issues_section()` | L59-66 | 从证据文本抽 Issue 记录，上限 2000 字 | ✅ |
| `collect_evidence()` | L69-114 | Submission + 仓库文本 + 视觉 → 证据字典 | ✅ |
| `format_visual_evidence()` | L117-132 | 视觉结果 → 事实文本（含图片指纹） | ✅ |
| `snapshot_evidence()` | L138-153 | 证据 + CI + task_id → `sha256[:16]` | ✅ |
| `evidence_text()` | L156-169 | 证据字典 → Reviewer 读的正文 | ✅ |
| `_missing_evidence()` | L172-178 | 反推缺失证据类型（`description` 不计） | ✅ |
| `evidence_precheck()` | L182-234 | **闸门 1** | ✅ |
| `compute_evaluation()` | L240-292 | **闸门 4**，三分桶聚合 | ✅ |
| `_CI_DIM_TO_EVIDENCE` | L297-301 | CI 维度映射表 `{build,test,runtime}` | — |
| `ci_direct_verdict()` | L304-359 | **闸门 2** | ✅ |
| `build_review_system_prompt()` | L365-469 | Reviewer Prompt（7 条铁律 + 视觉边界 + 报告规则 + Issue 用法 + CI 优先） | — |

## C2. 编排层（`ai_engine/app.py` `POST /api/ai/review`，L610-925）

| 行号 | 动作 |
| --- | --- |
| L613-623 | 入参校验（task_id / api_key / task 存在 / rubrics 非空） |
| L626-656 | 拉 GitHub 代码证据 + CI（失败不阻塞） |
| L658-688 | 可选视觉证据（失败 fail-open，只记元数据不记图片） |
| L690-694 | `collect_evidence` + README 启动命令补 runtime |
| L697-702 | `lazy_cleanup` + `snapshot_evidence` |
| L705-729 | 学生建档 + 提交落库 + Revision compare + 证据落库 |
| L734-742 | `_record_eval` 闭包（缓存命中也要记，因为提交是真实事件） |
| L745-750 | **失败熔断检查** |
| L753-765 | **幂等缓存命中分支** |
| L768-770 | 闸门 1 预检 |
| L774-785 | 闸门 2 CI 直判分流 |
| L788-823 | 全缺证据 → 零 LLM 返回 NEED_REVIEW |
| L828-853 | 闸门 3 LLM 评审（异常 → 熔断 + REVIEW_UNAVAILABLE） |
| L859-871 | 闸门 4 聚合 |
| L895-925 | 写缓存 → 写 evaluations → 挂学生态 → 返回 |

## C3. 持久化（`ai_engine/store.py`）

| 符号 / 常量 | 行号 | 说明 |
| --- | --- | --- |
| `REVIEW_RUBRIC_VERSION = "2"` | L30 | Rubric 规则版本 |
| `REVIEW_PROMPT_VERSION = "1"` | L31 | Prompt 版本 |
| `REVIEW_ENGINE_VERSION = "2"` | L32 | 聚合算法版本 |
| `FAILURE_TTL = 300` | L37 | 熔断 5 分钟 |
| `review_results` 表 + 唯一索引 | L110-126 | 幂等缓存，key = 6 元组 |
| `review_failures` 表 | L128-134 | 失败熔断 |
| `evidence` 表 | L136-142 | 证据存档（id 主键天然幂等） |
| `submissions` 表 | L156-171 | 提交事件（含 `head_sha` / `revision_json`） |
| `evaluations` 表 | L176-203 | **真相源**（含 `criteria_json` / `ci_conclusion`） |
| `get_review_result` / `save_review_result` | L299-322 | 幂等缓存读写 |
| `get_review_failure` / `save_review_failure` | L324-344 | 熔断读写 |
| `save_evaluation` | L421-438 | 按 `submission_id` 幂等 upsert |
| `latest_evaluations` | L447-470 | 批量取每任务最新一次 |
| `lazy_cleanup` | L532-555 | 过期熔断 + >90 天 + 每任务保留 200 条 |

## C4. 数据契约（`ai_engine/schemas.py`）

| 模型 | 关键字段 |
| --- | --- |
| `Rubric` | `id / task_id / criterion / description / required_evidence / pass_condition / weight / visual_check / visual_pass_condition / evaluation_role` |
| `EvaluationRole` | `acceptance` / `theory` / `reflection`（冻结基线 TOTAL=81：64/14/3） |
| `ReviewStatus` | `PASS` / `FAIL` / `NEED_REVIEW` |
| `EvidenceType` | `code / ci / runtime / visual / github / description / manual / trace / report / issue` |
| `ReviewCriterion` | `rubric_id / status / evidence / reason` |
| `ReviewEvaluation` | `status / score / criteria / next_step / learning_gaps / reflection` |
| `ReviewLLMOutput` | `criteria / next_step`（**无 score / status**） |
| `Submission` | `id / task_id / student_id / project_id / github_url / deployment_url / code / description / head_sha / parent_submission_id / revision_json / submitted_at` |
| `Task` | `... evidence_required`（**未消费**）/ `hints`（**未消费**）/ `completion_required` / `depends_on` |

## C5. 证据采集（`ai_engine/code_evidence.py`）

| 符号 | 行号 | 说明 |
| --- | --- | --- |
| `_KEY_REPORT` | L64-70 | 报告类文件名白名单（`test_report.md` / `report.md` / `bugs.md` / `retro.md` …） |
| `_KEY_README` | L71 | `readme.md` 等 |
| `_lines_cap_for()` | L226 | 报告类 250 行 / 普通 120 行 |
| `_is_report_file()` | L229-231 | 是否报告文件 |
| `_pick_key_files()` | L243- | 关键文件优先级选取 |
| `fetch_issues_evidence()` | L312- | Issues → 过滤 PR / 最多 5 条 / 正文 800 字 |
| `_assemble()` | L654 附近 | 给报告文件打 `【学生测试报告/问题记录】` 标记 |

## C6. 完成度聚合

| 文件 | 函数 | 规则 |
| --- | --- | --- |
| `project_state.py` | `compute_project_state()` | 只认 `completion_required=True` 的 Task 全 PASS → COMPLETED；`completion_defined=False` 时不做判定 |
| `project_state.py` | `task_blocked_reason()` | `depends_on` 仅生成提示，**不阻断** |
| `learner_state.py` | `compute_learner_state()` | UNSEEN/EXPOSED/PRACTICED/EVIDENCED；**EVIDENCED ≠ MASTERED** |
| `learner_state.py` | Learning Gap 归并 | 按 `(task_id, rubric_id)`；出现 ≥3 次 → high |
| `student_record.py` | `build_project_retro()` | 时间线 / 逐任务 / 汇总，零 LLM |
| `career.py` | `build_career_text()` | 只用已通过验收任务的 `resume_points`；过滤"学习属性"文本 |

---

# D. 真实案例

> **来源说明（必读）**：以下案例由「代码路径 + 测试夹具（`_test_phase7.py` / `_test_v11_fix.py` / `_test_evidence.py`）+ 课程数据」构成，**不是生产库回放**。写文章时请用"系统在此输入下会走此路径"的表述。
>
> 涉及的真实测试仓库：`https://github.com/W1413580489/chatbot-wrapper-test`（见 `_test_evidence.py` L6）。

## D1. 案例一：CI 结论直判 → 零 LLM 判定 PASS

| 项 | 内容 |
| --- | --- |
| 提交内容 | 一个配了 GitHub Actions 的公开仓库 |
| Agent 检查了什么 | 拉取仓库文件树与关键文件；拉取 Actions runs 并归一化为 `{name, dimension, conclusion}` |
| 使用什么证据 | `code`（仓库文本）+ CI `test` 维度 `conclusion=success` |
| 如何判定 | 闸门 1：`required_evidence=["test"]`，`test` 已在 available 中 → 可过。闸门 2：`ci_direct_verdict()` 中 `needed={"test"}`，不含 `description`/`code`，映射到 `test` 维度，结论集合 `{"success"}` → **PASS**，evidence 文本为 `CI 自动验收证据（system 判定）：<workflow名>（success）` |
| 结果 | 该 Rubric 不进 LLM。若全部 Rubric 都直判 → `latency_ms` 仅剩网络耗时，**零模型调用** |
| 代码位置 | `review.py#L304-L359`、`app.py#L774-L785` |
| 有没有误判 | 无。CI 结论是 GitHub 侧确定性结果，非 AI 推断 |

## D2. 案例二：证据缺失 → 零 LLM 判定 NEED_REVIEW

| 项 | 内容 |
| --- | --- |
| 提交内容 | 只填了文字自述（含 `description`），无 GitHub 仓库、无部署地址 |
| Agent 检查了什么 | `collect_evidence()` 得到 `{"description": "..."}`，无 `code` / `runtime` |
| 使用什么证据 | 仅 `description`（**被显式排除在硬证据之外**） |
| 如何判定 | 闸门 1：某 Rubric `required_evidence=["code","runtime"]` → `needed={"code","runtime"}`，`present={"description"}`，`missing_real={"code","runtime"}` 非空 → 强制 NEED_REVIEW |
| 返回内容 | `next_step` = `"请补充以下证据后重新提交：rb_xx 需要 code, runtime"` |
| 结果 | **不调用 LLM**，直接写幂等缓存 + 落 evaluations |
| 代码位置 | `review.py#L182-L234`、`app.py#L788-L823` |
| 有没有误判 | 这是**设计意图内的正确行为**。但见 F1：`description` 虽被排除在硬门槛外，**却仍被渲染进 Prompt 供 LLM 阅读**，存在被自述带偏的风险 |

## D3. 案例三：报告与代码双证据（课程 03 路径）

| 项 | 内容 |
| --- | --- |
| 提交内容 | 仓库根目录有 `TEST_REPORT.md`（含表格「场景 / 实际结果」）+ `main.py` |
| Agent 检查了什么 | `_pick_key_files` 把报告排在第一位（优先级最高）；`_assemble` 给它打标 `【学生测试报告/问题记录】`；报告类行数上限放宽到 250 |
| 使用什么证据 | `code` + `report`（`extract_report_section()` 抽出正文，上限 2500 字） |
| 如何判定 | 闸门 1：`report` 属 `optional_bonus`，**缺了不阻塞**；若 Rubric 写 `required_evidence=["report"]` 则整条 Rubric 都会 `passable`（`_test_phase7.py` T7.6 明确验证）。实际判定交 LLM，Prompt 的「测试报告的核对规则」要求：学生"实际结果"栏若只有"正常/OK/没问题"这类笼统描述 → **不足以判 PASS**；报告与 CI 冲突 → **判 NEED_REVIEW** |
| 代码位置 | `code_evidence.py#L64-L70,#L226,#L229,#L654`、`review.py#L37-L52,#L443-L448` |
| 有没有误判 | 有明确防线（笼统描述不判 PASS），但防线是 **Prompt 级**而非代码级，效果未经量化 |

---

# E. 成功案例

## E1. 「LLM 不产出总分」的防漂移设计（可验证）

```python
# review.py L240-L292（节选）
role_of = {r.id: _role(r) for r in rubrics}
weight_of = {r.id: max(int(r.weight), 0) for r in rubrics}
...
for c in criteria:
    role = role_of.get(c.rubric_id, EvaluationRole.acceptance)
    if role == EvaluationRole.theory:
        if c.status != ReviewStatus.PASS:
            learning_gaps.append(c)
        continue
    if role == EvaluationRole.reflection:
        reflection.append(c)
        continue
    # acceptance
    acc_criteria.append(c); w = weight_of.get(c.rubric_id, 1)
    total += w
    if c.status == ReviewStatus.PASS: passed += w
    elif c.status == ReviewStatus.FAIL: has_fail = True
    else: has_need_review = True
score = round(passed / total * 100) if total > 0 else 0
```

**为什么算成功**：总分是纯函数。相同 `criteria` + 相同 `rubrics` → 必然相同 `score`。模型无法通过措辞影响分数。

## E2. 幂等缓存让"重复提交"不重复烧额度

```python
# review.py L138-L153
canonical = json.dumps({
    "task_id": task_id,
    "evidence": dict(sorted(available.items())),
    "ci": sorted((wf.get("name",""), wf.get("dimension",""), str(wf.get("conclusion")))
                 for wf in (ci_workflows or [])),
}, ensure_ascii=False, sort_keys=True)
return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
```

`store._KV.fields()` 组成 6 元组 key：`task_id : snapshot_hash : rubric_version : prompt_version : engine_version : model`，`review_results` 上有唯一索引（`store.py#L123-L126`）。

**为什么算成功**：BYOK 场景下，学生重复点"提交验收"不会重复消耗自己的额度；且 `Revision`（`head_sha` / `revision_json`）被刻意排除在 key 之外——同一份代码哪怕换分支提交也照样命中。

## E3. 失败熔断保护学生额度

```python
# store.py L324-L334
def get_review_failure(self, task_id, snapshot_hash, model):
    key, _, _, _, _ = _KV.fields(task_id, snapshot_hash, model)
    row = self._fetchone("SELECT retry_after, error FROM review_failures WHERE review_key=?", (key,))
    if not row: return None
    if time.time() >= row["retry_after"]:
        self._exec("DELETE FROM review_failures WHERE review_key=?", (key,)); return None
    return row["error"] or "评审临时不可用"
```

**为什么算成功**：模型侧故障（限流/超时/JSON 连续非法）时，同 key 5 分钟内直接返回 `REVIEW_UNAVAILABLE`，并把"系统故障，与你提交的项目无关"写进 message（`app.py#L747-L750`）——错误归因隔离与额度保护同时做到。

## E4. 验收角色分离，理论题不再拉低交付判定

```python
# review.py L204-L208（闸门 1 内）
if _role(r) != EvaluationRole.acceptance:
    passable.append(r)      # theory / reflection 不参与证据硬门槛
    continue
```

**为什么算成功**：`criteria` 数组只回填 acceptance 条目（`compute_evaluation` docstring 明确），前端评审卡与简历通过率口径统一，理论题不会把简历通过率拉低。

---

# F. 失败 / 误判案例

## F1. `description` 被排除在硬门槛外，却仍进入 LLM 的视野（结构性软肋）

**代码事实：**

- 闸门 1 里：`missing_real = {m for m in missing if m != "description"}`（`review.py#L216`）→ description 不算硬证据。
- 但 `collect_evidence()` 会把 self-report 写进 `available["description"]`（`review.py#L102-L103`）；
- `evidence_text()` 会把 `description` 渲染成 `[学生自述] ...` 放进 Prompt（`review.py#L156-L169`）；
- 于是 LLM **看得到**它，闸门却**不认**它。

**误判路径**：学生只写了一段很有说服力的自述 + 无任何代码/运行证据 → 预检强制 NEED_REVIEW（正确）→ 但若该 Rubric 恰好没有硬证据要求（`required_evidence` 为空，走 `passable`），LLM 有可能仅凭自述判 PASS。

**结论**：这是**代码层可验证的真实漏洞面**。文章可写"系统用两道不同的规则处理同一份自述（预检排除 / 提示词可见），存在被自述锚定的风险"。

## F2. `code` 证据只能证明"写了什么"，不能证明"跑没跑通"

**代码事实**：Prompt 中已显式写死这条边界（`review.py#L393-L394`）：

```text
注意：代码证据只能证明「写了什么」，不能证明「跑没跑通」。运行类验收以「本地可复现
运行说明 / CI 结论 / 部署地址」三选一为准；三者都没有的项记 NEED_REVIEW。
```

**为什么仍是误判高发区**：因为**唯一的防线是 Prompt**。引擎没有任何代码层机制阻止 LLM 对一段"看起来完整"的代码给出 PASS。运行证据缺失时是否真的记 NEED_REVIEW，取决于模型是否遵守铁律。

## F3. `trace` 证据的字符串检测存在误报面

**代码事实**（`review.py#L81-L82`）：

```python
if "agent_trace.json" in repo_code_text:
    ev["trace"] = "仓库中包含 agent_trace.json（Agent 执行轨迹），可验证工具调用与多步行为"
```

**误判路径**：`repo_code_text` 是拼接后的全量证据文本。只要**任何位置**出现 `agent_trace.json` 这个字符串（例如 README 里写"本项目会生成 agent_trace.json"、或某文件里提到该文件名），`trace` 证据就被登记为"存在"。而 `trace` 是**硬证据类型**（不在 `optional_bonus` 中）。

**结论**：存在"声明即证据"的漏洞，可作为文章中"证据采集需要更强的存在性校验"的论据。

## F4. 幂等缓存不看 `head_sha`，可能复用旧结论

**代码事实**：`snapshot_evidence()` 的输入只有 `available`（证据文本）+ `ci_workflows` + `task_id`（`review.py#L138-L153`），`head_sha` 被刻意排除（`app.py#L637` 注释"只入 submissions/evaluations，不进快照/缓存 key"）。

**误判路径**：学生新提交的 commit 若**只改了非关键文件**（不在 `_pick_key_files` 选中范围内），`evidence_text` 完全一致 → 快照 hash 一致 → 命中旧缓存 → 返回旧判定。

**这是有意的取舍**（换来"同代码不重复烧额度"），但确实是"改动被忽略"的窗口。文章可写为"幂等粒度与证据粒度的耦合风险"。

## F5. 历史真实故障（有修复代码与回归测试）

### F5-a 输出截断导致 500

**现象**：模型输出在 char 430 处被截断（未设置 `max_tokens`）→ `json.loads` 失败 → 同一路径重试二次失败 → 接口 500。
**修复**（`llm_client.py#L233-L238`）：

```python
if raw.get("finish_reason") == "length":
    raise json.JSONDecodeError(
        "输出在长度限制处被截断（finish_reason=length），需加大额度重新生成",
        raw["content"], 0)
```

**回归测试**：`_test_v11_fix.py` T3（断言第二次调用 `max_tokens` 已从 1500 加大到 3000，且不把残缺 JSON 回传）。

### F5-b 模型返回空 JSON 数组导致 TypeError

**现象**：模型输出 `[]` → `_extract_json` 返回 `list` → `obj["mode"]` 抛 `TypeError` → 500。
**修复**：`teach()` 的 `except` 中捕获 `TypeError`。

### F5-c 语义校验缺失导致"未知 rubric_id 被静默接受"

**代码事实**（`llm_client.py#L132-L157`）：`_semantic_validate_review()` 强制三条——① `rubric_id` 必须在送审清单内；② `evidence` / `reason` 非空；③ 送审 Rubric 必须逐条覆盖。
**回归测试**：`_test_v11_fix.py` T2（未知 id、空 criteria、缺 evidence、漏判 四类均被拒）。

## F6. Prompt 与代码的双重真实来源风险

**代码事实**：`review.py` 里的评审铁律（7 条 + 视觉边界 + 报告规则 + Issue 用法）全部是**自然语言**。铁律 2「没有证据支撑的判定一律 NEED_REVIEW」在代码层**没有对应的强制校验**——`compute_evaluation` 只检查 `status` 取值，不检查 `status=PASS` 时 `evidence` 是否真的引用了有效证据。

**结论**：这是"Prompt 级约束 ≠ 代码级约束"的典型案例。

---

# G. 当前局限

## G1. 两个"看起来生效、实际不生效"的字段（课程作者最容易踩）

| 字段 | 位置 | 真实情况 |
| --- | --- | --- |
| `Task.evidence_required` | `schemas.py` 的 `Task`；course 数据里大量填写 | **引擎 0 处读取**。验收只读 `Rubric.required_evidence`。仅 `_test_phase8.py` 校验其取值合法性 |
| `Task.hints` | `schemas.py` 的 `Task`（`dict[int,str]`） | **全仓库 0 处读取**。提示程度由 `hint.py` 的 `hint_level` + Prompt 的提示等级表驱动 |

## G2. 全链路系统局限清单

| 局限 | 具体说明 |
| --- | --- |
| **引擎不执行代码** | 无沙箱、无内建 pytest 运行器。"能跑"的结论 100% 来自外部（CI / 自述 / 部署地址） |
| **无静态分析** | 不看 AST、不跑 lint、不做类型检查。代码类判定全靠 LLM 读文本 |
| **证据文本有硬上限** | 关键文件 ≤10 个、单文件 ≤120 行（报告 250 行）、总文本 ≤20000 字符。超出部分 LLM 看不到 |
| **GitHub-中心主义** | 没有公开 GitHub 仓库 → 没有 `code` 证据 → 大量 acceptance Rubric 直接 NEED_REVIEW |
| **无课程级前置/难度** | `Course` 只有 `id/title/description/projects` |
| **SkillKey 无文学类** | 13 项全为计算机类 |
| **不评美学** | Prompt 明确"不评价界面美观、配色、设计质量、响应式效果"；`visual` 永不作为硬门槛 |
| **无评估质量指标** | 没有准确率 / 精确率 / 召回率 / 一致性（Kappa）数据；没有标注集 |
| **单模型单调用** | 无多 Agent、无 Self-Consistency、无投票、无反思循环。仅"最多 2 次 Pydantic 校验重试" |
| **LLM 温度 0.4** | 非确定性输出；靠幂等缓存而非确定性来保证"同输入同输出" |
| **同秒排序不可靠** | `store.py#L447-L452` 注释明说：`created_at` 只到秒，同秒内多次评审顺序不可靠，故按 `(created_at, rowid)` 升序全取后在 Python 侧归并 |
| **需要 BYOK** | 无 api_key 直接 400（`app.py#L615-L616`）；所有评审成本由学生自付 |

## G3. 与文章标题的诚实对位

| 文章概念 | 本项目是否有 | 说明 |
| --- | --- | --- |
| Response Evaluation | ✅ 有 | `AiResponse` + `response_validator.validate()` 的 5 项检查（hint/role/context/learning/safety） |
| Deliverable Evaluation | ✅ 有 | `review.py` 整条链（本素材包主体） |
| Agent Evaluation（Agent 自身行为评价） | ❌ 无 | 不评 Agent 的工具选择/规划质量 |
| 内建执行沙箱 | ❌ 无 | 见 G2 |
| 评测基准 / 数据集 | ❌ 无 | 见 G2 |

---

# H. 可公开展示的代码

以下片段可直接进文章，均从仓库原文摘录（可对照文件行号核验）。

## H1. 数据契约：Rubric 与三态（`schemas.py`）

```python
class EvaluationRole(str, Enum):
    acceptance = "acceptance"   # 有阻断权：基于可核验交付证据
    theory     = "theory"       # 无阻断权：产出 Learning Gap
    reflection = "reflection"   # 无阻断权：产出 Retro

class ReviewStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEED_REVIEW = "NEED_REVIEW"     # 第三态：证据不足
```

## H2. 闸门 1：证据硬门槛（`review.py#L182-L234` 精简）

```python
optional_bonus = {"deployment", "visual", "report", "issue"}

for r in rubrics:
    if _role(r) != EvaluationRole.acceptance:
        passable.append(r); continue
    needed = set(r.required_evidence) - optional_bonus
    if not needed:
        passable.append(r); continue
    missing = needed - present
    missing_real = {m for m in missing if m != "description"}   # 自述不算硬证据
    if missing_real:
        forced.append({"rubric_id": r.id, "missing": sorted(missing_real),
                       "reason": f"缺少必要证据类型：{', '.join(sorted(missing_real))}，无法自动判定"})
    else:
        passable.append(r)
```

## H3. 闸门 2：CI 结论直判（`review.py#L304-L359` 精简）

```python
needed = set(rubric.required_evidence) - {"deployment"}
if not needed or ({"description", "code"} & needed):
    return None          # 语义判定类型 → CI 证明不了
...
conclusions = {c for _, _, c in matched}
if conclusions == {"success"}:
    return {"status": ReviewStatus.PASS,
            "evidence": f"CI 自动验收证据（system 判定）：{ev_src}"}
if conclusions == {"failure"}:
    return {"status": ReviewStatus.FAIL, ...}
return None              # 混合/异常结论 → 交给 LLM
```

## H4. 闸门 4：确定性聚合（`review.py#L282-L292`）

```python
score = round(passed / total * 100) if total > 0 else 0
if has_fail:            status = ReviewStatus.FAIL
elif has_need_review:   status = ReviewStatus.NEED_REVIEW
else:                   status = ReviewStatus.PASS
```

## H5. 幂等键（`review.py#L145-L153` + `store.py#L52-L63`）

```python
canonical = json.dumps({
    "task_id": task_id,
    "evidence": dict(sorted(available.items())),
    "ci": sorted((wf.get("name",""), wf.get("dimension",""), str(wf.get("conclusion")))
                 for wf in (ci_workflows or [])),
}, ensure_ascii=False, sort_keys=True)
snapshot_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

# key = f"{task_id}:{snapshot_hash}:{REVIEW_RUBRIC_VERSION}:{REVIEW_PROMPT_VERSION}:{REVIEW_ENGINE_VERSION}:{model}"
```

## H6. 评审铁律（`review.py#L427-L434`，Prompt 原文）

```text
1. 必须逐条检查每条 Rubric，一条都不能漏。
2. 每条判定都必须给出证据来源；没有证据支撑的判定一律 NEED_REVIEW，绝不判 PASS。
3. 三选一的运行证据都没有时，不得因为代码"看起来合理"就断定功能能跑通。
4. 不得伪造运行结果，不得替你设想学生没提交的效果。
5. 你不是来鼓励或教学的，只做客观评价。
6. FAIL 必须明确说清不达标的理由。
7. next_step 明确告诉学生：下一步需要补充哪种证据、或修正哪个不达标项。
```

## H7. 输出契约（`review.py#L460-L469`）

```json
{
  "criteria": [
    { "rubric_id": "rb_xxx", "status": "PASS | FAIL | NEED_REVIEW",
      "evidence": "依据的条目与来源", "reason": "判定理由" }
  ],
  "next_step": "下一步需补充的证据或修正项"
}
```

> 注意：schema 里**没有** `score` / `status`。这是"LLM 只做子判定、总分由代码算"的物理证据。

## H8. 存储表结构（`store.py`，可直接画 ER 图）

```sql
-- 真相源：每份提交一行
CREATE TABLE evaluations (
  submission_id TEXT PRIMARY KEY, student_id TEXT NOT NULL, task_id TEXT NOT NULL,
  project_id TEXT DEFAULT '', snapshot_hash TEXT DEFAULT '',
  rubric_version TEXT, prompt_version TEXT, engine_version TEXT, model TEXT,
  status TEXT NOT NULL, score INTEGER DEFAULT 0, passed INTEGER DEFAULT 0,
  ci_conclusion TEXT DEFAULT '', head_sha TEXT DEFAULT '', revision_json TEXT DEFAULT '',
  criteria_json TEXT DEFAULT '{}', created_at TEXT NOT NULL);

-- 缓存层：同输入同输出
CREATE TABLE review_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT, snapshot_hash TEXT, rubric_version TEXT,
  prompt_version TEXT, engine_version TEXT, model TEXT,
  response_json TEXT, created_at TEXT);
CREATE UNIQUE INDEX uq_review_result_key ON review_results(
  task_id, snapshot_hash, rubric_version, prompt_version, engine_version, model);

-- 熔断层：5 分钟
CREATE TABLE review_failures (
  review_key TEXT PRIMARY KEY, retry_after REAL NOT NULL, error TEXT, created_at TEXT);

-- 证据层：id 主键天然幂等
CREATE TABLE evidence (
  id TEXT PRIMARY KEY, task_id TEXT NOT NULL, rubric_id TEXT DEFAULT '',
  type TEXT NOT NULL, source TEXT DEFAULT '', content TEXT DEFAULT '',
  confidence REAL DEFAULT 1.0, created_at TEXT NOT NULL);
```

## H9. 前端消费（TypeScript，`TeachView.vue` 接口片段）

```ts
interface Project { project_id: string; title: string; description: string; stages: Stage[] }
interface Stage   { stage_id: string; title: string; objective: string; tasks: TaskItem[] }
interface TaskItem{ task_id: string; title: string; objective: string; skill?: string
                    completion_required: boolean; depends_on: string[] }
```

## H10. 可直接复刻的 YAML 输入样例（用于文章演示，非仓库原生格式）

> 仓库原生格式是 Python，但下面的 YAML 与 `Rubric` 字段一一对应，**仅作文章可读性演示**，需注明"等价改写"。

```yaml
rubric:
  id: rb_lit01_1
  task_id: lit_t01
  criterion: 脚本能正确统计并输出前 10 名
  required_evidence: [code, runtime]
  pass_condition: 代码中存在读取-计数-排序逻辑；运行输出含至少 10 条「人物 次数」
  weight: 2
  evaluation_role: acceptance
```

---

# I. 可绘制的架构图

## 图 1：评估链路主图（推荐作为文章首图）

```text
┌──────────── 引擎之外的现实世界 ────────────┐
│  学生本机开发 → push → GitHub 仓库          │
│  （可选）GitHub Actions 运行               │
│  （可选）部署到线上                         │
└───────────────┬───────────────────────────┘
                │ 痕迹
                ▼
        ┌──────────────────────────────────────────┐
        │ ① Evidence Collector                     │
        │  code_evidence.build_code_evidence()     │
        │   GitHub tree / key files / Actions / Issues
        │  review.collect_evidence()               │
        │   → {code, runtime, test, description,   │
        │      report, issue, deployment, visual…} │
        └───────────────┬──────────────────────────┘
                        ▼
        ┌──────────────────────────────────────────┐
        │ ② snapshot_evidence() → sha256[:16]      │
        │    + 3 个版本号 + model = 幂等 key        │
        └───────────────┬──────────────────────────┘
                        ▼
   ┌────────────────────┴────────────────────┐
   │ 熔断命中 → REVIEW_UNAVAILABLE（5min）      │
   │ 缓存命中 → 直接复用旧判定                  │
   └────────────────────┬────────────────────┘
                        ▼
   ┌──────────── 闸门 1 evidence_precheck ────────────┐
   │  仅 acceptance；缺硬证据 → forced NEED_REVIEW     │
   └────────────┬──────────────────┬──────────────────┘
                │ 可判定            │ 全缺证据
                ▼                  └──→ 零 LLM 返回 NEED_REVIEW
   ┌──────── 闸门 2 ci_direct_verdict ────────┐
   │  CI conclusion 同向 success/failure      │
   │  → PASS / FAIL（不经 LLM）               │
   └────────────┬─────────────────────────────┘
                │ 未直判的 Rubric
                ▼
   ┌──────── 闸门 3 LLM Reviewer ─────────────┐
   │  只输出逐条 criteria + next_step          │
   │  schema 无 score / status                 │
   └────────────┬─────────────────────────────┘
                ▼
   ┌──────── 闸门 4 compute_evaluation ───────┐
   │  acceptance → score / status（代码层）    │
   │  theory → learning_gaps（不改 status）   │
   │  reflection → retro（不改 status）       │
   └────────────┬─────────────────────────────┘
                ▼
   ┌──────── 落库 ────────┐
   │ evaluations（真相源） │
   │ review_results（缓存）│
   └──────────┬───────────┘
              ▼
   project_state → COMPLETED / IN_PROGRESS / BLOCKED
```

## 图 2：证据强度分层图

```text
强（system 权威，可直判）
 ├── CI build/test conclusion      → 可映射 PASS/FAIL
 ├── CI runtime conclusion          → 可映射 PASS/FAIL
 └── （外部）GitHub API 返回的确定性字段

中（客观但需语义解读，走 LLM）
 ├── code（仓库关键文件内容）      → 只证"写了什么"
 ├── trace（agent_trace.json 存在）
 └── report / issue（学生自己的记录）

弱（可选加分，永不作硬门槛）
 ├── deployment（在线地址）
 └── visual（截图事实，不评美观）

最弱（显式排除在硬证据之外）
 └── description（学生自述）
```

## 图 3：三种状态的判定树

```text
是否有 acceptance Rubric 缺硬证据？
 ├── 是 ──→ 该条 NEED_REVIEW（不调 LLM）
 └── 否 ──→ 是否有 CI 结论可直判？
             ├── 是 ──→ PASS / FAIL（不调 LLM）
             └── 否 ──→ LLM 逐条判定
                          └──→ compute_evaluation：
                                有 FAIL → FAIL
                                否则有 NEED_REVIEW → NEED_REVIEW
                                否则 PASS
```

## 图 4（可选）：持久化分层

```text
students ──1:N──> submissions ──1:1──> evaluations      （真相源 / 事件流）
                     │
                     └── id 被 evidence.id 引用（sha1(task:snapshot:type)）
review_results  = 缓存层（6 元组唯一索引，可删可重建）
review_failures = 熔断层（TTL 300s）
```

---

# J. 文章可以提出的技术观点

以下是可以作为**观点**（而非项目事实）输出的内容。每条都标注了它的项目依据，避免变成空谈。

## J1. Deliverable Evaluation 的第一原则是"证据先于判断"

**观点**：对交付物的评估，不应让模型先判断再找理由，而应"先确认证据齐备，再让模型判"。因为模型的第一个 token 一旦落下判定，后面的"理由"就只是事后合理化。

**项目依据**：`evidence_precheck()` 在 LLM 之前切断缺证据的条目（`review.py#L182-L234`），且缺证据时整条链**零模型调用**。

## J2. "总分"不能交给 LLM

**观点**：让 LLM 同时输出子判定和总分，会产生两个独立漂移源（子判定漂移 + 加权漂移），且总分不可复现。正确做法是把 `score` 从输出 schema 里彻底删掉。

**项目依据**：`ReviewLLMOutput` 只有 `criteria` / `next_step`；`compute_evaluation()` 是纯函数。

## J3. NEED_REVIEW 是第三态，不是"失败"或"待定"

**观点**：二值判定（通过/不通过）会强迫模型在证据不足时猜。引入第三态后，"证据不足"变成一种**可行动的产出**——它携带缺失清单，直接生成学生的下一步。

**项目依据**：`ReviewStatus` 三值；`next_step` 由 `missing` 自动拼装（`app.py#L867-L870`）。

## J4. 确定性前置：能被 system 判定的，绝不交给模型

**观点**：CI 结论是 GitHub 侧的确定性事实。把它交给 LLM 重述，只会引入噪声和成本。

**项目依据**：`ci_direct_verdict()`；保守策略——只要结论集合不是单一 `{"success"}` 或 `{"failure"}`，就退回 LLM（`review.py#L349-L359`）。

## J5. 幂等键应当由"证据快照"而非"会话/时间"定义

**观点**：用 session_id 或时间戳做缓存键，会导致同一份代码被反复评审；用证据内容的哈希做键，才能实现"内容寻址"的幂等。

**项目依据**：`snapshot_evidence()`；`state.py` 的 6 元组唯一索引；`Revision` 刻意排除在 key 之外。

## J6. 评估标准的"阻断权"应当显式建模

**观点**：把"这条标准不过会怎样"写进数据模型，而不是藏在权重里。交付类标准可阻断，理解类/反思类不应阻断。

**项目依据**：`EvaluationRole` 三值 + `compute_evaluation` 三分桶 + `project_state` 只认 `completion_required`。

## J7. 视觉证据必须被严格限权

**观点**：视觉模型只能输出"观察到的可读事实"，不能输出"好不好看"，更不能替代运行证据；且必须 fail-open（模型不支持时不影响主流程）。

**项目依据**：`format_visual_evidence()` 只渲染 `facts` / `uncertain` / 任务相关性 / 图片指纹；`optional_bonus` 含 `visual`；`app.py#L658-L688` 中任何视觉失败只跳过。

## J8. 错误归因隔离是评估系统的基本卫生

**观点**：平台故障（限流、超时、模型返回非法 JSON）绝不能被记进学生的评估结果。

**项目依据**：`llm_error_response(..., review=True)` 返回 `REVIEW_UNAVAILABLE`；message 明确写"系统故障，与你提交的项目无关"；且此分支不写 evaluations。

## J9. "证据存在性"检测需要强于字符串匹配

**观点**：仅凭文件名/关键字出现在文本中就登记证据，会制造"声明即证据"的漏洞。

**项目依据**：`trace` 的检测方式正是 `"agent_trace.json" in repo_code_text`（F3）；报告类证据依赖文件名白名单（F 系列）。

## J10. 无内建执行时，运行类判定的可靠性上限由外部决定

**观点**：如果评估系统自身不运行被测物，那么"它能跑"这一结论的可靠性上限，就等于它所依赖的外部证据（CI）的可靠性。承认这一点，比假装"AI 能看懂代码就知道能不能跑"更专业。

**项目依据**：Prompt 原文 `代码证据只能证明「写了什么」，不能证明「跑没跑通」`（`review.py#L393`）。

## J11. Response Evaluation 与 Deliverable Evaluation 的分工

**观点**：两者可以共用一套"证据 → 判定"的工程骨架，但证据类型、判定标准、失败语义完全不同——前者评"这段话是否合规/是否过早给答案"，后者评"这个产物是否达标"。混用一套 Rubric 会导致两个目标互相污染。

**项目依据**：本项目两套并存且物理隔离——`response_validator.validate()` 的 5 项检查（hint/role/context/learning/safety）作用于 `AiResponse`；`review.py` 作用于 `Submission`。二者共享的只是同一种工程范式（先约束输出 schema，再代码层判定）。

---

# K. 不能对外声称的内容

以下内容**若写进文章即为不实**，请逐条规避。

## K1. 关于能力

| ❌ 不可声称 | 真相 |
| --- | --- |
| "系统会执行/运行学生的代码来验证" | 无沙箱、无进程执行、无测试运行器。执行完全在引擎之外 |
| "系统会自动跑测试" | 从不。测试结果只能来自 GitHub Actions 或学生自述 |
| "做了静态分析 / AST 解析 / 类型检查" | 无。只做文本读取与截断 |
| "多 Agent 协作 / 规划器 / 反思循环 / 辩论" | 无。单次 LLM 调用 + 最多 2 次校验重试 |
| "自动修复学生代码" | 明确禁止（导师铁律 5、评审铁律 4） |
| "支持任意语言/任意学科的课程" | 证据体系（code/CI/runtime/trace/report/issue）是编程导向；`SkillKey` 13 项全为计算机类 |
| "用 RAG 做验收判定" | RAG（`chunks.jsonl` + `chunk_key`）**只用于 AI 导师的教学材料检索**，完全不参与评审链 |
| "有形式化验证 / 可证明正确" | 无 |

## K2. 关于效果

| ❌ 不可声称 | 真相 |
| --- | --- |
| "评估准确率 XX%" / "精确率/召回率/F1" | 无标注集、无基准测试、无混淆矩阵 |
| "与人工评分一致性 Kappa=XX" | 无此项实验 |
| "误判率很低" | 无任何量化数据；F 系列已列出多个结构性误判面 |
| "完全自动化，无需人工" | 存在 NEED_REVIEW 第三态，需学生补证 |
| "已在 X 名学生 / X 份提交上验证" | 本地库为空；生产库数据本次不可访问。**不要编造规模** |
| "LLM 判定是确定性的" | 温度 0.4，非确定性；靠幂等缓存获得"同输入同输出"，不是模型本身确定 |

## K3. 关于架构

| ❌ 不可声称 | 真相 |
| --- | --- |
| "Task 上的 `evidence_required` 控制验收" | 引擎 0 处读取（G1） |
| "Task 上的 `hints` 控制提示" | 全仓库 0 处读取 |
| "有 coach / debugger 两套独立导师模式" | `MODE_PROMPTS` 实际只剩 `tutor`；调试是内部 behavior |
| "课程数据是 JSON/YAML/Markdown 配置" | 是 Python 代码（Pydantic 对象常量） |
| "有一个课程管理后台 / CMS" | 无。加课程 = 改 Python 文件 |
| "数据库里有课程表" | 无。课程不进数据库 |

## K4. 关于案例

| ❌ 不可声称 | 真相 |
| --- | --- |
| "某学生提交后系统判定为……" | 本地库 0 行、生产库不可访问，**没有生产案例回放** |
| "这个案例解决了真实误判" | 只能写"代码里存在如下防线/测试覆盖如下路径" |
| 引用生产数据（学生数、评审数、通过率） | 无数据来源 |

## K5. 表述替换建议

| 想说的 | 改成 |
| --- | --- |
| "系统会自动验证代码能不能跑" | "系统通过 CI 结论或学生提供的运行说明来确认可运行性" |
| "我们用 AI 准确评估了学生的项目" | "我们把判定拆成「代码层可复现聚合」与「模型逐条语义判定」两层" |
| "这是一个多 Agent 评估系统" | "这是一个单模型 + 确定性前后置约束的评估流水线" |
| "评估准确率很高" | "缺证据时系统不猜——直接返回 NEED_REVIEW 并要求补证" |
| "支持全学科课程" | "课程模型与证据体系当前面向编程类交付物" |

---

# 附：一页速查（写作时放在手边）

```text
判定四闸门：precheck(确定性) → ci_direct(确定性) → LLM(主观) → compute(确定性)
三种状态：PASS / FAIL / NEED_REVIEW
三种角色：acceptance(阻断) / theory(Learning Gap) / reflection(Retro)
三个版本：REVIEW_RUBRIC_VERSION=2 / REVIEW_PROMPT_VERSION=1 / REVIEW_ENGINE_VERSION=2
幂等键：sha256(证据+CI+task_id)[:16] × 3版本 × model，存 review_results（唯一索引）
真相源：evaluations（每提交一行）；review_results 只是缓存
最硬的证据：CI conclusion
最弱的证据：description（被排除在硬门槛外，但仍进 Prompt —— 这是漏洞面）
最强的一句话：代码证据只能证明「写了什么」，不能证明「跑没跑通」
最大的局限：引擎不执行学生代码
最不能写的：准确率、规模、多 Agent、沙箱执行、RAG 参与验收
```

---

**素材包结束。** 全部结论可对照下列文件核验：
[review.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/review.py) ·
[app.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py) ·
[store.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/store.py) ·
[schemas.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/schemas.py) ·
[code_evidence.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/code_evidence.py) ·
[llm_client.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/llm_client.py) ·
[_test_phase7.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/_test_phase7.py) ·
[_test_phase8.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/_test_phase8.py) ·
[_test_v11_fix.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/_test_v11_fix.py)