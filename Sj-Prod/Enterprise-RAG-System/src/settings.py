"""Centralized configuration for the Enterprise RAG System.

All settings are loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
UI_PORT: int = int(os.getenv("UI_PORT", "8501"))
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:8501"
).split(",")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "data/chroma_db")
DOCS_DIR: Path = Path(os.getenv("DOCS_DIR", "sample_docs"))
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K: int = int(os.getenv("TOP_K", "5"))
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")  # "openai", "anthropic", or "" for fallback
