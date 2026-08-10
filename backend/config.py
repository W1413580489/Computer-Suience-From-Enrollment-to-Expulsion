# -*- coding: utf-8 -*-
"""
XKZ-Agent 后端配置（NFR-08：配置项集中于此）
所有项均可通过环境变量覆盖。平台兜底 Key 只从环境变量读取，绝不写死在代码里。
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent          # xkz-agent/
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

CHUNKS_FILE = DATA_DIR / "chunks.jsonl"
NAV_CONFIG_FILE = DATA_DIR / "nav_config.json"
CHANGELOG_FILE = DATA_DIR / "changelog.json"
HOT_QUESTIONS_FILE = DATA_DIR / "hot_questions.json"

ANSWERS_LOG = LOGS_DIR / "answers.jsonl"                   # 脱敏问答/反馈日志（FR-FB-03）
RATELIMIT_FILE = LOGS_DIR / "ratelimit.json"               # 文件级 IP 限额计数（FR-BY-IP-04）

# ---- 检索 ----
RETRIEVE_TOP_K = int(os.getenv("XKZ_TOP_K", "8"))          # FR-RT-03
MAX_CHUNKS_PER_DOC = int(os.getenv("XKZ_MAX_PER_DOC", "3"))  # 召回时单文档块数上限（多样性，FR-RT-06）
RETRIEVE_THRESHOLD = float(os.getenv("XKZ_THRESHOLD", "0.5"))  # FR-RT-04
# FR-RT-04 补充：BM25 原始分对中文常见问题词（怎么/什么）不敏感，
# 需同时满足「内容词命中」——查询中长度≥2 的非停用词至少命中 1 个，否则视为无相关内容
MAX_CHUNK_TEXT = 800                                       # FR-RT-03 单块截断

# ---- 平台兜底模型（FR-BY-MODEL）----
PLATFORM_API_KEY = os.getenv("XKZ_PLATFORM_API_KEY", "")   # 平台兜底 DeepSeek Key（不填则免费模式不可用）
PLATFORM_BASE_URL = os.getenv("XKZ_PLATFORM_BASE_URL", "https://api.deepseek.com/v1")
PLATFORM_MODEL = os.getenv("XKZ_PLATFORM_MODEL", "deepseek-chat")

# ---- BYOK 服务商预设（OpenAI 兼容协议）----
PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
    "qwen":     {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus"},
    "kimi":     {"base_url": "https://api.moonshot.cn/v1", "model": "moonshot-v1-8k"},
    "zhipu":    {"base_url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4-flash"},
}

# ---- IP 限额（FR-BY-IP）----
RATE_DAILY_LIMIT = int(os.getenv("XKZ_RATE_DAILY", "30"))      # 30 次/日/IP
RATE_MINUTE_LIMIT = int(os.getenv("XKZ_RATE_MINUTE", "5"))     # 5 次/分钟/IP
RATE_WHITELIST = {ip.strip() for ip in os.getenv("XKZ_IP_WHITELIST", "127.0.0.1,::1").split(",") if ip.strip()}

# ---- 其他 ----
MAX_HISTORY_ROUNDS = 6                                       # FR-QA-05
CORS_ORIGINS = [o.strip() for o in os.getenv(
    "XKZ_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
REQUEST_TIMEOUT = float(os.getenv("XKZ_REQUEST_TIMEOUT", "60"))   # 上游 API 请求超时（含流式）

SYSTEM_PROMPT = """你是「信科院智能助手」，基于暨南大学信科院学生共创的校园指南回答新生问题。

核心规则：
1. 只依据「参考资料」回答，禁止编造、禁止凭常识补充校园政策细节
2. 若参考资料未覆盖问题，回复：「资料库还没覆盖这个问题，建议咨询学长学姐或学校官方渠道」
3. 回答风格：简洁、口语化、面向大一新生；涉及政策时注明「以学校最新通知为准」
4. 涉及港澳台侨学生内容时，注意区分内招/外招政策差异

引用规范：
- 引用来源时标注 [来源1]、[来源2]，与参考资料编号一致
- 在回答末尾用「📌 参考来源：」列出引用的来源标题
- 同一来源只需引用一次，不要重复标注

结构化输出：
- 涉及步骤/流程时，用编号列表（①②③）清晰列出
- 涉及对比时，用表格或分点说明
- 涉及时间/地点/金额等关键信息时，用加粗强调"""
