"""Tests for src.model — training, evaluation, persistence, and inference."""

import numpy as np
import pytest
from xgboost import XGBClassifier

from src.model import train_model, save_model, load_model, predict_single

METRIC_KEYS = ["accuracy", "precision", "recall", "f1"]


class TestTrainModel:
    """Tests for train_model()."""

    def test_trains_successfully(self, trained_model_results):
        """train_model should return a dict containing a model."""
        assert "model" in trained_model_results
        assert isinstance(trained_model_results["model"], XGBClassifier)

    def test_metrics_keys_present(self, trained_model_results):
        """Result dict should contain accuracy, precision, recall, f1."""
        for key in METRIC_KEYS:
            assert key in trained_model_results, f"Missing metric: {key}"

    def test_metrics_between_0_and_1(self, trained_model_results):
        """All metric values should be in [0, 1]."""
        for key in METRIC_KEYS:
            val = trained_model_results[key]
            assert 0.0 <= val <= 1.0, f"{key} = {val} out of range"

    def test_has_feature_importance(self, trained_model_results):
        """Result should contain feature_importance dict."""
        assert "feature_importance" in trained_model_results
        assert isinstance(trained_model_results["feature_importance"], dict)
        assert len(trained_model_results["feature_importance"]) > 0

    def test_has_confusion_matrix(self, trained_model_results):
        """Result should contain a 2x2 confusion matrix."""
        cm = trained_model_results["confusion_matrix"]
        assert isinstance(cm, list)
        assert len(cm) == 2
        assert len(cm[0]) == 2

    def test_has_cv_scores(self, trained_model_results):
        """Result should contain cross-validation scores."""
        assert "cv_scores" in trained_model_results
        assert len(trained_model_results["cv_scores"]) == 5  # 5-fold CV
        assert "cv_mean" in trained_model_results
        assert 0.0 <= trained_model_results["cv_mean"] <= 1.0

    def test_reasonable_accuracy(self, trained_model_results):
        """Model accuracy should be at least 70% on synthetic data."""
        assert trained_model_results["accuracy"] >= 0.70


class TestSaveLoadModel:
    """Tests for save_model() and load_model()."""

    def test_save_creates_file(self, tmp_path, trained_model_results, feature_artifacts):
        """save_model should create a model_bundle.joblib file."""
        _, _, _, artifacts = feature_artifacts
        model = trained_model_results["model"]
        out = save_model(model, artifacts, path=tmp_path)
        assert out.exists()
        assert out.name == "model_bundle.joblib"

    def test_load_roundtrip(self, tmp_path, trained_model_results, feature_artifacts):
        """Loading a saved model should return the same artifacts."""
        _, _, _, artifacts = feature_artifacts
        model = trained_model_results["model"]
        out = save_model(model, artifacts, path=tmp_path)
        loaded = load_model(out)

        assert "model" in loaded
        assert isinstance(loaded["model"], XGBClassifier)
        assert "scaler" in loaded
        assert "encoders" in loaded
        assert "feature_names" in loaded

    def test_loaded_model_predicts(self, tmp_path, trained_model_results, feature_artifacts):
        """A loaded model should produce predictions identical to the original."""
        X, _, _, artifacts = feature_artifacts
        model = trained_model_results["model"]
        out = save_model(model, artifacts, path=tmp_path)
        loaded = load_model(out)

        orig_pred = model.predict(X[:5])
        loaded_pred = loaded["model"].predict(X[:5])
        np.testing.assert_array_equal(orig_pred, loaded_pred)


class TestPredictSingle:
    """Tests for predict_single()."""

    def test_returns_probability_and_prediction(self, trained_model, feature_artifacts):
        """predict_single should return churn_probability and prediction."""
        X, _, feature_names, _ = feature_artifacts
        result = predict_single(trained_model, X[:1], feature_names)
        assert "churn_probability" in result
        assert "prediction" in result
        assert "top_contributing_features" in result

    def test_probability_in_range(self, trained_model, feature_artifacts):
        """Churn probability should be between 0 and 1."""
        X, _, feature_names, _ = feature_artifacts
        result = predict_single(trained_model, X[:1], feature_names)
        assert 0.0 <= result["churn_probability"] <= 1.0

    def test_prediction_label(self, trained_model, feature_artifacts):
        """Prediction should be either 'churn' or 'no_churn'."""
        X, _, feature_names, _ = feature_artifacts
        result = predict_single(trained_model, X[:1], feature_names)
        assert result["prediction"] in {"churn", "no_churn"}

    def test_prediction_matches_probability(self, trained_model, feature_artifacts):
        """Prediction label should match the 0.5 threshold on probability."""
        X, _, feature_names, _ = feature_artifacts
        result = predict_single(trained_model, X[:1], feature_names)
        if result["churn_probability"] >= 0.5:
            assert result["prediction"] == "churn"
        else:
            assert result["prediction"] == "no_churn"

    def test_top_features_structure(self, trained_model, feature_artifacts):
        """Top contributing features should be a list of (name, importance) tuples."""
        X, _, feature_names, _ = feature_artifacts
        result = predict_single(trained_model, X[:1], feature_names)
        top = result["top_contributing_features"]
        assert isinstance(top, list)
        assert len(top) == 3  # top 3 features
        for name, imp in top:
            assert isinstance(name, str)
            assert isinstance(imp, float)
            assert name in feature_names
