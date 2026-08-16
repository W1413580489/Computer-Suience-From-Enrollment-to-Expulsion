# -*- coding: utf-8 -*-
"""BM25 检索服务（FR-RT-01~05），v3：多路召回(BM25+标题+章节+重叠+向量) + RRF融合 + Reranker精排 + 父级上下文 + 查询缓存。"""
import json
import re
import threading
import time

import numpy as np
import jieba
from rank_bm25 import BM25Okapi

import config
from embedding import EmbeddingService, RerankerService


# ---------- 自定义词典（校园术语，防止 jieba 过度切分）----------
_CUSTOM_WORDS = [
    "内招生", "外招生", "港澳台侨", "选课", "考研", "保研", "绩点", "学分",
    "奖学金", "助学金", "军训", "社团", "学生会", "答辩", "论文", "导师",
    "实习", "就业", "校招", "秋招", "春招", "毕设", "毕业设计", "毕业论文",
    "暨南大学", "信科院", "信息科学技术学院", "番禺校区", "石牌校区",
    "珠海校区", "深圳校区", "华文学院", "内招生办", "外招生办",
    "补考", "重修", "缓考", "免修", "退课", "旁听", "双学位", "辅修",
    "四六级", "六级", "英语四级", "英语六级", "托福", "雅思",
    "宿舍", "食堂", "图书馆", "校医院", "体育课", "公选课", "专业选修",
    "必修课", "通识课", "核心课", "实验课", "上机课", "网课",
    "考研英语", "考研数学", "考研政治", "专业课", "复试", "调剂",
    "保研夏令营", "推免", "直博", "硕博连读", "学术型硕士", "专业型硕士",
    "学硕", "专硕", "全日制", "非全日制", "在职研究生",
    "入党", "党员", "积极分子", "团组织", "团支书",
    "奖学金评定", "国家奖学金", "励志奖学金", "学业奖学金",
    "综测", "综合测评", "素质拓展", "志愿服务", "社会实践",
]
for w in _CUSTOM_WORDS:
    jieba.add_word(w)


def _tokenize(text: str) -> list:
    # 过滤纯标点/空白 token，保留含字母数字的词
    return [t for t in jieba.lcut(text) if t.strip() and any(ch.isalnum() for ch in t)]


# 常见疑问词/语气词不参与相关性判定与打分
_STOPWORDS = {
    "什么", "怎么", "怎么样", "怎样", "如何", "为什么", "为啥", "咋", "哪些", "哪个",
    "哪儿", "哪里", "多少", "吗", "嘛", "呢", "啊", "吧", "哦", "呀", "的", "了", "是",
    "有", "能", "会", "可以", "请问", "一下", "办", "没", "不", "要", "该", "这", "那",
    "啥", "弄", "搞", "咋办", "咋样", "告诉", "知道", "说说", "讲讲", "介绍", "推荐",
    "想", "需要", "应该", "好", "比较", "关于", "对于", "的话", "而且", "然后",
}


def content_terms(query: str) -> list:
    """提取查询中的内容词：非停用词。长词（≥2 字）单独返回用于命中判定。"""
    terms = [t for t in _tokenize(query) if t not in _STOPWORDS]
    return terms


def _content_tokenize(text: str) -> list:
    """打分用分词：过滤停用词，避免"话痨"文档靠高频虚词拿到高分。"""
    return [t for t in _tokenize(text) if t not in _STOPWORDS]


# ---------- 同义词映射（查询扩展）----------
_SYNONYMS: dict[str, list[str]] = {
    "选课": ["选课", "选课推荐", "课程推荐"],
    "考研": ["考研", "研究生考试", "考研准备"],
    "保研": ["保研", "推免", "推荐免试"],
    "绩点": ["绩点", "GPA", "成绩"],
    "宿舍": ["宿舍", "住宿", "寝室"],
    "奖学金": ["奖学金", "奖学金评定"],
    "食堂": ["食堂", "吃饭", "餐厅"],
    "入党": ["入党", "党员", "党组织"],
    "社团": ["社团", "学生组织", "协会"],
    "实习": ["实习", "实践", "实习经历"],
    "毕业": ["毕业", "毕设", "毕业设计"],
    "补考": ["补考", "补考流程"],
    "重修": ["重修", "重修流程"],
    "军训": ["军训", "军事训练"],
    "综测": ["综测", "综合测评"],
}


def _normalize_query(query: str) -> str:
    """查询规范化：将口语化表达转为标准术语，便于 BM25 匹配。"""
    _PATTERNS = [
        # 口语化 → 标准术语（注意顺序：长的先匹配，避免部分匹配）
        (r"奖学.{0,2}金", "奖学金"),
        (r"综合测评", "综合测评"),
        (r"选.{0,2}课", "选课"),
        (r"考.{0,2}研", "考研"),
        (r"保.{0,2}研", "保研"),
        (r"入.{0,2}党", "入党"),
        (r"加.{0,2}社团", "社团"),
        (r"补.{0,2}考", "补考"),
        (r"重.{0,2}修", "重修"),
        (r"军.{0,2}训", "军训"),
        (r"综.{0,2}测", "综合测评"),
        (r"四.{0,2}级", "四级"),
        (r"六.{0,2}级", "六级"),
    ]
    result = query
    for pattern, replacement in _PATTERNS:
        result = re.sub(pattern, replacement, result)
    return result


def _expand_query(query: str) -> str:
    """查询扩展：将同义词追加到原始查询，提高召回率。"""
    # 先规范化，再扩展
    normalized = _normalize_query(query)
    terms = content_terms(normalized)
    expansions = []
    for t in terms:
        if t in _SYNONYMS:
            for syn in _SYNONYMS[t]:
                if syn not in normalized:
                    expansions.append(syn)
    if expansions:
        return normalized + " " + " ".join(expansions[:3])  # 最多扩展 3 个词
    return normalized


class Retriever:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.chunks = []
        with open(config.CHUNKS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.chunks.append(json.loads(line))
        # v2: 将 section_path 纳入 BM25 索引，提高层级路径匹配
        # v3: 标题/section_path 词重复 3 次增强权重，命中标题的块得分更高
        corpus = [
            _content_tokenize(
                c["text"]
                + " " + (c.get("section_path", c.get("section", "")) + " ") * 3
                + " " + (c.get("section", "") + " ") * 3
                + " " + (c.get("doc", "") + " ") * 3
            )
            for c in self.chunks
        ]
        self.bm25 = BM25Okapi(corpus, k1=1.2, b=0.5)  # 中文短文本优化：降低 b 减少长度归一化影响

        # v3: 构建 (doc, section_path) → 父级大块文本 索引，用于召回时补充上下文
        self._parent_index: dict[str, str] = {}
        for c in self.chunks:
            key = (c["doc"], c.get("section_path", c.get("section", "")))
            if key not in self._parent_index:
                self._parent_index[key] = c["text"]
            else:
                # 同一章节下的所有块拼接成父级大块
                self._parent_index[key] += "\n\n" + c["text"]

        # v3: 查询缓存 {normalized_query: (results, expire_ts)}
        self._query_cache: dict[str, tuple] = {}
        self._cache_ttl = 3600  # 缓存有效期 1 小时
        self._cache_max = 200   # 最多缓存 200 条查询

        # v3: 预计算 chunk 向量矩阵，用于向量召回
        self._chunk_vectors = None  # np.ndarray [N, dim] 或 None
        self._embedding_svc = EmbeddingService.get()
        if self._embedding_svc.available:
            self._build_vector_index()

        # v3: Reranker 精排服务（懒加载，首次调用时生效）
        self._reranker_svc = RerankerService.get()

    @classmethod
    def get(cls) -> "Retriever":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    # ---------- 多路召回（v3）----------
    def classify_intent(self, query: str) -> str:
        """v3: 基于关键词规则的轻量意图分类。
        返回 policy / experience / tool / org / life / auto。
        auto 表示无法判定，召回时不做类别加权（全库检索兜底）。
        """
        q = _normalize_query(query).lower()

        # 关键词规则表（按优先级从高到低）
        rules = [
            ("policy", [
                "要求", "规定", "政策", "条件", "资格", "截止", "学分要求",
                "绩点要求", "门槛", "申请条件", "保研要求", "考研要求",
                "双学位要求", "必修", "选修要求", "毕业要求", "学位要求",
                "奖学金条件", "资助", "奖助", "转专业条件", "学籍",
            ]),
            ("tool", [
                "怎么用", "如何用", "工具", "软件", "链接", "网站", "网址",
                "命令", "安装", "配置", "git", "github", "编辑器", "插件",
                "vpn", "校园网", "邮箱", "账号", "登录", "下载", "教程",
                "工具推荐", "效率工具",
            ]),
            ("org", [
                "组织", "社团", "战队", "部门", "学生会", "加入",
                "招新", "报名", "哪个社团", "有哪些社团", "组织介绍",
            ]),
            ("life", [
                "好吃", "推荐", "排行", "哪家", "美食", "餐厅", "食堂",
                "外卖", "娱乐", "玩", "电影", "k歌", "周边", "好吃",
            ]),
            ("experience", [
                "怎么样", "经验", "建议", "心得", "攻略", "感受",
                "难吗", "值得吗", "怎么准备", "如何准备", "备考",
                "复习", "面试经验", "笔试经验", "恋爱", "情感",
                "健身", "减肥", "增肌", "大学生活", "适应",
            ]),
        ]

        # 计算各类别命中数，取命中最多者
        best_cat = "auto"
        best_hits = 0
        for cat, keywords in rules:
            hits = sum(1 for kw in keywords if kw in q)
            if hits > best_hits:
                best_hits = hits
                best_cat = cat

        return best_cat

    def _build_vector_index(self):
        """预计算所有 chunk 的向量矩阵。优先读缓存，否则现场编码并写缓存。"""
        # 尝试读缓存
        if config.EMBEDDING_CACHE.exists():
            try:
                cached = np.load(config.EMBEDDING_CACHE)
                if cached.shape[0] == len(self.chunks):
                    self._chunk_vectors = cached
                    print(f"[Embedding] 已加载向量缓存 {cached.shape} (来自 {config.EMBEDDING_CACHE.name})")
                    return
                else:
                    print(f"[Embedding] 缓存行数 {cached.shape[0]} != chunks {len(self.chunks)}，重新编码")
            except Exception as e:
                print(f"[Embedding] 缓存读取失败: {e}，重新编码")

        # 现场编码（410 chunks，batch=32，CPU 约 30-60 秒）
        print(f"[Embedding] 开始编码 {len(self.chunks)} 个 chunk...")
        texts = [c["text"] for c in self.chunks]
        self._chunk_vectors = self._embedding_svc.encode(texts, batch_size=32, is_query=False)
        if self._chunk_vectors is not None:
            # 写缓存
            try:
                np.save(config.EMBEDDING_CACHE, self._chunk_vectors)
                print(f"[Embedding] 编码完成 {self._chunk_vectors.shape}，缓存已写入")
            except Exception as e:
                print(f"[Embedding] 缓存写入失败: {e}")
        else:
            print("[Embedding] 编码失败，向量召回将禁用")

    def _vector_recall(self, query: str, candidate_k: int) -> list:
        """向量语义召回路：查询向量与 chunk 向量点积（已归一化=余弦相似度）。返回 [(idx, score), ...]"""
        if self._chunk_vectors is None:
            return []
        query_vec = self._embedding_svc.encode_one(query, is_query=True)
        if query_vec is None:
            return []
        # 点积 = 余弦相似度（向量已 L2 归一化）
        scores = self._chunk_vectors @ query_vec
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:candidate_k]
        return [(idx, float(score)) for idx, score in ranked if score > 0]

    def _bm25_recall(self, query_tokens: list, candidate_k: int) -> list:
        """BM25 召回路：基于词频的语义匹配。返回 [(idx, score), ...]"""
        scores = self.bm25.get_scores(query_tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:candidate_k]
        return [(idx, score) for idx, score in ranked if score > 0]

    def _title_match_recall(self, query_terms: list, candidate_k: int) -> list:
        """标题精确匹配路：查询内容词出现在 doc/section 中的块。返回 [(idx, score), ...]"""
        if not query_terms:
            return []
        terms_lower = [t.lower() for t in query_terms]
        scores = []
        for idx, c in enumerate(self.chunks):
            title_text = (
                c.get("doc", "") + " " + c.get("section", "")
            ).lower()
            hit_count = sum(1 for t in terms_lower if t in title_text)
            if hit_count > 0:
                # 命中率：命中词数 / 查询词总数
                score = hit_count / len(terms_lower)
                scores.append((idx, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:candidate_k]

    def _section_path_recall(self, query_terms: list, candidate_k: int) -> list:
        """section_path 层级匹配路：查询词出现在章节路径中的块。返回 [(idx, score), ...]"""
        if not query_terms:
            return []
        terms_lower = [t.lower() for t in query_terms]
        scores = []
        for idx, c in enumerate(self.chunks):
            sp = c.get("section_path", "").lower()
            if not sp:
                continue
            hit_count = sum(1 for t in terms_lower if t in sp)
            if hit_count > 0:
                score = hit_count / len(terms_lower)
                scores.append((idx, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:candidate_k]

    def _keyword_overlap_recall(self, query_terms: list, candidate_k: int) -> list:
        """关键词重叠度路：查询词与块文本的 Jaccard 相似度。返回 [(idx, score), ...]"""
        if not query_terms:
            return []
        query_set = set(t.lower() for t in query_terms)
        scores = []
        for idx, c in enumerate(self.chunks):
            text_tokens = set(t.lower() for t in _tokenize(c["text"]))
            if not text_tokens:
                continue
            overlap = len(query_set & text_tokens)
            if overlap > 0:
                # Jaccard 相似度
                score = overlap / len(query_set | text_tokens)
                scores.append((idx, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:candidate_k]

    def _fuse_results(self, recall_lists: list, weights: list, top_k: int) -> list:
        """加权 RRF (Reciprocal Rank Fusion) 融合多路召回。
        RRF_score(d) = Σ w_i / (k + rank_i(d) + 1)
        返回 [(idx, fused_score), ...] 按 fused_score 降序。
        """
        fused_scores: dict[int, float] = {}
        for recall_list, weight in zip(recall_lists, weights):
            for rank, (idx, _) in enumerate(recall_list):
                rrf_score = weight / (config.RRF_K + rank + 1)
                fused_scores[idx] = fused_scores.get(idx, 0.0) + rrf_score
        ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def search(self, query: str, top_k: int = None) -> list:
        top_k = top_k or config.RETRIEVE_TOP_K
        # v3: 查询缓存命中检查（基于规范化后的 query）
        cache_key = _normalize_query(query).strip().lower()
        now = time.time()
        if cache_key in self._query_cache:
            results, expire_ts = self._query_cache[cache_key]
            if now < expire_ts:
                return results
            else:
                del self._query_cache[cache_key]

        # 查询预处理：规范化 + 扩展
        normalized = _normalize_query(query)
        expanded_query = _expand_query(query)
        query_tokens = _content_tokenize(expanded_query)
        query_terms = content_terms(normalized)

        # ---- 第一阶段：多路召回 ----
        # 召回更多候选（RERANK_CANDIDATE_K），交给 Reranker 精排
        recall_k = max(config.RERANK_CANDIDATE_K, top_k * 2)
        bm25_results = self._bm25_recall(query_tokens, recall_k)
        title_results = self._title_match_recall(query_terms, recall_k)
        section_results = self._section_path_recall(query_terms, recall_k)
        overlap_results = self._keyword_overlap_recall(query_terms, recall_k)
        vector_results = self._vector_recall(normalized, recall_k)

        # 加权 RRF 融合（向量路可用时纳入，否则退回四路）
        recall_lists = [bm25_results, title_results, section_results, overlap_results]
        weights = [config.RECALL_WEIGHT_BM25, config.RECALL_WEIGHT_TITLE,
                   config.RECALL_WEIGHT_SECTION, config.RECALL_WEIGHT_OVERLAP]
        if vector_results:  # 向量路有结果才纳入
            recall_lists.append(vector_results)
            weights.append(config.RECALL_WEIGHT_VECTOR)

        fused = self._fuse_results(recall_lists, weights, recall_k)

        # ---- v3: 元数据加权（意图分类 + 同类加权 / 异类降权）----
        intent = self.classify_intent(query)
        if intent != "auto":
            weighted = []
            for idx, score in fused:
                chunk_cat = self.chunks[idx].get("category", "")
                if chunk_cat == intent:
                    score *= 1.3   # 同类加权
                elif chunk_cat and chunk_cat != "nav":  # nav 不降权（导航页通用）
                    score *= 0.8   # 异类降权（不丢弃，兜底）
                weighted.append((idx, score))
            weighted.sort(key=lambda x: x[1], reverse=True)
            fused = weighted

        # ---- 第二阶段：Reranker 精排 ----
        # 先做文档级去重，取 top RERANK_CANDIDATE_K 交给 Reranker
        deduped = []
        per_doc = {}
        for idx, score in fused:
            c = self.chunks[idx]
            doc = c["doc"]
            if per_doc.get(doc, 0) >= config.MAX_CHUNKS_PER_DOC:
                continue
            per_doc[doc] = per_doc.get(doc, 0) + 1
            deduped.append(idx)
            if len(deduped) >= config.RERANK_CANDIDATE_K:
                break

        # Reranker 精排：对 (query, chunk_text) pairs 打分
        if self._reranker_svc.available and len(deduped) > top_k:
            docs = [self.chunks[idx]["text"][:config.MAX_CHUNK_TEXT] for idx in deduped]
            rerank_scores = self._reranker_svc.rerank(normalized, docs)
            if rerank_scores is not None:
                # 按 reranker 分数重排
                reranked = sorted(zip(deduped, rerank_scores), key=lambda x: x[1], reverse=True)
                deduped = [idx for idx, _ in reranked[:top_k]]
            else:
                # Reranker 失败，保留 RRF 顺序
                deduped = deduped[:top_k]
        else:
            deduped = deduped[:top_k]

        # ---- 构建最终结果 + 父级上下文 ----
        results = []
        seen_parents = set()
        for idx in deduped:
            c = self.chunks[idx]
            doc = c["doc"]
            section_path = c.get("section_path", c.get("section", ""))
            parent_key = (doc, section_path)
            parent_ctx = ""
            if parent_key not in seen_parents:
                parent_full = self._parent_index.get(parent_key, "")
                hit_text = c["text"]
                pos = parent_full.find(hit_text[:50]) if hit_text else -1
                if pos >= 0:
                    start = max(0, pos - 400)
                    end = min(len(parent_full), pos + len(hit_text) + 400)
                    parent_ctx = parent_full[start:end]
                    if start > 0:
                        parent_ctx = "..." + parent_ctx
                    if end < len(parent_full):
                        parent_ctx = parent_ctx + "..."
                seen_parents.add(parent_key)
            results.append({
                "id": c["id"],
                "doc": doc,
                "section": c["section"],
                "section_path": section_path,
                "score": 1.0,  # Reranker 后绝对分无意义，统一为 1.0
                "text": c["text"][:config.MAX_CHUNK_TEXT],
                "parent_context": parent_ctx,
                "source_url": c.get("source_url", ""),
            })

        # v3: 写入查询缓存（LRU 简易淘汰）
        if len(self._query_cache) >= self._cache_max:
            sorted_keys = sorted(self._query_cache.items(), key=lambda x: x[1][1])
            for k, _ in sorted_keys[:self._cache_max // 5]:
                del self._query_cache[k]
        self._query_cache[cache_key] = (results, now + self._cache_ttl)
        return results

    def is_relevant(self, query: str, results: list) -> bool:
        """FR-RT-04 / FR-QA-03：判定检索结果是否足以回答。
        v3: 多路召回后用 RRF 融合分数，无绝对阈值意义，改为：
        条件 1：多路召回有结果返回（fused 非空）；
        条件 2：查询中的长内容词（≥2 字、非停用词）至少有一个出现在任一召回块中。
        """
        if not results:
            return False
        # 使用规范化后的查询提取内容词
        normalized = _normalize_query(query)
        long_terms = [t for t in content_terms(normalized) if len(t) >= 2]
        if not long_terms:
            # 查询本身没有长内容词（如"1+1等于几"），交给系统提示词兜底，不强行拒答
            return True
        # v3: haystack 也包含 section_path + parent_context，增强层级与上下文匹配
        haystack = "\n".join(
            r["text"] + r.get("section_path", r["section"]) + r["section"] + r["doc"]
            + r.get("parent_context", "")
            for r in results
        )
        return any(t in haystack for t in long_terms)

    @staticmethod
    def chunk_count() -> int:
        return len(Retriever.get().chunks)
