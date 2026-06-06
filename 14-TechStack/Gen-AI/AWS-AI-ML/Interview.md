# AWS AI/ML: Interview Questions & Answers

## Beginner Level

### Q1: What are the three tiers of AWS AI/ML services?
**A:**

| Tier | Services | Who Uses It |
|------|----------|------------|
| **AI Services** (pre-built APIs) | Comprehend (NLP), Rekognition (vision), Textract (docs), Polly (speech), Lex (chatbots) | Developers — no ML needed |
| **ML Platform** (SageMaker) | Training, tuning, deployment, monitoring, pipelines | Data scientists |
| **Foundation Models** (Bedrock) | Claude, Llama, Titan, Stable Diffusion | Anyone building GenAI apps |

Rule of thumb: Start with AI Services → if accuracy insufficient → SageMaker custom → if GenAI needed → Bedrock.

### Q2: How does SageMaker training work?
**A:**
```python
from sagemaker.estimator import Estimator

# 1. Specify algorithm (built-in or custom container)
estimator = Estimator(
    image_uri="xgboost-container-uri",
    role="arn:aws:iam::role/SageMakerRole",
    instance_count=1,
    instance_type="ml.m5.xlarge",
    hyperparameters={"max_depth": 5, "eta": 0.2, "num_round": 100},
    output_path="s3://bucket/output",
)

# 2. Point to S3 data → SageMaker spins up instance, trains, saves model to S3
estimator.fit({"train": "s3://bucket/train.csv"})

# 3. Deploy to real-time endpoint
predictor = estimator.deploy(instance_type="ml.m5.large", initial_instance_count=1)
```

SageMaker manages: provisioning, training, saving model artifacts, endpoint deployment. You provide: data in S3, algorithm choice, hyperparameters.

### Q3: What is Amazon Bedrock?
**A:** Bedrock is a managed service for accessing foundation models (FMs) via API.

```python
import boto3, json
client = boto3.client("bedrock-runtime")

# Access Claude via Bedrock (no infrastructure to manage)
response = client.invoke_model(
    modelId="anthropic.claude-sonnet-4-20250514-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Hello"}],
    }),
)
```

Key benefits: single API for multiple providers (Anthropic, Meta, Amazon, etc.), VPC private access, no model hosting management.

### Q4: When to use Comprehend vs custom NLP?
**A:**

| Use Case | Comprehend | Custom |
|----------|-----------|--------|
| General sentiment | ✅ Works well | Overkill |
| Entity recognition (standard) | ✅ PERSON, ORG, DATE | Not needed |
| Financial domain NER | ⚠️ Misses stock symbols | ✅ Fine-tune BERT |
| Custom classification | ✅ Comprehend Custom | ✅ SageMaker |
| Indian language support | ✅ Hindi, Tamil, etc. | ✅ Multilingual models |

```python
# Quick sentiment check — Comprehend (no training needed)
comprehend = boto3.client("comprehend")
result = comprehend.detect_sentiment(Text="RELIANCE profit surges", LanguageCode="en")
# If accuracy < 80% for your domain → fine-tune custom model
```

---

## Intermediate Level

### Q5: Design a SageMaker ML pipeline for stock prediction.
**A:**
```python
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep
from sagemaker.workflow.conditions import ConditionGreaterThan
from sagemaker.workflow.condition_step import ConditionStep

# Step 1: Feature engineering
process_step = ProcessingStep(
    name="FeatureEngineering",
    processor=SKLearnProcessor(role=role, instance_type="ml.m5.large"),
    code="scripts/preprocess.py",
    inputs=[ProcessingInput(source="s3://bucket/raw/", destination="/opt/ml/processing/input")],
    outputs=[ProcessingOutput(source="/opt/ml/processing/output/", destination="s3://bucket/features/")],
)

# Step 2: Train
train_step = TrainingStep(name="Train", estimator=xgb_estimator)

# Step 3: Evaluate
eval_step = ProcessingStep(name="Evaluate", processor=processor, code="scripts/evaluate.py")

# Step 4: Conditional deploy (only if accuracy > 0.6)
condition = ConditionGreaterThan(left=eval_step.properties.Outputs["accuracy"], right=0.6)
deploy_step = CreateModelStep(name="Deploy", model=model)
cond_step = ConditionStep(name="CheckAccuracy", conditions=[condition], if_steps=[deploy_step])

pipeline = Pipeline(name="stock-predictor", steps=[process_step, train_step, eval_step, cond_step])
```

### Q6: How do you implement SageMaker model monitoring?
**A:**
```python
from sagemaker.model_monitor import DataCaptureConfig, DefaultModelMonitor

# 1. Enable data capture on endpoint
data_capture = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,
    destination_s3_uri=f"s3://{bucket}/capture",
    capture_options=["Input", "Output"],
)

predictor = model.deploy(
    instance_type="ml.m5.large",
    data_capture_config=data_capture,
)

# 2. Create baseline from training data
monitor = DefaultModelMonitor(role=role, instance_type="ml.m5.large")
monitor.suggest_baseline(
    baseline_dataset="s3://bucket/train.csv",
    dataset_format=DatasetFormat.csv(header=True),
)

# 3. Schedule monitoring (hourly)
monitor.create_monitoring_schedule(
    monitor_schedule_name="stock-predictor-monitor",
    endpoint_input=predictor.endpoint_name,
    statistics=monitor.baseline_statistics(),
    constraints=monitor.suggested_constraints(),
    schedule_cron_expression="cron(0 * ? * * *)",
)
```

Monitors: data drift, prediction drift, feature importance shifts.

### Q7: How do you use SageMaker Autopilot (AutoML)?
**A:**
```python
from sagemaker.automl import AutoML

automl = AutoML(
    role=role,
    target_attribute_name="signal",  # Column to predict
    output_path=f"s3://{bucket}/automl-output",
    max_candidates=20,
    problem_type="BinaryClassification",
)

automl.fit(inputs="s3://bucket/training_data.csv")

# Get best model
best = automl.best_candidate()
print(f"Best model: {best['CandidateName']}, Metric: {best['FinalAutoMLJobObjectiveMetric']}")

# Deploy best model
predictor = automl.deploy(initial_instance_count=1, instance_type="ml.m5.large")
```

---

## Advanced Level

### Q8: Design a production ML system on AWS for financial trading.
**A:**

```python
# Architecture:
# S3 (data lake) → SageMaker Pipeline (daily retrain) → Model Registry
# → SageMaker Endpoint (real-time inference) → Model Monitor (drift detection)
# → Bedrock (GenAI layer for analysis) → EventBridge (orchestration)

# Daily pipeline via EventBridge
{
    "source": "aws.events",
    "detail-type": "Scheduled Event",
    "detail": {"pipeline": "stock-predictor-daily"},
    "schedule": "cron(0 18 ? * MON-FRI *)"  # 6 PM IST after market close
}

# Multi-model endpoint (serve all strategies from one endpoint)
from sagemaker.multidatamodel import MultiDataModel
mdm = MultiDataModel(
    name="trading-strategies",
    model_data_prefix=f"s3://{bucket}/models/",
    image_uri=inference_image,
    role=role,
)
predictor = mdm.deploy(instance_type="ml.m5.xlarge", initial_instance_count=2)

# Route to specific model
predictor.predict(data, target_model="momentum-v1.tar.gz")
predictor.predict(data, target_model="mean-reversion-v1.tar.gz")
```

### Q9: How do you optimize SageMaker costs?
**A:**

| Strategy | Savings | Implementation |
|----------|---------|---------------|
| Spot training | 70-90% | `use_spot_instances=True, max_wait=7200` |
| Serverless inference | Up to 90% | Zero cost when idle |
| Multi-model endpoint | 50-70% | One endpoint serves N models |
| Auto-scaling to zero | Variable | Scale-in policy with cooldown |
| Savings Plans | 20-30% | 1-3 year commitment |

```python
# Spot training (70% savings)
estimator = Estimator(
    ...,
    use_spot_instances=True,
    max_wait=7200,  # Max wait for spot capacity
    max_run=3600,   # Max training time
)

# Serverless inference (pay per request)
from sagemaker.serverless import ServerlessInferenceConfig
predictor = model.deploy(
    serverless_inference_config=ServerlessInferenceConfig(
        memory_size_in_mb=2048,
        max_concurrency=10,
    )
)
```

### Q10: How do you implement A/B testing with SageMaker?
**A:**
```python
from sagemaker.model import Model

# Deploy two model versions
model_a = Model(model_data="s3://bucket/model-v1.tar.gz", image_uri=image, role=role)
model_b = Model(model_data="s3://bucket/model-v2.tar.gz", image_uri=image, role=role)

# Production variant with traffic split
endpoint_config = sagemaker.Session().create_endpoint_config(
    name="ab-test-config",
    production_variants=[
        {"ModelName": model_a.name, "VariantName": "v1", "InitialVariantWeight": 0.9},
        {"ModelName": model_b.name, "VariantName": "v2", "InitialVariantWeight": 0.1},
    ],
)

# Monitor metrics per variant → if v2 outperforms → shift 100% traffic
sagemaker.Session().update_endpoint_weights_and_capacities(
    endpoint_name="my-endpoint",
    desired_weights_and_capacities=[
        {"DesiredWeight": 0.0, "VariantName": "v1"},
        {"DesiredWeight": 1.0, "VariantName": "v2"},
    ],
)
```

---

## Advanced Level (5 Additional Q&As)

### Q11: How do you build GenAI applications with Amazon Bedrock?
**A:**

```python
import boto3, json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# 1. Text generation with Claude on Bedrock
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Analyze NIFTY 50 trading signal: RSI=72, MACD bullish crossover"}],
    }),
)
result = json.loads(response["body"].read())

# 2. Embeddings with Titan
embed_response = bedrock.invoke_model(
    modelId="amazon.titan-embed-text-v2:0",
    body=json.dumps({"inputText": "SEBI circular on margin requirements"}),
)

# 3. Knowledge Bases (managed RAG)
bedrock_agent = boto3.client("bedrock-agent-runtime")
response = bedrock_agent.retrieve_and_generate(
    input={"text": "What are SEBI position limits for F&O?"},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": "KB_ID",
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
        },
    },
)
```

**Bedrock vs SageMaker:**
| Feature | Bedrock | SageMaker |
|---------|---------|-----------|
| Use case | Use pre-built foundation models | Train/deploy custom models |
| Setup | Zero infra, API call | Full ML lifecycle management |
| Cost | Per-token pricing | Instance-hour pricing |
| Customization | Fine-tuning, RAG | Full training control |
| Best for | GenAI apps, RAG, agents | Custom ML models, training |

### Q12: Design a multi-model ML pipeline on SageMaker for trading signals.
**A:**

```python
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, TransformStep
from sagemaker.workflow.conditions import ConditionGreaterThan
from sagemaker.workflow.condition_step import ConditionStep

# Step 1: Feature engineering (PySpark on SageMaker Processing)
processing_step = ProcessingStep(
    name="FeatureEngineering",
    processor=spark_processor,
    code="scripts/feature_engineering.py",
    inputs=[ProcessingInput(source="s3://data/ohlcv/", destination="/opt/ml/input")],
    outputs=[ProcessingOutput(source="/opt/ml/output", destination="s3://features/")],
)

# Step 2: Train XGBoost model
training_step = TrainingStep(
    name="TrainXGBoost",
    estimator=xgb_estimator,
    inputs={"train": TrainingInput(s3_data=processing_step.properties.ProcessingOutputConfig.Outputs["features"])},
)

# Step 3: Evaluate model
eval_step = ProcessingStep(name="EvaluateModel", processor=eval_processor, code="evaluate.py")

# Step 4: Conditional deploy (only if AUC > 0.55)
condition = ConditionGreaterThan(left=JsonGet(step_name="EvaluateModel", property_file="eval", json_path="auc"), right=0.55)
deploy_step = ConditionStep(name="DeployGate", conditions=[condition], if_steps=[deploy], else_steps=[notify_failure])

pipeline = Pipeline(name="trading-signals", steps=[processing_step, training_step, eval_step, deploy_step])
pipeline.upsert(role_arn=role)
pipeline.start()
```

### Q13: How do you implement real-time inference with SageMaker for sub-100ms latency?
**A:**

Key strategies:
1. **SageMaker Inference Recommender** — benchmarks instance types for your model
2. **Multi-model endpoints** — load 50+ strategy models on one endpoint
3. **Compiled models** — SageMaker Neo compiles to target hardware (10-25% speedup)
4. **Inference pipelines** — chain preprocessing + model in single endpoint call

```python
# Multi-model endpoint (serve 50 strategy models on 1 endpoint)
from sagemaker.multidatamodel import MultiDataModel

mme = MultiDataModel(
    name="trading-strategies-mme",
    model_data_prefix="s3://models/strategies/",
    model=base_model,
    sagemaker_session=session,
)
predictor = mme.deploy(initial_instance_count=2, instance_type="ml.g4dn.xlarge")

# Invoke specific strategy model
result = predictor.predict(data=payload, target_model="rsi-v1.tar.gz")
```

For sub-100ms: use `ml.g4dn.xlarge` (GPU inference), enable response streaming, pre-warm endpoint with scheduled invocations.

### Q14: How do you handle ML model monitoring and drift detection on AWS?
**A:**

```python
from sagemaker.model_monitor import DefaultModelMonitor, CronExpressionGenerator

# 1. Create baseline from training data
monitor = DefaultModelMonitor(role=role, instance_type="ml.m5.xlarge")
monitor.suggest_baseline(
    baseline_dataset="s3://data/training/baseline.csv",
    dataset_format=DatasetFormat.csv(header=True),
)

# 2. Schedule monitoring (hourly)
monitor.create_monitoring_schedule(
    monitor_schedule_name="trading-model-monitor",
    endpoint_input=endpoint_name,
    schedule_cron_expression=CronExpressionGenerator.hourly(),
    statistics=monitor.baseline_statistics(),
    constraints=monitor.suggested_constraints(),
)

# 3. CloudWatch alarm on drift
# SageMaker publishes /aws/sagemaker/Endpoints/data-metrics
# Set alarm: feature_baseline_drift_* > threshold → SNS → retrain trigger
```

**Types of drift:**
- **Data drift** — feature distributions shift (e.g., volatility regime change)
- **Concept drift** — relationship between features and target changes
- **Prediction drift** — output distribution changes without input changes

### Q15: Compare AWS AI/ML services for a GenAI Delivery Lead's technology selection.
**A:**

| Decision | Choose This | When |
|----------|-------------|------|
| **Pre-built GenAI** | Bedrock | Need Claude/Llama/Titan, zero ML ops |
| **Custom training** | SageMaker | Need full control, custom architectures |
| **Quick prototyping** | SageMaker Canvas | Business users, no-code ML |
| **RAG pipeline** | Bedrock Knowledge Bases | Document Q&A, managed vector store |
| **Agent framework** | Bedrock Agents | Multi-step tool-using workflows |
| **Batch inference** | SageMaker Batch Transform | Nightly signal generation for 500 stocks |
| **Real-time** | SageMaker Endpoints | Sub-100ms trading signal inference |
| **MLOps pipeline** | SageMaker Pipelines | CI/CD for ML, automated retraining |
| **Model governance** | SageMaker Model Registry | Approval workflows, lineage tracking |

**Cost optimization matrix:**
- Dev/test: Spot instances (70% savings) + serverless inference
- Production: Reserved capacity + auto-scaling + multi-model endpoints
- Batch: Managed Spot Training + S3 Express One Zone for data
