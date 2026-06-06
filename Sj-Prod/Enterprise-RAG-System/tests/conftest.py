"""Shared fixtures for Enterprise RAG System tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Ensure the project root is on sys.path so `src` imports work
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture()
def sample_docs_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample markdown files."""
    doc1 = tmp_path / "docker.md"
    doc1.write_text(
        "# Docker\n\n"
        "Docker is a platform for building, shipping, and running "
        "applications in containers. Containers package an application "
        "with all its dependencies into a standardized unit.\n\n"
        "## Key Concepts\n\n"
        "### Images\n"
        "A Docker image is a read-only template containing the "
        "application code, runtime, libraries, and system tools.\n\n"
        "### Containers\n"
        "A container is a running instance of an image."
    )

    doc2 = tmp_path / "kubernetes.md"
    doc2.write_text(
        "# Kubernetes\n\n"
        "Kubernetes is an open-source container orchestration platform. "
        "It automates deployment, scaling, and management of "
        "containerized applications.\n\n"
        "## Components\n\n"
        "### Pods\n"
        "A pod is the smallest deployable unit in Kubernetes."
    )

    return tmp_path


@pytest.fixture()
def empty_docs_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with an empty markdown file."""
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("")
    return tmp_path


@pytest.fixture()
def mixed_docs_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with mixed file types."""
    (tmp_path / "readme.md").write_text("# Readme\n\nSome content here.")
    (tmp_path / "notes.txt").write_text("Plain text notes about testing.")
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n")
    (tmp_path / "script.py").write_text("print('hello')")
    return tmp_path


@pytest.fixture()
def mock_sentence_transformer() -> MagicMock:
    """Mock SentenceTransformer to avoid downloading models in tests."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.rand(1, 384).astype("float32")

    with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
        yield mock_model


@pytest.fixture()
def mock_vector_store() -> MagicMock:
    """Create a mock VectorStore for tests that don't need real embeddings."""
    store = MagicMock()
    store.similarity_search.return_value = [
        {
            "content": "Docker is a platform for containers.",
            "metadata": {"source": "docker.md", "chunk_index": 0},
            "score": 0.92,
        },
        {
            "content": "Kubernetes orchestrates containers.",
            "metadata": {"source": "kubernetes.md", "chunk_index": 0},
            "score": 0.85,
        },
    ]
    store.get_stats.return_value = {
        "collection": "rag_documents",
        "total_chunks": 10,
        "embedding_model": "all-MiniLM-L6-v2",
        "persist_dir": "./data/chroma_db",
    }
    store.collection.count.return_value = 10
    return store


@pytest.fixture()
def unset_api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure no LLM API keys are set so tests use extractive fallback."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
