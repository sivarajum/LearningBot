"""
settings.py -- Centralized configuration for the Medallion Architecture system.

All settings are read from environment variables with sensible defaults.
Import this module instead of scattering os.getenv() calls across files.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(Path(__file__).parent.parent)))

RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", str(PROJECT_ROOT / "data" / "raw"))
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(PROJECT_ROOT / "data" / "warehouse.duckdb"))

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
UI_PORT = int(os.getenv("UI_PORT", "8501"))

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:8501"
).split(",")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
