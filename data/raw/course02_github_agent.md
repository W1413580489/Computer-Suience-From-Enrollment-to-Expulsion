## 前置教程：申请 GitHub Token

你的 Agent 需要读取 GitHub 仓库信息。GitHub 对匿名访客限制每小时 60 次请求，分析一个仓库就要用掉十几次；申请免费的 Personal Access Token 后限额提升到每小时 5000 次。申请路径：登录 GitHub → 右上角头像 → Settings → 左侧最底部 Developer settings → Personal access tokens → Tokens (classic) → Generate new token (classic)。Note 填 agent-course，Expiration 选 90 days，权限只勾 public_repo（本课程只读公开仓库，权限越少越安全），点 Generate token 后立刻复制保存——Token 只显示这一次。三条安全铁律：一、Token 绝不写进源代码，放 .env 文件且 .gitignore 必须包含 .env；二、代码里用 os.getenv("GITHUB_TOKEN") 读取；三、发现泄露立即回到 Tokens 页面点 Revoke 作废并重新生成。常见报错：401 是 Token 错或过期，重新生成；403 且响应头 X-RateLimit-Remaining 为 0 是限流，确认带 Token 后稍等；404 是仓库不存在或非公开，确认地址格式为 github.com/用户名/仓库名。验证方法：curl -H "Authorization: Bearer 你的Token" https://api.github.com/user，返回里能看到你的登录名即成功。

## T01 认识 Agent 与项目骨架

上一课你做的聊天机器人是"一问一答"：用户说话，模型回答，结束。Agent 的本质区别有三点：第一，它能**调用工具**——模型自己决定"我需要先查一下数据"；第二，它能**多步执行**——查完一步还能根据结果决定下一步；第三，它能**自主决策**——你给它目标，它自己规划路径。本课程的目标就是让你亲手做出这样一个 Agent，而不是调用别人的框架。项目骨架包含四个文件：agent.py（主循环与 LLM 调用）、tools.py（工具函数）、.env（存放 LLM API Key 和 GitHub Token，绝不进代码）、requirements.txt（依赖清单）。最小示例：agent.py 先实现"读输入、调 API、打印回答"，这就是你上一课的后端逻辑，只是搬进了命令行。常见坑：把 API Key 直接写在代码里提交到 GitHub——这是安全问题，验收会查；正确做法是 .env 加 python-dotenv 的 load_dotenv()，再用 os.getenv 读取。完成标准：CLI 运行后输入问题能打印回答，且 .gitignore 包含 .env。

## T02 最小 Agent Loop

让模型"会用工具"的关键是请求里多一个 tools 参数，告诉模型有哪些工具可用。以 OpenAI 兼容接口为例，请求体形如：`{"model": "deepseek-chat", "messages": [...], "tools": [{"type": "function", "function": {"name": "get_current_time", "description": "获取当前时间", "parameters": {"type": "object", "properties": {}}}}]}`。如果模型决定调用工具，响应里会出现 `choices[0].message.tool_calls`（含 name 和 arguments）。此时**不要直接打印回答**，而是：本地执行工具 → 把结果作为一条 `role=tool` 的消息追加进 messages → 再次调用模型，它就能基于工具结果给出最终回答。这个"调用→执行→回传→再调用"的闭环就是最小的 Agent Loop。常见坑：一，忘记把 assistant 的 tool_calls 消息本身也追加进 messages，导致回传时对不上号；二，把工具结果直接打印给用户就结束了——模型根本没看到结果。本任务只做一个工具，重点是跑通闭环，并用 --trace 参数把每一步写入 agent_trace.json，从现在开始养成留证据的习惯。

## T03 GitHub API Client 与 Token 限流

所有 GitHub 请求都应经过一个统一的 GitHubClient 类，而不是在各个工具里裸写 httpx。Client 的职责：自动加请求头 `Authorization: Bearer <你的Token>`；把三类错误区分开——401（Token 无效或过期，提示重新生成）、403 且响应头 X-RateLimit-Remaining 为 0（限流，读 Retry-After 头等待后重试一次）、404（仓库或路径不存在）；任何错误都以 `{"ok": false, "code": "...", "error": "..."}` 结构返回，绝不静默吞掉。示例响应头关键字段：`X-RateLimit-Remaining: 4999`、`X-RateLimit-Reset: 1700000000`（Unix 时间戳，限额重置时间）。常见坑：一，重试不设次数导致无限循环；二，把错误直接 raise 出去导致整个 Agent 崩溃——正确做法是把错误信息返回给 Agent，让它自己调整。本任务同时要求单元测试：用 mock 模拟 401/403/404 三种响应，不真调 API（快、稳定、不吃额度）。

## T04 仓库信息与文件树工具

两个只读工具是分析仓库的"眼睛"。get_repo_info 调用 `GET /repos/{owner}/{repo}`，从返回 JSON 中抽取关键字段：language（主语言）、stargazers_count（star 数）、description（描述）、default_branch（默认分支）、updated_at。get_file_tree 调用 `GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1`，返回 JSON 的 tree 数组里每个元素有 path 和 type（blob 是文件、tree 是目录）——只保留文件，按路径排序，超过 200 项截断并注明"共 N 项，已截断"。截断是必须的：大仓库的文件树有几万项，全塞给模型既浪费 token 又降低分析质量。常见坑：一，branch 写死 main——应该先用 get_repo_info 拿 default_branch；二，tree 返回 truncated 字段为 true 时说明 GitHub 侧已截断，要提示用户仓库过大。两个工具都要有 mock 单测。

## T05 文件内容工具与大小保护

get_file_content 调用 `GET /repos/{owner}/{repo}/contents/{path}?ref={branch}`，返回 JSON 的 content 字段是 base64 编码的文件内容，用 `base64.b64decode(content).decode("utf-8", errors="replace")` 解码。三条保护路径：一，行数超过 200 行就截断，末尾追加"（已截断，仅显示前 200 行，共 N 行）"——上下文是有限资源，把大文件全塞给模型既贵又降低分析质量；二，二进制文件（解码失败或 content 为空）返回"（二进制文件，无法显示）"；三，文件不存在返回"（文件不存在）"。常见坑：一，忘记 errors="replace"，遇到非 UTF-8 字节直接抛 UnicodeDecodeError；二，把整个文件原样返回，没截断。三条路径都要有 mock 单测：正常文件、超长文件、不存在的路径。

## T06 工具注册与 Schema

现在把散落的工具统一管理。核心是一个注册表：`TOOL_MAP = {"get_repo_info": (get_repo_info, schema1), ...}`，外加一个 schemas 列表传给 API。Schema 里的 description 字段**是写给模型看的**——模型靠它决定"什么问题用什么工具"，所以描述要写清楚工具做什么、什么时候该用。比如 get_file_tree 的描述："列出仓库的完整文件结构，用于了解项目组成；在读取具体文件前应先调用本工具"。参数设计要尽量简单：本课程的工具只需要 owner/repo（可合并为一个 repo 参数）和 path。常见坑：一，描述含糊（"获取数据"）导致模型乱选；二，工具函数直接散在 agent.py 里用 if-else 调用——扩展新工具要改多处。验证方式：用三类不同的问题（问语言、问结构、问文件内容）测试模型是否每次都选对工具，并把轨迹留档。

## T07 多步 Agent Loop

真正的 Agent 分析一个仓库不会只调一次工具：先 get_repo_info 看概况 → get_file_tree 看结构 → get_file_content 读关键文件——每一步都依赖前一步的结果。实现方式是把单次调用改成 while 循环：每次响应里有 tool_calls 就执行、以 role=tool 回传、继续循环；响应里没有 tool_calls（模型给出最终回答）就结束。每一步都要写进 trace：step（步数）、tool_name、arguments、result_summary（结果摘要，比如"获取到 85 个文件"而不是全文）、timestamp。常见坑：一，循环里忘记 append assistant 的 tool_calls 消息，导致 API 报错 messages 格式不对；二，result_summary 塞了整个文件全文，trace 变得巨大。验证标准：找一个真实仓库跑"分析项目结构"，trace 里应出现至少 2 次连续、且相互依赖的工具调用——这就是"自主性"的证据。

## T08 max_steps 与安全退出

不给 Loop 设上限的后果有两个：模型陷入重复调用同一工具的死循环，token 消耗失控。三个安全机制：一，`for step in range(max_steps)`（默认 10）替代裸 while，步数耗尽时写 stop_reason 为 max_steps_reached，输出已收集的部分结果并提示"已达步数上限"；二，工具执行包 try/except——工具报错时把错误文本作为结果回传给模型（比如"404 文件不存在"），模型会自己调整换一个文件，Agent 整体不崩溃；三，stop_reason 三种取值：completed（模型给出最终回答）、max_steps_reached（超限安全退出）、error（致命错误）。常见坑：异常直接 raise 导致 CLI 崩溃退出，前面收集的信息全部丢失。单测用 mock：让工具永远抛异常，验证 Loop 在 max_steps 后正常退出且 trace 完整。

## T09 带证据的分析报告

最终交付物：`report.md` + `agent_trace.json`。报告四部分：仓库概况（来自 get_repo_info）、结构分析（来自 get_file_tree）、关键文件解读（来自 get_file_content）、结论与建议。核心要求是**证据可追溯**：报告中每个关键结论都要标注来源，格式如"主语言为 Python [见 trace step 1]"——读者拿着 trace 就能验证你的 Agent 真的读过这个仓库，而不是模型编的。实现要点：在 Loop 结束后，让模型基于完整 messages 历史生成报告（追加一条 user 消息："请把以上分析整理成 Markdown 报告，结论标注 [见 trace step N]"）；trace 和报告一并保存。常见坑：一，报告结论与仓库事实不符（模型幻觉）——追溯机制就是为了抓住这一点；二，报告没有引用任何 step，等于没有证据链。写 README 说明运行方式是加分项但不是验收必需——验收看的是报告质量和证据链。
