#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BM25 检索 CLI（XKZ-Agent）—— M1 检索验证
用法:
  python scripts/retrieve.py "挂科了怎么办"
  python scripts/retrieve.py --eval        # 内置 30 题评测，输出 Top-5 命中率

实现需求: FR-RT-01 ~ FR-RT-05
- BM25 (rank-bm25)，不依赖向量库
- jieba 中文分词
- top-8 召回，单块截断 800 字
- 得分阈值（默认 0.5，可用 --threshold 调整）
"""
import argparse
import json
import sys
from pathlib import Path

import jieba
from rank_bm25 import BM25Okapi

BASE = Path(__file__).resolve().parent.parent
CHUNKS_FILE = BASE / "data" / "chunks.jsonl"

DEFAULT_TOP_K = 8
DEFAULT_THRESHOLD = 0.5
MAX_CHUNK_TEXT = 800
MAX_CHUNKS_PER_DOC = 2   # 召回时单文档块数上限（多样性，FR-RT-06）

# M1 评测集：30 个测试问题 + 期望命中的文档（任一命中即算中）
EVAL_SET = [
    ("挂科了会怎样？能重修吗？", ["大学政策简解"]),
    ("奖学金怎么申请？", ["大学政策简解"]),
    ("毕业审核有什么要求？", ["大学政策简解"]),
    ("处分会有什么后果？", ["大学政策简解"]),
    ("保研需要什么条件？", ["学术发展规划", "大学政策简解"]),
    ("考研怎么准备？", ["学术发展规划"]),
    ("双学位怎么申请？", ["学术发展规划", "大学政策简解"]),
    ("怎么进组做科研？", ["学术发展规划"]),
    ("港澳台学生怎么保研？", ["学术发展规划", "大学政策简解", "新生指南补缺"]),
    ("简历怎么写才不被刷？", ["就业发展规划"]),
    ("实习怎么找？", ["就业发展规划"]),
    ("考公和选调有什么区别？", ["就业发展规划", "大学政策简解"]),
    ("互联网大厂求职怎么准备？", ["就业发展规划"]),
    ("有哪些值得参加的竞赛？", ["竞赛指导"]),
    ("A类竞赛有哪些？", ["竞赛指导"]),
    ("学生会有哪些部门？", ["学生组织介绍"]),
    ("团委和学生会有什么区别？", ["学生组织介绍"]),
    ("勤工助学怎么申请？", ["学生组织介绍", "大学政策简解"]),
    ("新生入学要准备什么？", ["新生指南补缺"]),
    ("宿舍条件怎么样？", ["新生指南补缺", "情感与生活指南"]),
    ("校园网怎么办理？", ["常用链接", "新生指南补缺"]),
    ("教务系统网址是什么？", ["常用链接"]),
    ("学校附近有什么好吃的？", ["美食娱乐排行"]),
    ("有什么好吃的推荐？", ["美食娱乐排行"]),
    ("大学生必备哪些效率工具？", ["效率工具推荐"]),
    ("Git 怎么入门？", ["Git使用指南"]),
    ("怎么谈恋爱？", ["情感与生活指南", "林家络的恋爱教学笔记"]),
    ("健身怎么开始？", ["健身指北"]),
    ("大学四年怎么规划？", ["学术发展规划", "新生指南补缺"]),
    ("转专业难吗？", ["大学政策简解", "新生指南补缺"]),
]


def load_chunks(path: Path = CHUNKS_FILE) -> list:
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def tokenize(text: str) -> list:
    return [t for t in jieba.lcut(text) if t.strip() and any(ch.isalnum() for ch in t)]


# 常见疑问词/语气词不参与相关性判定与打分
_STOPWORDS = {
    "什么", "怎么", "怎么样", "怎样", "如何", "为什么", "为啥", "咋", "哪些", "哪个",
    "哪儿", "哪里", "多少", "吗", "嘛", "呢", "啊", "吧", "哦", "呀", "的", "了", "是",
    "有", "能", "会", "可以", "请问", "一下", "办", "没", "不", "要", "该", "这", "那",
    "啥", "弄", "搞", "咋办", "咋样",
}


def content_terms(query: str) -> list:
    return [t for t in tokenize(query) if t not in _STOPWORDS]


def content_tokenize(text: str) -> list:
    """打分用分词：过滤停用词，避免"话痨"文档靠高频虚词拿到高分。"""
    return [t for t in tokenize(text) if t not in _STOPWORDS]


def is_relevant(query: str, results: list, threshold: float = DEFAULT_THRESHOLD) -> bool:
    """top1 得分 ≥ 阈值，且长内容词（≥2 字非停用词）至少命中 1 个。"""
    if not results or results[0]["score"] < threshold:
        return False
    long_terms = [t for t in content_terms(query) if len(t) >= 2]
    if not long_terms:
        return True
    haystack = "\n".join(r["text"] + r["section"] + r["doc"] for r in results)
    return any(t in haystack for t in long_terms)


class Retriever:
    def __init__(self, chunks: list):
        self.chunks = chunks
        self.corpus = [content_tokenize(c["text"] + " " + c.get("section", "") + " " + c.get("doc", "")) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query: str, top_k: int = DEFAULT_TOP_K) -> list:
        # 先取更多候选再做文档级去重，避免单个"话痨"文档霸占全部位置
        candidate_k = max(top_k * 4, 32)
        scores = self.bm25.get_scores(content_tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:candidate_k]
        results = []
        per_doc = {}
        for idx, score in ranked:
            if score <= 0:   # 无查询词匹配的块直接丢弃，不充数
                continue
            c = self.chunks[idx]
            doc = c["doc"]
            if per_doc.get(doc, 0) >= MAX_CHUNKS_PER_DOC:
                continue
            per_doc[doc] = per_doc.get(doc, 0) + 1
            results.append({
                "id": c["id"],
                "doc": doc,
                "section": c["section"],
                "score": round(float(score), 4),
                "text": c["text"][:MAX_CHUNK_TEXT],
                "source_url": c.get("source_url", ""),
            })
            if len(results) >= top_k:
                break
        return results


def evaluate(retriever: Retriever, top_n: int = 5):
    hits = 0
    details = []
    for q, expected_docs in EVAL_SET:
        results = retriever.search(q, top_k=top_n)
        hit_docs = {r["doc"] for r in results}
        ok = bool(hit_docs & set(expected_docs))
        hits += ok
        details.append((q, ok, sorted(hit_docs)))
    rate = hits / len(EVAL_SET) * 100
    print(f"\n=== M1 评测: Top-{top_n} 命中率 {hits}/{len(EVAL_SET)} = {rate:.1f}% (目标 ≥80%) ===")
    for q, ok, docs in details:
        mark = "OK " if ok else "MISS"
        print(f"[{mark}] {q}  -> {', '.join(docs[:3])}")
    return rate


def main():
    ap = argparse.ArgumentParser(description="XKZ-Agent BM25 检索 CLI")
    ap.add_argument("query", nargs="?", help="查询问题")
    ap.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--eval", action="store_true", help="运行内置评测集")
    args = ap.parse_args()

    chunks = load_chunks()
    retriever = Retriever(chunks)
    print(f"加载 {len(chunks)} 个文档块", file=sys.stderr)

    if args.eval:
        rate = evaluate(retriever)
        sys.exit(0 if rate >= 80 else 1)

    if not args.query:
        ap.print_help()
        sys.exit(2)

    results = retriever.search(args.query, top_k=args.top_k)
    if not is_relevant(args.query, results, args.threshold):
        print("资料库未覆盖该问题，建议咨询学长学姐或学校官方渠道")
        sys.exit(1)
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['doc']} - {r['section']} (score={r['score']})")
        print(f"    {r['text'][:120]}...")
        print(f"    {r['source_url']}")


if __name__ == "__main__":
    main()
