"""Tests for the embeddings / vector store module.

The SentenceTransformer is mocked to avoid downloading the 80MB model in CI,
but all ChromaDB operations use a real temporary ChromaDB instance.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from langchain_core.documents import Document

from src.embeddings import COLLECTION_NAME, VectorStore


@pytest.fixture()
def vector_store(tmp_path: Path) -> VectorStore:
    """Create a VectorStore backed by a temporary directory, with a mocked
    SentenceTransformer so no model download is required.
    ChromaDB operations are real."""
    mock_model = MagicMock()

    # Return deterministic embeddings: 384-dim vectors (matching all-MiniLM-L6-v2)
    def fake_encode(texts: list[str], **kwargs) -> np.ndarray:
        rng = np.random.RandomState(42)
        return rng.rand(len(texts), 384).astype("float32")

    mock_model.encode.side_effect = fake_encode

    with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
        store = VectorStore(persist_dir=str(tmp_path / "chroma_test"))
    return store


@pytest.fixture()
def sample_documents() -> list[Document]:
    """A small set of LangChain Document objects for testing."""
    return [
        Document(
            page_content="Docker is a platform for building containers.",
            metadata={"source": "docker.md", "chunk_index": 0, "total_chunks": 2},
        ),
        Document(
            page_content="Kubernetes orchestrates containerized applications.",
            metadata={"source": "kubernetes.md", "chunk_index": 0, "total_chunks": 1},
        ),
        Document(
            page_content="Docker images are built from Dockerfiles.",
            metadata={"source": "docker.md", "chunk_index": 1, "total_chunks": 2},
        ),
    ]


class TestVectorStoreInitialization:
    """Tests for VectorStore creation and configuration."""

    def test_store_initializes(self, vector_store: VectorStore) -> None:
        assert vector_store is not None
        assert vector_store.collection is not None

    def test_store_uses_correct_collection_name(self, vector_store: VectorStore) -> None:
        assert vector_store.collection.name == COLLECTION_NAME

    def test_empty_store_has_zero_count(self, vector_store: VectorStore) -> None:
        assert vector_store.collection.count() == 0

    def test_get_stats_empty(self, vector_store: VectorStore) -> None:
        stats = vector_store.get_stats()
        assert stats["total_chunks"] == 0
        assert stats["collection"] == COLLECTION_NAME


class TestDocumentAddition:
    """Tests for adding documents to the vector store."""

    def test_add_documents_returns_count(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        count = vector_store.add_documents(sample_documents)
        assert count == 3

    def test_add_documents_updates_collection_count(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        vector_store.add_documents(sample_documents)
        assert vector_store.collection.count() == 3

    def test_add_empty_list_returns_zero(self, vector_store: VectorStore) -> None:
        count = vector_store.add_documents([])
        assert count == 0

    def test_add_documents_idempotent(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        """Adding the same documents twice should not duplicate them
        because we use content-based hashing."""
        vector_store.add_documents(sample_documents)
        vector_store.add_documents(sample_documents)
        assert vector_store.collection.count() == 3

    def test_get_stats_after_add(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        vector_store.add_documents(sample_documents)
        stats = vector_store.get_stats()
        assert stats["total_chunks"] == 3


class TestSimilaritySearch:
    """Tests for similarity search."""

    def test_search_returns_results(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        vector_store.add_documents(sample_documents)
        results = vector_store.similarity_search("What is Docker?", k=2)
        assert len(results) == 2

    def test_search_result_structure(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        vector_store.add_documents(sample_documents)
        results = vector_store.similarity_search("containers", k=1)
        assert len(results) >= 1
        result = results[0]
        assert "content" in result
        assert "metadata" in result
        assert "score" in result
        assert isinstance(result["score"], float)

    def test_search_empty_store_returns_empty(self, vector_store: VectorStore) -> None:
        results = vector_store.similarity_search("anything", k=5)
        assert results == []

    def test_search_k_exceeds_collection(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        vector_store.add_documents(sample_documents)
        results = vector_store.similarity_search("Docker", k=100)
        assert len(results) == 3  # only 3 documents exist

    def test_search_scores_are_between_0_and_1(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        vector_store.add_documents(sample_documents)
        results = vector_store.similarity_search("Docker", k=3)
        for r in results:
            assert 0.0 <= r["score"] <= 1.0

    def test_search_metadata_preserved(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        """Ensure metadata survives the round-trip through ChromaDB."""
        vector_store.add_documents(sample_documents)
        results = vector_store.similarity_search("Docker", k=3)
        sources = {r["metadata"]["source"] for r in results}
        assert "docker.md" in sources


class TestVectorStoreReset:
    """Tests for resetting the vector store."""

    def test_reset_clears_documents(
        self, vector_store: VectorStore, sample_documents: list[Document]
    ) -> None:
        vector_store.add_documents(sample_documents)
        assert vector_store.collection.count() == 3
        vector_store.reset()
        assert vector_store.collection.count() == 0
