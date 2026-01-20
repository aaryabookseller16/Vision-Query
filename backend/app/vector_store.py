"""
vector_store.py

Simple in-memory vector store.

Stores (path -> embedding) and supports cosine similarity search.
Cosine sim becomes dot product after L2 normalization.
"""

from dataclasses import dataclass
from threading import Lock
from typing import List

import numpy as np


@dataclass(frozen=True)
class SearchResult:
    path: str
    score: float


class VectorStore:
    def __init__(self) -> None:
        self._paths: List[str] = []
        self._embs: np.ndarray | None = None
        self._lock = Lock()

    def __len__(self) -> int:
        return len(self._paths)

    @staticmethod
    def _l2_normalize(v: np.ndarray) -> np.ndarray:
        v = v.astype(np.float32, copy=False)
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm

    def add(self, path: str, embedding: np.ndarray) -> None:
        emb = self._l2_normalize(np.asarray(embedding))

        with self._lock:
            self._paths.append(path)
            if self._embs is None:
                self._embs = emb.reshape(1, -1)
            else:
                self._embs = np.vstack([self._embs, emb.reshape(1, -1)])

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        q = self._l2_normalize(np.asarray(query_embedding))

        with self._lock:
            if self._embs is None or len(self._paths) == 0:
                return []

            scores = self._embs @ q
            k = max(1, min(int(top_k), scores.shape[0]))

            idx = np.argpartition(-scores, kth=k - 1)[:k]
            idx = idx[np.argsort(-scores[idx])]

            return [SearchResult(path=self._paths[i], score=float(scores[i])) for i in idx]