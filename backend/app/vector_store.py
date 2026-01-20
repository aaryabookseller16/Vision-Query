import numpy as np
from typing import List, Dict

class VectorStore:
    def __init__(self):
        self.vectors: List[np.ndarray] = []
        self.metadata: List[Dict] = []

    def add(self, vector: List[float], meta: Dict):
        self.vectors.append(np.array(vector))
        self.metadata.append(meta)

    def search(self, query_vector: List[float], top_k: int = 5):
        if not self.vectors:
            return []

        q = np.array(query_vector)
        scores = []

        for i, v in enumerate(self.vectors):
            score = np.dot(q, v) / (np.linalg.norm(q) * np.linalg.norm(v))
            scores.append((score, self.metadata[i]))

        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]