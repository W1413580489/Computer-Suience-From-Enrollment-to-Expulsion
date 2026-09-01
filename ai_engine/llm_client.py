# -*- coding: utf-8 -*-
"""
LLM 客户端：调用 DeepSeek chat/completions（JSON 模式）+ Pydantic 校验 + 失败重试。

V1 架构适配：
  - 使用 DeepSeek 的 response_format={"type":"json_object"}（JSON 模式）
  - 返回原始文本后，用 AiResponse Pydantic 模型校验
  - 校验失败自动重试一次（把错误信息回传给模型，让它修正）
  - BYOK：每个请求携带用户自己的 API Key
"""
from __future__ import annotations

import json

import httpx
from pydantic import ValidationError

from schemas import AiResponse, Mode, ReviewEvaluation

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"

MAX_RETRIES = 2
# 只限制"对话历史"的长度；system prompt 永不因限长被丢弃（见 _trim 不变量）
HISTORY_CHAR_LIMIT = 6000


class ProviderError(RuntimeError):
    """模型服务商侧故障（网络不通 / HTTP 4xx/5xx）。与学生项目无关，绝不写入学生评审结果。"""


class EngineError(RuntimeError):
    """本平台自身的故障（请求构造违约 / 模型连续输出非法 JSON）。属于 ENGINE_ERROR。"""


# ---------------------------------------------------------------------------
# Provider Constraints：模型服务商硬约束表（数据驱动，新增约束=加一行表项）
# ---------------------------------------------------------------------------
PROVIDER_CONSTRAINTS: list[dict] = [
    {
        "id": "json_object_requires_json_keyword",
        # DeepSeek：response_format=json_object 时，请求消息中必须出现 "json" 字样
        "match": lambda payload: (payload.get("response_format") or {}).get("type") == "json_object",
        "check": lambda messages: "json" in "\n".join(
            m.get("content", "") for m in messages).lower(),
        "violation": "response_format=json_object 要求请求消息中必须包含 'json' 字样",
    },
]


def _validate_request(payload: dict, messages: list[dict]) -> None:
    """请求前置校验：在真正调用服务商前本地拦截违约请求（不浪费 API 调用）。"""
    for c in PROVIDER_CONSTRAINTS:
        try:
            if c["match"](payload) and not c["check"](messages):
                raise EngineError(f"[engine] 请求前置校验失败（{c['id']}）：{c['violation']}")
        except EngineError:
            raise
        except Exception:  # noqa: BLE001 — 约束项自身出错不阻塞主流程
            continue


def _trim(messages: list[dict], limit: int = HISTORY_CHAR_LIMIT) -> list[dict]:
    """截断消息历史。

    不变量（消息组装契约）：
      1. system 消息（第一条 role=system）永不丢弃——它承载角色规则与 JSON 输出契约；
      2. 限长只作用于其后的对话历史，从最新一条往前保留。
    """
    if not messages:
        return []
    system = messages[0] if messages[0].get("role") == "system" else None
    rest = messages[1:] if system else messages

    total = 0
    out: list[dict] = []
    for m in reversed(rest):
        total += len(m.get("content", ""))
        out.insert(0, m)
        if total > limit:
            break
    return ([system] + out) if system else out


def _extract_json(text: str) -> dict:
    """容错提取：去掉可能的 markdown 代码块围栏。"""
    t = text.strip()
    if t.startswith("```"):
        lines = t.split("\n")
        lines = lines[1:] if lines else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    # 找到第一个 { 到最后一个 }
    start = t.find("{")
    end = t.rfind("}")
    if start >= 0 and end > start:
        t = t[start:end + 1]
        return json.loads(t)
    return json.loads(text)


class LLMClient:
    def __init__(self, api_key: str, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or DEFAULT_MODEL

    async def _call(self, messages: list[dict]) -> str:
        """调用 DeepSeek，返回 model 的文本输出（不流式，便于结构化校验）。"""
        payload = {
            "model": self.model,
            "messages": _trim(messages),
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
        }
        # 请求前置校验：服务商硬约束在发送前本地拦截
        _validate_request(payload, payload["messages"])
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(
                connect=10.0, read=60.0, write=30.0, pool=10.0)) as client:
                r = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}",
                             "Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.RequestError as e:
            raise ProviderError(f"无法连接模型服务：{type(e).__name__}") from e
        if r.status_code in (401, 403):
            raise PermissionError("API Key 无效或已过期")
        if r.status_code == 429:
            raise TimeoutError("服务商限流，请稍后重试")
        if r.status_code != 200:
            raise ProviderError(f"模型服务错误 HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        return data["choices"][0]["message"]["content"]

    async def review(self, messages: list[dict]) -> ReviewEvaluation:
        """调用并校验评审输出（ReviewEvaluation）。校验失败把错误回传模型重试。"""
        last_error = None
        current_messages = list(messages)
        for attempt in range(MAX_RETRIES):
            raw = await self._call(current_messages)
            try:
                obj = _extract_json(raw)
                return ReviewEvaluation.model_validate(obj)
            except (ValidationError, json.JSONDecodeError, KeyError) as e:
                last_error = e
                current_messages = current_messages + [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": (
                        f"你的上一次回答不是合法 JSON 或缺少必要字段。校验错误：{e}\n"
                        "请重新只输出符合 ReviewEvaluation schema 的合法 JSON，不要输出任何额外文字。"
                    )},
                ]
        raise EngineError(f"模型连续 {MAX_RETRIES} 次输出非法 JSON：{last_error}")

    async def teach(self, messages: list[dict], mode: Mode) -> AiResponse:
        """调用并校验结构化输出。每轮校验失败后把错误回传模型重试。"""
        last_error = None
        current_messages = list(messages)
        for attempt in range(MAX_RETRIES):
            raw = await self._call(current_messages)
            try:
                obj = _extract_json(raw)
                obj["mode"] = mode.value
                return AiResponse.model_validate(obj)
            except (ValidationError, json.JSONDecodeError, KeyError) as e:
                last_error = e
                current_messages = current_messages + [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": (
                        f"你的上一次回答不是合法 JSON 或缺少必要字段。校验错误：{e}\n"
                        "请重新只输出一个符合 schema 的合法 JSON 对象，不要输出任何额外文字。"
                    )},
                ]
        raise EngineError(f"模型连续 {MAX_RETRIES} 次输出非法 JSON：{last_error}")