# 前置准备：申请 GitHub Token（10 分钟搞定）

> 课程：《GitHub 项目分析 Agent》 ｜ 第 3 个任务（T03）前必读
> 你要做的 Agent 需要读取 GitHub 仓库的信息。GitHub 对"没登录的访客"限制很严：**每小时只能查 60 次**，而你的 Agent 分析一个仓库就要用掉十几次。申请一个免费的 Token（通行证）后，限额会升到 **每小时 5000 次**，做作业绰绰有余。

---

## 第一步：找到申请入口（1 分钟）

1. 打开 [github.com](https://github.com)，登录你的账号
2. 点右上角你的**头像**
3. 在菜单里选 **Settings**（设置）

> 如果没看到 Settings，说明你还没登录，先登录再回来。

## 第二步：进入 Token 页面（1 分钟）

1. 在 Settings 页面左侧，一路**往下滚**，找到最底部一项：**Developer settings**（开发者设置）
2. 点开之后，左侧会出现 **Personal access tokens**
3. 点它下面的 **Tokens (classic)** → 进入后点右上角的 **Generate new token (classic)**
4. 如果提示要输入密码，输入你的 GitHub 密码确认即可

## 第三步：填写并生成（2 分钟）

在弹出的表格里，跟着填：

| 项目 | 填什么 |
|---|---|
| **Note**（备注） | 随便起个名，比如 `agent-course`（方便以后认出来） |
| **Expiration**（有效期） | 选 **90 days**（到期前要重新申请，到时你的课也差不多结束了） |
| **Select scopes**（权限） | 只勾 **`public_repo`** 这一项！其他一律不勾 |

> ⚠️ **只勾 public_repo**。我们这门课只读公开仓库，用不到别的权限。权限给得越少越安全。

选完后，点最底下的绿色按钮 **Generate token**。

## 第四步：立刻复制保存（唯一的机会！）

生成后页面会显示一串以 **`ghp_`** 开头的乱码——**这就是你的 Token，只显示这一次！** 刷新页面就再也看不到了。

1. 点旁边的**复制按钮**把它复制下来
2. **立即粘贴**到一个安全的地方（比如你自己电脑上的笔记软件）
3. 不要截图发到任何聊天群！它相当于你的 GitHub 密码

---

## 把 Token 交给你的程序（别直接写进代码！）

拿到 Token 后，按下面两步配置，**不要把 Token 直接写进 .py 代码里**：

**① 创建 `.env` 文件**（和 `agent.py` 同一个文件夹）：

```
# .env 文件内容
GITHUB_TOKEN=把刚复制的 ghp_ 开头的字符串粘贴到这里
```

**② 确保 `.env` 不会被上传**：在项目根目录创建 `.gitignore` 文件，写上：

```
.env
```

然后你的 Python 代码里用这种方式读取（这样代码里永远看不到 Token 明文）：

```python
from dotenv import load_dotenv
import os

load_dotenv()          # 读取 .env 文件
token = os.getenv("GITHUB_TOKEN")
```

> 小提示：`python-dotenv` 需要先安装：`pip install python-dotenv`

---

## 三个安全铁律（记住这三条，你就不会踩坑）

1. **Token 绝不写进源代码**——一律放 `.env`，且 `.gitignore` 必须包含 `.env`
2. **代码里只用环境变量读取**——用 `os.getenv("GITHUB_TOKEN")`
3. **发现泄露立即作废**——回到 Tokens 页面点 **Revoke**（作废）并重新生成一个

---

## 常见报错对照表（遇到别慌）

| 报错 | 意思 | 怎么办 |
|---|---|---|
| **401 Unauthorized** | Token 不对或已过期 | 重新生成一个 Token，确认粘贴无误 |
| **403** + 返回头里有 `X-RateLimit-Remaining: 0` | 限流了（请求次数用完） | 确认请求带上了 Token；等一会儿再试 |
| **403** + 没有限流字样 | Token 权限不够 | 检查生成时是否勾了 `public_repo` |
| **404 Not Found** | 仓库不存在或不是公开的 | 确认仓库地址是 `https://github.com/用户名/仓库名` 的格式 |

---

## 自检清单（做完这几点，就可以开始 T03 了）

- [ ] 已生成 Token 并**复制保存**到安全位置
- [ ] 项目里有 `.env` 文件，Token 已粘贴进去
- [ ] 项目里有 `.gitignore` 文件，里面包含 `.env`
- [ ] 代码用 `os.getenv("GITHUB_TOKEN")` 读取，源码里搜不到 `ghp_` 开头的字符串
- [ ] 用下面这行命令能测通（会返回你 GitHub 账号的登录名）：
  ```bash
  curl -H "Authorization: Bearer 你的Token" https://api.github.com/user
  ```
  能看到 `"login": "你的用户名"` 就说明 Token 配置成功了。

---

如果照着做还是卡住，不用慌——切回「指导」模式，把你的报错原文贴给 AI 导师，它会带着你一步步排查。
