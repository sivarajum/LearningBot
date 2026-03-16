"""FastAPI service for churn prediction."""

import io
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.model import load_model, predict_single
from src.feature_engineering import build_features

# --- Global state loaded at startup ---
# Single-process; would use dependency injection in production
MODEL_BUNDLE: dict = {}
TRAINING_METRICS: dict = {}
STARTUP_TIME: str = ""


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Load model artifacts when the application starts."""
    global MODEL_BUNDLE, TRAINING_METRICS, STARTUP_TIME
    bundle = load_model()
    MODEL_BUNDLE.update(bundle)
    TRAINING_METRICS.update(bundle.get("metrics", {}))
    STARTUP_TIME = datetime.now(timezone.utc).isoformat()
    yield


app = FastAPI(title="Churn Prediction API", version="1.0.0", lifespan=lifespan)


class CustomerInput(BaseModel):
    tenure: int
    monthly_charges: float
    total_charges: Optional[float] = None
    contract_type: str = "month-to-month"
    payment_method: str = "electronic_check"
    internet_service: str = "Fiber"
    num_support_tickets: int = 2


class PredictionResponse(BaseModel):
    churn_probability: float
    prediction: str
    top_contributing_features: list


def _prepare_input(customer: CustomerInput) -> np.ndarray:
    """Convert a single customer input to a scaled feature vector."""
    if customer.total_charges is None:
        customer.total_charges = round(customer.tenure * customer.monthly_charges, 2)

    row = pd.DataFrame([customer.model_dump()])
    X, _, _, _ = build_features(
        row,
        scaler=MODEL_BUNDLE["scaler"],
        encoders=MODEL_BUNDLE["encoders"],
        fit=False,
    )
    return X


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy", "model_loaded": "model" in MODEL_BUNDLE}


@app.get("/model-info")
def model_info() -> dict:
    return {
        "training_date": STARTUP_TIME,
        "metrics": TRAINING_METRICS,
        "feature_importance": MODEL_BUNDLE.get("feature_importance", {}),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerInput) -> dict:
    try:
        X = _prepare_input(customer)
        result = predict_single(
            MODEL_BUNDLE["model"], X, MODEL_BUNDLE["feature_names"]
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/batch-predict")
async def batch_predict(file: UploadFile = File(...)) -> dict:
    """Upload a CSV of customers and get batch predictions."""
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    results = []
    for _, row in df.iterrows():
        customer = CustomerInput(**{
            k: row[k] for k in CustomerInput.model_fields if k in row.index
        })
        X = _prepare_input(customer)
        pred = predict_single(
            MODEL_BUNDLE["model"], X, MODEL_BUNDLE["feature_names"]
        )
        pred["customer_id"] = row.get("customer_id", "unknown")
        results.append(pred)

    return {"predictions": results, "total": len(results)}
