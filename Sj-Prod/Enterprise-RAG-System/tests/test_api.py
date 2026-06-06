"""Tests for the FastAPI application.

Uses a real temporary ChromaDB for the vector store (with mocked
SentenceTransformer to avoid downloading the 80MB model in CI).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from src.api import app
from src.embeddings import VectorStore


def _make_mock_model() -> MagicMock:
    """Create a mock SentenceTransformer with deterministic embeddings."""
    mock_model = MagicMock()

    def fake_encode(texts: list[str], **kwargs) -> np.ndarray:
        rng = np.random.RandomState(42)
        return rng.rand(len(texts), 384).astype("float32")

    mock_model.encode.side_effect = fake_encode
    return mock_model


@pytest.fixture()
def real_vector_store(tmp_path: Path) -> VectorStore:
    """Create a real VectorStore with mocked embeddings and temp ChromaDB."""
    mock_model = _make_mock_model()
    with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
        store = VectorStore(persist_dir=str(tmp_path / "chroma_api_test"))
    return store


@pytest.fixture()
def populated_vector_store(real_vector_store: VectorStore) -> VectorStore:
    """A real VectorStore pre-loaded with sample documents."""
    docs = [
        Document(
            page_content="Docker is a platform for containers.",
            metadata={"source": "docker.md", "chunk_index": 0, "total_chunks": 1},
        ),
        Document(
            page_content="Kubernetes orchestrates containers.",
            metadata={"source": "kubernetes.md", "chunk_index": 0, "total_chunks": 1},
        ),
    ]
    real_vector_store.add_documents(docs)
    return real_vector_store


@pytest.fixture()
def client(populated_vector_store: VectorStore) -> TestClient:
    """Create a TestClient backed by a real pre-populated vector store."""
    app.state.vector_store = populated_vector_store
    return TestClient(app)


@pytest.fixture()
def client_empty_store(real_vector_store: VectorStore) -> TestClient:
    """Create a TestClient with a real but empty vector store."""
    app.state.vector_store = real_vector_store
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["service"] == "rag-api"


class TestStatsEndpoint:
    """Tests for GET /stats."""

    def test_stats_returns_200(self, client: TestClient) -> None:
        response = client.get("/stats")
        assert response.status_code == 200

    def test_stats_includes_expected_fields(self, client: TestClient) -> None:
        data = client.get("/stats").json()
        assert "collection" in data
        assert "total_chunks" in data
        assert "embedding_model" in data

    def test_stats_shows_correct_count(self, client: TestClient) -> None:
        data = client.get("/stats").json()
        assert data["total_chunks"] == 2  # populated with 2 docs

    def test_stats_empty_store(self, client_empty_store: TestClient) -> None:
        data = client_empty_store.get("/stats").json()
        assert data["total_chunks"] == 0


class TestQueryEndpoint:
    """Tests for POST /query."""

    def test_query_returns_200(self, client: TestClient, unset_api_keys: None) -> None:
        response = client.post("/query", json={"question": "What is Docker?"})
        assert response.status_code == 200

    def test_query_response_structure(self, client: TestClient, unset_api_keys: None) -> None:
        data = client.post("/query", json={"question": "What is Docker?"}).json()
        assert "answer" in data
        assert "model_used" in data
        assert "sources" in data
        assert "elapsed_seconds" in data

    def test_query_uses_extractive_fallback(self, client: TestClient, unset_api_keys: None) -> None:
        data = client.post("/query", json={"question": "What is Docker?"}).json()
        assert data["model_used"] == "extractive-fallback"

    def test_query_returns_sources(self, client: TestClient, unset_api_keys: None) -> None:
        data = client.post("/query", json={"question": "What is Docker?"}).json()
        assert len(data["sources"]) >= 1

    def test_query_empty_store_returns_400(self, client_empty_store: TestClient) -> None:
        response = client_empty_store.post(
            "/query", json={"question": "What is Docker?"}
        )
        assert response.status_code == 400
        assert "No documents indexed" in response.json()["detail"]

    def test_query_with_custom_k(self, client: TestClient, unset_api_keys: None) -> None:
        response = client.post("/query", json={"question": "Docker", "k": 1})
        assert response.status_code == 200

    def test_query_missing_question_returns_422(self, client: TestClient) -> None:
        response = client.post("/query", json={})
        assert response.status_code == 422


class TestQueryInputValidation:
    """Tests for QueryRequest field validation."""

    def test_query_empty_question_returns_422(self, client: TestClient) -> None:
        response = client.post("/query", json={"question": ""})
        assert response.status_code == 422

    def test_query_question_too_long_returns_422(self, client: TestClient) -> None:
        response = client.post("/query", json={"question": "x" * 2001})
        assert response.status_code == 422

    def test_query_k_zero_returns_422(self, client: TestClient) -> None:
        response = client.post("/query", json={"question": "test", "k": 0})
        assert response.status_code == 422

    def test_query_k_too_large_returns_422(self, client: TestClient) -> None:
        response = client.post("/query", json={"question": "test", "k": 51})
        assert response.status_code == 422

    def test_query_k_negative_returns_422(self, client: TestClient) -> None:
        response = client.post("/query", json={"question": "test", "k": -1})
        assert response.status_code == 422


class TestIngestEndpoint:
    """Tests for POST /ingest."""

    def test_ingest_nonexistent_dir_returns_400(self, client: TestClient) -> None:
        response = client.post("/ingest", json={"directory": "/nonexistent/path"})
        assert response.status_code == 400


class TestIngestInputValidation:
    """Tests for IngestRequest field validation."""

    def test_ingest_chunk_size_too_small_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/ingest", json={"directory": "./sample_docs", "chunk_size": 50}
        )
        assert response.status_code == 422

    def test_ingest_chunk_size_too_large_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/ingest", json={"directory": "./sample_docs", "chunk_size": 6000}
        )
        assert response.status_code == 422

    def test_ingest_chunk_overlap_negative_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/ingest",
            json={"directory": "./sample_docs", "chunk_overlap": -1},
        )
        assert response.status_code == 422

    def test_ingest_chunk_overlap_too_large_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/ingest",
            json={"directory": "./sample_docs", "chunk_overlap": 501},
        )
        assert response.status_code == 422

    def test_ingest_overlap_gte_size_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/ingest",
            json={"directory": "./sample_docs", "chunk_size": 200, "chunk_overlap": 200},
        )
        assert response.status_code == 422

    def test_ingest_overlap_exceeds_size_returns_422(self, client: TestClient) -> None:
        response = client.post(
            "/ingest",
            json={"directory": "./sample_docs", "chunk_size": 200, "chunk_overlap": 300},
        )
        assert response.status_code == 422
