"""
logging_config.py -- Centralized logging setup for the Medallion Architecture system.

Call setup_logging() once at process startup (in main.py) to configure the
root logger. All modules then use ``logging.getLogger(__name__)`` and
inherit this configuration automatically.
"""

from __future__ import annotations

import logging
import sys

from .settings import LOG_LEVEL


def setup_logging() -> None:
    """Configure the root logger with a consistent format and level."""
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    # Avoid duplicate handlers if called more than once
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(level)
