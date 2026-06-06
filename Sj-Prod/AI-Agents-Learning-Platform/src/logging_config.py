"""Logging configuration for the AI Agents Learning Platform."""

import logging
import sys

from src.settings import LOG_LEVEL


def setup_logging() -> None:
    """Configure structured logging for the application.

    Sets up a consistent format across all modules with the level
    controlled by the LOG_LEVEL setting (default: INFO).
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
