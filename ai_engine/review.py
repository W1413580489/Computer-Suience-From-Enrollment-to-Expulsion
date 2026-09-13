# -*- coding: utf-8 -*-
"""
评审链（Sprint 5）：Submission → Evidence Collector → Rubric → Reviewer → Evaluation。

对齐规格书：
  - Rubric 是"每条验收条件"一个对象，含 requiredEvidence / passCondition / weight
  - Reviewer 遵循 **Evidence First**：没有充分证据 → NEED_REVIEW，绝不凭"看起来合理"判 PASS
  - 独立 POST /api/ai/review 流水线

V2 修改版（输出漂移治理）：
  - LLM 只输出逐条 criteria 判定；score/status 由 compute_evaluation() 在代码层聚合
  - CI 结论（build/test success/fail）在代码层直判对应 Rubric，不经 LLM（ci_direct_verdict）
  - 部署不再是强制交付项：运行证据 = 本地可复现运行说明 / CI 结论 / 自愿部署地址（三选一）
"""
from __future__ import annotations

import hashlib
import json

from code_evidence import detect_run_cmd
from schemas import ReviewCriterion, ReviewEvaluation, ReviewLLMOutput, ReviewRequest, ReviewStatus, Rubric, Submission, Task


# ---------------------------------------------------------------------------
# Evidence Collector
# ---------------------------------------------------------------------------
def collect_evidence(submission: Submission | None, repo_code_text: str = "",
                     visual=None) -> dict[str, str]:
    """把 submission 各字段跟仓库代码证据归一成"可用证据"清单。

    返回 { 证据类型: 文本 }，证据类型 ∈ code / runtime / test / url / description / visual。
    """
    ev: dict[str, str] = {}
    sub = submission or Submission(task_id="")

    if repo_code_text:
        ev["code"] = f"GitHub 代码证据（已拉取结构与关键文件内容）：\n{repo_code_text}"
        # 课程 02+：仓库含 agent_trace.json 时登记 Trace 证据（Agent 执行轨迹）
        if "agent_trace.json" in repo_code_text:
            ev["trace"] = "仓库中包含 agent_trace.json（Agent 执行轨迹），可验证工具调用与多步行为"
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
        # 修改 1：本地可复现运行也算运行证据——自述中出现启动命令（uvicorn/npm run/docker compose…）
        if "runtime" not in ev:
            cmd_line = detect_run_cmd(sub.description)
            if cmd_line:
                ev["runtime"] = f"本地可复现运行说明（学生自述含启动命令）：{cmd_line}"

    # V2.1：视觉证据（只把"观察到的事实"注入，原图不进入任何证据文本）
    if visual is not None and getattr(visual, "status", "") == "ok":
        ev["visual"] = format_visual_evidence(visual)

    return ev


def format_visual_evidence(v) -> str:
    """把视觉分析结果渲染成给 Reviewer 读的事实文本（不含图片内容）。

    带上图片哈希，使证据快照能如实反映"本次分析了哪几张图"（可审计、可复现）。
    """
    lines = ["[视觉证据] 以下事实由视觉模型从学生提交的运行截图中**观察**得到（原图未保存）："]
    for f in (v.facts or []):
        lines.append(f"  - 观察到：{f}")
    for u in (v.uncertain or []):
        lines.append(f"  - 无法确认：{u}")
    if not v.facts and not v.uncertain:
        lines.append("  - （未观察到明确事实）")
    lines.append(f"  - 与任务相关性：{v.task_relation}")
    if v.image_hashes:
        lines.append(f"  - 截图指纹：{', '.join(v.image_hashes)}（共 {v.count} 张）")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# V2 修改 6 · L4：证据快照冻结（幂等缓存的前提："同输入"可被哈希定义）
# ---------------------------------------------------------------------------
def snapshot_evidence(available: dict[str, str], ci_workflows: list[dict] | None = None,
                      task_id: str = "") -> str:
    """把评审输入冻结为快照并返回 sha256 短 hash。

    快照覆盖：全部可用证据文本 + CI 工作流结论 + 任务 id。
    同一快照 hash → 评审必然命中幂等缓存（L5），保证"同输入同输出"。
    """
    canonical = json.dumps({
        "task_id": task_id,
        "evidence": dict(sorted(available.items())),
        "ci": sorted(
            (wf.get("name", ""), wf.get("dimension", ""), str(wf.get("conclusion")))
            for wf in (ci_workflows or [])
        ),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def evidence_text(available: dict[str, str]) -> str:
    if not available:
        return "（学生本次未提交任何证据）"
    lines = []
    label = {
        "code": "代码证据", "runtime": "运行证据", "test": "测试证据",
        "deployment": "部署地址", "url": "仓库链接",
        "description": "学生自述", "visual": "视觉证据（运行截图观察结果）",
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

    # 修改 1：部署降级——deployment 不再是硬性必交项（自愿提供时仅作加分证据）
    # V2.1：visual 同理——视觉证据永远是可选增强，绝不作为硬门槛（防止课程作者误写入 required_evidence）
    optional_bonus = {"deployment", "visual"}

    for r in rubrics:
        needed = set(r.required_evidence) - optional_bonus
        if not needed:
            # 无证据要求的 Rubric 交给 LLM
            passable.append(r)
            continue
        missing = needed - present
        # description 不算硬证据
        missing_real = {m for m in missing if m != "description"}
        if missing_real:
            reason = f"缺少必要证据类型：{', '.join(sorted(missing_real))}，无法自动判定"
            # V2.1：该标准有视觉观察点时，说明"截图只是辅助、不能替代运行证据"，避免学生困惑
            if getattr(r, "visual_check", "none") == "supported" and "runtime" in missing_real:
                reason += "（运行截图仅作辅助证据，不能替代运行证据：请补充启动命令说明 / CI 结论 / 部署地址）"
            forced.append({
                "rubric_id": r.id,
                "missing": sorted(missing_real),
                "reason": reason,
            })
        else:
            passable.append(r)

    return {
        "all_passable": len(forced) == 0,
        "forced_needs_review": forced,
        "passable_rubrics": passable,
    }


# ---------------------------------------------------------------------------
# V2 修改 6：score/status 规则化（L1/L2）+ CI 直判（L3）
# ---------------------------------------------------------------------------
def compute_evaluation(criteria: list[ReviewCriterion],
                       rubrics: list[Rubric],
                       next_step: str = "") -> ReviewEvaluation:
    """由逐条 criteria 聚合出 score/status（代码层确定性计算，同证据 → 同分）。

    规则：
      - score = sum(通过条目 weight) / sum(全部 weight) × 100，四舍五入取整
      - status：有 FAIL → FAIL；否则有 NEED_REVIEW → NEED_REVIEW；全 PASS → PASS
    """
    weight_of = {r.id: max(int(r.weight), 0) for r in rubrics}
    total = 0
    passed = 0
    has_fail = False
    has_need_review = False
    for c in criteria:
        w = weight_of.get(c.rubric_id, 1)
        total += w
        if c.status == ReviewStatus.PASS:
            passed += w
        elif c.status == ReviewStatus.FAIL:
            has_fail = True
        else:
            has_need_review = True
    score = round(passed / total * 100) if total > 0 else 0
    if has_fail:
        status = ReviewStatus.FAIL
    elif has_need_review:
        status = ReviewStatus.NEED_REVIEW
    else:
        status = ReviewStatus.PASS
    return ReviewEvaluation(status=status, score=score, criteria=criteria, next_step=next_step)


# CI 维度 → 可直判的 requiredEvidence 类型（与 code_evidence._CI_DIMENSION 对应）
# 注意：code / description 是语义判定（如"Key 未暴露前端"），CI 结论证明不了，必须留给 LLM
_CI_DIM_TO_EVIDENCE = {
    "build": {"build"},
    "test": {"test"},
    "runtime": {"runtime"},
}


def ci_direct_verdict(rubric: Rubric, ci_workflows: list[dict]) -> dict | None:
    """CI 结论直判（L3）：system 判定的 CI 结论在代码层映射该 Rubric 的 PASS/FAIL，不经 LLM。

    规则（保守，只直判有把握的）：
      - 所需证据含语义判定类型（description / code）→ 不直判，交给 LLM
      - Rubric 所需证据类型全部落在某个 CI 维度覆盖范围内，且该维度工作流有结论：
          conclusion=success → PASS（权威证据）
          conclusion=failure → FAIL（权威证据）
          conclusion=其它（startup_failure/neutral/cancelled/timed_out…）→ 返回 None，交给 LLM/NEED_REVIEW
    返回 {"status": ReviewStatus, "evidence": str} 或 None。
    """
    needed = set(rubric.required_evidence) - {"deployment"}  # deployment 已降级为可选加分项
    if not needed or ({"description", "code"} & needed):
        return None  # 含语义判定类型 → CI 结论不足以直判

    # 找到每个所需证据类型对应的 CI 维度工作流结论
    wf_by_dim: dict[str, list[dict]] = {}
    for wf in ci_workflows or []:
        dim = wf.get("dimension", "unknown")
        wf_by_dim.setdefault(dim, []).append(wf)

    matched: list[tuple[str, str, str]] = []  # (etype, workflow_name, conclusion)
    for etype in needed:
        found = None
        for dim, etypes in _CI_DIM_TO_EVIDENCE.items():
            if etype in etypes:
                found = dim
                break
        if not found or found not in wf_by_dim:
            return None  # 有证据类型 CI 覆盖不到 → 不直判
        # 取该维度第一个有结论的工作流
        concl = None
        name = ""
        for wf in wf_by_dim[found]:
            if wf.get("conclusion"):
                concl = str(wf["conclusion"]).lower()
                name = wf.get("name", found)
                break
        if not concl:
            return None  # 该维度工作流尚未运行出结论
        matched.append((etype, name, concl))

    # 所需证据类型之间结论一致才直判（如 runtime+test 都要求时，两个维度结论必须同向）
    conclusions = {c for _, _, c in matched}
    if conclusions == {"success"}:
        ev_src = "；".join(f"{n}（{c}）" for _, n, c in matched)
        return {"status": ReviewStatus.PASS,
                "evidence": f"CI 自动验收证据（system 判定）：{ev_src}"}
    if conclusions == {"failure"}:
        ev_src = "；".join(f"{n}（{c}）" for _, n, c in matched)
        return {"status": ReviewStatus.FAIL,
                "evidence": f"CI 自动验收证据（system 判定）：{ev_src}"}
    return None  # 结论混合或非 success/failure → 交给 LLM/预检


# ---------------------------------------------------------------------------
# Reviewer System Prompt
# ---------------------------------------------------------------------------
def build_review_system_prompt(task: Task, rubrics: list[Rubric],
                               available: dict[str, str]) -> str:
    rubric_lines = []
    for i, r in enumerate(rubrics, 1):
        line = (
            f"{i}. [{r.id}] {r.criterion}\n"
            f"   说明：{r.description}\n"
            f"   所需证据：{', '.join(r.required_evidence) or '自述即可'}\n"
            f"   达标条件：{r.pass_condition}（权重 {r.weight}）"
        )
        # V2.1：该标准有可通过截图观察的事实时，告知 Reviewer 观察点（可选增强，非硬门槛）
        if getattr(r, "visual_check", "none") == "supported":
            line += ("\n   视觉观察点（可选增强证据，缺失不扣分）："
                     + (r.visual_pass_condition or "如提供运行截图，应能观察到该运行结果"))
        rubric_lines.append(line)

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
            "  - 注意：代码证据只能证明「写了什么」，不能证明「跑没跑通」。运行类验收以「本地可复现运行说明 / CI 结论 / 部署地址」三选一为准；"
            "三者都没有的项记 NEED_REVIEW，并明确让学生补运行说明或 CI。")
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

【运行证据标准（修改版，三选一即可）】
运行类验收项满足以下任一即为有运行证据：
  ① 本地可复现运行：学生自述/README 写明启动命令与访问效果；
  ② CI 结论：build/test 工作流 success（系统已在证据中标注，属权威判定）；
  ③ 在线部署地址（自愿提供）。
不再要求域名、HTTPS、进程守护；部署地址只是加分证据，缺失不扣分、不卡验收。

【评审铁律】（严格遵循）
1. 必须逐条检查每条 Rubric，一条都不能漏。
2. 每条判定都必须给出证据来源；没有证据支撑的判定一律 NEED_REVIEW，绝不判 PASS。
3. 三选一的运行证据都没有时，不得因为代码"看起来合理"就断定功能能跑通。
4. 不得伪造运行结果，不得替你设想学生没提交的效果。
5. 你不是来鼓励或教学的，只做客观评价。
6. FAIL 必须明确说清不达标的理由。
7. next_step 明确告诉学生：下一步需要补充哪种证据、或修正哪个不达标项。

【视觉证据的边界（V2.1，严格遵循）】若证据里出现 "[视觉证据]"（视觉模型从学生运行截图中观察到的事实）：
  - 视觉证据只能证明"截图中出现了某个可观察结果"，**不能**证明代码结构正确、也不能替代运行/CI 证据；
  - 视觉证据**不评价界面美观、配色、设计质量、响应式效果**——这类内容一律不参与判定；
  - 若代码证据显示没有对应功能，而截图显示了该结果 → 视为证据冲突，判 NEED_REVIEW 并在理由中说明冲突；
  - 若某条标准的 Visual 观察点在截图中得不到支持，按该标准原有证据判定，**不得仅因"缺少截图"判 FAIL 或 NEED_REVIEW**；
  - 视觉证据未提供时（模型不支持视觉 / 学生未上传），完全按原有证据链判定，不受任何影响。

【CI 硬证据优先】若证据里出现 "[CI 自动验收证据]"（来自 GitHub Actions，是 system 判定而非 AI 猜测）：
  - build 类工作流 conclusion=success → 这是"可构建/能启动"的权威证据，对应验收项可直接 PASS。
  - test 类工作流 conclusion=success → 功能/持久化类验收可按此判 PASS；fail 则对应项判 FAIL。
  - 若仓库没有 CI 工作流（系统明确说明"无 CI 自动验收证据"），则运行/测试类验收项不得靠 AI 判断，按学生是否给出三选一的运行证据来判；拿不出证据就是 NEED_REVIEW。

【输出格式硬性要求】
只输出一个合法 JSON 对象，不要任何其它文字。注意：不要输出总分 status/score（系统会根据你
的逐条判定在代码层计算），你只负责逐条 criteria 与 next_step，结构如下：
{{
  "criteria": [
    {{ "rubric_id": "rb_xxx", "status": "PASS" | "FAIL" | "NEED_REVIEW",
       "evidence": "依据的条目与来源", "reason": "判定理由" }}
  ],
  "next_step": "下一步需补充的证据或修正项"
}}"""