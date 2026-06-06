"""Tests for the RAG pipeline module.

Includes unit tests for individual functions and an end-to-end test
that exercises the full extractive fallback pipeline with a real
VectorStore (mocked SentenceTransformer, real ChromaDB).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from langchain_core.documents import Document

from src.rag_pipeline import (
    RAGResponse,
    _build_prompt,
    _extractive_fallback,
    query,
)


class TestRAGResponse:
    """Tests for the RAGResponse dataclass."""

    def test_default_values(self) -> None:
        resp = RAGResponse(answer="Hello")
        assert resp.answer == "Hello"
        assert resp.sources == []
        assert resp.model_used == "extractive-fallback"

    def test_custom_values(self) -> None:
        resp = RAGResponse(
            answer="Answer text",
            sources=[{"source": "test.md"}],
            model_used="openai/gpt-3.5-turbo",
        )
        assert resp.model_used == "openai/gpt-3.5-turbo"
        assert len(resp.sources) == 1


class TestBuildPrompt:
    """Tests for prompt assembly from context chunks."""

    def test_prompt_contains_question(self) -> None:
        chunks = [
            {
                "content": "Docker runs containers.",
                "metadata": {"source": "docker.md"},
                "score": 0.9,
            }
        ]
        prompt = _build_prompt("What is Docker?", chunks)
        assert "What is Docker?" in prompt

    def test_prompt_contains_context(self) -> None:
        chunks = [
            {
                "content": "Kubernetes is an orchestrator.",
                "metadata": {"source": "k8s.md"},
                "score": 0.8,
            }
        ]
        prompt = _build_prompt("What is K8s?", chunks)
        assert "Kubernetes is an orchestrator." in prompt

    def test_prompt_contains_source_labels(self) -> None:
        chunks = [
            {
                "content": "Content A",
                "metadata": {"source": "fileA.md"},
                "score": 0.9,
            },
            {
                "content": "Content B",
                "metadata": {"source": "fileB.md"},
                "score": 0.8,
            },
        ]
        prompt = _build_prompt("question", chunks)
        assert "Source 1: fileA.md" in prompt
        assert "Source 2: fileB.md" in prompt

    def test_prompt_with_no_chunks(self) -> None:
        prompt = _build_prompt("What?", [])
        assert "What?" in prompt


class TestExtractiveFallback:
    """Tests for the extractive fallback mode (no LLM)."""

    def test_fallback_returns_best_chunk(self) -> None:
        chunks = [
            {
                "content": "Docker is great for containers.",
                "metadata": {"source": "docker.md"},
                "score": 0.95,
            },
        ]
        answer = _extractive_fallback("What is Docker?", chunks)
        assert "Docker is great for containers." in answer
        assert "docker.md" in answer

    def test_fallback_mentions_no_llm(self) -> None:
        chunks = [
            {
                "content": "Some content",
                "metadata": {"source": "test.md"},
                "score": 0.8,
            },
        ]
        answer = _extractive_fallback("question", chunks)
        assert "no LLM configured" in answer.lower() or "Extractive" in answer

    def test_fallback_empty_chunks(self) -> None:
        answer = _extractive_fallback("What?", [])
        assert "No relevant documents" in answer

    def test_fallback_includes_similarity_score(self) -> None:
        chunks = [
            {
                "content": "Content here",
                "metadata": {"source": "file.md"},
                "score": 0.88,
            },
        ]
        answer = _extractive_fallback("question", chunks)
        assert "88%" in answer


class TestQueryPipeline:
    """Tests for the full query pipeline in extractive fallback mode."""

    def test_query_returns_rag_response(
        self, mock_vector_store: MagicMock, unset_api_keys: None
    ) -> None:
        result = query("What is Docker?", mock_vector_store)
        assert isinstance(result, RAGResponse)

    def test_query_uses_extractive_fallback(
        self, mock_vector_store: MagicMock, unset_api_keys: None
    ) -> None:
        result = query("What is Docker?", mock_vector_store)
        assert result.model_used == "extractive-fallback"

    def test_query_includes_sources(
        self, mock_vector_store: MagicMock, unset_api_keys: None
    ) -> None:
        result = query("What is Docker?", mock_vector_store)
        assert len(result.sources) == 2
        assert result.sources[0]["source"] == "docker.md"

    def test_query_answer_not_empty(
        self, mock_vector_store: MagicMock, unset_api_keys: None
    ) -> None:
        result = query("Tell me about containers", mock_vector_store)
        assert len(result.answer) > 0

    def test_query_with_empty_results(self, unset_api_keys: None) -> None:
        empty_store = MagicMock()
        empty_store.similarity_search.return_value = []
        result = query("Unknown topic", empty_store)
        assert "No relevant documents" in result.answer

    def test_query_source_preview_truncated(self, unset_api_keys: None) -> None:
        store = MagicMock()
        long_content = "A" * 500
        store.similarity_search.return_value = [
            {
                "content": long_content,
                "metadata": {"source": "big.md", "chunk_index": 0},
                "score": 0.9,
            },
        ]
        result = query("question", store)
        # Preview should be truncated to 200 chars + "..."
        assert result.sources[0]["preview"].endswith("...")
        assert len(result.sources[0]["preview"]) <= 204

    def test_query_calls_similarity_search(
        self, mock_vector_store: MagicMock, unset_api_keys: None
    ) -> None:
        query("Docker question", mock_vector_store, k=3)
        mock_vector_store.similarity_search.assert_called_once_with("Docker question", k=3)


class TestEndToEndExtractivePipeline:
    """End-to-end test of the extractive fallback pipeline with a real
    VectorStore (real ChromaDB, mocked SentenceTransformer)."""

    @pytest.fixture()
    def real_vector_store_with_docs(self, tmp_path: Path) -> "VectorStore":
        """Build a real VectorStore, ingest documents, and return it."""
        from src.embeddings import VectorStore

        mock_model = MagicMock()

        def fake_encode(texts: list[str], **kwargs) -> np.ndarray:
            # Use hash-based embeddings so different texts get different vectors
            vecs = []
            for text in texts:
                rng = np.random.RandomState(hash(text) % (2**31))
                vecs.append(rng.rand(384).astype("float32"))
            return np.array(vecs)

        mock_model.encode.side_effect = fake_encode

        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            store = VectorStore(persist_dir=str(tmp_path / "e2e_chroma"))

        docs = [
            Document(
                page_content=(
                    "Docker is a platform for building, shipping, and running "
                    "applications in containers."
                ),
                metadata={"source": "docker.md", "chunk_index": 0, "total_chunks": 2},
            ),
            Document(
                page_content=(
                    "Docker images are read-only templates used to create containers."
                ),
                metadata={"source": "docker.md", "chunk_index": 1, "total_chunks": 2},
            ),
            Document(
                page_content=(
                    "Kubernetes is an open-source container orchestration platform "
                    "that automates deployment, scaling, and management."
                ),
                metadata={"source": "kubernetes.md", "chunk_index": 0, "total_chunks": 1},
            ),
        ]
        store.add_documents(docs)
        return store

    def test_e2e_extractive_returns_answer(
        self, real_vector_store_with_docs, unset_api_keys: None
    ) -> None:
        """Full pipeline: real ChromaDB retrieval -> extractive fallback."""
        result = query("What is Docker?", real_vector_store_with_docs, k=2)

        assert isinstance(result, RAGResponse)
        assert result.model_used == "extractive-fallback"
        assert len(result.answer) > 0
        assert len(result.sources) == 2

    def test_e2e_sources_have_scores(
        self, real_vector_store_with_docs, unset_api_keys: None
    ) -> None:
        result = query("container orchestration", real_vector_store_with_docs, k=3)
        for source in result.sources:
            assert "score" in source
            assert 0.0 <= source["score"] <= 1.0
            assert "source" in source
            assert "preview" in source

    def test_e2e_answer_contains_content(
        self, real_vector_store_with_docs, unset_api_keys: None
    ) -> None:
        result = query("Tell me about containers", real_vector_store_with_docs, k=1)
        # The extractive fallback should include text from the best match
        assert "Extractive" in result.answer or "container" in result.answer.lower()
