# MLflow - Complete Guide (Basic to Advanced)

## 🎯 What is MLflow?

**MLflow** is an open-source platform for managing the ML lifecycle, including experimentation, reproducibility, and deployment. You use it in Module 04 for experiment tracking and model versioning.

### Why MLflow?
- **Experiment Tracking**: Log and compare ML experiments
- **Reproducibility**: Package code and environments
- **Model Registry**: Version and manage models
- **Deployment**: Deploy models to production
- **Collaboration**: Share experiments with team

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic MLflow Usage

```python
import mlflow
import mlflow.sklearn

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("my-experiment")

# Start a run
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("epochs", 10)
    
    # Train model
    model = train_model()
    
    # Log metrics
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metric("loss", 0.05)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
```

### Key Concepts

#### 1. **Tracking Server**
- Stores experiments, runs, metrics, parameters
- Can be local file system or remote server
- Provides UI for visualization

#### 2. **Experiments**
- Group related runs together
- Compare different approaches
- Organize ML work

#### 3. **Runs**
- Single execution of training code
- Contains parameters, metrics, artifacts
- Can be compared with other runs

#### 4. **Models**
- Trained models stored as artifacts
- Can be loaded and used for predictions
- Supports multiple frameworks

### Basic Example: Track Training

```python
import mlflow
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

mlflow.set_experiment("churn-prediction")

with mlflow.start_run():
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    # Log metrics
    mlflow.log_metric("accuracy", accuracy)
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
    
    print(f"Run ID: {mlflow.active_run().info.run_id}")
```

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Advanced Logging

```python
# Log multiple metrics over time
for epoch in range(10):
    train_loss = train_epoch()
    val_loss = validate_epoch()
    
    mlflow.log_metric("train_loss", train_loss, step=epoch)
    mlflow.log_metric("val_loss", val_loss, step=epoch)

# Log dictionaries
params = {"lr": 0.01, "batch_size": 32, "epochs": 100}
mlflow.log_params(params)

metrics = {"accuracy": 0.95, "precision": 0.93, "recall": 0.89}
mlflow.log_metrics(metrics)

# Log artifacts
mlflow.log_artifact("plots/training_curve.png")
mlflow.log_artifacts("outputs/")  # Log entire directory
```

### Model Registry

```python
# Register model
model_uri = f"runs:/{run_id}/model"
registered_model = mlflow.register_model(model_uri, "ChurnModel")

# Create new version
model_version = mlflow.register_model(
    model_uri,
    "ChurnModel",
    tags={"stage": "production"}
)

# Transition to production
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="ChurnModel",
    version=model_version.version,
    stage="Production"
)
```

### Loading Models

```python
# Load model from run
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

# Load from registry
model = mlflow.sklearn.load_model(
    "models:/ChurnModel/Production"
)

# Make predictions
predictions = model.predict(X_new)
```

### Autologging

```python
# Automatic logging for scikit-learn
mlflow.sklearn.autolog()

# Train model - MLflow automatically logs everything
model = RandomForestClassifier()
model.fit(X_train, y_train)
# Parameters, metrics, model automatically logged!
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Custom Model Flavors

```python
import mlflow.pyfunc

class CustomModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # Load artifacts
        self.model = joblib.load(context.artifacts["model"])
    
    def predict(self, context, model_input):
        # Custom prediction logic
        return self.model.predict(model_input)

# Log custom model
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        "model",
        python_model=CustomModel(),
        artifacts={"model": "model.pkl"}
    )
```

### Model Serving

```python
# Serve model locally
mlflow models serve -m "models:/ChurnModel/Production" -p 5000

# Or programmatically
import mlflow.pyfunc

model = mlflow.pyfunc.load_model("models:/ChurnModel/Production")

# Create prediction service
class PredictionService:
    def __init__(self, model_uri):
        self.model = mlflow.pyfunc.load_model(model_uri)
    
    def predict(self, features):
        return self.model.predict(features)
```

### Experiment Comparison

```python
# Search runs
runs = mlflow.search_runs(
    experiment_ids=[experiment_id],
    filter_string="metrics.accuracy > 0.9",
    order_by=["metrics.accuracy DESC"]
)

# Get best run
best_run = runs.iloc[0]
best_model = mlflow.sklearn.load_model(
    f"runs:/{best_run.run_id}/model"
)
```

### Integration with Vertex AI

```python
# Log to MLflow during training
with mlflow.start_run():
    # Train model
    model = train_model()
    
    # Log to MLflow
    mlflow.sklearn.log_model(model, "model")
    mlflow.log_metrics(metrics)
    
    # Also register in Vertex AI
    from google.cloud import aiplatform
    aiplatform.init(project="project-id")
    
    # Upload model to Vertex AI
    vertex_model = aiplatform.Model.upload(
        display_name="churn-model",
        artifact_uri=f"gs://bucket/mlruns/{run_id}/artifacts/model"
    )
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Simple Tracking
```
Training Script → MLflow Tracking → UI Dashboard
```

### Pattern 2: With Registry
```
Training → MLflow Tracking → Model Registry → Deployment
```

### Pattern 3: Full Pipeline
```
Data → Training → MLflow Tracking → Evaluation →
  → Model Registry → Deployment → Monitoring
```

---

## 🔗 Integration with Your POCs

### Module 04: ML Pipeline
- **File**: `04-End-to-End-ML-Pipeline/src/model_training.py`
- **Usage**: Experiment tracking, model versioning
- **Features**: Log parameters, metrics, models, artifacts

---

## 📊 Best Practices

### 1. **Organize Experiments**
```python
# Use descriptive experiment names
mlflow.set_experiment("churn-prediction-v2")
```

### 2. **Log Everything**
```python
# Log all relevant information
mlflow.log_params(params)
mlflow.log_metrics(metrics)
mlflow.log_artifacts(artifacts)
mlflow.log_model(model, "model")
```

### 3. **Use Tags**
```python
# Add tags for organization
mlflow.set_tag("team", "ml-team")
mlflow.set_tag("project", "churn-prediction")
```

### 4. **Version Models**
```python
# Always register models
mlflow.register_model(model_uri, "ModelName")
```

### 5. **Monitor Production**
```python
# Track production metrics
mlflow.log_metric("production_accuracy", accuracy, step=day)
```

---

## 🎯 Key Takeaways

1. **MLflow = ML Lifecycle Management**
2. **Tracking = Log experiments**
3. **Registry = Version models**
4. **Reproducibility = Package code + env**
5. **Deployment = Serve models**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with Module 04
5. 🎯 Explain it confidently

