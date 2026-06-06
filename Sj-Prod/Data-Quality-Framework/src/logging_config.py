"""
logging_config.py -- Centralized logging setup for the Enterprise Data Quality Framework.

Call setup_logging() once at application startup (in main.py) to configure
the root logger with a consistent format and level across all modules.
"""

import logging

from .settings import LOG_LEVEL


def setup_logging() -> None:
    """Configure the root logger with a standard format and level from settings."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
