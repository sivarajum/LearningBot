"""Tests for src.api — FastAPI endpoints using TestClient."""

import io
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from src.api import app, MODEL_BUNDLE, TRAINING_METRICS
from src.data_generator import generate_customers
from src.feature_engineering import build_features
from src.model import train_model


@pytest.fixture(scope="module")
def client():
    """
    Create a TestClient with a pre-loaded model bundle.

    Instead of relying on the lifespan event (which needs a persisted model file),
    we populate MODEL_BUNDLE directly with freshly trained artifacts.
    """
    # Generate a small dataset and train
    df = generate_customers(n=500, seed=99)
    X, y, feature_names, artifacts = build_features(df, fit=True)
    results = train_model(X, y, feature_names)

    # Populate the global state that the API endpoints read
    MODEL_BUNDLE.clear()
    MODEL_BUNDLE.update({
        "model": results["model"],
        "scaler": artifacts["scaler"],
        "encoders": artifacts["encoders"],
        "feature_names": artifacts["feature_names"],
        "feature_importance": results["feature_importance"],
        "metrics": {
            "accuracy": results["accuracy"],
            "precision": results["precision"],
            "recall": results["recall"],
            "f1": results["f1"],
        },
    })
    TRAINING_METRICS.clear()
    TRAINING_METRICS.update(MODEL_BUNDLE["metrics"])

    # Use the TestClient without triggering lifespan (which would try to load from disk)
    with TestClient(app, raise_server_exceptions=True) as tc:
        yield tc


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_status_healthy(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert data["status"] == "healthy"

    def test_health_model_loaded(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert data["model_loaded"] is True


class TestModelInfoEndpoint:
    """Tests for GET /model-info."""

    def test_model_info_returns_200(self, client):
        resp = client.get("/model-info")
        assert resp.status_code == 200

    def test_model_info_has_metrics(self, client):
        resp = client.get("/model-info")
        data = resp.json()
        assert "metrics" in data
        assert "accuracy" in data["metrics"]

    def test_model_info_has_feature_importance(self, client):
        resp = client.get("/model-info")
        data = resp.json()
        assert "feature_importance" in data
        assert len(data["feature_importance"]) > 0


class TestPredictEndpoint:
    """Tests for POST /predict."""

    def test_predict_valid_input(self, client):
        payload = {
            "tenure": 12,
            "monthly_charges": 65.0,
            "contract_type": "month-to-month",
            "payment_method": "electronic_check",
            "internet_service": "Fiber",
            "num_support_tickets": 3,
        }
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 200

    def test_predict_response_structure(self, client):
        payload = {
            "tenure": 12,
            "monthly_charges": 65.0,
            "contract_type": "month-to-month",
            "payment_method": "electronic_check",
            "internet_service": "Fiber",
            "num_support_tickets": 3,
        }
        resp = client.post("/predict", json=payload)
        data = resp.json()
        assert "churn_probability" in data
        assert "prediction" in data
        assert "top_contributing_features" in data

    def test_predict_probability_range(self, client):
        payload = {
            "tenure": 12,
            "monthly_charges": 65.0,
            "contract_type": "month-to-month",
            "payment_method": "electronic_check",
            "internet_service": "Fiber",
            "num_support_tickets": 3,
        }
        resp = client.post("/predict", json=payload)
        data = resp.json()
        assert 0.0 <= data["churn_probability"] <= 1.0

    def test_predict_valid_label(self, client):
        payload = {
            "tenure": 12,
            "monthly_charges": 65.0,
            "contract_type": "month-to-month",
            "payment_method": "electronic_check",
            "internet_service": "Fiber",
            "num_support_tickets": 3,
        }
        resp = client.post("/predict", json=payload)
        data = resp.json()
        assert data["prediction"] in {"churn", "no_churn"}

    def test_predict_with_defaults(self, client):
        """Only required fields; optional fields use defaults."""
        payload = {
            "tenure": 24,
            "monthly_charges": 40.0,
        }
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 200

    def test_predict_low_risk_customer(self, client):
        """A long-tenure, low-charge, two-year-contract customer should have low churn."""
        payload = {
            "tenure": 60,
            "monthly_charges": 25.0,
            "contract_type": "two_year",
            "payment_method": "bank_transfer",
            "internet_service": "DSL",
            "num_support_tickets": 0,
        }
        resp = client.post("/predict", json=payload)
        data = resp.json()
        # Should generally have low churn probability
        assert data["churn_probability"] < 0.5

    def test_predict_high_risk_customer(self, client):
        """A short-tenure, high-charge, month-to-month customer should have high churn."""
        payload = {
            "tenure": 2,
            "monthly_charges": 110.0,
            "contract_type": "month-to-month",
            "payment_method": "electronic_check",
            "internet_service": "Fiber",
            "num_support_tickets": 8,
        }
        resp = client.post("/predict", json=payload)
        data = resp.json()
        # Should generally have high churn probability
        assert data["churn_probability"] > 0.5


class TestInputValidation:
    """Tests for input validation on POST /predict."""

    def test_reject_negative_tenure(self, client):
        payload = {"tenure": -1, "monthly_charges": 50.0}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_tenure_over_limit(self, client):
        payload = {"tenure": 101, "monthly_charges": 50.0}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_negative_monthly_charges(self, client):
        payload = {"tenure": 12, "monthly_charges": -10.0}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_monthly_charges_over_limit(self, client):
        payload = {"tenure": 12, "monthly_charges": 501.0}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_negative_support_tickets(self, client):
        payload = {"tenure": 12, "monthly_charges": 50.0, "num_support_tickets": -1}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_support_tickets_over_limit(self, client):
        payload = {"tenure": 12, "monthly_charges": 50.0, "num_support_tickets": 51}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_invalid_contract_type(self, client):
        payload = {"tenure": 12, "monthly_charges": 50.0, "contract_type": "invalid"}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_invalid_payment_method(self, client):
        payload = {"tenure": 12, "monthly_charges": 50.0, "payment_method": "bitcoin"}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_invalid_internet_service(self, client):
        payload = {"tenure": 12, "monthly_charges": 50.0, "internet_service": "5G"}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422

    def test_reject_negative_total_charges(self, client):
        payload = {"tenure": 12, "monthly_charges": 50.0, "total_charges": -100.0}
        resp = client.post("/predict", json=payload)
        assert resp.status_code == 422


class TestBatchPredictEndpoint:
    """Tests for POST /batch-predict."""

    def test_batch_predict_csv(self, client):
        """Upload a CSV with multiple rows and get batch predictions."""
        df = pd.DataFrame([
            {
                "customer_id": "TEST-001",
                "tenure": 12,
                "monthly_charges": 65.0,
                "total_charges": 780.0,
                "contract_type": "month-to-month",
                "payment_method": "electronic_check",
                "internet_service": "Fiber",
                "num_support_tickets": 3,
            },
            {
                "customer_id": "TEST-002",
                "tenure": 48,
                "monthly_charges": 30.0,
                "total_charges": 1440.0,
                "contract_type": "two_year",
                "payment_method": "bank_transfer",
                "internet_service": "DSL",
                "num_support_tickets": 1,
            },
        ])
        csv_bytes = df.to_csv(index=False).encode()
        resp = client.post(
            "/batch-predict",
            files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "predictions" in data
        assert "total" in data
        assert data["total"] == 2
        for pred in data["predictions"]:
            assert "churn_probability" in pred
            assert "prediction" in pred
            assert "customer_id" in pred
