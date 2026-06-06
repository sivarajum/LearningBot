"""
FastAPI Server for ML Pipeline
Serves churn prediction model via REST API
"""
import os
import logging
import joblib
import pandas as pd
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from model_training import ModelTrainingPipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Churn Prediction API",
    description="Real-time customer churn prediction API",
    version="1.0.0"
)

# Global model variable
model = None
feature_columns = None


class PredictionRequest(BaseModel):
    """Request model for predictions"""
    customer_id: str = Field(..., description="Customer ID")
    hour_of_day: int = Field(..., ge=0, le=23, description="Hour of day")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week")
    is_weekend: int = Field(..., ge=0, le=1, description="Is weekend")
    total_spent_sum: float = Field(..., description="Total spent sum")
    total_spent_mean: float = Field(..., description="Total spent mean")
    total_spent_std: float = Field(..., description="Total spent std")
    num_orders_sum: int = Field(..., description="Number of orders sum")
    num_orders_mean: float = Field(..., description="Number of orders mean")
    days_since_last_order_min: int = Field(..., description="Days since last order min")
    days_since_last_order_mean: float = Field(..., description="Days since last order mean")
    avg_order_value_mean: float = Field(..., description="Average order value mean")
    avg_order_value_std: float = Field(..., description="Average order value std")
    event_count: int = Field(..., description="Event count")
    spending_per_order: float = Field(..., description="Spending per order")
    order_frequency: float = Field(..., description="Order frequency")
    spending_consistency: float = Field(..., description="Spending consistency")


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    customer_id: str
    churn_probability: float = Field(..., ge=0, le=1)
    churn_prediction: bool
    confidence: float = Field(..., ge=0, le=1)


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""
    customers: List[PredictionRequest]


def load_model(model_path: str = "models/churn_model.pkl"):
    """
    Load trained model
    
    Args:
        model_path: Path to model file
    """
    global model, feature_columns
    
    if not os.path.exists(model_path):
        logger.warning(f"Model not found at {model_path}, training new model...")
        # Train a new model if not found
        project_id = os.getenv("GCP_PROJECT_ID", "your-project-id")
        training = ModelTrainingPipeline(
            project_id=project_id,
            dataset_id="customer_data"
        )
        model, _ = training.train_and_evaluate()
        training.save_model(model, model_path)
    else:
        model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
    
    # Get feature columns from model
    if hasattr(model, "feature_names_in_"):
        feature_columns = list(model.feature_names_in_)
    else:
        # Default feature columns
        feature_columns = [
            "hour_of_day", "day_of_week", "is_weekend",
            "total_spent_sum", "total_spent_mean", "total_spent_std",
            "num_orders_sum", "num_orders_mean",
            "days_since_last_order_min", "days_since_last_order_mean",
            "avg_order_value_mean", "avg_order_value_std",
            "event_count", "spending_per_order",
            "order_frequency", "spending_consistency"
        ]


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    model_path = os.getenv("MODEL_PATH", "models/churn_model.pkl")
    load_model(model_path)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Churn Prediction API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict churn for a single customer
    
    Args:
        request: Prediction request
        
    Returns:
        Prediction response
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare features
        features = pd.DataFrame([request.dict()])
        features = features[feature_columns]
        
        # Make prediction
        churn_probability = float(model.predict_proba(features)[0, 1])
        churn_prediction = bool(model.predict(features)[0])
        
        # Calculate confidence
        confidence = abs(churn_probability - 0.5) * 2
        
        return PredictionResponse(
            customer_id=request.customer_id,
            churn_probability=churn_probability,
            churn_prediction=churn_prediction,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict churn for multiple customers
    
    Args:
        request: Batch prediction request
        
    Returns:
        List of prediction responses
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare features
        features_list = [customer.dict() for customer in request.customers]
        features_df = pd.DataFrame(features_list)
        features_df = features_df[feature_columns]
        
        # Make predictions
        churn_probabilities = model.predict_proba(features_df)[:, 1]
        churn_predictions = model.predict(features_df)
        
        # Build responses
        responses = []
        for i, customer in enumerate(request.customers):
            confidence = abs(churn_probabilities[i] - 0.5) * 2
            responses.append(PredictionResponse(
                customer_id=customer.customer_id,
                churn_probability=float(churn_probabilities[i]),
                churn_prediction=bool(churn_predictions[i]),
                confidence=float(confidence)
            ))
        
        return responses
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

