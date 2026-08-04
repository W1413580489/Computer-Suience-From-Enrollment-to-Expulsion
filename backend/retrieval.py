# -*- coding: utf-8 -*-
"""BM25 检索服务（FR-RT-01~05），与 scripts/retrieve.py 同一套逻辑，供 API 常驻使用。"""
import json
import threading

import jieba
from rank_bm25 import BM25Okapi

import config


def _tokenize(text: str) -> list:
    # 过滤纯标点/空白 token，保留含字母数字的词
    return [t for t in jieba.lcut(text) if t.strip() and any(ch.isalnum() for ch in t)]

# 常见疑问词/语气词不参与相关性判定与打分
_STOPWORDS = {
    "什么", "怎么", "怎么样", "怎样", "如何", "为什么", "为啥", "咋", "哪些", "哪个",
    "哪儿", "哪里", "多少", "吗", "嘛", "呢", "啊", "吧", "哦", "呀", "的", "了", "是",
    "有", "能", "会", "可以", "请问", "一下", "办", "没", "不", "要", "该", "这", "那",
    "啥", "弄", "搞", "咋办", "咋样",
}


def content_terms(query: str) -> list:
    """提取查询中的内容词：非停用词。长词（≥2 字）单独返回用于命中判定。"""
    terms = [t for t in _tokenize(query) if t not in _STOPWORDS]
    return terms


def _content_tokenize(text: str) -> list:
    """打分用分词：过滤停用词，避免"话痨"文档靠高频虚词拿到高分。"""
    return [t for t in _tokenize(text) if t not in _STOPWORDS]


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
        corpus = [_content_tokenize(c["text"] + " " + c.get("section", "") + " " + c.get("doc", ""))
                  for c in self.chunks]
        self.bm25 = BM25Okapi(corpus)

    @classmethod
    def get(cls) -> "Retriever":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def search(self, query: str, top_k: int = None) -> list:
        top_k = top_k or config.RETRIEVE_TOP_K
        # 先取更多候选（top 64），再做文档级去重，避免单个"话痨"文档霸占全部位置
        candidate_k = max(top_k * 4, 32)
        scores = self.bm25.get_scores(_content_tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:candidate_k]
        results = []
        per_doc = {}
        for idx, score in ranked:
            if score <= 0:   # 无查询词匹配的块直接丢弃，不充数
                continue
            c = self.chunks[idx]
            doc = c["doc"]
            if per_doc.get(doc, 0) >= config.MAX_CHUNKS_PER_DOC:
                continue
            per_doc[doc] = per_doc.get(doc, 0) + 1
            results.append({
                "id": c["id"],
                "doc": doc,
                "section": c["section"],
                "score": float(score),
                "text": c["text"][:config.MAX_CHUNK_TEXT],
                "source_url": c.get("source_url", ""),
            })
            if len(results) >= top_k:
                break
        return results

    def is_relevant(self, query: str, results: list) -> bool:
        """FR-RT-04 / FR-QA-03：判定检索结果是否足以回答。
        条件 1：top1 得分 ≥ 阈值；
        条件 2：查询中的长内容词（≥2 字、非停用词）至少有一个出现在任一召回块中。
        """
        if not results or results[0]["score"] < config.RETRIEVE_THRESHOLD:
            return False
        long_terms = [t for t in content_terms(query) if len(t) >= 2]
        if not long_terms:
            # 查询本身没有长内容词（如"1+1等于几"），交给系统提示词兜底，不强行拒答
            return True
        haystack = "\n".join(r["text"] + r["section"] + r["doc"] for r in results)
        return any(t in haystack for t in long_terms)

    @staticmethod
    def chunk_count() -> int:
        return len(Retriever.get().chunks)
