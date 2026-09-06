import numpy as np
import pytest

from app.vector_store import VectorStore


def test_search_ranks_by_cosine_similarity():
    store = VectorStore()
    store.add("red.jpg", [1.0, 0.0])
    store.add("blue.jpg", [0.0, 1.0])
    results = store.search([0.9, 0.1], top_k=2)
    assert [result.path for result in results] == ["red.jpg", "blue.jpg"]
    assert results[0].score > results[1].score


def test_reingest_replaces_instead_of_duplicating():
    store = VectorStore()
    store.add("one.jpg", [1.0, 0.0])
    store.add("one.jpg", [0.0, 1.0])
    assert len(store) == 1
    assert store.search([0.0, 1.0])[0].score == pytest.approx(1.0)


@pytest.mark.parametrize("vector", [[], [0.0, 0.0], [np.nan, 1.0]])
def test_rejects_invalid_vectors(vector):
    with pytest.raises(ValueError):
        VectorStore().add("bad.jpg", vector)


def test_rejects_dimension_mismatch():
    store = VectorStore()
    store.add("one.jpg", [1.0, 0.0])
    with pytest.raises(ValueError, match="dimension"):
        store.search([1.0, 0.0, 0.0])
