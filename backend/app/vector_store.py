"""
vector_store.py

This file implements a simple in-memory vector store.

Goal:
- Store embeddings (vectors) for images
- Search for the most similar vectors given a query vector

Why keep it simple:
- For an MVP, an in-memory store is the fastest way to get end-to-end search working.
- It's easy to understand and debug.
- Later, this module can be swapped out for FAISS / pgvector / Pinecone / etc
  without changing the API layer (main.py) much.

Key idea:
- We use cosine similarity to rank results.
- Metadata is stored alongside each vector (e.g., image path).
"""

from typing import Dict, List, Tuple
import numpy as np


class VectorStore:
    """
    In-memory store for vectors + metadata.

    Stored state:
    - self.vectors: list of numpy arrays (each is a vector embedding)
    - self.metadata: list of dicts, one per vector (same index as vectors)
    """

    def __init__(self):
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict] = []

    def add(self, vector: List[float], meta: Dict) -> None:
        """
        Add a new vector + metadata into the store.

        Args:
            vector: embedding as a Python list (float values)
            meta:   arbitrary metadata (ex: {"path": "...", "id": 123})

        Notes:
            We store vectors as numpy arrays because it's convenient for math ops.
        """
        self.vectors.append(np.array(vector, dtype=np.float32))
        self.metadata.append(meta)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[float, Dict]]:
        """
        Search for the most similar vectors.

        Args:
            query_vector: embedding of the user query
            top_k: number of results to return

        Returns:
            List of (score, metadata) tuples sorted by highest similarity.

        Similarity metric:
            cosine_similarity(a, b) = dot(a,b) / (||a|| * ||b||)

        We use cosine similarity because CLIP embeddings are typically compared this way.
        """
        if not self.vectors:
            return []

        q = np.array(query_vector, dtype=np.float32)

        # Precompute query norm once for efficiency
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []

        results: List[Tuple[float, Dict]] = []

        for vec, meta in zip(self.vectors, self.metadata):
            v_norm = np.linalg.norm(vec)
            if v_norm == 0:
                continue

            score = float(np.dot(q, vec) / (q_norm * v_norm))
            results.append((score, meta))

        # Sort by similarity score descending (best match first)
        results.sort(key=lambda x: x[0], reverse=True)

        return results[:top_k]