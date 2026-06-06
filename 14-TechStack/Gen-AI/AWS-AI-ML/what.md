# AWS AI/ML Services: Complete Guide

## 1. What is AWS AI/ML?

AWS provides a comprehensive suite of AI/ML services spanning from pre-trained APIs (no ML knowledge needed) to fully managed ML platforms (SageMaker) to foundation model access (Bedrock).

**Service Tiers:**
| Tier | Services | ML Knowledge |
|------|----------|-------------|
| AI Services (pre-built) | Comprehend, Rekognition, Textract, Polly, Lex | None |
| ML Platform | SageMaker (train, deploy, monitor) | Intermediate |
| Foundation Models | Bedrock (Claude, Llama, Titan) | Basic-Intermediate |
| Infrastructure | EC2 GPU, Inferentia, Trainium | Advanced |

---

## 2. Amazon SageMaker

### SageMaker Studio Notebooks
```python
# SageMaker notebook — pre-configured with ML libraries
import sagemaker
from sagemaker import get_execution_role

role = get_execution_role()
session = sagemaker.Session()
bucket = session.default_bucket()
```

### Training a Model
```python
from sagemaker.estimator import Estimator

estimator = Estimator(
    image_uri=sagemaker.image_uris.retrieve("xgboost", region, version="1.7-1"),
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    output_path=f"s3://{bucket}/output",
    hyperparameters={
        "max_depth": 5,
        "eta": 0.2,
        "objective": "binary:logistic",
        "num_round": 100,
    },
)

estimator.fit({"train": f"s3://{bucket}/train.csv", "validation": f"s3://{bucket}/val.csv"})
```

### Deploy as Endpoint
```python
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    serializer=sagemaker.serializers.CSVSerializer(),
    deserializer=sagemaker.deserializers.JSONDeserializer(),
)

result = predictor.predict("0.5,1.2,3.4,0.8")  # Feature values

# Cleanup
predictor.delete_endpoint()
```

### SageMaker Pipelines (MLOps)
```python
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import TrainingStep, ProcessingStep

# Define steps
process_step = ProcessingStep(
    name="PreprocessData",
    processor=sklearn_processor,
    inputs=[...],
    outputs=[...],
)

train_step = TrainingStep(
    name="TrainModel",
    estimator=estimator,
    inputs={"train": process_step.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri},
)

pipeline = Pipeline(name="stock-predictor-pipeline", steps=[process_step, train_step])
pipeline.upsert(role_arn=role)
pipeline.start()
```

---

## 3. Amazon Bedrock (Foundation Models)

### Access Foundation Models
```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Claude via Bedrock
response = bedrock.invoke_model(
    modelId="anthropic.claude-sonnet-4-20250514-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Analyze NIFTY50 outlook"}],
    }),
)
result = json.loads(response["body"].read())
print(result["content"][0]["text"])
```

### Bedrock Knowledge Bases (RAG)
```python
bedrock_agent = boto3.client("bedrock-agent-runtime")

response = bedrock_agent.retrieve_and_generate(
    input={"text": "What is our company's revenue policy?"},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": "KB12345",
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-20250514-v1:0",
        },
    },
)
```

### Bedrock Guardrails
```python
# Apply content filtering
response = bedrock.invoke_model(
    modelId="anthropic.claude-sonnet-4-20250514-v1:0",
    guardrailIdentifier="my-guardrail-id",
    guardrailVersion="1",
    body=json.dumps({...}),
)
```

---

## 4. AI Services (Pre-Built)

### Amazon Comprehend (NLP)
```python
comprehend = boto3.client("comprehend")

# Sentiment analysis
result = comprehend.detect_sentiment(
    Text="RELIANCE profit surges 30% on strong Jio growth",
    LanguageCode="en",
)
# {"Sentiment": "POSITIVE", "SentimentScore": {"Positive": 0.95, ...}}

# Entity recognition
entities = comprehend.detect_entities(Text="SEBI fined RELIANCE ₹25 crore", LanguageCode="en")
# Entities: [{"Text": "SEBI", "Type": "ORGANIZATION"}, {"Text": "₹25 crore", "Type": "QUANTITY"}]

# Key phrases
phrases = comprehend.detect_key_phrases(Text="Q3 revenue grew 15% YoY", LanguageCode="en")
```

### Amazon Rekognition (Vision)
```python
rekognition = boto3.client("rekognition")

# Detect text in chart images
response = rekognition.detect_text(
    Image={"S3Object": {"Bucket": "my-bucket", "Name": "chart.png"}}
)
for text in response["TextDetections"]:
    print(f"{text['DetectedText']} (confidence: {text['Confidence']:.1f}%)")
```

### Amazon Textract (Document Processing)
```python
textract = boto3.client("textract")

# Extract tables from financial reports
response = textract.analyze_document(
    Document={"S3Object": {"Bucket": "reports", "Name": "annual_report.pdf"}},
    FeatureTypes=["TABLES", "FORMS"],
)
# Returns structured table data from PDF
```

### Amazon Lex (Chatbots)
```python
lex = boto3.client("lexv2-runtime")

response = lex.recognize_text(
    botId="BOTID",
    botAliasId="ALIASID",
    localeId="en_US",
    sessionId="user123",
    text="Show my portfolio performance",
)
```

---

## 5. Installation & Setup

```bash
pip install boto3 sagemaker

# Configure AWS credentials
aws configure
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: ...
# Default region: us-east-1
# Default output format: json

# Verify
python -c "import boto3; print(boto3.client('sts').get_caller_identity()['Account'])"
```

---

## 6. Best Practices

1. **Start with AI Services** — Use Comprehend/Textract before building custom models
2. **Use SageMaker for custom** — When pre-built APIs don't meet accuracy needs
3. **Bedrock for GenAI** — Access multiple FMs without managing infrastructure
4. **Spot instances** — 70% savings on SageMaker training
5. **Model monitoring** — SageMaker Model Monitor for data/concept drift
6. **VPC endpoints** — Keep ML traffic private (no internet traversal)
7. **Auto-scaling** — SageMaker endpoints scale to zero when idle

---

## 7. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Leaving endpoints running ($$) | Set auto-scaling to zero min, delete test endpoints |
| Wrong instance type | Start small (ml.m5.large), scale up based on metrics |
| No model versioning | Use SageMaker Model Registry |
| Ignoring data drift | SageMaker Model Monitor with scheduled checks |
| S3 data not in same region | Keep data and compute in same AWS region |
| Manual pipeline steps | Use SageMaker Pipelines for reproducible workflows |

---

## 8. AWS vs GCP vs Azure ML

| Feature | AWS SageMaker | GCP Vertex AI | Azure ML |
|---------|--------------|---------------|----------|
| Notebook IDE | SageMaker Studio | Workbench | ML Studio |
| AutoML | Autopilot | AutoML | AutoML |
| Foundation Models | Bedrock (Claude, Llama, Titan) | Model Garden (Gemini, Claude) | Azure OpenAI (GPT-4) |
| MLOps Pipeline | SageMaker Pipelines | Vertex Pipelines | ML Pipeline |
| Model Monitoring | Model Monitor | Model Monitoring | Model Monitor |
| Edge Deployment | SageMaker Neo | Edge Manager | IoT Edge |
| Pricing | Pay-per-use | Pay-per-use | Pay-per-use |

---

## 9. Amazon Bedrock Deep Dive

Bedrock provides serverless access to foundation models without managing infrastructure.

### Basic Bedrock Usage
```python
import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Claude via Bedrock
response = client.invoke_model(
    modelId="anthropic.claude-sonnet-4-20250514",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Analyze RELIANCE quarterly earnings"}],
    }),
)
result = json.loads(response["body"].read())
print(result["content"][0]["text"])
```

### Bedrock Knowledge Bases (RAG)
```python
# Create knowledge base backed by S3 + OpenSearch
kb_client = boto3.client("bedrock-agent-runtime")

response = kb_client.retrieve_and_generate(
    input={"text": "What is SEBI's latest circular on margin requirements?"},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": "KB_ID",
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-20250514",
        },
    },
)
```

### Bedrock Guardrails
```python
# Content filtering, PII detection, denied topics
response = client.invoke_model(
    modelId="anthropic.claude-sonnet-4-20250514",
    guardrailIdentifier="my-guardrail-id",
    guardrailVersion="1",
    body=json.dumps({...}),
)
```

---

## 10. SageMaker Pipelines (MLOps)

```python
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep

# Define steps
preprocess_step = ProcessingStep(name="PreprocessData", ...)
train_step = TrainingStep(name="TrainModel", estimator=estimator, ...)
eval_step = ProcessingStep(name="EvaluateModel", ...)
register_step = RegisterModel(name="RegisterModel", ...)

# Build pipeline
pipeline = Pipeline(
    name="nse-trading-signal-pipeline",
    steps=[preprocess_step, train_step, eval_step, register_step],
    parameters=[instance_type, model_approval_status],
)

pipeline.upsert(role_arn=role)
execution = pipeline.start()
```

### A/B Testing with SageMaker
```python
from sagemaker.model import Model

# Deploy two variants
endpoint_config = sagemaker.session.production_variant(
    model_name="model-v1", instance_type="ml.m5.large", initial_weight=90
)
shadow_variant = sagemaker.session.production_variant(
    model_name="model-v2", instance_type="ml.m5.large", initial_weight=10
)
# Traffic split: 90% v1, 10% v2 — measure metrics before full rollout
```

---

## 11. Cost Optimization

| Strategy | Savings | Description |
|----------|---------|-------------|
| Spot instances | Up to 90% | For training jobs (checkpointing required) |
| Managed Spot Training | 60-90% | SageMaker handles interruptions |
| Serverless Inference | Variable | Pay per inference (cold starts ~5s) |
| Auto-scaling to 0 | 100% when idle | Scale-down during off-market hours |
| Savings Plans | Up to 64% | 1-3 year commitment for SageMaker |
| Inf2 instances | 40% vs GPU | AWS Inferentia chips for inference |

### Managed Spot Training
```python
estimator = Estimator(
    image_uri=image,
    role=role,
    instance_count=1,
    instance_type="ml.p3.2xlarge",
    use_spot_instances=True,                # Enable spot
    max_wait=7200,                          # Max wait time
    max_run=3600,                           # Max training time
    checkpoint_s3_uri=f"s3://{bucket}/checkpoints",  # Resume on interruption
)
```

---

## 12. Real-World Architecture: Financial ML on AWS

```
┌──────────────────────────────────────────────────────────┐
│  Data Ingestion                                          │
│  EventBridge → Lambda → S3 (market data, filings)       │
├──────────────────────────────────────────────────────────┤
│  Feature Engineering                                     │
│  SageMaker Processing → Feature Store (online/offline)   │
├──────────────────────────────────────────────────────────┤
│  Model Training                                          │
│  SageMaker Training (Spot) → Model Registry              │
├──────────────────────────────────────────────────────────┤
│  Inference                                               │
│  SageMaker Endpoint (real-time) / Bedrock (LLM analysis) │
├──────────────────────────────────────────────────────────┤
│  Monitoring                                              │
│  Model Monitor → CloudWatch → SNS Alerts                 │
└──────────────────────────────────────────────────────────┘
```
