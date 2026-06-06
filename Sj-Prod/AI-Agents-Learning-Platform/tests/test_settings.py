"""Tests for the centralized settings module."""

import os

from src.settings import API_HOST, API_PORT, UI_PORT, CORS_ORIGINS, LOG_LEVEL


class TestDefaultSettings:
    """Verify default values when no env vars are set."""

    def test_api_host_default(self):
        assert API_HOST == os.getenv("API_HOST", "0.0.0.0")

    def test_api_port_is_int(self):
        assert isinstance(API_PORT, int)

    def test_api_port_default(self):
        if "API_PORT" not in os.environ:
            assert API_PORT == 8000

    def test_ui_port_is_int(self):
        assert isinstance(UI_PORT, int)

    def test_ui_port_default(self):
        if "UI_PORT" not in os.environ:
            assert UI_PORT == 8501

    def test_cors_origins_is_list(self):
        assert isinstance(CORS_ORIGINS, list)

    def test_cors_origins_has_entries(self):
        assert len(CORS_ORIGINS) > 0

    def test_log_level_is_string(self):
        assert isinstance(LOG_LEVEL, str)

    def test_log_level_default(self):
        if "LOG_LEVEL" not in os.environ:
            assert LOG_LEVEL == "INFO"
