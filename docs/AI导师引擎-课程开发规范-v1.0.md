# AI导师引擎课程开发规范 v1.0

> 本文档的唯一目的：告诉另一个 AI（或课程作者）**如何按照当前 AI 导师引擎的真实实现方式**设计并接入一门新课程。
>
> 编写原则：所有结论均来自对当前仓库代码的实际追踪；**已实现** 与 **建议未来增加** 严格区分；不虚构字段。
>
> 事实基准版本：`ai_engine/schemas.py`（382 行）、`ai_engine/course_data.py`（874 行）、`ai_engine/course03_data.py`（537 行）、`ai_engine/review.py`（475 行）、`ai_engine/app.py`、`ai_engine/store.py`。
>
> 阅读顺序建议：先读 **Part A** 建立对系统的准确认知，再读 **Part B** 拿模板开写。

---

# Part A · 现状分析（系统真实事实）

## A1. 完整链路追踪：课程从代码到学生屏幕

一条课程数据从「定义」到「被 AI 导师讲授 / 被验收」，实际经过 6 段。每一段对应的真实文件与函数如下。

### 第 1 段：课程定义（数据源 = Python 代码，不是 JSON/YAML/数据库）

| 文件 | 内容 |
| --- | --- |
| `ai_engine/course_data.py` | `_COURSES`（course_id → 元信息 dict）、`_PROJECT_BUILDERS`（project_id → 构造函数）、`_P4_REQUIRED`、`_P4_DEPENDS_ON` |
| `ai_engine/course03_data.py` | `COURSE_003` 元信息 + `build_project_mcp_build()` / `build_project_mcp_test()` |
| `data/chunks.jsonl` | RAG 教学材料语料（每行一个 JSON chunk，含 `section_path` / `text` 等字段） |
| `frontend/public/courses/*.webp` | 课程选课卡配图（前端静态资源，非后端数据） |

注册动作在 `course_data.py` 末尾完成：

```python
_PROJECT_BUILDERS = {"project_chatbot": _chatbot_project, "project_agent": _agent_project}
_COURSES = {"course_001": {...}, "course_002": {...}}
from course03_data import COURSE_003, build_project_mcp_build, build_project_mcp_test
_PROJECT_BUILDERS["project_mcp_build"] = build_project_mcp_build
_PROJECT_BUILDERS["project_mcp_test"]  = build_project_mcp_test
_COURSES["course_003"] = COURSE_003
```

**关键事实：全部课程数据都是 Python 函数返回的 Pydantic 对象，没有 CMS、没有数据库课程表、没有 Markdown 课程文件。**

### 第 2 段：后端装配与配置下发

```text
GET /api/ai/config   (app.py L240)
  └─ list_courses()  (course_data.py L790)
       └─ get_project(project_id)  (course_data.py L805)
            ├─ _PROJECT_BUILDERS[pid]()      # 构建
            ├─ _apply_p4_config(proj)        # 写入 completion_required / depends_on
            └─ _project_cache[pid] = proj    # 缓存（进程生命周期内只构建一次）
       └─ _project_summary(proj)             # 裁剪成前端要用的字段
```

`_project_summary()` 的输出即前端契约（`course_data.py` L772）：

```python
{
  "project_id", "title", "description",
  "stages": [{
     "stage_id", "title", "objective",
     "tasks": [{ "task_id", "title", "objective", "skill",
                 "completion_required", "depends_on" }]
  }]
}
```

`/api/ai/config` 的完整返回（`app.py` L240-259）：

```json
{ "ok": true, "data": {
    "models": [{"model": "deepseek-flash", "label": "DeepSeek V4.1（默认）"}],
    "config_source": "xkz_settings_v1",
    "vision_models": ["..."],
    "modes": ["tutor", "coach", "debugger"],
    "hint_levels": {"0": "仅引导", "1": "提示方向", "2": "思路步骤", "3": "具体做法", "4": "答案片段", "5": "完整方案"},
    "courses": [ { "course_id", "title", "description", "projects": [ ... ], "img", "img_pos" } ],
    "projects": [ ... ]
} }
```

### 第 3 段：前端渲染（完全数据驱动）

`frontend/src/views/TeachView.vue`：

| 位置 | 行为 |
| --- | --- |
| L844-870 `onMounted` | 拉 `GET /api/ai/config`，写入 `courses` / `projects` |
| L724-757 `wheelList` | 转盘卡片 = 真实课程 + 固定末位占位卡「更多课程」 |
| L826-842 `loadProject()` | 由 `stages[].tasks[]` 渲染任务清单（无硬编码任务） |
| L919-921 `isTaskDone` | 读 `student.completed_tasks` |
| L1215-1255 | 提交验收，`POST /api/ai/review`；PASS 后写 `completed_tasks` |

**结论：新增课程不需要改前端。** 唯一残留硬编码在 `doEnterCourse()`（L780-801），只影响成就解锁映射（`course_001 → eva_unit01`、`course_002 → stand_in_heaven`），不影响课程能否运行。

### 第 4 段：AI 导师讲授

```text
POST /api/ai/teach   (app.py L331)
  ├─ student = req.student or 新建
  ├─ ctx = build_context(req, student)         # context_builder.py
  │     ├─ get_task / get_stage / get_project(_of_task) / get_rubrics
  │     ├─ calculate_hint_level(attempt_count, user_requested_answer)   # hint.py
  │     └─ _retrieve_material(task.chunk_key)  # 按 section_path 前缀检索 chunks.jsonl，≤6 条
  ├─ behavior = route_behavior(req.user_input, sess)   # prompts.py：decompose/advance/debug
  ├─ ctx.behavior = behavior; ctx.code_evidence = build_code_evidence(...)  # 可选
  ├─ system = build_system_prompt(ctx, "tutor")        # prompts.py
  ├─ LLMClient.teach(messages, max_tokens=MAX_TOKENS_BY_BEHAVIOR[behavior])
  ├─ validate(resp, ctx)                               # response_validator.py 5 项检查
  └─ db.save_session(...)
```

### 第 5 段：验收

```text
POST /api/ai/review   (app.py L610)
  ├─ build_code_evidence(repo_url, task_id, code_context, client)   # code_evidence.py
  │     → { ok, repo, default_branch, head_sha, file_count, key_files,
  │         evidence_text, readme_run_cmd, ci, issues }
  ├─ vision.analyze(visual_images)            # 可选，失败不阻塞
  ├─ available = collect_evidence(submission, evidence_text, visual)  # review.py L69
  ├─ snapshot = snapshot_evidence(available, ci, task_id)   # sha256[:16] 幂等键
  ├─ 熔断检查（review_failures，5 分钟）→ 幂等缓存检查（review_results）
  ├─ pre = evidence_precheck(rubrics, available)      # 仅 acceptance 硬门槛
  ├─ 逐条分流：ci_direct_verdict(rubric, ci)  命中→代码层直判；未命中→进 LLM
  ├─ LLMClient.review(...)  → ReviewLLMOutput（只含逐条 criteria + next_step）
  ├─ evaluation = compute_evaluation(criteria, rubrics, next_step)    # 代码层聚合 score/status
  ├─ db.save_review_result(...) + db.add_evaluation(...)              # 必须先落库
  └─ attach_student_state(data, ...)                                  # 再挂学生态（不可污染缓存）
```

### 第 6 段：学习记录

| 产物 | 来源 | 关键约束 |
| --- | --- | --- |
| Project State | `project_state.compute_project_state()` | 只认 `completion_required=True` 的 Task；空集合 → `completion_defined=False`，**不做完成判定** |
| Learner State | `learner_state.compute_learner_state()` | 四态 UNSEEN/EXPOSED/PRACTICED/EVIDENCED；**EVIDENCED ≠ MASTERED** |
| Learning Gap | `evaluations.criteria_json.learning_gaps` | 只有 `theory` 角色的 FAIL 会产生 |
| 项目复盘 | `student_record.build_project_retro()` | 零 LLM，纯模板 |
| 简历文本 | `career.build_career_text()` | 只用**已通过验收**任务的 `resume_points`；过滤"学习属性"文本 |

---

## A2. 系统真实课程模型（逐字段）

层级：**Course → Project → Stage → Task → Rubric**。

> 命名对照：需求文档里的 **Chapter = Stage**，**Lesson = Task**。系统**不存在** Module / Lesson / Chapter 这些类型。

### A2.1 Course（已确认，`schemas.py` L112）

| 字段 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `id` | str | 必填 | 课程 id，如 `course_004` |
| `title` | str | 必填 | 课程名 |
| `description` | str | `""` | 课程简介（**前置知识/难度只能写在这里的文本里**） |
| `projects` | list[str] | `[]` | project_id 列表（一门课可有多个项目，见 course_003） |

**`_COURSES` dict 额外携带（仅用于选课卡，不属 Pydantic Course）：**

| 键 | 说明 |
| --- | --- |
| `img` | 选课卡配图路径，如 `/courses/lit.webp`（放在 `frontend/public/courses/`） |
| `img_pos` | 配图 `object-position`，如 `center 30%` |

**当前不存在（不要写，写了也不会被读取）：** `difficulty`、`prerequisite`、`estimated_time`、`tags`、`project_type`、`objectives`、`cover`、`author`、`version`。

### A2.2 Project（已确认，`schemas.py` L120）

| 字段 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `id` | str | 必填 | project_id，全局唯一 |
| `title` | str | 必填 | 项目名 |
| `description` | str | `""` | 项目简介 |
| `stages` | list[Stage] | `[]` | 阶段列表 |
| `tasks` | list[Task] | `[]` | 全部任务（**扁平存放**，靠 `stage_id` 归属阶段） |
| `rubrics` | list[Rubric] | `[]` | 全部验收标准（**扁平存放**，靠 `task_id` 归属任务） |
| `source_url` | str | `""` | 关联外部文档 |
| `resume_intro` | str | `""` | 简历项目简介 |
| `resume_role` | str | `"独立开发"` | 简历角色（标题行） |
| `resume_tech` | list[str] | `[]` | **纯技术名词**列表 |
| `resume_metrics` | list[str] | `[]` | 额外量化指标 |

### A2.3 Stage（= Chapter，`schemas.py` L150）

| 字段 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `id` | str | 必填 | stage_id，建议加项目前缀避免碰撞（如 `lit_stage1`） |
| `title` | str | 必填 | 阶段名（现有课程用 `① …` 序号风格） |
| `order` | int | 必填 | 阶段顺序 |
| `objective` | str | `""` | 阶段目标 |
| `tasks` | list[str] | `[]` | task_id 列表（顺序即学生看到的顺序，但真正排序按 Task.order） |

**当前不存在：** `duration`、`week`、`videos`、`materials`、`prerequisite`。

### A2.4 Task（= Lesson，`schemas.py` L178）

| 字段 | 类型 | 默认 | 是否被引擎消费 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | str | 必填 | ✅ | **必须全局唯一**（`get_task()` 遍历所有项目按 id 查找） |
| `title` | str | 必填 | ✅ | 任务名 |
| `stage_id` | str | 必填 | ✅ | 所属阶段 id |
| `order` | int | 必填 | ✅ | 阶段内顺序 |
| `objective` | str | `""` | ✅ | 注入 AI 导师 Prompt 的「任务目标」 |
| `steps` | list[str] | `[]` | ✅ | 注入 Prompt 的「任务步骤」 |
| `rubric_ids` | list[str] | `[]` | ✅ | 决定该任务送审哪些 Rubric |
| `skill` | SkillKey? | `None` | ✅ | 决定 Learner State 技能归属 |
| `chunk_key` | str | `""` | ✅ | RAG 检索前缀，匹配 `chunks.jsonl` 的 `section_path` |
| `code_context` | CodeContext? | `None` | ✅ | 指导代码证据检索（`rank_candidate_files`） |
| `completion_required` | bool | `False` | ✅（由 `_P4_REQUIRED` 覆盖） | 是否项目完成必做 |
| `depends_on` | list[str] | `[]` | ✅（由 `_P4_DEPENDS_ON` 覆盖） | 仅生成 blocked_reason，不阻断 |
| `source_url` | str | `""` | ⚠️ 弱 | 仅进 TeachContext.source_url |
| `interview_questions` | list[InterviewQuestion] | `[]` | ⚠️ 弱 | 由 `GET /api/ai/interview` 单独消费，不进评审 |
| `resume_points` | list[ResumePoint] | `[]` | ✅ | 简历生成素材 |
| `evidence_required` | Literal | `"none"` | ❌ **未被消费** | **声明性字段**：验收链只读 `Rubric.required_evidence`，此字段不控制任何验收 |
| `hints` | dict[int,str] | `{}` | ❌ **未被消费** | 全仓库无任何读取点；提示程度由 `hint.py` 的 hint_level + Prompt 的提示等级表驱动 |

> ⚠️ **最容易被误用的字段**：`evidence_required` 和 `hints`。它们存在于模型中、课程数据里也大量填写，但**引擎不读取**。想控制验收，只能改 `Rubric.required_evidence`；想控制提示，只能靠任务难度与 `steps` 的颗粒度。（建议：保留填写习惯以便未来启用，但不要以为它生效。）

### A2.5 Rubric（验收的最小单元，`schemas.py` L204）

| 字段 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `id` | str | 必填 | 建议 `rb_<task>_<n>`，全局唯一 |
| `task_id` | str | `""` | 归属任务 |
| `criterion` | str | `""` | 验收条件标题（进 Prompt 与前端评审卡） |
| `description` | str | `""` | 详细说明 |
| `required_evidence` | list[str] | `[]` | **硬门槛**：取值 ∈ `code / runtime / test / url / description / visual / deployment / report / issue / trace / build / ci`（见 A3.3） |
| `pass_condition` | str | `""` | 达标条件（写给 Reviewer 看的判定尺子） |
| `weight` | int | `1` | 权重，参与 score 加权 |
| `visual_check` | `"none"\|"supported"` | `"none"` | 该条是否有可截图观察的事实（可选增强） |
| `visual_pass_condition` | str | `""` | 有截图时应观察到什么事实 |
| `evaluation_role` | `acceptance\|theory\|reflection` | `acceptance` | 在**项目完成判定**中的职责 |

### A2.6 辅助模型

```python
CodeContext:       keywords: list[str]  likelyFiles: list[str]  searchPatterns: list[str]
ResumePoint:       point: str  purpose: str = ""  result: str = ""
                   kind: "architecture"|"stability"|"delivery"|"engineering" = "delivery"
InterviewQuestion: id: str  question: str  answer_anchor: str  hint: str = ""
                   type: "explain"|"debug"|"transfer" = "explain"
```

### A2.7 SkillKey 枚举（13 个，`schemas.py` L44）

```text
git  prompt  env_setup  debug  prd  ui_design  vibe_coding
project_dev  ai_assisted  workflow  deployment  rag  paper_writing
```

**已确认不存在文学/人文类技能。** 面向文学院的课程只能复用现有键（见 A6 限制说明）。

---

## A3. 验收机制完整拆解（本文档最重要的部分）

### A3.1 判定「完成任务」的真实入口

前端点「提交验收」→ `POST /api/ai/review`。系统内部有 **4 道闸门**，顺序固定：

```text
闸门 1  evidence_precheck   证据缺失 → 直接 NEED_REVIEW，不调 LLM      【确定性】
闸门 2  ci_direct_verdict   CI 结论可直判 → PASS/FAIL，不调 LLM        【确定性】
闸门 3  LLM Reviewer        逐条判定 PASS/FAIL/NEED_REVIEW            【AI 主观】
闸门 4  compute_evaluation  按 weight 聚合 score/status               【确定性】
```

### A3.2 确定性验收 vs AI 主观判断

| 类型 | 组件 | 输入 | 输出 | 是否可复现 |
| --- | --- | --- | --- | --- |
| **确定性** | `evidence_precheck()` | `Rubric.required_evidence` × `available` 证据类型集合 | `forced_needs_review[]` | ✅ 同输入必同输出 |
| **确定性** | `ci_direct_verdict()` | Rubric 所需证据类型 × GitHub Actions `conclusion` | `PASS` / `FAIL` / `None` | ✅ |
| **确定性** | `compute_evaluation()` | 逐条 criteria | `score` / `status` | ✅ 同证据同分 |
| **确定性** | `snapshot_evidence()` | 证据文本 + CI 结论 + task_id | `sha256[:16]` 幂等键 | ✅ |
| **主观** | `LLMClient.review()` | Prompt（含 Rubric + 证据全文） | 逐条 `criteria` + `next_step` | ⚠️ 有 JSON 模式 + Pydantic + 语义校验 + 最多 2 次重试，但仍非严格可复现（幂等缓存兜底） |

**LLM 无权决定 `score` / `status`**：`ReviewLLMOutput` 里根本没有这两个字段；`compute_evaluation()` 在代码层按 weight 加权聚合。这是防"模型输出漂移"的核心设计。

### A3.3 证据类型与可收集性（`collect_evidence`，`review.py` L69）

| 证据键 | 来源 | 是否硬门槛候选 | 备注 |
| --- | --- | --- | --- |
| `code` | GitHub 仓库拉取的关键文件内容 + 学生粘贴的代码 | ✅ | 只能证明"写了什么"，**不能证明"跑没跑通"** |
| `runtime` | ① 部署地址 ② 学生自述里含启动命令（`detect_run_cmd`） ③ CI runtime 维度 | ✅ | 三选一即可 |
| `test` | CI test 维度结论 | ✅ | |
| `url` | 仅提供 GitHub 链接但未拉取成功 | ✅ | 语义弱，一般别用 |
| `description` | 学生自述说明 | ❌ **不算硬证据**（`_missing_evidence` 与 `precheck` 都排除它） | |
| `trace` | 仓库中出现 `agent_trace.json` | ✅ | 课程 02 引入 |
| `report` | 仓库内报告文件（`TEST_REPORT.md` 等，被 `_assemble` 打标 `【学生测试报告/问题记录】`） | ❌ **可选加分** | 课程 03 引入 |
| `issue` | 仓库 GitHub Issues（被 `_assemble` 打标 `[GitHub Issues]`） | ❌ **可选加分** | 课程 03 引入 |
| `visual` | 截图经视觉模型分析出的**事实文本**（原图不落盘） | ❌ **可选加分（永不作硬门槛）** | |
| `deployment` | 在线部署地址 | ❌ **可选加分** | |
| `build` / `ci` | CI build 维度结论 | ✅ | 与 `_CI_DIM_TO_EVIDENCE` 对应 |

`optional_bonus = {"deployment", "visual", "report", "issue"}` —— 这四类**永远不会因为缺失而阻塞判定**。

### A3.4 `evidence_precheck` 的真实规则（`review.py` L182）

```text
对每条 Rubric：
  1) evaluation_role != acceptance  → 直接 passable（theory/reflection 永不因缺证据阻塞）
  2) needed = required_evidence - {deployment, visual, report, issue}
  3) needed 为空 → passable
  4) missing = needed - available 的键；再去掉 description
  5) missing 非空 → forced NEED_REVIEW，带上 missing 与可读 reason
若某条 Rubric 的 visual_check == "supported" 且缺 runtime，
  reason 追加提示：（运行截图仅作辅助证据，不能替代运行证据）
```

### A3.5 `ci_direct_verdict` 的真实规则（`review.py` L304）

```text
1) evaluation_role != acceptance → None（不直判）
2) needed = required_evidence - {deployment}
   若 needed 为空，或与 {description, code} 有交集 → None（语义判定必须交给 LLM）
3) 逐个证据类型找 CI 维度：build / test / runtime
   任一类型无对应维度、或工作流无 conclusion → None
4) 所有维度结论集合：
   == {"success"}  → PASS（evidence: "CI 自动验收证据（system 判定）：…"）
   == {"failure"}  → FAIL
   其他（混合 / startup_failure / neutral / cancelled / timed_out）→ None
```

### A3.6 `compute_evaluation` 的真实规则（`review.py` L240）

```text
按 evaluation_role 三分桶：
  theory     未 PASS → learning_gaps[]（永不改 status）
  reflection 全部     → reflection[]（永不改 status）
  acceptance 全部     → criteria[]（唯一决定 score/status 的桶）

score  = round(Σ acceptance 中 PASS 的 weight / Σ acceptance 的 weight × 100)
status = 有 FAIL → FAIL；否则有 NEED_REVIEW → NEED_REVIEW；否则 PASS
```

> **`criteria` 数组只含 acceptance 条目** —— 这是前端评审卡与简历通过率的统一口径。

### A3.7 三个角色的语义（`EvaluationRole`，冻结基线 TOTAL=81：acceptance=64 / theory=14 / reflection=3）

| 角色 | 判定依据 | 失败后果 | 有阻断权 |
| --- | --- | --- | --- |
| `acceptance` | **客观可核验的交付证据**（code / CI / runtime / report / issue） | 任务 FAIL，项目不可 COMPLETED | ✅ |
| `theory` | 对知识、原理、方法、排障技能的理解（多为 `description` 证据） | 产出 Learning Gap，技能状态回落 | ❌ |
| `reflection` | 过程记录、体验反馈、边界说明、复盘 | 记录进 Project Retro | ❌ |

**分类依据是"这条 Rubric 到底在验证什么（证据类型）"，不是文字长相。** 同一 Task 内允许混合角色（`c3_t08` = acceptance + reflection）。五个已冻结的边界样本：

```text
rb_link_2   → theory      排障技能（证据 description + runtime）
rb_c3t03_2  → theory      痛点理解（属 Project Reflection）
rb_c3t05_1  → acceptance  验证实现是否真的区分 4 种记忆（证据 code + runtime）
rb_c3t08_2  → acceptance  验证跨会话恢复是否真的发生（证据 runtime）
rb_c3t09_3  → acceptance  验证是否交付了规定的测试报告（证据 report）
```

### A3.8 验收结果如何保存（`store.py`）

SQLite（WAL），文件 `/opt/xkz-agent/data/engine.db`。相关表：

| 表 | 作用 |
| --- | --- |
| `review_results` | **幂等缓存**（key 含 rubric/prompt/engine 版本 + model + snapshot_hash） |
| `review_failures` | 失败熔断（5 分钟） |
| `evaluations` | **真相源**：一份提交一行，含 `criteria_json`（内含 learning_gaps/reflection）、`ci_conclusion`、`head_sha` |
| `submissions` | 提交存档（含 `revision_json`） |
| `evidence` | 证据存档（id = `sha1(task_id:snapshot:type)`，天然幂等） |
| `sessions` | 对话历史 |

**版本常量（`store.py`，改规则必须手动 bump）：**

```python
REVIEW_RUBRIC_VERSION = "2"    # 改【已有】Rubric 的语义/分类时 bump
REVIEW_PROMPT_VERSION = "1"    # 改 review Prompt 时 bump
REVIEW_ENGINE_VERSION = "2"    # 改聚合逻辑时 bump
```

**硬约束：`Revision` 信息（`head_sha` / `revision_json`）只写入 `submissions` / `evaluations`，绝不进 review 缓存 key。** 目的：同一份代码重复提交能命中幂等缓存，不重复消耗学生 BYOK。

### A3.9 前端如何展示

`TeachView.vue` 提交后接 `POST /api/ai/review` 的返回：

```text
data.status        → 评审卡总状态（PASS/FAIL/NEED_REVIEW）
data.score         → 总分
data.criteria[]    → 仅 acceptance 的逐条判定
data.learning_gaps[] / data.reflection[]  → 非阻断角色的判定
data.next_step     → 补证指引
data.blocked_reason / data.project_state / data.learner_state  → 学生态（由 attach_student_state 追加）
```

PASS 时前端把 `task_id` push 进 `student.completed_tasks` 并 `saveStudent()`。

---

## A4. AI 导师 Agent 的课程依赖方式

### A4.1 「学生现在在学什么」是怎么告诉 AI 的

唯一通道是 `context_builder.build_context()` 组装的 `TeachContext`，再由 `prompts.build_system_prompt()` 拼进 System Prompt。逐项来源：

| 注入内容 | 真实来源 | 位置 |
| --- | --- | --- |
| 课程名 | `req.course_id`（**注意：注入的是 id 字符串，不是 title**，`context_builder.py` L56） | `【当前任务上下文】课程:` |
| 项目名 | `project.title` | 同上 |
| 阶段名 | `stage.title` | 同上 |
| 任务名 | `task.title` | 同上 |
| 任务目标 | `task.objective` | 同上 |
| 任务步骤 | `task.steps` | 同上 |
| 验收标准 | `get_rubrics(task_id)` → 只取 `r.criterion`（**不含 description / pass_condition**） | 同上 |
| 关联技能 | `task.skill.value` | 同上 |
| **教学材料** | `chunks_by_section_path(task.chunk_key)`，≤6 条，带 `[section] text` | `【教学材料】` |
| **代码证据** | `build_code_evidence(repo_url, task_id, task.code_context, client).evidence_text` | `【代码证据】` |
| 调试进度 | `session.debug_state` 渲染 | `【上一轮调试进度】` |
| 系统错误隔离 | `sess.last_system_error` | `【系统状态·重要】` |
| 提示等级 | `calculate_hint_level(attempt_count, user_requested_answer)` | `本次学生适用的提示等级为: N` |
| 内部行为 | `route_behavior(user_input, sess)` | `【当前行为：拆解/推进/调试】` |
| 对话历史 | `req.history`（前端每条消息带完整历史），上限 `HISTORY_CHAR_LIMIT=6000` 字符 | `_trim()`（system 永不丢） |

**降级行为（重要）**：`chunk_key` 匹配不到任何 chunk 时，`material=[]`，Prompt 写入 `(暂无检索到教学材料，请基于通用知识引导)` —— **不报错**。所以 `chunk_key` 是**可选增强**，不是接入必需项。

### A4.2 内部行为路由（用户无感）

系统对外只有一个 `Mode.tutor`（`MODE_PROMPTS` 实际只剩 `tutor`，`Mode` 枚举虽保留 `coach/debugger` 但无对应 Prompt 分支）。真正的分化在**内部行为**：

```text
route_behavior(user_input, sess)  (prompts.py L97)
  1. debug_state 存在且未到 done，且学生未说"已解决" → debug
  2. 消息命中 DEBUG_SIGNALS（traceback/error/cors/报错/跑不起来…）→ debug
  3. 会话第一问（history 为空）→ decompose
  4. 其余 → advance
```

| 行为 | 必输出字段 | max_tokens |
| --- | --- | --- |
| `decompose` | `hint_level` `hint` `leading_question` | 3500 |
| `advance` | `current_step`（可选 `hint`） | 1500 |
| `debug` | `suspected_cause` `verify_steps` `diagnostic_question` | 2500 |

`response_validator.validate()` 按行为做 Role Compliance 检查，不合格会带着问题重试。

### A4.3 AI 导师的输入 / 输出职责

**输入（课程侧必须提供）：** `objective`、`steps`、`criterion` 列表、（可选）`chunk_key`、`code_context`、`skill`。

**输出职责（`AiResponse`）：** `message` / `next_action` / `hints_used` + 行为条件字段。

课程作者必须遵守的角色边界（`prompts.CORE_POLICY` 铁律）：

1. 绝不替学生完成思考；2. 绝不鼓励学术造假；3. 只基于材料与任务信息作答；4. 每次给一个明确下一步；5. 学生代码有 bug 时引导发现而不是直接改好；6. **禁止要求学生提供截图/录屏作为验收证据**；7. **系统错误隔离**——模型/平台故障绝不算学生项目的问题。

### A4.4 「AI 导师」≠「AI 编程 Agent」

| | AI 导师（本引擎） | 学生做的 AI 编程 Agent（课程内容） |
| --- | --- | --- |
| 身份 | 平台能力，`POST /api/ai/teach` 的 LLM 调用 | 学生要交付的**项目产物**（如 course_002 的 CLI Agent） |
| 产出 | 引导文本 + 结构化 JSON | 可运行的代码 + 报告 |
| 是否被验收 | 否 | 是（通过 `code`/`runtime`/`trace` 证据） |
| 课程里怎么写 | 不写。它是**运行环境**，课程数据只给它喂上下文 | 写进 `objective`/`steps`/`Rubric` |

课程作者**不需要（也不能）为 AI 导师写 prompt**；你能控制的只有「喂给它的任务上下文」。

---

## A5. 完整参考样本

### A5.1 推荐样本：`course_002 / project_agent`（标准样板）

选择理由：结构最完整（4 Stage / 9 Task / 21 Rubric）、三种 EvaluationRole 齐备、用了 `code_context` + `chunk_key` + `resume_points` + `interview_questions`，是"标准"。

```text
Course course_002「Agent 实战（GitHub 项目分析）」
 └── Project project_agent「GitHub 项目分析 Agent」
      ├── Stage c2_stage1「① 认识 Agent」order=1
      │    ├── Task c2t01 认识 Agent 与项目骨架      order=1  skill=ai_assisted
      │    │     objective / steps / chunk_key / code_context / rubric_ids=[rb_c2t01_1..3]
      │    │     └── Rubric rb_c2t01_1 acceptance  evidence=[code]              weight=2
      │    │         Rubric rb_c2t01_2 theory      evidence=[description]       weight=1
      │    │         Rubric rb_c2t01_3 acceptance  evidence=[code]              weight=2
      │    │     resume_points=[ResumePoint(engineering)]
      │    └── Task c2t02 最小 Agent Loop（单工具）  order=2  skill=workflow
      │          └── Rubric ×4（1 theory + 3 acceptance，含 visual_check="supported"）
      ├── Stage c2_stage2「② 接入 GitHub 工具」order=2
      │    └── Task c2t03 / c2t04 / c2t05
      ├── Stage c2_stage3「③ 工具驱动执行」order=3
      │    └── Task c2t06 / c2t07 / c2t08（用到 trace 证据）
      └── Stage c2_stage4「④ 完成项目」order=4
           └── Task c2t09 带证据的项目分析报告
                 └── Rubric rb_c2t09_2 evidence=[trace]、rb_c2t09_4 evidence=[trace, description]
```

**参考样本中每个 Task 的五要素落点：**

| 概念 | 在系统中的字段 |
| --- | --- |
| Learning objective | `Task.objective` + `Stage.objective` |
| Student action | `Task.steps[]` |
| Deliverable | 由 `Rubric.required_evidence` + `pass_condition` 隐含定义（系统**没有**独立的 deliverable 字段） |
| AI Tutor role | 无专属字段；由 `objective` / `steps` / `criterion` 的写法 + 系统行为路由决定 |
| Acceptance | `Task.rubric_ids` → `Rubric`（criterion / required_evidence / pass_condition / weight / evaluation_role） |

### A5.2 最先进样板：`course_003`

`course003` 额外演示了三件前沿能力，是**做过程型/迭代型课程**的首选参考：

1. 一门课程挂**两个项目**（`project_mcp_build` → `project_mcp_test`），且**跨项目依赖** `c3_t08 depends_on c3_t07`。
2. 使用 `report` 与 `issue` 两类新证据（学生测试报告、GitHub Issue）。
3. `reflection` 角色的真实用法（`rb_c3t08_1`、`rb_c3t08_3`、`rb_c3t10_3`）。

### A5.3 抽象模板（脱离内容）

```text
Course(Course)
 └── Project(Project)
      ├── Stage(Stage, order=i, objective=…)
      │    └── Task(Task, stage_id, order=j, objective=…, steps=[…],
      │              skill=…, chunk_key=…, code_context=…,
      │              rubric_ids=[…], resume_points=[…])
      │         └── Rubric(Rubric, task_id, criterion, description,
      │                    required_evidence=[…], pass_condition, weight,
      │                    evaluation_role=acceptance|theory|reflection)
      └── [可选] 第二个 Project（同课程内的后续项目）
```

---

## A6. 系统对「文学院零基础课程」的支持与限制（必须如实告知）

| 维度 | 现状 | 结论 |
| --- | --- | --- |
| 课程能否新增 | `_COURSES` + `_PROJECT_BUILDERS` 完全数据驱动 | ✅ 支持 |
| 前端会不会自动出现 | `/api/ai/config` → 转盘 / 下拉 / 任务清单全自动 | ✅ 无需改前端 |
| 难度 / 前置知识展示 | Course 无 `difficulty` / `prerequisite` 字段 | ❌ 只能写进 `description` 文本 |
| 技能标签 | `SkillKey` 13 项全为计算机类 | ⚠️ 无文学类技能；只能复用（见下）或扩枚举 |
| 验收证据体系 | code / runtime / test / ci / trace / report / issue / visual | ⚠️ **编程导向**；纯文学论述**没有专属证据类型** |
| 强制 GitHub | `code` 证据依赖 `repo_url` + 公开仓库 | ⚠️ 不交代码就没有 code 证据；但可用 `report` + `description` 走通 |
| 纯主观美学评价 | Review 铁律明确**不评价美观**、`visual` 只作事实观察 | ❌ 文学审美类标准无法自动验收 |
| 课程间依赖 | 无课程级依赖字段（只有 Task 级 `depends_on`） | ⚠️ 仅能在 `description` 里写"前置：…" |
| 完成判定 | 只认 `completion_required` Task 全 PASS | ✅ 必须显式配置，否则项目永远不 COMPLETED |

### 面向文学院课程的**唯一可行落地范式**

把文学主题包装成 **"数字人文（Digital Humanities）小工具"**：学生用 Python 处理文本（如统计《红楼梦》人物共现、生成关系图、做文学地图 HTML），交付到 GitHub。

这样做的原因是：**它天然映射到现有证据体系**（`code` + `runtime` + `report`），无需引擎改造；而"写一篇文学赏析"这种交付物，在本引擎里**无法被自动验收**（既无 `code` 也无 `runtime`，只能全判 NEED_REVIEW）。

**推荐技能复用映射：**

| 文学课程任务性质 | 建议复用 `SkillKey` |
| --- | --- |
| 环境准备 / 装 Python、装依赖 | `env_setup` |
| 写文本分析脚本、数据处理 | `project_dev` |
| 做关系图 / 文学地图前端页面 | `ui_design` 或 `vibe_coding` |
| 需求梳理（要分析什么、输出什么） | `prd` |
| 用 AI 辅助读原文、提炼规则 | `ai_assisted` |
| 排查脚本报错 | `debug` |
| 交付到 GitHub、写 README | `git` |
| 产出分析报告 / 综述 | `paper_writing` |
| 多步流程编排（如清洗→统计→可视化） | `workflow` |
| 检索式问答（如"诗中某意象在哪出现"） | `rag` |

**建议未来增加（本文档不实施）：** 在 `SkillKey` 增加 `text_analysis` / `data_viz` / `digital_humanities` 等键；在 `Course` 增加 `difficulty` / `prerequisite` 字段。两者都需同步改 `schemas.py` 与前端展示，属于引擎改造，不在"新增课程"范围内。

---

# Part B · AI导师引擎课程开发规范 v1.0

## 1. 系统课程模型

```text
Course  ──1:N──>  Project  ──1:N──>  Stage  ──1:N──>  Task  ──1:N──>  Rubric
(课程)            (项目)            (阶段=Chapter)    (任务=Lesson)      (验收标准)
   │                                   │                │
   └ _COURSES[img, img_pos]            └ order          ├ order / stage_id
                                                       ├ objective / steps
                                                       ├ skill / chunk_key / code_context
                                                       ├ completion_required / depends_on
                                                       └ resume_points / interview_questions
```

**四条不可违反的模型规则：**

1. **层级只有 4 级**。没有 Module，没有 Lesson（Lesson = Task）。
2. **`tasks` 与 `rubrics` 扁平存放在 Project 上**，靠 `stage_id` / `task_id` 归属，不嵌在 Stage/Task 内部。
3. **`task_id` / `rubric_id` 必须全局唯一**（`get_task()` 遍历所有项目查找）。
4. **`completion_required` 必须显式配置**，否则项目无法判定 COMPLETED。

---

## 2. Course 模板

```python
# 追加到 ai_engine/course_data.py 的 _COURSES（或独立文件后 import 注册）
_COURSES["course_004"] = {
    "title": "古典文学探索器",
    "description": (
        "面向零基础同学的数字人文入门：用 Python 统计古典诗词的意象与用字规律，"
        "做成一个可以查询、可以看图的小工具。"
        "前置：无需编程基础，会打字、会用浏览器即可。"
        "预计投入：约 6 小时。"
    ),
    "projects": ["project_lit_poem"],
    "img": "/courses/lit_poem.webp",     # 图片放 frontend/public/courses/
    "img_pos": "center 30%",
}
```

**编写要点：**

- `description` 是唯一能承载"难度 / 前置知识 / 预计时长 / 适合人群"的地方（因为没有对应字段）。
- `projects` 可以是 1 个（如 course_001/002）或 2 个（如 course_003）。
- `img` 可省略，前端会走默认占位图（`wheelList` 里 `c.img || '/courses/more.webp'`）；但建议提供。

---

## 3. Chapter（Stage）模板

```python
stage1 = Stage(
    id="lit_stage1",                       # 建议带项目前缀，避免跨项目冲突
    title="① 认识文本数据",
    order=1,
    objective="把一首诗、一本小说看成可以被程序处理的数据，跑通第一个统计脚本。",
    tasks=["lit_t01", "lit_t02"],
)
```

**编写要点：**

- 一个 Stage 建议 1–4 个 Task。参考数据：course_001 = 3 Stage / 5 Task；course_002 = 4 Stage / 9 Task；course_003 = 5 Stage / 12 Task。
- `objective` 会注入 AI 导师的上下文（**但只注入 `stage.title`，`objective` 目前不进 Prompt**，见 `context_builder.py` L58）。它主要服务前端展示与课程作者自我校验。
- 序号风格建议沿用 `① ② ③`，与现有课程视觉一致。

---

## 4. Task 模板

```python
task_t01 = Task(
    id="lit_t01",
    title="数一数：谁出现得最多",
    stage_id="lit_stage1",
    order=1,
    objective=(
        "用 Python 读取一份《红楼梦》人物出场章节表，统计每个人物的出场次数，"
        "打印出前 10 名。要求脚本能重复运行，且不依赖任何手工改动的数据。"
    ),
    steps=[
        "建项目目录与虚拟环境（python -m venv .venv），激活后安装所需依赖",
        "准备数据文件（课程提供的人物-章节 CSV 或 JSON），放进项目目录",
        "写 main.py：读取数据 → 用字典累加计数 → 用 sorted 取前 10 → 打印",
        "运行脚本两次，确认两次输出完全一致（可重复）",
    ],
    skill=SkillKey.project_dev,                 # 无文学类技能，按 A6 映射表复用
    chunk_key="古典文学探索器 > T01 词频统计",   # 匹配 chunks.jsonl 的 section_path；可选
    code_context=CodeContext(                   # 可选，但强烈建议（提升代码证据命中率）
        keywords=["read", "csv", "dict", "count", "sorted", "print"],
        likelyFiles=["main", "analyze", "utils"],
        searchPatterns=["open\\(", "Counter", "sorted\\("],
    ),
    rubric_ids=["rb_lit01_1", "rb_lit01_2"],
    resume_points=[
        ResumePoint(
            point="实现可重复运行的文本统计脚本（读取 → 计数 → 排序输出）",
            purpose="让统计结果可被第三方复现",
            result="形成了可复用的文本分析基础脚本",
            kind="delivery",
        ),
    ],
)
```

**Task 编写检查清单：**

- [ ] `objective` 写"学生要做出什么"，而不是"学生要学会什么"（后者无法验收）。
- [ ] `steps` 每步对应一个**可验证产出**（文件、命令输出、截图可见结果）。
- [ ] `objective` / `steps` 里出现的每个要求，都要能对应到至少一条 `Rubric`。
- [ ] 需要代码证据 → 学生在 Task 里有"推到 GitHub"这一步（否则 `repo_url` 为空，`code` 证据永远缺失）。
- [ ] `completion_required` **不要写在 builder 里**，统一在 `_P4_REQUIRED` 配置（见第 11 章）。
- [ ] `evidence_required` / `hints` 可填但**不生效**，不要依赖它们。

---

## 5. Deliverable 模板

**系统没有独立的 Deliverable 字段。** 交付物由两处共同定义：

1. `Task.objective` + `Task.steps` —— 用人话告诉学生要交什么；
2. `Rubric.required_evidence` + `Rubric.pass_condition` —— 用机器能核的方式约束"交东西交到什么程度"。

**四种标准交付物形态（按可验收强度排序）：**

| 形态 | 需要的证据 | 学生动作 | 适用 |
| --- | --- | --- | --- |
| A. 可运行代码 + 运行说明 | `code` + `runtime` | 推到 GitHub + 自述启动命令 | 首选，强度最高 |
| B. 代码 + 测试报告 | `code` + `report` | 推到 GitHub，仓库根目录放 `TEST_REPORT.md` | 过程型任务 |
| C. 代码 + CI | `code` + `ci` + `test` | 配 GitHub Actions | 工程型任务 |
| D. 仅自述 | `description`（非硬证据） | 打字说明 | ⚠️ **只能做 theory/reflection，不能做 acceptance 硬门槛** |

> **红线：任何 `acceptance` 角色的 Rubric，`required_evidence` 不能只写 `["description"]`**。因为 `description` 在 `evidence_precheck` 与 `_missing_evidence` 里都被显式排除，写它等于"无硬证据要求"，Reviewer 只能靠自述判——这会让验收失去客观性。若某条标准只能靠自述，它就应该被设为 `theory` 或 `reflection`。

**报告类交付物的落盘约定**（课程 03 已验证）：文件名在 `code_evidence._KEY_REPORT` 名单内（如 `TEST_REPORT.md`、`report.md`、`bugs.md`、`retro.md`），放在**仓库根目录**，会被自动打标 `【学生测试报告/问题记录】` 并注入 Reviewer。内容上限 2500 字。

**Issue 类交付物**：学生的 GitHub Issues（自动过滤 PR，最多取 5 条，正文 800 字），打标 `[GitHub Issues]`。

---

## 6. Acceptance 模板

### 6.1 标准写法

```python
rubric_t01 = [
    # —— acceptance：交付物是否达标（有阻断权）——
    Rubric(
        id="rb_lit01_1",
        task_id="lit_t01",
        criterion="脚本能正确统计并输出前 10 名",
        description="读取数据文件，按出场次数排序，输出前 10 个人物及其次数",
        required_evidence=["code", "runtime"],
        pass_condition="代码中存在读取-计数-排序逻辑；贴出的运行输出含 ≥10 条「人物 次数」",
        weight=2,
        evaluation_role="acceptance",
    ),
    # —— theory：知识理解（无阻断权，未过则产 Learning Gap）——
    Rubric(
        id="rb_lit01_2",
        task_id="lit_t01",
        criterion="能说清为什么字典计数是合适的做法",
        description="理解「键=人物，值=次数」这一映射关系",
        required_evidence=["description"],
        pass_condition="自述能说明用字典按人物累加、用排序取前 N 的思路",
        weight=1,
        evaluation_role="theory",
    ),
    # —— 可选：有视觉观察点的 acceptance ——
    Rubric(
        id="rb_lit01_3",
        task_id="lit_t01",
        criterion="输出结果可读（能看出人物与次数）",
        description="运行输出格式清晰",
        required_evidence=["runtime"],
        pass_condition="运行输出中每行能看出人物与次数对应关系",
        weight=1,
        visual_check="supported",
        visual_pass_condition="终端截图中可见形如「宝玉 42」的多行统计结果",
    ),
]
```

### 6.2 Rubric 编写规则

| 规则 | 说明 |
| --- | --- |
| 一条 criterion 一个对象 | 不要一条 Rubric 塞多个验收点（会破坏逐条打分与 next_step 精度） |
| `required_evidence` 决定"能不能自动判" | 只写实际能从 GitHub/CI/学生自述拿到的类型。**写多了 = 必然 NEED_REVIEW** |
| `pass_condition` 要可核对 | 好的：`"贴出 SELECT 输出，能看到刚写入的记录"`；坏的：`"功能正常"` |
| `weight` 用 1 或 2 | 参考分布：核心交付 = 2，辅助 = 1。现有课程几乎只用 1/2 |
| `visual_check` 慎用 | 只写"能观察到的事实"，不写"美观/配色/设计感"（Reviewer 铁律明确不评美学） |
| `visual` **绝不写进 `required_evidence`** | 否则模型不支持视觉或学生没传图时会强制 NEED_REVIEW |
| 角色划分看证据类型 | 见 A3.7；`description` 类基本是 theory，`code/runtime/report/issue` 类基本是 acceptance |
| 同任务可混合角色 | `c3_t08` = acceptance + reflection 是合法且推荐的 |

### 6.3 数量参考（现有课程的实测分布）

| 课程 | Task 数 | Rubric 数 | 平均每 Task |
| --- | --- | --- | --- |
| course_001 / project_chatbot | 5 | 17 | 3.4 |
| course_002 / project_agent | 9 | 28 | 3.1 |
| course_003 / build | 7 | 21 | 3.0 |
| course_003 / test | 5 | 14 | 2.8 |

**建议：每个 Task 配 2–4 条 Rubric，其中 `acceptance` 占多数，`theory` 1 条，`reflection` 按需。**

### 6.4 验收链上每个字段的实际权力

| 字段 | 权力 |
| --- | --- |
| `Rubric.required_evidence` | **决定是否需要人工补证（硬门槛）** |
| `Rubric.pass_condition` | 交给 Reviewer 当判定尺子 |
| `Rubric.weight` | 决定 `score` 加权（仅 acceptance 参与） |
| `Rubric.evaluation_role` | 决定是否阻断任务完成 |
| `Rubric.visual_check` / `visual_pass_condition` | 仅在 prompt 里追加"视觉观察点"，**非硬门槛** |
| `Task.evidence_required` | **无**（不参与验收） |
| `Task.completion_required` | 决定项目能否 COMPLETED |
| `Task.depends_on` | 只生成 blocked_reason，**不阻断** |

---

## 7. AI Tutor 模板

### 7.1 你只能通过 5 个字段影响 AI 导师

```python
task.objective      # → Prompt「任务目标」
task.steps          # → Prompt「任务步骤」
rubric.criterion    # → Prompt「验收标准」（只有 criterion，不含 description/pass_condition）
task.chunk_key      # → Prompt「教学材料」（RAG 检索，可选）
task.skill          # → Prompt「关联技能」
```

**没有 course prompt / task prompt 这种东西。** 所有课程共用一个 `CORE_POLICY` + 一个 `MODE_PROMPTS["tutor"]` + 由代码路由出的行为 Prompt。课程作者**不写 prompt，只写上下文**。

### 7.2 各任务的 AI Tutor 职责设计模板

由于没有专属字段，职责是通过 `objective` / `steps` 的**写法**引导出的。推荐按任务类型设计：

| 任务类型 | 建议写法 | AI 导师实际会做什么 |
| --- | --- | --- |
| 认知/拆解型 | `objective` 写"说清 X 与 Y 的区别"，`steps` 写"读…→列出…→写一段话" | `decompose`：拆步骤 + `leading_question` 反问 |
| 实现型 | `objective` 写清"做出什么、用什么技术"，`steps` 写 4–6 步可验证动作 | `advance`：只推当前一步 |
| 排障型 | `objective` 写"报错时按 A→B→C 排查" | `debug`（学生一发报错就自动切）：`suspected_cause` + `verify_steps` + `diagnostic_question` |
| 交付型 | `objective` 写"补 README、推到 GitHub、提交验收" | `advance` + 完成后建议提交验收 |
| 反思型 | `objective` 写"复盘：具体问题→定位→修复→验证" | 引导复盘，结果进 `reflection` 桶 |

### 7.3 AI 导师的硬边界（`CORE_POLICY` 铁律，课程作者不能绕过）

```text
1. 绝不替学生完成思考            → 所以 steps 要拆细，不能只写"写一个爬虫"
2. 绝不鼓励学术造假              → 报告类任务必须要求真实输出原文
3. 只基于提供的材料与任务信息作答  → chunk_key 命不中时它会说"暂无教学材料"，不会瞎编
4. 每次给一个明确下一步          → 不要设计"开放式探索"型任务（它会强行收敛）
5. 学生代码有 bug → 引导发现，不直接改
6. 禁止要求学生提供截图/录屏作证据 → 课程里不要写"提交截图作为验收材料"
7. 系统错误隔离                  → 平台故障永不归因为学生问题
```

### 7.4 课外的陪练（不进验收）：`interview_questions`

若想让学生自检，可加：

```python
interview_questions=[
    InterviewQuestion(
        id="iq_lit01_1",
        question="如果数据文件多了一列，你的脚本需要改几处？",
        answer_anchor="只有读取与字段取值两处；统计与排序逻辑不用动。",
        hint="从「数据形状变了，哪一步依赖数据形状」这个角度想。",
        type="transfer",
    ),
]
```

**硬边界：陪练结果不进 Evidence Store、不影响 score、不写评审日志。** 它由 `GET /api/ai/interview` 单独返回。零基础课程建议每 2–3 个任务配 1 题。

---

## 8. 课程难度设计规则

系统没有难度字段，难度只能靠**任务颗粒度 + 证据严格度**体现。参考现有课程的真实梯度：

| 维度 | 简单 | 中等 | 难 |
| --- | --- | --- | --- |
| Stage 数 | 3 | 4 | 5 |
| Task 数 | 5 | 9 | 12 |
| 单 Task 的 Rubric 数 | 3 | 3–4 | 3–4 |
| 学生独立决策量 | `steps` 给出完整命令 | `steps` 给动作不给命令 | `steps` 只给目标 |
| 证据严格度 | `code` 为主 | `code` + `runtime` | `code` + `runtime` + `test`/`ci`/`report` |
| 项目间依赖 | 无 | 同项目内 `depends_on` | 跨项目 `depends_on` |
| 技能覆盖 | 2–3 个 SkillKey | 4–6 个 | 7+ 个 |

**现有课程的三级梯度实例：**

```text
course_001  套壳聊天机器人     3 Stage / 5 Task   → 入门（十几分钟级微项目）
course_002  GitHub Agent      4 Stage / 9 Task   → 进阶（含单测、trace、截断保护）
course_003  MCP Server        5 Stage / 12 Task  → 项目级（含跨项目依赖、Issue、回归）
```

**升级原则（Progression）：**

1. 同一技能在后续任务中**减少提示量**（`steps` 从"给命令"变成"给目标"）。
2. 每进入新 Stage，新增一个**证据类型**（第 1 阶段只用 code → 第 2 阶段加 runtime → 第 3 阶段加 trace/report → 第 4 阶段加 ci）。
3. 复杂度提升必须**有路由**：每个难任务前面要有一个"最小可跑通"的铺垫任务（参考 `c2t02 最小 Agent Loop` → `c2t07 多步 Agent Loop`）。

---

## 9. 零基础课程设计规则

面向文学院/非计算机专业学生，以下 10 条为硬规则：

1. **每个任务都能在本地跑出可见结果**。第一个任务不要写"理解概念"，要写"装环境 + 跑出 hello world"。
2. **`steps` 必须给到命令级**。零基础学生不会从"配置环境"推出 `python -m venv .venv`。
3. **一条命令一步**。不要把"建 venv、装依赖、跑脚本"塞进一条 step。
4. **首个 Stage 必须有"环境准备"任务**（参考 `c3_t01`）——`SkillKey.env_setup`。
5. **数据文件由课程提供**。不要让零基础学生自己去网上找《红楼梦》语料（会失败）。
6. **不假设 Git 知识**。涉及 GitHub 的任务，`steps` 里要写明"推送到 GitHub（教程见…）"，并配 `SkillKey.git`。
7. **验收证据优先用 `code` + `runtime`**，避免一上来就要求学生配 CI。
8. **theory 类 Rubric 要问"你做了什么、为什么"**，不要问"某概念是什么"（后者与被导引的项目脱节）。
9. **禁止在课程中要求截图作为验收材料**（违反铁律 6）。视觉只是可选增强。
10. **每个 Stage 结束时能向别人演示**（有可展示产物），维持零基础学生的成就感。

**零基础任务的 `steps` 标准写法（对比）：**

```text
❌ 差： "实现文本统计功能"
✅ 好：
   1. 建目录 lit_t01，进入后运行 python -m venv .venv
   2. Windows 激活：.venv\Scripts\activate；Mac：source .venv/bin/activate
   3. pip install pandas
   4. 把课程提供的人物表.csv 复制到项目目录
   5. 写 main.py：读取 csv → 统计出现次数 → 打印前 10 名
   6. 运行 python main.py，把输出留在手边（这就是运行证据）
```

---

## 10. 课程数据格式

### 10.1 真实格式：Python 函数 + Pydantic 对象

**不是 JSON / YAML / Markdown / 数据库表。** 课程就是 Python 代码。

推荐文件组织（与 course_003 一致）：

```text
ai_engine/
├── course_data.py       # 主注册表：_COURSES / _PROJECT_BUILDERS / _P4_REQUIRED / _P4_DEPENDS_ON
├── course03_data.py     # 课程 03 独立文件（一个课程一个文件，避免主文件膨胀）
└── course_lit_data.py   # ← 新课程建议新建这个文件
```

独立文件的标准骨架：

```python
# -*- coding: utf-8 -*-
"""课程 04《…》课程数据。"""
from schemas import (CodeContext, InterviewQuestion, Project, ResumePoint,
                     Rubric, SkillKey, Stage, Task)

COURSE_004 = {
    "title": "...", "description": "...", "projects": ["project_lit"],
    "img": "/courses/lit.webp", "img_pos": "center 30%",
}

def build_project_lit() -> Project:
    stage1 = Stage(...)
    task_t01 = Task(...)
    rubrics = [Rubric(...)]
    return Project(id="project_lit", title="...", description="...",
                   stages=[stage1], tasks=[task_t01], rubrics=rubrics,
                   resume_intro="...", resume_tech=["Python", "..."])
```

### 10.2 字段速查（可直接复制）

```python
Course(id, title, description="", projects=[])

Project(id, title, description="", stages=[], tasks=[], rubrics=[],
        source_url="", resume_intro="", resume_role="独立开发",
        resume_tech=[], resume_metrics=[])

Stage(id, title, order, objective="", tasks=[])

Task(id, title, stage_id, order, objective="", steps=[], hints={},
     evidence_required="none",              # 声明性，不生效
     rubric_ids=[], skill=None, source_url="", chunk_key="",
     code_context=None, interview_questions=[], resume_points=[],
     completion_required=False, depends_on=[])   # 由 _P4_* 覆盖

Rubric(id, task_id="", criterion="", description="", required_evidence=[],
       pass_condition="", weight=1, visual_check="none",
       visual_pass_condition="", evaluation_role="acceptance")

CodeContext(keywords=[], likelyFiles=[], searchPatterns=[])
ResumePoint(point, purpose="", result="", kind="delivery")
InterviewQuestion(id, question, answer_anchor, hint="", type="explain")
```

### 10.3 可选的 RAG 教学材料

若想让 AI 导师引用课程自有材料，需在 `data/chunks.jsonl` 里准备 chunk，并让 `Task.chunk_key` 匹配其 `section_path`：

```json
{"id": "lit_01", "doc": "古典文学探索器自学材料",
 "section": "T01 词频统计", "section_path": "古典文学探索器 > T01 词频统计",
 "category": "guide", "text": "…这里是与任务相关的教学正文…", "source_url": ""}
```

匹配是**子串匹配**（`keyword in c["section_path"]`），最多取 6 条。**匹配不到不报错**，Prompt 降级为"暂无检索到教学材料"。所以这是可选增强。

---

## 11. 代码接入方式

### 11.1 唯一必改文件：`ai_engine/course_data.py`

```python
# ── 第 1 处：import 课程模块并注册（文件末尾，紧随 course03 的注册之后）──
from course_lit_data import COURSE_004, build_project_lit   # noqa: E402

_PROJECT_BUILDERS["project_lit"] = build_project_lit
_COURSES["course_004"] = COURSE_004

# ── 第 2 处：把交付里程碑任务加入 _P4_REQUIRED（必须！否则项目永远不 COMPLETED）──
_P4_REQUIRED |= {"lit_t01", "lit_t02", "lit_t03"}

# ── 第 3 处（可选）：声明前置任务，仅用于前端提示 blocked_reason ──
_P4_DEPENDS_ON.update({
    "lit_t02": ["lit_t01"],
    "lit_t03": ["lit_t02"],
})
```

### 11.2 接入指南（路径 ↓ 原因 ↓ 内容 ↓ 是否必须）

| 文件路径 | 修改原因 | 修改内容 | 是否必须 |
| --- | --- | --- | --- |
| `ai_engine/course_lit_data.py` | 承载课程数据 | **新建**：`COURSE_00X` dict + `build_project_*()` 函数 | ✅ 必须 |
| `ai_engine/course_data.py` | 注册课程与项目 | ① import 并写入 `_PROJECT_BUILDERS` / `_COURSES`；② 扩充 `_P4_REQUIRED`；③ 可选扩充 `_P4_DEPENDS_ON` | ✅ 必须（三条都要） |
| `data/chunks.jsonl` | 提供 RAG 教学材料 | 追加 chunk，`section_path` 与 `Task.chunk_key` 一致 | ⭕ 可选 |
| `frontend/public/courses/lit.webp` | 选课卡配图 | 放入图片文件 | ⭕ 可选（缺失走占位图） |
| `data/docs_manifest.csv` | 仅当有飞书/外部文档要进 RAG 导航 | 追加一行 | ⭕ 可选 |
| `ai_engine/store.py` | **仅当修改【已有】课程的 Rubric 语义或分类时** | bump `REVIEW_RUBRIC_VERSION` | ❌ **新增课程不需要** |
| `frontend/src/views/TeachView.vue` | 仅当要加成就解锁映射 | 在 `doEnterCourse()` 增加分支 | ❌ 不需要 |
| `ai_engine/schemas.py` | 仅当要加新字段/新 SkillKey | 改 Pydantic 模型（属引擎改造） | ❌ 不需要 |

### 11.3 已支持动态化的地方 vs 存在硬编码的地方

**已经完全动态化（新增课程零改动）：**

```text
✅ 课程列表/选课转盘        ← GET /api/ai/config → list_courses()
✅ 项目下拉                 ← /api/ai/config → projects
✅ 阶段与任务清单渲染        ← loadProject() 遍历 stages[].tasks[]
✅ 任务完成状态             ← student.completed_tasks（前端 localStorage）
✅ 项目完成判定             ← project_state.compute_project_state()（只认 _P4_REQUIRED）
✅ 技能状态 / 学习缺口       ← learner_state.compute_learner_state()
✅ 简历素材                 ← career.build_career_text()
✅ 项目复盘                 ← student_record.build_project_retro()
✅ AI 导师上下文             ← context_builder.build_context()
✅ 验收链                   ← review.py（按 rubric_ids 取 Rubric，无课程白名单）
```

**仍存在硬编码的地方（新增课程不会崩，但要注意）：**

```text
⚠️ TeachView.vue doEnterCourse()  成就解锁映射，仅 course_001 / course_002 有分支 → 新课程无成就，不影响功能
⚠️ TeachRequest.course_id 默认值     "course_001"（请求未带时兜底）
⚠️ TeachRequest.project_id 默认值    "project_chatbot"
⚠️ Course 无 difficulty/prerequisite 字段 → 难度信息只能写 description
⚠️ SkillKey 枚举无文学类技能 → 只能复用现有 13 键
```

### 11.4 新增课程会不会影响已有课程？

**结论：只要遵守以下 4 条，就不会影响任何已有课程。**

1. **`task_id` / `rubric_id` 全局唯一**。`get_task()` 是"遍历所有项目、返回第一个命中"；id 冲突会导致新课程的 Rubric 被误判给旧任务。
2. **`stage_id` 带项目前缀**（`lit_stage1` 而不是 `stage1`）。虽无全局查找函数会因此出错，但可读性与未来扩展更安全。
3. **不要改 `_P4_REQUIRED` 的已有元素**，只用 `|=` 追加。
4. **不要 bump `REVIEW_RUBRIC_VERSION`**（除非你改了旧课程的 Rubric）。bump 会让**所有学生**已有的幂等缓存全部失效，重新烧 BYOK。

---

## 12. 一个完整示例：最小可运行课程

> 说明：以下代码是**可直接运行的完整文件**。它能被引擎正确加载、在前端自动出现、能被验收。
> 内容用「古典文学探索器 · 最小示例」填充，仅为证明链路可跑通；**它不是最终课程内容**。
> 交付物刻意选择"用 Python 统计文本 + 输出报告"这一形态，因为它能映射到现有 `code` / `runtime` / `report` 证据（见 A6）。

### 12.1 新建文件 `ai_engine/course_lit_data.py`

```python
# -*- coding: utf-8 -*-
"""最小可运行课程示例：古典文学探索器（课程 04）。

结构：1 课程 → 1 项目 → 1 阶段 → 3 任务
验收：acceptance（code + runtime + report）+ theory（description）
"""
from schemas import (
    CodeContext,
    Project,
    ResumePoint,
    Rubric,
    SkillKey,
    Stage,
    Task,
)

# 课程元信息（由 course_data 注册进 _COURSES）
COURSE_004 = {
    "title": "古典文学探索器（最小示例）",
    "description": "面向零基础同学的数字人文入门：用 Python 统计古典小说的人物出场情况，"
                   "做出一个可重复运行的分析脚本和一份分析报告。"
                   "前置：无需编程基础，会打字、会用浏览器即可。预计投入：约 3 小时。",
    "projects": ["project_lit"],
    "img": "/courses/more.webp",       # 临时占位，正式课程请替换为专用配图
    "img_pos": "center 30%",
}


def build_project_lit() -> Project:
    # ---------------- Stage 1 ----------------
    stage1 = Stage(
        id="lit_stage1", title="① 把小说变成数据", order=1,
        objective="装好环境，把《红楼梦》人物出场表当成数据读进来并数出结果。",
        tasks=["lit_t01", "lit_t02", "lit_t03"],
    )

    # ---------------- T01 环境准备 + 第一个脚本 ----------------
    task_t01 = Task(
        id="lit_t01", title="装好环境，跑出第一份统计", stage_id="lit_stage1", order=1,
        objective="建好 Python 项目环境，写一个脚本读取课程提供的人物出场表（CSV），"
                  "统计每个人物出现的章节数，并按次数从多到少打印出前 10 名。",
        steps=[
            "建项目目录 lit_project，进入后运行 python -m venv .venv",
            "激活虚拟环境：Windows 用 .venv\\Scripts\\activate；Mac/Linux 用 source .venv/bin/activate",
            "把课程提供的 characters.csv（两列：chapter,character）复制到项目目录",
            "写 main.py：读取 csv → 用字典累加每个人的出现次数 → 排序后打印前 10 名",
            "运行 python main.py，把终端输出留在手边（这就是运行证据）",
        ],
        evidence_required="code",          # 声明性字段，不生效；验收看 Rubric
        rubric_ids=["rb_lit01_1", "rb_lit01_2"],
        skill=SkillKey.env_setup,
        chunk_key="古典文学探索器 > T01 环境与统计",   # 无对应 chunk 时自动降级，不报错
        code_context=CodeContext(
            keywords=["csv", "dict", "count", "sorted", "print", "read"],
            likelyFiles=["main", "analyze"],
            searchPatterns=["open\\(", "Counter", "sorted\\(", "for "],
        ),
        resume_points=[
            ResumePoint(point="搭建 Python 项目环境并实现文本统计脚本（读取 → 计数 → 排序输出）",
                        purpose="让统计结果可被第三方复现",
                        result="形成了可复用的文本分析基础脚本", kind="delivery"),
        ],
    )

    # ---------------- T02 让结果可核对：报告 ----------------
    task_t02 = Task(
        id="lit_t02", title="写一份能核对的统计报告", stage_id="lit_stage1", order=2,
        objective="把统计结果整理成仓库根目录的 REPORT.md：写明数据来源、统计口径、前 10 名结果，"
                  "并如实说明本次没有统计到什么（如未区分同名人物）。",
        steps=[
            "在项目根目录新建 REPORT.md",
            "写清三件事：数据文件是什么、统计口径是什么（按章节记一次）、前 10 名结果（用真实输出）",
            "补一节「本次没覆盖到什么」——如实写比假装完整更专业",
            "把项目推到 GitHub（含 main.py、characters.csv、REPORT.md）",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit02_1", "rb_lit02_2"],
        skill=SkillKey.paper_writing,
        chunk_key="古典文学探索器 > T02 统计报告",
        code_context=CodeContext(
            keywords=["report", "readme", "结论", "口径"],
            likelyFiles=["report", "readme"],
            searchPatterns=["REPORT", "数据来源", "未覆盖"],
        ),
        resume_points=[
            ResumePoint(point="产出含统计口径与结果明细的分析报告，并如实交代未覆盖范围",
                        purpose="让结论可核对而非笼统断言",
                        result="提升了分析结果的可验证性", kind="engineering"),
        ],
    )

    # ---------------- T03 解释与复盘 ----------------
    task_t03 = Task(
        id="lit_t03", title="说清你的统计口径", stage_id="lit_stage1", order=3,
        objective="用自己的话讲清两件事：为什么用字典按人物累加计数；"
                  "如果人物有多个别名（如「贾宝玉」与「宝玉」），你会怎么处理。"
                  "把这两段话写成一段自述并随提交附上。",
        steps=[
            "回顾 main.py 的计数逻辑，用一两句话说明「键是什么、值是什么」",
            "想一想别名问题：是合并统计，还是分开统计？各自会带来什么偏差",
            "把这两段话写成不超过 200 字的自述（在提交验收时填入「自述说明」）",
        ],
        evidence_required="none",
        rubric_ids=["rb_lit03_1"],
        skill=SkillKey.ai_assisted,
        chunk_key="古典文学探索器 > T03 统计口径",
    )

    # ---------------- Rubrics ----------------
    rubrics = [
        # T01：acceptance（code + runtime 硬门槛）
        Rubric(
            id="rb_lit01_1", task_id="lit_t01",
            criterion="脚本能正确统计并输出前 10 名",
            description="读取 CSV，按人物累加出现次数，排序后输出前 10 名",
            required_evidence=["code", "runtime"],
            pass_condition="代码中存在读取-计数-排序逻辑；运行输出含至少 10 条「人物 次数」",
            weight=2, evaluation_role="acceptance",
        ),
        Rubric(
            id="rb_lit01_2", task_id="lit_t01",
            criterion="脚本可重复运行且结果一致",
            description="不依赖手工改动，连续运行两次输出相同",
            required_evidence=["code"],
            pass_condition="代码里没有硬编码的结果列表；数据来自文件读取",
            weight=1, evaluation_role="acceptance",
        ),
        # T02：acceptance（report 为可选加分，code 为硬门槛）
        Rubric(
            id="rb_lit02_1", task_id="lit_t02",
            criterion="仓库根目录存在结构化统计报告",
            description="REPORT.md 含数据来源、统计口径、结果三部分",
            required_evidence=["code"],
            pass_condition="仓库根目录可见 REPORT.md，且三部分齐全",
            weight=2, evaluation_role="acceptance",
        ),
        Rubric(
            id="rb_lit02_2", task_id="lit_t02",
            criterion="报告结论与真实输出一致且交代了未覆盖范围",
            description="结果来自脚本真实输出，并有一节说明本次没有统计到什么",
            required_evidence=["report"],
            pass_condition="报告中的结果与运行输出一致；有如实说明未覆盖范围的一节",
            weight=1, evaluation_role="acceptance",
        ),
        # T03：theory（无阻断权，未达标只产 Learning Gap）
        Rubric(
            id="rb_lit03_1", task_id="lit_t03",
            criterion="能说清统计口径与别名的处理取舍",
            description="讲清字典计数的键值含义，并对别名问题给出方案与偏差分析",
            required_evidence=["description"],
            pass_condition="自述能准确说明键值含义，且对别名问题给出明确取舍与理由",
            weight=1, evaluation_role="theory",
        ),
    ]

    return Project(
        id="project_lit",
        title="古典文学探索器（最小示例）",
        description="用 Python 把古典小说的人物出场表变成可统计的数据，输出一份可核对的统计分析报告。",
        stages=[stage1],
        tasks=[task_t01, task_t02, task_t03],
        rubrics=rubrics,
        resume_intro="用 Python 读取古典小说人物出场数据，实现可重复运行的统计脚本，"
                     "并产出含统计口径与结果明细的分析报告。",
        resume_role="独立开发",
        resume_tech=["Python", "CSV 数据处理", "字典计数与排序", "Markdown 报告"],
        resume_metrics=["统计结果可重复复现；报告交代了未覆盖范围"],
    )
```

### 12.2 修改 `ai_engine/course_data.py`（3 处）

在文件末尾（`_COURSES["course_003"] = COURSE_003` 之后、`_project_cache` 之前）插入：

```python
# ---- 课程 04：古典文学探索器（最小示例）----
from course_lit_data import COURSE_004, build_project_lit  # noqa: E402

_PROJECT_BUILDERS["project_lit"] = build_project_lit
_COURSES["course_004"] = COURSE_004
```

在 `_P4_REQUIRED` 集合内追加（**必须**，否则项目永远不 COMPLETED）：

```python
    # 古典文学探索器：核心交付（统计脚本 / 统计报告）
    "lit_t01", "lit_t02",
```

（可选）在 `_P4_DEPENDS_ON` 内追加：

```python
    # 古典文学探索器
    "lit_t02": ["lit_t01"],
    "lit_t03": ["lit_t01"],
```

> 注意：`lit_t03` 刻意**不**设为 `completion_required`——它是 theory-only 的理解任务，不应阻断项目完成。

### 12.3 验证清单（接完就跑）

```text
1. 后端重启后访问 GET /api/ai/config
   → data.courses 里出现 {"course_id": "course_004", ...}
   → data.courses[3].projects[0].stages[0].tasks 有 3 个任务
2. GET /api/ai/project_state?student_id=demo&project_id=project_lit
   → completion_defined == true，required_total == 2
3. 前端进入课程，任务清单出现「装好环境，跑出第一份统计」等 3 个任务
4. POST /api/ai/teach（course_id=course_004, project_id=project_lit, task_id=lit_t01）
   → 返回 JSON 含 message / next_action（behavior=decompose）
5. POST /api/ai/review（task_id=lit_t01，repo_url=某公开仓库，submission.description 含启动命令）
   → 不传代码证据时应返回 NEED_REVIEW 且 next_step 提示补充 code/runtime
   → 传了含 main.py 的公开仓库时应能给出逐条 criteria
```

### 12.4 交付物三要素对照（这个示例为什么能跑通）

| 学生动作 | 产生的证据 | 哪条 Rubric 吃它 |
| --- | --- | --- |
| 写 `main.py` 并推到 GitHub | `code`（`build_code_evidence` 按 `code_context.likelyFiles` 命中 `main`） | `rb_lit01_1`、`rb_lit01_2`、`rb_lit02_1` |
| 运行 `python main.py` 并写进提交自述 | `runtime`（`detect_run_cmd` 命中 `python xxx.py`） | `rb_lit01_1` |
| 仓库根目录写 `REPORT.md` | `report`（`_KEY_REPORT` 命中并打标） | `rb_lit02_2` |
| 提交时填「自述说明」 | `description` | `rb_lit03_1`（theory） |

---

## 附录：课程作者自查表（交付前逐项打勾）

**数据层**

- [ ] `task_id` / `rubric_id` / `stage_id` 全局唯一
- [ ] `Task.stage_id` 与 `Stage.id` 一致；`Rubric.task_id` 与 `Task.id` 一致
- [ ] `Stage.tasks` 列表与 `Task.stage_id` 归属一致
- [ ] `Task.rubric_ids` 里每个 id 都存在于 `Project.rubrics`
- [ ] `Task.order` 在同一 Stage 内连续且不重复

**验收层**

- [ ] 每条 `acceptance` Rubric 的 `required_evidence` 里**至少有一个可自动获取的类型**（code/runtime/test/ci/trace/url）
- [ ] `description` **没有**被当作 acceptance 的唯一硬证据
- [ ] `visual` **没有**出现在任何 `required_evidence` 里
- [ ] `pass_condition` 是可核对的（含具体数字/字段/文本形态），不是"功能正常"
- [ ] 只能靠自述判定的标准，角色设为 `theory` 或 `reflection`

**完成判定层**

- [ ] 所有"交付里程碑"任务的 id 已加入 `_P4_REQUIRED`
- [ ] 认知/复盘类任务**没有**被加入 `_P4_REQUIRED`
- [ ] `_P4_DEPENDS_ON` 只用于"自然进入下一阶段"的提示，没有做成硬门禁

**导师层**

- [ ] `objective` 描述的是"做出什么"而非"学到什么"
- [ ] `steps` 给到零基础学生可直接执行的程度
- [ ] `chunk_key` 若填了，`data/chunks.jsonl` 里确有对应 `section_path`
- [ ] 课程中没有要求学生提交截图作为验收材料

**接入层**

- [ ] `schemas.py` 未被修改
- [ ] `_P4_REQUIRED` 用 `|=` 追加，未改动旧元素
- [ ] **未** bump `REVIEW_RUBRIC_VERSION`（除非确实改了旧课程 Rubric）
- [ ] 配图已放 `frontend/public/courses/`，或接受默认占位图

---

**文档结束。** 版本 v1.0，基于仓库当前实现。若后续 `schemas.py` / `review.py` / `store.py` 发生变更，请同步更新本文档的 Part A。