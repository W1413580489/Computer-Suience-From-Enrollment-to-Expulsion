# -*- coding: utf-8 -*-
"""BGE Embedding + Reranker 服务（v3）。

- EmbeddingService: 加载 BAAI/bge-small-zh-v1.5，编码文本为 512 维向量，用于向量召回
- RerankerService:  加载 BAAI/bge-reranker-base，对 (query, doc) pairs 精排打分

两者均为单例 + 线程安全懒加载，模型加载失败时优雅降级（返回 None），
调用方检查返回值决定是否走该路召回/精排。

国内服务器通过环境变量 XKZ_HF_ENDPOINT=https://hf-mirror.com 加速模型下载。
"""
import os
import threading

import numpy as np

import config

# 设置 HuggingFace 镜像（必须在 import transformers 之前）
_hf_endpoint = os.getenv("XKZ_HF_ENDPOINT", "")
if _hf_endpoint:
    os.environ["HF_ENDPOINT"] = _hf_endpoint


# ---------- Embedding 服务 ----------
class EmbeddingService:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.dimension = 0
        self._available = False
        try:
            import torch
            # v3: CPU 优化 —— 限制线程数，降低内存峰值
            torch.set_num_threads(2)
            from transformers import AutoModel, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(config.EMBEDDING_MODEL)
            # v3: FP16 加载，模型内存 130MB → 65MB，低配服务器省内存，效果无损
            self.model = AutoModel.from_pretrained(config.EMBEDDING_MODEL, torch_dtype=torch.float16)
            self.model.eval()
            # 获取维度（取配置或实际推理）
            self.dimension = self.model.config.hidden_size
            self._available = True
            print(f"[Embedding] 已加载 {config.EMBEDDING_MODEL} (dim={self.dimension})")
        except Exception as e:
            print(f"[Embedding] 模型加载失败，向量召回将禁用: {type(e).__name__}: {e}")
            self._available = False

    @classmethod
    def get(cls) -> "EmbeddingService":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    @property
    def available(self) -> bool:
        return self._available

    def _mean_pool(self, token_embeddings, attention_mask):
        """BGE 使用 mean pooling + attention_mask。"""
        import torch
        mask = attention_mask.unsqueeze(-1).float()
        summed = torch.sum(token_embeddings * mask, dim=1)
        counts = torch.clamp(mask.sum(dim=1), min=1e-9)
        return summed / counts

    def encode(self, texts: list[str], batch_size: int = 32, is_query: bool = False) -> np.ndarray | None:
        """编码文本列表，返回 L2 归一化后的向量矩阵 [N, dim]。
        BGE 查询需加前缀 "为这个句子生成表示以用于检索相关文章："。
        """
        if not self._available:
            return None
        import torch

        if is_query:
            texts = [f"为这个句子生成表示以用于检索相关文章：{t}" for t in texts]

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            encoded = self.tokenizer(batch, padding=True, truncation=True,
                                     max_length=512, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**encoded)
                embeddings = self._mean_pool(outputs.last_hidden_state, encoded["attention_mask"])
            all_embeddings.append(embeddings.numpy())

        result = np.vstack(all_embeddings)
        # L2 归一化，后续点积即为余弦相似度
        norms = np.linalg.norm(result, axis=1, keepdims=True)
        norms = np.where(norms < 1e-9, 1e-9, norms)
        return result / norms

    def encode_one(self, text: str, is_query: bool = False) -> np.ndarray | None:
        """编码单条文本，返回归一化向量 [dim]。"""
        mat = self.encode([text], is_query=is_query)
        if mat is None:
            return None
        return mat[0]


# ---------- Reranker 服务 ----------
class RerankerService:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._available = False
        # v3: 低配服务器可设 XKZ_RERANK_ENABLED=0 跳过模型加载，省 ~600MB 内存
        if not config.RERANK_ENABLED:
            print("[Reranker] 已通过 XKZ_RERANK_ENABLED=0 关闭，跳过模型加载（省约600MB内存）")
            return
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(config.RERANKER_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(config.RERANKER_MODEL)
            self.model.eval()
            self._available = True
            print(f"[Reranker] 已加载 {config.RERANKER_MODEL}")
        except Exception as e:
            print(f"[Reranker] 模型加载失败，精排将禁用: {type(e).__name__}: {e}")
            self._available = False

    @classmethod
    def get(cls) -> "RerankerService":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    @property
    def available(self) -> bool:
        return self._available and config.RERANK_ENABLED

    def rerank(self, query: str, documents: list[str], batch_size: int = 16) -> list[float] | None:
        """对 (query, doc) pairs 打分，返回与 documents 等长的分数列表。
        分数越高表示越相关。失败时返回 None（调用方保留原始排序）。
        """
        if not self._available or not documents:
            return None
        import torch

        all_scores = []
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            pairs = [[query, doc] for doc in batch_docs]
            with torch.no_grad():
                inputs = self.tokenizer(pairs, padding=True, truncation=True,
                                        max_length=512, return_tensors="pt")
                logits = self.model(**inputs).logits.squeeze(-1)
                all_scores.extend(logits.numpy().tolist())

        return all_scores
