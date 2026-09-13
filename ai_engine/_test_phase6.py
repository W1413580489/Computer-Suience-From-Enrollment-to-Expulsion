# -*- coding: utf-8 -*-
"""
阶段 6 验收测试：对话附图（V2.2 chat vision）。

覆盖：
  T6.1 只贴图不打字也能发送（不再报 EMPTY_INPUT）
  T6.2 读图转录结果注入对话（模型能看到图里的内容）
  T6.3 读图结果参与行为路由（贴报错截图 → 自动进入调试行为）
  T6.4 对话场景使用"转录型"提示词（与验收场景的"观察型"区分）
  T6.5 非白名单模型带图 → 跳过读图，纯文本对话照常（fail-open）
  T6.6 非法格式 / 超大 / 超数量 → 读图失败但对话照常
  T6.7 纯文本对话（无图）行为与改动前一致（回归）
  T6.8 同图重复发送命中事实缓存（不重复调用模型）
  T6.9 日志与隐私：只记元数据，绝不含图片内容
  T6.10 图片要点回传前端（visual_note，供后续追问保留上下文）

运行：python _test_phase6.py（不调真实模型，httpx 全 mock）
"""
import base64
import json

from fastapi.testclient import TestClient

import app as app_mod
import vision as vision_mod
from schemas import AiResponse, Mode
from vision import VisualFacts

PASS_COUNT = 0
FAIL_LINES = []


def check(name: str, cond: bool, detail: str = ""):
    global PASS_COUNT
    if cond:
        PASS_COUNT += 1
        print(f"  ✓ {name}")
    else:
        FAIL_LINES.append(name)
        print(f"  ✕ {name}  {detail}")


def png(size: int = 200) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"0" * max(0, size - 8)


def img(raw: bytes, name="shot.png", mime="image/png") -> dict:
    return {"name": name, "mime": mime, "data_base64": base64.b64encode(raw).decode()}


# ---------------------------------------------------------------------------
# Mock：视觉调用与 teach 调用
# ---------------------------------------------------------------------------
CALLS = {"vision": 0, "teach": 0, "system_prompt": "", "images": 0, "messages": []}
LOG_EVENTS: list[dict] = []

TRANSCRIPT = VisualFacts(
    facts=[
        "终端显示 Traceback (most recent call last):",
        "ModuleNotFoundError: No module named 'requests'",
        "执行的命令是 python agent.py",
    ],
    uncertain=["终端上方的路径文字太小，无法辨认"],
    task_relation="relevant",
)


async def fake_call_vision(model, api_key, base_url, provider, user_text, images,
                           system_prompt=None):
    CALLS["vision"] += 1
    CALLS["system_prompt"] = system_prompt or ""
    CALLS["images"] = len(images)
    return TRANSCRIPT


async def fake_teach(self, messages, mode):
    CALLS["teach"] += 1
    CALLS["messages"] = list(messages)
    return AiResponse(mode=Mode.tutor,
                      message="看起来是缺少 requests 依赖，先在终端执行 pip install requests，再重新运行。")


def fake_log(**kw):
    LOG_EVENTS.append(kw)


vision_mod._call_vision = fake_call_vision
app_mod.LLMClient.teach = fake_teach
app_mod.validate = lambda resp, ctx: (True, [])
app_mod.logs_mod.log_event = fake_log

client = TestClient(app_mod.app)


def teach(body: dict) -> dict:
    r = client.post("/api/ai/teach", json=body)
    return {"status": r.status_code, "json": r.json()}


def base_body(**kw) -> dict:
    b = {"session_id": "t6", "task_id": "task_review", "mode": "tutor",
         "project_id": "project_chatbot", "course_id": "course_001",
         "user_input": "", "api_key": "sk-test", "model": "deepseek-flash"}
    b.update(kw)
    return b


# ---------------------------------------------------------------------------
print("== T6.1 只贴图不打字也能发送 ==")
vision_mod.cache_clear()
LOG_EVENTS.clear()
r = teach(base_body(session_id="t6-a", visual_images=[img(png())]))
check("HTTP 200 且 ok（不再因空文字被拒）",
      r["status"] == 200 and r["json"].get("ok") is True, json.dumps(r["json"], ensure_ascii=False)[:160])
d = r["json"]["data"]
check("视觉状态 ok", d["visual"] and d["visual"]["status"] == "ok", str(d.get("visual"))[:120])
check("图片张数 = 1", d["visual"]["count"] == 1, str(d["visual"])[:120])

print("== T6.2 读图结果注入对话 ==")
user_msgs = [m["content"] for m in CALLS["messages"] if m.get("role") == "user"]
joined = "\n".join(user_msgs)
check("对话里有读图转录消息", "[学生上传了运行截图" in joined, joined[:120])
check("转录含报错原文（模型能看到 ModuleNotFoundError）", "ModuleNotFoundError" in joined)
check("转录含无法辨认部分", "无法辨认" in joined)
check("最后一条是学生提问占位（只贴图时）",
      user_msgs and "图片" in user_msgs[-1], user_msgs[-1][:60] if user_msgs else "")

print("== T6.3 读图结果参与行为路由（贴报错截图 → 调试行为） ==")
check("behavior == debug", d["behavior"] == "debug", str(d.get("behavior")))

print("== T6.4 对话场景使用转录型提示词 ==")
check("使用 CHAT_VISION_SYSTEM_PROMPT",
      CALLS["system_prompt"] == vision_mod.CHAT_VISION_SYSTEM_PROMPT,
      CALLS["system_prompt"][:60])
check("与验收观察提示词不同", CALLS["system_prompt"] != vision_mod.VISION_SYSTEM_PROMPT)
check("载荷里确实带了图片", CALLS["images"] == 1, str(CALLS["images"]))

print("== T6.5 非白名单模型带图 → 跳过读图，对话照常 ==")
vision_mod.cache_clear()
before = CALLS["vision"]
r = teach(base_body(session_id="t6-b", model="qwen-plus", visual_images=[img(png())]))
d = r["json"]["data"]
check("对话正常返回", r["json"].get("ok") is True)
check("视觉 skipped / VISION_UNSUPPORTED",
      d["visual"] and d["visual"]["status"] == "skipped" and d["visual"]["code"] == "VISION_UNSUPPORTED",
      str(d.get("visual"))[:120])
check("未发起任何视觉调用（零成本）", CALLS["vision"] == before, f'{CALLS["vision"]} vs {before}')
check("仍能基于文字回答（teach 照常调用）", CALLS["teach"] > 0)

print("== T6.6 非法 / 超大 / 超数量 → 读图失败但对话照常 ==")
vision_mod.cache_clear()
r = teach(base_body(session_id="t6-c", user_input="帮我看看这个报错",
                    visual_images=[img(b"this is definitely not an image")]))
d = r["json"]["data"]
check("非法格式 → IMAGE_FORMAT_INVALID",
      d["visual"]["status"] == "error" and d["visual"]["code"] == "IMAGE_FORMAT_INVALID",
      str(d.get("visual"))[:120])
check("对话仍正常返回", r["json"].get("ok") is True)

vision_mod.cache_clear()
r = teach(base_body(session_id="t6-d", visual_images=[img(png(900 * 1024))]))
d = r["json"]["data"]
check("超大图 → IMAGE_TOO_LARGE",
      d["visual"]["code"] == "IMAGE_TOO_LARGE", str(d.get("visual"))[:120])

vision_mod.cache_clear()
r = teach(base_body(session_id="t6-e", visual_images=[img(png()), img(png()), img(png())]))
d = r["json"]["data"]
check("超数量 → IMAGE_TOO_MANY", d["visual"]["code"] == "IMAGE_TOO_MANY", str(d.get("visual"))[:120])

print("== T6.7 纯文本对话（无图）回归 ==")
vision_mod.cache_clear()
r = teach(base_body(session_id="t6-f", user_input="我卡在第 3 步了"))
d = r["json"]["data"]
check("visual 为 None（未传图不产生视觉字段）", d["visual"] is None, str(d.get("visual")))
check("visual_note 为空", d["visual_note"] == "", str(d.get("visual_note")))
check("纯文本照常返回", r["json"].get("ok") is True and bool(d["message"]))

print("== T6.8 同图重复发送命中缓存 ==")
vision_mod.cache_clear()
b = base_body(session_id="t6-g", user_input="再看一次", visual_images=[img(png())])
r1 = teach(b)
c1 = r1["json"]["data"]["visual"]["cached"]
n1 = CALLS["vision"]
r2 = teach(dict(b, session_id="t6-h"))
c2 = r2["json"]["data"]["visual"]["cached"]
n2 = CALLS["vision"]
check("首次未命中缓存", c1 is False, str(c1))
check("第二次命中缓存", c2 is True, str(c2))
check("缓存命中不重复调用模型", n2 == n1, f"{n2} vs {n1}")

print("== T6.9 日志隐私（只记元数据） ==")
check("记录了 vision 事件", any(e.get("type") == "vision" for e in LOG_EVENTS), str(len(LOG_EVENTS)))
blob = json.dumps(LOG_EVENTS, ensure_ascii=False, default=str)
raw_b64 = base64.b64encode(png()).decode()
check("日志不含 base64 图片内容", raw_b64 not in blob)
check("日志不含 data URL", "data:image" not in blob)
check("日志只含元数据字段（数量/字节/状态）",
      all(set(e.keys()) <= {"type", "session_id", "task_id", "project_id", "vision_purpose",
                            "vision_status", "vision_code", "image_count", "image_bytes",
                            "vision_model", "vision_cached", "vision_ms"}
          for e in LOG_EVENTS if e.get("type") == "vision"))
check("日志标记 purpose=chat",
      any(e.get("vision_purpose") == "chat" for e in LOG_EVENTS if e.get("type") == "vision"))

print("== T6.10 图片要点回传前端 ==")
vision_mod.cache_clear()
r = teach(base_body(session_id="t6-i", user_input="这个报错什么意思", visual_images=[img(png())]))
note = r["json"]["data"]["visual_note"]
check("visual_note 非空", bool(note), note[:80])
check("visual_note 含图中要点", "ModuleNotFoundError" in note, note[:120])
check("visual_note 长度受限（≤400 字摘要）", len(note) <= 460, str(len(note)))
check("visual_note 不含图片数据", "data:image" not in note and base64.b64encode(png()).decode() not in note)

print()
print(f"通过 {PASS_COUNT} 项")
if FAIL_LINES:
    print(f"失败 {len(FAIL_LINES)} 项：")
    for n in FAIL_LINES:
        print(f"  - {n}")
    raise SystemExit(1)
print("全部通过 ✓")
