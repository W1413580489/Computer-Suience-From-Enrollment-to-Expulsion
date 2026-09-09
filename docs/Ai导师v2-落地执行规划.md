# Ai导师v2 修改版方案 — 研究结论与落地执行规划

> 研究对象：飞书《Ai导师v2》修改版方案（revision 126，2026-09-09 读取）
> 代码基线：`D:\Assistant\tralis\xkz-agent\ai_engine\` + `frontend/src/views/TeachView.vue`
> 本文档结论已逐条对照真实代码核实，非纸上推演。

---

## 一、方案研究摘要

### 1.1 产品定位（不变）

> 让基础一般、缺项目经历的大学生，在 AI 协作下完成真实项目，产出可写进简历的项目描述，并通过"质检陪练"确认自己能讲清、能改。

成功链条：需求 → 项目 → AI 辅助开发 → 项目交付 → 自动验收 → 质检陪练 → 简历描述 → 求职

### 1.2 六点修改要求（方案核心）

| # | 修改 | 本质 | 代码影响量级 |
|---|------|------|------------|
| 1 | 不再强制部署 | 消除"部署门槛 vs 完课率"矛盾；交付三选一（本地可复现 / CI 通过 / 自愿部署） | 小：改 rubric 数据 + precheck 判定 + 评审 Prompt |
| 2 | 质检陪练 ≠ 能力证明 | 面试自检，不判定、不进评审、不算分 | 中：全新模块（数据模型 + 接口 + 前端卡片） |
| 3 | 只生成一段简历文字 | 不做简历导出/作品集；模板填充而非 LLM 自由生成 | 中：新接口 `POST /api/career/text` + 完成页展示 |
| 4 | 课程计划存档不执行 | 《企业 AI 知识库助手》写入文档第七章，待主链路验证后再做 | 零代码 |
| 5 | 双模式架构保留 | 后端早已收敛（tutor+route_behavior / review），前端残留四模式 UI 需收敛 | 小：仅前端 TeachView.vue 改造 |
| 6 | 模型输出漂移治理 | score/status 从 LLM 输出改为后端计算（六层方案，核心是 L1/L2） | 中：schemas + review + app 三处联动 |

### 1.3 与现有代码的核实结果（2026-09-09 实查）

方案"现状盘点"表中的每一条都与代码对得上，可直接作为验收依据：

| 方案断言 | 代码实查 | 结论 |
|---------|---------|------|
| ReviewEvaluation 的 score/status 是 LLM 输出字段 | `schemas.py`：`ReviewEvaluation.status` / `.score` 确为模型字段，随 LLM 输出填充 | ✅ 漂移风险属实，需改 |
| 后端已收敛为双模式（tutor + reviewer） | `prompts.py:113 route_behavior()` 存在；`app.py:247` 调用；reviewer 走独立 `/api/ai/review`（app.py:414） | ✅ 后端无需动，只改前端 |
| Evaluation Firewall 已存在 | `app.py` review 链只调 `collect_evidence` + `evidence_precheck`，不读会话历史 | ✅ 保留即可 |
| deployment 仍被强制 | `course_data.py` 中 task_review 环节存在 `required_evidence=["runtime","deployment"]` | ✅ 需降级 |
| 质检陪练 / Career Text 不存在 | 全局无 `/api/career`、无 InterviewQuestion 模型 | ✅ 全新增量 |
| 前端四模式 UI 残留 | `TeachView.vue` 存在 `teach__modes` 按钮组 + `MODES` 数组 + mode_advice 切换逻辑 | ✅ 需收敛为单一"AI 项目导师"入口 |

**总体判断：这份方案不是重构，是"收敛 UI + 规则化评分 + 补两个新模块"。方案与代码高度互恰，可以直接进入执行。**

---

## 二、执行规划（三阶段，每阶段独立可验证）

### 阶段 1：收敛与规则化（低成本，先做，纯减法 + 确定性提升）

目标：消除输出漂移的主要来源 + 降低交付门槛 + 前端统一入口。全部改动不引入新概念，风险最低。

**T1.1 score 规则化（L1，核心）**
- 文件：`schemas.py`、`app.py`
- 改法：
  - `ReviewCriterion` 保留 LLM 输出的逐条判定（PASS/FAIL/NEED_REVIEW + 理由）；
  - `ReviewEvaluation.score` 改为后端计算：`sum(通过条目 weight) / sum(全部 weight) × 100`；
  - `status` 同理（见 T1.2）；
  - LLM 的 JSON Schema 中移除 score/status 字段，Pydantic 校验时忽略而非报错（向后兼容旧输出）。
- 验收：同一份证据mock 连续评审 5 次，score 与 status 完全一致。

**T1.2 status 规则化（L2）**
- 规则：有 FAIL → FAIL；否则有 NEED_REVIEW → NEED_REVIEW；否则 PASS。
- 注意与 T1.1 在同一处代码实现，一次改动。

**T1.3 CI 结论直判加强（L3）**
- 文件：`review.py`
- 改法：`fetch_ci_evidence` 的 build/test success/fail 在代码层直接映射对应 rubric 条目为 PASS/FAIL，这部分条目不再送 LLM。
- 现状：precheck 已有（缺证据直接 NEED_REVIEW），CI 直判待加强。

**T1.4 部署要求降级（修改1）**
- 文件：`course_data.py`、`review.py`、`prompts.py`
- 改法：
  - `required_evidence=["runtime","deployment"]` → `["runtime"]`，runtime 证据由"本地可运行说明 / CI 结论"满足；
  - `evidence_precheck` 强制列表移除 deployment；
  - 评审 Prompt 中"运行证据"说明改为三选一标准（本地可复现 / CI 通过 / 自愿部署加分）。
- 验收：无部署地址、无 CI 的提交，只要 README 含启动命令 + 学生自述，precheck 不再卡死。

**T1.5 前端四模式 → 双模式收敛（修改5）**
- 文件：`frontend/src/views/TeachView.vue`
- 改法：
  - `MODES` 四按钮组 → 单一"AI 项目导师"入口；
  - 内部行为标签（拆解中/推进中/调试中，来自 route_behavior 的 behavior）轻量展示为 chip；
  - `mode_advice` 推荐卡改为行为建议（不再是"切到 XX 模式"），验收入口收进"提交验收"按钮处；
  - 保留 `xkz_theme_v1` 双主题兼容（组件如按 `theme.isZzz` 分支，两条分支都要改）。
- 验收：学生全程无需手动选模式；指导/验收切换只由系统在"提交验收"处触发。

**阶段 1 退出标准**：评审同证据同分；无部署也能走完验收；前端只有一个 AI 入口。

### 阶段 2：新增能力（中成本，建立在阶段 1 之上）

**T2.1 证据快照 + hash（L4）**
- 文件：`review.py`
- 改法：`collect_evidence` 输出加 sha256 hash，作为"同输入同输出"的前提和缓存 key。

**T2.2 评审幂等缓存（L5）**
- 文件：`app.py`
- 改法：`task_id + snapshot_hash` 在 TTL 内（建议 10 分钟）直接返回缓存评审结果，不重调 LLM。
- 注意：当前无数据库（进程内存即可，方案明确不建库），重启丢失可接受。

**T2.3 Career Text 生成器（修改3，5.1）**
- 文件：`ai_engine/` 新增 `career.py`；`app.py` 加 `POST /api/career/text`
- 设计要点：
  - 模板 + 数据填充，**不用 LLM 自由生成**（避免文案漂移）；LLM 最多润色且输入固定；
  - 输入：project_id + 验收结果（score、通过证据数、CI 结论、任务完成清单）；
  - 模板字段：项目名 / 技术栈（任务 skill + code_context）/ 核心功能（通过的 rubric 标题）/ 量化结果（CI 测试数 + 验收通过数）/ 可验证证据（GitHub 链接）；
  - 输出：`{ "text": "100~200字一段", "bullets": [...] }`；
  - 前端：项目完成页（验收 PASS 后）展示 + "复制"按钮。
- 验收：同一验收结果多次生成，文本一致。

**T2.4 质检陪练试点（修改2，5.2）**
- 文件：`schemas.py`（InterviewQuestion 模型 + Task.interview_questions 可选字段）、`course_data.py`（给"套壳聊天机器人"配 2 题）、`app.py`（接口）、前端卡片
- 硬边界（必须写进代码注释与 Prompt）：
  - 陪练结果**不进** Evidence Store、不影响 score、不写进日志评审字段；
  - 文案叫"面试自检"，不叫"能力验证"；
  - 流程：验收 PASS → 2~3 张问题卡 → 自答 → 展开参考答案锚点自比 → 提示不判分 → "这段项目经历可以写进简历了"。
- 先只给一门课一门项目试点，跑通后再铺。

**T2.5 Artifact Evidence 轻量扩展（5.3）**
- 文件：`code_evidence.py`
- 改法：README 启动命令提取（正则匹配 `uvicorn|npm run|docker compose` 出现与否），作为 runtime 证据加分项。
- 明确不做：部署地址可访问性爬虫、架构图检测。

**阶段 2 退出标准**：完成页能复制出一段稳定简历文字；套壳聊天机器人项目可完整走通"验收 PASS → 面试自检"。

### 阶段 3：存档不执行（防范围回弹）

- 《企业 AI 知识库助手》8-Task 课程设计仅停留在文档第七章；
- 课程工程化（course_data 模板化）只评估不实施；
- 两个待解难点先记录：BYOK embedding 成诚方案（服务端免费额度 or 内置已向量化语料）、可公开语料版权。

### 明确不做清单（执行中随时对照，防止范围回弹）

❌ 部署上线要求 ❌ 能力图谱/Competency Profile ❌ 防作弊检测 ❌ 完整简历导出 ❌ 过程证据采集（录屏/键盘/代码相似度） ❌ 建数据库

---

## 三、执行顺序与依赖关系

```text
阶段1（先做，互相独立可并行）
  T1.1+T1.2 score/status 规则化 ──┐
  T1.3 CI 直判                    ├─→ 阶段1整体回归测试
  T1.4 部署降级                   │
  T1.5 前端收敛                   ─┘
                                    ↓
阶段2（有依赖）
  T2.1 快照hash → T2.2 幂等缓存   （串行，缓存依赖 hash 作 key）
  T2.3 Career Text                （依赖 T1.4，"本地可运行"进简历文案）
  T2.4 质检陪练试点               （依赖 T1.5 完成页改造）
  T2.5 README 启动命令提取        （独立，随时可插）
                                    ↓
阶段3：只写文档，不写代码
```

## 四、风险与注意事项

1. **旧版评审结果兼容**：score/status 改为后端计算后，历史已存的评审记录字段语义变化——当前无数据库、结果存 localStorage，建议前端展示层做一次字段适配说明。
2. **LLM 仍可能输出 score/status**：Pydantic 用"忽略多余字段"策略，不要 strict 拒绝，否则旧 Prompt 未更新时全部报错。
3. **前端双主题**：TeachView 改造必须同时过 zzz / ak 两套主题的视觉验收。
4. **陪练硬边界靠纪律**：不判分是产品原则，代码层面建议陪练接口与评审接口物理隔离（不同 endpoint、不同日志字段），防止未来有人顺手把分数接回去。
5. **部署流程**：按既定约定——本地改码 → git push → 用户手动在阿里云 Workbench `git pull + pm2 restart xkz`；纯前端改动 dist 入库即生效零停机，后端改动预留 1-5 分钟 502 启动窗口。

## 五、建议的验证策略

- 阶段 1 验收用"同证据重评审 5 次"做漂移回归测试（可直接写进 `_test_evidence.py` 的测试习惯里）；
- 阶段 2 用"套壳聊天机器人"作为金丝雀项目端到端跑通全链条；
- 每阶段完成 → commit → push → 用户手动部署 → 线上冒烟后再进下一阶段。
