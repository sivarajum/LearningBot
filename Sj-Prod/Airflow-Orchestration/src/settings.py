"""
Centralized configuration for the Airflow Orchestration system.

All settings are read from environment variables with sensible defaults.
Override any setting by exporting the corresponding env var before running.
"""

import os

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
UI_PORT: int = int(os.getenv("UI_PORT", "8501"))
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:8501"
).split(",")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
DAGS_DIR: str = os.getenv("DAGS_DIR", "dags")
CONFIG_DIR: str = os.getenv("CONFIG_DIR", "config")
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))
