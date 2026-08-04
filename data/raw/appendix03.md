<title>©️邪修学习指南（谨慎观看）</title>

> 以下所教均为**旁门左道**，稍有不慎，行将踏错，如非不得已的情况，还是应当沉心基础，所谓：
> 
> 积土成山，风雨兴焉
> 
> 积水成渊，蛟龙生焉
> 
> 积善成德，而神明自得，圣心备焉

# 大一如何零基础做项目？

> 这是一个相对邪修的方法，不能提高你的代码水平和技术能力，唯一的作用是让你简历上，至少有东西可写，至少能完整的说出你开发的一个项目，VibeCoding时代的大势浩浩荡荡，我也无法评估此教程的合适与否，**姑妄言之，姑妄听之**

## 配置与需求：

1.学会如何使用github

2.下载trae/Codex/Claude code，并知悉如何接Api

3.仅建议游戏本/台式机

![这是一张用于说明相关项目开发配置的趣味梗图，上方配文“不会带团队 你就只能干到死”，图中戴眼镜的卡通拟人化猫咪用手指向上，连接着分别带有不同项目相关工具标识的卡通小狗，这些工具标识依次对应了文档中提及的需要使用的OpenAI类工具、特定AI工具、Anthropic类工具以及相关代码工具，直观呼应了该项目配置中需要使用多种AI工具完成开发的内容。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZWNmYjc0YzljNWFjMGMzM2VhYmUzODdiOTE4MmY0NWNfOTRmOTkzZDA2N2JhYzg5NzljNGU1ZTRkYTZkMjdkY2ZfSUQ6NzY2ODYyNjg1NTEyMTM1ODEyM18xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

---

## 第一节：克隆复现

### 本节目的

- 熟悉软件怎么下载（Python、Git、代码编辑器、各种依赖）
- 熟悉环境怎么配置（虚拟环境、依赖包版本管理）
- 熟悉怎么向AI提问（把报错日志丢给AI）

这一节做出来的项目不代表是你做的。 你只是把别人写好的代码搬到本地跑起来，如果你有一定的代码经验，跳到第二节即可



### 操作流程

#### 1.打开仓库

![这张图片展示的是GitHub平台上名为“pen-ho/medical_knowledge_graph_app-master”的代码仓库页面，与文档介绍的GitHub仓库操作流程相关。页面中清晰列出了该仓库包含的文件，包括文档提及的两个关键文件：`README.md`和`requirements.txt`，另外还有`img`、`kg`、`med_kg`、`gitignore`等文件。页面右侧的About区域标注了项目的核心功能模块，如代码复用、迭代检测等，明确这是一个与医疗知识图谱相关的项目，页面顶部显示了仓库的分支信息、提交记录等内容，符合文档中打开GitHub仓库后查看文件的操作场景。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZDIxNTYyNTU4ZjA1MzY4NTA2ZDZlNjVlZTFlNmUxZTJfMzA0MDJhZTNhMmQxNGZhZThhYWQ0ZTdkNjdlMjdhODJfSUQ6NzY2ODYyMzE4NTMxMTU4MzIwNV8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

1. 打开任意一个GitHub仓库
2. **先找到仓库里的两个关键文件**：

   - `README.md` —— 这是项目说明书

   ![图片展示了GitHub仓库中两个关键文件的图标及名称。上方是.gitignore文件，图标为一个文件夹图标，名称为.gitignore；下方是README.md文件，图标为一个带有“M”标识的文件图标，名称为README.md。该图片与文档中“先找到仓库里的两个关键文件”部分内容对应，直观呈现了“README.md”文件在GitHub仓库中的标识，强调其在项目说明书中的重要性。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NTI1ODFlNzA3MmUyNGE3YjliNWQ3YzkzNTIwMDkwMmJfYzhkNTM5NTdhNzBjMGYxNjliMmVhNGNjNjQ5MDQ3NTRfSUQ6NzY2ODYyMzE4NTgzOTkzNDM5M18xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

   - `requirements.txt`（Python项目）或 `package.json`（前端/Node项目）—— 依赖清单
   
     ![图片展示了GitHub仓库中`requirements.txt`文件的内容。左侧是仓库文件目录，包含`img`、`kg`、`med_kg`等文件夹及`.gitignore`、`README.md`、`requirement.txt`文件。右侧是`requirements.txt`文件内容，列出Python项目所需依赖库，如python 3.6、neo4j-community 4.1.4、boto3、tqdm等，还有torch 1.10.0、transformers 4.12.5等库版本号。该图片与上文介绍的GitHub仓库操作流程中，找到`requirements.txt`文件的内容相呼应，直观呈现了Python项目依赖清单。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZGI5YjU1YzgzMWNlMDY4NTBiMTJmNGVjY2M1MzQ0ZTVfMDU5ZDk2MjQ4YTdlOTM5NDY5OTk4M2FkZmUxNWIxNjZfSUQ6NzY2ODYyMzE4NzExNDU2MDc4NF8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

README里通常记载了：

> 1.项目功能和效果截图
> 
> 2.需要下载的软件清单及下载地址
> 
> 3.需要的版本号（例如 `python 3.6`、`neo4j-community 4.1.4`、`torch 1.10.0`、`django 3.2.7`）
> 
> 4.项目目录结构和运行方式



<callout emoji="⚠️">
**最大的误区是跳过README直接下代码，听着，跳过**~~剧情~~**readme，等于跳过**~~人生~~**项目**
</callout>



#### 2.打开AI

掌握README的信息之后，你**不需要自己逐个搜索下载地址**。直接把README全文发给AI，使用这样的提示词：

> "这是一个开源项目的README，请帮我列出运行这个项目需要的所有软件和依赖，并给出每个软件对应的官方下载地址（注意区分Windows版本）。同时告诉我安装的先后顺序。"



AI会帮你整理出一张清单，类似：

| 顺序 | 软件 | 版本要求 | 下载地址 | 备注 |
|-|-|-|-|-|
| 1 | Python | 3.6+ | python.org | 安装时勾选Add to PATH |
| 2 | Git | 最新 | git-scm.com | 一路下一步 |
| 3 | 代码编辑器 | VS Code | code.visualstudio.com | 装Python扩展 |
| 4 | Neo4j | 4.1.4 | neo4j.com | 本项目专用 |
| ... | ... | ... | ... | ... |



#### 3.下载代码

1. 回到仓库首页，点击绿色 `Code` 按钮 → `Download ZIP`
2. 保存时**选D盘路径，不要占C盘空间**（有些软件或者配置可能需要C盘，但至少大部分代码项目不需要）
3. 解压后，在文件夹上右键 → "通过Code打开"（或你用的任意编辑器）

![图片展示的是GitHub仓库“pen-ho/medical_knowledge_graph_app-master”的页面。页面左侧是仓库目录，包含img、kg、med_kg等文件夹及.gitignore、README.md、requirement.txt等文件。右侧是仓库介绍，提到该系统实现包括构建知识图谱、基于知识图谱的流水线问答以及前端展示等内容。页面右上角有“Code”按钮，点击后弹出下拉菜单，其中“Download ZIP”选项被红色框突出显示，对应文档中“下载代码”步骤里“点击绿色`Code`按钮→`Download ZIP`”的操作说明。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NDdhMzk1OGM4NWQxNmRjZmE1YzQ2MGFlMjZmZjJmZDJfOGJkOTA0N2M0YjAwODNhZDljZmU1YmJlZTEzZTI0ZTRfSUQ6NzY2ODYyMzE5MDU1NzUyNzAyMV8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)



#### 4.Bug！

理论上现在就可以直接运行了。但现实中你一定会遇到：

> - 依赖包版本冲突
> - 环境变量没配
> - 代码里的小bug
> - 注释里的坑

<callout emoji="😆">
**这就对了，没问题你都多余克隆，目的就是让你来解决问题的**
</callout>

1. 点运行 → 看报错
2. **把报错的日志截图（或复制全文）发给AI**，问："运行这个项目时报错如下，请告诉我原因和解决方法"
3. 按AI给的方案修改 → 再运行 → 再报错 → 再问AI
4. 循环直到跑通

> 正常快的话，**一个小时以内肯定能解决**。但初次尝试可能会花几个小时在环境配置上



### 验收标准

- [ ] 能清楚的知道这个项目需要什么环境

- [ ] 能独立完成一次"下载→配环境→跑通"的全流程

- [ ] 遇到报错能够截图问AI解决

---



## 第二节：重建项目

### 本节目的

> 只拿项目的README（说明书），不拿代码，让AI根据说明书把同样的功能重新写出来。这一步的意义在于验证你是否真的理解了项目的功能逻辑，而不是只会下载。



### 操作流程

#### 1.下载README

在仓库页面单独下载（或直接复制）`README.md` 的内容，**不下载任何代码文件**。



#### 2.拆解开发任务

把README发给AI，用这样的提示词：

> "这是一个开源项目的说明书，但没有源代码。请你以资深开发者的视角，把这份说明书拆解为一份开发任务清单：
> 
> 1. 项目需要实现哪些功能模块？
> 2. 每个模块需要哪些文件？
> 3. 推荐的文件夹结构是什么样的？
> 4. 开发的先后顺序建议是什么？"



#### 3.逐步重建

按照AI给出的结构：

1. 自己在D盘新建一个空文件夹
2. 让AI从第一个文件开始逐一生成代码
3. 每生成一个文件，**确认你看懂了它的作用**（看不懂就问AI"这个文件的每一部分分别干什么"）
4. 逐步补齐，直到功能复现

> ⚠️ 这一节是抄别人的README、抄AI生成的代码。但你需要保证自己能看懂项目里的文件，否则在面试上你什么都说不出来



#### 4.跑通&修Bug

流程与第一节第四步相同：报错 → 截图/复制 → 问AI → 修改 → 循环，这一操作甚至可能持续几天，持续到你崩溃，有时候可能是AI的长记忆出现问题，或者是AI思考过度，可以多个AI交叉审查

![图片是一只站在窗边的动物，上方文字为“Token又不够了”。这与文档中“4.跑通&修Bug”部分内容相关，可能是用来幽默地表达在AI辅助修复bug过程中，因Token数量不足而遇到的困扰，形象地说明了在AI辅助开发过程中可能遇到的资源限制问题。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YzdhOGQzMTc4MGVhZDM4NTVhNTA2ODc1YTk2YzQzOTNfOGY2NjI2N2IzYTkxN2E1MTZiOTVjNTY3OTY2ZDdhZDlfSUQ6NzY2ODYyNTQ2MjYyMTQwODIzN18xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

### 验收标准

- [ ] 能对着README复述项目有哪些功能模块

- [ ] 重建的项目功能与README描述一致

- [ ] 能解释每个文件的职责

---



## 第三节：项目开发

### 本节目的

> 前两节都是复现，这一次要做的是**从0到1创造一个属于你的项目**。

![图片展示了“想象中的vibe coding”与“vibe coding半小时后...”的对比。上方文字为“想象中的vibe coding”，画面中左侧是手持锤子的猿人，右侧是手持剑的猿人。下方文字为“vibe coding半小时后...”，画面中左侧是穿着西装的猿人，右侧是西装男子，猿人手中拿着一个带有图案的徽章。该图片与上下文“大一如何零基础做项目”相关，通过幽默对比，暗示实际编程可能与想象中存在差异。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzA4NGFmN2Q1MTRiYjA0N2I5YmFjNDRmYWMxOTVjMTdfZjVhZDg1ZDEzMmZmMDRmZGYxNDQ0NzY2OTQxZTExM2RfSUQ6NzY2ODYyNTM4NzAzOTU3NTI0N18xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

### 操作流程

#### 1.需求文档（PRD）

不要上来就说帮我写个XX系统

> "我想做一个[一句话描述，例如：面向大学生的二手书交易平台]。请你扮演产品经理，通过向我提问的方式，帮我明确这个产品需要哪些功能。每次最多问5个问题，等我回答后再继续。"



通过多轮问答，让AI帮你产出一份**结构化的需求文档**，至少包含：

1. **项目简介**：一句话说清这是什么
2. **目标用户**：谁会用？
3. **核心功能列表**：每个功能用一句话描述（例如"用户可以发布二手书信息，包含书名、价格、照片"）
4. **页面清单**：有哪些页面，每个页面承担什么功能
5. **技术选型**：前端用什么、后端用什么、数据库用什么（不懂技术就让AI推荐并说理由）

#### 2.增 / 删 / 改

> **这一步是最重要的环节，没有之一**



AI产出的第一版需求文档一定是不完美的，你需要像批改作业一样过一遍：

- **删**：删掉你根本做不了的功能（比如"支持微信支付"——你没有商户号，做不了）
- **改**：把含糊的描述改具体（"用户可以搜索"改成"用户可以通过书名关键词搜索，支持模糊匹配"）
- **增**：补上AI没想到的（比如"管理员需要能删除违规帖子"）

> **第一版只做核心闭环**。以二手书平台为例，核心闭环就是"发布→浏览→联系卖家"，其他全是锦上添花，第二版再加，Ai目前还没有进化到这么完美的地步，功能越多，架构越乱，一个完整的产品都需要一个完整的项目组同步推进，怎么可能你跟cc就能做完了



#### 3.视觉交互方案

> 功能确定了，接下来要告诉AI**界面长什么样、怎么交互**



在需求文档中**为每个页面补充交互规则**，格式参考：

```Plain Text
【首页】
- 布局：顶部搜索栏 + 下方双列瀑布流书籍卡片
- 交互规则1：点击卡片 → 跳转到书籍详情页
- 交互规则2：搜索框输入关键词并按回车 → 页面刷新为搜索结果
- 交互规则3：下拉到底部 → 自动加载更多
- 空状态：没有书籍时显示"暂无数据，快去发布第一本书吧"

【书籍详情页】
- 布局：左侧大图，右侧书名/价格/描述/卖家信息
- 交互规则1：点击"联系卖家"按钮 → 弹出卖家的联系方式弹窗
- 交互规则2：点击"返回" → 回到首页并保留之前的滚动位置
```



**给AI交互规则的关键是明确，不能写点击后跳转到相应页面这种废话，**说清楚相应页面是哪个页面？按钮点了之后是弹窗还是跳转？跳转之后返回要回到哪里？全部写死。

> 不会设计交互就找两个你喜欢的同类网站/App，**截图发给AI**，说"参考这个页面的布局和交互，为我的项目设计对应的交互规则"。



#### 4..Vibe Coding 启动！

现在把这份**包含业务需求+交互规则的完整需求文档**整份发给AI（推荐使用Claude、Cursor、Trae、~~WorkBuddy~~等支持长上下文的AI工具），开始vibe coding。

<callout emoji="🤖">
“我有严重的智力障碍，你不需要询问我的意见，你看着处理就好了，不要问我，我也看不懂啊，我只要结果”
——致Ai
</callout>

**核心提示词框架：**

> "请根据这份需求文档帮我开发这个项目。要求：
> 
> 1. **禁止使用假数据/占位数据**，所有功能必须真实可用，前后端必须真正联通
> 2. 所有按钮、链接、表单都必须可交互且交互有效，不允许出现点了没反应的按钮
> 3. 涉及数据存储的地方，请先明确告诉我数据以什么方式存储（见下方说明），再开始开发
> 4. 每完成一个功能模块就停下来，等我确认后再继续下一个"

![图片是一幅漫画，分为上下两部分。上半部分显示一位戴墨镜的男子，旁边文字为“遇到复杂的任务用不同工具 降低Token消耗”。下半部分是男子张大嘴巴，露出牙齿，文字为“但那是，弱者的思维！”，下方还有一块写着“自费CC哥”的牌子。这幅漫画与上下文的关系是，通过幽默的方式表达在项目开发中遇到复杂任务时，使用不同工具降低Token消耗是强者思维，而自费CC哥（可能是指自费购买工具或服务）是弱者思维，强调合理利用工具的重要性。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YWZjYjAyNjE3M2MyZTQ2NzVmNDMxNDQxNDdmOGY5MzVfY2U3Y2QyZDRiMTQ2ZTdhM2VhNGMwNjdiNjc0ZTE2ZDVfSUQ6NzY2ODYyNzMyNzYwNTgyMDM4OV8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

![图片是一位戴眼镜的男子，他手指放在嘴边，表情专注，旁边有对话框写着“我要在接下来的两小时内”“用CC写完整个项目”。这与文档中“大一如何零基础做项目”“项目开发”“操作流程”等内容相关，可能是用来幽默地表达在短时间内完成项目开发的紧迫感，与上下文关于项目开发的讨论相呼应。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzAyNDVjN2NkYzZkODIxZTQ1NjY5NjM2MTY1MzA5MzlfNTA4NjU1OGJkZGE1MTU1M2NmZDYwYmJjNWYyODdhNjNfSUQ6NzY2ODYyNzM5Nzk5NDUxNTczOV8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

不使用假数据:AI为了快速出效果，会把数据写死在代码里（例如前端页面直接写死"张三的二手书，30元"）。这等于做了个PPT，不是做了个系统。



在需求文档或提示词中明确数据存储方式：

| 项目规模 | 推荐存储方式 | 说明 |
|-|-|-|
| 个人练手小项目 | SQLite | 单文件数据库，零配置，Python/Node原生支持 |
| 正经课程设计 | SQLite / MySQL/SQL Server | MySQL需要单独装，但更接近真实生产环境 |
| 纯前端演示 | 浏览器 localStorage | 不需要后端，但刷新数据还在 |
| 不想管数据库 | JSON文件 / 云数据库 |  |

<callout emoji="⚠️">
**开发过程中，每完成一个功能，立刻做一次真实验证**：发布一条数据 → 刷新页面 → 数据还在
</callout>



#### 5.改Bug

功能做完 ≠ 项目完成。接下来进入漫长的修Bug阶段

1. **逐个功能点击测试**（把自己当sb，乱点、狂点、连续点、输入奇怪的东西）
2. 发现Bug → **完整描述现象 + 报错信息**发给AI

   > ❌ 错误示范：我草它坏了！
   > 
   > ❌ 错误示范：帮帮我，Ai先生！
   > 
   > ✅ 正确示范：点击发布按钮后，页面提示提交失败，控制台报错 xxx，后端日志显示 xxx
3. AI修复 → 回归测试（重新测一遍这个功能 + 顺带测一遍它附近的功能，防止改A坏B）
4. 循环直到你连续乱点五分钟都点不出新问题

<callout emoji="🤖">
Gpt！你都做了些什么！code值都是null。网站后端数据的code字段根本没填值！
</callout>



## 当所有功能都真实、可交互、经得住乱点时——**恭喜你**

![图片展示了一群人物站在类似海底的场景中。人物们身着不同风格的服装，有的穿着西装，有的穿着连衣裙，姿态各异，有的双手抱胸，有的双手叉腰，还有的双手合十。背景是蓝色的天空和海洋，天空中有白云。这张图片可能用于表达人物在特定情境下的状态或氛围，与上下文讨论大一如何零基础做项目的内容无直接关联。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MDI4ODExOGVjMmUwYmY1MzhhZDI0Yjc4ZGQ3Y2Q0YzhfZjRhMmZmZTczY2FlMjg1NGU5NGVhNDQ3MmYzMDhlOTJfSUQ6NzY2ODYyNzc4Njc0NzEwNDI0NF8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

---

# 论文怎么写？

> 这是一个只能用在课程小论文或者是论文初稿，一旦完全依赖ai工具，这会造成学术造假，必须注意，ai只是工具而非，真正的内容是需要手动修改填补优化的，

## 配置与需求：

1.需要完成所有代码工作

2.下载trae/Codex/Claude code

# 论文步骤

## 1.预准备

使用trae等软件，打开代码所在的文件夹，让trae内置的ai阅读你的代码，告诉你整个项目具体有哪些功能，并生成为一个**项目文档**。

再生成2个文档：

- [ ] **readme**，作为系统的使用说明书

- [ ] **论文辅助文档**，作为论文写作的参考

> 其中**readme**让ai自行生成即可，**论文辅助文档**生成指令词参考以下：
> 
> 我在撰写学术论文，基于**项目文档**：检索该项目的代码，重新撰写一份‘**论文辅助文档**’，辅助我写论文，告诉我该项目
> 
> 1.如何基于深度学习进行检测
> 
> 2.数据增强技术应用
> 
> 3.特征融合模块的设计
> 
> 4.边界框回归损失函数的优化
> 
> 5.模型训练策略
> 
> 6.基于视频流的目标检测技术
> 
> 7.前端用户界面的实现
> 
> 8.如有其他则补充
> 
> 以上内容同时需要写出代码出自哪个文件夹



## 2.进行中

然后去我们学校官网点击右上角的图书馆，里面可以搜索论文，你去搜索一些相关内容的论文建议硕士论文为主，太高级的你用不上。

使用Gemini的pro模型加深度研究，或者其他你用习惯的ai，鉴于Gemini近期的降智与降额行为，建议改用其他ai，把你找到的参考论文资料，论文模板和格式要求都扔上去

> 生成指令词参考以下：
> 
> 我正在撰写大学的学术论文，根据我的要求完成以下的事项，且必须遵守：
> 
> 1.阅读**论文辅助文档**和**README**（或者**项目文档**），这是我的作品，一个基于xxx的xxxx系统
> 
> 2.阅读并记忆暨南大学本科毕业论文模板，保障后续生产的结果不会偏离模板要求
> 
> 3.阅读并参考给你的相关论文文献，学习如何编写相关题目的论文，这只是学习，禁止抄袭，否则会导致被开除！
> 
> 4.论文内容中，如果有关作品图表或数据，需要严格按照**论文辅助文档**和**README**（or**项目文档**）内容，有需要填充但缺乏数据和实验的位置留空标注，通知我修改。
> 
> 5.开始撰写一份论文



## 3.修正

这基本就会产生一个初稿，然后要对这个初稿进行修改，把初稿和这个语句发给另外一个ai，让他们互相监督，这边比较建议使用DeepSeek，D老师目前的逻辑链和思考特别严谨，评论相对冷酷和客观，像Gemini，豆包等非常谄媚

> 生成指令词参考以下：
> 
> 这是我计算机科学与技术专业学生的毕业论文，你作为这个领域的专家，根据本科毕设难度，从论文完整度，内容分布合理方面先对其进行整体评价，满分一百。打分后请详细全面客观准确的找出其中的问题，并给出我能直接复制成批注的具有可操作性的建议，越详细越好。你得写的尽可能通俗易懂



## 4.持续进行

继续进行修改，直到你觉得改无可改了，就开始画图，我是做yolo视觉检测，下面的1234就是论文的内容，是我论文中图像标准化预处理的步骤

> 生成指令词参考以下：
> 
> 我在撰写一篇学术论文，生成图像标准化预处理科研绘图（图的名字），插入论文中
> 
> 1.LetterBox 等比例缩放：将原始图像按比例缩放到模型要求的输入尺寸 640×640，保持图像原始长宽比不变，对缩放后不足的区域采用灰度值 114 进行边界填充，避免图像拉伸变形导致的病斑特征失真；
> 
> 2.色彩空间转换：将 OpenCV 读取的 BGR 格式图像转换为 RGB 格式，适配 PyTorch 模型的输入要求；
> 
> 3.维度转换与归一化：将图像从 HWC（高度、宽度、通道）格式转换为 CHW（通道、高度、宽度）格式，同时将像素值从 0-255 的整数范围归一化到 0-1 的浮点数范围，适配模型的张量输入要求；
> 
> 批次维度扩展：为单张图像扩展 batch 批次维度，最终生成形状为 (1, 3, 640, 640) 的输入张量，输入模型完成推理

你知道那个图的名字，你就直接说，像什么用例图，架构图，

> 我在撰写一篇学术论文生成系统整体架构图，插入论文中
> 
> Plain Text
> 
> 输入层（图片/视频/实时摄像头流）
> 
>     ↓
> 
> 预处理模块（缩放/归一化/格式转换）
> 
>     ↓
> 
> 算法检测核心（YOLOv8s）
> 
> ├─ 主干网络Backbone（C2f+SPPF）→ 多尺度特征提取
> 
> ├─ 特征融合网络Neck（FPN+PAN）→ 语义与位置特征双向融合
> 
> └─ 解耦检测头Head → 病害分类与边界框回归
> 
>     ↓
> 
> 后处理模块（NMS/阈值过滤/结果解析）
> 
>     ↓
> 
> 可视化交互系统（PyQt5）
> 
> ├─ 结果渲染（检测框/标签/置信度绘制）
> 
> ├─ 实时显示（图像/视频/摄像头流预览）
> 
> └─ 参数交互（置信度/IOU阈值动态调整）
> 
>     ↓
> 
> 输出层（检测结果保存/病害统计输出）

如果你不知道那个图的名字就统一叫科研绘图，会跑代码然后生成图的，还有就是论文那些公式，AI也会自动生成插入在里面。



## 5.补缺

基本做到这里，你的大致框架都出来了，你就开始修改细节，文字和格式类的细节可以不着急，先把图片细节补好，然后图片下面标注图几，公式也要标注，如果有表格就弄成三线表，可以直接去b站搜索论文三线表制作就会有教程，表也记得标注表几。

如果参考文献有点找不到的话，这边比较喜欢使用谷歌的 **NotebookLM** 这个网站，有点偏向于AI笔记本，不用钱，去搜索**知网总库**，然后把他的网址复制下来放在图片中间那个位置，转一会就解析到了，到时候它就会自动搜索这个网站的东西

> 对了，这些是需要开VPN的，建议是开全局，然后走新加坡或者台湾之类的地区

![这张图片展示的是可免费使用的AI笔记本工具NotebookLM的操作界面界面。界面中央有搜索框，输入栏提示可“在网络中搜索来源”，下方提供了上文件、网站、云端硬盘、复制的文字这几种添加内容的方式，对应了文档中提到的在NotebookLM里添加知网网址进行解析的使用场景，同时界面左侧还有“添加来源”的相关选项，右侧设有Studio功能区，该工具使用需开启VPN，与上下文内容相互契合。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MTBjODBhNDU3YjU5MzQ4N2VlNWZlMjVkZTAwYzQ5YThfZDBhNzMzYjRiNWMzODk1ZjUwMDQ2YjMxNWE4ZTEwNDJfSUQ6NzY1NzUzNjc3Njk3Mzc4MTk3NF8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

![这张图片展示的是AI笔记本工具NotebookLM的操作界面，界面主题为“China National Knowledge Infrastructure Resource and Navigation Guide”，也就是中国知网相关内容。界面左侧为来源栏，可选择搜索渠道，勾选了“Web”和“Fast Research”选项，还显示已选中“首页-总库平台-中国知网”，用于搜索相关来源内容；右侧为对话栏，呈现了关于中国知网的介绍内容，说明该平台整合了各类学术资源，用户还可选择输入内容进行操作，界面底部标注该功能由NotebookLM提供。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NmY2YTM3YjIzOWYyYTRiZWQwMDk1Y2M4ZGEyNWEzODNfM2EyYzAyYTM4MmM5OGI4ODUyZWQ5ZTgwZDY3ZDAxYTJfSUQ6NzY1NzUzNzI1MTM1MzY0NDI0NV8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

记得把它勾选上，这样搜索的时候，就会搜索来源了，然后继续在左边那个来源：添加来源里面，塞进你的论文，或者其他资料，它就会读取你的论文，你的资料，网站，你就去让他搜索有没有相关研究的论文，就可以查出很多了，如果你不是很擅长引用的话，你就去淘宝买一个知网查重，有很便宜的几块钱，不过字数只有15000，你可以把没用的地方上删掉，保留正文，然后去查重，标红的地方，它就可以是你的参考文献来源，甚至就等于直接告诉你，你这一段跟什么论文重复了，有了公式，有了图，有了表之后，论文就有模有样了

![图片展示了中国知网总库的界面。上方显示“中国国家知识基础设施资源导航指南”，下方有“来源”和“对错”两个选项卡。在“来源”选项卡下，有“在互联网中搜索来源”“在知网中搜索来源”“在合作平台中搜索来源”三个来源类别，其中“在互联网中搜索来源”类别被红圈突出显示。该图片与上文提到的使用谷歌NotebookLM网站搜索知网总库内容，以及在来源处添加论文等查找相关研究论文的内容相关，直观呈现了操作界面。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODE5NzBjOTIzODIwYzQ2MzE3OTEzMDRjMjQ5ZGM4NDZfOWVlYTM5NjRlZTExZDNjOWQxZjQ4ZjY5ZDdhNDA1OTZfSUQ6NzY1NzUzNzk2NDc5NjM0OTYzM18xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM)

我试过生成纯英文的图，然后它有个问题，就是英文文字太长了，它容易重叠，如果你想要显得高端就继续英文，你想要细看没什么瑕疵，你就用中文

<table><colgroup><col/><col/></colgroup><tbody><tr><td><img name="17b2a13cb3faeaeb7b2e36ccef421f8d.png" alt="图片为特征融合模块设计示意图，展示了从Backbone P3、P4、P5提取的特征通过C2f模块进行融合的过程。P3提取浅层特征，P4提取中层特征，P5提取深层特征，经C2f模块后，通过Concat和C2f模块进行上采样和下采样，最终与检测头（Large Targets、Medium Targets、Small Targets）相连。该图与上下文介绍的特征融合模块设计相关，直观呈现了各部分的连接关系。" crop="[0.000000,0.000000,1.000000,0.957000]" href="https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=M2M5ZDJlYTUwNzQ1MGE0ZmVmMjA3NzU1YWQyOTM5ZDZfMWYwN2ZjNGNkYTMyOGYxYTQ0MTNhNTU3ZTEyMTlmZDFfSUQ6NzY1NzUzODg1MTE0OTI4NjM3OF8xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM" mime="image/png" scale="0.323055" src="AdsFb9X7Xob82dxPcStcfGQtnYb"/></td><td><img name="4babfe4cbe836dfb7b1f472829a12cfd.png" alt="图片展示了病害检测系统架构图。系统分为算法检测核心与可视化交互系统两大模块。算法检测核心包括输入层、预处理模块、算法检测核心（YOLOv8s）、后处理模块；可视化交互系统包含结果渲染、实时显示、参数交互、输出层。图中还标注了各模块的具体内容，如主干网络Backbone、特征融合网络Neck、解耦检测头Head等。该图与上文提到的病害检测系统架构相呼应，直观呈现了系统各部分的组成及关系。" crop="[0.000000,0.068300,1.000000,0.984100]" href="https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NThjY2ZlZDVkYjYyYTc2ZTdmMTFhNDc4YjAzZmFmOGFfYWUyMDI2YzE2YjEzYzdkM2U3ZjU4Mjc4NDA2Mzc4NWFfSUQ6NzY1NzUzODg3NTY4MjE5NjQ1M18xNzg1ODMxNTc5OjE3ODU4MzUxNzlfVjM" mime="image/png" scale="0.309756" src="EH7YbQHNbo4KqHxxl6wcTS5fnJb"/></td></tr></tbody></table>

AI它可能某些地方还是不遵守模板，或者造假，所以在全部做完之后，你还要再重新用AI+人工双重检查，Gemini生成的文字内容还是偏少的，当时大概生成了七八千字，而豆包专家版大概有1万多，具体要用什么AI自己决定，都是限制ai要跟着模板，且要符合代码内容，可以参考其他论文格式，但不能抄袭，做到这一步，基本论文初稿完成的差不多了，你就要确定论文是不是没问题，然后开始改正

**但是要注意以上经验，不是每一种方向都可以通用！！！**具体的指示词请自行微调，但ai生成论文的底层逻辑，还是以你提供的参考论文为基础，因此参考论文的选择极为重要，不需要多，但是一定要最契合四五篇内足矣

---

<callout emoji="🐳"><h3>返回导航页：<cite doc-id="VvKVwsHo2iIIC4ko0PmcKs4lnKd" file-type="wiki" title="信科院-从入学到被开除" type="doc"></cite></h3></callout>
