"""Shared fixtures for Intelligent Churn Prediction tests."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure project root is on sys.path so `src.*` imports work when running pytest
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_generator import generate_customers
from src.feature_engineering import build_features
from src.model import train_model


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def raw_dataframe() -> pd.DataFrame:
    """Generate a small synthetic customer dataset (500 rows) for fast tests."""
    return generate_customers(n=500, seed=99)


@pytest.fixture(scope="session")
def full_dataframe() -> pd.DataFrame:
    """Generate the default-sized dataset (10 000 rows) with default seed."""
    return generate_customers()


@pytest.fixture(scope="session")
def feature_artifacts(raw_dataframe):
    """Build features from the small dataset — returns (X, y, feature_names, artifacts)."""
    X, y, feature_names, artifacts = build_features(raw_dataframe, fit=True)
    return X, y, feature_names, artifacts


@pytest.fixture(scope="session")
def trained_model_results(feature_artifacts):
    """Train a model on the small dataset and return the results dict."""
    X, y, feature_names, _ = feature_artifacts
    results = train_model(X, y, feature_names, test_size=0.2, seed=42)
    return results


@pytest.fixture(scope="session")
def trained_model(trained_model_results):
    """Return just the trained XGBClassifier."""
    return trained_model_results["model"]
