# AI Teaching Engine — Project Overview (AI-readable)

## Quick Reference

| Item | Value |
|------|-------|
| Project root | `d:\Assistant\tralis\xkz-agent\` |
| Engine dir | `d:\Assistant\tralis\xkz-agent\ai_engine\` |
| Data dir | `d:\Assistant\tralis\xkz-agent\data\` |
| Backend port | 8099 (uvicorn) |
| Test page | 8130 (http.server) |
| DB | None (in-memory + JSONL logs) |
| RAG | `chunks.jsonl` + bge-small-zh-v1.5 |
| LLM | DeepSeek (BYOK) |
| Default model | `deepseek-v4-flash` |
| Default base URL | `https://api.deepseek.com` |

## Architecture Overview

```
┌─────────────┐     HTTP/JSON     ┌──────────────────────────────────────┐
│  testpage    │ ────────────────> │  FastAPI Backend (:8099)            │
│  (static     │                   │                                      │
│   HTML/JS)   │ <──────────────── │  /api/ai/teach    — Tutor/Coach/    │
│              │                   │  /api/ai/review   — Reviewer         │
│  Browser     │                   │  /api/ai/health   — Health check     │
│  localhost:  │                   │  /api/ai/config   — Course config    │
│  8130 or     │                   │  /api/ai/stats    — AI Evaluation    │
│  file://     │                   │  /api/ai/feedback — User feedback    │
└─────────────┘                   │  /api/github/retrieve — Code retrv   │
                                  └──────────────────────────────────────┘
                                           │
                                    ┌──────┴──────┐
                                    │  code_evidence.py  (GitHub REST API)
                                    │  course_data.py    (chunks.jsonl RAG)
                                    │  llm_client.py     (DeepSeek API)
                                    └──────────────────┘
```

## File Inventory (ai_engine/)

| File | Size | Role |
|------|------|------|
| `app.py` | 25,220 B | **Entry point**: FastAPI app, 6 API routes, orchestration |
| `schemas.py` | 11,828 B | **Data models**: 15+ Pydantic models, enums, type definitions |
| `code_evidence.py` | 19,663 B | **Code Evidence Pipeline**: GitHub repo parsing, file tree, CI Actions |
| `course_data.py` | 17,019 B | **Course data**: "套壳聊天机器人" project, 3 stages, 5 tasks, 17 rubrics |
| `review.py` | 9,198 B | **Review chain**: Evidence collector, precheck, Reviewer prompt builder |
| `prompts.py` | 9,614 B | **System prompts**: Core policy + 4 mode-specific prompts |
| `response_validator.py` | 6,397 B | **Quality control**: 6 validation checks, auto-retry on violation |
| `llm_client.py` | 5,468 B | **LLM gateway**: DeepSeek API, JSON mode, retry, Pydantic validation |
| `logs.py` | 4,670 B | **Event logging**: JSONL append, thread-safe, AI Evaluation stats |
| `context_builder.py` | 2,512 B | **Context assembly**: Task info + RAG retrieval + hint level |
| `hint.py` | 1,578 B | **Hint level state machine**: 0-5 progression |
| `testpage.html` | 33,474 B | **Frontend test page**: Chat UI, review card, CI display, mode switching |
| `__init__.py` | 24 B | Package marker |
| `_test_evidence.py` | 688 B | Test helper |

## API Endpoints

### `GET /api/ai/health`
Health check. Returns status, engine name, model info.

### `GET /api/ai/config`
Returns course structure (projects, stages, tasks), available models, modes, hint levels.

### `POST /api/ai/teach`
**Core teaching interface.** BYOK authentication.

**Required fields:**
- `task_id`: string
- `api_key`: string (BYOK)
- `user_input`: string
- `mode`: "tutor" | "coach" | "debugger" | "reviewer"

**Optional fields:**
- `repo_url`: GitHub repo URL (triggers code evidence pipeline)
- `student`: Student object (localStorage, attempt tracking)
- `history`: previous messages for context
- `submission`: Submission object for reviewer mode
- `model`: override model name
- `base_url`: override API base URL

**Response structure:**
```json
{
  "ok": true,
  "data": {
    "mode": "tutor",
    "message": "AI reply text",
    "next_action": "suggested next step",
    "hints_used": 1,
    "hint_level": 1,
    "hint": "...",
    "leading_question": "...",
    "current_step": "...",
    "suspected_cause": "...",
    "verify_steps": [...],
    "diagnostic_question": "...",
    "evaluation": "...",
    "score": 85,
    "passed": true,
    "evidence": {"status": "ok", "repo": "owner/repo", "file_count": 42},
    "debug_state": {"rounds": 2, "phase": "verify", "phase_desc": "验证假设"},
    "mode_advice": {"mode": "coach", "reason": "...", "task_id": "..."},
    "quality_warnings": [],
    "latency_ms": 1234,
    "session_id": "s_abc123"
  }
}
```

### `POST /api/ai/review`
**Independent review chain.** BYOK.

**Required:** `task_id`, `api_key`
**Optional:** `submission` (github_url, deployment_url, code, description, screenshot_urls), `repo_url`

**Flow:**
1. Evidence Collector: gather code evidence from GitHub if repo_url provided
2. CI evidence: fetch GitHub Actions workflows and run conclusions
3. Evidence Precheck: check each Rubric's required_evidence against available evidence
4. If ALL rubrics lack critical evidence → return NEED_REVIEW directly (no LLM call)
5. If some rubrics are passable → build Reviewer system prompt, call LLM
6. Merge forced NEED_REVIEW results with LLM evaluation

### `POST /api/ai/feedback`
Records user satisfaction on a teach response. Updates the most recent matching event's `accepted_by_user` field.

### `GET /api/ai/stats`
AI Evaluation aggregation. Returns task completion rates, hint distribution, mode distribution, blocked tasks, quality warnings.

### `POST /api/github/retrieve`
Task-aware code retrieval. Returns candidate files with relevance scores and AI-filtered results.

## Data Models (schemas.py)

### Core Business Objects
- **Student**: session_id, name, skills, completed_tasks, attempt_count
- **Course**: id, title, projects
- **Project**: id, title, stages, tasks, rubrics
- **Stage**: id, title, order, objective, tasks (list of task_ids)
- **Task**: id, title, stage_id, order, objective, steps, hints, evidence_required, rubric_ids, skill, chunk_key, code_context
- **Rubric**: id, task_id, criterion, description, required_evidence, pass_condition, weight
- **Submission**: task_id, github_url, deployment_url, code, screenshot_urls, description
- **Evidence**: task_id, rubric_id, type, source, content, confidence

### Enums
- **Mode**: tutor, coach, debugger, reviewer
- **HintLevel**: 0-5 + NONE
- **SkillKey**: git, prompt, env_setup, debug, prd, ui_design, vibe_coding, project_dev, etc.
- **EvidenceType**: code, ci, runtime, screenshot, github, description, manual
- **DebugPhase**: symptom, evidence, narrow, verify, locate, explain, done
- **ReviewStatus**: PASS, FAIL, NEED_REVIEW

### Engine Objects
- **AiResponse**: mode, message, next_action, hints_used + conditional fields per mode
- **TeachRequest**: session_id, student, course_id, project_id, task_id, mode, user_input, repo_url, submission, api_key, base_url, model, history
- **ReviewRequest**: session_id, project_id, task_id, submission, repo_url, api_key, base_url, model
- **TeachContext**: assembled context for prompt injection
- **ReviewEvaluation**: status, score, criteria (list of ReviewCriterion), next_step
- **ReviewCriterion**: rubric_id, status, evidence, reason
- **DebuggerState**: phase, rounds, last_diagnostic_question, last_suspected_cause, hypothesis_confirmed
- **CodeContext**: keywords, likelyFiles, searchPatterns (for task-aware code retrieval)

## Course Structure: "套壳聊天机器人"

### 3 Stages, 5 Tasks, 17 Rubrics

```
Stage 1: ① 拆解与准备 (Tutor)
  ├── task_setup: 拆解任务与准备环境
  │   ├── rb_setup_1: 能说清前后端组成 (description)
  │   ├── rb_setup_2: Python 环境就绪 (description)
  │   └── rb_setup_3: 已准备 API Key (description)

Stage 2: ② 开发与联调 (Coach / Debugger)
  ├── task_backend: 写后端接口 (code)
  │   ├── rb_backend_1: POST /chat 接口 (code)
  │   ├── rb_backend_2: 带 API Key 转发 DeepSeek (code)
  │   ├── rb_backend_3: 能 uvicorn 启动 (code + runtime)
  │   └── rb_backend_4: 能解释代码 (description)
  ├── task_frontend: 写前端页面 (code)
  │   ├── rb_frontend_1: 输入框+消息列表+发送按钮 (code)
  │   ├── rb_frontend_2: fetch POST 后显示回答 (code + runtime)
  │   └── rb_frontend_3: 消息可滚动 (code)
  └── task_link: 联调跑通 (test)
      ├── rb_link_1: 前后端联通 (runtime + test)
      ├── rb_link_2: 报错能正确排查 (description + runtime)
      └── rb_link_3: API Key 未在前端 (code) [weight=2]

Stage 3: ③ 提交验收 (Reviewer)
  └── task_review: 提交成果验收 (code)
      ├── rb_review_1: 正常问答 (runtime + deployment) [weight=2]
      ├── rb_review_2: 消息可滚动 (code)
      ├── rb_review_3: Key 只在后端 (code)
      └── rb_review_4: 能讲清数据流向 (description)
```

### RAG Chunk Keys
Tasks reference `chunk_key` to retrieve relevant chunks from `chunks.jsonl`:
- `task_setup` → "套壳聊天机器人实战 > 前置准备"
- `task_backend` → "套壳聊天机器人实战 > 后端接口"
- `task_frontend` → "套壳聊天机器人实战 > 前端页面"
- `task_link` → "套壳聊天机器人实战 > 联调与验收"
- `task_review` → "套壳聊天机器人实战 > 联调与验收"

## State Machines

### 1. Hint Level State Machine (hint.py)
```
attempt_count=0 → L0: 仅反问/引导
attempt_count=1 → L1: 提示方向
attempt_count=2 → L2: 思路步骤
attempt_count=3 → L3: 具体做法
attempt_count≥4 → L4: 关键代码片段
attempt_count≥4 + "直接给答案" → L5: 完整方案
```

### 2. Debugger Phase State Machine (app.py update_debugger_state)
```
symptom → evidence → narrow → verify → locate → explain → done

Transitions:
- Round 0: symptom
- suspected_cause present AND specific (not "未确定"/"尚不"/"无法") → verify
- suspected_cause is vague → evidence
- Not symptom and not evidence → stays in current phase
```

### 3. Mode Advice State Machine (app.py compute_mode_advice)
```
Tutor finishes → Coach (next task)
Coach → user says "完成了" → Reviewer
Debugger (locates bug) → Coach (continue)
Reviewer PASS → Coach (next task), or DONE (all tasks complete)
Reviewer FAIL → Coach (fix and resubmit)
```

## Code Evidence Pipeline (code_evidence.py)

### Flow
```
repo_url → parse_repo_url() → (owner, repo)
  → _repo_default_branch(owner, repo) → branch name
  → _fetch_tree(owner, repo, branch) → raw file tree
  → _filter_structure(tree) → filtered paths (skip .git, node_modules, etc.)
  → _pick_key_files(paths, tree) → README, deps, main, config files
    OR with code_context:
      → rank_candidate_files(paths, code_context) → scored files
      → optionally ai_relevance_filter(ranked, task, client) → LLM picks relevant files
  → _fetch_file_content(owner, repo, branch, path) → file text (base64 decoded)
  → _assemble() → structured evidence text
  → fetch_ci_evidence(owner, repo, branch) → GitHub Actions status
    → _ci_dimension(name) → maps workflow name to "build"/"test"/"lint"/"runtime"
  → combine evidence + CI block → evidence_text
```

### CI Evidence (fetch_ci_evidence)
- Calls `GET /repos/{owner}/{repo}/actions/workflows` for workflow list
- Calls `GET /repos/{owner}/{repo}/actions/runs?branch={branch}` for run conclusions
- Maps each workflow name to a dimension (build/test/lint/runtime) using keyword matching
- Output format: `[CI 自动验收证据]（来自 GitHub Actions，system 判定，权威）`
- Failures (403 rate limit, 404 disabled, network error) → non-blocking, returns error in CI block

### Evidence Priority Rules (injected into Reviewer prompt)
1. CI evidence is system-verified, not AI guesswork
2. build workflow conclusion=success → "可构建/能启动" → PASS related criteria
3. test workflow conclusion=success → functional criteria can PASS
4. No CI workflows → runtime/test criteria must rely on student's real evidence (deployment URL, description), not AI speculation

### Caching
- TTL cache (300s) keyed by repo_url
- `invalidate_cache()` for testing

## Review Chain (review.py)

### Evidence Collector (collect_evidence)
Normalizes submission fields + code evidence into a dict of evidence types:
- `code`: GitHub code evidence + student's pasted code
- `runtime`: deployment URL
- `test`: (from submission)
- `deployment`: deployment URL
- `description`: student's self-description
- `url`: GitHub URL (if not fetched)

### Evidence Precheck (evidence_precheck)
- For each Rubric, checks if `required_evidence` is present in available evidence
- Missing critical evidence → forced NEED_REVIEW (no LLM call)
- If ALL rubrics have missing evidence → return NEED_REVIEW response directly, never call LLM
- If some rubrics passable → pass only those to LLM, merge forced NEED_REVIEW afterward

### Reviewer Prompt Builder (build_review_system_prompt)
- Injects: task info, rubric list, available evidence, missing evidence
- GitHub evidence status section: tells reviewer whether code was actually fetched or just URL-only
- CI hard evidence priority rules
- 9 review rules (evidence-based, no fabrication, strict scoring)
- JSON output format specification

## Quality Control (response_validator.py)

### 6 Validation Checks
1. **Hint Compliance**: L0-1 shouldn't give full answers or code
2. **Role Compliance**: debugger must have suspected_cause, verify_steps, diagnostic_question
3. **Context Compliance**: reply should stay on task topic
4. **Evidence Compliance**: reviewer score/passed consistency, no contradiction
5. **Learning Compliance**: low attempt count shouldn't get complete solutions
6. **Safety/Integrity**: no fabricated run results, no premature root cause conclusion

### Retry Mechanism
- Up to 2 retries when validation fails
- Retry message includes specific validation errors
- Accepts retry output only if it improves (fewer issues)

## LLM Client (llm_client.py)

### DeepSeek Integration
- `response_format={"type": "json_object"}` for structured output
- `temperature=0.4` for consistent structured output
- Pydantic validation of parsed JSON
- Retry on validation failure (up to 2 times)

### Error Handling
- `PermissionError` (401/403) → KEY_INVALID
- `TimeoutError` (429) → RATE_LIMITED
- `RuntimeError` (other) → PROVIDER_DOWN
- `_extract_json()`: robust JSON extraction (strip markdown fences, find first/last brace)

## Data Flow: Teach Request

```
User Input
    │
    ▼
app.py teach()
    ├── Validate task_id, api_key, user_input
    ├── Build/retrieve AISession (in-memory)
    ├── build_context()
    │   ├── Get task/stage/project from course_data
    │   ├── Calculate hint_level from attempt count
    │   ├── Retrieve RAG chunks by chunk_key → material
    │   └── Return TeachContext
    ├── If repo_url: build_code_evidence() → inject code_evidence into context
    ├── If debugger mode: render_debug_progress() → inject debug_progress
    ├── build_system_prompt() → CorePolicy + context + mode prompt + output format
    ├── LLMClient.teach() → call DeepSeek, parse AiResponse
    ├── validate() → retry if quality issues
    ├── update_debugger_state() → advance phase
    ├── compute_mode_advice() → suggest next mode/task
    ├── log_event() → structured JSONL log
    └── Return JSON response
```

## Data Flow: Review Request

```
User Input (task_id + submission/repo_url)
    │
    ▼
app.py review()
    ├── Validate task_id, api_key
    ├── Get task, rubrics from course_data
    ├── If repo_url: build_code_evidence()
    │   ├── GitHub file tree + key files
    │   └── fetch_ci_evidence() → workflow status
    ├── collect_evidence() → dict of available evidence
    ├── evidence_precheck() → forced NEED_REVIEW vs passable
    ├── If all forced: return NEED_REVIEW directly (no LLM)
    ├── build_review_system_prompt() → Rubric list + evidence
    ├── LLMClient.review() → call DeepSeek, parse ReviewEvaluation
    ├── Merge forced NEED_REVIEW results
    ├── log_event() → structured JSONL log
    └── Return JSON response
```

## Logging & AI Evaluation (logs.py)

### Event Schema
Each event is a JSONL line with fields:
- `ts`: timestamp
- `type`: "teach" | "review" | "feedback"
- `session_id`, `student_id`, `project_id`, `task_id`
- `mode`: string
- `attempt_count`, `hint_level`
- `user_message`, `ai_response` (truncated)
- `next_action`, `accepted_by_user`
- `task_completed`, `review_status`, `review_score`
- `quality_warnings`: list of validation issues
- `repo_used`: boolean

### Stats (compute_stats)
- Total teach/review calls
- Per-task attempt counts
- Task completion rate
- Hint level distribution
- Mode distribution
- Early answer warnings (quality violations)
- Blocked tasks (attempts ≥ 3, not completed)
- Feedback acceptance rate

## Deployment

### Local
```bash
cd d:\Assistant\tralis\xkz-agent\ai_engine
python -m uvicorn app:app --host 0.0.0.0 --port 8099
python -m http.server 8130  # test page
```

### Server (production)
- FastAPI behind Nginx reverse proxy
- Nginx config: proxy_buffering off, proxy_cache off, proxy_http_version 1.1 (for SSE)
- Nginx on port 8080, custom proxy on ports 80/443
- RAG: bge-small-zh-v1.5 FP32, no reranker (1.8G memory constraint)
- 2G swap configured
- GITHUB_TOKEN env var for higher API rate limit

## Key Design Decisions

1. **BYOK (Bring Your Own Key)**: API key passed per-request, not stored server-side. Enables students to use their own DeepSeek credits.

2. **No persistent DB**: In-memory sessions + JSONL logs. Sessions survive process restart (logs only), sessions are lost on restart. Adequate for V1.

3. **Evidence First review**: No AI guessing. If evidence is missing, it's NEED_REVIEW. The evidence precheck runs before LLM to avoid wasting tokens.

4. **CI as system-verified truth**: GitHub Actions results are injected as authoritative evidence, replacing AI speculation about runtime behavior.

5. **Structured output via JSON mode**: All LLM responses are constrained to JSON schema, validated by Pydantic. This enables deterministic frontend rendering and downstream processing.

6. **Quality auto-retry**: If validation fails, the error is fed back to the model for self-correction, up to 2 retries.

7. **Code evidence via GitHub API exclusively**: Uses api.github.com/contents (not raw.githubusercontent.com) to avoid DNS/connectivity issues. Base64 decoded server-side.

8. **Frontend as standalone HTML**: No framework, no build step. Single HTML file with embedded CSS/JS. Suitable for file:// or minimal http.server.

## Test Page Features (testpage.html)

- Dark theme, responsive layout (sidebar + chat area)
- API Key management (localStorage, password visibility toggle)
- Model selection from backend config
- Task selection with stage progress bar (3 stages, stage completed when all tasks done)
- 4 mode buttons (Tutor/Coach/Debugger/Reviewer) with descriptions
- GitHub repo URL input (optional, triggers code evidence)
- Review panel: deployment URL, code block, description, review button
- Chat interface with structured message rendering
- Mode advice card with one-click mode/task switching
- Feedback buttons on each AI response
- Student progress tracking (localStorage)
- Statistics panel (AI Evaluation data)
- Session management (reset, clear chat)
- CI evidence display in review cards (workflow chips with PASS/FAIL colors)
- Code evidence status display in review cards (fetched/failed)

## Error Codes

| Code | Meaning | HTTP |
|------|---------|------|
| NO_TASK | task_id not provided | 400 |
| NO_API_KEY | API key not provided | 400 |
| EMPTY_INPUT | Empty user input | 400 |
| BAD_TASK | Task not found | 404 |
| NO_RUBRIC | No rubrics for task | 404 |
| KEY_INVALID | API key rejected by provider | 401 |
| RATE_LIMITED | Provider rate limit | 429 |
| PROVIDER_DOWN | Provider service error | 502 |
| BAD_REPO_URL | Cannot parse GitHub URL | (evidence) |
| REPO_NOT_FOUND | Repo/branch doesn't exist | (evidence) |
| RATE_LIMITED | GitHub API rate limit | (evidence) |
| CI_RATE_LIMITED | GitHub Actions rate limit | (ci) |
| CI_DISABLED | Actions disabled for repo | (ci) |
| CI_NETWORK | Cannot connect to GitHub | (ci) |
| NETWORK | Cannot connect to GitHub | (evidence) |
| EMPTY_REPO | No source files found | (evidence) |
| UNKNOWN | Unexpected error | (evidence) |