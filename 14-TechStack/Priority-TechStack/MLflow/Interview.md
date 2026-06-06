# MLflow - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your MLflow interviews. Answers connect to your POC projects.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is MLflow and why use it?

**Answer:**
"MLflow is an open-source platform for managing the ML lifecycle. It provides tools for experiment tracking, model versioning, and deployment.

I used it in Module 04 because:

1. **Experiment Tracking**: Log and compare different training runs
2. **Reproducibility**: Package code and environments
3. **Model Registry**: Version and manage models
4. **Collaboration**: Share experiments with team
5. **Deployment**: Deploy models to production

Without MLflow, I'd have to manually track experiments in spreadsheets and manage model versions manually. MLflow automates this and provides a UI for visualization."

**Key Points:**
- ML lifecycle management
- Experiment tracking
- Model registry
- Reproducibility

---

### Q2: How does MLflow tracking work?

**Answer:**
"MLflow tracking logs parameters, metrics, and artifacts during training:

**Basic Usage:**
```python
with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_model(model, "model")
```

**What Gets Logged:**
- **Parameters**: Hyperparameters (learning_rate, batch_size)
- **Metrics**: Training metrics (accuracy, loss) - can log over time
- **Artifacts**: Models, plots, files
- **Tags**: Custom metadata

**Storage:**
- Metadata stored in tracking server (file system or database)
- Artifacts stored in artifact store (local, S3, GCS)

In Module 04, I log all hyperparameters, training metrics at each epoch, and the final model. This allows me to compare different runs and identify the best configuration."

**Key Points:**
- Parameters, metrics, artifacts
- Tracking server
- Artifact store
- UI visualization

---

### Q3: What's the difference between an experiment and a run?

**Answer:**
"**Experiment**: A container for organizing related runs. Think of it as a project folder.

**Run**: A single execution of your training code. Each time you train a model, it's a run.

**Example:**
```python
# Create experiment
mlflow.set_experiment("churn-prediction")

# Multiple runs in same experiment
with mlflow.start_run():  # Run 1
    train_model_v1()

with mlflow.start_run():  # Run 2
    train_model_v2()
```

**Benefits:**
- Compare runs within an experiment
- Organize work by project/team
- Filter and search runs

In Module 04, I have one experiment 'churn-prediction' with multiple runs testing different algorithms and hyperparameters."

**Key Points:**
- Experiment = container
- Run = single execution
- Compare runs in experiment

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How do you use MLflow Model Registry?

**Answer:**
"Model Registry provides versioning and lifecycle management:

**Registering Models:**
```python
# After training
model_uri = f"runs:/{run_id}/model"
registered_model = mlflow.register_model(model_uri, "ChurnModel")
```

**Stages:**
- **None**: Just registered
- **Staging**: Testing before production
- **Production**: Live in production
- **Archived**: Old versions

**Transitioning:**
```python
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="ChurnModel",
    version=1,
    stage="Production"
)
```

**Benefits:**
- Track which model is in production
- Easy rollback to previous versions
- A/B testing with multiple versions

In Module 04, I register all good models and use the registry to manage which version is deployed to production."

**Key Points:**
- Version control
- Stage management
- Production tracking
- Easy rollback

---

### Q5: How do you ensure reproducibility with MLflow?

**Answer:**
"MLflow ensures reproducibility through:

**1. Code Packaging (MLflow Projects)**
```python
# MLproject file defines environment
name: churn-prediction
conda_env: conda.yaml
entry_points:
  main:
    parameters:
      learning_rate: {type: float, default: 0.01}
    command: "python train.py --lr {learning_rate}"
```

**2. Environment Capture**
- Conda environment or requirements.txt
- MLflow records exact versions

**3. Artifact Storage**
- Models stored with code
- Can reproduce exact model

**4. Parameter Logging**
- All hyperparameters logged
- Can rerun with same parameters

**Reproducing a Run:**
```python
# Get run details
run = mlflow.get_run(run_id)
params = run.data.params

# Recreate environment
# Rerun with same parameters
```

In Module 04, I use MLflow Projects to package my training code, ensuring anyone can reproduce my experiments."

**Key Points:**
- Code packaging
- Environment capture
- Parameter logging
- Artifact storage

---

### Q6: How do you compare experiments in MLflow?

**Answer:**
"Multiple ways to compare:

**1. MLflow UI**
- Visual comparison of runs
- Side-by-side metrics
- Parameter differences

**2. Programmatic Search**
```python
# Search runs
runs = mlflow.search_runs(
    experiment_ids=[experiment_id],
    filter_string="metrics.accuracy > 0.9",
    order_by=["metrics.accuracy DESC"]
)

# Compare
for run in runs:
    print(f"Run {run.run_id}: Accuracy={run.data.metrics['accuracy']}")
```

**3. Best Run Selection**
```python
best_run = runs.iloc[0]  # Highest accuracy
best_model = mlflow.sklearn.load_model(
    f"runs:/{best_run.run_id}/model"
)
```

**Comparison Metrics:**
- Accuracy, loss, F1-score
- Training time
- Resource usage
- Parameter differences

In Module 04, I compare runs to find the best hyperparameters and algorithm combination."

**Key Points:**
- UI comparison
- Programmatic search
- Filter and sort
- Best run selection

---

## 🔴 ADVANCED LEVEL Questions

### Q7: How would you integrate MLflow with a CI/CD pipeline?

**Answer:**
"**CI/CD Integration:**

**1. Training Pipeline**
```yaml
# GitHub Actions
- name: Train Model
  run: |
    python train.py
    
- name: Register Model
  run: |
    mlflow.register_model(
      model_uri,
      "ChurnModel"
    )
```

**2. Model Validation**
```python
# In CI pipeline
run = mlflow.get_run(run_id)
accuracy = run.data.metrics['accuracy']

if accuracy < 0.9:
    raise Exception("Model accuracy too low")
```

**3. Automated Deployment**
```python
# If validation passes
client.transition_model_version_stage(
    name="ChurnModel",
    version=new_version,
    stage="Staging"
)

# Deploy to staging
deploy_to_staging(model_uri)
```

**4. Production Promotion**
```python
# After staging tests pass
client.transition_model_version_stage(
    name="ChurnModel",
    version=version,
    stage="Production"
)
```

**Benefits:**
- Automated model validation
- Consistent deployment process
- Audit trail
- Easy rollback

In Module 04, I'd integrate this with GitHub Actions to automate the entire pipeline from training to deployment."

**Key Points:**
- CI/CD integration
- Automated validation
- Staged deployment
- Audit trail

---

### Q8: How do you handle model versioning and rollback?

**Answer:**
"**Versioning Strategy:**

**1. Semantic Versioning**
- Major: Breaking changes
- Minor: New features
- Patch: Bug fixes

**2. Model Registry**
```python
# Register with version
model = mlflow.register_model(model_uri, "ChurnModel")

# Get all versions
versions = client.search_model_versions("name='ChurnModel'")
```

**3. Rollback Process**
```python
# Current production
prod_version = client.get_latest_versions(
    "ChurnModel",
    stages=["Production"]
)[0]

# Rollback to previous version
client.transition_model_version_stage(
    name="ChurnModel",
    version=prod_version.version - 1,
    stage="Production"
)

# Archive current
client.transition_model_version_stage(
    name="ChurnModel",
    version=prod_version.version,
    stage="Archived"
)
```

**4. A/B Testing**
```python
# Deploy two versions
# Monitor metrics
# Keep better performing version
```

**Best Practices:**
- Always keep previous version available
- Test rollback procedure
- Monitor production metrics
- Document version changes

In Module 04, I maintain at least 2 production-ready versions for quick rollback if issues occur."

**Key Points:**
- Semantic versioning
- Registry management
- Rollback procedure
- A/B testing

---

### Q9: How would you design an MLflow-based MLOps system?

**Answer:**
"**Architecture:**

**1. Experimentation Layer**
- MLflow Tracking for experiments
- Multiple experiments per project
- Team collaboration

**2. Model Management Layer**
- Model Registry for versioning
- Stage management (Dev → Staging → Prod)
- Approval workflows

**3. Deployment Layer**
- Automated deployment from registry
- Integration with serving infrastructure
- Health checks

**4. Monitoring Layer**
- Production metrics tracking
- Drift detection
- Automated retraining triggers

**5. CI/CD Integration**
- Automated training pipelines
- Model validation
- Staged deployments

**Flow:**
```
Training → MLflow Tracking → Model Registry →
  → Validation → Staging → Production →
  → Monitoring → Retraining (if needed)
```

**Components:**
- MLflow Tracking Server
- Model Registry
- Artifact Store (GCS/S3)
- CI/CD Pipeline
- Monitoring System

**From Module 04:**
I built this with MLflow for tracking, Vertex AI for deployment, and automated retraining based on drift detection."

**Key Points:**
- Multi-layer architecture
- Automated workflows
- Monitoring integration
- CI/CD pipeline

---

### Q10: How do you optimize MLflow for large-scale use?

**Answer:**
"**Optimization Strategies:**

**1. Backend Storage**
- Use database backend (PostgreSQL) instead of file system
- Scales better for many runs
- Better query performance

**2. Artifact Storage**
- Use cloud storage (GCS, S3) instead of local
- Handles large models
- Better for distributed teams

**3. Run Cleanup**
```python
# Archive old runs
client.delete_run(run_id)

# Or use retention policies
```

**4. Efficient Logging**
```python
# Batch metric logging
metrics = {"acc": 0.95, "loss": 0.05}
mlflow.log_metrics(metrics)  # Single call

# Instead of multiple calls
```

**5. Model Registry Organization**
- Use naming conventions
- Tag models appropriately
- Archive old versions

**6. Distributed Tracking**
- Multiple tracking servers
- Load balancing
- Regional deployments

**Performance:**
- Database backend: 10x faster queries
- Cloud artifacts: Unlimited storage
- Batch logging: Reduced overhead

In production, I'd use PostgreSQL backend and GCS for artifacts to handle thousands of runs efficiently."

**Key Points:**
- Database backend
- Cloud artifacts
- Run cleanup
- Efficient logging

---

## 🎯 System Design Questions

### Q11: Design an experiment tracking system.

**Answer:**
"**Architecture:**

**Components:**
1. **Tracking Server**: Stores metadata (PostgreSQL)
2. **Artifact Store**: Stores models/files (GCS)
3. **UI Dashboard**: Visualization (MLflow UI)
4. **API Layer**: REST API for logging
5. **Client Libraries**: Python, R, Java clients

**Features:**
- Log parameters, metrics, artifacts
- Search and filter runs
- Compare experiments
- Model versioning
- Team collaboration

**Scalability:**
- Database for metadata (scales horizontally)
- Object storage for artifacts (unlimited)
- Caching for UI
- Load balancing for API

**Security:**
- Authentication/authorization
- Encrypted storage
- Audit logging

This is essentially MLflow's architecture, which I use in Module 04 for tracking all my experiments."

---

## 💡 STAR Framework Examples

### Situation: Managing ML Experiments

**Situation**: Needed to track and compare multiple ML experiments for churn prediction.

**Task**: Implement experiment tracking system to manage runs and identify best models.

**Action**: 
- Set up MLflow tracking server
- Integrated into training pipeline
- Logged all parameters and metrics
- Used Model Registry for versioning
- Set up UI for team collaboration

**Result**: 
- Can compare 50+ experiments easily
- Identified best model configuration
- Reduced experiment time by 40%
- Team can collaborate effectively

---

## 📊 Quick Reference

### Key Concepts
1. **Tracking**: Log experiments
2. **Registry**: Version models
3. **Projects**: Package code
4. **Models**: Deploy models
5. **UI**: Visualize experiments

### Common Interview Topics
- Experiment tracking
- Model versioning
- Reproducibility
- CI/CD integration
- Production deployment

---

## ✅ Practice Checklist

- [ ] Can explain MLflow in 2 minutes
- [ ] Understand tracking vs registry
- [ ] Know how to compare experiments
- [ ] Understand model versioning
- [ ] Know CI/CD integration
- [ ] Can explain your POC usage
- [ ] Ready for system design questions

---

**Remember**: Connect answers to your actual POC projects (Module 04).

