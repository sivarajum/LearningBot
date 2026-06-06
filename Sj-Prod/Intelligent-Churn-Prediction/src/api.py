"""FastAPI service for churn prediction."""

import io
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from src.feature_engineering import build_features
from src.model import MODEL_DIR, load_model, predict_single
from src.settings import CORS_ORIGINS

logger = logging.getLogger(__name__)

# --- Global state loaded at startup ---
MODEL_BUNDLE: dict = {}
TRAINING_METRICS: dict = {}
STARTUP_TIME: str = ""


# --- Allowed values ----------------------------------------------------------
ALLOWED_CONTRACT_TYPES = {"month-to-month", "one_year", "two_year"}
ALLOWED_PAYMENT_METHODS = {"electronic_check", "mailed_check", "bank_transfer", "credit_card"}
ALLOWED_INTERNET_SERVICES = {"DSL", "Fiber", "No"}


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Load model artifacts when the application starts. Auto-train if missing."""
    global MODEL_BUNDLE, TRAINING_METRICS, STARTUP_TIME
    model_path = MODEL_DIR / "model_bundle.joblib"
    if not model_path.exists():
        logger.info("No model bundle found at %s — running training pipeline", model_path)
        from src.pipeline import run_pipeline

        run_pipeline()
    bundle = load_model()
    MODEL_BUNDLE.update(bundle)
    TRAINING_METRICS.update(bundle.get("metrics", {}))
    STARTUP_TIME = datetime.now(timezone.utc).isoformat()
    logger.info("Model loaded successfully. Startup time: %s", STARTUP_TIME)
    yield


app = FastAPI(title="Churn Prediction API", version="1.0.0", lifespan=lifespan)

# --- CORS middleware ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request / response models -----------------------------------------------


class CustomerInput(BaseModel):
    tenure: int = Field(ge=0, le=100, description="Months as customer")
    monthly_charges: float = Field(ge=0, le=500, description="Monthly charge amount in dollars")
    total_charges: Optional[float] = Field(default=None, ge=0, description="Cumulative charges")
    contract_type: str = Field(default="month-to-month", description="Contract type")
    payment_method: str = Field(default="electronic_check", description="Payment method")
    internet_service: str = Field(default="Fiber", description="Internet service type")
    num_support_tickets: int = Field(default=2, ge=0, le=50, description="Number of support tickets")

    @field_validator("contract_type")
    @classmethod
    def validate_contract_type(cls, v: str) -> str:
        if v not in ALLOWED_CONTRACT_TYPES:
            raise ValueError(f"contract_type must be one of {sorted(ALLOWED_CONTRACT_TYPES)}, got '{v}'")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        if v not in ALLOWED_PAYMENT_METHODS:
            raise ValueError(f"payment_method must be one of {sorted(ALLOWED_PAYMENT_METHODS)}, got '{v}'")
        return v

    @field_validator("internet_service")
    @classmethod
    def validate_internet_service(cls, v: str) -> str:
        if v not in ALLOWED_INTERNET_SERVICES:
            raise ValueError(f"internet_service must be one of {sorted(ALLOWED_INTERNET_SERVICES)}, got '{v}'")
        return v


class PredictionResponse(BaseModel):
    churn_probability: float
    prediction: str
    top_contributing_features: List[Tuple[str, float]]


class BatchPredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    total: int


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    status: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    training_date: str
    metrics: Dict[str, Any]
    feature_importance: Dict[str, float]


# --- Helpers ------------------------------------------------------------------


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


# --- Endpoints ----------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", model_loaded="model" in MODEL_BUNDLE)


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        training_date=STARTUP_TIME,
        metrics=TRAINING_METRICS,
        feature_importance=MODEL_BUNDLE.get("feature_importance", {}),
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerInput) -> PredictionResponse:
    try:
        X = _prepare_input(customer)
        result = predict_single(
            MODEL_BUNDLE["model"], X, MODEL_BUNDLE["feature_names"]
        )
        return PredictionResponse(**result)
    except (KeyError, ValueError) as exc:
        logger.error("Prediction failed for input %s: %s", customer.model_dump(), exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(file: UploadFile = File(...)) -> BatchPredictionResponse:
    """Upload a CSV of customers and get batch predictions."""
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        logger.error("Failed to parse uploaded CSV: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    results: List[Dict[str, Any]] = []
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

    logger.info("Batch prediction completed: %d customers processed", len(results))
    return BatchPredictionResponse(predictions=results, total=len(results))
