"""Centralized configuration for the Multi-Cloud Data Lake system."""

import os
from pathlib import Path

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
UI_PORT: int = int(os.getenv("UI_PORT", "8501"))
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
LAKE_DIR: Path = Path(os.getenv("LAKE_DIR", "data/lake"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
CUSTOMERS_PER_CLOUD: int = int(os.getenv("CUSTOMERS_PER_CLOUD", "1000"))
TRANSACTIONS_PER_CLOUD: int = int(os.getenv("TRANSACTIONS_PER_CLOUD", "5000"))

ALLOWED_CLOUDS: set[str] = {"aws", "azure", "gcp"}
ALLOWED_LAKE_TABLES: set[str] = {"customers", "transactions", "customer_metrics"}
