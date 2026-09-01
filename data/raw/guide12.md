# RAG知识库问答实战指南

在前面的实战篇中，我们用 AI 完成了一个网站的开发、美化和部署。但那个网站只有静态页面和导航功能，距离智能助手还差知识库问答。

完整的 RAG 流程包含以下环节：

> 1. 数据准备：收集原始文档，清洗后切成小块（分块）
> 2. 向量化：将每个文本块编码为向量（嵌入向量）
> 3. 检索：用户提问时，从知识库中找到最相关的文本块
> 4. 融合：多路检索结果合并排序
> 5. 生成：将检索结果作为参考资料，交给 AI 生成回答

## 第一节：RAG 准备工作

本节目的：了解 RAG 的完整工作流程，准备好开发环境。

RAG（Retrieval-Augmented Generation，检索增强生成）是一种让 AI 模型先查资料再回答的技术方案。它的核心流程是：用户提问 → 从知识库中检索相关文档 → 将检索结果作为参考资料交给 AI → AI 基于参考资料生成回答。

纯 AI 模型的知识存在截止日期，也无法了解你特定的业务知识，RAG 解决了这个问题，让 AI 在回答之前先查你的知识库，确保回答基于你提供的材料。

## 操作流程

以 XKZ-Agent 项目为例！不要直接抄。

### 1.安装 Python 依赖

```bash
pip install numpy rank-bm25 jieba
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers huggingface-hub
pip install fastapi uvicorn httpx pydantic
pip install sse-starlette
```

### 2.下载嵌入模型

嵌入模型用于将文本转换为向量。推荐使用 BAAI/bge-small-zh-v1.5，中文效果好，模型体积小（约 95MB），CPU 即可运行。

```bash
# 国内服务器建议设置镜像加速
export HF_ENDPOINT=https://hf-mirror.com
```

### 3.项目目录结构

建议按以下结构组织项目：

```text
your-project/
├── backend/
│   ├── config.py          # 集中配置
│   ├── embedding.py       # 嵌入模型服务
│   ├── retrieval.py       # 检索核心
│   └── main.py            # API 网关
├── data/
│   ├── raw/               # 原始文档
│   ├── chunks.jsonl       # 分块结果
│   └── embedding_cache.npy # 向量缓存
└── scripts/
    └── chunker.py         # 分块工具
```

## 验收标准

- [ ] 了解 RAG 是什么，以及它解决了什么问题
- [ ] Python 环境配置完成，能成功导入 transformers 和 torch
- [ ] 嵌入模型下载成功

## 第二节：数据准备与分块

## 操作流程

### 1.文档收集与整理

知识库的质量直接决定了 RAG 系统的效果。首先需要收集原始文档。常见的文档来源：

> - 飞书文档/知识库：通过 lark-cli 批量导出为 Markdown
> - 本地 Markdown 或文本文件
> - 网页内容：爬取后转为 Markdown
> - PDF/Word：转换为 Markdown 后使用

建议维护一份文档清单，记录每个文档的元信息（你对于某个问题没有调查，就停止你对于某个问题的发言权。《毛泽东选集》即我们常说的，没有调查，就没有发言权。该图片位于介绍文档收集与整理操作流程中"结构化语义分块"部分，用以强调在数据准备与分块环节中，对文档进行结构化语义分块的重要性，即原始文档需切成适当大小的文本块，以适应检索需求）。

### 2.结构化语义分块

原始文档不能直接用于检索，需要切成适当大小的文本块（chunk）。分块策略直接影响检索效果：块太大则检索精度低，块太小则丢失上下文。

推荐基于 Markdown 标题层级进行语义切分，确保每个块是完整的语义单元。但这代表你可能需要手动列出标题，以下是 XKZ-Agent 项目中的分块器核心逻辑：

```python
import json
import re
from pathlib import Path

CHUNK_MAX = 600       # 目标块最大字符数
CHUNK_MIN = 30        # 最小块字符数
CHUNK_OVERLAP = 80    # 块间重叠字符数，避免边界上下文断裂

def clean_markdown(text: str) -> str:
    """清洗 Markdown：移除 HTML 标签、Markdown 标记、导航噪音行"""
    # 移除 HTML 标签
    html_tags = re.compile(r"</?(?:img|figure|source|cite|callout|blockquote|table|div|p|b|i|br|h[1-6])[^>]*/?>", re.IGNORECASE)
    text = html_tags.sub("", text)
    # 移除 Markdown 链接标记，保留文字
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # 移除粗体/斜体/行内代码标记
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # 移除列表/引用前导符
    text = re.sub(r"^\s*[-*+>]\s+", "", text, flags=re.MULTILINE)
    # 合并多余空行
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def chunk_document(filepath: Path, doc_title: str, source_url: str) -> list[dict]:
    """基于 Markdown 标题层级进行语义切分"""
    raw = filepath.read_text(encoding="utf-8")
    clean = clean_markdown(raw)

    header_stack = [doc_title]  # 标题路径栈，如 ["首页", "新生指南", "入学准备"]
    chunks = []
    buf = []
    chunk_idx = 0
    last_tail = ""  # 上一块尾部文本，用于构造重叠窗口

    def section_path() -> str:
        return " > ".join(header_stack)

    def flush():
        nonlocal buf, chunk_idx, last_tail
        text = "\n".join(buf).strip()
        if not text or len(text) < CHUNK_MIN:
            return
        # 超过上限按段落边界拆
        if len(text) > CHUNK_MAX:
            paragraphs = re.split(r"\n{2,}", text)
            sub_buf = ""
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                if sub_buf and len(sub_buf) + len(p) + 2 > CHUNK_MAX:
                    chunk_text = _apply_overlap(sub_buf.strip(), last_tail) if sub_buf.strip() else ""
                    if chunk_text:
                        chunks.append(make_chunk(chunk_text, chunk_idx))
                        chunk_idx += 1
                        last_tail = sub_buf.strip()[-CHUNK_OVERLAP:]
                    sub_buf = ""
                sub_buf = (sub_buf + "\n\n" + p).strip() if sub_buf else p
            if sub_buf and len(sub_buf.strip()) >= CHUNK_MIN:
                chunk_text = _apply_overlap(sub_buf.strip(), last_tail)
                chunks.append(make_chunk(chunk_text, chunk_idx))
                chunk_idx += 1
        else:
            chunk_text = _apply_overlap(text, last_tail)
            chunks.append(make_chunk(chunk_text, chunk_idx))
            chunk_idx += 1
        buf.clear()

    def make_chunk(text: str, idx: int) -> dict:
        return {
            "id": f"{filepath.stem}_{idx:03d}",
            "doc": doc_title,
            "section": header_stack[-1],
            "section_path": section_path(),
            "text": text,
            "source_url": source_url,
            "chunk_size": len(text),
        }

    lines = clean.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buf:
                buf.append("")
            continue
        # 检测标题行
        if re.match(r"^#{1,3}\s+\S", stripped):
            m = re.match(r"^(#{1,3})\s+(.+)", stripped)
            level = len(m.group(1))
            h_text = m.group(2).strip()
            # 切换章节时刷新上一块
            flush()
            last_tail = ""
            # 维护标题栈
            while len(header_stack) > level:
                header_stack.pop()
            if len(header_stack) < level:
                header_stack.append(h_text)
            else:
                header_stack[-1] = h_text
            continue
        buf.append(stripped)

    flush()
    return chunks


def _apply_overlap(text: str, prev_tail: str) -> str:
    """为当前块前部拼接上一块尾部，形成重叠窗口"""
    if not prev_tail:
        return text
    # 找一个干净的断点
    cut = prev_tail
    for sep in ["。", "；", "，", " ", "\n"]:
        idx = prev_tail.rfind(sep)
        if idx >= 0:
            cut = prev_tail[idx + len(sep):]
            break
    if cut:
        return f"[上文] {cut}\n\n{text}"
    return text
```

语义分块可**按段落/固定长度/语义分块**，你可以让 AI 判断分块的方法。

> #### 2.1 XKZ-Agent 设计要点
>
> - **标题层级切分**：以 Markdown 的 # / ## / ### 为章节边界，确保每个块是完整的语义单元
> - **块大小控制**：600 字符上限，30 字符下限。太短则信息量不足，太长则降低检索精度
> - **块间重叠**：80 字符重叠窗口，以 [上文] 前缀标记，避免边界上下文断裂
> - **标题路径栈**：维护 section_path 层级路径，如"首页 > 新生指南 > 入学准备"，便于层级检索

### 2.生成 chunks.jsonl

运行分块脚本后，输出为 JSONL 格式（每行一个 JSON 对象）：

```json
{"id": "scholarship_000", "doc": "奖学金评定办法", "section": "申请条件", "section_path": "奖学金评定办法 > 申请条件", "text": "国家奖学金申请条件：...", "source_url": "", "chunk_size": 245}
{"id": "scholarship_001", "doc": "奖学金评定办法", "section": "评审流程", "section_path": "奖学金评定办法 > 评审流程", "text": "评审流程如下：...", "source_url": "", "chunk_size": 312}
```

每个块包含字段：

> - **id**：唯一标识，格式为"文档名_序号"
> - **doc**：所属文档标题
> - **section**：当前章节名称
> - **section_path**：从根到当前章节的完整路径
> - **text**：块文本内容
> - **source_url**：来源链接（可选）
> - **chunk_size**：字符数

## 验收标准

- [ ] 原始文档已收集并整理到 data/raw/ 目录
- [ ] 分块脚本运行成功，生成了 chunks.jsonl
- [ ] 能理解为什么需要标题层级切分和重叠窗口

## 第三节：搭建检索系统

本节目的：搭建多路召回 + 加权 RRF 融合的检索系统。

## 操作流程

### 1.嵌入模型服务

嵌入模型（Embedding Model）将文本转换为固定长度的向量，语义相近的文本在向量空间中距离更近。推荐使用 BAAI/bge-small-zh-v1.5，512 维向量，CPU 推理友好。

```python
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

# 加载模型（CPU 上用 FP32，FP16 在 CPU 无原生支持）
torch.set_num_threads(2)  # 限制线程数，降低内存峰值
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-zh-v1.5")
model = AutoModel.from_pretrained("BAAI/bge-small-zh-v1.5")
model.eval()


def mean_pooling(token_embeddings, attention_mask):
    """BGE 使用 mean pooling + attention_mask"""
    mask = attention_mask.unsqueeze(-1).float()
    summed = torch.sum(token_embeddings * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def encode(texts: list[str], batch_size: int = 32, is_query: bool = False) -> np.ndarray:
    """编码文本列表，返回 L2 归一化后的向量矩阵 [N, dim]"""
    # BGE 查询需加前缀
    if is_query:
        texts = [f"为这个句子生成表示以用于检索相关文章：{t}" for t in texts]

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        encoded = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**encoded)
            embeddings = mean_pooling(outputs.last_hidden_state, encoded["attention_mask"])
        all_embeddings.append(embeddings.numpy())

    result = np.vstack(all_embeddings)
    # L2 归一化，后续点积即为余弦相似度
    norms = np.linalg.norm(result, axis=1, keepdims=True)
    return result / norms
```

### 2.向量预计算与缓存

首次启动时，将所有 chunk 编码为向量矩阵并缓存到磁盘，后续启动秒级加载，避免每次重启都重新编码。

```python
import numpy as np
from pathlib import Path

CACHE_PATH = Path("data/embedding_cache.npy")

def build_vector_index(chunks: list[dict], embed_svc) -> np.ndarray | None:
    """预计算所有 chunk 的向量矩阵，优先读缓存"""
    # 尝试读缓存
    if CACHE_PATH.exists():
        cached = np.load(CACHE_PATH)
        if cached.shape[0] == len(chunks):
            print(f"已加载向量缓存 {cached.shape}")
            return cached
        print("缓存行数与 chunks 数不一致，重新编码")

    # 现场编码
    print(f"开始编码 {len(chunks)} 个 chunk...")
    texts = [c["text"] for c in chunks]
    vectors = embed_svc.encode(texts, batch_size=32, is_query=False)
    if vectors is not None:
        np.save(CACHE_PATH, vectors)
        print(f"编码完成，缓存已写入 {CACHE_PATH}")
    return vectors
```

### 3.BM25 关键词检索

BM25 是一种基于词频的检索算法，是传统搜索引擎的核心。它不依赖深度学习，计算速度快，特别适合精确匹配场景（如政策条款中的关键词）。

```python
from rank_bm25 import BM25Okapi
import jieba

def tokenize(text: str) -> list[str]:
    """分词，过滤纯标点/空白 token"""
    return [t for t in jieba.lcut(text)
            if t.strip() and any(ch.isalnum() for ch in t)]

def build_bm25_index(chunks: list[dict]) -> BM25Okapi:
    """构建 BM25 索引，将标题和章节路径词重复 3 次增强权重"""
    corpus = []
    for c in chunks:
        text = (
            c["text"]
            + " " + (c.get("section_path", c.get("section", "")) + " ") * 3
            + " " + (c.get("section", "") + " ") * 3
            + " " + (c.get("doc", "") + " ") * 3
        )
        corpus.append(tokenize(text))
    # k1=1.2, b=0.5 适合中文短文本场景
    return BM25Okapi(corpus, k1=1.2, b=0.5)
```

### 4.多路加权 RRF 融合

单一检索方式（如只用 BM25 或只用向量检索）都有局限性。BM25 擅长精确匹配但无法理解语义，向量检索擅长语义匹配但可能漏掉精确关键词，多路召回 + 融合可以取长补短。

RRF（Reciprocal Rank Fusion）是一种简单但有效的融合算法，不依赖分数绝对值，而是基于排名进行融合：

```python
def fuse_results(recall_lists: list[list], weights: list[float], rrf_k: int = 60, top_k: int = 8) -> list:
    """加权 RRF 融合多路召回结果
    RRF_score(d) = Σ w_i / (k + rank_i(d) + 1)
    """
    fused_scores = {}
    for recall_list, weight in zip(recall_lists, weights):
        for rank, (idx, _) in enumerate(recall_list):
            rrf_score = weight / (rrf_k + rank + 1)
            fused_scores[idx] = fused_scores.get(idx, 0.0) + rrf_score

    ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
```

### 5.五路召回配置

以 XKZ-Agent 项目为例，使用五路召回，每路有不同权重：

- **BM25 基础路**（权重 1.0）：基于词频的通用匹配
- **标题精确匹配**（权重 2.0）：查询词命中文档/章节标题，最相关，权重最高
- **章节路径匹配**（权重 1.5）：查询词出现在章节路径中
- **关键词重叠**（权重 1.0）：Jaccard 相似度，衡量词集重叠程度
- **向量语义匹配**（权重 1.5）：嵌入向量余弦相似度，弥补 BM25 词面局限

### 6.查询预处理

用户输入的问题通常是口语化的，直接用于检索效果不佳。需要进行预处理。

### 7.查询规范化

将口语化表达转为标准术语，便于 BM25 精确匹配：

```python
import re

def normalize_query(query: str) -> str:
    """将口语化表达转为标准术语"""
    patterns = [
        (r"考.{0,2}研", "考研"),
        (r"保.{0,2}研", "保研"),
        (r"绩点|GPA", "绩点"),
        (r"选.{0,2}课", "选课"),
        (r"奖学.{0,2}金", "奖学金"),
        (r"补.{0,2}考", "补考"),
        (r"重.{0,2}修", "重修"),
        (r"军.{0,2}训", "军训"),
        (r"入.{0,2}党", "入党"),
        (r"社.{0,2}团", "社团"),
    ]
    result = query
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)
    return result
```

> `r"考.{0,2}研"`
> `.{0,2}`：中间可以夹 0～2 个任意字符，可以匹配：考研、考个研、考一下研 → 全部统一替换成 `考研`。但极端情况会误替换，而且没有最长匹配优先，只做替换，不做分词。你可以再优化。

### 8.同义词扩展

将同义词追加到查询中，提高召回率：

```python
synonyms = {
    "选课": ["选课", "选课推荐", "课程推荐"],
    "考研": ["考研", "研究生考试", "考研准备"],
    "保研": ["保研", "推免", "推荐免试"],
    "绩点": ["绩点", "GPA", "成绩"],
    "宿舍": ["宿舍", "住宿", "寝室"],
    "奖学金": ["奖学金", "奖学金评定"],
    "实习": ["实习", "实践", "实习经历"],
    "毕业": ["毕业", "毕设", "毕业设计"],
}

def expand_query(query: str) -> str:
    """查询扩展：将同义词追加到原始查询"""
    normalized = normalize_query(query)
    terms = [t for t in jieba.lcut(normalized) if len(t) >= 2]
    expansions = []
    for t in terms:
        if t in synonyms:
            for syn in synonyms[t]:
                if syn not in normalized:
                    expansions.append(syn)
    if expansions:
        return normalized + " " + " ".join(expansions[:3])  # 最多扩展 3 个词
    return normalized
```

### 9.停用词过滤

常见疑问词和语气词不参与相关性打分，避免干扰：

```python
STOPWORDS = {
    "什么", "怎么", "怎么样", "怎样", "如何", "为什么", "为啥", "哪些",
    "哪里", "多少", "吗", "嘛", "呢", "啊", "吧", "哦", "呀", "的", "了",
    "是", "有", "能", "会", "可以", "请问", "一下", "这", "那",
}

def content_terms(query: str) -> list[str]:
    """提取查询中的内容词：非停用词"""
    return [t for t in jieba.lcut(query) if t not in STOPWORDS and t.strip()]
```

### 10.完整检索流程

将所有环节串联起来：

```python
def search(query: str, top_k: int = 8) -> list[dict]:
    """完整检索流程：预处理 → 多路召回 → RRF 融合 → 排序 → 输出"""
    # 1. 查询预处理
    normalized = normalize_query(query)
    expanded = expand_query(query)

    # 2. 多路召回
    recall_k = max(top_k * 2, 20)  # 召回更多候选
    bm25_results = bm25_recall(tokenize(expanded), recall_k)
    title_results = title_match_recall(content_terms(normalized), recall_k)
    section_results = section_path_recall(content_terms(normalized), recall_k)
    overlap_results = keyword_overlap_recall(content_terms(normalized), recall_k)
    vector_results = vector_recall(normalized, recall_k)  # 向量服务不可用时返回空

    # 3. 加权 RRF 融合
    recall_lists = [bm25_results, title_results, section_results, overlap_results]
    weights = [1.0, 2.0, 1.5, 1.0]
    if vector_results:  # 向量路有结果才纳入
        recall_lists.append(vector_results)
        weights.append(1.5)

    fused = fuse_results(recall_lists, weights, top_k=recall_k)

    # 4. 文档级去重（单文档最多 3 块，保证多样性）
    deduped = []
    per_doc = {}
    for idx, score in fused:
        doc = chunks[idx]["doc"]
        if per_doc.get(doc, 0) >= 3:
            continue
        per_doc[doc] = per_doc.get(doc, 0) + 1
        deduped.append(idx)
        if len(deduped) >= top_k:
            break

    # 5. 构建结果
    return [{
        "id": chunks[idx]["id"],
        "doc": chunks[idx]["doc"],
        "section": chunks[idx]["section"],
        "section_path": chunks[idx]["section_path"],
        "text": chunks[idx]["text"],
        "source_url": chunks[idx].get("source_url", ""),
    } for idx in deduped]
```

（该图片为检索场景的幽默梗图，用"鱼片"搜索却返回刺身海鲜，暗含检索结果不符合需求的情况，以此说明检索系统搭建中可能遇到的不理想结果。）

## 验收标准

- [ ] 嵌入模型加载成功，能正常编码文本
- [ ] BM25 索引构建成功
- [ ] 输入一个查询问题，能返回相关的知识库内容
- [ ] 理解"多路召回"和"RRF 融合"的基本思路

## 第四节：接入已有网站

本节目的：实现用户提问 → 检索 → AI 流式回答 → 展示引用的闭环。

## 操作流程

### 1.后端 API 设计

在已有的 FastAPI 后端中新增一个流式问答接口：

```python
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()


class AskRequest(BaseModel):
    question: str
    session_id: str | None = None
    history: list[dict] | None = None
    api_key: str | None = None
    provider: str | None = "deepseek"
    base_url: str | None = None
    model: str | None = None


def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.post("/api/ask")
async def ask(req: AskRequest):
    question = (req.question or "").strip()
    if not question:
        return JSONResponse({"ok": False, "error": {"code": "EMPTY_QUESTION", "message": "问题不能为空"}}, status_code=400)

    # 1. 检索知识库
    retriever = Retriever()
    results = retriever.search(question)

    if not results:
        async def no_content():
            yield sse({"type": "start"})
            yield sse({"type": "error", "code": "NO_CONTENT",
                       "message": "资料库未覆盖该问题"})
            yield sse({"type": "done"})
        return StreamingResponse(no_content(), media_type="text/event-stream")

    # 2. 构建引用信息
    citations = [
        {"id": i + 1, "title": r.get("section_path", f"{r['doc']}-{r['section']}"),
         "url": r["source_url"], "excerpt": r["text"][:80]}
        for i, r in enumerate(results)
    ]

    # 3. 组装参考资料块
    ref_block = "\n".join(
        f"[来源{i + 1}]（{r['section_path']}）: {r['text']}"
        for i, r in enumerate(results)
    )

    # 4. 组装 LLM 消息
    system_prompt = f"""你是一个智能助手，基于以下参考资料回答用户的问题。
核心规则：
1. 只依据「参考资料」回答，禁止编造
2. 若参考资料未覆盖问题，回复：「资料库未覆盖该问题」
3. 引用来源时标注 [来源1]、[来源2]
4. 回答末尾列出参考来源标题"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"<参考资料>\n{ref_block}\n</参考资料>\n\n问题：{question}"}
    ]

    # 5. 调用 LLM 流式返回
    async def stream():
        yield sse({"type": "start"})
        yield sse({"type": "citations", "citations": citations})

        # 调用 OpenAI 兼容 API
        import httpx
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {req.api_key or 'YOUR_KEY'}",
                         "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": messages,
                       "stream": True, "stream_options": {"include_usage": True}},
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    for choice in data.get("choices", []):
                        content = choice.get("delta", {}).get("content")
                        if content:
                            yield sse({"type": "token", "content": content})

        yield sse({"type": "done"})

    return StreamingResponse(stream(), media_type="text/event-stream")
```

#### 1.1 SSE 事件流设计

前端通过 SSE（Server-Sent Events）接收流式响应，事件类型：

- **start**：开始标志
- **citations**：引用来源列表（先于回答内容发送）
- **token**：流式回答文本片段
- **done**：结束标志
- **error**：错误信息

### 2.前端集成

#### 2.1 SSE 客户端实现

```typescript
// api/client.ts
export async function askStream(
  question: string,
  history: { role: string; content: string }[],
  apiKey?: string,
  onToken: (text: string) => void,
  onCitations: (citations: Citation[]) => void,
  onDone: () => void,
  onError: (err: string) => void,
  signal?: AbortSignal,
) {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      history,
      api_key: apiKey,
    }),
    signal,
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";  // 保留未完成的行

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = JSON.parse(line.slice(6));
      switch (data.type) {
        case "citations":
          onCitations(data.citations);
          break;
        case "token":
          onToken(data.content);
          break;
        case "done":
          onDone();
          break;
        case "error":
          onError(data.message);
          break;
      }
    }
  }
}
```

#### 2.2 聊天状态管理

```typescript
// stores/chatStore.ts
import { defineStore } from "pinia";

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

interface Citation {
  id: number;
  title: string;
  url: string;
  excerpt: string;
}

export const useChatStore = defineStore("chat", {
  state: () => ({
    messages: [] as Message[],
    loading: false,
    abortController: null as AbortController | null,
  }),

  actions: {
    async sendMessage(question: string, apiKey?: string) {
      this.messages.push({ role: "user", content: question });

      const assistantMsg: Message = { role: "assistant", content: "" };
      this.messages.push(assistantMsg);
      this.loading = true;

      const controller = new AbortController();
      this.abortController = controller;

      try {
        await askStream(
          question,
          this.messages.slice(-6).map(m => ({ role: m.role, content: m.content })),
          apiKey,
          (token) => { assistantMsg.content += token; },
          (citations) => { assistantMsg.citations = citations; },
          () => { this.loading = false; },
          (err) => {
            assistantMsg.content = `错误：${err}`;
            this.loading = false;
          },
          controller.signal,
        );
      } catch (e: any) {
        if (e.name !== "AbortError") {
          assistantMsg.content = `请求失败：${e.message}`;
        }
        this.loading = false;
      }
    },

    stopGeneration() {
      this.abortController?.abort();
      this.loading = false;
    },
  },
});
```

#### 2.3 问答界面组件

```vue
<!-- views/ChatView.vue -->
<template>
  <div class="chat-container">
    <div class="messages" ref="scrollRef">
      <div v-for="(msg, i) in chat.messages" :key="i"
           :class="['message', msg.role]">
        <div class="bubble">{{ msg.content }}</div>
        <div v-if="msg.citations?.length" class="citations">
          <span v-for="c in msg.citations" :key="c.id"
                class="citation" @click="openUrl(c.url)">
            [{{ c.id }}] {{ c.title }}
          </span>
        </div>
      </div>
      <div v-if="chat.loading" class="typing">思考中...</div>
    </div>

    <div class="input-bar">
      <input v-model="input" @keydown.enter="send"
             :disabled="chat.loading"
             placeholder="输入你的问题..." />
      <button @click="chat.stopGeneration()" v-if="chat.loading">
        停止
      </button>
      <button @click="send" v-else :disabled="!input.trim()">
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useChatStore } from "../stores/chatStore";

const chat = useChatStore();
const input = ref("");
const scrollRef = ref<HTMLElement>();

function send() {
  if (!input.value.trim() || chat.loading) return;
  chat.sendMessage(input.value.trim());
  input.value = "";
}
</script>
```

### 3.改造已有网站

将 RAG 问答功能集成到现有网站中，需要修改以下文件：

- **backend/main.py**：新增 /api/ask 端点（如上文所示）
- **backend/requirements.txt**：添加 httpx、sse-starlette 等依赖
- **frontend/src/api/client.ts**：新增 SSE 客户端
- **frontend/src/stores/chatStore.ts**：新增聊天状态管理
- **frontend/src/views/ChatView.vue**：新增问答页面
- **frontend/src/router/index.ts**：添加聊天页面路由

如果已有导航系统，在导航栏中增加一个"智能问答"入口，指向聊天页面即可。如果你没有做网站，只是完成了 RAG 问答，那忽略。

## 验收标准

- [ ] 打开网站能正常提问，AI 能基于知识库内容回答
- [ ] 回答正确引用知识库中的来源，引用可点击查看
- [ ] 流式输出正常，用户体验流畅
- [ ] 知识库未覆盖的问题能正确提示"资料库未覆盖"

## 第五节：进阶优化

以上教程已经搭建了一个可用的 RAG 系统。以下优化方向可以根据实际需求选择性实现。

## 操作流程

### 1.意图分类

根据用户问题的类型，动态调整 System Prompt 的回答风格。例如，政策类问题要求严格引用原文，经验类问题可以用口语化回答。

```python
def classify_intent(query: str) -> str:
    """基于关键词规则的轻量意图分类"""
    rules = [
        ("policy", ["要求", "规定", "政策", "条件", "资格", "截止"]),
        ("tool", ["怎么用", "如何用", "工具", "软件", "链接", "网址"]),
        ("org", ["组织", "社团", "部门", "学生会", "加入", "招新"]),
        ("life", ["好吃", "推荐", "美食", "餐厅", "娱乐", "玩"]),
        ("experience", ["经验", "建议", "心得", "攻略", "感受", "难吗"]),
    ]
    q = query.lower()
    best_cat = "auto"
    best_hits = 0
    for cat, keywords in rules:
        hits = sum(1 for kw in keywords if kw in q)
        if hits > best_hits:
            best_hits = hits
            best_cat = cat
    return best_cat
```

### 2.Reranker 精排

在 RRF 融合之后，用专门的排序模型对候选结果进行重新排序，进一步提高相关性。推荐 BAAI/bge-reranker-base，但需要额外约 600MB 内存。

### 3.查询缓存

对相同或相似的问题，缓存检索结果，避免重复计算。使用 LRU 淘汰策略，但有缓存有效期。

### 4.问答日志与反馈

记录脱敏后的问答日志（仅记录问题 hash、耗时、命中数据源），并实现点赞/点踩功能，用于后续优化知识库质量。

### 5.自定义词典

jieba 分词对特定领域术语可能切分不当，添加自定义词典可提高分词准确率：

```python
import jieba
custom_words = [
    "内招生", "外招生", "港澳台侨", "绩点", "保研", "综测",
    "双学位", "辅修", "四六级", "通识课", "专业选修",
]
for w in custom_words:
    jieba.add_word(w)
```

同时也可以再参考一下：全流程踩坑复盘。

## 总结

至此，你已经完成了一个完整的 RAG 知识库问答系统的搭建和集成。回顾整个过程：

1. 理解了 RAG 的核心流程和原理
2. 准备好了原始文档，用语义分块器将其切分为知识库
3. 搭建了多路召回 + 加权 RRF 融合的检索系统
4. 接入了已有网站，实现了流式问答和引用展示
5. 部署到服务器，并了解了日常运维方法

RAG 系统的**效果高度依赖知识库的质量和检索配置的调优**。建议在上线后持续收集反馈，逐步优化分块策略、权重配置和查询预处理逻辑。