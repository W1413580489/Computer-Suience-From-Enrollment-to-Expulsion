# Ai导师 V2 · 修改版方案

> 基于飞书《Ai导师v2》重构方案 + 现有项目代码（ai_engine/）逐条核实的修订版。
> 核心变化：定位不变（项目交付 + 求职成果），但**收敛范围、降低门槛、消除矛盾**。
> 所有"已有能力"均标注了真实代码位置，可作为验收依据。

---

## 一、产品定位（保留 V2 核心）

**一句话定位：**

> 让一个基础一般、缺乏项目经历的大学生，在 AI 协作下完成真实项目，产出一段可写进简历的项目描述，并通过"质检陪练"确认自己能讲清、能改。

**成功链条（保留 V2）：**

```
需求 → 项目 → AI 辅助开发 → 项目交付 → 自动验收 → 质检陪练 → 简历描述 → 求职
```

**与 V1（教学平台）的本质区别：**

| | V1 教学平台 | V2 项目交付系统 |
|---|---|---|
| 用户成功定义 | 学会了、完成了任务 | 做出了项目、能写进简历 |
| 验收终点 | Task 通过 | 项目可验证 + 能讲清 + 一段简历文字 |
| 过程证据 | 尽量采集 | 不采集（证据 = 工作副产物） |
| AI 角色 | 四模式 | **双模式**（指导 + 验收） |

---

## 二、现状盘点（基于真实代码，不是纸上谈兵）

### 2.1 已有能力（V2 的增量需求中，这些已存在，保留）

| V2 需求 | 现有实现 | 位置 |
|---|---|---|
| 双模式内部集成（指导/验收） | `Mode` 枚举 4 值，但 Prompt 只实现 tutor + reviewer；debugger 已是 tutor 内部 `behavior=debug`；coach 无独立 Prompt | [prompts.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/prompts.py#L43-L70)、[schemas.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/schemas.py#L28-L32) |
| Evaluation Firewall（Reviewer 不读指导对话） | `/api/ai/review` 独立接口，`collect_evidence` 只读 submission + 仓库证据，不接触会话历史 | [app.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py#L414-L456) |
| Reviewer 证据硬约束 | `evidence_precheck`：缺证据直接 NEED_REVIEW，不走 LLM | [review.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/review.py#L72-L110) |
| CI 自动验收 | `fetch_ci_evidence`：build/test workflow 结论映射为权威证据 | [code_evidence.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/code_evidence.py#L183-L245) |
| Task-aware Code Retrieval | `rank_candidate_files` 评分 + `ai_relevance_filter` AI 二次筛选 | [code_evidence.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/code_evidence.py#L252-L328) |
| RAG 知识库 | chunks.jsonl + bge-small-zh-v1.5 本地向量化 + 上下文注入 | [context_builder.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/context_builder.py)、[backend/embedding.py](file:///d:/Assistant/tralis/xkz-agent/backend/embedding.py) |
| 输出质量控制 | 5 项校验 + 重试 2 次 + JSON 模式 + Pydantic 校验 | [response_validator.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/response_validator.py)、[llm_client.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/llm_client.py) |
| 项目结构（Course/Stage/Task/Rubric） | 硬编码于 course_data.py，两门课已落地 | [course_data.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/course_data.py) |

### 2.2 与 V2 的差距（真正的新增量）

| 增量 | 现状 | 本方案处理 |
|---|---|---|
| Career Converter（简历描述） | 无 | 简化版：只生成一段文字（见 5.1） |
| 质检陪练（Transfer Task） | 无 | 全新设计，定位陪练非裁决（见 5.2） |
| Artifact Evidence 扩展 | 拉 README/依赖/CI，但不验证部署可访问、不检查架构图 | 轻量扩展（见 5.3） |
| 课程工程化（项目生产工厂） | course_data 硬编码 | 暂缓（见 4.4） |
| 能力图谱 / Competency Level | 无 | **明确砍掉**（见 4.2） |

---

## 三、六点修改要求 → 落地设计

### 3.1 修改 1：不再要求部署（消除"部署门槛 vs 完课率"矛盾）

**原 V2 问题：** 交付物清单强制"在线 Demo / Deployment"，但部署（服务器/域名/HTTPS/进程守护）对零基础学生是比写代码更高的门槛，会重创完课率。

**修改后交付标准：**

```
必交付（三选一即可，覆盖"项目能跑"）：
  ① 本地可复现运行（README 写明启动命令 + 学生文字说明访问效果）
  ② CI 通过（test/build workflow 结论 success → 视为可构建/能启动的权威证据）
  ③ 在线部署地址（自愿，作为加分证据，不强制）

不再要求：域名、HTTPS、进程守护、架构图、API 文档（降为"可选加分项"）。
```

**代码影响：**
- `Rubric.required_evidence` 中的 `deployment` 不再作为硬性必交项（仅当学生自愿提供时作为加分证据）。
- `evidence_precheck` 的缺失证据判定中，`deployment` 从强制列表移除；`runtime` 证据由"本地可运行说明 / CI 结论"满足。
- `review.py` 评审 Prompt 中关于"运行证据"的说明同步改为上述三选一标准。

### 3.2 修改 2：质检陪练，而非能力证明/防作弊

**原 V2 问题：** Transfer Task 被描述为"验证理解""让 AI 代写暴露"。但学生同样可以把变式题丢给 AI 拿答案，防不住，也不该由系统裁决。

**修改后定位：**

> 质检陪练 = 项目做完后，系统基于这份代码生成"面试官大概率会问的问题"，让学生自答自评。系统给提示、给参考答案锚点，**不做判定、不进评审结果、不算分**。

**产品原则（写入文案）：**
- 不叫"能力验证"，叫"**面试自检**"
- 学生答不上来 → 提示"这里讲不清，面试时会是短板"，并引导回看对应代码/资料
- 讲得清 → "这段可以放心写进简历"

**代码影响：** 全新能力，见 5.2。

### 3.3 修改 3：只生成一段简历文字，不做简历导出

**修改后范围：**

```
输出：一段 100~200 字的"项目经历描述"（可整段粘贴进简历）
输入：项目元数据 + 验收结果（证据数、CI 结论、测试通过数）
不做：完整简历导出、作品集页面、PDF/Word 生成
```

示例输出：

> 独立完成"套壳聊天机器人"：基于 FastAPI 实现 POST /chat 接口，接入 DeepSeek API 完成消息转发与回复解析；前端用原生 HTML/JS 实现聊天界面与滚动加载。已通过 12 项自动验收，GitHub Actions 测试通过，代码仓库与运行说明可公开验证。

**代码影响：** 全新接口 `POST /api/career/text`，见 5.1。

### 3.4 修改 4：MVP 课程计划存档，短期不执行

《企业 AI 知识库助手》的完整课程设计**写入本文档第七章**，作为未来课程计划存档。明确标记：**待 V2 主链路（双模式 + 质检陪练 + 简历文字）验证通过后再执行**，不纳入当前 Sprint。

### 3.5 修改 5：双模式架构保留（指导 + 验收）

**V2 原文主张"四个角色收敛为一个 AI"，但现有代码已经是更彻底的做法——后端早就收敛为两种模式，前端还残留四模式 UI。** 本方案确认保留现有双模式设计，并统一文档表述：

```
                Project AI（统一入口，学生只看到"AI 项目导师"）
                              │
              ┌───────────────┴───────────────┐
              ↓                               ↓
       【指导模式】Guide                  【验收模式】Reviewer
        教学权限                            评价权限（独立，Firewall）
              │                               │
   ┌────┬─────┴─────┬────┐                   │
   ↓    ↓           ↓    ↓                   ↓
拆解  推进  调试(状态机) 建议转验收    Evidence Collector → Snapshot → 评审
```

- **指导模式** = 现有 `tutor` + 内部行为路由 `decompose / advance / debug`（[route_behavior](file:///d:/Assistant/tralis/xkz-agent/ai_engine/prompts.py#L113-L131)），保留不变。
- **验收模式** = 现有 `/api/ai/review` 评审链，保留不变。
- **Evaluation Firewall 保留**：Reviewer 只读证据快照，不读指导对话历史。
- **前端收敛**：把四模式切换按钮改为单一"AI 项目导师"入口，内部行为标签（拆解中/推进中/调试中）轻量展示，验收入口单独放在"提交验收"处。

### 3.6 修改 6：模型输出漂移解决方案

**问题定义：** 评审 `score` 目前由 LLM 直接输出（[llm_client.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/llm_client.py#L139-L157) `ReviewEvaluation.score`），同一份证据换 key / 换重试可能得出不同分数和不同总体结论。这就是输出漂移。

**解决方案（六层，从根治到兜底）：**

| 层 | 方案 | 说明 | 现状 |
|---|---|---|---|
| L1 | **score 规则化** | LLM 只输出逐条 `PASS/FAIL/NEED_REVIEW`，**score 由后端按 weight 加权计算**：`sum(通过条目weight) / sum(全部weight) × 100`。同证据 → 同分，彻底消除分数漂移 | **要改**（核心） |
| L2 | **status 规则化** | 总状态由代码判定：有 FAIL → FAIL；有 NEED_REVIEW → NEED_REVIEW；全 PASS → PASS。LLM 不输出总状态 | **要改** |
| L3 | **确定性证据直判** | CI 结论（build/test success/fail）与证据缺失（precheck）在代码层直接映射 PASS/FAIL/NEED_REVIEW，**不经 LLM** | 已有 precheck，CI 直判待加强 |
| L4 | **证据快照冻结** | 评审输入在进入 LLM 前冻结为不可变快照（含 hash），Reviewer 只看快照 → 保证"同输入同输出"的前提成立 | 部分已有（collect_evidence），快照 hash 待加 |
| L5 | **评审幂等缓存** | 同 `task_id + 快照hash` 的评审请求返回缓存结果（TTL 内），重复评审不重新调用 LLM | **要加** |
| L6 | **输出校验兜底** | JSON 模式 + Pydantic 校验 + 失败重试 2 次（已有）；校验失败时**丢弃 LLM 自由文本，绝不展示** | 已有，保留 |

**核心改动只有一个：`ReviewEvaluation` 的 `score` 与 `status` 从"LLM 输出字段"改为"后端计算字段"。** LLM 只负责逐条 `criteria` 的二元判定与理由，所有聚合逻辑进代码。这样输出漂移从"不可避免"变成"只剩单条判定级别的轻微波动"。

---

## 四、系统架构（V2 修改版）

```
                ┌─────────────────────────┐
                │    Project Catalog      │  课程数据（course_data.py，硬编码保留）
                │  Course/Stage/Task/…    │
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │    Project Planner      │  任务编排（保留，含阶段进度/下一任务）
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │      Project AI         │  统一入口（前端收敛为"AI 项目导师"）
                │   ┌───────┴────────┐    │
                │   ↓                ↓    │
                │  指导模式          验收模式 │  ← 双模式保留，Firewall 隔离
                │ (tutor+行为路由)  (review)│
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │   Student Development   │
                │  GitHub / CI / 本地运行  │
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │   Evidence Collector    │  code + CI + 运行说明 + 自述
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │  Evidence Snapshot(冻结) │  快照 + hash（L4/L5）
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │   Verification Engine   │  precheck 硬约束 + CI 直判 + score/status 规则化
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │   质检陪练 Transfer      │  面试自检（不判分）
                └───────────┬─────────────┘
                            ↓
                ┌─────────────────────────┐
                │   Career Text（一段）     │  → 学生粘贴进简历
                └─────────────────────────┘
```

**与现有架构的映射：** 上图所有模块（除"质检陪练"与"Career Text"）在现有代码中已有对应实现，本方案是收敛 UI + 规则化评分 + 补两个新模块，**不是重构**。

---

## 五、新增能力设计

### 5.1 Career Text 生成器（`POST /api/career/text`）

```
输入：project_id + 验收结果（score、通过证据数、CI 结论、任务完成清单）
输出：{ "text": "一段 100~200 字项目经历描述", "bullets": ["技术栈", "核心功能", "量化结果"] }
```

- 生成方式：模板 + 数据填充（**不用 LLM 自由生成**，避免文案漂移；用 LLM 也只是润色，输入固定）。
- 模板字段：项目名 / 技术栈（来自任务 skill + code_context）/ 核心功能（来自通过的 rubric 标题）/ 量化结果（CI 测试数 + 验收通过数）/ 可验证证据（GitHub 链接）。
- 前端位置：项目完成页（验收 PASS 后）展示一段文字 + "复制"按钮。

### 5.2 质检陪练（Transfer Task，定位面试自检）

**数据模型（Task 扩展，可选字段）：**

```python
class InterviewQuestion(BaseModel):
    id: str
    question: str                    # 面试官风格问题（如"把 Top-K 从 3 改成 5，解释结果为何变化"）
    answer_anchor: str               # 参考答案锚点（1-2 句，供学生自比）
    hint: str = ""                   # 答不上时的提示
    type: Literal["explain", "debug", "transfer"]  # 解释/调试/变式
```

`Task.interview_questions: list[InterviewQuestion] = []`（课程作者标注；无标注时由 AI 基于代码生成，标记"AI 生成"）。

**交互流程：**
```
项目验收 PASS → 进入质检陪练
  → 展示 2~3 个问题（每题一张卡）
  → 学生作答 → 展开参考答案锚点自比
  → 系统给提示（不判对错，不给分）
  → 全部浏览完 → "这段项目经历可以写进简历了"
```

**硬边界（写入 Prompt/代码注释）：** 陪练结果**不进入** Evidence Store、不影响 score、不写入日志的评审字段。

### 5.3 Artifact Evidence 轻量扩展

- 已有：README / 依赖清单 / 主入口 / CI 已拉取（`code_evidence.py`）。
- 新增（轻量）：README 存在性检测（已有）+ 启动命令提取（README 中匹配 `uvicorn|npm run|docker compose` 出现与否，作为"本地可运行说明"的证据加分项）。
- 不做：部署地址可访问性爬虫验证、架构图检测（超出当前范围）。

---

## 六、模型输出漂移：落地清单

| # | 改动 | 文件 | 说明 |
|---|---|---|---|
| 1 | `ReviewEvaluation` 移除 `score`/`status` 的 LLM 输入，改为后端计算 | [schemas.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/schemas.py)、[app.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py#L503-L527) | LLM 只输出 criteria；score/status 由代码按 weight 计算 |
| 2 | CI 结论直判加强 | [review.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/review.py#L176-L179) | build/test workflow 的 success/fail 在代码层直接映射对应项 PASS/FAIL |
| 3 | 证据快照 + hash | [review.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/review.py#L18-L45) | `collect_evidence` 输出加 hash，作为评审缓存 key |
| 4 | 评审幂等缓存 | [app.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/app.py) | `task_id + snapshot_hash` 的评审在 TTL 内返回缓存 |
| 5 | 前端收敛为双模式 | [TeachView.vue](file:///d:/Assistant/tralis/xkz-agent/frontend/src/views/TeachView.vue) | 四模式按钮 → 单一"AI 项目导师"；行为标签轻量展示 |
| 6 | 部署要求降级 | [course_data.py](file:///d:/Assistant/tralis/xkz-agent/ai_engine/course_data.py) | rubric 的 deployment 证据不再强制 |

---

## 七、未来课程计划：《企业 AI 知识库助手》（存档，暂不执行）

> **状态标记：DRAFT · 待 V2 主链路验证通过后执行。** 本文档只做设计存档，不纳入当前 Sprint。

**业务目标：** 为一家虚拟企业内部知识库做客服问答系统。

**交付物（V2 降级标准后）：** 前端页面 / FastAPI 后端 / DeepSeek API / RAG / 用户会话 / GitHub 仓库 / README（含运行说明）/ API 文档（可选加分）/ 测试结果 / 简历描述文字。

**任务编排（8 Task）：**
```
T01 搭建 API 服务        T05 处理异常
T02 完成模型调用          T06 加入测试
T03 增加上下文记忆        T07 整理项目（README/启动说明/简历文字）
T04 接入知识库(RAG)       T08 质检陪练（面试自检）
```

**每 Task 的 Rubric 要点：** 沿用现有双模式结构（指导拆解 + 验收逐条判定），运行证据按"本地可运行说明 / CI / 自愿部署"三选一。

**已识别的技术难点（必须先解决再开课）：**
1. **BYOK embedding 成本**：学生自做 RAG 项目时，embedding 用自己的 API key 花钱、或本地起模型门槛高。方案待定（备选：服务端免费提供 embedding 额度 / 课程内置已向量化语料）。
2. **知识库语料**：需要一份可公开的、有版权允许的语料，作为课程内建知识库。

---

## 八、落地顺序（分阶段，独立验证）

### 阶段 1：收敛与规则化（低成本，先做）
- [ ] 前端四模式 → 双模式收敛（6-5）
- [ ] score/status 规则化（6-1、6-2）
- [ ] 部署要求降级（6-6、3.1）

### 阶段 2：新增能力（中成本）
- [ ] Career Text 接口 + 前端展示（5.1）
- [ ] 评审幂等缓存 + 证据快照 hash（6-3、6-4）
- [ ] 质检陪练试点：给"套壳聊天机器人"配 2 个面试问题跑通流程（5.2）

### 阶段 3：存档不执行
- [ ] 第七章《企业 AI 知识库助手》完整课程设计（写文档，不做）
- [ ] 课程工程化（course_data 模板化，评估后再定）

---

## 九、明确不做（防止范围回弹）

- ❌ 不要求部署上线（修改 1）
- ❌ 不做能力 Level 判定 / 能力图谱 / Competency Profile（砍掉）
- ❌ 不做防作弊检测（转移任务定位为陪练，不裁决）
- ❌ 不做完整简历导出 / 作品集页（只生成一段文字）
- ❌ 不采集过程证据（录屏 / 键盘 / 终端埋点 / 代码相似度检测）
- ❌ 不建数据库（维持进程内存 + localStorage，规模扩大后再定）
- ❌ 不执行《企业 AI 知识库助手》课程（存档）
