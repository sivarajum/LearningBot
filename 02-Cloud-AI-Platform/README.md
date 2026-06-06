# Module 02: Cloud AI Platform - Vertex AI Churn Prediction

## Overview
End-to-end machine learning on Google Cloud Platform using Vertex AI for customer churn prediction with production-ready deployment.

## Architecture
- **Data Storage**: BigQuery
- **Model Training**: Vertex AI AutoML
- **Model Deployment**: Vertex AI Endpoints
- **API Serving**: FastAPI REST API
- **Deployment**: Cloud Run

## Features
- ✅ Vertex AI AutoML training
- ✅ Automated model deployment
- ✅ Real-time predictions
- ✅ FastAPI REST API
- ✅ Production-ready code

## Quick Start

### Prerequisites
- GCP project with Vertex AI enabled
- BigQuery dataset with training data
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
export VERTEX_AI_ENDPOINT_NAME="your-endpoint-name"
```

2. Prepare training data in BigQuery:
```sql
-- Ensure customer_features table exists with is_churn column
```

3. Train AutoML model:
```python
from src.vertex_ai_training import VertexAITrainingPipeline

pipeline = VertexAITrainingPipeline(
    project_id="your-project-id",
    dataset_id="customer_data",
    table_id="customer_features"
)

result = pipeline.train_automl_model(
    display_name="churn-prediction-automl",
    budget_milli_node_hours=1000
)
```

4. Deploy model:
```python
deployment = pipeline.deploy_model(
    model_name=result["model_name"],
    endpoint_display_name="churn-prediction-endpoint"
)
```

5. Start API server:
```bash
python src/api_server.py
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Prediction
```bash
POST /predict
Content-Type: application/json

{
  "instances": [
    {
      "feature1": value1,
      "feature2": value2,
      ...
    }
  ]
}
```

## Project Structure
```
02-Cloud-AI-Platform/
├── src/
│   ├── vertex_ai_training.py
│   └── api_server.py
├── requirements.txt
└── README.md
```

## Success Metrics
- Model AUC >0.85
- API latency <100ms
- Throughput >1000 req/min
- 99.9% uptime

## Cost Optimization
- Use AutoML budget controls
- Deploy with appropriate machine types
- Monitor usage and costs

## Next Steps
- Add monitoring dashboard
- Implement batch predictions
- Add model versioning
- Deploy to Cloud Run
