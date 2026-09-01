# BUG: 评审仍要求截图 + GitHub 仓库无法读取

## 现象（线上 jnuxky.xyz/teach，Reviewer 模式）

用户提交 GitHub 仓库链接 `https://github.com/W1413580489/chatbot-wrapper-test` 后，
AI 回复：

> "你提供了仓库链接，但我无法直接读取 GitHub 仓库里的代码内容，所以不能凭空评估。
> 请把关键证据直接发在对话里：1) 前端页面截图或录屏；2) 消息滚动截图；
> 3) 后端代码和前端代码片段；4) 数据流向说明。
> 没有这些证据，我无法对照验收标准给出真实结论。"

**两个问题均未修复：**
1. 仍然要求截图/录屏作为评审证据
2. GitHub 仓库链接提交后无法读取代码

## 已做的本地修改（2026-08-27）

以下文件已在本地 `d:\Assistant\tralis\xkz-agent\ai_engine\` 修改过：

| 文件 | 修改内容 |
|------|---------|
| `course_data.py` | 所有 Rubric 的 `required_evidence` 移除 `screenshot`；`task_review.evidence_required` 改为 `"code"` |
| `review.py` | `collect_evidence` 移除截图收集；prompt 铁律第3条移除截图引用；CI 部分移除截图引用 |
| `prompts.py` | Debugger 模式第2步移除"是否有截图" |
| `testpage.html` | 评审面板移除截图文本域 |

## 部署情况

- ai_engine 12 个 .py 文件已通过 scp 上传到服务器 `/opt/xkz-agent/ai_engine/`
- 后端用 pm2 运行（进程名 `xkz-ai`，端口 8099，interpreter: backend venv python）
- Nginx `/api/ai/` 反代到 8099 已配置
- `/api/ai/config` 接口可正常访问

## 排查方向

### 问题1：截图要求仍在
- 检查服务器上 `/opt/xkz-agent/ai_engine/course_data.py` 是否确实是最新版本（`required_evidence` 不含 `screenshot`）
- 检查 pm2 进程是否加载了最新代码（`pm2 restart xkz-ai`）
- 检查 `review.py` 的 `build_review_system_prompt` 生成的 prompt 是否还包含截图关键词
- 注意：`prompts.py` 中的 Coach 模式 prompt 可能也硬编码了截图要求，需要一并检查

### 问题2：GitHub 仓库无法读取
- 服务器可能无法访问 `api.github.com`（网络/防火墙/SSL 问题）
- 检查 `code_evidence.py` 的 `build_code_evidence` 函数在服务器上的执行结果
- 检查 `app.py` 的 `/api/ai/review` 端点是否正确调用了 `build_code_evidence`
- 检查返回的 `evidence.status` 是否为 `error`（如果是，说明拉取失败）
- 注意：本地测试时 GitHub API 访问正常，但服务器环境可能不同

## 验证方法

```bash
# 1. 检查服务器上 course_data.py 的 rubric 证据类型
ssh root@120.25.213.121 "cd /opt/xkz-agent/ai_engine && grep -n 'screenshot' course_data.py"

# 2. 检查 review.py 是否含截图
ssh root@120.25.213.121 "grep -n '截图\|screenshot\|录屏' /opt/xkz-agent/ai_engine/review.py"

# 3. 测试 GitHub API 从服务器访问
ssh root@120.25.213.121 "curl -s https://api.github.com/repos/W1413580489/chatbot-wrapper-test | head -c 200"

# 4. 测试 code_evidence 拉取
ssh root@120.25.213.121 "cd /opt/xkz-agent/ai_engine && /opt/xkz-agent/backend/venv/bin/python -c \"
import asyncio
from code_evidence import build_code_evidence
r = asyncio.run(build_code_evidence('https://github.com/W1413580489/chatbot-wrapper-test'))
print('ok:', r.get('ok'), 'error:', r.get('error'))
\""

# 5. 重启 pm2 确保加载最新代码
ssh root@120.25.213.121 "pm2 restart xkz-ai && sleep 3 && pm2 logs xkz-ai --lines 5 --nostream"
```

## 时间线

- 2026-08-27 ~16:00 本地完成所有截图移除修改
- 2026-08-27 ~17:00 部署到服务器，Nginx 反代配置完成
- 2026-08-27 ~17:10 浏览器验证页面渲染正常（模型/任务/阶段条均正确）
- 2026-08-27 用户实际使用评审功能，发现两个问题均未修复
