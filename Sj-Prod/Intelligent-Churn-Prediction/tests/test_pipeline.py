"""Tests for src.pipeline — end-to-end training pipeline."""

from pathlib import Path

import pytest

from src.pipeline import run_pipeline
from src.data_generator import OUTPUT_PATH
from src.model import MODEL_DIR


class TestRunPipeline:
    """Tests for run_pipeline()."""

    def test_pipeline_runs_end_to_end(self):
        """Full pipeline should run without errors and return metrics."""
        metrics = run_pipeline()
        assert isinstance(metrics, dict)

    def test_pipeline_returns_expected_metrics(self):
        """Pipeline metrics dict should contain expected keys."""
        metrics = run_pipeline()
        expected_keys = ["accuracy", "precision", "recall", "f1", "cv_mean",
                         "confusion_matrix", "training_date"]
        for key in expected_keys:
            assert key in metrics, f"Missing metric key: {key}"

    def test_pipeline_creates_output_files(self):
        """Pipeline should create both the CSV data file and model bundle."""
        run_pipeline()
        assert OUTPUT_PATH.exists(), f"customers.csv not created at {OUTPUT_PATH}"
        model_path = MODEL_DIR / "model_bundle.joblib"
        assert model_path.exists(), f"model_bundle.joblib not created at {model_path}"

    def test_pipeline_metrics_in_range(self):
        """All numeric metrics from pipeline should be between 0 and 1."""
        metrics = run_pipeline()
        for key in ["accuracy", "precision", "recall", "f1", "cv_mean"]:
            assert 0.0 <= metrics[key] <= 1.0, f"{key} = {metrics[key]} out of range"
