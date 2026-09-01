# -*- coding: utf-8 -*-
"""
评审链（Sprint 5）：Submission → Evidence Collector → Rubric → Reviewer → Evaluation。

对齐规格书：
  - Rubric 是"每条验收条件"一个对象，含 requiredEvidence / passCondition / weight
  - Reviewer 遵循 **Evidence First**：没有充分证据 → NEED_REVIEW，绝不凭"看起来合理"判 PASS
  - 独立 POST /api/ai/review 流水线
"""
from __future__ import annotations

from schemas import ReviewEvaluation, ReviewRequest, Rubric, Submission, Task


# ---------------------------------------------------------------------------
# Evidence Collector
# ---------------------------------------------------------------------------
def collect_evidence(submission: Submission | None, repo_code_text: str = "") -> dict[str, str]:
    """把 submission 各字段跟仓库代码证据归一成"可用证据"清单。

    返回 { 证据类型: 文本 }，证据类型 ∈ code / runtime / test / url / description。
    """
    ev: dict[str, str] = {}
    sub = submission or Submission(task_id="")

    if repo_code_text:
        ev["code"] = f"GitHub 代码证据（已拉取结构与关键文件内容）：\n{repo_code_text}"
    elif sub.github_url:
        ev["url"] = f"GitHub 仓库地址：{sub.github_url}（尚未拉取，仅链路可访问）"
        ev["code"] = f"GitHub 仓库地址已提供：{sub.github_url}"

    if sub.code:
        ev["code"] = (ev.get("code") + "\n" if "code" in ev else "") + f"学生粘贴的代码片段：\n{sub.code}"

    if sub.deployment_url:
        ev["deployment"] = f"在线部署地址（可访问验收）：{sub.deployment_url}"
        ev["runtime"] = f"在线部署地址（运行证据）：{sub.deployment_url}"

    if sub.description:
        ev["description"] = f"学生自述说明：\n{sub.description}"

    return ev


def evidence_text(available: dict[str, str]) -> str:
    if not available:
        return "（学生本次未提交任何证据）"
    lines = []
    label = {
        "code": "代码证据", "runtime": "运行证据", "test": "测试证据",
        "deployment": "部署地址", "url": "仓库链接",
        "description": "学生自述",
    }
    for typ, text in available.items():
        lines.append(f"[{label.get(typ, typ)}] {text}")
    return "\n\n".join(lines)


def _missing_evidence(rubrics: list[Rubric], available: dict[str, str]) -> list[str]:
    """按各 Rubric 的 requiredEvidence，反推哪些证据类型仍缺失（供 next_step 指引）。"""
    needed: set[str] = set()
    for r in rubrics:
        needed.update(r.required_evidence)
    present = {t for t in available if t != "description"}
    return sorted(needed - present)


# V1.5 Sprint 2：Evidence 硬约束——证据缺失时直接 NEED_REVIEW，不走 LLM
def evidence_precheck(rubrics: list[Rubric], available: dict[str, str]) -> dict:
    """代码层预检：逐条 Rubric 检查 requiredEvidence 是否齐备。

    返回:
      {
        "all_passable": bool,        # 是否所有 Rubric 都有足够证据走 LLM
        "forced_needs_review": [    # 证据缺失的 Rubric（直接 NEED_REVIEW）
          {"rubric_id": str, "missing": [str], "reason": str}
        ],
        "passable_rubrics": list[Rubric],  # 有足够证据的 Rubric（交给 LLM 判断）
      }
    """
    forced = []
    passable = []
    present = set(available.keys())

    for r in rubrics:
        needed = set(r.required_evidence)
        if not needed:
            # 无证据要求的 Rubric 交给 LLM
            passable.append(r)
            continue
        missing = needed - present
        # description 不算硬证据
        missing_real = {m for m in missing if m != "description"}
        if missing_real:
            forced.append({
                "rubric_id": r.id,
                "missing": sorted(missing_real),
                "reason": f"缺少必要证据类型：{', '.join(sorted(missing_real))}，无法自动判定",
            })
        else:
            passable.append(r)

    return {
        "all_passable": len(forced) == 0,
        "forced_needs_review": forced,
        "passable_rubrics": passable,
    }


# ---------------------------------------------------------------------------
# Reviewer System Prompt
# ---------------------------------------------------------------------------
def build_review_system_prompt(task: Task, rubrics: list[Rubric],
                               available: dict[str, str]) -> str:
    rubric_lines = []
    for i, r in enumerate(rubrics, 1):
        rubric_lines.append(
            f"{i}. [{r.id}] {r.criterion}\n"
            f"   说明：{r.description}\n"
            f"   所需证据：{', '.join(r.required_evidence) or '自述即可'}\n"
            f"   达标条件：{r.pass_condition}（权重 {r.weight}）"
        )

    missing = _missing_evidence(rubrics, available)
    missing_text = "；".join(missing) if missing else "无（全部所需证据类型齐备）"

    # 区分代码证据是否真的被拉到（决定 Reviewer 能否基于代码判，还是只能看链接）
    vals = [t for t in available.values() if isinstance(t, str)]
    has_gh_code = any("GitHub 代码证据" in t for t in vals)
    has_gh_url_only = any(t.startswith("GitHub 仓库地址已提供") for t in vals)
    if has_gh_code:
        gh_note = (
            "【GitHub 代码证据状态】已成功拉取该 GitHub 仓库的结构与关键文件（依赖/主入口/配置）。\n"
            "  - 必须基于这些代码判断：是否存在 POST /chat、API Key 是否只在后端而未出现在前端/页面、代码结构是否符合任务。\n"
            "  - 不得再说“仅凭仓库链接无法判断代码”——代码你已实际读过。代码证据充分时，相关验收项就按代码给出 PASS/FAIL，并引用你判断所依据的文件。\n"
            "  - 注意：代码证据只能证明「写了什么」，不能证明「跑没跑通」。运行/能问答/消息滚动仍以部署地址、CI 结论为准；缺运行证据的项记 NEED_REVIEW，并明确让学生补部署地址或运行说明。")
    elif has_gh_url_only:
        gh_note = (
            "【GitHub 代码证据状态】学生仅提供了仓库链接，但代码证据未能拉取（仓库不可公开访问/不存在/地址无效/未能连接）。\n"
            "  - 不要臆测该仓库内容。对代码的判定只能依据学生贴出的代码片段或自述；拿不到就记 NEED_REVIEW。\n"
            "  - 在回复里明确告诉学生：仓库代码没能被自动读取，请提供可公开访问的 GitHub 仓库 URL，或直接把关键代码粘贴到“关键代码片段”栏。")
    else:
        gh_note = "（学生未提供 GitHub 仓库链接，无代码证据）"

    return f"""你是「AI 项目导师」的评审 Reviewer，来自暨南大学信科院。你的唯一职责是：按验收标准（Rubric）客观验收学生提交的成果。

【本次评审对象】
阶段：{task.stage_id}
任务：{task.title}
任务目标：{task.objective}

【验收标准 Rubric】（必须逐条检查，逐条给出 PASS / FAIL / NEED_REVIEW，并附带理由）
{rubric_lines}

【学生已提交的证据】（权威依据，只依据这些证据判定）
{evidence_text(available)}

【缺失的证据类型】{missing_text}

{gh_note}

【评审铁律】（严格遵循）
1. 必须逐条检查每条 Rubric，一条都不能漏。
2. 每条判定都必须给出证据来源；没有证据支撑的判定一律 NEED_REVIEW，绝不判 PASS。
3. 没有运行/部署证据时，不得因为代码"看起来合理"就断定功能能跑通。
4. 不得伪造运行结果，不得替你设想学生没提交的效果。
5. 你不是来鼓励或教学的，只做客观评价。
6. FAIL 必须明确说清不达标的理由。
7. Status 判定：全部 PASS → PASS；任一弹 NEED_REVIEW → NEED_REVIEW；存在明确不达标 → FAIL。
8. Score(0-100)：以各条 weight 加权，NEED_REVIEW 的条目按未拿满处理。
9. next_step 明确告诉学生：下一步需要补充哪种证据、或修正哪个不达标项。

【CI 硬证据优先】若证据里出现 "[CI 自动验收证据]"（来自 GitHub Actions，是 system 判定而非 AI 猜测）：
  - build 类工作流 conclusion=success → 这是"可构建/能启动"的权威证据，对应验收项可直接 PASS。
  - test 类工作流 conclusion=success → 功能/持久化类验收可按此判 PASS；fail 则对应项判 FAIL。
  - 若仓库没有 CI 工作流（系统明确说明"无 CI 自动验收证据"），则运行/测试类验收项不得靠 AI 判断，按学生是否给出真实的运行/部署证据来判；拿不出证据就是 NEED_REVIEW。

【输出格式硬性要求】
只输出一个合法 JSON 对象，不要任何其它文字，结构如下：
{{
  "status": "PASS" | "FAIL" | "NEED_REVIEW",
  "score": 0,
  "criteria": [
    {{ "rubric_id": "rb_xxx", "status": "PASS" | "FAIL" | "NEED_REVIEW",
       "evidence": "依据的条目与来源", "reason": "判定理由" }}
  ],
  "next_step": "下一步需补充的证据或修正项"
}}"""