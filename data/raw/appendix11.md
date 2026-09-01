# 全流程踩坑复盘

本节基于 2026-08-04 至 08-14 的完整开发日志，按阶段复盘每个坑的现象、根因和避坑方法。

### 需求与设计阶段（5 坑）

**坑 1：需求文档与代码脱节 12 项。** 文档写 `--accent-yellow`，代码已删；文档列了不存在的组件 NewsView；模型名写 DeepSeek-V4，实际是 deepseek-chat。根因是文档更新滞后于代码迭代。每次功能迭代后，同步过一遍需求文档（token 表、组件目录、路由表、模型名、里程碑状态）。

**坑 2：改版方向漂移（AI Slop）。** 首页按 AI 自由发挥，用户反馈"哪里都不对"。根因是没有先对齐视觉方向就写代码。先出静态 mockup（HTML 预览）→ 用户确认 → 再重构，参考权威设计稿逐条落地。

**坑 3：UI 审计暴露的基础问题。** 对比度 3:1 不达 WCAG AA、无 `:focus-visible`、清空会话无二次确认、Google Fonts 国内不可达、立绘 1.5MB。上线前做一轮 UI 审计，P1 五项必修：对比度、焦点样式、误操作确认、字体自托管、图片压缩。

**坑 4：全局 zoom 放大方案不可用。** `.hud-root` 固定 100vh，zoom 放大导致 flex 两端元素被裁剪。改用系统性放大 px/clamp 数值（约 15%），不用 CSS zoom。

**坑 5：设计 Token 冗余。** `--accent-yellow` 与 `--amber` 两套琥珀、`--accent-green` 与 `--success` 重复。统一单一语义 token，硬编码 rgba 全部提为 token。

### 前端开发阶段（7 坑）

**坑 6：Vue 响应式陷阱（最痛，问答永远空白）。** SSE 流式内容实际已写入后端日志，但前端永远显示空白光标。根因是 chatStore 中 `assistantMsg` 是普通对象引用，SSE 回调直接 `assistantMsg.content += ...` 绕过 Vue 3 Proxy，不触发 UI 更新。所有状态修改必须走 store 的响应式引用，不要持有裸对象引用后直接改。

**坑 7：vite build 清空 dist 被拦截。** safe-delete 拦截 `dist` 清理报错。`rm -rf dist` 后再 `npm run build`。

**坑 8：vue-router 版本坑。** 4.6.4 在 Edge 最小化后卡死。锁稳定版本 4.5.1，引入新依赖时留意版本已知问题。

**坑 9：Markdown callout 渲染被 HTML escape 破坏。** `:::callout` 转义后变成裸文本。先用 `@@CALLOUT_N@@` 占位符避开 escape 阶段，渲染末尾再还原。

**坑 10：文件被外部删除导致构建失败。** NewsView.vue 等被删但 HomeView 仍引用。删除组件时同步清理引用，会话间检查构建产物。

**坑 11：body overflow:hidden 锁死页面滚动。** 全局 `body{overflow:hidden}` 导致校历页无法滑动。长页面用自容器滚动（`height:100dvh` + 内部 `overflow-y:auto`）。

**坑 12：Teleport 弹窗不显示。** 设置弹窗用定位样式 + nextTick 控制，首帧 style 为空导致不可见。用 `<Teleport to="body">` + 独立遮罩层居中，不依赖计算定位。

### 后端检索阶段（4 坑）

**坑 13：BM25 对中文疑问词不敏感。** "今天天气怎么样"得分也高，拒答逻辑失效。`is_relevant` 双重拒答 = top1 得分 ≥ 阈值且查询长内容词（≥2 字非停用词）至少命中一个召回块。

**坑 14：虚词高分 / 话痨文档霸榜。** 情感指南文风话痨，高频虚词（了/会/能/吗）对任何疑问句都拿高分，霸占 top-8。打分用过滤停用词后的 `content_tokenize`；扩展停用词表；top-64 候选后按文档去重（每文档最多 2 块）；score ≤ 0 的块直接丢弃。

**坑 15：查询口语化无法匹配。** "咋保研""奖学金怎么拿"匹配不到标准术语。查询规范化正则（口语→标准术语）+ 同义词扩展（保研→推免→推荐免试）。

**坑 16：启动期首个请求慢。** BM25 初始化 ~600ms，首个请求等待。FastAPI startup 事件预热 `Retriever.get()` + httpx 连接池复用。

### 部署上线阶段（12 坑，最惨烈）

**坑 17：核心数据文件被 .gitignore 排除。** `*.jsonl` 把 `data/chunks.jsonl`（306KB 检索库）排除 → 服务器检索库为空，无法回答。加 `!data/chunks.jsonl` 例外；部署前 git 体检。

**坑 18：缺 requirements.txt。** 后端依赖清单化，Python ≥ 3.10。

**坑 19：修复文件从未提交。** UI 审计修复的 22 个文件全未 commit，服务器拉到旧版。修复完成后立即 `git add -A && git commit && git push`。

**坑 20：AL3 默认 Python 3.6。** 3.6.8 无法装 fastapi/pydantic v2。`dnf install -y python3.11`，用 `python3.11` 建 venv。

**坑 21：dnf exclude nginx 导致 git 也没装上。** `dnf install ... nginx` 整个事务失败，连带 git 装不上 → 后续 clone 全部失败，venv/.env 建错到 /opt 根目录，PM2 errored（重启 15 次）。git 单独装 `dnf install -y git`；nginx 用 `--disableexcludes=main`。

**坑 22：venv/.env 建错位置。** clone 失败后手动建 venv，实际建到 `/opt` 根目录。`rm -rf /opt/venv /opt/.env` → 重新 clone → 正确路径重建。

**坑 23：firewalld 未放行自定义端口（最终网络根因）。** 安全组 8000 OK、实例绑定 OK、服务监听 OK，外部仍连不上。AL3 默认 firewalld active，白名单只有宝塔预设端口。`firewall-cmd --permanent --add-port=8000/tcp && firewall-cmd --reload`。三层防火墙逐层排查：安全组 → firewalld/iptables → 应用层。

**坑 24：NAT hairpin 误导排障。** 服务器内 curl 自己公网 IP 超时，误判为不通。NAT hairpin 测试不可信，外部视角用手机 4G/5G 流量测试。

**坑 25：PM2 fork 模式 bash 包装层。** 整体引号 `pm2 start "venv/bin/uvicorn ..."` → status online + 138MB 内存，但 `ss -tlnp` 无监听、外部 REFUSED。PM2 起非 Node 进程必须 `--interpreter none` + `--` 直起二进制。

**坑 26：服务器 1G 内存构建 OOM。** 本地构建 `npm run build` → 同步 dist 到服务器；或加 2G swap。

**坑 27：scp 不清理旧文件。** dist/assets 累积 14 个历史 HomeView-*.js。先 `rm -rf` 远端 dist 再上传；用 tar 管道 `tar czf - . | ssh ... 'tar xzf - -C <dir>'`（Git Bash 无 rsync 时）。

**坑 28：SSH 中文用户名路径乱码。** Git Bash 把中文用户名「王凌骏」解析成 GBK 路径，找不到 key。显式 `-i "C:/Users/王凌骏/.ssh/id_ed25519"` + `-o UserKnownHostsFile=/dev/null`；`.env` 排除在同步之外保护平台 Key。

### 运维与内容更新阶段（5 坑）

**坑 29：备案状态决定访问方式。** 大陆节点未备案 → 80/443 被机房拦截，只能 `http://IP:8000`；微信内置浏览器强制 HTTPS 打不开。备案前用 IP:8000 + 普通浏览器测试；备案流程与开发并行（1-3 周）。

**坑 30：飞书内容更新未同步。** guide01 新增「新玩家账号登录」整章、guide07/appendix02 有更新，本地旧数据不命中。改文档后重新拉取 → `scripts/chunker.py` 重新分块（404→410）→ 同步部署 → 验证 health chunks 数。

**坑 31：更新部署后未验证。** 每次部署后验证三件事：`/api/health`（chunks 数量正确）、站点 HTTP 200、PM2 online。

**坑 32：字体 CDN 国内不稳。** Google Fonts / 外链字体加载超时 → 闪烁。字体自托管 woff2 或切换国内镜像。

**坑 33：更新日志漏维护。** 每次发版同步更新 `data/changelog.json`（版本号/日期/变更要点 ≤5 条）。

### 模型接入与部署同步阶段（7 坑）

> 本阶段坑全部来自"优化问答机器人 + 纯 BYOK 上线"迭代。表面症状都是"提问没回复"，实际是三条不同链路断裂：前端没发出、模型名对不上、前端修复没到服务器。

**坑 34：crypto.subtle 在非安全上下文不可用（前端请求静默失败）。** 填了 Key，提问后前端毫无反应；后端日志连 `POST /api/ask` 都没有。根因是 `crypto.subtle.digest`（Web Crypto API）只在安全上下文（https 或 localhost）可用；纯 BYOK 站点用 `http://IP:8000` 时 `crypto.subtle` 是 `undefined`，`sha256Short()` 抛异常，`ask()` 卡在 `await` 处，`fetch` 根本没发出。用 Web Crypto 前判断 `crypto?.subtle` 是否存在，非安全上下文降级为纯 JS 哈希（如 FNV-1a）。"请求没到后端"第一步先查浏览器 Console 是否抛异常。

**坑 35：模型名失效（deepseek-chat 已废弃）。** `/api/verify` 显示"连接成功"，但提问后长时间无回复。根因是 DeepSeek `/v1/models` 现只返回 `deepseek-v4-flash` / `deepseek-v4-pro`，旧的 `deepseek-chat` 已下线；`verify` 走 `/models`（不校验模型名）所以"成功"，`ask` 走 `/chat/completions` 带无效模型名 → 卡住。`/models` 验证通过 ≠ 模型可用。接入新模型直接 `curl /chat/completions` 用真实模型名跑一次。

**坑 36：frontend/dist 被 gitignore 排除（最痛，前端修复全失效）。** 修完前端（crypto 降级、模型名），本地 build 成功、push、服务器 pull 重启后，浏览器仍报旧错误、加载旧 bundle 文件名。根因是 `.gitignore` 里 `frontend/dist/` 被排除 → git 不带 dist；服务器无 Node.js 无法本地 build，一直跑部署初期上传的旧 dist。**本地 build 成功 ≠ 服务器更新。** 服务器无 Node 环境时 dist 必须入库（`.gitignore` 加 `!frontend/dist/` 例外）；部署后 F12 Network 确认加载的 bundle hash 是否为最新。

**坑 37：pm2 logs | grep 挂起阻塞后续命令。** 跑 `pm2 logs xkz --lines 0 --raw | grep "..."` 后命令不退出（grep 一直等匹配），占着前台，后续命令全被阻塞。用 `--lines N`（有限行）替代 `--lines 0`，或记住 `Ctrl+C` 退出。

**坑 38：git pull 与 scp 文件冲突。** 服务器 `git pull` 报 `Your local changes to data/chunks.jsonl would be overwritten by merge`。根因是之前 scp 上传过 chunks.jsonl，服务器工作区有未提交改动。`git checkout -- data/chunks.jsonl && git pull` 丢弃本地改动；尽量不 scp 覆盖 git 已跟踪文件。

**坑 39：本地 SSH 直连 ECS 失败。** 本地 `scp`/`ssh root@IP` 报 `Permission denied (publickey)`。根因是之前部署走阿里云 Workbench 网页终端（密码登录），本地没配对应 SSH key。若要本地自动化部署，先在 ECS 配置本地公钥；否则统一走 Workbench 手动执行，别混用两套路径/凭据。

**坑 40：浏览器顽固缓存。** `Ctrl+Shift+R` 强刷后仍加载旧 bundle（F12 Network 看到旧 hash 文件名）。根因是浏览器磁盘缓存/Service Worker 顽固。无痕模式（Ctrl+Shift+N）验证；用 F12 Network 确认 bundle hash 是否最新（这是判断"到底加载了哪版"的唯一硬证据）。

## 提前准备清单（照做避坑）

### 开发前

- [ ] 写需求文档（PRD）：一句话定位 / 核心价值 / ICP / FR 编号 / NFR / 数据模型 / API / Prompt
- [ ] 明确数据存储方式（禁假数据）
- [ ] 先出静态 mockup 对齐视觉方向，再写代码

### 写代码时

- [ ] 所有状态修改走 store 响应式引用，不持有裸对象引用
- [ ] BM25 类检索：停用词过滤 + 文档级去重 + 双重拒答
- [ ] 依赖锁稳定版本（vue-router 4.5.1 等已知坑）
- [ ] 每完成一个功能：真实验证（发布数据 → 刷新 → 数据还在）+ 乱点五分钟

### 上线前

- [ ] **git 体检**：requirements.txt 存在 / 数据文件未被 ignore / 工作区无未提交
- [ ] **dist 是否入库**：服务器无 Node 时，`frontend/dist` 必须在 `.gitignore` 放行，否则前端修复永远到不了服务器
- [ ] UI 审计一轮：对比度 ≥4.5:1、:focus-visible、误操作二次确认、字体自托管、图片压缩
- [ ] 本地构建成功 → 提交 → 推送

### 部署时

- [ ] 服务器装好 Python3.11 + git（单独装）+ swap
- [ ] PM2 用 `--interpreter none` 直起 uvicorn
- [ ] firewalld 放行 8000 + 安全组核对实例绑定
- [ ] 手机 4G 测外部视角（NAT hairpin 不可信）
- [ ] 保护服务器 `.env`（不同步覆盖）

### 部署后

- [ ] health API：chunks 数量 / platform_key_configured 状态
- [ ] **F12 Network 确认浏览器加载的 bundle hash 是最新**（本地 build 成功 ≠ 服务器更新 ≠ 浏览器加载新版）
- [ ] **接新模型**：`curl /chat/completions` 用真实模型名测一次，别只信 `/models` 返回"成功"
- [ ] **纯 BYOK + http://IP 站点**：确认前端不依赖 `crypto.subtle`（非安全上下文 undefined），否则降级为纯 JS 哈希
- [ ] 更新 changelog.json
- [ ] 更新需求文档（token/组件/路由/模型名）

## 可复用结论

1. **部署失败链几乎总是"小坑连锁"**：git 没装上 → clone 失败 → venv 建错 → PM2 崩 → 排查半天。打破链条 = 部署前体检。
2. **改完不验证 = 白改**：前端响应式、弹窗、滚动、检索质量，全是"日志正常但界面异常"的隐性 bug。
3. **方向比速度重要**：先 mockup 后重构，避免 AI Slop 返工。
4. **国内环境三件套**：字体自托管、镜像源（npmmirror/阿里云 pip）、备案意识。
5. **文档是项目的一部分**：需求文档、部署手册、复盘报告、changelog 四件套随代码维护。
6. **"没回复"要拆三层查**：请求到没到后端（看日志/Network）、模型名对不对（curl /chat/completions）、前端有没有抛异常（Console）。同一症状，三个不同根因。
7. **前端改动要"端到端"验证**：本地 build → 服务器真拿到新 dist → 浏览器真加载新 hash，三步缺一不可。

## 从 0 到 1 的全流程总结

第 1 步：写需求文档
  └─ 用模板（第一章），把"想做什么"写清楚
  └─ 每条需求编号，每个数据结构给 JSON 示例

第 2 步：做视觉交互方案
  └─ 用模板（第二章），定义 Token、布局、组件、状态机
  └─ 先出 ASCII 布局图，再写代码

第 3 步：开发
  └─ 前后端按需求编号逐条实现
  └─ 前端用设计 Token 保证一致性
  └─ 警惕 Vue 响应式陷阱（第六章坑 6）
  └─ 检索注意停用词过滤 + 文档去重（第六章坑 13-16）

第 4 步：UI 审计
  └─ 用 Nielsen 10 启发式逐项检查
  └─ 修复 P1 问题再上线（第六章坑 3）

第 5 步：部署
  └─ 用模板（第四章），先做 git 体检再碰服务器
  └─ 三层防火墙逐层排查（第六章坑 17-28）
  └─ 部署后验证三件事：health / HTTP 200 / PM2 online

第 6 步：迭代
  └─ 每轮只改 3-5 个点，改完立刻部署验证
  └─ 视觉重构时先出 Mockup 确认方向（第六章坑 2）

第 7 步：沉淀
  └─ 更新需求文档、changelog、部署手册
  └─ 对照第七章检查清单，确保没有遗漏

---

*本文档基于「信科院智能助手（XKZ-Agent）」项目的完整开发与部署经验编写。项目从 2026 年 7 月启动，经历需求文档编写、Vue 3 + FastAPI 开发、BM25 RAG 检索、阿里云 ECS 部署、UI 工程审计、游戏化改造、ZZZ 风格视觉重构等完整流程，最终上线于 http://jnuxky.xyz（备案中，临时访问）。*