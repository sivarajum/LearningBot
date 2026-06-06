"""Shared fixtures for AI Agents Learning Platform tests."""

import pytest
from fastapi.testclient import TestClient

from src.api import app


@pytest.fixture()
def client():
    """FastAPI test client."""
    return TestClient(app)
