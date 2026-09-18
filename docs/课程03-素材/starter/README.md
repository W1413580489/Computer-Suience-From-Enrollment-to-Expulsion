# MCP 骨架（课程 03 起点）

这是一个**能跑起来的最小 MCP Server**。课程的第一个任务不是写代码，而是**让它跑起来并接进你的 AI 客户端**。

## 1. 装依赖

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> ⚠️ 注意包名：官方包叫 **`mcp`**。另有一个第三方框架叫 `fastmcp`（gofastmcp.com），**不是同一个东西**，装错了后面会一直报奇怪的错。

> ⚠️ **版本差异（真实踩坑，我们实测过）**：`mcp` **2.x 把 v1 的 `FastMCP` 改名为 `MCPServer`**，
> 导入路径也从 `mcp.server.fastmcp` 变成 `mcp.server.mcpserver`。
> 如果你照网上的老教程写 `from mcp.server.fastmcp import FastMCP`，会看到一条明确的报错
> （提示 FastMCP 已改名并给出迁移链接）——**这不是你的环境坏了，是版本差异**。
> 想跟着老教程走，可以临时 `pip install "mcp<2"`；本课程按 2.x 写。

## 2. 确认它能跑

```bash
python -c "import server; print('ok:', server.mcp.name)"
```

打印出 `ok: ai-work-continuity` 就说明骨架正常。

## 3. 接进你的 AI 客户端

看《学生版-客户端接入指南》，把下面的配置填进你的客户端（路径换成你本机这个 `server.py` 的绝对路径）：

```json
{
  "mcpServers": {
    "work-continuity": {
      "command": "python",
      "args": ["/绝对路径/server.py"]
    }
  }
}
```

Windows 上如果 `python` 不在 PATH，把 `command` 写成解释器的绝对路径（例如 `.venv\\Scripts\\python.exe`）。

## 4. 接好之后应该看到什么

- 客户端的 MCP 列表里出现 `work-continuity`
- 工具列表里有 `hello`
- 在对话里让 AI 调用它，能看到 `你好，xxx！MCP 服务器已就绪。`

看到这些，**第一个任务就算完成了**——接下来才是把它扩展成真正的项目记忆服务。
