# Module 04: End-to-End ML Pipeline

## Overview
Complete machine learning pipeline for customer churn prediction, from real-time data ingestion through model deployment, demonstrating production-ready MLOps practices.

## Architecture
- **Data Ingestion**: Pub/Sub → BigQuery
- **Feature Engineering**: Automated feature creation
- **Model Training**: Vertex AI with MLflow tracking
- **Model Serving**: FastAPI REST API
- **Deployment**: Docker + Cloud Run

## Features
- ✅ Real-time data ingestion
- ✅ Automated feature engineering
- ✅ Model training with MLflow
- ✅ REST API for predictions
- ✅ Docker containerization
- ✅ Production-ready code

## Quick Start

### Prerequisites
- GCP project with Vertex AI enabled
- BigQuery dataset created
- Python 3.9+

### Installation
```bash
pip install -r requirements.txt
```

### Setup
1. Set environment variables:
```bash
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

2. Run data ingestion:
```bash
python src/data_ingestion.py
```

3. Run feature engineering:
```bash
python src/feature_engineering.py
```

4. Train model:
```bash
python src/model_training.py
```

5. Start API server:
```bash
python src/api_server.py
```

### Docker Deployment
```bash
docker build -t ml-pipeline .
docker run -p 8000:8000 ml-pipeline
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Single Prediction
```bash
POST /predict
Content-Type: application/json

{
  "customer_id": "CUST_001",
  "hour_of_day": 14,
  "day_of_week": 3,
  ...
}
```

### Batch Prediction
```bash
POST /predict/batch
Content-Type: application/json

{
  "customers": [...]
}
```

## Project Structure
```
04-End-to-End-ML-Pipeline/
├── src/
│   ├── data_ingestion.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   └── api_server.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Success Metrics
- Model accuracy >82%
- API latency <100ms
- Pipeline latency <5min
- 99.9% uptime

## Next Steps
- Add monitoring dashboard
- Implement automated retraining
- Add drift detection
- Deploy to Cloud Run
