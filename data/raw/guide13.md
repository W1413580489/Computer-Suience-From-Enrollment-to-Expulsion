# 套壳聊天机器人实战

用十几分钟做一个「套壳聊天机器人」：一个简单的网页 + 一个后端接口，把消息转发给 DeepSeek 大模型，再把回答显示在网页上。不涉及数据库、不涉及复杂的工程，目的是让你完整体验「前端 → 后端 → 大模型 API」的最小闭环。

整体结构：

> 用户输入问题 → 前端页面 →（POST）→ 后端接口 →（转发）→ DeepSeek API → 返回回答 → 前端显示

前后端职责分工：

- **前端**：一块聊天界面（输入框 + 消息列表 + 发送按钮），负责收集问题、展示回答。
- **后端**：一个接口，收到前端发来的问题，带着你的 API Key 转发给 DeepSeek，把返回的答案送回去。

## 前置准备

开始前先确认三件事：

1. **装好 Python**：本教程用 Python 写后端。命令行输入 `python --version` 能输出版本号即可（3.9+）。
2. **准备一个 DeepSeek API Key**：到 DeepSeek 开放平台申请，形如 `sk-xxxxxxxx`。
3. **建一个项目文件夹**：比如 `D:\chatbot\`，后端代码和前端页面都放这里。

依赖安装（在项目文件夹里执行）：

```bash
pip install fastapi uvicorn httpx
```

装完验证：`python -c "import fastapi, uvicorn, httpx; print('ok')"` 输出 `ok` 就绪。

## 后端接口

创建一个文件 `main.py`，写一个接口 `POST /chat`：接收 `{message}`，转发到 DeepSeek，返回 `{reply}`。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

# 允许前端页面跨域访问
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

API_KEY = "在这里填你的DeepSeek Key"   # BYOK：用你自己的 Key
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

class ChatIn(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatIn):
    # 1. 把用户问题组装成发给大模型的消息
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": req.message}],
    }
    # 2. 用你的 Key 调用 DeepSeek
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}",
                     "Content-Type": "application/json"},
            json=payload,
        )
    # 3. 取出回答内容返回给前端
    answer = r.json()["choices"][0]["message"]["content"]
    return {"reply": answer}

# 启动：uvicorn main:app --reload --port 8000
```

关键点：

- `POST /chat` 是接口地址；`ChatIn` 声明了它接收 `{message}` 字段。
- 转发时带着你的 `API_KEY`，并把大模型返回的 `choices[0].message.content` 抽出来当作 `reply`。
- 启动命令写在注释里：`uvicorn main:app --reload --port 8000`，`--reload` 改代码自动重启。

启动后端：在项目文件夹运行 `uvicorn main:app --reload --port 8000`，看到 `Uvicorn running on http://127.0.0.1:8000` 说明成功。

## 前端页面

创建一个文件 `index.html`，一个自包含的聊天页面：输入框 + 消息列表 + 发送按钮，点击发送就把内容 POST 给后端并把返回显示出来。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>套壳聊天机器人</title>
<style>
  body{display:flex;flex-direction:column;height:100vh;margin:0;font-family:system-ui,sans-serif}
  #list{flex:1;overflow-y:auto;padding:16px}
  .msg{margin:6px 0;padding:8px 12px;border-radius:8px;max-width:70%;white-space:pre-wrap}
  .user{align-self:flex-end;background:#4f7cff;color:#fff;margin-left:auto}
  .bot{align-self:flex-start;background:#eee;color:#222}
  .bar{display:flex;gap:8px;padding:10px;border-top:1px solid #ddd}
  #input{flex:1;padding:8px}
</style>
</head>
<body>
  <div id="list"></div>
  <div class="bar">
    <input id="input" placeholder="输入你的问题...">
    <button id="send">发送</button>
  </div>

<script>
  const list = document.getElementById("list");
  const input = document.getElementById("input");
  const send = document.getElementById("send");

  function add(role, text){
    const d = document.createElement("div");
    d.className = "msg " + role;
    d.textContent = text;
    list.appendChild(d);
    list.scrollTop = list.scrollHeight;  // 自动滚到底，显示最新消息
  }

  send.onclick = async () => {
    const q = input.value.trim();
    if (!q) return;
    add("user", q);
    input.value = "";

    // 把问题 POST 给后端
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: q}),
    });
    const data = await res.json();
    add("bot", data.reply);
  };
</script>
</body>
</html>
```

把前端 `fetch` 的地址指向你后端启动的端口（这里是 `8000`）。`add()` 函数负责把一条消息插进列表，并滚动到底部。

启动前端：直接用浏览器双击打开 `index.html` 即可。

## 联调与验收

前后端都起来后，在页面输入一个问题点击发送，看到机器人回答即联调成功。

先以「能跑」为准，通过后逐条对照验收：

- [ ] 输入内容能发出去，页面能看到你自己说的话
- [ ] 机器人能正常回答（把问题转发给了 DeepSeek 并显示了返回结果）
- [ ] 消息多了列表能上下滚动，最新消息在最下面
- [ ] 后端接口你大致能讲清：`POST /chat` 做了什么、Key 放在哪、为什么能回答
- [ ] API Key 只出现在后端 `main.py`，没有硬编码进前端页面

如果页面控制台报错（F12 打开），按这三步查：① 后端有没有起来（端口有没有监听）② 前端 POST 的地址端口对不对 ③ 是不是 CORS 跨域被挡（后端要开 `allow_origins=["*"]`）。

到这里，一个最小的「前后端 + 大模型 API」闭环就完成了。