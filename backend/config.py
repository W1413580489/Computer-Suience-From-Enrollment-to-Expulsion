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
GLOSSARY_FILE = DATA_DIR / "glossary.json"

ANSWERS_LOG = LOGS_DIR / "answers.jsonl"                   # 脱敏问答/反馈日志（FR-FB-03）
RATELIMIT_FILE = LOGS_DIR / "ratelimit.json"               # 文件级 IP 限额计数（FR-BY-IP-04）

# ---- 检索 ----
RETRIEVE_TOP_K = int(os.getenv("XKZ_TOP_K", "8"))          # FR-RT-03
MAX_CHUNKS_PER_DOC = int(os.getenv("XKZ_MAX_PER_DOC", "3"))  # 召回时单文档块数上限（多样性，FR-RT-06）
RETRIEVE_THRESHOLD = float(os.getenv("XKZ_THRESHOLD", "0.5"))  # FR-RT-04（v3 后仅用于 BM25 单路兜底）
# FR-RT-04 补充：BM25 原始分对中文常见问题词（怎么/什么）不敏感，
# 需同时满足「内容词命中」——查询中长度≥2 的非停用词至少命中 1 个，否则视为无相关内容
MAX_CHUNK_TEXT = 800                                       # FR-RT-03 单块截断

# ---- 多路召回加权融合（v3）----
# 五路召回：BM25 / 标题精确 / section_path / 关键词重叠 / 向量语义
# 使用加权 RRF (Reciprocal Rank Fusion) 融合，权重越大该路影响力越高
RECALL_WEIGHT_BM25 = float(os.getenv("XKZ_W_BM25", "1.0"))      # BM25 基础路
RECALL_WEIGHT_TITLE = float(os.getenv("XKZ_W_TITLE", "2.0"))    # 标题精确匹配（权重最高，标题命中最相关）
RECALL_WEIGHT_SECTION = float(os.getenv("XKZ_W_SECTION", "1.5"))  # section_path 层级匹配
RECALL_WEIGHT_OVERLAP = float(os.getenv("XKZ_W_OVERLAP", "1.0"))  # 关键词重叠度
RECALL_WEIGHT_VECTOR = float(os.getenv("XKZ_W_VECTOR", "1.5"))  # 向量语义匹配（弥补 BM25 词面局限）
RRF_K = int(os.getenv("XKZ_RRF_K", "60"))                       # RRF 常数，越大排名差异越平滑

# ---- Embedding + Reranker（v3）----
# 模型从 HuggingFace 下载，国内服务器设置环境变量 XKZ_HF_ENDPOINT=https://hf-mirror.com
EMBEDDING_MODEL = os.getenv("XKZ_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")  # ~95MB, 512维
RERANKER_MODEL = os.getenv("XKZ_RERANKER_MODEL", "BAAI/bge-reranker-base")     # ~278MB
EMBEDDING_CACHE = DATA_DIR / "embedding_cache.npy"   # 预计算的 chunk 向量缓存
RERANK_CANDIDATE_K = int(os.getenv("XKZ_RERANK_K", "20"))  # Reranker 精排候选数（召回 top-20 → 精排 top-k）
RERANK_ENABLED = os.getenv("XKZ_RERANK_ENABLED", "0") == "1"  # 默认关闭，低配服务器省600MB内存；设1启用

# ---- 平台兜底模型（FR-BY-MODEL）----
PLATFORM_API_KEY = os.getenv("XKZ_PLATFORM_API_KEY", "")   # 平台兜底 DeepSeek Key（不填则免费模式不可用）
PLATFORM_BASE_URL = os.getenv("XKZ_PLATFORM_BASE_URL", "https://api.deepseek.com/v1")
PLATFORM_MODEL = os.getenv("XKZ_PLATFORM_MODEL", "deepseek-v4-flash")

# ---- BYOK 服务商预设（OpenAI 兼容协议）----
PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-v4-flash"},
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

# ---- v3: 动态 System Prompt（按意图分类追加风格指令）----
# 基础 prompt 之上，根据 classify_intent 结果追加不同风格
INTENT_PROMPTS = {
    "policy": """

【当前问题类型：政策规章】
回答风格调整：
- 严格引用政策原文，不补充个人解读或经验性判断
- 回答末尾必须标注「⚠️ 以上为资料库收录的政策信息，具体执行请以学校最新通知为准」
- 涉及 GPA/学分/资格门槛等硬性指标时，用加粗强调数值
- 涉及内招/外招/港澳台侨差异时，分点列明各自适用条件
- 避免使用「应该」「大概」「可能」等模糊措辞""",

    "experience": """

【当前问题类型：经验心得】
回答风格调整：
- 用口语化、亲切的学长学姐口吻回答
- 可适当加入「学长建议」「过来人经验」等引导语
- 鼓励性表达，但不把个人经验绝对化（避免「一定要」「必须」）
- 可适当补充注意事项或常见误区
- 涉及主观感受时，明确标注「因人而异」""",

    "tool": """

【当前问题类型：工具与链接】
回答风格调整：
- 优先列出工具名称 + 链接/网址 + 一句话用途说明
- 结构化呈现：工具名（加粗）→ 链接 → 用途
- 涉及操作步骤时，用编号列表清晰列出每一步
- 涉及命令行操作时，用代码块格式展示命令
- 链接失效风险提示：如资料较旧，可提醒「链接可能失效，请以官方渠道为准」""",

    "org": """

【当前问题类型：组织介绍】
回答风格调整：
- 结构化介绍每个组织：名称（加粗）→ 性质 → 加入方式 → 联系方式
- 用列表形式清晰呈现多个组织
- 客观描述组织职能，不加主观评价
- 涉及招新时间/条件时，提醒「以当年招新通知为准」""",

    "life": """

【当前问题类型：生活娱乐】
回答风格调整：
- 推荐式表达，可适当加入主观评价（「这家口碑不错」「性价比高」）
- 涉及排行/榜单时，保留原资料的排序
- 涉及价格/位置时，用加粗强调
- 提醒「口味因人而异，仅供参考」""",

    "auto": "",  # 无法判定意图，不追加额外指令，使用基础 prompt
}
