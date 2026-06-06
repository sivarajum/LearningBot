# Module 06: MLOps Automation

## Overview
Automated MLOps pipeline for continuous model maintenance. Implements drift detection, automated retraining, and model deployment - ensuring production ML models stay accurate and reliable.

## Features
- ✅ Data drift detection (Evidently AI)
- ✅ Model performance monitoring
- ✅ Automated retraining triggers
- ✅ Scheduled retraining pipeline
- ✅ MLflow integration

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Usage

#### Drift Detection
```python
from src.drift_detection import DriftDetector
import pandas as pd

# Initialize detector
detector = DriftDetector(reference_data, target_column="is_churn")

# Detect drift
drift_result = detector.detect_data_drift(current_data)
print(f"Drift detected: {drift_result['drift_detected']}")
```

#### Automated Retraining
```python
from src.retraining_pipeline import AutomatedRetrainingPipeline

# Initialize pipeline
pipeline = AutomatedRetrainingPipeline(
    drift_detector=detector,
    training_function=your_training_function,
    retrain_interval_hours=24
)

# Check and retrain
result = pipeline.check_and_retrain(current_data, current_predictions)
```

## Project Structure
```
06-MLOps-Automation/
├── src/
│   ├── drift_detection.py
│   └── retraining_pipeline.py
├── requirements.txt
└── README.md
```

## Success Metrics
- Automated retraining maintains >80% accuracy
- Drift detection alerts within minutes
- Successful CI/CD deployments
- Model rollback capabilities
