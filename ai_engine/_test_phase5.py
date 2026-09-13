# -*- coding: utf-8 -*-
"""
阶段 5 验收测试：V2.1 视觉证据（Visual Evidence）。

覆盖：
  T5.1 图片校验：魔数判定（不信 MIME）、数量上限、单张/总量上限
  T5.2 模型门控：白名单内（deepseek-flash）启用；其他模型整体跳过且不报错
  T5.3 fail-open：不支持/超时/繁忙/非法格式 → 验收照常完成，绝不阻塞
  T5.4 结构化事实 + 事实缓存（命中不重复调用模型）
  T5.5 证据链：visual 进入 available 与快照；纯文本验收（无图）完全不受影响
  T5.6 日志与隐私：日志只记元数据，绝不含图片内容
  T5.7 non-DeepSeek provider 行为与现状一致（回归）
运行：python _test_phase5.py（不调真实模型，httpx 全 mock）
"""
import asyncio
import base64
import json

import httpx
from fastapi.testclient import TestClient

import app as app_mod
import vision as vision_mod
from review import build_review_system_prompt, collect_evidence, evidence_precheck
from schemas import ReviewLLMOutput, Rubric, VisualImage
from course_data import get_rubrics

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


# 造一张合法的最小 PNG（魔数 + 填充）
def png(size: int = 200) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"0" * max(0, size - 8)


def img(raw: bytes, name="shot.png", mime="image/png") -> VisualImage:
    return VisualImage(name=name, mime=mime, data_base64=base64.b64encode(raw).decode())


print("== T5.1 图片校验（魔数 / 数量 / 体积） ==")
check("PNG 魔数识别", vision_mod.sniff_mime(png()) == "image/png")
check("JPEG 魔数识别", vision_mod.sniff_mime(b"\xff\xd8\xff\xe0" + b"0" * 50) == "image/jpeg")
check("WebP 魔数识别", vision_mod.sniff_mime(b"RIFF" + b"\x00" * 4 + b"WEBP" + b"0" * 20) == "image/webp")
check("非图片内容被拒", vision_mod.sniff_mime(b"this is not an image") is None)

# 伪造 MIME：声称 image/png 实际是文本 → 以魔数为准，必须拒绝
fake = VisualImage(name="x.png", mime="image/png",
                   data_base64=base64.b64encode(b"not-an-image-really").decode())
try:
    vision_mod.decode_images([fake])
    check("伪造 MIME 被拒（以魔数为准）", False, "未抛错")
except vision_mod.VisionError as e:
    check("伪造 MIME 被拒（以魔数为准）", e.code == "IMAGE_FORMAT_INVALID", e.code)

try:
    vision_mod.decode_images([img(png()), img(png()), img(png())])
    check("超过 2 张被拒", False, "未抛错")
except vision_mod.VisionError as e:
    check("超过 2 张被拒", e.code == "IMAGE_TOO_MANY", e.code)

try:
    vision_mod.decode_images([img(png(vision_mod.MAX_IMAGE_BYTES + 10))])
    check("单张超 800KB 被拒", False, "未抛错")
except vision_mod.VisionError as e:
    check("单张超 800KB 被拒", e.code == "IMAGE_TOO_LARGE", e.code)

big = vision_mod.MAX_IMAGE_BYTES - 8
try:
    vision_mod.decode_images([img(png(big)), img(png(big))])
    check("两张合计超 1.5MB 被拒", False, "未抛错")
except vision_mod.VisionError as e:
    check("两张合计超 1.5MB 被拒", e.code == "IMAGE_TOO_LARGE", e.code)

print("== T5.2 模型门控 ==")
check("deepseek-flash 支持视觉", vision_mod.is_vision_supported("deepseek-flash"))
check("旧名 deepseek-v4-flash（兼容路由）支持", vision_mod.is_vision_supported("deepseek-v4-flash"))
check("deepseek-v4-flash-vision-exp（兼容路由）支持",
      vision_mod.is_vision_supported("deepseek-v4-flash-vision-exp"))
check("qwen-plus 不支持（未核实 → 不列入）", not vision_mod.is_vision_supported("qwen-plus"))
check("moonshot-v1-8k 不支持", not vision_mod.is_vision_supported("moonshot-v1-8k"))
check("glm-4-flash 不支持", not vision_mod.is_vision_supported("glm-4-flash"))
check("自定义模型不支持（无法判定）", not vision_mod.is_vision_supported("my-custom-model"))

print("== T5.3 fail-open（vision.analyze_images 永不抛异常） ==")


def run(coro):
    return asyncio.run(coro)


base_kwargs = dict(task_title="写前端页面", task_objective="做出聊天界面", visual_conditions=[],
                   api_key="sk-test")

ev = run(vision_mod.analyze_images([img(png())], model="qwen-plus", **base_kwargs))
check("非白名单模型 → skipped/VISION_UNSUPPORTED（不报错）",
      ev.status == "skipped" and ev.code == "VISION_UNSUPPORTED", f"{ev.status}/{ev.code}")

ev = run(vision_mod.analyze_images([img(png())], model="deepseek-flash",
                                   task_title="t", task_objective="o", visual_conditions=[],
                                   api_key=""))
check("无 Key → skipped/NO_API_KEY", ev.status == "skipped" and ev.code == "NO_API_KEY")

ev = run(vision_mod.analyze_images([fake], model="deepseek-flash", **base_kwargs))
check("非法格式 → error/IMAGE_FORMAT_INVALID（不抛异常）",
      ev.status == "error" and ev.code == "IMAGE_FORMAT_INVALID", f"{ev.status}/{ev.code}")

print("== T5.4 结构化事实 + 事实缓存 ==")
CALLS = {"n": 0}


class FakeResp:
    def __init__(self, status=200, body=None, text=""):
        self.status_code = status
        self._body = body or {}
        self.text = text

    def json(self):
        return self._body


def facts_body():
    content = json.dumps({
        "facts": ["页面存在输入框", "存在用户消息“你好”", "存在 AI 回复"],
        "uncertain": ["无法确认该页面对应 GitHub 当前版本"],
        "task_relation": "relevant",
        "analysis_error": "",
    }, ensure_ascii=False)
    return {"choices": [{"message": {"content": content}}]}


class FakeClient:
    payloads: list = []

    def __init__(self, *a, **k):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, headers=None, json=None):
        CALLS["n"] += 1
        FakeClient.payloads.append(json)
        return FakeResp(200, facts_body())


orig = httpx.AsyncClient
httpx.AsyncClient = FakeClient
vision_mod.cache_clear()
try:
    ev1 = run(vision_mod.analyze_images([img(png())], model="deepseek-flash", **base_kwargs))
    ev2 = run(vision_mod.analyze_images([img(png())], model="deepseek-flash", **base_kwargs))
finally:
    httpx.AsyncClient = orig

check("分析成功且返回结构化事实", ev1.status == "ok" and len(ev1.facts) == 3, str(ev1.facts))
check("带图片指纹（进快照）", len(ev1.image_hashes) == 1 and len(ev1.image_hashes[0]) == 16)
check("task_relation 归一化", ev1.task_relation == "relevant", ev1.task_relation)
check("第二次同图命中事实缓存（只调用 1 次模型）", CALLS["n"] == 1 and ev2.cached, f"calls={CALLS['n']}")
check("载荷使用 base64 data URL 内联", "data:image/png;base64," in
      str(FakeClient.payloads[0]["messages"][1]["content"][1]["image_url"]["url"]))
check("载荷带 detail=low（省 token）",
      FakeClient.payloads[0]["messages"][1]["content"][1]["image_url"].get("detail") == "low")
check("载荷使用 json_object 模式", FakeClient.payloads[0].get("response_format") == {"type": "json_object"})

print("== T5.4b 服务商字段兼容自愈（400 → 去掉 detail / response_format 重试） ==")
RETRY = {"n": 0, "payloads": []}


class PickyClient(FakeClient):
    async def post(self, url, headers=None, json=None):
        RETRY["n"] += 1
        RETRY["payloads"].append(json)
        if json.get("response_format") or json["messages"][1]["content"][1]["image_url"].get("detail"):
            return FakeResp(400, {}, text='{"error":{"message":"Invalid parameter: detail is not supported"}}')
        return FakeResp(200, facts_body())


httpx.AsyncClient = PickyClient
vision_mod.cache_clear()
try:
    ev3 = run(vision_mod.analyze_images([img(png())], model="deepseek-flash", **base_kwargs))
finally:
    httpx.AsyncClient = orig
check("别家不认 detail/response_format 时自愈成功", ev3.status == "ok", f"{ev3.status}/{ev3.code}")
check("自愈过程最终去掉了两个可选字段", RETRY["n"] >= 2 and
      "response_format" not in RETRY["payloads"][-1] and
      "detail" not in RETRY["payloads"][-1]["messages"][1]["content"][1]["image_url"],
      f"retries={RETRY['n']}")


class RejectImage:
    def __init__(self, *a, **k):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, headers=None, json=None):
        return FakeResp(400, {}, text='{"error":{"message":"This model does not support image"}}')


httpx.AsyncClient = RejectImage
vision_mod.cache_clear()
try:
    ev4 = run(vision_mod.analyze_images([img(png())], model="deepseek-flash", **base_kwargs))
finally:
    httpx.AsyncClient = orig
check("明确不支持图片 → VISION_UNSUPPORTED（不做无意义重试）",
      ev4.status == "error" and ev4.code == "VISION_UNSUPPORTED", f"{ev4.status}/{ev4.code}")

print("== T5.5 证据链（可用证据 / 快照 / 无图不受影响） ==")
from schemas import VisualEvidence
sample = VisualEvidence(status="ok", facts=["存在输入框", "存在 AI 回复"],
                        uncertain=["无法确认版本"], task_relation="relevant",
                        count=1, bytes=200, image_hashes=["abc123def456"], model="deepseek-flash")
avail = collect_evidence(None, "", visual=sample)
check("visual 进入可用证据", "visual" in avail)
check("证据文本含事实与指纹", "存在 AI 回复" in avail["visual"] and "abc123def456" in avail["visual"])

# 视觉不可用时不影响证据收集
avail_none = collect_evidence(None, "", visual=VisualEvidence(status="skipped", code="VISION_BUSY"))
check("视觉 skipped 时证据链不含 visual", "visual" not in avail_none)

# visual 永不作为硬门槛：即使误写进 required_evidence 也不触发 NEED_REVIEW
rb = Rubric(id="rb_x", task_id="t", criterion="x", required_evidence=["visual"], weight=1)
pre = evidence_precheck([rb], {"description": "自述"})
check("visual 写在 required_evidence 里也不当硬门槛",
      all(f["rubric_id"] != "rb_x" for f in pre["forced_needs_review"]), str(pre["forced_needs_review"]))

# 提示词包含视觉观察点与边界规则
rb2 = Rubric(id="rb_y", task_id="t", criterion="能问答", required_evidence=["code"], weight=2,
             visual_check="supported", visual_pass_condition="截图中同时存在用户消息与 AI 回复")
from schemas import Task
prompt = build_review_system_prompt(
    Task(id="task_review", title="提交成果验收", stage_id="stage_accept", order=1),
    [rb2], {"code": "代码证据", "visual": sample.model_dump_json()})
check("红头声明视觉观察点", "视觉观察点" in prompt and "用户消息与 AI 回复" in prompt)
check("Prompt 含视觉边界规则（不评美观/不替代运行证据/缺失不扣分）",
      "不评价界面美观" in prompt and "不能替代" in prompt and "不得仅因" in prompt)

print("== T5.6 端到端：无图验收完全不受影响 + 有图走视觉（mock） ==")
client = TestClient(app_mod.app)
FIXED = {"criteria": [
    {"rubric_id": "rb_review_2", "status": "PASS", "evidence": "code", "reason": "ok"},
    {"rubric_id": "rb_review_3", "status": "PASS", "evidence": "code", "reason": "ok"},
    {"rubric_id": "rb_review_4", "status": "PASS", "evidence": "description", "reason": "ok"},
], "next_step": "无"}


async def fake_review(self, messages):
    return ReviewLLMOutput.model_validate(FIXED)


async def fake_code_evidence(repo_url, task_id="", code_context=None, client=None):
    return {"ok": True, "repo": "u/r", "default_branch": "main", "file_count": 2, "key_files": [],
            "evidence_text": "GITHUB-REPO: u/r", "readme_run_cmd": "uvicorn main:app",
            "ci": {"ok": True, "has_ci": True, "runs_count": 1, "text": "[CI]",
                   "workflows": [{"name": "tests", "dimension": "test", "conclusion": "success",
                                  "status": "completed", "url": ""}]}}


o_rev, o_ev = app_mod.LLMClient.review, app_mod.build_code_evidence
app_mod.LLMClient.review, app_mod.build_code_evidence = fake_review, fake_code_evidence
app_mod._REVIEW_CACHE.clear()
vision_mod.cache_clear()
httpx.AsyncClient = FakeClient
try:
    body_noimg = {"session_id": "t5", "task_id": "task_review", "project_id": "project_chatbot",
                  "submission": {"code": "x", "description": "uvicorn main:app 启动"},
                  "api_key": "sk-test", "model": "deepseek-flash"}
    r1 = client.post("/api/ai/review", json=body_noimg).json()["data"]
    check("无图验收正常返回", r1["status"] in ("PASS", "FAIL", "NEED_REVIEW"), str(r1.get("status")))
    check("无图时 visual 字段为 null", r1.get("visual") is None)

    body_img = dict(body_noimg)
    body_img["visual_images"] = [{"name": "s.png", "mime": "image/png",
                                  "data_base64": base64.b64encode(png()).decode()}]
    r2 = client.post("/api/ai/review", json=body_img).json()["data"]
    check("有图验收：visual 返回结构化事实",
          r2["visual"] and r2["visual"]["status"] == "ok" and r2["visual"]["facts"],
          str(r2.get("visual"))[:120])
    check("有图验收：快照变化（图片指纹进入快照）",
          r1["snapshot_hash"] != r2["snapshot_hash"], f'{r1["snapshot_hash"]} vs {r2["snapshot_hash"]}')

    # 非 DeepSeek 模型 + 带图 → 跳过视觉，验收照常（先清缓存，避免命中"无图"版本）
    body_qwen = dict(body_img)
    body_qwen["model"] = "qwen-plus"
    body_qwen["session_id"] = "t5-qwen"
    app_mod._REVIEW_CACHE.clear()
    r3 = client.post("/api/ai/review", json=body_qwen).json()["data"]
    check("非白名单模型带图 → 视觉跳过但验收完成",
          r3["visual"]["status"] == "skipped" and r3["visual"]["code"] == "VISION_UNSUPPORTED"
          and r3["status"] in ("PASS", "FAIL", "NEED_REVIEW"), str(r3.get("visual"))[:80])
    check("非白名单模型：判定与无图版本一致（视觉不参与）",
          r3["status"] == r1["status"] and r3["score"] == r1["score"],
          f'{r3["status"]}/{r3["score"]} vs {r1["status"]}/{r1["score"]}')
    check("非白名单模型：快照与无图版本一致（视觉被完全忽略）",
          r3["snapshot_hash"] == r1["snapshot_hash"], f'{r3["snapshot_hash"]} vs {r1["snapshot_hash"]}')
finally:
    app_mod.LLMClient.review, app_mod.build_code_evidence = o_rev, o_ev
    app_mod._REVIEW_CACHE.clear()
    vision_mod.cache_clear()
    httpx.AsyncClient = orig

print("== T5.6b 日志隐私：只记元数据，不含图片内容 ==")
import logs as logs_mod
events = logs_mod.read_events(limit=200)
vision_events = [e for e in events if e.get("type") == "vision"]
check("写入了 vision 元数据事件", bool(vision_events), f"n={len(vision_events)}")
if vision_events:
    blob = json.dumps(vision_events, ensure_ascii=False)
    check("日志含图片数量/字节/耗时",
          all(k in vision_events[-1] for k in ("image_count", "image_bytes", "vision_ms")),
          str(vision_events[-1]))
    check("日志不含 base64 图片内容", "data:image" not in blob and "iVBOR" not in blob)
    check("日志不含图片字节字段", "visual_images" not in blob and "data_base64" not in blob)

print()
if FAIL_LINES:
    print(f"FAILED: {len(FAIL_LINES)} 项未通过 → {FAIL_LINES}")
    raise SystemExit(1)
print(f"ALL PASSED: {PASS_COUNT} checks")
