# -*- coding: utf-8 -*-
"""
LLM 客户端：调用 OpenAI 兼容 chat/completions（JSON 模式）+ Pydantic 校验 + 失败重试。

V1 架构适配：
  - 使用响应服务商的 response_format={"type":"json_object"}（JSON 模式），服务商不支持时自动降级
  - 返回原始文本后，用 AiResponse / ReviewLLMOutput Pydantic 模型校验
  - 校验失败自动重试（把错误信息回传给模型，让它修正）
  - BYOK：每个请求携带用户自己的 API Key

v1.1 修订（JSON 容错加固）：
  - 行为级 max_tokens（不再依赖服务商默认输出上限）
  - 读取 finish_reason：截断（length）时加大额度重新完整请求，不做"续写残缺 JSON"
  - json-repair 作为第二防线（第一防线是 JSON mode）
  - review 严格语义校验：rubric_id 必须属于送审清单、evidence/reason 非空、逐条覆盖
  - teach 绝对兜底：全部失败后降级为纯文本回复，学生不再看到 500
"""
from __future__ import annotations

import json

import httpx
from pydantic import ValidationError

from schemas import AiResponse, Mode, ReviewLLMOutput

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-flash"  # DeepSeek V4.1（2026-09：V4 Flash/Pro 合并为 V4.1-Flash，官方模型名 deepseek-flash）

MAX_RETRIES = 2
# 只限制"对话历史"的长度；system prompt 永不因限长被丢弃（见 _trim 不变量）
HISTORY_CHAR_LIMIT = 6000

# 行为级输出上限（token）。初始建议值，按实测调优；review 用独立的值 REVIEW_MAX_TOKENS。
MAX_TOKENS_BY_BEHAVIOR = {
    "decompose": 3500,   # 拆解：字段最多（message/hint/leading_question/current_step…）
    "advance": 1500,     # 推进：只输出 message+current_step
    "debug": 2500,       # 调试：message+suspected_cause+verify_steps+diagnostic_question
}
DEFAULT_TEACH_MAX_TOKENS = 2048  # 未匹配到行为的兜底
REVIEW_MAX_TOKENS = 3000         # 评审链：逐条 criteria + evidence/reason

# json-repair 容错（第二防线）；未安装时降级为"无修复"（仍走重新请求/兜底路径）
try:  # noqa: E402  — 允许在常量区惰性导入
    import json_repair as _json_repair  # type: ignore
except ImportError:
    _json_repair = None


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
    """容错提取：先去 markdown 围栏，再尝试解析；失败时用 json-repair 修补（第二防线）。"""
    t = text.strip()
    if t.startswith("```"):
        lines = t.split("\n")
        lines = lines[1:] if lines else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    # 找到第一个 { 到最后一个 }（排除模型在 JSON 外的说明文字）
    start = t.find("{")
    end = t.rfind("}")
    if start >= 0 and end > start:
        t = t[start:end + 1]
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        if _json_repair is not None:
            try:
                return _json_repair.loads(t)
            except Exception:  # noqa: BLE001 — 修补失败也走下游重试/降级
                pass
        raise


def _semantic_validate_review(out: ReviewLLMOutput, allowed_rubric_ids: list[str]) -> str | None:
    """review 语义校验（严格）：repair/补值后的输出绝不能直接当正式评审。

    规则：
      - criteria 非空；
      - 每条 rubric_id 必须属于本次送审清单（现状 weight_of.get(id,1) 会静默容忍未知 id）；
      - evidence / reason 非空（评审铁律 2：每条判定必须给出证据来源）；
      - 送审 Rubric 必须逐条覆盖，不得漏判。
    返回错误描述或 None（通过）。
    """
    if not out.criteria:
        return "criteria 为空：必须对送审的每条 Rubric 给出判定"
    judged = []
    for c in out.criteria:
        if allowed_rubric_ids and c.rubric_id not in allowed_rubric_ids:
            return f"rubric_id={c.rubric_id!r} 不属于本次送审的验收标准，请只对清单内 Rubric 判定"
        if not (c.evidence or "").strip():
            return f"rubric_id={c.rubric_id} 缺少 evidence（必须注明判定依据）"
        if not (c.reason or "").strip():
            return f"rubric_id={c.rubric_id} 缺少 reason（必须写明判定理由）"
        judged.append(c.rubric_id)
    if allowed_rubric_ids:
        missing = [rid for rid in allowed_rubric_ids if rid not in judged]
        if missing:
            return "以下 Rubric 未给出判定：" + "、".join(missing)
    return None


class LLMClient:
    def __init__(self, api_key: str, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or DEFAULT_MODEL
        # 2026-09：导师页改为复用「API 配置」的服务商（可能是 qwen / kimi / GLM / 自定义），
        # 部分 OpenAI 兼容服务商不支持 response_format=json_object → 首次被拒后自动降级，
        # 仅靠提示词约束 JSON（下游仍有 Pydantic 校验 + 重试兜底，安全性不降低）。
        self._use_json_mode = True

    async def _call(self, messages: list[dict], *, max_tokens: int | None = None,
                    json_mode: bool | None = None) -> dict:
        """调用上游，返回 {"content": str, "finish_reason": str | None}（不流式，便于结构化校验）。

        json_mode：None → 沿用 self._use_json_mode；False → 强制纯文本（teach 兜底用）。
        """
        use_json = self._use_json_mode if json_mode is None else json_mode
        payload = {
            "model": self.model,
            "messages": _trim(messages),
            "temperature": 0.4,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if use_json:
            payload["response_format"] = {"type": "json_object"}
        # 请求前置校验：服务商硬约束在发送前本地拦截（仅 JSON 模式需要）
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
        if r.status_code == 400 and self._use_json_mode and "response_format" in r.text.lower():
            # 该服务商/模型不支持 JSON 模式 → 关闭后重试一次（避免学生一换模型就报错）
            self._use_json_mode = False
            return await self._call(messages, max_tokens=max_tokens, json_mode=json_mode)
        if r.status_code in (401, 403):
            raise PermissionError("API Key 无效或已过期")
        if r.status_code == 429:
            raise TimeoutError("服务商限流，请稍后重试")
        if r.status_code != 200:
            raise ProviderError(f"模型服务错误 HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content") or ""
        if not content.strip():
            # 推理型服务商可能把正文放 reasoning_content，正文为空时兜底读取
            content = (msg.get("reasoning_content") or "").strip()
        if not content:
            raise ProviderError("模型未返回任何文本内容")
        finish_reason = data["choices"][0].get("finish_reason") or ""
        return {"content": content, "finish_reason": finish_reason or None}

    async def review(self, messages: list[dict], *, max_tokens: int | None = None,
                     allowed_rubric_ids: list[str] | None = None) -> ReviewLLMOutput:
        """调用并校验评审输出（ReviewLLMOutput：只含逐条 criteria 判定）。

        V2 修改 6（输出漂移治理）：LLM 只输出逐条判定，score/status 由代码聚合。
        v1.1：解析/校验 + 语义校验（严格），失败把错误回传模型重试。
        """
        last_error = None
        current_messages = list(messages)
        for _attempt in range(MAX_RETRIES):
            raw = await self._call(current_messages, max_tokens=max_tokens)
            try:
                obj = _extract_json(raw["content"])
                if raw.get("finish_reason") == "length":
                    # 输出被截断：不接受 repair 补全的残缺结果（可能截断半句话），
                    # 一律回退到原始请求、加大额度重新完整生成。
                    raise json.JSONDecodeError(
                        "输出在长度限制处被截断（finish_reason=length），需加大额度重新生成",
                        raw["content"], 0)
                out = ReviewLLMOutput.model_validate(obj)
            except (ValidationError, json.JSONDecodeError, KeyError) as e:
                last_error = e
                if raw.get("finish_reason") == "length":
                    max_tokens = (max_tokens or REVIEW_MAX_TOKENS) * 2
                    current_messages = list(messages)
                    continue
                current_messages = current_messages + [
                    {"role": "assistant", "content": raw["content"]},
                    {"role": "user", "content": (
                        f"你的上一次回答不是合法 JSON 或缺少必要字段。校验错误：{e}\n"
                        "请重新只输出符合 ReviewLLMOutput schema 的合法 JSON，不要输出任何额外文字。"
                    )},
                ]
                continue
            # —— 语义校验（严格）：repair 补出来的值绝不直接当正式评审 ——
            sem_err = _semantic_validate_review(out, allowed_rubric_ids or [])
            if sem_err:
                last_error = ValueError(sem_err)
                current_messages = current_messages + [
                    {"role": "assistant", "content": raw["content"]},
                    {"role": "user", "content": (
                        f"你的上一次评审输出未通过语义校验：{sem_err}\n"
                        "请重新逐条输出判定 JSON：只针对送审 Rubric 清单逐条判定，"
                        "每条必须带 evidence（判定依据）与 reason（判定理由）。不要输出额外文字。"
                    )},
                ]
                continue
            return out
        raise EngineError(f"模型连续 {MAX_RETRIES} 次输出非法 JSON：{last_error}")

    async def teach(self, messages: list[dict], mode: Mode,
                    *, max_tokens: int | None = None) -> AiResponse:
        """调用并校验结构化输出。每轮校验失败后把错误回传模型重试。

        v1.1：
          - 截断（finish_reason=length）→ 回到原始请求、加大 max_tokens 重新完整输出；
          - 全部失败后绝对兜底：纯文本回复（学生不再看到 500）。
        """
        last_error = None
        current_messages = list(messages)
        for _attempt in range(MAX_RETRIES):
            raw = await self._call(current_messages, max_tokens=max_tokens)
            try:
                obj = _extract_json(raw["content"])
                if raw.get("finish_reason") == "length":
                    # 输出被截断：不接受 repair 补全的残缺结果（可能截断半句话），
                    # 一律回退到原始请求、加大额度重新完整生成。
                    raise json.JSONDecodeError(
                        "输出在长度限制处被截断（finish_reason=length），需加大额度重新生成",
                        raw["content"], 0)
                obj["mode"] = mode.value
                return AiResponse.model_validate(obj)
            # TypeError：模型输出无对象的 JSON 数组（如 []）时 _extract_json 返回 list，
            # obj["mode"] 会抛 TypeError，必须一并捕获走重试，否则直接 500。
            except (ValidationError, json.JSONDecodeError, KeyError, TypeError) as e:
                last_error = e
                if raw.get("finish_reason") == "length":
                    # 输出被截断：重置为原始请求（不带残缺 JSON），仅加大额度重新完整输出。
                    # 不做"续写残缺 JSON"——不同服务商对半截 assistant 内容的续写行为不一致。
                    max_tokens = (max_tokens or DEFAULT_TEACH_MAX_TOKENS) * 2
                    current_messages = list(messages)
                    continue
                current_messages = current_messages + [
                    {"role": "assistant", "content": raw["content"]},
                    {"role": "user", "content": (
                        f"你的上一次回答不是合法 JSON 或缺少必要字段。校验错误：{e}\n"
                        "请重新只输出一个符合 schema 的合法 JSON 对象，不要输出任何额外文字。"
                    )},
                ]

        # —— 绝对兜底：纯文本回复（学生永远拿到回答，不再 500）——
        fallback_messages = current_messages + [
            {"role": "user", "content": (
                "模型结构化输出连续失败。请忽略之前的 JSON 要求，直接给这位学生一句有帮助的纯文本回复："
                "简要说明当前状态 + 明确的下一步。不要输出任何 JSON 结构、不要代码块、不要任何额外说明。"
            )},
        ]
        # 服务商侧故障（PermissionError/TimeoutError/ProviderError）原样透传，由上游错误分类漏斗处理
        raw = await self._call(fallback_messages,
                               max_tokens=(max_tokens or DEFAULT_TEACH_MAX_TOKENS),
                               json_mode=False)
        text = (raw.get("content") or "").strip()
        if not text:
            raise EngineError(f"模型连续 {MAX_RETRIES} 次输出非法 JSON：{last_error}")
        return AiResponse(mode=mode, message=text[:800])