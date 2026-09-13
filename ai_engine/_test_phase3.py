# -*- coding: utf-8 -*-
"""
阶段 3 验收测试：DeepSeek 模型名更新（V4.1）+ 导师/问答共用同一份 API 配置 + 服务商容错。

覆盖：
  T3.1 模型名更新：DEFAULT_MODEL / /api/ai/config（单一 deepseek-flash，下线 v4-pro）
  T3.2 服务商容错：不支持 response_format=json_object 时自动降级重试一次
  T3.3 非 response_format 的 400 仍按 ProviderError 抛出（降级不能吞掉真实错误）
运行：python _test_phase3.py
"""
import asyncio
import json

import httpx
from fastapi.testclient import TestClient

import app as app_mod
from llm_client import DEFAULT_MODEL, EngineError, LLMClient, ProviderError

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


print("== T3.1 DeepSeek 模型名更新（V4.1） ==")
check("DEFAULT_MODEL = deepseek-flash", DEFAULT_MODEL == "deepseek-flash", f"got {DEFAULT_MODEL}")

client = TestClient(app_mod.app)
j = client.get("/api/ai/config").json()
models = [m["model"] for m in j["data"]["models"]]
check("config 暴露 deepseek-flash", "deepseek-flash" in models, str(models))
check("config 不再暴露 deepseek-v4-pro", "deepseek-v4-pro" not in models, str(models))
check("config 不再暴露旧名 deepseek-v4-flash", "deepseek-v4-flash" not in models, str(models))
check("config 标明配置来源（与导航「API 配置」同源）",
      j["data"].get("config_source") == "xkz_settings_v1", str(j["data"].get("config_source")))

import os  # noqa: E402
import sys  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
try:
    import config as backend_config  # noqa: E402
    check("backend PLATFORM_MODEL = deepseek-flash",
          backend_config.PLATFORM_MODEL == "deepseek-flash", backend_config.PLATFORM_MODEL)
    check("backend deepseek 预设模型 = deepseek-flash",
          backend_config.PROVIDERS["deepseek"]["model"] == "deepseek-flash")
except Exception as e:  # noqa: BLE001
    print(f"  ! 跳过 backend 校验：{e}")

print("== T3.2 服务商容错：不支持 json_object 时自动降级 ==")


class FakeResp:
    def __init__(self, status: int, text: str, body: dict | None = None):
        self.status_code = status
        self.text = text
        self._body = body or {"choices": [{"message": {"content": '{"criteria": []}'}}]}

    def json(self):
        return self._body


class FakeAsyncClient:
    calls: list = []

    def __init__(self, *a, **k):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, headers=None, json=None):
        FakeAsyncClient.calls.append(json.get("response_format"))
        if json.get("response_format"):
            # 模拟 qwen/自定义服务商：直接拒绝 response_format
            return FakeResp(400, '{"error":{"message":"Invalid parameter: response_format is not supported"}}')
        return FakeResp(200, "")


orig_client = httpx.AsyncClient
httpx.AsyncClient = FakeAsyncClient
try:
    c = LLMClient("sk-test", "https://api.example.com/v1", "some-custom-model")
    out = asyncio.run(c._call([{"role": "user", "content": "只输出 json"}]))
finally:
    httpx.AsyncClient = orig_client

check("第一次带 response_format，第二次自动去掉（共 2 次调用）",
      FakeAsyncClient.calls == [{"type": "json_object"}, None], str(FakeAsyncClient.calls))
check("降级后仍拿到模型输出", '"criteria"' in out, out[:60])
check("降级标记在实例上持久（后续调用不再带该参数）", c._use_json_mode is False)

print("== T3.3 其它 400 仍抛 ProviderError（不吞真实错误） ==")


class FakeAsyncClient400(FakeAsyncClient):
    calls: list = []

    async def post(self, url, headers=None, json=None):
        FakeAsyncClient400.calls.append(json.get("response_format"))
        return FakeResp(400, '{"error":{"message":"model not found"}}')


httpx.AsyncClient = FakeAsyncClient400
try:
    c2 = LLMClient("sk-test", "https://api.example.com/v1", "bad-model")
    err = None
    try:
        asyncio.run(c2._call([{"role": "user", "content": "json"}]))
    except ProviderError as e:
        err = e
finally:
    httpx.AsyncClient = orig_client

check("无关 400 不触发降级（只调用 1 次）", len(FakeAsyncClient400.calls) == 1, str(FakeAsyncClient400.calls))
check("无关 400 抛 ProviderError", err is not None and "HTTP 400" in str(err), str(err))
check("无关 400 不会把 json 模式关掉", c2._use_json_mode is True)

print()
if FAIL_LINES:
    print(f"FAILED: {len(FAIL_LINES)} 项未通过 → {FAIL_LINES}")
    raise SystemExit(1)
print(f"ALL PASSED: {PASS_COUNT} checks")
