# -*- coding: utf-8 -*-
"""
文件级 IP 限额（FR-BY-IP-01~07）。
存储：logs/ratelimit.json
  {"daily": {"2026-08-04": {"1.2.3.4": 7}}, "minute": {"1.2.3.4": [ts, ts, ...]}}
MVP 用文件 + 进程内锁，重启后每日计数保留、分钟窗口自然失效。
"""
import json
import threading
import time
from datetime import date

import config

_lock = threading.Lock()


def _load() -> dict:
    if config.RATELIMIT_FILE.exists():
        try:
            with open(config.RATELIMIT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"daily": {}, "minute": {}}


def _save(data: dict):
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = config.RATELIMIT_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    tmp.replace(config.RATELIMIT_FILE)


def get_client_ip(request) -> str:
    """FR-BY-IP-07：优先 X-Forwarded-For 最左 IP，否则 socket 远端 IP。"""
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_and_count(ip: str) -> tuple:
    """
    检查并计数一次提问。返回 (allowed: bool, reason: str|None)。
    白名单 IP 直接放行（FR-BY-IP-06）。
    """
    if ip in config.RATE_WHITELIST:
        return True, None

    now = time.time()
    today = date.today().isoformat()
    with _lock:
        data = _load()
        daily = data.setdefault("daily", {})
        minute = data.setdefault("minute", {})

        # 清理非当日计数，避免文件无限增长
        for d in list(daily.keys()):
            if d != today:
                del daily[d]

        day_count = daily.setdefault(today, {}).get(ip, 0)
        if day_count >= config.RATE_DAILY_LIMIT:
            return False, f"今日免费额度已用完（{config.RATE_DAILY_LIMIT} 次/日），可在设置页配置自己的 API Key 解除限制"

        window = [t for t in minute.get(ip, []) if now - t < 60]
        if len(window) >= config.RATE_MINUTE_LIMIT:
            minute[ip] = window
            _save(data)
            return False, f"提问太频繁（{config.RATE_MINUTE_LIMIT} 次/分钟），请稍后再试；配置自己的 Key 可解除限制"

        window.append(now)
        minute[ip] = window
        daily[today][ip] = day_count + 1
        _save(data)
    return True, None
