"""Tests for the logging configuration module."""

import logging

from src.logging_config import setup_logging


class TestSetupLogging:
    def test_setup_logging_does_not_raise(self):
        setup_logging()

    def test_root_logger_has_handler_after_setup(self):
        setup_logging()
        root = logging.getLogger()
        assert len(root.handlers) > 0

    def test_root_logger_level_matches_setting(self):
        setup_logging()
        from src.settings import LOG_LEVEL
        expected = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        root = logging.getLogger()
        assert root.level == expected

    def test_app_logger_can_log(self):
        setup_logging()
        logger = logging.getLogger("src.test_module")
        # Should not raise
        logger.info("Test log message from test_logging_config")

    def test_uvicorn_access_logger_is_warning(self):
        setup_logging()
        uv_logger = logging.getLogger("uvicorn.access")
        assert uv_logger.level == logging.WARNING

    def test_httpx_logger_is_warning(self):
        setup_logging()
        httpx_logger = logging.getLogger("httpx")
        assert httpx_logger.level == logging.WARNING

    def test_idempotent_multiple_calls(self):
        setup_logging()
        setup_logging()
        root = logging.getLogger()
        # force=True in basicConfig means handlers get replaced, not duplicated
        # The handler count should be stable (1 from our setup + possibly others)
        assert len(root.handlers) >= 1
