# -*- coding: utf-8 -*-
"""课程 04《古典文学探索器》课程数据。

结构：一个课程（course_004）→ 一个项目
  project_lit_poem · 古典文学探索器：从开源数据到自己的文学作品（T01–T08，Stage 1–4）

设计依据：AI导师引擎_文科零基础三课程_DeepSeek执行规格 v1.1 §3
技术栈：原生 HTML / CSS / JavaScript + JSON + Python 自带 http.server（仅本地静态服务器）
验收证据：全部走 GitHub 代码 + 本地 runtime（README/自述中的 `python -m http.server 8000`）
          （不要求部署；GitHub 只作代码交付与证据采集）

证据路径约定（v1.1 课程侧最小改动，不改 code_evidence.py 的候选逻辑）：
  - code_context.likelyFiles 一律写「不含扩展名的 basename」（现有引擎的真实语义）；
  - 所有数据核心 Task 必须显式写 code_context，否则会掉进默认精选逻辑而漏掉 data/*.json；
  - keywords 必含 "json"，作为数据文件进入候选集的第二重保险。
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
    "title": "古典文学探索器：从开源数据到自己的文学作品",
    "description": "不需要编程基础。使用课程提供的古典文学数据，在 AI 导师帮助下做出一个可以搜索、浏览和统计的"
                   "文学探索器；最后把数据换成你真正感兴趣的文学内容，完成自己的版本。",
    "projects": ["project_lit_poem"],
    "img": "/courses/literary.webp",
    "img_pos": "center 30%",
}


def build_project_lit_poem() -> Project:
    # ===================== Stage 1：先让作品跑起来 =====================
    stage1 = Stage(
        id="c4_stage1", title="① 先让作品跑起来", order=1,
        objective="用 Python 自带的静态服务器在本地启动模板，看到第一版作品列表，并理解「网页内容」和「文学数据」是两样东西",
        tasks=["lit04_t01", "lit04_t02"],
    )
    stage2 = Stage(
        id="c4_stage2", title="② 让作品会查、会看", order=2,
        objective="给探索器加上搜索与作品详情，让数据真正可以被查找与阅读",
        tasks=["lit04_t03", "lit04_t04"],
    )
    stage3 = Stage(
        id="c4_stage3", title="③ 把别人的数据换成我的数据", order=3,
        objective="在不破坏原有功能的前提下替换数据、增加统计，体会「程序没换，换的是数据」",
        tasks=["lit04_t05", "lit04_t06"],
    )
    stage4 = Stage(
        id="c4_stage4", title="④ 做成「我的版本」", order=4,
        objective="确定个人主题、整理最终作品并完成一次真实复盘，交付可稳定运行的本地数字作品",
        tasks=["lit04_t07", "lit04_t08"],
    )

    # ---- T01 打开我的第一个文学作品 ----
    task_t01 = Task(
        id="lit04_t01", title="打开我的第一个文学作品", stage_id="c4_stage1", order=1,
        objective="在自己的电脑上启动课程提供的古典文学探索器，并在浏览器中看到第一版文学作品列表。",
        steps=[
            "下载并解压课程提供的 course_004_literary_explorer 模板",
            "打开项目文件夹",
            "在项目文件夹地址栏输入 cmd 并回车（Windows）；Mac/Linux 使用终端进入该目录",
            "运行 python --version，确认电脑可以使用 Python",
            "运行 python -m http.server 8000",
            "打开浏览器访问 http://127.0.0.1:8000",
            "确认页面出现文学作品列表",
            "不修改代码，先完成一次本地运行",
            "将项目复制到自己的 GitHub 仓库并保存仓库地址",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t01_1", "rb_lit04_t01_2", "rb_lit04_t01_3"],
        skill=SkillKey.env_setup,
        chunk_key="古典文学探索器 > T01 本地运行",
        code_context=CodeContext(
            keywords=["json", "poems", "python", "http.server", "index.html", "app.js"],
            likelyFiles=["index", "app", "README", "poems"],
            searchPatterns=["http.server", "<title", "script src"],
        ),
        resume_points=[
            ResumePoint(point="用 Python 自带静态服务器在本地跑通一个数据驱动的静态站点",
                        purpose="规避 fetch 读取 JSON 时的本地跨域问题",
                        result="作品可在本地稳定打开", kind="delivery"),
        ],
    )

    # ---- T02 我发现作品内容藏在哪里 ----
    task_t02 = Task(
        id="lit04_t02", title="我发现作品内容藏在哪里", stage_id="c4_stage1", order=2,
        objective="找到并修改 data/poems.json 中的一条作品信息，使网页中的对应作品内容发生变化，同时保持页面仍能正常显示。",
        steps=[
            "在项目中找到 data/poems.json",
            "找到第一条作品",
            "只修改这条作品的 title",
            "保存文件",
            "刷新浏览器页面",
            "确认修改后的标题出现在页面中",
            "如果页面报错，把完整报错交给 AI 导师处理，不直接复制一个新项目覆盖原项目",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t02_1", "rb_lit04_t02_2", "rb_lit04_t02_3"],
        skill=SkillKey.ai_assisted,
        chunk_key="古典文学探索器 > T02 认识文学数据",
        code_context=CodeContext(
            keywords=["json", "poems", "title", "author", "content"],
            likelyFiles=["poems", "app", "index", "README"],
            searchPatterns=["poems", "title", "author", "content"],
        ),
    )

    # ---- T03 搜索我想看的作品 ----
    task_t03 = Task(
        id="lit04_t03", title="搜索我想看的作品", stage_id="c4_stage2", order=3,
        objective="为文学探索器加入关键词搜索，使学生可以按标题或作者找到对应作品。",
        steps=[
            "确认页面已经有搜索输入框",
            "向 AI 编程工具描述「我想按标题或作者搜索作品」",
            "让 AI 修改 app.js，但不要删除原来的数据读取逻辑",
            "运行项目",
            "输入一个课程数据中存在的作者名称",
            "确认列表缩小到相关作品",
            "输入一个不存在的作者名称",
            "确认页面能够正常显示「没有找到相关作品」之类的结果",
            "保存修改并提交到 GitHub",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t03_1", "rb_lit04_t03_2", "rb_lit04_t03_3"],
        skill=SkillKey.project_dev,
        chunk_key="古典文学探索器 > T03 搜索作品",
        code_context=CodeContext(
            keywords=["json", "poems", "fetch", "search", "filter", "title", "author"],
            likelyFiles=["app", "index", "poems", "README"],
            searchPatterns=["fetch\\(", "filter\\(", "title", "author"],
        ),
    )

    # ---- T04 点开一首作品，认真看看它 ----
    task_t04 = Task(
        id="lit04_t04", title="点开一首作品，认真看看它", stage_id="c4_stage2", order=4,
        objective="点击作品后，在详情区域显示标题、作者、朝代、正文和标签，让作品具备基本的阅读体验。",
        steps=[
            "选择一首已有作品作为详情展示目标",
            "让 AI 编程工具加入「点击作品显示详情」的功能",
            "详情必须显示标题、作者、朝代和正文",
            "如果作品存在 tags，也显示标签",
            "运行项目",
            "点击至少两首不同作品确认详情会变化",
            "提交 GitHub",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t04_1", "rb_lit04_t04_2", "rb_lit04_t04_3"],
        skill=SkillKey.ui_design,
        chunk_key="古典文学探索器 > T04 作品详情",
        code_context=CodeContext(
            keywords=["json", "poems", "title", "author", "dynasty", "content", "tags"],
            likelyFiles=["app", "index", "poems", "README"],
            searchPatterns=["title", "author", "dynasty", "content"],
        ),
    )

    # ---- T05 换成我真正想看的文学作品（核心实验任务）----
    task_t05 = Task(
        id="lit04_t05", title="换成我真正想看的文学作品", stage_id="c4_stage3", order=5,
        objective="在不破坏现有页面功能的情况下，将课程提供的示例文学数据替换成自己选择的一组至少 20 条作品，"
                  "并让原有搜索与详情功能继续工作。",
        steps=[
            "保留一份课程原始 poems.json 备份",
            "选择自己喜欢的文学主题",
            "准备至少 20 条作品",
            "将每条作品整理成课程规定的 JSON 字段结构",
            "替换 data/poems.json",
            "不修改 app.js 的核心读取逻辑，先运行项目",
            "测试搜索一个作者",
            "点击至少一首新加入的作品查看详情",
            "保存并提交 GitHub",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t05_1", "rb_lit04_t05_2", "rb_lit04_t05_3"],
        skill=SkillKey.ai_assisted,
        chunk_key="古典文学探索器 > T05 替换数据",
        code_context=CodeContext(
            keywords=["json", "poems", "title", "author", "content", "dynasty"],
            likelyFiles=["poems", "app", "index", "README"],
            searchPatterns=["poems", "title", "author", "content"],
        ),
        resume_points=[
            ResumePoint(point="将课程示例数据替换为自选的 20 条以上文学作品数据，且不改动核心 JS 读取逻辑",
                        purpose="验证「数据与展示分离」的工程结构",
                        result="作品从课程模板变为具有个人主题的版本", kind="delivery"),
        ],
    )

    # ---- T06 让我自己的数据也能被「看懂」----
    task_t06 = Task(
        id="lit04_t06", title="让我自己的数据也能被「看懂」", stage_id="c4_stage3", order=6,
        objective="在自己的数据基础上增加一个简单统计区域，例如作品总数、作者数量、朝代分布或标签数量，"
                  "使作品不仅能浏览，还能从数据中得到一个可见结论。",
        steps=[
            "选一个最容易理解的统计目标",
            "先用自然语言告诉 AI 编程工具「我想统计什么」",
            "让 AI 修改 app.js",
            "运行项目",
            "增加或删除一条数据，再刷新页面",
            "确认统计数字会随着数据变化",
            "不允许把统计数字直接写死在 HTML 中",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t06_1", "rb_lit04_t06_2", "rb_lit04_t06_3"],
        skill=SkillKey.workflow,
        chunk_key="古典文学探索器 > T06 文学数据统计",
        code_context=CodeContext(
            keywords=["json", "poems", "count", "length", "stats", "author", "dynasty"],
            likelyFiles=["app", "poems", "index", "README"],
            searchPatterns=["length", "count", "reduce", "forEach"],
        ),
        resume_points=[
            ResumePoint(point="新增基于 JSON 数据的动态统计区域（总数 / 作者数 / 朝代分布）",
                        purpose="让浏览升级为可从数据得到的结论",
                        result="数据变化能实时反映到统计数字", kind="engineering"),
        ],
    )

    # ---- T07 决定这是谁的文学探索器 ----
    task_t07 = Task(
        id="lit04_t07", title="决定这是谁的文学探索器", stage_id="c4_stage4", order=7,
        objective="根据自己的文学主题，修改作品标题、介绍语和内容组织方式，让它从「课程模板」变成一个有明确主题的个人版本。",
        steps=[
            "写一句话说明自己的文学主题",
            "确定探索器的新名称",
            "修改首页标题",
            "修改一句介绍语",
            "选择一个最重要的搜索 / 筛选方式作为首页主要入口",
            "运行并检查页面",
            "确保没有因为改标题而破坏原有功能",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t07_1", "rb_lit04_t07_2", "rb_lit04_t07_3"],
        skill=SkillKey.prd,
        chunk_key="古典文学探索器 > T07 个人化设计",
        code_context=CodeContext(
            keywords=["json", "poems", "title", "theme"],
            likelyFiles=["index", "app", "poems", "README"],
            searchPatterns=["<title", "<h1", "theme"],
        ),
    )

    # ---- T08 完成我的古典文学探索器 ----
    task_t08 = Task(
        id="lit04_t08", title="完成我的古典文学探索器", stage_id="c4_stage4", order=8,
        objective="将个人文学主题、自己的数据、搜索、详情和统计功能整理为一个可以稳定运行的本地数字作品，并通过最终验收。",
        steps=[
            "再次运行 python -m http.server 8000",
            "测试首页是否打开",
            "测试搜索",
            "测试作品详情",
            "测试统计",
            "随机修改一条数据并刷新，确认程序仍能运行",
            "将最终版本提交 GitHub",
            "更新 README：写清楚作品名称、主题、运行方法和数据来源",
            "提交最终验收",
        ],
        evidence_required="code",
        rubric_ids=["rb_lit04_t08_1", "rb_lit04_t08_2", "rb_lit04_t08_3", "rb_lit04_t08_4"],
        skill=SkillKey.git,
        chunk_key="古典文学探索器 > T08 最终交付",
        code_context=CodeContext(
            keywords=["json", "poems", "readme", "data_source", "http.server"],
            likelyFiles=["poems", "index", "app", "README", "data_source"],
            searchPatterns=["http.server", "<title", "poems"],
        ),
        resume_points=[
            ResumePoint(point="交付含 README 与数据来源说明（DATA_SOURCE.md）的完整本地作品",
                        purpose="让他人可复现、让数据来源可追溯",
                        result="作品具备可交付与可复现性", kind="delivery"),
        ],
    )

    rubrics = [
        # T01
        Rubric(id="rb_lit04_t01_1", task_id="lit04_t01", criterion="模板项目文件完整",
               description="仓库中存在模板规定的四项核心文件，没有丢失或改名",
               required_evidence=["code"],
               pass_condition="仓库中存在 index.html、style.css、app.js、data/poems.json 四项核心文件", weight=2),
        Rubric(id="rb_lit04_t01_2", task_id="lit04_t01", criterion="文学探索器能够在本地运行",
               description="学生提供本地启动方式，并说明运行结果",
               required_evidence=["code", "runtime"],
               pass_condition="学生提供 python -m http.server 8000 运行方式，且运行结果说明页面能打开并出现作品列表", weight=2),
        Rubric(id="rb_lit04_t01_3", evaluation_role="theory", task_id="lit04_t01", criterion="能说明自己实际完成了什么",
               description="用自己的话说明本次实际做了什么，不要求专业术语",
               required_evidence=["description"],
               pass_condition="自述至少说明「我启动了本地服务，并看到了课程提供的文学数据」", weight=1),
        # T02
        Rubric(id="rb_lit04_t02_1", task_id="lit04_t02", criterion="页面读取 JSON 数据",
               description="代码里存在加载 data/poems.json 并把内容显示到页面的逻辑，运行后能看到数据",
               required_evidence=["code", "runtime"],
               pass_condition="app.js 存在加载 data/poems.json 并将其内容显示到页面的逻辑；运行后能看到数据", weight=2),
        Rubric(id="rb_lit04_t02_2", task_id="lit04_t02", criterion="修改 JSON 后页面内容发生变化",
               description="仓库中的 poems.json 与页面展示内容一致，且至少有一项已被学生修改",
               required_evidence=["code", "runtime"],
               pass_condition="仓库中的 poems.json 与页面展示内容一致，且至少有一项已被学生修改", weight=2),
        Rubric(id="rb_lit04_t02_3", evaluation_role="theory", task_id="lit04_t02", criterion="能说明数据与页面代码的关系",
               description="能用自己的话说明改数据文件后页面内容会变化",
               required_evidence=["description"],
               pass_condition="能用自己的话说明「改数据文件后页面内容会变化」，不要求使用专业术语", weight=1),
        # T03
        Rubric(id="rb_lit04_t03_1", task_id="lit04_t03", criterion="支持按标题或作者筛选",
               description="代码中存在针对标题或作者的筛选逻辑，运行时输入已知关键词能缩小结果",
               required_evidence=["code", "runtime"],
               pass_condition="app.js 存在针对标题或作者的筛选逻辑；运行时输入已知关键词能缩小结果", weight=2),
        Rubric(id="rb_lit04_t03_2", task_id="lit04_t03", criterion="无结果时程序仍正常",
               description="输入不存在的关键词后页面不崩溃、不空白",
               required_evidence=["runtime"],
               pass_condition="输入不存在的关键词后页面仍正常显示，没有 JS 报错导致页面空白", weight=1),
        Rubric(id="rb_lit04_t03_3", evaluation_role="theory", task_id="lit04_t03", criterion="能说明自己通过什么方式验证",
               description="写出实际测试关键词及看到的结果",
               required_evidence=["description"],
               pass_condition="自述写出至少一个实际测试关键词及看到的结果", weight=1),
        # T04
        Rubric(id="rb_lit04_t04_1", task_id="lit04_t04", criterion="作品详情功能存在",
               description="代码存在选中作品后更新详情区域的逻辑，实际点击作品可以看到对应内容",
               required_evidence=["code", "runtime"],
               pass_condition="代码存在选中作品后更新详情区域的逻辑，实际点击作品可以看到对应内容", weight=2),
        Rubric(id="rb_lit04_t04_2", task_id="lit04_t04", criterion="详情字段完整",
               description="详情区域至少展示标题、作者、朝代、正文四类信息",
               required_evidence=["runtime"],
               pass_condition="至少显示标题、作者、朝代、正文四类信息", weight=2),
        Rubric(id="rb_lit04_t04_3", evaluation_role="theory", task_id="lit04_t04", criterion="能解释为什么不同作品显示不同内容",
               description="结合刚完成的功能说明点击不同作品会读取对应数据",
               required_evidence=["description"],
               pass_condition="能结合自己刚完成的功能说明「点击不同作品，页面读取对应数据」", weight=1),
        # T05
        Rubric(id="rb_lit04_t05_1", task_id="lit04_t05", criterion="成功替换文学数据",
               description="data/poems.json 中至少有 20 条记录，且内容明显不是原始课程示例的简单复制",
               required_evidence=["code"],
               pass_condition="data/poems.json 中至少有 20 条记录，且内容明显不是原始课程示例的简单复制", weight=2),
        Rubric(id="rb_lit04_t05_2", task_id="lit04_t05", criterion="原有程序无需重写即可读取新数据",
               description="页面仍能读取新 JSON，搜索和详情功能至少各成功验证一次",
               required_evidence=["code", "runtime"],
               pass_condition="页面仍能读取新 JSON；搜索和详情功能至少各成功验证一次", weight=2),
        Rubric(id="rb_lit04_t05_3", evaluation_role="theory", task_id="lit04_t05", criterion="能说明自己为什么选择这些数据",
               description="说明自己的文学主题与至少一个数据选择理由",
               required_evidence=["description"],
               pass_condition="自述说明自己的文学主题与至少一个数据选择理由", weight=1),
        # T06
        Rubric(id="rb_lit04_t06_1", task_id="lit04_t06", criterion="统计结果来自数据",
               description="统计代码实际读取 poems.json 计算结果，而不是把一个固定数字写死",
               required_evidence=["code", "runtime"],
               pass_condition="统计代码实际读取 poems.json 计算结果，而不是把一个固定数字写死", weight=2),
        Rubric(id="rb_lit04_t06_2", task_id="lit04_t06", criterion="数据变化会导致统计变化",
               description="学生增加 / 删除至少一条记录后，页面统计数字随之变化",
               required_evidence=["runtime"],
               pass_condition="学生增加 / 删除至少一条记录后，页面统计数字随之变化", weight=2),
        Rubric(id="rb_lit04_t06_3", evaluation_role="theory", task_id="lit04_t06", criterion="能说出自己的统计发现",
               description="至少写出一个从自己数据中观察到的事实",
               required_evidence=["description"],
               pass_condition="至少写出一个从自己数据中观察到的事实", weight=1),
        # T07
        Rubric(id="rb_lit04_t07_1", task_id="lit04_t07", criterion="作品具有明确个人主题",
               description="首页标题与当前数据主题一致，不再是课程默认名称",
               required_evidence=["code", "runtime"],
               pass_condition="首页标题与当前数据主题一致，不再是课程默认名称", weight=2),
        Rubric(id="rb_lit04_t07_2", task_id="lit04_t07", criterion="原有核心功能仍然可用",
               description="搜索、详情、统计至少各成功运行一次",
               required_evidence=["runtime"],
               pass_condition="搜索、详情、统计至少各成功运行一次", weight=2),
        Rubric(id="rb_lit04_t07_3", evaluation_role="reflection", task_id="lit04_t07", criterion="能描述自己的作品定位",
               description="自述包含「我做的是什么 / 给谁看 / 为什么选这个主题」中的至少两项",
               required_evidence=["description"],
               pass_condition="自述包含「我做的是什么 / 给谁看 / 为什么选这个主题」中的至少两项", weight=1),
        # T08
        Rubric(id="rb_lit04_t08_1", task_id="lit04_t08", criterion="最终项目能够运行",
               description="仓库包含完整核心文件，并能按 README 的本地命令启动",
               required_evidence=["code", "runtime"],
               pass_condition="仓库包含完整核心文件，并能按 README 的本地命令启动", weight=2),
        Rubric(id="rb_lit04_t08_2", task_id="lit04_t08", criterion="最终作品包含个人化内容",
               description="数据主题、页面标题或作品筛选逻辑至少有两处明显个人化修改",
               required_evidence=["code", "runtime"],
               pass_condition="数据主题、页面标题或作品筛选逻辑至少有两处明显个人化修改", weight=2),
        Rubric(id="rb_lit04_t08_3", task_id="lit04_t08", criterion="README 与数据来源说明完整",
               description="README 写明本地运行方法；DATA_SOURCE.md 有数据来源说明",
               required_evidence=["code"],
               pass_condition="README 写明本地运行方法；DATA_SOURCE.md 有数据来源说明", weight=1),
        Rubric(id="rb_lit04_t08_4", evaluation_role="reflection", task_id="lit04_t08", criterion="完成项目复盘",
               description="说明一个自己遇到的问题、AI 如何帮助、最终如何验证",
               required_evidence=["description"],
               pass_condition="说明一个自己遇到的问题、AI 如何帮助、最终如何验证", weight=1),
    ]

    return Project(
        id="project_lit_poem",
        title="古典文学探索器",
        description="从课程提供的古典文学小数据集出发，在本地做出一个可搜索、可看详情、可统计的文学探索器；"
                    "再把它替换成自己真正感兴趣的文学内容，完成属于自己的版本。",
        stages=[stage1, stage2, stage3, stage4],
        tasks=[task_t01, task_t02, task_t03, task_t04, task_t05, task_t06, task_t07, task_t08],
        rubrics=rubrics,
        resume_intro="使用原生 HTML/CSS/JavaScript 与 JSON 数据分离的结构，实现一个本地运行的古诗词探索器："
                     "支持按标题/作者搜索、作品详情查看与基础统计，并把示例数据替换为自选的文学主题数据集。",
        resume_role="独立开发",
        resume_tech=["HTML", "CSS", "JavaScript", "JSON", "Python http.server", "GitHub"],
        resume_metrics=["把课程示例数据替换为 20 条以上自选文学数据且不改核心逻辑",
                        "实现搜索 / 详情 / 统计三类交互"],
    )