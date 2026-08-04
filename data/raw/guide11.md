<title>🏢Git 使用指南（零基础入门到协作进阶）</title>

# 一、前言：为什么要学 Git？

### **学习前置说明**

学习 Git 无需死记硬背所有命令，核心掌握**工作区域流转逻辑、分支管理、协同流程、报错处理**四大核心。绝大多数日常开发场景，仅需掌握 20% 高频命令即可覆盖 99% 需求。本指南从零基础实操出发，规避晦涩理论，全程结合真实开发场景，兼顾个人开发与企业团队协作，新手可直接跟着实操落地。

### Git 是什么

> Git 是一款**免费、开源的分布式版本控制系统**，由 Linux 之父林纳斯·托瓦兹开发，核心作用是对项目代码、文档进行版本管理，全程记录每一次修改、新增、删除操作，支持随时回溯历史版本、切换开发分支、多人协同开发。是目前开发行业通用的版本管理工具，适配所有编程语言、项目类型。实习/工作/做项目必须会用到！

![图片展示的是《辛普森一家》中的角色，他穿着黑色西装、红色领结，双手合十放在嘴边，表情专注。画面下方有文字“git add . git commit -m ' '”，意在幽默地表达在使用Git时进行“添加”和“提交”操作的场景。该图片位于文档中“学习前置说明”部分，用以辅助说明Git相关操作，增添趣味性。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZjY1NGQyOTZjZmQzZjQ3MzYzZWEzZmY5MmFkNzBiMDFfYjM4OWZhZTY2MmU0OGI0ODdhZWIzZWNmNmEzMmQwNDNfSUQ6NzY1ODMzNzA4NDExNzIwODA0N18xNzg1ODMxNTc0OjE3ODU4MzUxNzRfVjM)

### Git VS SVN：核心区别与优势

> 早期行业主流版本控制工具为 SVN（集中式），如今已基本被 Git 替代，二者核心差异如下：

| **架构差异**： | SVN 是集中式，所有版本数据仅存储在中央服务器，本地仅保存最新代码 | Git 是分布式，每一台开发者电脑都是完整仓库，包含全部历史版本。 |
|-|-|-|
| **离线操作能力**： | SVN 必须联网才能提交、查看版本 | Git 支持**离线本地提交**，联网后同步远程即可，开发不受网络限制 |
| **容错性**： | SVN 中央服务器故障会导致整个项目版本丢失 | Git 本地留存完整版本，服务器故障不影响项目数据。 |
| **分支能力**： | SVN 分支创建繁琐、合并风险高 | Git 分支轻量化，创建、切换、合并、删除秒级完成，适配多并行开发场景 |

### 核心适用场景

> 1. **个人项目管理**：记录代码迭代版本，无需手动备份多个版本文件，随时回溯 bug、恢复误删代码。
> 2. **团队协同开发**：多人并行开发不同功能，互不干扰，统一合并代码、追溯修改人、记录开发日志。
> 3. **版本迭代管理**：适配项目测试版、正式版、修复版迭代，精准标记每一个发布版本。
> 4. **代码安全备份**：本地+远程双备份，避免本地文件丢失、电脑故障导致项目损毁。

---

# 二、Git 环境搭建与基础配置

### 1. 多平台安装教程

#### Windows 安装

> 1. 前往 Git 官网（git-scm.com）下载对应系统版本，推荐 64 位稳定版；
> 
> 2. 双击安装包，全程默认下一步即可，无需修改复杂配置；
> 
> 3. 安装完成后，桌面右键可看到「Git Bash Here」，打开即可使用 Git 命令。

#### Mac 安装

> 方式一（推荐）：打开终端，输入 brew install git（需提前安装 Homebrew）；
> 
> 方式二：下载官网 dmg 安装包，手动安装。

#### Linux 安装（Ubuntu/CentOS）

> Ubuntu/Debian：sudo apt install git -y
> 
> CentOS/RHEL：sudo yum install git -y

![图片是一张关于选择电脑操作系统的选择图。图中以“开始！”为起点，根据是否是小白、是否在意垃圾文件、能否容忍多少垃圾等条件分支，最终指向不同操作系统。如小白且在意垃圾文件，可选择Ubuntu；小白且能容忍较多垃圾，可选择Linux Mint等。图中还标注了不同操作系统，如HarmonyOS、Fedora、openSUSE等，以及一些操作系统的特点说明。该图与文档中操作系统选择的内容相关，为读者提供了一种选择操作系统的趣味方式。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MGI4ZjljMzY1Nzg0ZGM5M2EyZjNiODQ5ZDA4M2NjM2VfYTQ0ZDk4MzM3M2MyNmU2YzJhZmI0OGU5ZjhmOGE1NDhfSUQ6NzY1ODMzODYwNDI1NDU0NjkyM18xNzg1ODMxNTc0OjE3ODU4MzUxNzRfVjM)

### 2. 核心全局必配（安装后第一步操作）

Git 每一次提交都会记录作者信息，必须配置用户名和邮箱，否则无法正常提交代码，全局配置仅需设置一次。

```Plaintext
# 配置用户名（自定义，建议真实姓名/开发昵称）
git config --global user.name "你的用户名"

# 配置邮箱（与 Gitee/GitHub 注册邮箱一致，便于识别提交记录）
git config --global user.email "你的邮箱"
```

### 3. 辅助优化配置

```Plaintext
# 开启大小写敏感（Windows 默认不敏感，项目必备）
git config --global core.ignorecase false

# 统一换行符，解决 Windows/Mac 换行符冲突报错
git config --global core.autocrlf true

# 设置默认编辑器为 Vim（可选，新手可默认）
git config --global core.editor vim
```

### 4. 远程仓库 SSH 密钥配置（免密推送）

默认 HTTPS 推送代码需要频繁输入账号密码，配置 SSH 密钥后可实现永久免密推送，适配 GitHub、Gitee、GitLab。

1. 终端输入密钥生成命令，全程回车默认即可：

```Plaintext
ssh-keygen -t ed25519 -C "你的注册邮箱"
```

2. 查看并复制公钥文件内容：

```Plaintext
# Windows
cat ~/.ssh/id_ed25519.pub

# Mac/Linux 通用
cat ~/.ssh/id_ed25519.pub
```

3. 进入 Gitee/GitHub 个人设置，找到「SSH 公钥配置」，粘贴内容并保存；

4. 验证是否配置成功：ssh -T git@gitee.com / ssh -T git@github.com

### 5. 环境校验命令

```Plaintext
# 查看 Git 版本，验证安装成功
git --version

# 查看所有全局配置
git config --global --list
```

---

# 三、Git 核心概念与工作机制（不用死记命令）

### 1. Git 四大工作区域

所有命令都是围绕区域文件流转展开：

> - **工作区（Working Directory）**：本地项目文件夹，日常写代码、改代码的目录，肉眼可见文件。
> - **暂存区（Stage/Index）**：临时缓存区域，用于存放即将提交的代码，执行 git add 后文件进入暂存区。
> - **本地仓库（Local Repository）**：本地隐藏的 .git 文件夹，执行 git commit 后，暂存区文件永久存入本地仓库，生成版本快照。
> - **远程仓库（Remote Repository）**：云端仓库（Gitee/GitHub），用于团队共享、云端备份，执行 git push 后同步本地版本到云端。

<callout emoji="🔃">
**流转顺序**：工作区 → 暂存区 → 本地仓库 → 远程仓库
</callout>

### 2. 核心对象概念

> - **快照**：Git 核心存储方式，每一次 commit 都是一次完整项目快照，而非记录文件差异，回退版本速度极快。
> - **提交记录（commit）**：每一次版本保存的唯一记录，包含唯一 hash 值、作者、时间、修改说明，可精准定位每一次变更。
> - **分支（branch）**：独立的开发线路，互不干扰，支持多分支并行开发。
> - **标签（tag）**：用于标记正式版本（如 v1.0.0、v2.1.0），固定版本快照，不随代码迭代变更。

### 3. 文件状态完整流转

> - **未跟踪（Untracked）**：新建文件，未被 Git 管理，无任何版本记录。
> - **已修改（Modified）**：已纳入 Git 管理的文件，内容发生修改，未加入暂存区。
> - **已暂存（Staged）**：修改后的文件执行 git add，等待提交到本地仓库。
> - **已提交（Committed）**：执行 git commit，文件已永久存入本地仓库，生成稳定版本。

### 4. 版本控制核心原理

Git 采用**快照存储**，每次提交都会保存当前项目所有文件的完整快照，后续迭代仅记录变更文件，保留文件索引。优势：版本回退秒级完成、分支切换高效、数据完整性极高。

---

# 四、🏠本地仓库基础操作（个人开发必备）

### 1. 仓库初始化

#### 本地新建仓库

进入项目根目录，打开 Git Bash，执行初始化命令，生成隐藏 .git 文件夹，项目正式被 Git 管理：

```Plaintext
git init
```

#### 克隆远程仓库到本地

将云端已有仓库完整下载到本地，自动关联远程仓库：

```Plaintext
git clone 远程仓库地址
```

### 2. 文件基础操作

日常开发新增、修改、删除、重命名文件后，均需通过 Git 命令同步状态：

```Plaintext
# 删除文件（Git 同步删除状态）
git rm 文件名

# 重命名文件
git mv 旧文件名 新文件名
```

手动修改、新增文件无需单独命令，直接通过 add 命令纳入暂存即可。

### 3. 暂存与提交（核心高频操作）

#### 暂存命令 git add

```Plaintext
# 暂存单个文件
git add 文件名

# 暂存所有变更文件（日常开发最常用）
git add .
```

#### 提交命令 git commit

提交必须携带备注，清晰说明本次修改内容，方便后续追溯版本：

```Plaintext
git commit -m "本次修改说明：新增登录接口、修复首页样式bug"
```

![这张图片是一张趣味设计的火灾自救常识标识牌，将Git相关命令与火灾自救步骤做了结合。标识牌上方标注“火灾自救常识”，下方列出三条内容：第一条为带对应图标的“git commit”，第二条是带图标的“git push”，第三条为带图标且指向现实动作的“逃离建筑”，整体是用程序员常用的Git操作，戏仿表达火灾自救的核心步骤。该图片放置在Git使用指南中提交命令相关内容的位置，用趣味形式呼应Git操作的重要性，同时做出了将Git命令类比为自救步骤的创意解读。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODRjZjY3YzkwZTA5OWI5ZmFhODE4MWQ4MGQ4Yzk0N2VfMGJlYzFlZjE4Y2FhY2IxZTI0ZThlN2ExYmU3ODlkMDZfSUQ6NzY1ODM0MjEzODc3Mzc4NTU0NV8xNzg1ODMxNTc0OjE3ODU4MzUxNzRfVjM)

<callout emoji="👨‍💻">
规范要求：备注简洁精准，说明功能新增、问题修复、优化内容，禁止无意义备注（如 update、修改代码）。
</callout>

### 4. 状态与日志查看

```Plaintext
# 查看当前文件状态（是否修改、是否暂存、未跟踪文件）
git status

# 查看简洁版状态（精简展示）
git status -s

# 查看完整提交日志
git log

# 简洁单行展示所有提交记录
git log --oneline
```

### 5. 本地撤回操作（高频避坑）

#### 撤销工作区修改（未暂存）

```Plaintext
# 撤销单个文件修改
git checkout -- 文件名

# 撤销所有工作区修改
git checkout .
```

#### 取消暂存（已 add，未 commit）

```Plaintext
git reset HEAD .
```

#### 撤回本地提交（已 commit，未 push）

```Plaintext
# 保留修改内容，仅撤回提交记录（最常用）
git reset --soft HEAD~1

# 彻底撤回提交，删除本次修改内容（谨慎使用）
git reset --hard HEAD~1
```

---

# 五、🖥️远程仓库操作（对接 GitHub / Gitee / GitLab）

### 1. 远程仓库基础管理

```Plaintext
# 查看已关联远程仓库
git remote -v

# 关联远程仓库（本地新项目绑定云端仓库）
git remote add origin 远程仓库地址

# 解绑远程仓库
git remote remove origin

# 重命名远程仓库别名
git remote rename 旧别名 新别名
```

### 2. 核心推拉操作

#### 拉取远程代码 git pull

同步远程仓库最新代码到本地，解决本地版本滞后问题，开发前必执行：

```Plaintext
git pull
```

#### 推送本地代码 git push

将本地已提交的版本同步到远程仓库：

```Plaintext
# 首次推送需要指定分支
git push -u origin 分支名

# 后续推送直接使用
git push
```

### 3. 远程代码同步进阶

git pull 等价于 git fetch + git merge，如需手动精细化同步，可使用 fetch 命令（仅拉取代码不自动合并）：

```Plaintext
# 拉取远程最新版本到本地缓存
git fetch origin

# 合并远程代码到本地
git merge origin/分支名
```

<callout emoji="💾">
### 新项目推送远程完整流程
➡️本地初始化仓库：git init
↪️暂存所有文件：git add 
↪️首次提交：git commit -m "项目初始化，基础框架搭建"
↪️关联远程空仓库：git remote add origin 仓库地址
↪️首次推送：git push -u origin main
</callout>

---

# 六、🏘️分支管理（团队开发核心）

### 1. 分支类型核心概念

- **主分支（main/master）**：线上正式代码分支，保持稳定，禁止直接修改、直接提交。
- **开发分支（develop）**：日常迭代开发主干，汇总所有功能分支代码，测试无误后合并到主分支发布。
- **功能分支（feature/\*）**：单独开发新功能，一个功能对应一个分支，开发完成后合并到开发分支。
- **修复分支（bugfix/hotfix/\*）**：修复线上 bug，hotfix 用于紧急线上修复，bugfix 用于迭代 bug 修复。

### 2. 基础分支操作

```Plaintext
# 查看本地所有分支
git branch

# 查看所有远程分支
git branch -r

# 创建新分支
git branch 分支名

# 切换分支
git checkout 分支名

# 创建并直接切换到新分支（高频）
git checkout -b 分支名

# 重命名分支
git branch -m 旧分支名 新分支名

# 删除本地分支
git branch -d 分支名

# 删除远程分支
git push origin --delete 分支名
```

### 3. 分支合并与冲突原理

#### 分支合并方式

- **快速合并（Fast-forward）**：当前分支无新提交，直接移动分支指针，无合并记录，无冲突。
- **普通合并（Merge）**：两个分支均有新提交，生成新的合并提交记录，可能产生代码冲突。

<callout emoji="‼️">
#### 冲突产生原因
多人修改**同一个文件的同一行代码**，Git 无法自动判断保留哪段代码，因此触发冲突，需要人工手动解决。
</callout>

### 4. 代码冲突完整解决流程

1. 执行合并命令后提示冲突，打开冲突文件；

2. 文件中 <<< HEAD 为当前分支代码，>>> 为待合并分支代码；

3. 手动删除冲突标记，保留正确代码，删除冗余代码；

4. 保存文件，执行 git add . 暂存；

5. 执行 git commit 完成合并，无需加备注。

### 5. merge 与 rebase 区别与适用场景

> - **merge 合并**：保留所有分支提交记录，生成新合并节点，分支历史清晰，适合主干分支合并，缺点是提交记录较多、树形复杂。
> - **rebase 变基**：将当前分支所有提交平移到目标分支最新节点，提交记录线性整洁，适合功能分支同步主干代码，**禁止在公共主干分支使用**。

```Plaintext
# 合并分支
git merge 待合并分支名

# 变基同步主干代码
git rebase main
```

### 6. 远程分支管理

```Plaintext
# 拉取远程分支到本地
git checkout -b 本地分支名 origin/远程分支名

# 推送本地新分支到远程
git push origin 本地分支名
```

---

# 七、高阶技巧（提升开发效率）

### 1. stash 代码暂存（临时保存工作区）

> 开发到一半需要切换分支改 bug，不想提交半成品代码，使用 stash 临时保存工作区所有修改，切换分支无残留。

```Plaintext
# 临时保存所有修改
git stash

# 保存并添加备注
git stash save "临时保存用户模块开发代码"

# 查看所有暂存记录
git stash list

# 恢复最新暂存代码（保留暂存记录）
git stash apply

# 恢复并删除暂存记录
git stash pop

# 清空所有暂存记录
git stash clear
```

### 2. 版本回退三种模式

> 1. **soft 软回退**：仅撤回提交记录，代码修改保留在工作区，适合改错提交备注、多提交合并。
> 2. **mixed 混合回退（默认）**：撤回提交，代码退回暂存区。
> 3. **hard 硬回退**：彻底删除本次所有修改，数据不可逆，谨慎使用。

```Plaintext
# 软回退上一次提交
git reset --soft HEAD~1

# 硬回退到指定 commit 版本
git reset --hard 版本hash值
```

### 3. cherry-pick 跨分支迁移提交

> 将某一个分支的**指定单条提交记录**迁移到当前分支，无需合并整个分支，适配精准同步功能代码场景。

```Plaintext
git cherry-pick 目标提交hash值
```

### 4. 标签 tag 版本管理

> 用于标记项目正式发布版本，固定版本快照，不随迭代变更。

```Plaintext
# 创建轻量标签
git tag v1.0.0

# 创建带备注的附注标签
git tag -a v1.0.0 -m "正式版1.0.0发布"

# 查看所有标签
git tag

# 推送单个标签到远程
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

### 5. .gitignore 忽略文件配置

> 新建 .gitignore 文件，配置无需提交的文件/文件夹，避免日志、缓存、配置隐私文件上传远程仓库。

常用忽略规则模板：

```Plaintext
# 日志文件
*.log

# 缓存文件夹
node_modules/
dist/
build/

# 系统文件
.DS_Store
Thumbs.db

# 环境配置文件
.env
.env.local
```

### 6. 命令别名配置

> 简化高频长命令，提升操作效率：

```Plaintext
# 简化查看日志
git config --global alias.lg "log --oneline --graph"

# 简化暂存提交
git config --global alias.cm "commit -m"

# 简化拉取代码
git config --global alias.pul "pull"
```

---

# 八、🏢团队协作标准流程（企业通用规范）

### 1. 主流分支工作流

#### GitHub Flow（轻量简洁，适合敏捷开发）

> 核心逻辑：基于 main 分支拉取功能分支，开发完成后提 PR 合并主干，审核通过合并、删除功能分支，流程轻量化、迭代速度快。

#### GitFlow（规范严谨，适合版本迭代项目）

> 核心分支：main（正式）、develop（开发）、feature（功能）、hotfix（紧急修复），严格区分开发、测试、发布分支，适合大型项目、版本化迭代产品。

### 2. 多人协作完整标准流程

- [ ] 1. 开发前：git pull 拉取远程最新代码，保证本地版本最新；

- [ ] 2. 新建专属功能分支：git checkout -b feature/xxx功能；

- [ ] 3. 本地开发、调试、自测；

- [ ] 4. 频繁小批量提交，填写规范备注；

- [ ] 5. 开发完成后，再次 pull 同步主干代码，解决本地冲突；

- [ ] 6. 推送本地功能分支到远程；

- [ ] 7. 提交 PR/MR，等待代码评审；

- [ ] 8. 评审通过后合并到开发/主干分支，删除废弃功能分支。

### ❗️PR/MR 代码评审规范

- 提交合并时清晰填写：开发功能、修改点、测试范围、注意事项；
- 禁止一次性提交大量代码，小迭代、小合并、高频提交；
- 评审重点检查：代码规范、逻辑漏洞、安全问题、性能问题。

### ❗️ 团队协作核心避坑要点

- 禁止直接在 main/develop 主干分支开发、提交代码；
- 开发前必须拉取最新代码，避免版本滞后导致大规模冲突；
- 公共分支禁止使用 rebase 变基，仅个人功能分支使用；
- 禁止强制推送主干分支（git push -f）。

# 九、⚠️常见问题排查与避坑指南（高频报错解决方案）

![图片是一张红色背景的宣传画，画面中有三名身着军装、手持步枪的士兵，其中一人指向远方。画面下方有白色大字“一不怕苦 二不怕死”，以及红色大字“时刻准备为宕机背锅”。该图片位于文档中“常见问题排查与避坑指南”部分，用以幽默地表达在Git使用中遇到问题时，应保持积极态度，勇于面对困难，与文档中解决推送报错等常见问题的指导相呼应。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MDJkM2EwMWUzN2E2YTYxYzcyODFlNjE1YjgzN2MxZmRfNWZlMTk3NmFkZmVkYWQ4YjYwZWM0MjdlMGE1YzAzYjJfSUQ6NzY1ODM0MDAzMjg1NTU0Mjk2OV8xNzg1ODMxNTc0OjE3ODU4MzUxNzRfVjM)

### 1. 推送报错问题

#### 远程代码冲突报错

原因：本地版本落后远程，远程已有新代码，解决方案：先 git pull 拉取合并，解决冲突后再推送。

#### 权限不足/密钥失效

原因：SSH 密钥过期、未配置、账号无仓库权限，解决方案：重新生成配置 SSH 密钥，联系管理员开通权限。

### 2. 误操作撤回修复

#### 误提交敏感代码

立即使用 git reset 回退版本，修改敏感信息后重新提交，若已推送远程，需同步清理远程版本记录。

#### 误合并代码

使用 git revert 撤销合并提交，生成新的反向提交，不破坏原有版本记录，适合公共分支修复。

### 3. 分支异常问题

#### rebase 变基失败

大概率是代码冲突，解决冲突后执行 git rebase --continue，如需终止变基执行 git rebase --abort。

#### 分支错乱、版本滞后

清理无效本地分支，git fetch origin --prune 同步删除远程已废弃分支，保持本地分支整洁。

### 4. 其他高频问题

- 文件不跟踪：检查是否被 .gitignore 忽略，取消忽略后重新 add；
- 提交记录错乱：禁止跨分支随意 cherry-pick，规范分支开发流程；
- 仓库同步失败：检查网络、仓库地址、账号权限。

---

# 十、Git 规范化使用规范（企业落地标准）

### 📖 Commit 提交信息规范

统一格式：【类型】具体描述，简洁清晰，语义化提交

- feat：新增功能
- fix：修复 bug
- opt：代码优化、性能优化
- docs：文档修改
- style：样式、格式调整，无代码逻辑变更
- refactor：代码重构
- test：新增测试代码

<callout emoji="👨‍💻">
示例：feat: 新增用户登录注册功能、fix: 修复列表分页异常bug
</callout>

### 🖋️分支命名规范

- 功能分支：feature/模块名-功能名 例：feature/user-login
- bug修复分支：bugfix/问题描述 例：bugfix/list-page-error
- 紧急线上修复：hotfix/线上问题 例：hotfix/login-token-expire
- 测试分支：test/迭代版本 例：test/v1.1.0

### ✒️版本标签命名规范

采用三段式版本号：主版本.次版本.修订版本

- 主版本：整体架构、重大功能迭代变更
- 次版本：新增功能、模块迭代
- 修订版本：bug修复、小优化

<callout emoji="👨‍💻">
示例：v1.0.0（初始版本）、v1.1.1（小优化修复）
**王叔**注：文档主页的更新日志并没有按照命名规范来，而是按照日期，在此承认错误，但是不改
</callout>

### 4. 🚫团队协作禁忌操作

- 禁止在主干分支直接开发、提交代码；
- 禁止随意强制推送代码**（git push -f）**；
- 禁止提交无意义备注、大批量一次性提交；
- 禁止在公共分支使用 rebase、reset 高危操作；
- 禁止上传隐私配置、密钥、日志、依赖包文件。

![图片是一张卡通风格的图片，上方文字为“GIT PUSH ORIGIN MASTER --FORCE”。画面中，汤姆猫和杰瑞猫坐在沙发上，汤姆猫戴着一顶蓝色帽子，杰瑞猫戴着一顶黄色帽子，两人面露惊讶之色。这张图片被用作禁止随意强制推送代码（git push -f）的警示图，与文档中“团队协作禁忌操作”部分内容相关，直观地传达了该操作可能带来的风险，提醒团队成员在Git操作时应避免此类高危操作。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTJlNzJmNThjMWM1MWJkMzUyMjk0OWQ2MzI2NjVjMWFfMDU1MmIwOTU2OGJiODVjNDZiYWUwYWM3NjA4MjE5MzNfSUQ6NzY1ODM0MTQ0ODA4OTIxMDA0MV8xNzg1ODMxNTc0OjE3ODU4MzUxNzRfVjM)

---

# 十一、附录：高频命令速查表

### 1. 基础操作命令

```Plaintext
git init                  # 初始化本地仓库
git add .                 # 暂存所有文件
git commit -m "备注"      # 提交代码
git status                # 查看文件状态
git log                   # 查看提交日志
git checkout .            # 撤销工作区修改
git reset HEAD .          # 取消暂存
```

### 2. 分支与远程操作命令

```Plaintext
git branch                # 查看本地分支
git checkout -b 分支名    # 新建并切换分支
git pull                  # 拉取远程代码
git push                  # 推送代码
git remote -v             # 查看远程仓库
git merge 分支名          # 合并分支
```

### 3. 高阶与问题修复命令

```Plaintext
git stash                 # 临时暂存代码
git reset --soft HEAD~1   # 软回退提交
git reset --hard 版本号   # 硬回退指定版本
git cherry-pick hash值    # 迁移指定提交
git tag                   # 查看版本标签
git rebase --continue     # 继续变基
git rebase --abort        # 终止变基
```

<callout emoji="😀">
真不愧是我们暨大刀枪炮--薛总，太管用了
</callout>

---

<callout emoji="🐳"><h3>返回导航页：<cite doc-id="VvKVwsHo2iIIC4ko0PmcKs4lnKd" file-type="wiki" title="信科院-从入学到被开除" type="doc"></cite></h3></callout>
