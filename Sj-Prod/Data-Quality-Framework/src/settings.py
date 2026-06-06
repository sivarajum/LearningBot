"""
settings.py -- Centralized configuration for the Enterprise Data Quality Framework.

All settings are read from environment variables with sensible defaults.
Import from here instead of reading os.environ directly in application code.
"""

import os

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
UI_PORT = int(os.getenv("UI_PORT", "8501"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
DATA_DIR = os.getenv("DATA_DIR", "data")
CONFIG_DIR = os.getenv("CONFIG_DIR", "config")
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
