"""Shared fixtures for Medallion Architecture dbt tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the project root is on sys.path so that `src` is importable.
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture()
def project_root() -> Path:
    """Return the resolved project root directory."""
    return PROJECT_ROOT


@pytest.fixture()
def tmp_output_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test output files."""
    output = tmp_path / "raw"
    output.mkdir(parents=True, exist_ok=True)
    return output
