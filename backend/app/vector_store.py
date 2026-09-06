"""Thread-safe, in-memory cosine-similarity index."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

import numpy as np


@dataclass(frozen=True)
class SearchResult:
    path: str
    score: float


class VectorStore:
    """Stores one normalized embedding per image path."""

    def __init__(self) -> None:
        self._paths: list[str] = []
        self._embeddings: np.ndarray | None = None
        self._lock = RLock()

    def __len__(self) -> int:
        with self._lock:
            return len(self._paths)

    @staticmethod
    def _normalize(vector: np.ndarray | list[float]) -> np.ndarray:
        value = np.asarray(vector, dtype=np.float32).reshape(-1)
        if value.size == 0 or not np.isfinite(value).all():
            raise ValueError("embedding must contain finite values")
        norm = float(np.linalg.norm(value))
        if norm == 0:
            raise ValueError("embedding cannot be the zero vector")
        return value / norm

    def add(self, path: str, embedding: np.ndarray | list[float]) -> None:
        """Insert an image or replace its existing vector idempotently."""
        if not path.strip():
            raise ValueError("path is required")
        normalized = self._normalize(embedding)

        with self._lock:
            if self._embeddings is not None and normalized.size != self._embeddings.shape[1]:
                raise ValueError("embedding dimension does not match the index")
            if path in self._paths:
                index = self._paths.index(path)
                self._embeddings[index] = normalized
                return
            self._paths.append(path)
            self._embeddings = normalized.reshape(1, -1) if self._embeddings is None else np.vstack([self._embeddings, normalized])

    def search(self, query_embedding: np.ndarray | list[float], top_k: int = 5) -> list[SearchResult]:
        query = self._normalize(query_embedding)
        with self._lock:
            if self._embeddings is None:
                return []
            if query.size != self._embeddings.shape[1]:
                raise ValueError("query dimension does not match the index")
            scores = self._embeddings @ query
            count = min(max(int(top_k), 1), len(self._paths))
            indices = np.argsort(-scores, kind="stable")[:count]
            return [SearchResult(path=self._paths[index], score=float(scores[index])) for index in indices]
