"""
Centralized logging configuration for the Airflow Orchestration system.

Call setup_logging() once at application startup (in main.py) to configure
the root logger with a consistent format across all modules.
"""

import logging
import sys

from src.settings import LOG_LEVEL


def setup_logging() -> None:
    """Configure the root logger with a structured format and the configured log level."""
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Avoid adding duplicate handlers on repeated calls
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(level)
