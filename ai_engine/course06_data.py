# -*- coding: utf-8 -*-
"""课程 06《文学地图 / 数字叙事》课程数据。

结构：一个课程（course_006）→ 一个项目
  project_lit_map · 文学地图：把文学故事放到一条可以点击的路线里（T01–T08，Stage 1–4）

设计依据：AI导师引擎_文科零基础三课程_DeepSeek执行规格 v1.1 §5
技术栈：原生 HTML / CSS / JavaScript + 课程提供的 SVG / CSS 示意地图 + JSON + Python 自带 http.server
数据文件：data/places.json（地点，x/y 为示意图坐标）、data/stories.json（故事，place_id 关联地点、order 决定顺序）

技术边界：不是 GIS 课程——不引入高德/百度/Google Maps、Mapbox token、经纬度、GIS 数据库。

证据路径约定（与 course04/05 一致）：
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
COURSE_006 = {
    "title": "文学地图：把文学故事放到一条可以点击的路线里",
    "description": "不需要编程基础。使用课程整理的示例故事数据，在 AI 导师帮助下做出一个可点击地点、可顺序浏览的"
                   "本地文学地图；再替换成自己的叙事并新增地点，完成属于自己的版本。这是 SVG 示意地图，不涉及 GIS 与经纬度。",
    "projects": ["project_lit_map"],
    "img": "/courses/litmap.webp",
    "img_pos": "center 30%",
}


def build_project_lit_map() -> Project:
    # ===================== Stage 1：先看到一条文学路线 =====================
    stage1 = Stage(
        id="c6_stage1", title="① 先看到一条文学路线", order=1,
        objective="在本地跑通模板，看到至少三个文学地点与一条故事路线，并理解「地点」与「故事」是两份互相引用、分开存放的数据",
        tasks=["map06_t01", "map06_t02"],
    )
    stage2 = Stage(
        id="c6_stage2", title="② 让文学地图真的讲故事", order=2,
        objective="给地图加上地点点击与按顺序浏览，让这张图真正能把一个文学故事讲完",
        tasks=["map06_t03", "map06_t04"],
    )
    stage3 = Stage(
        id="c6_stage3", title="③ 把别人的故事换成自己的叙事", order=3,
        objective="在保持结构不变的前提下替换故事数据并新增地点，体会「数据决定故事的样子」",
        tasks=["map06_t05", "map06_t06"],
    )
    stage4 = Stage(
        id="c6_stage4", title="④ 完成我的数字文学叙事", order=4,
        objective="确定个人叙事主题与顺序、整理最终作品并完成一次真实复盘，交付可稳定运行的本地数字叙事作品",
        tasks=["map06_t07", "map06_t08"],
    )

    # ---- T01 打开我的第一张文学地图 ----
    task_t01 = Task(
        id="map06_t01", title="打开我的第一张文学地图", stage_id="c6_stage1", order=1,
        objective="在本地运行课程提供的文学地图，并看到至少三个文学地点与一条故事路线。",
        steps=[
            "下载并解压课程提供的 course_006_literary_map 模板",
            "在项目文件夹地址栏输入 cmd 并回车（Windows）；Mac/Linux 使用终端进入该目录",
            "运行 python -m http.server 8000",
            "打开浏览器访问 http://127.0.0.1:8000",
            "确认地图区域显示地点节点",
            "确认至少三个地点可以在页面中看到",
            "确认页面有一个简单的时间 / 顺序信息",
            "将项目复制到自己的 GitHub 仓库并保存仓库地址",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t01_1", "rb_map06_t01_2", "rb_map06_t01_3"],
        skill=SkillKey.env_setup,
        chunk_key="文学地图 > T01 本地运行",
        code_context=CodeContext(
            keywords=["json", "places", "stories", "svg", "app.js", "index.html"],
            likelyFiles=["places", "stories", "app", "index", "README"],
            searchPatterns=["http.server", "<svg", "circle", "place"],
        ),
        resume_points=[
            ResumePoint(point="用 Python 自带静态服务器在本地跑通一个 SVG 示意地图 + 数据驱动的叙事站点",
                        purpose="规避 fetch 读取 JSON 时的本地跨域问题",
                        result="文学地图可在本地稳定打开", kind="delivery"),
        ],
    )

    # ---- T02 我发现地图上的故事也是数据 ----
    task_t02 = Task(
        id="map06_t02", title="我发现地图上的故事也是数据", stage_id="c6_stage1", order=2,
        objective="修改一个地点或故事的文本内容，使地图上的对应内容发生变化，并保持原有路线仍能运行。",
        steps=[
            "找到 data/places.json",
            "修改一个地点名称或简介",
            "找到 data/stories.json",
            "修改对应故事标题",
            "保存文件并刷新浏览器页面",
            "确认地图和故事面板出现修改后的内容",
            "如果对应关系断开，向 AI 导师描述现象并定位 place_id",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t02_1", "rb_map06_t02_2", "rb_map06_t02_3"],
        skill=SkillKey.ai_assisted,
        chunk_key="文学地图 > T02 地点与故事数据",
        code_context=CodeContext(
            keywords=["json", "places", "stories", "name", "place_id"],
            likelyFiles=["places", "stories", "app", "index", "README"],
            searchPatterns=["places", "stories", "place_id", "id"],
        ),
    )

    # ---- T03 点击一个地方，讲一个故事 ----
    task_t03 = Task(
        id="map06_t03", title="点击一个地方，讲一个故事", stage_id="c6_stage2", order=3,
        objective="点击地图上的地点后，右侧 / 下方出现该地点对应的故事内容。",
        steps=[
            "选择一个地点",
            "让 AI 编程工具加入地点点击事件",
            "根据地点 ID 查找对应 stories.json 数据",
            "显示时间、标题和正文",
            "运行项目",
            "点击至少两个不同地点验证内容不同",
            "不允许把故事正文硬编码在 HTML 中",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t03_1", "rb_map06_t03_2", "rb_map06_t03_3"],
        skill=SkillKey.project_dev,
        chunk_key="文学地图 > T03 地点点击",
        code_context=CodeContext(
            keywords=["json", "stories", "place_id", "title", "body"],
            likelyFiles=["app", "stories", "places", "index", "README"],
            searchPatterns=["place_id", "find", "filter", "click"],
        ),
    )

    # ---- T04 沿着路线看完一个故事 ----
    task_t04 = Task(
        id="map06_t04", title="沿着路线看完一个故事", stage_id="c6_stage2", order=4,
        objective="增加一个明确的故事顺序，让学生可以按照时间 / 顺序查看地点与故事。",
        steps=[
            "确认 stories.json 中存在 order",
            "让 AI 按 order 排序故事",
            "页面提供「上一个 / 下一个」或等价的顺序浏览方式",
            "运行项目",
            "从第一个故事走到最后一个故事",
            "检查地点与故事内容始终保持对应",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t04_1", "rb_map06_t04_2", "rb_map06_t04_3"],
        skill=SkillKey.ui_design,
        chunk_key="文学地图 > T04 故事顺序",
        code_context=CodeContext(
            keywords=["json", "stories", "order", "sort"],
            likelyFiles=["app", "stories", "places", "index", "README"],
            searchPatterns=["order", "sort", "prev", "next"],
        ),
    )

    # ---- T05 替换一组我真正想讲的故事（核心实验任务）----
    task_t05 = Task(
        id="map06_t05", title="替换一组我真正想讲的故事", stage_id="c6_stage3", order=5,
        objective="在保持现有数据结构不变的情况下，将至少 5 条故事内容替换为学生自己选择和整理的文学故事。",
        steps=[
            "先备份原始 stories.json",
            "选择一个文学人物、作品或主题",
            "准备至少 5 个事件 / 故事节点",
            "按课程 schema 填入 stories.json",
            "为故事指定已有地点或增加一个符合格式的新地点",
            "运行项目",
            "依次点击这些故事对应地点",
            "确认新故事可以正常展示",
            "保存并提交 GitHub",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t05_1", "rb_map06_t05_2", "rb_map06_t05_3"],
        skill=SkillKey.ai_assisted,
        chunk_key="文学地图 > T05 替换故事",
        code_context=CodeContext(
            keywords=["json", "stories", "place_id", "title", "body", "order"],
            likelyFiles=["stories", "places", "app", "index", "README"],
            searchPatterns=["stories", "place_id", "order", "title"],
        ),
        resume_points=[
            ResumePoint(point="在不改动核心渲染逻辑的前提下，替换至少 5 条故事并保持 place_id 关联有效",
                        purpose="验证「地点 + 故事」双数据结构的可扩展性",
                        result="地图从课程示例变为具有个人叙事主题的版本", kind="delivery"),
        ],
    )

    # ---- T06 增加一个属于我自己的地点 / 路线节点 ----
    task_t06 = Task(
        id="map06_t06", title="增加一个属于我自己的地点 / 路线节点", stage_id="c6_stage3", order=6,
        objective="在现有地图数据结构内增加至少一个新地点，并为它增加至少一条故事，使地图成为学生自己的路线。",
        steps=[
            "复制一个已有地点对象",
            "修改 id 和 name",
            "修改 x / y 到地图内可见位置",
            "保存 places.json",
            "在 stories.json 中新增一条 story",
            "将新的 place_id 指向新地点",
            "运行项目",
            "点击新地点并查看故事",
            "不允许使用经纬度或外部地图服务",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t06_1", "rb_map06_t06_2", "rb_map06_t06_3"],
        skill=SkillKey.workflow,
        chunk_key="文学地图 > T06 新增地点",
        code_context=CodeContext(
            keywords=["json", "places", "stories", "x", "y", "id"],
            likelyFiles=["places", "stories", "app", "index", "README"],
            searchPatterns=["places", "\"x\"", "\"y\"", "place_id"],
        ),
        resume_points=[
            ResumePoint(point="在地图数据结构内新增至少一个地点并为其关联至少一条故事",
                        purpose="让地图从「课程路线」变为「学生自己的路线」",
                        result="地图出现学生自建的地点节点与故事", kind="engineering"),
        ],
    )

    # ---- T07 决定我要讲什么故事 ----
    task_t07 = Task(
        id="map06_t07", title="决定我要讲什么故事", stage_id="c6_stage4", order=7,
        objective="明确自己的数字叙事主题、顺序和重点地点，并修改首页标题与说明。",
        steps=[
            "写一句话定义故事主题",
            "确定 5 个以上核心故事节点",
            "为节点确定顺序",
            "修改首页标题",
            "修改首页介绍语",
            "设置一个默认起点",
            "运行项目并按顺序浏览一次",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t07_1", "rb_map06_t07_2", "rb_map06_t07_3"],
        skill=SkillKey.prd,
        chunk_key="文学地图 > T07 个人叙事",
        code_context=CodeContext(
            keywords=["json", "stories", "title", "order", "theme"],
            likelyFiles=["index", "app", "stories", "places", "README"],
            searchPatterns=["<title", "<h1", "order", "default"],
        ),
    )

    # ---- T08 完成我的文学地图 ----
    task_t08 = Task(
        id="map06_t08", title="完成我的文学地图", stage_id="c6_stage4", order=8,
        objective="完成一份可以在自己的电脑上稳定运行的数字文学叙事作品，并通过最终验收。",
        steps=[
            "再次运行 python -m http.server 8000",
            "从默认起点开始浏览",
            "点击至少三个地点",
            "使用故事顺序功能完整浏览一次",
            "检查个人新增地点和故事仍在",
            "更新 README：写清楚作品名称、主题、运行方法",
            "更新 DATA_SOURCE.md：写清楚数据来源与整理方式",
            "推送最终版本到 GitHub 并提交最终验收",
        ],
        evidence_required="code",
        rubric_ids=["rb_map06_t08_1", "rb_map06_t08_2", "rb_map06_t08_3", "rb_map06_t08_4"],
        skill=SkillKey.git,
        chunk_key="文学地图 > T08 最终交付",
        code_context=CodeContext(
            keywords=["json", "places", "stories", "readme", "data_source"],
            likelyFiles=["stories", "places", "README", "data_source"],
            searchPatterns=["http.server", "places", "stories"],
        ),
        resume_points=[
            ResumePoint(point="交付含 README 与数据来源说明（DATA_SOURCE.md）的完整本地数字叙事作品",
                        purpose="让他人可复现、让文学数据来源可追溯",
                        result="作品具备可交付与可复现性", kind="delivery"),
        ],
    )

    rubrics = [
        # T01
        Rubric(id="rb_map06_t01_1", task_id="map06_t01", criterion="项目文件完整",
               description="仓库中存在模板规定的核心文件，没有丢失或改名",
               required_evidence=["code"],
               pass_condition="存在 index.html、style.css、app.js、places.json、stories.json", weight=2),
        Rubric(id="rb_map06_t01_2", task_id="map06_t01", criterion="本地文学地图可运行",
               description="学生提供本地启动方式，运行后可看到地点节点",
               required_evidence=["code", "runtime"],
               pass_condition="按本地命令运行后可看到至少三个地点节点", weight=2),
        Rubric(id="rb_map06_t01_3", evaluation_role="theory", task_id="map06_t01", criterion="能描述地图节点的含义",
               description="用自己的话说明节点与故事数据的对应关系",
               required_evidence=["description"],
               pass_condition="能说明一个节点代表什么，故事数据代表什么", weight=1),
        # T02
        Rubric(id="rb_map06_t02_1", task_id="map06_t02", criterion="地点数据被真正读取",
               description="代码从 places.json 加载地点并渲染，改数据后节点文本变化",
               required_evidence=["code", "runtime"],
               pass_condition="修改 places.json 后地图节点文本发生变化", weight=2),
        Rubric(id="rb_map06_t02_2", task_id="map06_t02", criterion="故事与地点关联正确",
               description="故事用 place_id 引用地点，且指向存在的 id",
               required_evidence=["code"],
               pass_condition="stories.json 的 place_id 能对应 places.json 中已有 id", weight=2),
        Rubric(id="rb_map06_t02_3", evaluation_role="theory", task_id="map06_t02", criterion="能说明自己修改了哪里",
               description="自述指出至少一个修改的数据文件和结果",
               required_evidence=["description"],
               pass_condition="自述指出至少一个修改的数据文件和结果", weight=1),
        # T03
        Rubric(id="rb_map06_t03_1", task_id="map06_t03", criterion="地点点击能够显示故事",
               description="点击地点后故事面板显示对应故事",
               required_evidence=["code", "runtime"],
               pass_condition="点击地点后故事面板显示对应故事", weight=2),
        Rubric(id="rb_map06_t03_2", task_id="map06_t03", criterion="显示内容来自 stories.json",
               description="代码通过 place_id 查找故事，而不是把正文写死在 HTML",
               required_evidence=["code"],
               pass_condition="代码通过 place_id 查找对应故事，而不是把故事正文硬编码在 HTML", weight=2),
        Rubric(id="rb_map06_t03_3", evaluation_role="theory", task_id="map06_t03", criterion="能说明地点与故事如何关联",
               description="用自己的话说明 place_id 的用途",
               required_evidence=["description"],
               pass_condition="用自己的话说明 place_id 的用途", weight=1),
        # T04
        Rubric(id="rb_map06_t04_1", task_id="map06_t04", criterion="故事按 order 排序",
               description="页面展示顺序与 stories.json 的 order 一致",
               required_evidence=["code", "runtime"],
               pass_condition="页面展示顺序与 stories.json 的 order 一致", weight=2),
        Rubric(id="rb_map06_t04_2", task_id="map06_t04", criterion="可以连续浏览故事",
               description="存在前后切换或等价的连续阅读机制",
               required_evidence=["runtime"],
               pass_condition="至少存在前后切换或等价的连续阅读机制", weight=2),
        Rubric(id="rb_map06_t04_3", evaluation_role="theory", task_id="map06_t04", criterion="能说出一次实际阅读路径",
               description="自述写出从哪个地点到哪个地点，期间看到了什么",
               required_evidence=["description"],
               pass_condition="自述写出从哪个地点到哪个地点，期间看到了什么", weight=1),
        # T05
        Rubric(id="rb_map06_t05_1", task_id="map06_t05", criterion="成功替换至少 5 条故事数据",
               description="stories.json 中至少 5 条为学生自己整理的版本",
               required_evidence=["code"],
               pass_condition="stories.json 中至少 5 条内容为学生自己整理的版本", weight=2),
        Rubric(id="rb_map06_t05_2", task_id="map06_t05", criterion="新故事能被地图读取",
               description="新增内容可通过地点点击或顺序浏览正常展示",
               required_evidence=["code", "runtime"],
               pass_condition="新增内容能够通过地点点击或顺序浏览正常展示", weight=2),
        Rubric(id="rb_map06_t05_3", evaluation_role="theory", task_id="map06_t05", criterion="能说明自己的叙事主题",
               description="说明选择这一文学主题的原因",
               required_evidence=["description"],
               pass_condition="说明选择这一文学主题的原因", weight=1),
        # T06
        Rubric(id="rb_map06_t06_1", task_id="map06_t06", criterion="新增至少一个有效地点",
               description="places.json 中新增地点，地图能显示该节点",
               required_evidence=["code", "runtime"],
               pass_condition="places.json 中新增地点，地图能显示该地点节点", weight=2),
        Rubric(id="rb_map06_t06_2", task_id="map06_t06", criterion="新地点关联至少一条故事",
               description="新故事的 place_id 对应新增地点并可点击查看",
               required_evidence=["code", "runtime"],
               pass_condition="新故事的 place_id 对应新增地点，并能点击查看", weight=2),
        Rubric(id="rb_map06_t06_3", evaluation_role="theory", task_id="map06_t06", criterion="能解释自己新增的位置",
               description="说明为什么把该文学事件放在这个节点",
               required_evidence=["description"],
               pass_condition="说明为什么把该文学事件放在这个节点", weight=1),
        # T07
        Rubric(id="rb_map06_t07_1", task_id="map06_t07", criterion="作品有明确叙事主题",
               description="标题与故事数据主题一致",
               required_evidence=["code", "runtime"],
               pass_condition="标题与故事数据主题一致", weight=2),
        Rubric(id="rb_map06_t07_2", task_id="map06_t07", criterion="至少有 5 个核心故事节点",
               description="stories.json 至少包含 5 个学生整理 / 修改的核心节点",
               required_evidence=["code"],
               pass_condition="stories.json 至少包含 5 个学生整理 / 修改的核心节点", weight=2),
        Rubric(id="rb_map06_t07_3", evaluation_role="reflection", task_id="map06_t07", criterion="能说明故事为什么按此顺序组织",
               description="自述至少说明一处顺序设计理由",
               required_evidence=["description"],
               pass_condition="自述至少说明一处顺序设计理由", weight=1),
        # T08
        Rubric(id="rb_map06_t08_1", task_id="map06_t08", criterion="最终项目能够本地运行",
               description="按 README 的本地命令启动并显示地图",
               required_evidence=["code", "runtime"],
               pass_condition="项目可按 README 使用本地命令启动并显示地图", weight=2),
        Rubric(id="rb_map06_t08_2", task_id="map06_t08", criterion="地点、故事、顺序三个部分均可用",
               description="地点点击、故事展示、顺序浏览三项均验证成功",
               required_evidence=["runtime"],
               pass_condition="地点点击、故事展示、顺序浏览三项均验证成功", weight=2),
        Rubric(id="rb_map06_t08_3", task_id="map06_t08", criterion="有学生自己的叙事内容",
               description="至少 5 条个人故事 + 至少 1 个个人新增地点",
               required_evidence=["code"],
               pass_condition="至少 5 条个人故事 + 至少 1 个个人新增地点", weight=1),
        Rubric(id="rb_map06_t08_4", evaluation_role="reflection", task_id="map06_t08", criterion="完成一次真实项目复盘",
               description="写出一个遇到的问题、如何与 AI 协作解决、如何验证",
               required_evidence=["description"],
               pass_condition="写出一个遇到的问题、如何与 AI 协作解决、如何验证", weight=1),
    ]

    return Project(
        id="project_lit_map",
        title="文学地图 / 数字叙事",
        description="从课程整理的示例故事数据集出发，用课程提供的 SVG 示意地图做出一个可点击地点、"
                    "可顺序浏览的本地文学地图；再替换成自己的叙事并新增地点，完成属于自己的数字叙事版本。",
        stages=[stage1, stage2, stage3, stage4],
        tasks=[task_t01, task_t02, task_t03, task_t04, task_t05, task_t06, task_t07, task_t08],
        rubrics=rubrics,
        resume_intro="使用原生 HTML/CSS/JavaScript 与课程提供的 SVG 示意地图，基于「地点 + 故事」双 JSON 数据，"
                     "实现一个本地运行的文学地图 / 数字叙事作品：支持地点点击查看故事、按 order 顺序浏览，并新增自选地点与故事。",
        resume_role="独立开发",
        resume_tech=["HTML", "CSS", "JavaScript", "SVG", "JSON", "Python http.server", "GitHub"],
        resume_metrics=["替换 5 条以上自选故事并新增至少 1 个地点，place_id 关联全部有效",
                        "实现地点点击 / 故事展示 / 顺序浏览三类交互"],
    )