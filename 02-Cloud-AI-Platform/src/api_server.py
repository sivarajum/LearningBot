"""
FastAPI Server for Vertex AI Churn Prediction
"""
import os
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from vertex_ai_training import VertexAITrainingPipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vertex AI Churn Prediction API",
    description="Customer churn prediction using Vertex AI",
    version="1.0.0"
)

# Global variables
pipeline = None
endpoint_name = None


class PredictionRequest(BaseModel):
    """Request model for predictions"""
    instances: List[Dict[str, Any]] = Field(..., description="List of customer feature instances")


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    predictions: List[Dict[str, Any]]


@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup"""
    global pipeline, endpoint_name
    
    project_id = os.getenv("GCP_PROJECT_ID")
    endpoint_name = os.getenv("VERTEX_AI_ENDPOINT_NAME")
    
    if not project_id:
        logger.warning("GCP_PROJECT_ID not set")
        return
    
    try:
        pipeline = VertexAITrainingPipeline(
            project_id=project_id,
            dataset_id="customer_data",
            table_id="customer_features"
        )
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing pipeline: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vertex AI Churn Prediction API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipeline_ready": pipeline is not None,
        "endpoint_configured": endpoint_name is not None
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict churn using Vertex AI endpoint
    
    Args:
        request: Prediction request
        
    Returns:
        Prediction response
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    if endpoint_name is None:
        raise HTTPException(status_code=503, detail="Endpoint not configured")
    
    try:
        predictions = pipeline.predict(
            endpoint_name=endpoint_name,
            instances=request.instances
        )
        
        return PredictionResponse(predictions=predictions)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

