# Vertex AI Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Setup**
```python
from google.cloud import aiplatform

aiplatform.init(project="my-project", location="us-central1")
```

### 2. **AutoML**
```python
dataset = aiplatform.TabularDataset.create(
    display_name="my-dataset",
    gcs_source="gs://bucket/data.csv"
)

job = aiplatform.AutoMLTabularTrainingJob(
    display_name="train-automl"
)

model = job.run(dataset=dataset, target_column="target")
```

### 3. **Custom Training**
```python
job = aiplatform.CustomTrainingJob(
    display_name="my-job",
    script_path="train.py",
    container_uri="gcr.io/my-project/trainer:latest"
)

model = job.run()
```

## Level 2 – Production Patterns

### Pipelines
```python
from kfp.v2 import dsl

@dsl.pipeline(name="ml-pipeline")
def pipeline():
    preprocess_op = preprocess_component()
    train_op = train_component(preprocess_op.outputs["data"])
    eval_op = evaluate_component(train_op.outputs["model"])

job = aiplatform.PipelineJob(
    display_name="my-pipeline",
    template_path="pipeline.json"
)
job.run()
```

### Model Deployment
```python
endpoint = model.deploy(
    deployed_model_display_name="my-model",
    machine_type="n1-standard-2"
)

predictions = endpoint.predict(instances=[[1, 2, 3]])
```

## Level 3 – Architect Playbook

### Feature Store
```python
featurestore = aiplatform.Featurestore.create(
    featurestore_id="my-featurestore"
)

entity_type = featurestore.create_entity_type(
    entity_type_id="users"
)
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| List models | `aiplatform.Model.list()` | View models |
| Deploy | `model.deploy()` | Deploy model |
| Predict | `endpoint.predict()` | Make predictions |

## Checklist Before Production

- [ ] Set up proper IAM roles
- [ ] Configure VPC
- [ ] Set up model registry
- [ ] Implement monitoring
- [ ] Configure auto-scaling
- [ ] Set up feature store
- [ ] Implement logging
- [ ] Configure cost monitoring
