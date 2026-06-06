"""Centralized configuration — all tunables read from environment variables."""

import os
from pathlib import Path

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
UI_PORT = int(os.getenv("UI_PORT", "8501"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", "data/model_bundle.joblib"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
N_CUSTOMERS = int(os.getenv("N_CUSTOMERS", "10000"))
