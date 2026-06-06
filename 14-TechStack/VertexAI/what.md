# Vertex AI: Unified ML Platform

## Overview

Vertex AI is Google Cloud's unified machine learning platform that provides end-to-end ML capabilities, from data preparation to model deployment and monitoring. It combines AutoML for automated model building with custom training options, all integrated with comprehensive MLOps tools.

## Core Components

### Vertex AI Platform Architecture
- **Unified Platform**: Single interface for all ML workflows
- **AutoML**: Automated machine learning for various data types
- **Custom Training**: Full control over model development
- **Model Registry**: Centralized model management and versioning
- **Endpoints**: Scalable model serving with monitoring
- **Feature Store**: Managed feature engineering and serving
- **Pipelines**: Orchestrated ML workflows

### Key Capabilities
- **Data Preparation**: Integrated data labeling and preprocessing
- **Model Training**: AutoML and custom training options
- **Model Evaluation**: Comprehensive performance analysis
- **Model Deployment**: Serverless and scalable serving
- **Monitoring**: Performance tracking and drift detection
- **Explainability**: Model interpretation and bias detection

## Getting Started

### Platform Setup

```python
from google.cloud import aiplatform
from google.auth import default

# Initialize Vertex AI
PROJECT_ID = 'your-project-id'
REGION = 'us-central1'
BUCKET_NAME = 'your-bucket-name'

aiplatform.init(
    project=PROJECT_ID,
    location=REGION,
    staging_bucket=f'gs://{BUCKET_NAME}'
)

# Verify authentication
credentials, project = default()
print(f"Authenticated to project: {project}")
```

### Basic AutoML Workflow

```python
def create_automl_model():
    """Create an AutoML tabular classification model"""

    # Define training data
    dataset = aiplatform.TabularDataset.create(
        display_name="customer_churn_dataset",
        gcs_source="gs://your-bucket/data/customer_churn.csv"
    )

    # Create AutoML training job
    job = aiplatform.AutoMLTabularTrainingJob(
        display_name="customer_churn_automl",
        optimization_prediction_type="classification",
        column_specs={
            "tenure": "numeric",
            "monthly_charges": "numeric",
            "contract_type": "categorical",
            "churn": "categorical"
        }
    )

    # Train model
    model = job.run(
        dataset=dataset,
        target_column="churn",
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        budget_milli_node_hours=1000,
        model_display_name="customer_churn_model"
    )

    return model

# Usage
model = create_automl_model()
print(f"Model created: {model.resource_name}")
```

## AutoML Capabilities

### Tabular Data (Regression/Classification)

```python
# Advanced AutoML tabular configuration
def advanced_automl_tabular():
    dataset = aiplatform.TabularDataset.create(
        display_name="advanced_tabular_dataset",
        gcs_source=["gs://bucket/train.csv", "gs://bucket/validation.csv"]
    )

    job = aiplatform.AutoMLTabularTrainingJob(
        display_name="advanced_automl_job",
        optimization_prediction_type="regression",
        column_transformations=[
            # Custom column transformations
            {"numeric": {"column_name": "age"}},
            {"categorical": {"column_name": "category"}},
            {"text": {"column_name": "description"}},
            {"timestamp": {"column_name": "timestamp"}}
        ],
        optimization_objective="minimize-rmse"
    )

    model = job.run(
        dataset=dataset,
        target_column="price",
        training_fraction_split=0.7,
        validation_fraction_split=0.2,
        test_fraction_split=0.1,
        budget_milli_node_hours=2000,
        disable_early_stopping=False,
        export_evaluated_data_items=True,
        export_evaluated_data_items_bigquery_destination_uri="bq://project.dataset.table"
    )

    return model

# Model evaluation
def evaluate_automl_model(model):
    # Get evaluation metrics
    evaluation = model.get_model_evaluation()

    # Print metrics
    for metric in evaluation.metrics:
        print(f"{metric.metric_id}: {metric.value}")

    # Get feature importance
    feature_importance = evaluation.feature_attributions
    for feature, importance in feature_importance.items():
        print(f"{feature}: {importance}")

# Usage
model = advanced_automl_tabular()
evaluate_automl_model(model)
```

### Image Classification and Object Detection

```python
def create_automl_image_model():
    """Create AutoML image classification model"""

    # Create dataset from Cloud Storage
    dataset = aiplatform.ImageDataset.create(
        display_name="product_images_dataset",
        gcs_source="gs://your-bucket/images/*.jpg",
        import_schema_uri=aiplatform.schema.dataset.ioformat.image.classification_single_label
    )

    # Create training job
    job = aiplatform.AutoMLImageTrainingJob(
        display_name="product_classifier_training",
        prediction_type="classification",
        multi_label=False,
        model_type="CLOUD",  # or "MOBILE_TF_VERSATILE_1", "MOBILE_TF_HIGH_ACCURACY_1"
        base_model=None  # or specify a model for transfer learning
    )

    # Train model
    model = job.run(
        dataset=dataset,
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        budget_milli_node_hours=8000,
        model_display_name="product_classifier"
    )

    return model

# Object detection
def create_automl_object_detection():
    dataset = aiplatform.ImageDataset.create(
        display_name="object_detection_dataset",
        gcs_source="gs://bucket/images/*.jpg",
        import_schema_uri=aiplatform.schema.dataset.ioformat.image.bounding_box
    )

    job = aiplatform.AutoMLImageTrainingJob(
        display_name="object_detector_training",
        prediction_type="object_detection",
        multi_label=False,
        model_type="CLOUD_HIGH_ACCURACY_1"
    )

    model = job.run(
        dataset=dataset,
        budget_milli_node_hours=20000,
        model_display_name="object_detector"
    )

    return model
```

### Text Classification and Entity Extraction

```python
def create_automl_text_model():
    """Create AutoML text classification model"""

    # Single-label classification
    dataset = aiplatform.TextDataset.create(
        display_name="sentiment_dataset",
        gcs_source="gs://bucket/text_data.csv",
        import_schema_uri=aiplatform.schema.dataset.ioformat.text.single_label_classification
    )

    job = aiplatform.AutoMLTextTrainingJob(
        display_name="sentiment_classifier_training",
        prediction_type="classification"
    )

    model = job.run(
        dataset=dataset,
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        model_display_name="sentiment_classifier"
    )

    return model

# Multi-label classification
def create_multilabel_text_model():
    dataset = aiplatform.TextDataset.create(
        display_name="multilabel_dataset",
        gcs_source="gs://bucket/multilabel_data.jsonl",
        import_schema_uri=aiplatform.schema.dataset.ioformat.text.multi_label_classification
    )

    job = aiplatform.AutoMLTextTrainingJob(
        display_name="multilabel_classifier",
        prediction_type="classification"
    )

    model = job.run(
        dataset=dataset,
        model_display_name="multilabel_classifier"
    )

    return model

# Entity extraction
def create_entity_extraction_model():
    dataset = aiplatform.TextDataset.create(
        display_name="entity_extraction_dataset",
        gcs_source="gs://bucket/entity_data.jsonl",
        import_schema_uri=aiplatform.schema.dataset.ioformat.text.extraction
    )

    job = aiplatform.AutoMLTextTrainingJob(
        display_name="entity_extractor",
        prediction_type="extraction"
    )

    model = job.run(
        dataset=dataset,
        model_display_name="entity_extractor"
    )

    return model
```

### Video Classification

```python
def create_automl_video_model():
    """Create AutoML video classification model"""

    dataset = aiplatform.VideoDataset.create(
        display_name="video_dataset",
        gcs_source="gs://bucket/videos/*.mp4",
        import_schema_uri=aiplatform.schema.dataset.ioformat.video.classification
    )

    job = aiplatform.AutoMLVideoTrainingJob(
        display_name="video_classifier_training",
        prediction_type="classification"
    )

    model = job.run(
        dataset=dataset,
        training_fraction_split=0.8,
        validation_fraction_split=0.1,
        test_fraction_split=0.1,
        model_display_name="video_classifier"
    )

    return model

# Action recognition
def create_action_recognition_model():
    dataset = aiplatform.VideoDataset.create(
        display_name="action_recognition_dataset",
        gcs_source="gs://bucket/action_videos/*.mp4",
        import_schema_uri=aiplatform.schema.dataset.ioformat.video.action_recognition
    )

    job = aiplatform.AutoMLVideoTrainingJob(
        display_name="action_recognizer",
        prediction_type="action_recognition"
    )

    model = job.run(
        dataset=dataset,
        model_display_name="action_recognizer"
    )

    return model
```

## Custom Training

### Custom Training Jobs

```python
def custom_training_job():
    """Run custom training job with custom container"""

    # Define training job
    job = aiplatform.CustomTrainingJob(
        display_name="custom_tensorflow_training",
        script_path="trainer/train.py",
        container_uri="gcr.io/your-project/custom-training:latest",
        requirements=["tensorflow==2.8.0", "pandas", "scikit-learn"],
        model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-8:latest"
    )

    # Run training
    model = job.run(
        dataset=None,  # Custom training handles data loading
        model_display_name="custom_tf_model",
        args=[
            "--batch_size=32",
            "--epochs=10",
            "--learning_rate=0.001",
            "--model_dir=gs://bucket/models"
        ],
        replica_count=1,
        machine_type="n1-standard-4",
        accelerator_type="ACCELERATOR_TYPE_NVIDIA_TESLA_K80",
        accelerator_count=1
    )

    return model

# Distributed training
def distributed_training():
    job = aiplatform.CustomTrainingJob(
        display_name="distributed_training",
        script_path="trainer/distributed_train.py",
        container_uri="gcr.io/your-project/distributed-training:latest",
        model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-8:latest"
    )

    model = job.run(
        model_display_name="distributed_model",
        args=["--num_workers=4", "--batch_size=64"],
        replica_count=4,  # Number of worker replicas
        machine_type="n1-highmem-8",
        accelerator_type="ACCELERATOR_TYPE_NVIDIA_TESLA_V100",
        accelerator_count=2
    )

    return model
```

### Hyperparameter Tuning

```python
def hyperparameter_tuning():
    """Perform hyperparameter tuning with Vertex AI"""

    # Define custom job for tuning
    job = aiplatform.CustomTrainingJob(
        display_name="hpt_training",
        script_path="trainer/hpt_train.py",
        container_uri="gcr.io/your-project/hpt-training:latest",
        model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-8:latest"
    )

    # Define hyperparameter tuning job
    hpt_job = aiplatform.HyperparameterTuningJob(
        display_name="hpt_job",
        custom_job=job,
        metric_spec={
            "accuracy": "maximize",
            "loss": "minimize"
        },
        parameter_spec={
            "learning_rate": aiplatform.hyperparameter_tuning.DoubleParameterSpec(
                min=0.001, max=0.1, scale="log"
            ),
            "batch_size": aiplatform.hyperparameter_tuning.IntegerParameterSpec(
                min=16, max=128, scale="linear"
            ),
            "num_layers": aiplatform.hyperparameter_tuning.IntegerParameterSpec(
                min=1, max=5, scale="linear"
            ),
            "dropout_rate": aiplatform.hyperparameter_tuning.DoubleParameterSpec(
                min=0.0, max=0.5, scale="linear"
            )
        },
        max_trial_count=20,
        parallel_trial_count=5
    )

    # Run hyperparameter tuning
    hpt_job.run()

    # Get best trial
    best_trial = hpt_job.trials[0]  # Trials are sorted by objective value
    print(f"Best trial: {best_trial.id}")
    print(f"Best hyperparameters: {best_trial.parameters}")
    print(f"Best metrics: {best_trial.final_measurement.metrics}")

    return hpt_job
```

### Training with Pre-built Containers

```python
def prebuilt_container_training():
    """Use pre-built containers for common frameworks"""

    # TensorFlow training
    job = aiplatform.CustomTrainingJob(
        display_name="tensorflow_training",
        script_path="trainer/task.py",
        container_uri="gcr.io/cloud-aiplatform/training/tf-cpu.2-8:latest",
        model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-8:latest"
    )

    # PyTorch training
    job = aiplatform.CustomTrainingJob(
        display_name="pytorch_training",
        script_path="trainer/train.py",
        container_uri="gcr.io/cloud-aiplatform/training/pytorch-cpu.1-11:latest",
        model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/pytorch-cpu.1-11:latest"
    )

    # XGBoost training
    job = aiplatform.CustomTrainingJob(
        display_name="xgboost_training",
        script_path="trainer/train.py",
        container_uri="gcr.io/cloud-aiplatform/training/scikit-learn-cpu.0-24:latest",
        model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.0-24:latest"
    )

    # Run training
    model = job.run(
        model_display_name="prebuilt_model",
        args=["--model_dir", "gs://bucket/models"]
    )

    return model
```

## Model Deployment and Serving

### Endpoint Creation and Deployment

```python
def deploy_model_to_endpoint():
    """Deploy model to Vertex AI endpoint"""

    # Get existing model
    model = aiplatform.Model("projects/your-project/locations/us-central1/models/your-model-id")

    # Create endpoint
    endpoint = aiplatform.Endpoint.create(
        display_name="model_endpoint",
        project=PROJECT_ID,
        location=REGION
    )

    # Deploy model to endpoint
    deployed_model = endpoint.deploy(
        model=model,
        deployed_model_display_name="deployed_model_v1",
        traffic_percentage=100,
        machine_type="n1-standard-2",
        min_replica_count=1,
        max_replica_count=3,
        accelerator_type=None,
        accelerator_count=0
    )

    print(f"Model deployed to endpoint: {endpoint.resource_name}")
    return endpoint

# GPU deployment
def deploy_with_gpu():
    endpoint = aiplatform.Endpoint.create(display_name="gpu_endpoint")

    deployed_model = endpoint.deploy(
        model=model,
        deployed_model_display_name="gpu_model",
        machine_type="n1-standard-4",
        accelerator_type="ACCELERATOR_TYPE_NVIDIA_TESLA_T4",
        accelerator_count=1,
        min_replica_count=1,
        max_replica_count=5
    )

    return endpoint
```

### Online Prediction

```python
def online_prediction():
    """Make online predictions"""

    # Get endpoint
    endpoint = aiplatform.Endpoint("projects/your-project/locations/us-central1/endpoints/your-endpoint-id")

    # Prepare instances for prediction
    instances = [
        {
            "feature1": 1.0,
            "feature2": "category_a",
            "feature3": [0.1, 0.2, 0.3]
        },
        {
            "feature1": 2.0,
            "feature2": "category_b",
            "feature3": [0.4, 0.5, 0.6]
        }
    ]

    # Make prediction
    prediction = endpoint.predict(instances=instances)

    print("Predictions:")
    for i, pred in enumerate(prediction.predictions):
        print(f"Instance {i}: {pred}")

    # Get prediction explanations (if enabled)
    if hasattr(prediction, 'explanations'):
        for i, explanation in enumerate(prediction.explanations):
            print(f"Explanation {i}: {explanation}")

    return prediction

# Batch prediction
def batch_prediction():
    """Make batch predictions"""

    # Get model
    model = aiplatform.Model("projects/your-project/locations/us-central1/models/your-model-id")

    # Create batch prediction job
    batch_prediction_job = model.batch_predict(
        job_display_name="batch_prediction_job",
        gcs_source="gs://bucket/input_data.csv",
        gcs_destination_prefix="gs://bucket/predictions",
        instances_format="csv",
        predictions_format="jsonl",
        machine_type="n1-standard-2",
        accelerator_type=None,
        accelerator_count=0,
        starting_replica_count=1,
        max_replica_count=10
    )

    # Wait for completion
    batch_prediction_job.wait()

    print(f"Batch prediction completed: {batch_prediction_job.resource_name}")
    return batch_prediction_job
```

### Model Monitoring

```python
def setup_model_monitoring():
    """Set up monitoring for deployed model"""

    from google.cloud.aiplatform import model_monitoring

    # Create model monitor
    model_monitor = model_monitoring.ModelMonitor.create(
        display_name="churn_model_monitor",
        project=PROJECT_ID,
        location=REGION
    )

    # Configure monitoring objective
    monitoring_config = model_monitoring.ModelMonitoringConfig(
        # Data drift detection
        data_drift_config=model_monitoring.DataDriftConfig(
            drift_threshold=0.1,
            attribute_drift_thresholds={
                "tenure": 0.05,
                "monthly_charges": 0.1
            }
        ),
        # Prediction drift detection
        prediction_drift_config=model_monitoring.PredictionDriftConfig(
            drift_threshold=0.1
        ),
        # Feature attribution drift
        feature_attribution_config=model_monitoring.FeatureAttributionConfig(
            drift_threshold=0.1
        )
    )

    # Create monitoring job
    monitoring_job = model_monitor.create_monitoring_job(
        display_name="churn_monitoring_job",
        endpoint=endpoint,
        monitoring_config=monitoring_config,
        alert_config=model_monitoring.AlertConfig(
            email_alert_config=model_monitoring.EmailAlertConfig(
                user_emails=["ml-team@company.com"]
            )
        ),
        schedule_config=model_monitoring.ScheduleConfig(
            cron="0 */4 * * *"  # Every 4 hours
        )
    )

    return monitoring_job

# Get monitoring metrics
def get_monitoring_metrics(monitoring_job):
    """Retrieve monitoring metrics"""

    # Get monitoring statistics
    stats = monitoring_job.get_monitoring_stats()

    print("Monitoring Statistics:")
    print(f"Data drift score: {stats.data_drift_score}")
    print(f"Prediction drift score: {stats.prediction_drift_score}")

    # Get feature drift details
    for feature, drift_score in stats.feature_drift_scores.items():
        print(f"{feature} drift: {drift_score}")

    return stats
```

## Feature Store

### Feature Store Management

```python
def create_feature_store():
    """Create and manage feature store"""

    from google.cloud.aiplatform import featurestore

    # Create feature store
    feature_store = featurestore.Featurestore.create(
        featurestore_id="customer_features",
        display_name="Customer Feature Store",
        online_serving_config=featurestore.OnlineServingConfig(
            fixed_node_count=1
        ),
        project=PROJECT_ID,
        location=REGION
    )

    # Create entity type
    entity_type = feature_store.create_entity_type(
        entity_type_id="customer",
        description="Customer entity features"
    )

    # Create features
    features = entity_type.create_features([
        featurestore.Feature(
            feature_id="tenure_months",
            value_type=featurestore.Feature.ValueType.INT64,
            description="Customer tenure in months"
        ),
        featurestore.Feature(
            feature_id="monthly_charges",
            value_type=featurestore.Feature.ValueType.DOUBLE,
            description="Monthly charges"
        ),
        featurestore.Feature(
            feature_id="contract_type",
            value_type=featurestore.Feature.ValueType.STRING,
            description="Contract type"
        ),
        featurestore.Feature(
            feature_id="churn_probability",
            value_type=featurestore.Feature.ValueType.DOUBLE,
            description="Predicted churn probability"
        )
    ])

    return feature_store

# Ingest features
def ingest_features(feature_store):
    """Ingest feature data"""

    # Batch ingestion
    entity_type = feature_store.get_entity_type("customer")

    feature_values = {
        "customer_123": {
            "tenure_months": 24,
            "monthly_charges": 75.50,
            "contract_type": "Month-to-month",
            "churn_probability": 0.15
        },
        "customer_456": {
            "tenure_months": 12,
            "monthly_charges": 65.25,
            "contract_type": "One year",
            "churn_probability": 0.05
        }
    }

    # Ingest to online store
    entity_type.ingest_from_dict(
        feature_ids=["tenure_months", "monthly_charges", "contract_type", "churn_probability"],
        feature_values=feature_values,
        timestamp=datetime.now()
    )

    # Batch ingestion from BigQuery
    entity_type.ingest_from_bq(
        feature_ids=["tenure_months", "monthly_charges", "contract_type"],
        feature_time="timestamp",
        bq_source_uri="bq://project.dataset.customer_features",
        entity_id_field="customer_id"
    )

# Online feature serving
def serve_features_online(feature_store):
    """Serve features for online prediction"""

    entity_type = feature_store.get_entity_type("customer")

    # Read features for specific entities
    features = entity_type.read(
        entity_ids=["customer_123", "customer_456"],
        feature_ids=["tenure_months", "monthly_charges", "contract_type"]
    )

    return features
```

## Pipelines (Kubeflow Pipelines)

### Pipeline Creation

```python
from kfp import dsl
from kfp.v2 import compiler
from kfp.v2.dsl import component

@component
def preprocess_data(input_data: str, output_data: str):
    """Preprocess data component"""
    import pandas as pd
    from sklearn.preprocessing import StandardScaler

    # Load data
    df = pd.read_csv(input_data)

    # Preprocessing logic
    scaler = StandardScaler()
    numerical_cols = ['tenure', 'monthly_charges']
    df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

    # Save processed data
    df.to_csv(output_data, index=False)

@component
def train_model(input_data: str, model_output: str, metrics_output: str):
    """Train model component"""
    import pandas as pd
    import pickle
    import json
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score
    from sklearn.model_selection import train_test_split

    # Load processed data
    df = pd.read_csv(input_data)

    # Split data
    X = df.drop('churn', axis=1)
    y = df['churn']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred)
    }

    # Save model and metrics
    with open(model_output, 'wb') as f:
        pickle.dump(model, f)

    with open(metrics_output, 'w') as f:
        json.dump(metrics, f)

@component
def deploy_model(model_input: str, endpoint_name: str):
    """Deploy model component"""
    import pickle
    from google.cloud import aiplatform

    # Load model
    with open(model_input, 'rb') as f:
        model = pickle.load(f)

    # Upload to Vertex AI
    vertex_model = aiplatform.Model.upload(
        display_name="pipeline_model",
        artifact_uri=model_input,
        serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.0-24:latest"
    )

    # Deploy to endpoint
    endpoint = aiplatform.Endpoint.create(display_name=endpoint_name)
    endpoint.deploy(model=vertex_model)

@dsl.pipeline(
    name="ml-pipeline",
    description="End-to-end ML pipeline"
)
def ml_pipeline(
    input_data: str = "gs://bucket/data.csv",
    project_id: str = PROJECT_ID,
    region: str = REGION
):
    # Preprocess data
    preprocess_task = preprocess_data(
        input_data=input_data,
        output_data="gs://bucket/processed_data.csv"
    )

    # Train model
    train_task = train_model(
        input_data=preprocess_task.output,
        model_output="gs://bucket/model.pkl",
        metrics_output="gs://bucket/metrics.json"
    )

    # Deploy model
    deploy_task = deploy_model(
        model_input=train_task.outputs["model_output"],
        endpoint_name="pipeline_endpoint"
    )

# Compile and run pipeline
def run_pipeline():
    compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path="pipeline.json"
    )

    # Submit to Vertex AI Pipelines
    from google.cloud.aiplatform import PipelineJob

    job = PipelineJob(
        display_name="ml_pipeline_job",
        template_path="pipeline.json",
        parameter_values={
            "input_data": "gs://bucket/data.csv",
            "project_id": PROJECT_ID,
            "region": REGION
        }
    )

    job.submit()
```

## Model Explainability

### Feature Attributions

```python
def explain_predictions():
    """Get explanations for model predictions"""

    # For AutoML models
    model = aiplatform.Model("projects/project/locations/region/models/model-id")

    # Get explanations
    explanation_spec = model.explanation_spec

    if explanation_spec:
        print("Explanation metadata:")
        print(f"Parameters: {explanation_spec.parameters}")

        # Make prediction with explanation
        endpoint = aiplatform.Endpoint("projects/project/locations/region/endpoints/endpoint-id")

        instances = [{"feature1": 1.0, "feature2": "value"}]

        # Enable explanations in prediction
        prediction = endpoint.explain(
            instances=instances,
            parameters={"sampled_shapley_attribution": {"path_count": 10}}
        )

        print("Prediction:", prediction.predictions)
        print("Explanations:", prediction.explanations)

# Custom explanation with SHAP
def custom_explanations():
    """Implement custom explanations for custom models"""

    import shap
    import pickle

    # Load model
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

    # Load test data
    X_test = pd.read_csv("test_data.csv")

    # Create explainer
    explainer = shap.TreeExplainer(model)

    # Calculate SHAP values
    shap_values = explainer.shap_values(X_test)

    # Summary plot
    shap.summary_plot(shap_values, X_test)

    # Waterfall plot for single prediction
    shap.plots.waterfall(explainer.expected_value[1], shap_values[1][0], X_test.iloc[0])

    return shap_values
```

## Advanced Features

### Model Registry and Versioning

```python
def manage_model_versions():
    """Manage model versions in Model Registry"""

    # Upload model to registry
    model = aiplatform.Model.upload(
        display_name="churn_model_v2",
        artifact_uri="gs://bucket/models/",
        serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.0-24:latest",
        labels={"version": "2.0", "framework": "sklearn"}
    )

    # List model versions
    models = aiplatform.Model.list(
        filter='display_name="churn_model*"',
        order_by="create_time desc"
    )

    for model in models:
        print(f"Model: {model.display_name}, Version: {model.version_id}")

    # Set alias for production model
    model.add_labels({"alias": "production"})

    return model

# Model comparison
def compare_models():
    """Compare performance of different model versions"""

    from google.cloud import bigquery

    # Query model performance from BigQuery
    client = bigquery.Client()

    query = """
    SELECT
        model_version,
        AVG(accuracy) as avg_accuracy,
        AVG(precision) as avg_precision,
        AVG(recall) as avg_recall,
        COUNT(*) as prediction_count
    FROM `project.dataset.model_performance`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    GROUP BY model_version
    ORDER BY avg_accuracy DESC
    """

    results = client.query(query).result()

    for row in results:
        print(f"Version {row.model_version}: Acc={row.avg_accuracy:.3f}, Prec={row.avg_precision:.3f}")
```

### Cost Optimization

```python
def optimize_costs():
    """Implement cost optimization strategies"""

    # Use spot instances for training
    job = aiplatform.CustomTrainingJob(
        display_name="cost_optimized_training",
        script_path="trainer/train.py",
        container_uri="gcr.io/your-project/training:latest"
    )

    model = job.run(
        model_display_name="cost_optimized_model",
        machine_type="n1-standard-4",
        accelerator_type="ACCELERATOR_TYPE_NVIDIA_TESLA_T4",
        accelerator_count=1,
        # Use spot instances (preemptible)
        spot=True,
        # Set maximum training time
        max_wait_duration=3600  # 1 hour
    )

    # Auto-scaling endpoints
    endpoint = aiplatform.Endpoint.create(display_name="auto_scaling_endpoint")

    deployed_model = endpoint.deploy(
        model=model,
        min_replica_count=1,
        max_replica_count=10,  # Auto-scale up to 10 replicas
        traffic_percentage=100
    )

    # Set up budget alerts
    from google.cloud import billing

    # Monitor costs programmatically
    # Implementation would integrate with Cloud Billing API

    return endpoint
```

## Best Practices

### Development Best Practices
1. **Use Appropriate Tools**: Choose AutoML for quick prototyping, custom training for specialized needs
2. **Version Control**: Track all experiments, models, and data versions
3. **Modular Design**: Break pipelines into reusable components
4. **Testing**: Implement comprehensive testing for models and pipelines
5. **Documentation**: Maintain clear documentation for models and processes

### Deployment Best Practices
1. **Gradual Rollout**: Use canary deployments for safe model updates
2. **Monitoring**: Implement comprehensive monitoring from day one
3. **Rollback Plan**: Have clear procedures for model rollback
4. **Resource Management**: Optimize compute resources for cost efficiency
5. **Security**: Implement proper access controls and data encryption

### Performance Best Practices
1. **Data Quality**: Ensure high-quality, representative training data
2. **Feature Engineering**: Invest time in meaningful feature creation
3. **Model Selection**: Choose appropriate algorithms for your use case
4. **Hyperparameter Tuning**: Perform systematic hyperparameter optimization
5. **Evaluation**: Use proper validation techniques and metrics

### Operational Best Practices
1. **CI/CD Integration**: Automate model training and deployment
2. **Monitoring**: Track model performance and data drift continuously
3. **Retraining**: Implement automated model retraining pipelines
4. **Governance**: Establish model governance and approval processes
5. **Cost Management**: Monitor and optimize cloud resource usage

Vertex AI represents the evolution of machine learning platforms, providing a comprehensive, unified environment that supports the entire ML lifecycle from experimentation to production deployment, enabling organizations to operationalize AI at scale while maintaining governance, security, and cost efficiency.
