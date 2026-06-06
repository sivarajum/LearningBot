# Intelligent Churn Prediction

End-to-end ML churn prediction pipeline with XGBoost — synthetic data generation, feature engineering, model training, FastAPI serving + Streamlit dashboard.

## What It Does

- **Data Generation**: Synthetic customer data with realistic churn patterns (~2,000 records)
- **Feature Engineering**: 11 derived features (tenure buckets, charge ratios, interaction scores, StandardScaler normalization)
- **Model Training**: XGBoost classifier with 5-fold cross-validation
- **Prediction API**: Real-time churn predictions via FastAPI with Pydantic input validation
- **Dashboard**: Streamlit UI for model metrics, feature importance, individual predictions

## Architecture

```
src/data_generator.py         # Synthetic customer data generation
src/feature_engineering.py    # Feature extraction pipeline (11 features)
src/model.py                  # XGBoost training + evaluation + persistence
src/pipeline.py               # End-to-end pipeline orchestration
src/api.py                    # FastAPI prediction API
src/ui.py                     # Streamlit dashboard
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py pipeline    # Train model (generates data + trains)
python main.py api         # API on :8002
python main.py ui          # Dashboard on :8501
python main.py all         # Both API + UI
```

## Testing

```bash
pytest                     # 85 tests
```

## Model Performance

Typical results on synthetic data:
- Accuracy: ~85%
- Precision: ~74%
- Recall: ~70%
- AUC-ROC: ~0.87

## Docker

```bash
docker compose up --build
```

See [RUNNING.md](RUNNING.md) for full build, test, and deployment instructions.
