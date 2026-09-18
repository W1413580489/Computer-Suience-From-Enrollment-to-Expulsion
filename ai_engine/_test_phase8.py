# -*- coding: utf-8 -*-
"""
阶段 8 验收测试：课程 03 课程数据完整性。

覆盖：
  T8.1 课程与项目结构（course_003 = 两个项目）
  T8.2 任务 / Rubric 数量与 id 唯一性
  T8.3 任务 ↔ Rubric ↔ Stage 的引用一致性（rubric_ids / stage_id / tasks 列表 / order）
  T8.4 字段合法性（skill / evidence_required / required_evidence）
  T8.5 简历素材（技术栈必须是纯技术名词、亮点必须含目的与结果）
  T8.6 面试自检题字段
  T8.7 课程 03 确实用到 report / issue 两种新证据类型
  T8.8 课程 01/02 未受影响（回归）

运行：python _test_phase8.py
"""
import course_data as cd
from schemas import SkillKey

PASS = 0
FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = ""):
    global PASS
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAILS.append(name)
        print(f"  ✕ {name}  {detail}")


VALID_EVIDENCE_REQ = {"code", "code+test", "test", "url", "screenshot", "none"}
VALID_RUBRIC_EVIDENCE = {"code", "runtime", "test", "ci", "report", "issue",
                         "visual", "description", "url", "deployment", "trace"}
FORBIDDEN_TECH_WORDS = ("AI 协作", "工作流编排", "工程化能力", "全栈项目开发", "学习能力")

print("== T8.1 课程与项目结构 ==")
courses = {c["course_id"]: c for c in cd.list_courses()}
check("course_003 已注册", "course_003" in courses, str(list(courses)))
c3 = courses.get("course_003", {})
check("课程 03 挂了两个项目", len(c3.get("projects", [])) == 2,
      str([p.get("project_id") for p in c3.get("projects", [])]))
check("课程 03 有封面图", c3.get("img") == "/courses/mcp.jpg", str(c3.get("img")))
check("课程 01/02 仍在（回归）", "course_001" in courses and "course_002" in courses)

build = cd.get_project("project_mcp_build")
testp = cd.get_project("project_mcp_test")
check("项目一可加载", build is not None)
check("项目二可加载", testp is not None)

print("== T8.2 任务 / Rubric 数量与 id 唯一性 ==")
check("项目一 7 个任务", len(build.tasks) == 7, str(len(build.tasks)))
check("项目二 5 个任务", len(testp.tasks) == 5, str(len(testp.tasks)))
check("项目一 2 个阶段", len(build.stages) == 2, str(len(build.stages)))
check("项目二 3 个阶段", len(testp.stages) == 3, str(len(testp.stages)))
check("Rubric 合计 32 条", len(build.rubrics) + len(testp.rubrics) == 32,
      f"{len(build.rubrics)}+{len(testp.rubrics)}")

all_tasks = list(build.tasks) + list(testp.tasks)
all_rubrics = list(build.rubrics) + list(testp.rubrics)
check("任务 id 全局唯一", len({t.id for t in all_tasks}) == len(all_tasks))
check("Rubric id 全局唯一", len({r.id for r in all_rubrics}) == len(all_rubrics))

print("== T8.3 引用一致性 ==")
for t in all_tasks:
    got = cd.get_rubrics(t.id)
    ok = len(got) == len(t.rubric_ids) and got and all(r.task_id == t.id for r in got)
    check(f"{t.id} 的 rubric_ids 能查到且归属正确", bool(ok),
          f"声明 {len(t.rubric_ids)} / 查到 {len(got)}")
for p in (build, testp):
    valid_stages = {s.id for s in p.stages}
    check(f"{p.id} 任务的 stage_id 都有效", all(t.stage_id in valid_stages for t in p.tasks),
          str({t.stage_id for t in p.tasks} - valid_stages))
    for s in p.stages:
        actual = [t.id for t in sorted((t for t in p.tasks if t.stage_id == s.id),
                                       key=lambda x: x.order)]
        check(f"{s.id} 的 tasks 列表与实际一致", list(s.tasks) == actual,
              f"{list(s.tasks)} vs {actual}")
        orders = [t.order for t in p.tasks if t.stage_id == s.id]
        check(f"{s.id} 的 order 无重复", len(orders) == len(set(orders)), str(orders))

print("== T8.4 字段合法性 ==")
check("skill 都是合法枚举",
      all(t.skill is None or isinstance(t.skill, SkillKey) for t in all_tasks),
      str([t.id for t in all_tasks if t.skill is not None and not isinstance(t.skill, SkillKey)]))
check("evidence_required 取值合法",
      all(t.evidence_required in VALID_EVIDENCE_REQ for t in all_tasks),
      str([(t.id, t.evidence_required) for t in all_tasks if t.evidence_required not in VALID_EVIDENCE_REQ]))
check("每个任务都有 objective",
      all(t.objective.strip() for t in all_tasks))
check("每个任务都有 2~4 个步骤",
      all(2 <= len(t.steps) <= 4 for t in all_tasks),
      str([(t.id, len(t.steps)) for t in all_tasks if not 2 <= len(t.steps) <= 4]))
bad_ev = [(r.id, e) for r in all_rubrics for e in r.required_evidence if e not in VALID_RUBRIC_EVIDENCE]
check("Rubric 的 required_evidence 取值合法", not bad_ev, str(bad_ev))
check("每条 Rubric 都有 criterion / pass_condition 与 weight≥1",
      all(r.criterion.strip() and r.pass_condition.strip() and r.weight >= 1 for r in all_rubrics),
      str([r.id for r in all_rubrics if not (r.criterion.strip() and r.pass_condition.strip() and r.weight >= 1)]))

print("== T8.5 简历素材 ==")
for p in (build, testp):
    check(f"{p.id} 有简历简介", bool(p.resume_intro.strip()))
    check(f"{p.id} 技术栈 ≥5 项且为纯技术名词",
          len(p.resume_tech) >= 5 and not any(w in x for w in FORBIDDEN_TECH_WORDS for x in p.resume_tech),
          str(p.resume_tech))
    pts = [rp for t in p.tasks for rp in t.resume_points]
    check(f"{p.id} 有 ≥3 条简历亮点", len(pts) >= 3, str(len(pts)))
    check(f"{p.id} 亮点都写了目的与结果", all(rp.purpose.strip() and rp.result.strip() for rp in pts),
          str([rp.point for rp in pts if not (rp.purpose.strip() and rp.result.strip())]))
    check(f"{p.id} 亮点分类合法",
          all(rp.kind in ("architecture", "stability", "delivery", "engineering") for rp in pts),
          str({rp.kind for rp in pts}))

print("== T8.6 面试自检题 ==")
iqs = [iq for t in all_tasks for iq in t.interview_questions]
check("有 ≥3 道面试题", len(iqs) >= 3, str(len(iqs)))
check("题目字段齐全（含参考答案锚点与类型）",
      all(iq.id and iq.question and iq.answer_anchor and iq.type in ("explain", "debug", "transfer")
          for iq in iqs))
check("题目 id 唯一", len({iq.id for iq in iqs}) == len(iqs))

print("== T8.7 课程 03 用到了新证据类型 ==")
ers = {e for r in all_rubrics for e in r.required_evidence}
check("用到 report（测试报告）", "report" in ers, str(sorted(ers)))
check("用到 issue（GitHub Issue）", "issue" in ers, str(sorted(ers)))
check("用到 ci（回归由 CI 判定）", "ci" in ers, str(sorted(ers)))

print("== T8.8 课程 01/02 回归 ==")
c1 = cd.get_project("project_chatbot")
c2 = cd.get_project("project_agent")
check("课程 01 仍可加载", c1 is not None and len(c1.tasks) == 5, str(len(c1.tasks) if c1 else None))
check("课程 02 仍可加载", c2 is not None and len(c2.tasks) == 9, str(len(c2.tasks) if c2 else None))
check("课程 01/02 的 rubric 仍可查", bool(cd.get_rubrics("task_review")) and bool(cd.get_rubrics("c2t01")))

print()
print(f"通过 {PASS} 项")
if FAILS:
    print(f"失败 {len(FAILS)} 项：")
    for n in FAILS:
        print(f"  - {n}")
    raise SystemExit(1)
print("全部通过 ✓")
