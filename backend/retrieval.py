# -*- coding: utf-8 -*-
"""BM25 检索服务（FR-RT-01~05），v2：结构化分词 + section_path 索引 + 查询扩展 + 同义词增强。"""
import json
import re
import threading

import jieba
from rank_bm25 import BM25Okapi

import config


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
        corpus = [
            _content_tokenize(
                c["text"]
                + " " + c.get("section_path", c.get("section", ""))
                + " " + c.get("section", "")
                + " " + c.get("doc", "")
            )
            for c in self.chunks
        ]
        self.bm25 = BM25Okapi(corpus, k1=1.2, b=0.5)  # 中文短文本优化：降低 b 减少长度归一化影响

    @classmethod
    def get(cls) -> "Retriever":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def search(self, query: str, top_k: int = None) -> list:
        top_k = top_k or config.RETRIEVE_TOP_K
        # 查询扩展：加入同义词提高召回
        expanded_query = _expand_query(query)
        # 先取更多候选（top 64），再做文档级去重，避免单个"话痨"文档霸占全部位置
        candidate_k = max(top_k * 4, 32)
        scores = self.bm25.get_scores(_content_tokenize(expanded_query))
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
                "section_path": c.get("section_path", c.get("section", "")),
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
        # 使用规范化后的查询提取内容词
        normalized = _normalize_query(query)
        long_terms = [t for t in content_terms(normalized) if len(t) >= 2]
        if not long_terms:
            # 查询本身没有长内容词（如"1+1等于几"），交给系统提示词兜底，不强行拒答
            return True
        # v2: haystack 也包含 section_path，增强层级路径匹配
        haystack = "\n".join(
            r["text"] + r.get("section_path", r["section"]) + r["section"] + r["doc"]
            for r in results
        )
        return any(t in haystack for t in long_terms)

    @staticmethod
    def chunk_count() -> int:
        return len(Retriever.get().chunks)
