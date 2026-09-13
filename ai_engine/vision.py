# -*- coding: utf-8 -*-
"""
V2.1 Visual Evidence：运行截图的视觉分析（服务端只转发，不做本地推理）。

设计硬约束（对应《AI 项目导师 V2.1 执行报告（修订版）》）：
  1. **模型白名单**：只有真实验证过支持图片的模型才进入 VISION_WHITELIST。
     当前仅 DeepSeek V4.1（官方模型名 deepseek-flash，原生多模态）。
     旧名 deepseek-v4-flash / deepseek-v4-flash-vision-exp 目前仍被官方兼容路由到
     V4.1-Flash，故一并列入；Qwen / Kimi / GLM / Custom **一律不列入**（未核实）。
  2. **fail-open**：模型不支持 / 超时 / 排队满 / 调用失败 → 返回 skipped 或 error，
     Reviewer 侧忽略视觉证据，普通验收完全不受影响（绝不因视觉失败而阻塞验收）。
  3. **原图不持久化**：图片只在请求内存中存在，处理完即释放；
     不落磁盘、不写 JSONL、不进 Session、不进日志（仅记录数量/字节/耗时/错误码）。
  4. **图片校验**：数量 ≤2、单张 ≤800KB、合计 ≤1.5MB、格式以**文件魔数**判断
     （不信任客户端声明的 MIME），不引入 Pillow 等图像库。
  5. **并发闸门**：服务器为 2 核 / 1.8GB（可用约 830MB），同时最多 2 个视觉分析，
     超出直接跳过并标记 VISION_BUSY（不排队、不堆积内存）。
  6. **结果缓存**：仅缓存结构化事实文本（image_hash → facts），上限 200 条，TTL 30 分钟；
     **绝不缓存图片字节**。
"""
from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import re
import time

import httpx
from pydantic import BaseModel, Field, ValidationError

from llm_client import DEFAULT_BASE_URL, _extract_json
from schemas import VisualEvidence, VisualImage

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
VISION_WHITELIST: set[str] = {
    "deepseek-flash",                  # V4.1（原生多模态，当前默认）
    "deepseek-v4.1-flash",             # 官方文档提到的等价名
    "deepseek-v4-flash",               # 旧名，官方暂时路由到 V4.1
    "deepseek-v4-flash-vision-exp",    # 旧视觉实验模型名，官方暂时路由到 V4.1
}

MAX_IMAGES = 2
MAX_IMAGE_BYTES = 800 * 1024          # 单张 800KB（比报告的 1MB 更严，适配 2C2G）
MAX_TOTAL_BYTES = int(1.5 * 1024 * 1024)
MAX_CONCURRENT = 2
CACHE_TTL = 1800                      # 30 分钟
CACHE_MAX = 200

VISION_TIMEOUT = httpx.Timeout(connect=10.0, read=90.0, write=30.0, pool=10.0)

# 各服务商的载荷差异（新增一家支持 = 加一行，不改主逻辑）
PROVIDER_VISION_OVERRIDES: dict[str, dict] = {}


class VisionError(Exception):
    """视觉链路错误（带错误码，fail-open 用）。"""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code
        self.message = message or code


class VisualFacts(BaseModel):
    """视觉模型的结构化输出（只讲观察到的事实，不做审美判断）。"""
    facts: list[str] = Field(default_factory=list)
    uncertain: list[str] = Field(default_factory=list)
    task_relation: str = "unclear"     # relevant / irrelevant / unclear
    analysis_error: str = ""


# ---------------------------------------------------------------------------
# 状态：并发闸门 + 事实缓存（进程内存，重启丢失；不建数据库）
# ---------------------------------------------------------------------------
_inflight = 0
_FACTS_CACHE: dict[str, tuple[float, VisualFacts]] = {}


def cache_clear() -> None:
    _FACTS_CACHE.clear()


def inflight() -> int:
    return _inflight


# ---------------------------------------------------------------------------
# 图片校验
# ---------------------------------------------------------------------------
def sniff_mime(raw: bytes) -> str | None:
    """按文件魔数判断图片类型（不信任客户端 MIME）。"""
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if raw.startswith(b"GIF87a") or raw.startswith(b"GIF89a"):
        return "image/gif"
    if len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return None


def _decode_one(img: VisualImage) -> tuple[bytes, str]:
    """base64 解码 + 魔数校验；失败抛 VisionError。"""
    data = (img.data_base64 or "").strip()
    if data.startswith("data:"):                      # 容错：去掉 data URL 前缀
        data = data.split(",", 1)[-1]
    if not data:
        raise VisionError("IMAGE_FORMAT_INVALID", "图片内容为空")
    try:
        raw = base64.b64decode(data, validate=False)
    except (binascii.Error, ValueError) as e:
        raise VisionError("IMAGE_FORMAT_INVALID", f"base64 解码失败：{type(e).__name__}") from e
    if len(raw) > MAX_IMAGE_BYTES:
        raise VisionError("IMAGE_TOO_LARGE", f"单张图片超过 {MAX_IMAGE_BYTES // 1024}KB")
    mime = sniff_mime(raw)
    if not mime:
        raise VisionError("IMAGE_FORMAT_INVALID", "仅支持 PNG / JPEG / GIF / WebP")
    return raw, mime


def decode_images(images: list[VisualImage]) -> list[tuple[bytes, str]]:
    """校验数量与体积并解码全部图片。"""
    if len(images) > MAX_IMAGES:
        raise VisionError("IMAGE_TOO_MANY", f"最多上传 {MAX_IMAGES} 张运行截图")
    decoded = [_decode_one(i) for i in images]
    total = sum(len(raw) for raw, _ in decoded)
    if total > MAX_TOTAL_BYTES:
        raise VisionError("IMAGE_TOO_LARGE", f"图片总量超过 {MAX_TOTAL_BYTES // 1024}KB")
    return decoded


def image_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()[:16]


# ---------------------------------------------------------------------------
# 提示词与载荷
# ---------------------------------------------------------------------------
VISION_SYSTEM_PROMPT = """你是「AI 项目导师」的视觉证据观察器，唯一职责是**观察并提取事实**。

【只做观察，不做裁判】
- 只描述画面中实际存在的内容；不确定的内容放进 uncertain；
- 禁止评价界面美不美、配色是否合理、UI 是否高级、响应式是否完美；
- 禁止推断学生是否完成任务、禁止给出通过/不通过结论。

【输出格式】只输出一个合法 JSON：
{
  "facts": ["画面中观察到的事实，每条一句话"],
  "uncertain": ["无法从该截图确认的内容"],
  "task_relation": "relevant" | "irrelevant" | "unclear",
  "analysis_error": ""
}
task_relation 表示该截图与「当前任务」是否相关。"""


def build_vision_prompt(task_title: str, task_objective: str,
                        visual_conditions: list[str]) -> str:
    cond = "\n".join(f"- {c}" for c in visual_conditions) or "（本任务未声明视觉观察点）"
    return (
        f"【当前任务】{task_title}\n【任务目标】{task_objective}\n\n"
        f"【需要观察的要点】\n{cond}\n\n"
        "请观察下面这些运行截图，逐条给出你**实际看到**的事实（不要推测、不要评价设计）。"
    )


def build_vision_payload(model: str, provider: str, system_prompt: str,
                         user_text: str, images: list[tuple[bytes, str]],
                         use_json_mode: bool = True, use_detail: bool = True) -> dict:
    """构建 OpenAI 兼容的多模态请求载荷（唯一出口，provider 差异在此收口）。

    图片统一以 base64 data URL 内联——不落盘、不外链（外链要求图片公开可访问，与隐私冲突）。
    """
    content: list[dict] = [{"type": "text", "text": user_text}]
    for raw, mime in images:
        b64 = base64.b64encode(raw).decode("ascii")
        item: dict = {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
        if use_detail:
            # 截图验收只需"看到即算过"，low 会降采样到 512×512，显著降低 token 成本
            item["image_url"]["detail"] = "low"
        content.append(item)

    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "temperature": 0.2,
    }
    if use_json_mode:
        payload["response_format"] = {"type": "json_object"}
    payload.update(PROVIDER_VISION_OVERRIDES.get(provider, {}))
    return payload


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
async def analyze_images(images: list[VisualImage],
                         task_title: str,
                         task_objective: str,
                         visual_conditions: list[str],
                         model: str,
                         api_key: str,
                         base_url: str | None = None,
                         provider: str = "deepseek") -> VisualEvidence:
    """分析运行截图，返回结构化事实。

    永远不抛异常：任何失败都以 status=skipped/error 返回，由调用方决定忽略（fail-open）。
    """
    global _inflight

    # 1) 模型门控：不在白名单 → 直接跳过（不影响普通验收）
    if not is_vision_supported(model):
        return VisualEvidence(status="skipped", code="VISION_UNSUPPORTED", model=model,
                              message="当前模型未验证支持图片输入，已跳过视觉证据")
    if not images:
        return VisualEvidence(status="skipped", code="NO_IMAGE", model=model)
    if not api_key:
        return VisualEvidence(status="skipped", code="NO_API_KEY", model=model)

    # 2) 校验（数量/体积/格式）
    try:
        decoded = decode_images(images)
    except VisionError as e:
        return VisualEvidence(status="error", code=e.code, message=e.message,
                              count=len(images), model=model)

    hashes = [image_hash(raw) for raw, _ in decoded]
    total_bytes = sum(len(raw) for raw, _ in decoded)
    cache_key = "|".join(sorted(hashes)) + f"::{model}"

    # 3) 事实缓存（文本；命中不再调用模型）
    now = time.time()
    hit = _FACTS_CACHE.get(cache_key)
    if hit and now < hit[0]:
        f = hit[1]
        return VisualEvidence(status="ok", facts=f.facts, uncertain=f.uncertain,
                              task_relation=_norm_relation(f.task_relation),
                              count=len(decoded), bytes=total_bytes, image_hashes=hashes,
                              model=model, cached=True)

    # 4) 并发闸门：服务器仅 2 核 / 1.8GB，超出即跳过（排队会堆积内存）
    if _inflight >= MAX_CONCURRENT:
        return VisualEvidence(status="skipped", code="VISION_BUSY", model=model,
                              count=len(decoded), bytes=total_bytes, image_hashes=hashes,
                              message="视觉分析繁忙，已跳过（可稍后重新提交）")
    _inflight += 1
    start = time.time()
    try:
        facts = await _call_vision(model, api_key, base_url or DEFAULT_BASE_URL, provider,
                                   build_vision_prompt(task_title, task_objective, visual_conditions),
                                   decoded)
    except VisionError as e:
        return VisualEvidence(status="error", code=e.code, message=e.message,
                              count=len(decoded), bytes=total_bytes, image_hashes=hashes,
                              model=model, latency_ms=int((time.time() - start) * 1000))
    except Exception as e:  # noqa: BLE001 — 视觉失败绝不阻塞验收
        return VisualEvidence(status="error", code="VISION_FAILED",
                              message=f"{type(e).__name__}", count=len(decoded),
                              bytes=total_bytes, image_hashes=hashes, model=model,
                              latency_ms=int((time.time() - start) * 1000))
    finally:
        _inflight -= 1

    _cache_put(cache_key, facts)
    return VisualEvidence(status="ok", facts=facts.facts, uncertain=facts.uncertain,
                          task_relation=_norm_relation(facts.task_relation),
                          count=len(decoded), bytes=total_bytes, image_hashes=hashes,
                          model=model, latency_ms=int((time.time() - start) * 1000))


def is_vision_supported(model: str | None) -> bool:
    return bool(model) and str(model).strip() in VISION_WHITELIST


def _norm_relation(v: str) -> str:
    v = (v or "").strip().lower()
    return v if v in ("relevant", "irrelevant", "unclear") else "unclear"


def _cache_put(key: str, facts: VisualFacts) -> None:
    if len(_FACTS_CACHE) >= CACHE_MAX:
        for k in [k for k, (exp, _) in _FACTS_CACHE.items() if exp < time.time()]:
            _FACTS_CACHE.pop(k, None)
        if len(_FACTS_CACHE) >= CACHE_MAX:      # 仍满 → 淘汰最早过期的一条
            _FACTS_CACHE.pop(min(_FACTS_CACHE, key=lambda k: _FACTS_CACHE[k][0]), None)
    _FACTS_CACHE[key] = (time.time() + CACHE_TTL, facts)


async def _call_vision(model: str, api_key: str, base_url: str, provider: str,
                       user_text: str, images: list[tuple[bytes, str]]) -> VisualFacts:
    """调用视觉模型（服务端只转发，不做本地推理）。

    兼容性自愈：服务商若拒绝 response_format 或 detail 字段，自动去掉后重试一次；
    明确报"不支持图片"则抛 VISION_UNSUPPORTED（不做无意义重试）。
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    use_json, use_detail = True, True
    last_err = ""

    for _attempt in range(3):
        payload = build_vision_payload(model, provider, VISION_SYSTEM_PROMPT, user_text,
                                       images, use_json_mode=use_json, use_detail=use_detail)
        try:
            async with httpx.AsyncClient(timeout=VISION_TIMEOUT) as client:
                r = await client.post(url, headers=headers, json=payload)
        except httpx.RequestError as e:
            raise VisionError("VISION_FAILED", f"无法连接模型服务：{type(e).__name__}") from e

        if r.status_code == 200:
            data = r.json()
            text = data["choices"][0]["message"]["content"]
            try:
                obj = _extract_json(text)
                return VisualFacts.model_validate(obj)
            except (ValidationError, json.JSONDecodeError, KeyError) as e:
                last_err = f"输出不是合法 JSON：{type(e).__name__}"
                continue

        body = (r.text or "")[:400]
        low = body.lower()
        if r.status_code in (401, 403):
            raise VisionError("VISION_FAILED", "API Key 无效或已过期")
        if "not support image" in low or "不支持图片" in body or "does not support image" in low:
            raise VisionError("VISION_UNSUPPORTED", "该模型不支持图片输入")
        if r.status_code == 429:
            raise VisionError("VISION_TIMEOUT", "服务商限流，视觉分析已跳过")
        # 400 兼容自愈：逐次摘掉可选字段（别家可能不认 detail / response_format）
        if r.status_code == 400:
            if use_detail and "detail" in low:
                use_detail = False
                continue
            if use_json and "response_format" in low:
                use_json = False
                continue
            if use_detail or use_json:
                # 报错原因未明说：一次摘掉全部可选字段再试（避免因字段差异直接失败）
                use_detail, use_json = False, False
                continue
        snippet = re.sub(r"\s+", " ", body)[:120]   # 注意：不能在 f-string 表达式里写反斜杠（服务器为 Python 3.11）
        raise VisionError("VISION_FAILED", f"模型服务错误 HTTP {r.status_code}: {snippet}")

    raise VisionError("VISION_FAILED", last_err or "视觉分析重试后仍失败")
