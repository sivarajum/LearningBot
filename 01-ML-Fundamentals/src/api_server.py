"""
FastAPI Server for ML Fundamentals Projects
Serves all three ML models via REST API
"""
import os
import logging
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# Import models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from iris_classification.iris_classifier import IrisClassificationPipeline
from movie_recommendation.recommendation_system import RecommendationSystem
from sentiment_analysis.sentiment_analysis import SentimentAnalysisPipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ML Fundamentals API",
    description="API for Iris Classification, Movie Recommendation, and Sentiment Analysis",
    version="1.0.0"
)

# Global models
iris_model = None
recommendation_model = None
sentiment_model = None


# Request/Response Models
class IrisPredictionRequest(BaseModel):
    """Request for Iris classification"""
    sepal_length: float = Field(..., ge=0, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, description="Sepal width in cm")
    petal_length: float = Field(..., ge=0, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, description="Petal width in cm")


class IrisPredictionResponse(BaseModel):
    """Response for Iris classification"""
    species: str
    probabilities: Dict[str, float]
    confidence: float


class MovieRecommendationRequest(BaseModel):
    """Request for movie recommendations"""
    user_id: int = Field(..., ge=0, description="User ID")
    num_recommendations: int = Field(default=5, ge=1, le=20, description="Number of recommendations")


class MovieRecommendationResponse(BaseModel):
    """Response for movie recommendations"""
    recommendations: List[Dict[str, Any]]


class SentimentRequest(BaseModel):
    """Request for sentiment analysis"""
    text: str = Field(..., min_length=1, description="Text to analyze")


class SentimentResponse(BaseModel):
    """Response for sentiment analysis"""
    sentiment: str
    probability: float
    confidence: float


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    global iris_model, recommendation_model, sentiment_model
    
    try:
        # Initialize Iris classifier
        iris_model = IrisClassificationPipeline()
        iris_model.load_data()
        iris_model.preprocess_data()
        iris_model.train_all_models()
        logger.info("Iris classifier loaded")
        
        # Initialize Recommendation system
        recommendation_model = RecommendationSystem()
        recommendation_model.load_data()
        recommendation_model.build_similarity_matrices()
        logger.info("Recommendation system loaded")
        
        # Initialize Sentiment analyzer
        sentiment_model = SentimentAnalysisPipeline()
        sentiment_model.load_data()
        sentiment_model.preprocess_data()
        sentiment_model.train_all_models()
        logger.info("Sentiment analyzer loaded")
    except Exception as e:
        logger.error(f"Error loading models: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ML Fundamentals API",
        "version": "1.0.0",
        "endpoints": {
            "iris": "/predict/iris",
            "movies": "/recommend/movies",
            "sentiment": "/analyze/sentiment"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": {
            "iris": iris_model is not None,
            "recommendation": recommendation_model is not None,
            "sentiment": sentiment_model is not None
        }
    }


@app.post("/predict/iris", response_model=IrisPredictionResponse)
async def predict_iris(request: IrisPredictionRequest):
    """Predict Iris species"""
    if iris_model is None:
        raise HTTPException(status_code=503, detail="Iris model not loaded")
    
    try:
        # Prepare input
        features = np.array([[
            request.sepal_length,
            request.sepal_width,
            request.petal_length,
            request.petal_width
        ]])
        
        # Get best model (Random Forest)
        best_model = iris_model.models.get("Random Forest")
        if best_model is None:
            raise HTTPException(status_code=500, detail="Best model not available")
        
        # Predict
        prediction = best_model.predict(features)[0]
        probabilities = best_model.predict_proba(features)[0]
        
        species_names = ["setosa", "versicolor", "virginica"]
        species = species_names[prediction]
        
        prob_dict = {species_names[i]: float(prob) for i, prob in enumerate(probabilities)}
        confidence = float(max(probabilities))
        
        return IrisPredictionResponse(
            species=species,
            probabilities=prob_dict,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/movies", response_model=MovieRecommendationResponse)
async def recommend_movies(request: MovieRecommendationRequest):
    """Get movie recommendations"""
    if recommendation_model is None:
        raise HTTPException(status_code=503, detail="Recommendation model not loaded")
    
    try:
        recommendations = recommendation_model.get_recommendations(
            user_id=request.user_id,
            num_recommendations=request.num_recommendations
        )
        
        return MovieRecommendationResponse(recommendations=recommendations)
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """Analyze text sentiment"""
    if sentiment_model is None:
        raise HTTPException(status_code=503, detail="Sentiment model not loaded")
    
    try:
        # Get best model (Logistic Regression)
        best_model = sentiment_model.models.get("Logistic Regression")
        if best_model is None:
            raise HTTPException(status_code=500, detail="Best model not available")
        
        # Preprocess and predict
        processed_text = sentiment_model.preprocess_text(request.text)
        features = sentiment_model.vectorizer.transform([processed_text])
        
        prediction = best_model.predict(features)[0]
        probability = best_model.predict_proba(features)[0][prediction]
        
        sentiment = "positive" if prediction == 1 else "negative"
        confidence = float(probability)
        
        return SentimentResponse(
            sentiment=sentiment,
            probability=confidence,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

