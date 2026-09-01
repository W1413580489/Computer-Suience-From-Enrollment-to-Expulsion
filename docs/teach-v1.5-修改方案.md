# AI Teaching Engine V1.5 修改方案

> 基于飞书文档《AI Teaching Engine V1.5》需求 + 当前项目现状 + 确认决策  
> 2026-08-27

---

## 一、已确认的决策

| 问题 | 决策 |
|------|------|
| Q1: Code Retrieval 元数据谁维护？ | 课程作者在 `course_data.py` 手动写 |
| Q2: Evidence Store 存在哪里？ | 进程内存 dict（重启丢失） |
| Q3: Reviewer 返回值改不改流式？ | 不改，保持现有 JSON 返回 |
| Q4: AI 自检重试次数和策略？ | 最多重试 2 次，不暴露 retry_count 到前端 |
| Q5: 验收测试写 pytest？ | 不需要，手动验证 |
| 数据库表结构 | 不上，后续大规模再考虑 |
| 代码目录重构 | 不重构，保持 flat 结构 |
| 已完成的 Rubric/Evidence/Reviewer | 不做重复工作 |

---

## 二、改动清单

### Sprint 1：Code Retrieval 升级（3 项改动）

#### 1.1 Task 模型添加 `code_context` 字段

**文件：** `schemas.py`

```python
class CodeContext(BaseModel):
    """Task 的代码检索提示（课程作者手动标注）。"""
    keywords: list[str] = Field(default_factory=list)          # 关键词匹配
    likelyFiles: list[str] = Field(default_factory=list)        # 期望文件名（不含扩展名）
    searchPatterns: list[str] = Field(default_factory=list)     # 代码搜索模式

class Task(BaseModel):
    ...
    # 新增字段
    code_context: Optional[CodeContext] = None
```

#### 1.2 补全 Task 的 code_context 数据

**文件：** `course_data.py`

为"套壳聊天机器人"的 5 个 Task 逐一添加 `code_context`：

| Task | keywords | likelyFiles |
|------|----------|-------------|
| `task_setup` | 环境/Python/API/Key/项目结构 | (无，证据=自述) |
| `task_backend` | POST/chat/FastAPI/DeepSeek/httpx/CORS | main.py, app.py, requirements.txt |
| `task_frontend` | fetch/index.html/消息/输入框/发送 | index.html |
| `task_link` | 联调/端口/CORS/uvicorn | main.py, index.html |
| `task_review` | (无，证据=自述+部署) | (无，证据=自述+部署) |

#### 1.3 `code_evidence.py` 改造：按 Task 评分候选文件

**当前行为：** 固定选取 README / 依赖 / 主入口 / 配置文件（`_pick_key_files()`）

**改为：** 三步走

```
1. 文件名匹配评分（基于 Task.code_context.likelyFiles）
2. 关键词搜索评分（基于 Task.code_context.keywords，在文件内容中搜索）
3. AI 二次筛选（把候选文件列表 + Task 目标给 AI，让 AI 判断真正相关哪些）
```

**改动：**
- 新增 `rank_candidate_files(paths, task_context)` 函数，按文件名/关键词评分
- 新增 `ai_relevance_filter(candidates, task, client)` 函数，调用 LLM 做二次判断
- 修改 `build_code_evidence()` 入口，允许传入 `task_id` 参数
- 当 `code_context` 为 None 时回退到当前固定选取逻辑

#### 1.4 新增 `POST /api/github/retrieve` 接口

**文件：** `app.py`

```python
class CodeRetrieveRequest(BaseModel):
    repo_url: str
    task_id: str = ""

@router.post("/api/github/retrieve")
async def code_retrieve(req: CodeRetrieveRequest):
    """按 Task 检索相关代码，返回候选文件 + AI 筛选结果。"""
```

**内部流程：** `loadTask() → loadRepositoryTree() → candidateGeneration() → fetchCandidateFiles() → candidateRanking() → AI relevance filtering → return CodeEvidence`

**返回格式：**

```json
{
  "ok": true,
  "data": {
    "task_id": "task_backend",
    "files": [
      { "path": "main.py", "startLine": 1, "endLine": 40, "relevance": 0.92, "reason": "FastAPI app entry" },
      { "path": "requirements.txt", "startLine": 1, "endLine": 5, "relevance": 0.85, "reason": "Dependencies" }
    ]
  }
}
```

---

### Sprint 2：Evidence Store + 评审硬约束（2 项改动）

#### 2.1 新增 Evidence 模型 + 进程内存 Store

**文件：** `schemas.py`

```python
class EvidenceType(str, Enum):
    CODE = "code"
    CI = "ci"
    RUNTIME = "runtime"
    SCREENSHOT = "screenshot"
    GITHUB = "github"
    DESCRIPTION = "description"
    MANUAL = "manual"

class Evidence(BaseModel):
    """一条证据记录。"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    task_id: str
    rubric_id: str
    type: EvidenceType
    source: str             # 来源（如 "GitHub Actions" / "TodoList.jsx"）
    content: str            # 证据内容摘要
    confidence: float = 1.0
    created_at: str = Field(default_factory=_now)
```

**文件：** `app.py`

```python
# 进程内存 Evidence Store
_evidence_store: dict[str, list[Evidence]] = {}  # task_id -> [Evidence]

def store_evidence(ev: Evidence):
    key = ev.task_id
    if key not in _evidence_store:
        _evidence_store[key] = []
    _evidence_store[key].append(ev)

def get_evidence(task_id: str, rubric_id: str | None = None) -> list[Evidence]:
    evs = _evidence_store.get(task_id, [])
    if rubric_id:
        evs = [e for e in evs if e.rubric_id == rubric_id]
    return evs
```

#### 2.2 Evidence 硬约束

**文件：** `review.py` — 修改 `build_review_system_prompt()` 前增加代码层检查：

```python
def evidence_precheck(rubrics: list[Rubric], available: dict[str, str]) -> list[str]:
    """检查是否有 Rubric 所需证据类型完全缺失，缺失则标记 NEED_REVIEW 不走 LLM。"""
    forced: list[str] = []
    for r in rubrics:
        needed = set(r.required_evidence)
        if not needed:
            continue
        present = set(available.keys())
        missing = needed - present
        if missing:
            forced.append(f"Rubric {r.id} 缺少必要证据类型：{', '.join(missing)}，自动标记 NEED_REVIEW")
    return forced
```

在 `review` 接口中，LLM 调用前先做 precheck，如果某些 Rubric 缺失关键证据，直接返回 NEED_REVIEW + 提示（不走 LLM，节省 token）。

---

### Sprint 3：AI 自检升级（1 项改动）

#### 3.1 `response_validator.py` 增加 6 项检查

**当前已有 4 条规则：** low hint level 不能给答案 / 回复不能过短 / reviewer 必须有 score+passed / debugger 必须给 verify_steps 和 diagnostic_question

**新增 6 项检查（对应文档要求）：**

```python
_VIOLATION_CHECKS = {
    "role_compliance":       # 当前 mode 是 debugger，AI 有没有真的在 debug？
    "hint_compliance":       # hint_level=1 却给了完整代码？
    "context_compliance":    # 当前 Task 是"删除 Todo"，AI 却在讲 React Router？
    "evidence_compliance":   # reviewer 没有测试证据却判 PASS？
    "learning_compliance":   # 学生还没尝试，AI 直接完成任务？
    "safety":                # AI 编造运行结果/代码/项目状态？
}
```

**重试策略优化：** 当前已做 1 次重试 → 改为最多 2 次重试，重试消息携带 `Previous Response + Detected Violations`。

---

## 三、改动文件汇总

| 文件 | 改动 | Sprint |
|------|------|--------|
| `schemas.py` | 新增 `CodeContext`、`Evidence`、`EvidenceType` 模型；`Task` 加 `code_context` 字段 | 1+2 |
| `course_data.py` | 为 5 个 Task 补 `code_context` 数据 | 1 |
| `code_evidence.py` | 新增 `rank_candidate_files()`、`ai_relevance_filter()`；`build_code_evidence()` 支持 task_id 参数 | 1 |
| `app.py` | 新增 `POST /api/github/retrieve` 接口；新增 `_evidence_store` 及 `store_evidence()`/`get_evidence()`；`review` 接口增加 evidence precheck | 1+2 |
| `review.py` | 新增 `evidence_precheck()` 函数；`build_review_system_prompt()` 前增加代码层检查 | 2 |
| `response_validator.py` | 新增 6 项检查；重试次数改为 2 次 | 3 |

---

## 四、执行顺序

```
Sprint 1 (Code Retrieval) → Sprint 2 (Evidence Store) → Sprint 3 (AI 自检)
```

每个 Sprint 完成后可独立部署验证，不相互阻塞。

---

## 五、不做的内容

| 内容 | 原因 |
|------|------|
| 数据库表结构 | 进程内存够用，后续大规模再上 |
| 代码目录重构 | 保持 flat 结构，避免 import 断裂 |
| SSE 流式输出 | 保持现有 JSON 同步返回 |
| 前端改动 | 本版本全部为后端改动，前端只需适配新接口返回字段 |
| 前端暴露 retry_count | 用户确认不需要 |
| 新课程数据 | 只补现有"套壳聊天机器人"的 code_context |
| 已完成的 Rubric/Evidence 体系 | 当前已实现，无需再建 |