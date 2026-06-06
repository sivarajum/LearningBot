# Vertex AI - Complete Guide (Basic to Advanced)

## 🎯 What is Vertex AI?

**Vertex AI** is Google Cloud's unified ML platform that helps you build, deploy, and scale machine learning models faster. It's your one-stop shop for everything ML on GCP.

### Why Vertex AI Matters
- **Unified Platform**: One place for all ML needs (training, deployment, monitoring)
- **AutoML**: Train models without writing code
- **Custom Training**: Full control with your own code
- **Production-Ready**: Built-in monitoring, versioning, and scaling
- **Cost-Effective**: Pay only for what you use

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### What Can Vertex AI Do?

```python
# Vertex AI provides:
1. Model Training (AutoML or Custom)
2. Model Deployment (Endpoints)
3. Model Monitoring (Drift detection)
4. Feature Store (Feature management)
5. Pipelines (ML workflows)
```

### Key Concepts

#### 1. **Vertex AI Workbench**
- Jupyter notebook environment in the cloud
- Pre-configured with ML libraries
- Access to GCP services

#### 2. **AutoML**
- Train models without coding
- Just provide data and labels
- Best for structured data (tables, images, text)

#### 3. **Custom Training**
- Use your own code (TensorFlow, PyTorch, scikit-learn)
- Full control over training process
- Deploy anywhere

#### 4. **Model Endpoints**
- Deploy models for predictions
- Auto-scaling
- Real-time or batch predictions

### Basic Example: AutoML Training

```python
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(project="your-project", location="us-central1")

# Create dataset
dataset = aiplatform.TabularDataset.create(
    display_name="churn-dataset",
    bq_source="bq://project.dataset.table"
)

# Train AutoML model
job = aiplatform.AutoMLTabularTrainingJob(
    display_name="churn-prediction",
    optimization_objective="MAXIMIZE_AU_ROC"
)

model = job.run(
    dataset=dataset,
    target_column="is_churn",
    budget_milli_node_hours=1000
)

print(f"Model trained: {model.resource_name}")
```

### Basic Example: Deploy Model

```python
# Deploy model to endpoint
endpoint = model.deploy(
    endpoint=aiplatform.Endpoint.create(display_name="churn-endpoint"),
    machine_type="n1-standard-2"
)

# Make prediction
predictions = endpoint.predict(instances=[
    {"feature1": 1.0, "feature2": 2.0, ...}
])
```

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Custom Training with Vertex AI

#### Training Job Structure

```python
from google.cloud import aiplatform
from google.cloud.aiplatform import training_jobs

# Define custom training job
job = aiplatform.CustomTrainingJob(
    display_name="custom-churn-model",
    script_path="train.py",  # Your training script
    container_uri="gcr.io/cloud-aiplatform/training/tf-cpu.2-8:latest",
    model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-8:latest"
)

# Run training
model = job.run(
    args=["--epochs", "10", "--batch-size", "32"],
    replica_count=1,
    machine_type="n1-standard-4"
)
```

#### Training Script Template

```python
# train.py
import argparse
import os
from google.cloud import storage
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    
    # Load data from GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket("your-bucket")
    blob = bucket.blob("data/train.csv")
    df = pd.read_csv(blob.download_as_string())
    
    # Train model
    X = df.drop("target", axis=1)
    y = df["target"]
    model = RandomForestClassifier()
    model.fit(X, y)
    
    # Save model
    joblib.dump(model, "model.pkl")
    
    # Upload to GCS
    model_blob = bucket.blob("models/model.pkl")
    model_blob.upload_from_filename("model.pkl")

if __name__ == "__main__":
    main()
```

### Model Deployment Patterns

#### Real-Time Endpoint

```python
# Deploy for real-time predictions
endpoint = model.deploy(
    endpoint=aiplatform.Endpoint.create(display_name="realtime-endpoint"),
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=10,  # Auto-scaling
    traffic_split={"0": 100}  # 100% traffic to new model
)
```

#### Batch Prediction

```python
# Batch predictions for large datasets
batch_prediction_job = model.batch_predict(
    job_display_name="batch-prediction",
    instances_format="jsonl",
    predictions_format="jsonl",
    gcs_source="gs://bucket/input/*.jsonl",
    gcs_destination_prefix="gs://bucket/output/"
)

batch_prediction_job.wait()
```

### Feature Store

```python
from google.cloud import aiplatform
from google.cloud.aiplatform import featurestore

# Create feature store
fs = featurestore.Featurestore.create(
    featurestore_id="customer-features",
    online_serving_config={
        "fixed_node_count": 1
    }
)

# Create entity type
entity_type = fs.create_entity_type(
    entity_type_id="customer",
    description="Customer features"
)

# Create feature
feature = entity_type.create_feature(
    feature_id="total_spent",
    value_type="DOUBLE",
    description="Total amount spent"
)
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Vertex AI Pipelines

#### Pipeline Definition

```python
from kfp.v2 import dsl
from kfp.v2.dsl import component, Input, Output, Dataset, Model
from google.cloud import aiplatform

@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "scikit-learn"]
)
def train_model(
    dataset: Input[Dataset],
    model: Output[Model]
):
    import pandas as pd
    import joblib
    from sklearn.ensemble import RandomForestClassifier
    
    # Load data
    df = pd.read_csv(dataset.path)
    X = df.drop("target", axis=1)
    y = df["target"]
    
    # Train
    model_obj = RandomForestClassifier()
    model_obj.fit(X, y)
    
    # Save
    joblib.dump(model_obj, model.path)

@dsl.pipeline(
    name="churn-prediction-pipeline",
    pipeline_root="gs://bucket/pipelines"
)
def pipeline():
    # Data preparation step
    prepare_data_op = prepare_data()
    
    # Training step
    train_op = train_model(dataset=prepare_data_op.outputs["dataset"])
    
    # Evaluation step
    eval_op = evaluate_model(model=train_op.outputs["model"])
    
    # Deploy if good
    with dsl.Condition(eval_op.outputs["accuracy"] > 0.8):
        deploy_op = deploy_model(model=train_op.outputs["model"])

# Compile and run
from kfp.v2 import compiler
compiler.Compiler().compile(pipeline_func=pipeline, package_path="pipeline.json")

job = aiplatform.PipelineJob(
    display_name="churn-pipeline",
    template_path="pipeline.json",
    pipeline_root="gs://bucket/pipelines"
)
job.run()
```

### Model Monitoring

```python
from google.cloud.aiplatform import model_monitoring

# Create monitoring job
monitoring_job = model_monitoring.ModelMonitoringJob.create(
    model=model,
    endpoint=endpoint,
    display_name="drift-monitoring",
    monitoring_config={
        "drift_detection_config": {
            "categorical_attributes": ["category"],
            "numerical_attributes": ["amount", "quantity"],
            "threshold": 0.05  # 5% drift threshold
        },
        "sampling_config": {
            "sample_rate": 0.1  # Monitor 10% of predictions
        }
    }
)

# Check for drift
drift_results = monitoring_job.get_latest_monitoring_stats()
if drift_results.drift_detected:
    print("Drift detected! Retraining needed.")
```

### Advanced Deployment Patterns

#### A/B Testing

```python
# Deploy two model versions
endpoint = aiplatform.Endpoint("endpoints/123")

# Deploy v1 (50% traffic)
model_v1.deploy(
    endpoint=endpoint,
    deployed_model_display_name="v1",
    traffic_split={"0": 50}
)

# Deploy v2 (50% traffic)
model_v2.deploy(
    endpoint=endpoint,
    deployed_model_display_name="v2",
    traffic_split={"1": 50}
)

# Gradually shift traffic
endpoint.update_traffic_split({"0": 30, "1": 70})  # More to v2
```

#### Canary Deployment

```python
# Deploy new version with 10% traffic
new_model.deploy(
    endpoint=endpoint,
    deployed_model_display_name="canary",
    traffic_split={"0": 90, "1": 10}  # 10% to new model
)

# Monitor metrics
# If good, increase traffic
endpoint.update_traffic_split({"0": 50, "1": 50})
```

### Cost Optimization

```python
# Use preemptible VMs for training
job = aiplatform.CustomTrainingJob(...)
model = job.run(
    replica_count=4,
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    use_preemptible_vms=True  # 80% cost savings
)

# Use smaller machines for endpoints
endpoint = model.deploy(
    machine_type="n1-standard-1",  # Smaller = cheaper
    min_replica_count=0,  # Scale to zero when not used
    max_replica_count=5
)
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Simple Training → Deployment

```
Data (BigQuery) → Vertex AI Training → Model → Endpoint → API
```

### Pattern 2: Pipeline-Based ML

```
Data → Feature Engineering → Training → Evaluation → 
  → Model Registry → Deployment → Monitoring → Retraining
```

### Pattern 3: Multi-Model Serving

```
Request → Load Balancer → Endpoint → 
  → Model A (50%) or Model B (50%) → Response
```

---

## 🔗 Integration with Your POCs

### Module 02: Cloud AI Platform
- **Used for**: AutoML training, model deployment
- **Key Code**: `02-Cloud-AI-Platform/src/vertex_ai_training.py`
- **Learn**: AutoML, endpoints, basic deployment

### Module 04: ML Pipeline
- **Used for**: Custom training, pipelines, monitoring
- **Key Code**: `04-End-to-End-ML-Pipeline/src/model_training.py`
- **Learn**: Custom training, MLflow integration, production patterns

---

## 📊 Best Practices

### 1. **Use AutoML for Quick Prototypes**
```python
# Fast way to get baseline model
automl_model = aiplatform.AutoMLTabularTrainingJob(...).run(...)
```

### 2. **Use Custom Training for Control**
```python
# When you need specific algorithms or preprocessing
custom_job = aiplatform.CustomTrainingJob(...).run(...)
```

### 3. **Always Monitor Production Models**
```python
# Set up monitoring from day 1
monitoring_job = model_monitoring.ModelMonitoringJob.create(...)
```

### 4. **Version Your Models**
```python
# Use model registry for versioning
model = aiplatform.Model.upload(...)
model_version = model.create_version(...)
```

### 5. **Optimize Costs**
- Use preemptible VMs for training
- Scale endpoints to zero when not used
- Use smaller machine types when possible

---

## 🎯 Key Takeaways

1. **Vertex AI = Unified ML Platform** on GCP
2. **AutoML** = Quick, no-code training
3. **Custom Training** = Full control
4. **Endpoints** = Production serving
5. **Pipelines** = Automated workflows
6. **Monitoring** = Production reliability

---

## 📚 Next Steps

1. ✅ Read this guide (you're here!)
2. 📊 Review `Visual.md` for diagrams
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with Module 02/04
5. 🎯 Explain it confidently

---

**Remember**: Vertex AI is your ML platform. Master it, and you're ready for production ML roles.

