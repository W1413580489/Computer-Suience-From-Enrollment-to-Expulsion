"""最小可运行的 MCP Server 骨架（课程 03 的起点）。

它现在只会一件事：回答一次打招呼。
你的任务是基于它做出一个「跨会话项目记忆」服务（见课程任务清单）。

启动（stdio 传输，供 AI 客户端调用）：
    python server.py

不想接客户端，只想确认它能跑：
    python -c "import server; print('import ok:', server.mcp.name)"
"""
from mcp.server.mcpserver import MCPServer

# 这个名字会出现在客户端的 MCP 服务器列表里
# 注意：mcp 2.x 起，v1 的 FastMCP 已改名为 MCPServer
mcp = MCPServer("ai-work-continuity")


@mcp.tool()
def hello(name: str) -> str:
    """打招呼，用来验证服务器是否接通。

    Args:
        name: 要打招呼的对象
    """
    return f"你好，{name}！MCP 服务器已就绪。"


if __name__ == "__main__":
    # 默认 stdio：客户端通过标准输入/输出与本进程通信
    mcp.run()
