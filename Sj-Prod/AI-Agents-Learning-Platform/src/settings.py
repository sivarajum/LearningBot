"""Centralized configuration loaded from environment variables."""

import os

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
UI_PORT = int(os.getenv("UI_PORT", "8501"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
