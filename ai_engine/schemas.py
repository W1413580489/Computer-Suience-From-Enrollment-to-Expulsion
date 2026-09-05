# -*- coding: utf-8 -*-
"""
AI Teaching Engine 核心数据模型（Pydantic v2）

8 个核心业务对象 + 2 个引擎对象：
  Student / Course / Project / Stage / Task / Rubric / Submission / AISession
  AiResponse（AI 结构化输出的校验模型）/ TeachRequest / TeachContext
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

TZ = timezone.utc


def _now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------
class Mode(str, Enum):
    tutor = "tutor"          # 教练：拆解任务、引导方向
    coach = "coach"          # 督学：追问进度、推动执行
    debugger = "debugger"    # 调错：定位报错、逐步修复
    reviewer = "reviewer"    # 评审：对照验收标准评估成果


class HintLevel(str, Enum):
    H0 = 0     # 不提示，仅反问/引导
    H1 = 1     # 提示方向/关键点
    H2 = 2     # 给出思路步骤
    H3 = 3     # 给出具体做法
    H4 = 4     # 给出关键代码/答案片段
    H5 = 5     # 直接给出解决方案
    NONE = "none"


class SkillKey(str, Enum):
    git = "git"
    prompt = "prompt"
    env_setup = "env_setup"
    debug = "debug"
    prd = "prd"
    ui_design = "ui_design"
    vibe_coding = "vibe_coding"
    project_dev = "project_dev"
    ai_assisted = "ai_assisted"
    workflow = "workflow"
    deployment = "deployment"
    rag = "rag"
    paper_writing = "paper_writing"


# ---------------------------------------------------------------------------
# 8 个核心业务对象
# ---------------------------------------------------------------------------
class Student(BaseModel):
    """学生档案。V1 存 localStorage，由前端提交。"""
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    name: str = "匿名学生"
    skills: dict[SkillKey, int] = Field(
        default_factory=lambda: {k: 0 for k in SkillKey}
    )  # 技能→熟练度 0-5
    completed_tasks: list[str] = Field(default_factory=list)
    attempt_count: dict[str, int] = Field(default_factory=dict)  # task_id -> 尝试次数
    timestamp: str = Field(default_factory=_now)


class Course(BaseModel):
    """一门课程 = 课程元信息 + 若干 Project。"""
    id: str
    title: str
    description: str = ""
    projects: list[str] = Field(default_factory=list)  # project_id 列表


class Project(BaseModel):
    """一个项目 = 若干 Stage + Task + Rubric 的完整结构。"""
    id: str
    title: str
    description: str = ""
    stages: list[Stage] = Field(default_factory=list)
    tasks: list[Task] = Field(default_factory=list)
    rubrics: list[Rubric] = Field(default_factory=list)
    source_url: str = ""


class Stage(BaseModel):
    """项目内的阶段。"""
    id: str
    title: str
    order: int
    objective: str = ""          # 本阶段目标
    tasks: list[str] = Field(default_factory=list)  # task_id 列表


class CodeContext(BaseModel):
    """Task 的代码检索提示（课程作者手动标注，指引 Code Retrieval 找到正确文件）。"""
    keywords: list[str] = Field(default_factory=list)       # 关键词匹配（在文件内容中搜索）
    likelyFiles: list[str] = Field(default_factory=list)    # 期望文件名（不含扩展名，小写比对）
    searchPatterns: list[str] = Field(default_factory=list)  # 代码搜索模式（如 "POST.*chat", "httpx.*post"）


class Task(BaseModel):
    """一个任务单元，是 AI 辅导的最小粒度。"""
    id: str
    title: str
    stage_id: str
    order: int
    objective: str = ""                     # 任务目标
    steps: list[str] = Field(default_factory=list)   # 操作步骤列表
    hints: dict[int, str] = Field(default_factory=dict)  # hint_level -> 提示内容
    evidence_required: Literal["code", "code+test", "test", "url", "screenshot", "none"] = "none"
    rubric_ids: list[str] = Field(default_factory=list)
    skill: Optional[SkillKey] = None
    source_url: str = ""                    # 关联飞书文档
    chunk_key: str = ""                     # 关联 chunks.jsonl 的检索前缀（如 "学习指南 > 克隆复现"）
    code_context: Optional[CodeContext] = None  # V1.5：代码检索提示（Sprint 1）


class Rubric(BaseModel):
    """一条验收标准（每条 criterion 独立成对象，支撑逐条评审打分）。

    对齐规格书：criterion / description / requiredEvidence / passCondition / weight。
    """
    id: str
    task_id: str = ""
    criterion: str = ""                 # 验收条件标题（如 "删除 Todo"）
    description: str = ""               # 详细说明
    required_evidence: list[str] = Field(default_factory=list)  # code/runtime/test/screenshot/url
    pass_condition: str = ""            # 达标条件
    weight: int = 1


class Submission(BaseModel):
    """学生提交的成果（用于评审链，对齐规格书 Submission Schema）。"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    task_id: str = ""                 # 与 ReviewRequest.task_id 对齐，可省略
    student_id: str = ""
    github_url: str = ""                  # GitHub 仓库（代码证据）
    deployment_url: str = ""              # 在线访问地址（运行证据）
    code: str = ""                        # 关键代码片段
    screenshot_urls: list[str] = Field(default_factory=list)  # 运行截图（运行证据）
    description: str = ""                 # 自述说明
    submitted_at: str = Field(default_factory=_now)


# V1.5 Sprint 2：Evidence 模型
class EvidenceType(str, Enum):
    CODE = "code"
    CI = "ci"
    RUNTIME = "runtime"
    SCREENSHOT = "screenshot"
    GITHUB = "github"
    DESCRIPTION = "description"
    MANUAL = "manual"
    TRACE = "trace"   # Agent 执行轨迹（agent_trace.json，课程 02+）


class Evidence(BaseModel):
    """一条证据记录（V1.5 Evidence Store）。"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    task_id: str
    rubric_id: str = ""
    type: EvidenceType = EvidenceType.MANUAL
    source: str = ""             # 来源（如 "GitHub Actions" / "TodoList.jsx"）
    content: str = ""            # 证据内容摘要
    confidence: float = 1.0
    created_at: str = Field(default_factory=_now)


class AISession(BaseModel):
    """一次 AI 辅导会话的上下文。"""
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    student_id: str = ""
    task_id: str = ""
    mode: Mode = Mode.tutor
    attempt_count: int = 0
    hint_level: int = 0
    history: list[dict[str, Any]] = Field(default_factory=list)
    # Sprint 4：Debugger 多轮取证状态机（跨轮跟踪，避免重复提问、逐步收敛）
    debug_state: Optional["DebuggerState"] = None
    # 系统错误隔离：上一轮发生的系统内部错误摘要（下一轮注入隔离声明，用后即清）
    last_system_error: Optional[str] = None
    created_at: str = Field(default_factory=_now)


class DebugPhase(str, Enum):
    """Debugger 六段流程的阶段。"""
    symptom = "symptom"      # 收集症状
    evidence = "evidence"    # 要求证据
    narrow = "narrow"        # 缩小范围
    verify = "verify"        # 验证假设
    locate = "locate"        # 定位问题
    explain = "explain"      # 解释原因
    done = "done"


class DebuggerState(BaseModel):
    """Debugger 跨轮取证状态。"""
    phase: DebugPhase = DebugPhase.symptom
    rounds: int = 0                     # 已进行的调试轮次
    last_diagnostic_question: str = ""  # 上一轮反问过的问题（避免原样重复）
    last_suspected_cause: str = ""      # 上一轮给出的怀疑根因
    hypothesis_confirmed: bool = False  # 根因是否已被印证（进入定位/解释阶段）


# ---------------------------------------------------------------------------
# 引擎对象
# ---------------------------------------------------------------------------
class ReviewStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEED_REVIEW = "NEED_REVIEW"


class ReviewCriterion(BaseModel):
    """评审中单条 Rubric 的判定。"""
    rubric_id: str = ""
    status: ReviewStatus = ReviewStatus.NEED_REVIEW
    evidence: str = ""      # 依据的证据来源
    reason: str = ""        # 判定理由


class ReviewEvaluation(BaseModel):
    """评审输出（对齐规格书 Evaluation）。"""
    status: ReviewStatus = ReviewStatus.NEED_REVIEW
    score: int = 0
    criteria: list[ReviewCriterion] = Field(default_factory=list)
    next_step: str = ""     # 下一步需要补充的证据


class HintDecision(BaseModel):
    """Hint Level 计算决策。"""
    level: int = 0
    reason: str = "首次请求，仅引导方向"


class AiResponse(BaseModel):
    """AI 结构化输出（DeepSeek JSON 模式返回，经 Pydantic 校验）。

    无条件字段：
      mode / message / next_action
    条件字段（按指导模式内部行为 behavior，见 prompts.BEHAVIOR_PROMPTS）：
      decompose -> hint_level, hint, leading_question
      advance   -> current_step
      debug     -> suspected_cause, verify_steps, diagnostic_question
    """
    mode: Mode
    message: str                       # 给学生的回复
    next_action: str = ""              # 建议学生下一步做什么
    hints_used: int = 0                # 本次启用的提示等级
    # 拆解行为
    hint_level: Optional[int] = None
    hint: Optional[str] = None
    leading_question: Optional[str] = None
    # 推进行为
    current_step: Optional[str] = None    # 明确学生当前只需做哪一步（任务规划）
    # 调试行为
    suspected_cause: Optional[str] = None
    verify_steps: Optional[list[str]] = None
    diagnostic_question: Optional[str] = None   # 反问学生确认报错位置的诊断问题


class TeachRequest(BaseModel):
    """POST /api/ai/teach 请求体。"""
    session_id: str | None = None
    student: Student | None = None
    course_id: str = "course_001"
    project_id: str = "project_xie_xiu"
    task_id: str = ""
    mode: Mode = Mode.tutor
    user_input: str = ""
    repo_url: str | None = None              # V2：学员的 GitHub 仓库链接（代码证据）
    submission: Submission | None = None
    api_key: str = ""            # BYOK：用户 DeepSeek key
    base_url: str | None = None
    model: str | None = None
    history: list[dict[str, Any]] | None = None


class ReviewRequest(BaseModel):
    """POST /api/ai/review 请求体（评审链 Sprint 5）。"""
    session_id: str | None = None
    project_id: str = "project_chatbot"
    task_id: str = ""
    submission: Submission | None = None     # 学生提交的成果
    repo_url: str | None = None              # 兼容：也可单独传 GitHub 仓库链接（代码证据）
    api_key: str = ""                        # BYOK
    base_url: str | None = None
    model: str | None = None


class TeachContext(BaseModel):
    """组装后的教学上下文（注入 Prompt 前的结构）。"""
    task_id: str = ""
    course_title: str = ""
    project_title: str = ""
    stage_title: str = ""
    task_title: str = ""
    task_objective: str = ""
    task_steps: list[str] = Field(default_factory=list)
    rubric_criteria: list[str] = Field(default_factory=list)
    material: list[str] = Field(default_factory=list)   # 检索到的参考 chunk 文本
    code_evidence: str = ""         # V2：学员 GitHub 仓库的代码证据文本（注入 Prompt）
    debug_progress: str = ""        # Sprint 4：Debugger 上一轮取证进度（避免重复提问）
    behavior: str = ""              # 指导模式内部行为（decompose/advance/debug，系统路由）
    hint_level: int = 0
    skill: Optional[str] = None
    source_url: str = ""