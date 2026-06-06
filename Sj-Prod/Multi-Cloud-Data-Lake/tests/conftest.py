"""Shared fixtures for Multi-Cloud Data Lake tests."""

import shutil
from pathlib import Path

import pandas as pd
import pytest

from src.cloud_simulator import (
    _generate_customers,
    _generate_transactions,
    generate_cloud_data,
    save_cloud_data,
)


@pytest.fixture()
def tmp_data_dir(tmp_path, monkeypatch):
    """Redirect DATA_DIR and LAKE_DIR to a temp directory so tests never touch real data."""
    import src.settings as settings
    import src.cloud_simulator as cs
    import src.lake_builder as lb

    fake_data = tmp_path / "data"
    fake_data.mkdir()
    fake_lake = fake_data / "lake"
    fake_lake.mkdir()

    # Patch the canonical settings module
    monkeypatch.setattr(settings, "DATA_DIR", fake_data)
    monkeypatch.setattr(settings, "LAKE_DIR", fake_lake)

    # Patch the copies already imported into cloud_simulator, lake_builder, and api
    monkeypatch.setattr(cs, "DATA_DIR", fake_data)
    monkeypatch.setattr(lb, "DATA_DIR", fake_data)
    monkeypatch.setattr(lb, "LAKE_DIR", fake_lake)

    # Also patch the references imported into api.py so the lifespan and
    # endpoint handlers use the temp directories.
    import src.api as api_mod
    monkeypatch.setattr(api_mod, "DATA_DIR", fake_data)
    monkeypatch.setattr(api_mod, "LAKE_DIR", fake_lake)

    return fake_data


@pytest.fixture()
def small_cloud_data():
    """Generate a small dataset (10 customers, 50 transactions per cloud) for fast tests."""
    return generate_cloud_data(customers_per_cloud=10, transactions_per_cloud=50)


@pytest.fixture()
def aws_customers():
    """Generate a small AWS customer DataFrame."""
    return _generate_customers("aws", n=20, seed=42)


@pytest.fixture()
def aws_transactions(aws_customers):
    """Generate a small AWS transactions DataFrame."""
    return _generate_transactions("aws", aws_customers, n=100, seed=43)


@pytest.fixture()
def saved_cloud_data(tmp_data_dir, small_cloud_data):
    """Generate and save small cloud data to the temp data directory."""
    from src.cloud_simulator import save_cloud_data as _save

    _save(small_cloud_data)
    return tmp_data_dir


@pytest.fixture()
def built_lake(saved_cloud_data):
    """Generate cloud data, build the lake, and return the temp data directory."""
    from src.lake_builder import build_lake

    build_lake()
    return saved_cloud_data
