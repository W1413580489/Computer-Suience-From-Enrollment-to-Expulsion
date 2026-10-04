# -*- coding: utf-8 -*-
"""课程 05《红楼梦人物关系探索器》课程数据。

结构：一个课程（course_005）→ 一个项目
  project_red_chamber · 红楼梦人物关系探索器：把文学关系变成一张图（T01–T08，Stage 1–4）

设计依据：AI导师引擎_文科零基础三课程_DeepSeek执行规格 v1.1 §4
技术栈：原生 HTML / CSS / JavaScript + 原生 SVG + JSON + Python 自带 http.server
数据文件：data/characters.json（人物）、data/relations.json（关系，source/target 用稳定 id 关联）
图形约束：只用原生 <svg>/<line>/<circle>/<text>，不引入 D3 / Cytoscape / ECharts / Mermaid / 图数据库

证据路径约定（与 course04 一致）：
  - code_context.likelyFiles 一律写「不含扩展名的 basename」；
  - 所有数据核心 Task 必须显式写 code_context；
  - keywords 必含 "json"，确保 data/*.json 进入候选集。
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
COURSE_005 = {
    "title": "红楼梦人物关系探索器：把文学关系变成一张图",
    "description": "不需要编程基础。使用课程整理的小规模《红楼梦》人物关系数据，在 AI 导师帮助下做出一个可搜索、"
                   "可高亮、可按关系类型筛选的本地关系探索器；最后加入自己的人物关系，完成属于自己的版本。",
    "projects": ["project_red_chamber"],
    "img": "/courses/redchamber.webp",
    "img_pos": "center 30%",
}


def build_project_red_chamber() -> Project:
    # ===================== Stage 1：认识人物关系数据 =====================
    stage1 = Stage(
        id="c5_stage1", title="① 认识人物关系数据", order=1,
        objective="在本地跑通模板，看到人物节点与关系线，并理解「人物」与「关系」是两份互相引用、分开存放的数据",
        tasks=["red05_t01", "red05_t02"],
    )
    stage2 = Stage(
        id="c5_stage2", title="② 让人物关系可探索", order=2,
        objective="给关系图加上人物搜索与点击高亮，让这张图真正可以被查找与阅读",
        tasks=["red05_t03", "red05_t04"],
    )
    stage3 = Stage(
        id="c5_stage3", title="③ 我开始修改这张关系图", order=3,
        objective="在保持结构不变的前提下新增自己的关系数据，并加上关系类型筛选，体会「数据决定图的样子」",
        tasks=["red05_t05", "red05_t06"],
    )
    stage4 = Stage(
        id="c5_stage4", title="④ 做出我的人物关系版本", order=4,
        objective="确定个人研究主题、整理最终作品并完成一次真实复盘，交付可稳定运行的本地人物关系作品",
        tasks=["red05_t07", "red05_t08"],
    )

    # ---- T01 跑起来，我的第一张人物关系图 ----
    task_t01 = Task(
        id="red05_t01", title="跑起来，我的第一张人物关系图", stage_id="c5_stage1", order=1,
        objective="在本地启动课程提供的《红楼梦》人物关系探索器，并看到至少一组人物关系。",
        steps=[
            "下载并解压课程提供的 course_005_red_chamber 模板",
            "在项目文件夹地址栏输入 cmd 并回车（Windows）；Mac/Linux 使用终端进入该目录",
            "运行 python -m http.server 8000",
            "打开浏览器访问 http://127.0.0.1:8000",
            "确认页面存在人物节点和关系线",
            "点击一个人物，确认页面至少能显示人物名称",
            "不修改代码，先完成一次本地运行",
            "将项目复制到自己的 GitHub 仓库并保存仓库地址",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t01_1", "rb_red05_t01_2", "rb_red05_t01_3"],
        skill=SkillKey.env_setup,
        chunk_key="红楼梦人物关系探索器 > T01 本地运行",
        code_context=CodeContext(
            keywords=["json", "characters", "relations", "svg", "app.js", "index.html"],
            likelyFiles=["characters", "relations", "app", "index", "README"],
            searchPatterns=["http.server", "<svg", "circle", "line"],
        ),
        resume_points=[
            ResumePoint(point="用 Python 自带静态服务器在本地跑通一个 SVG 关系图站点",
                        purpose="规避 fetch 读取 JSON 时的本地跨域问题",
                        result="关系图可在本地稳定打开", kind="delivery"),
        ],
    )

    # ---- T02 我发现一张图其实有两份数据 ----
    task_t02 = Task(
        id="red05_t02", title="我发现一张图其实有两份数据", stage_id="c5_stage1", order=2,
        objective="修改 data/characters.json 中一个人物名称，并保持关系图仍然能显示该人物与相关关系。",
        steps=[
            "在项目中找到 data/characters.json",
            "找到一个人物",
            "只修改这个人物显示用的 name",
            "保存文件并刷新浏览器页面",
            "如果人物关系消失，阅读报错并询问 AI 导师",
            "修复数据关联，使人物名称修改后关系仍然存在",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t02_1", "rb_red05_t02_2", "rb_red05_t02_3"],
        skill=SkillKey.ai_assisted,
        chunk_key="红楼梦人物关系探索器 > T02 人物与关系数据",
        code_context=CodeContext(
            keywords=["json", "characters", "relations", "source", "target"],
            likelyFiles=["characters", "relations", "app", "index", "README"],
            searchPatterns=["characters", "relations", "id", "source", "target"],
        ),
    )

    # ---- T03 找到一个人物 ----
    task_t03 = Task(
        id="red05_t03", title="找到一个人物", stage_id="c5_stage2", order=3,
        objective="添加人物搜索功能，输入人物名称后能够定位或高亮对应人物。",
        steps=[
            "确认页面已经有搜索输入框",
            "向 AI 编程工具描述「我想按人物名称搜索并定位 / 高亮人物」",
            "让 AI 修改 app.js，但不要删除原来的数据读取逻辑",
            "运行项目",
            "搜索「贾宝玉」或数据中存在的其他人物",
            "确认对应人物被定位 / 高亮",
            "搜索一个不存在的人物，确认页面仍然正常",
            "保存修改并提交到 GitHub",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t03_1", "rb_red05_t03_2", "rb_red05_t03_3"],
        skill=SkillKey.project_dev,
        chunk_key="红楼梦人物关系探索器 > T03 人物搜索",
        code_context=CodeContext(
            keywords=["json", "characters", "search", "name", "highlight"],
            likelyFiles=["app", "characters", "relations", "index", "README"],
            searchPatterns=["search", "filter", "name", "highlight"],
        ),
    )

    # ---- T04 看看这个人物和谁有关系 ----
    task_t04 = Task(
        id="red05_t04", title="看看这个人物和谁有关系", stage_id="c5_stage2", order=4,
        objective="点击一个人物时，高亮与其直接相关的人物和关系线，并显示至少一种关系说明。",
        steps=[
            "选择一个人物作为测试对象",
            "让 AI 编程工具加入「点击人物高亮关系」的功能",
            "运行项目",
            "点击人物",
            "观察直接关系是否高亮",
            "再点击另一个人物进行验证",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t04_1", "rb_red05_t04_2", "rb_red05_t04_3"],
        skill=SkillKey.ui_design,
        chunk_key="红楼梦人物关系探索器 > T04 关系高亮",
        code_context=CodeContext(
            keywords=["json", "relations", "source", "target", "type", "highlight"],
            likelyFiles=["app", "relations", "characters", "index", "README"],
            searchPatterns=["source", "target", "type", "highlight"],
        ),
    )

    # ---- T05 增加一条属于我的人物关系（核心实验任务）----
    task_t05 = Task(
        id="red05_t05", title="增加一条属于我的人物关系", stage_id="c5_stage3", order=5,
        objective="在不破坏已有数据结构的情况下，增加至少 5 条新的有效人物关系，并让图上出现相应连接。",
        steps=[
            "保留一份课程原始 relations.json 备份",
            "打开 data/relations.json",
            "选择已有两个人物",
            "按课程规定的格式新增一条关系",
            "用相同方式再增加，总数达到至少 5 条",
            "运行项目",
            "随机点击新增关系涉及的人物",
            "确认新增关系可以被高亮",
            "保存并提交 GitHub",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t05_1", "rb_red05_t05_2", "rb_red05_t05_3"],
        skill=SkillKey.ai_assisted,
        chunk_key="红楼梦人物关系探索器 > T05 新增关系",
        code_context=CodeContext(
            keywords=["json", "characters", "relations", "source", "target", "relation"],
            likelyFiles=["relations", "characters", "app", "index", "README"],
            searchPatterns=["relations", "source", "target", "type", "label"],
        ),
        resume_points=[
            ResumePoint(point="在不改动核心渲染逻辑的前提下新增至少 5 条有效人物关系数据",
                        purpose="验证「稳定的 id 关联」让数据结构可扩展",
                        result="关系图出现学生自己新增的连接", kind="delivery"),
        ],
    )

    # ---- T06 让关系变得可以筛选 ----
    task_t06 = Task(
        id="red05_t06", title="让关系变得可以筛选", stage_id="c5_stage3", order=6,
        objective="增加关系类型筛选，使学生可以只查看某一种关系，例如 family 或 love。",
        steps=[
            "确认 relations.json 中存在不同 relation type",
            "选择最容易理解的两种类型",
            "让 AI 编程工具加入筛选器",
            "运行项目",
            "选择第一种关系类型",
            "确认图中只展示对应关系",
            "切换第二种类型再次验证",
            "不允许把筛选选项写死为数据中不存在的类型",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t06_1", "rb_red05_t06_2", "rb_red05_t06_3"],
        skill=SkillKey.workflow,
        chunk_key="红楼梦人物关系探索器 > T06 关系类型筛选",
        code_context=CodeContext(
            keywords=["json", "relations", "type", "filter", "family", "love"],
            likelyFiles=["app", "relations", "characters", "index", "README"],
            searchPatterns=["type", "filter", "family", "love"],
        ),
        resume_points=[
            ResumePoint(point="新增基于数据中真实 type 值的关系类型筛选器（如 family / love）",
                        purpose="让关系图可按语义维度查看",
                        result="切换类型时图中关系随之变化", kind="engineering"),
        ],
    )

    # ---- T07 选择我想研究的人物群体 ----
    task_t07 = Task(
        id="red05_t07", title="选择我想研究的人物群体", stage_id="c5_stage4", order=7,
        objective="根据自己的兴趣，选择一个人物子群体，并修改首页介绍与默认展示对象，让作品具有个人研究主题。",
        steps=[
            "从现有数据中选择一个人物群体",
            "用一句话写出自己想观察的问题，例如「宝玉与贾府核心人物的关系」",
            "修改首页标题与说明",
            "设置一个默认人物",
            "运行并确认默认人物正确",
            "再测试搜索和关系高亮没有被破坏",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t07_1", "rb_red05_t07_2", "rb_red05_t07_3"],
        skill=SkillKey.prd,
        chunk_key="红楼梦人物关系探索器 > T07 个人主题",
        code_context=CodeContext(
            keywords=["json", "characters", "title", "theme", "default"],
            likelyFiles=["index", "app", "characters", "relations", "README"],
            searchPatterns=["<title", "<h1", "default"],
        ),
    )

    # ---- T08 完成我的红楼梦人物关系探索器 ----
    task_t08 = Task(
        id="red05_t08", title="完成我的红楼梦人物关系探索器", stage_id="c5_stage4", order=8,
        objective="整理最终版本，确保人物搜索、关系高亮、关系筛选、个人数据修改均可正常运行，并通过最终验收。",
        steps=[
            "再次运行 python -m http.server 8000",
            "测试人物搜索",
            "测试点击人物和关系高亮",
            "测试关系类型筛选",
            "检查自己新增的数据仍在",
            "更新 README：写清楚作品名称、主题、运行方法",
            "更新 DATA_SOURCE.md：写清楚数据来源与整理方式",
            "提交 GitHub 并完成最终验收",
        ],
        evidence_required="code",
        rubric_ids=["rb_red05_t08_1", "rb_red05_t08_2", "rb_red05_t08_3", "rb_red05_t08_4"],
        skill=SkillKey.git,
        chunk_key="红楼梦人物关系探索器 > T08 最终交付",
        code_context=CodeContext(
            keywords=["json", "characters", "relations", "readme", "data_source"],
            likelyFiles=["characters", "relations", "README", "data_source"],
            searchPatterns=["http.server", "relations", "<svg"],
        ),
        resume_points=[
            ResumePoint(point="交付含 README 与数据来源说明（DATA_SOURCE.md）的完整本地关系图作品",
                        purpose="让他人可复现、让数据来源可追溯",
                        result="作品具备可交付与可复现性", kind="delivery"),
        ],
    )

    rubrics = [
        # T01
        Rubric(id="rb_red05_t01_1", task_id="red05_t01", criterion="人物关系项目文件完整",
               description="仓库中存在模板规定的核心文件，没有丢失或改名",
               required_evidence=["code"],
               pass_condition="存在 index.html、app.js、data/characters.json、data/relations.json", weight=2),
        Rubric(id="rb_red05_t01_2", task_id="red05_t01", criterion="本地能显示人物关系",
               description="学生提供本地启动方式，运行后可看到人物节点与关系线",
               required_evidence=["code", "runtime"],
               pass_condition="本地运行后可看到人物节点，并存在连接节点的关系线", weight=2),
        Rubric(id="rb_red05_t01_3", evaluation_role="theory", task_id="red05_t01", criterion="能描述自己看到的作品结构",
               description="用自己的话说明画面元素与数据的对应关系",
               required_evidence=["description"],
               pass_condition="能指出「人物」和「关系线」分别代表什么", weight=1),
        # T02
        Rubric(id="rb_red05_t02_1", task_id="red05_t02", criterion="人物数据文件被真正读取",
               description="代码从 characters.json 加载人物信息并展示到页面",
               required_evidence=["code", "runtime"],
               pass_condition="app.js 从 characters.json 加载人物信息并展示", weight=2),
        Rubric(id="rb_red05_t02_2", task_id="red05_t02", criterion="人物与关系通过稳定 ID 关联",
               description="关系记录用 id 引用人物，改显示名不会断关系",
               required_evidence=["code"],
               pass_condition="relations.json 的 source/target 能对应 characters.json 中现有 ID，修改显示名称不会破坏关系", weight=2),
        Rubric(id="rb_red05_t02_3", evaluation_role="theory", task_id="red05_t02", criterion="能说明人物和关系为什么要分开",
               description="用自己的话说明两类信息的不同",
               required_evidence=["description"],
               pass_condition="能用自己的话说明「人物是谁」和「谁与谁有关系」是两种不同的信息", weight=1),
        # T03
        Rubric(id="rb_red05_t03_1", task_id="red05_t03", criterion="人物搜索可用",
               description="代码存在按名称搜索人物的逻辑，运行时能定位 / 高亮",
               required_evidence=["code", "runtime"],
               pass_condition="输入现有人物名称后，页面能定位或高亮对应人物", weight=2),
        Rubric(id="rb_red05_t03_2", task_id="red05_t03", criterion="无结果情况可处理",
               description="输入不存在的人物名时页面不崩溃",
               required_evidence=["runtime"],
               pass_condition="输入不存在的人物名称时页面无崩溃", weight=1),
        Rubric(id="rb_red05_t03_3", evaluation_role="theory", task_id="red05_t03", criterion="能说出搜索验证方法",
               description="写出实际测试名称及看到的结果",
               required_evidence=["description"],
               pass_condition="给出一个实际测试名称及结果", weight=1),
        # T04
        Rubric(id="rb_red05_t04_1", task_id="red05_t04", criterion="点击人物会触发关系高亮",
               description="代码存在点击人物后更新高亮状态的逻辑，实际点击可见高亮",
               required_evidence=["code", "runtime"],
               pass_condition="点击人物后，其相关关系线或邻接人物出现明确高亮状态", weight=2),
        Rubric(id="rb_red05_t04_2", task_id="red05_t04", criterion="高亮关系与数据一致",
               description="高亮内容能在 relations.json 中找到对应关系",
               required_evidence=["code", "runtime"],
               pass_condition="高亮内容能在 relations.json 中找到对应关系", weight=2),
        Rubric(id="rb_red05_t04_3", evaluation_role="theory", task_id="red05_t04", criterion="能说明自己如何验证图是否正确",
               description="说明至少一个人物及其一条关系如何核对",
               required_evidence=["description"],
               pass_condition="说明至少一个人物及其一条关系如何核对", weight=1),
        # T05
        Rubric(id="rb_red05_t05_1", task_id="red05_t05", criterion="新增至少 5 条有效关系",
               description="relations.json 中至少有 5 条新增记录，且引用的 ID 真实存在",
               required_evidence=["code"],
               pass_condition="relations.json 中至少有 5 条新增有效记录，source/target 均引用存在的人物 ID", weight=2),
        Rubric(id="rb_red05_t05_2", task_id="red05_t05", criterion="新关系真正出现在图中",
               description="至少两条新增关系可在图中出现并被高亮",
               required_evidence=["code", "runtime"],
               pass_condition="至少验证 2 条新增关系可在图中出现并在点击人物时被高亮", weight=2),
        Rubric(id="rb_red05_t05_3", evaluation_role="theory", task_id="red05_t05", criterion="能说明一条关系为什么这样定义",
               description="对至少一条自定义关系给出真实依据或判断理由",
               required_evidence=["description"],
               pass_condition="对至少一条自定义关系给出真实依据或自己的判断理由", weight=1),
        # T06
        Rubric(id="rb_red05_t06_1", task_id="red05_t06", criterion="支持按关系类型筛选",
               description="代码存在关系类型筛选逻辑，选择类型后图中关系会变化",
               required_evidence=["code", "runtime"],
               pass_condition="页面存在关系类型筛选逻辑，选择类型后图中关系会变化", weight=2),
        Rubric(id="rb_red05_t06_2", task_id="red05_t06", criterion="筛选条件来源于数据",
               description="筛选使用 relations.json 中真实存在的 type 值",
               required_evidence=["code"],
               pass_condition="筛选使用 relations.json 中真实存在的 type 值", weight=2),
        Rubric(id="rb_red05_t06_3", evaluation_role="theory", task_id="red05_t06", criterion="能说出自己观察到的关系结构",
               description="至少写出一种关系类型及其出现情况",
               required_evidence=["description"],
               pass_condition="至少写出一种关系类型及其出现情况", weight=1),
        # T07
        Rubric(id="rb_red05_t07_1", task_id="red05_t07", criterion="作品具备明确主题",
               description="首页标题与说明体现明确的人物研究主题",
               required_evidence=["code", "runtime"],
               pass_condition="首页标题与说明体现明确人物研究主题", weight=2),
        Rubric(id="rb_red05_t07_2", task_id="red05_t07", criterion="默认展示对象与主题一致",
               description="页面启动后默认人物存在且能显示其关系",
               required_evidence=["runtime"],
               pass_condition="页面启动后默认人物存在于数据中并可以正常显示其关系", weight=2),
        Rubric(id="rb_red05_t07_3", evaluation_role="reflection", task_id="red05_t07", criterion="能说明主题选择理由",
               description="说明自己为什么选择这组人物",
               required_evidence=["description"],
               pass_condition="至少说明自己为什么选择这组人物", weight=1),
        # T08
        Rubric(id="rb_red05_t08_1", task_id="red05_t08", criterion="最终项目可运行",
               description="按 README 的本地命令启动后页面正常显示关系图",
               required_evidence=["code", "runtime"],
               pass_condition="本地服务器运行后页面正常显示人物关系图", weight=2),
        Rubric(id="rb_red05_t08_2", task_id="red05_t08", criterion="核心功能齐全",
               description="搜索、关系高亮、关系筛选均验证通过",
               required_evidence=["runtime"],
               pass_condition="搜索、关系高亮、关系筛选至少全部各验证一次", weight=2),
        Rubric(id="rb_red05_t08_3", task_id="red05_t08", criterion="数据具有个人修改",
               description="至少存在 5 条学生新增关系记录",
               required_evidence=["code"],
               pass_condition="至少存在 5 条学生新增关系记录", weight=1),
        Rubric(id="rb_red05_t08_4", evaluation_role="reflection", task_id="red05_t08", criterion="完成一次真实项目复盘",
               description="写出一个遇到的问题、解决方式和验证方式",
               required_evidence=["description"],
               pass_condition="写出一个遇到的问题、解决方式和验证方式", weight=1),
    ]

    return Project(
        id="project_red_chamber",
        title="红楼梦人物关系探索器",
        description="从课程整理的小规模《红楼梦》人物关系数据集出发，用原生 SVG 做出一个可搜索、可高亮、"
                    "可按关系类型筛选的本地关系图；再新增自己的人物关系数据，完成属于自己的版本。",
        stages=[stage1, stage2, stage3, stage4],
        tasks=[task_t01, task_t02, task_t03, task_t04, task_t05, task_t06, task_t07, task_t08],
        rubrics=rubrics,
        resume_intro="使用原生 HTML/CSS/JavaScript 与原生 SVG，基于「人物 + 关系」双 JSON 数据，实现一个本地运行的"
                     "《红楼梦》人物关系探索器：支持人物搜索、点击高亮邻接关系、按关系类型筛选，并新增自选人物关系数据。",
        resume_role="独立开发",
        resume_tech=["HTML", "CSS", "JavaScript", "SVG", "JSON", "Python http.server", "GitHub"],
        resume_metrics=["新增 5 条以上有效人物关系且引用 ID 全部有效",
                        "实现人物搜索 / 关系高亮 / 关系类型筛选三类交互"],
    )