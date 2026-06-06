"""
Gen-AI Tool: AWS AI/ML (SageMaker + Bedrock)
==============================================
Demonstrates: SageMaker endpoint deployment, Bedrock LLM API,
S3 model artifact storage, SageMaker training jobs, and
AWS AI services (Comprehend, Textract) integration.

Role in GenAI Nexus: Production cloud deployment — serve the startup
advisor model on SageMaker, use Bedrock for fallback LLM calls.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class SageMakerConfig:
    """SageMaker deployment configuration."""

    endpoint_name: str = "startup-advisor-endpoint"
    instance_type: str = "ml.g4dn.xlarge"   # T4 GPU, cheapest with GPU
    instance_count: int = 1
    model_data_s3: str = ""                  # s3://bucket/model.tar.gz
    container_image: str = ""               # ECR image URI
    role_arn: str = ""                       # SageMaker execution role
    region: str = "us-east-1"


@dataclass
class BedrockConfig:
    """Bedrock model configuration."""

    model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    region: str = "us-east-1"
    max_tokens: int = 1024
    temperature: float = 0.3


@dataclass
class EndpointStatus:
    """SageMaker endpoint status."""

    name: str
    status: str  # InService | Creating | Failed | Deleting
    instance_type: str
    creation_time: str = ""
    url: str = ""


@dataclass
class BedrockResponse:
    """Response from Bedrock API."""

    text: str
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0


# Demo endpoint config
DEMO_ENDPOINT = EndpointStatus(
    name="startup-advisor-endpoint",
    status="InService",
    instance_type="ml.g4dn.xlarge",
    creation_time="2026-03-01T09:00:00Z",
    url="https://runtime.sagemaker.us-east-1.amazonaws.com/endpoints/startup-advisor-endpoint/invocations",
)


class AWSClient:
    """
    AWS AI/ML services integration.

    Demonstrates:
    - SageMaker: Deploy model as real-time endpoint
    - SageMaker: Create training job
    - Bedrock: Call Claude/Titan/Llama via managed API
    - S3: Upload model artifacts
    - Comprehend: Entity detection + sentiment
    - Textract: Document text extraction
    """

    def __init__(
        self,
        aws_key: str = "",
        aws_secret: str = "",
        region: str = "us-east-1",
    ):
        self._demo = not (aws_key and aws_secret)
        self._region = region
        self._sagemaker = None
        self._bedrock = None
        self._s3 = None
        self._comprehend = None

        if not self._demo:
            try:
                import boto3

                session = boto3.Session(
                    aws_access_key_id=aws_key,
                    aws_secret_access_key=aws_secret,
                    region_name=region,
                )
                self._sagemaker = session.client("sagemaker")
                self._sagemaker_runtime = session.client("sagemaker-runtime")
                self._bedrock = session.client("bedrock-runtime")
                self._s3 = session.client("s3")
                self._comprehend = session.client("comprehend")
            except ImportError:
                self._demo = True

    # ─────────────────────────────────────────
    # SAGEMAKER
    # ─────────────────────────────────────────

    def deploy_endpoint(
        self, config: SageMakerConfig | None = None
    ) -> EndpointStatus:
        """
        Deploy model as SageMaker real-time endpoint.
        Uploads model to S3, creates model object, deploys endpoint.
        """
        cfg = config or SageMakerConfig()

        if self._demo:
            print(f"[Demo] Would deploy to SageMaker:")
            print(f"  Endpoint: {cfg.endpoint_name}")
            print(f"  Instance: {cfg.instance_type} × {cfg.instance_count}")
            print(f"  Model: {cfg.model_data_s3 or 's3://bucket/model.tar.gz'}")
            print(f"  Estimated cost: ${self._estimate_endpoint_cost(cfg)}/month")
            return DEMO_ENDPOINT

        try:
            # Create model
            self._sagemaker.create_model(
                ModelName=cfg.endpoint_name,
                PrimaryContainer={
                    "Image": cfg.container_image,
                    "ModelDataUrl": cfg.model_data_s3,
                },
                ExecutionRoleArn=cfg.role_arn,
            )

            # Create endpoint config
            self._sagemaker.create_endpoint_config(
                EndpointConfigName=f"{cfg.endpoint_name}-config",
                ProductionVariants=[
                    {
                        "VariantName": "primary",
                        "ModelName": cfg.endpoint_name,
                        "InstanceType": cfg.instance_type,
                        "InitialInstanceCount": cfg.instance_count,
                    }
                ],
            )

            # Deploy endpoint
            self._sagemaker.create_endpoint(
                EndpointName=cfg.endpoint_name,
                EndpointConfigName=f"{cfg.endpoint_name}-config",
            )

            return EndpointStatus(
                name=cfg.endpoint_name,
                status="Creating",
                instance_type=cfg.instance_type,
            )

        except Exception as e:
            print(f"[Error] Endpoint deployment failed: {e}")
            return DEMO_ENDPOINT

    def invoke_endpoint(self, endpoint_name: str, payload: dict) -> dict:
        """Send inference request to deployed SageMaker endpoint."""
        if self._demo:
            query = payload.get("inputs", "startup advice query")
            return {
                "generated_text": (
                    f"[SageMaker Demo] Advice for: {str(query)[:80]}... "
                    "Focus on mid-market legal tech, SOC2 compliance, and PLG growth."
                ),
                "endpoint": endpoint_name,
            }

        try:
            response = self._sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType="application/json",
                Body=json.dumps(payload),
            )
            result = json.loads(response["Body"].read())
            return result
        except Exception as e:
            return {"error": str(e)}

    def create_training_job(
        self, job_name: str, training_data_s3: str, output_s3: str, role_arn: str
    ) -> str:
        """Create a SageMaker training job."""
        if self._demo:
            print(f"[Demo] Would create training job: {job_name}")
            print(f"  Data: {training_data_s3}")
            print(f"  Output: {output_s3}")
            return f"training-job-{job_name}-demo"

        try:
            self._sagemaker.create_training_job(
                TrainingJobName=job_name,
                AlgorithmSpecification={
                    "TrainingImage": "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-training:2.1.0-transformers4.37.0-gpu-py310-cu121-ubuntu20.04",
                    "TrainingInputMode": "File",
                },
                RoleArn=role_arn,
                InputDataConfig=[
                    {
                        "ChannelName": "training",
                        "DataSource": {
                            "S3DataSource": {
                                "S3DataType": "S3Prefix",
                                "S3Uri": training_data_s3,
                            }
                        },
                    }
                ],
                OutputDataConfig={"S3OutputPath": output_s3},
                ResourceConfig={
                    "InstanceType": "ml.p4d.24xlarge",
                    "InstanceCount": 1,
                    "VolumeSizeInGB": 100,
                },
                StoppingCondition={"MaxRuntimeInSeconds": 86400},
            )
            return job_name
        except Exception as e:
            return f"Error: {e}"

    # ─────────────────────────────────────────
    # BEDROCK
    # ─────────────────────────────────────────

    def bedrock_invoke(
        self, prompt: str, config: BedrockConfig | None = None
    ) -> BedrockResponse:
        """
        Invoke Claude via Amazon Bedrock.
        Bedrock = managed LLM API (alternative to calling Anthropic directly).
        """
        cfg = config or BedrockConfig()

        if self._demo:
            return BedrockResponse(
                text=f"[Bedrock Claude Demo] For your startup query: '{prompt[:60]}...'"
                     " Focus on mid-market legal tech opportunity with PLG strategy.",
                model_id=cfg.model_id,
                input_tokens=len(prompt.split()),
                output_tokens=40,
            )

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": cfg.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": cfg.temperature,
            })

            response = self._bedrock.invoke_model(
                modelId=cfg.model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )

            result = json.loads(response["body"].read())
            return BedrockResponse(
                text=result["content"][0]["text"],
                model_id=cfg.model_id,
                input_tokens=result.get("usage", {}).get("input_tokens", 0),
                output_tokens=result.get("usage", {}).get("output_tokens", 0),
            )
        except Exception as e:
            return BedrockResponse(text=f"Error: {e}", model_id=cfg.model_id)

    # ─────────────────────────────────────────
    # AI SERVICES
    # ─────────────────────────────────────────

    def analyze_sentiment_comprehend(self, texts: list[str]) -> list[dict]:
        """AWS Comprehend: Managed sentiment analysis (no model needed)."""
        if self._demo:
            sentiments = ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"]
            return [
                {
                    "text": t[:60],
                    "sentiment": sentiments[i % 4],
                    "confidence": 0.85 + i * 0.01,
                }
                for i, t in enumerate(texts)
            ]

        results = []
        for text in texts:
            try:
                response = self._comprehend.detect_sentiment(
                    Text=text[:5000], LanguageCode="en"
                )
                results.append({
                    "text": text[:60],
                    "sentiment": response["Sentiment"],
                    "confidence": response["SentimentScore"].get(response["Sentiment"].title(), 0),
                })
            except Exception as e:
                results.append({"text": text[:60], "error": str(e)})
        return results

    def extract_text_textract(self, document_path: str) -> str:
        """AWS Textract: Extract text from PDF/image without OCR setup."""
        if self._demo:
            return (
                f"[Textract Demo] Extracted from {document_path}:\n"
                "CONTRACT AGREEMENT\n"
                "This Agreement is entered into as of January 1, 2026...\n"
                "Section 1: DEFINITIONS\n"
                "Section 2: TERM AND TERMINATION\n"
                "Section 3: LIMITATION OF LIABILITY\n"
                "Section 7: INDEMNIFICATION — [Red flag: unlimited indemnification]"
            )

        try:
            with open(document_path, "rb") as f:
                doc_bytes = f.read()

            from boto3 import client as boto_client

            textract = boto_client("textract", region_name=self._region)
            response = textract.detect_document_text(
                Document={"Bytes": doc_bytes}
            )
            lines = [
                block["Text"]
                for block in response.get("Blocks", [])
                if block["BlockType"] == "LINE"
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"Textract error: {e}"

    def upload_model_to_s3(self, local_path: str, bucket: str, key: str) -> str:
        """Upload model artifacts to S3 for SageMaker."""
        if self._demo:
            s3_uri = f"s3://{bucket}/{key}"
            print(f"[Demo] Would upload {local_path} → {s3_uri}")
            return s3_uri

        try:
            self._s3.upload_file(local_path, bucket, key)
            return f"s3://{bucket}/{key}"
        except Exception as e:
            return f"Error: {e}"

    def _estimate_endpoint_cost(self, config: SageMakerConfig) -> float:
        """Estimate monthly SageMaker endpoint cost in USD."""
        # Approximate hourly costs for common instance types
        hourly_costs = {
            "ml.t3.medium": 0.052,
            "ml.c5.xlarge": 0.228,
            "ml.g4dn.xlarge": 0.736,
            "ml.g4dn.4xlarge": 1.686,
            "ml.p3.2xlarge": 3.825,
            "ml.p4d.24xlarge": 32.77,
        }
        hourly = hourly_costs.get(config.instance_type, 1.0)
        return round(hourly * 24 * 30 * config.instance_count, 2)


def demo():
    print("=" * 60)
    print("DEMO: AWS AI/ML (SageMaker + Bedrock)")
    print("=" * 60)
    aws = AWSClient()  # demo mode

    print("\n[1] Deploy SageMaker Endpoint")
    config = SageMakerConfig(
        endpoint_name="startup-advisor-v1",
        instance_type="ml.g4dn.xlarge",
    )
    status = aws.deploy_endpoint(config)
    print(f"Status: {status.status}")
    print(f"Instance: {status.instance_type}")
    print(f"URL: {status.url}")

    print("\n[2] Invoke SageMaker Endpoint")
    result = aws.invoke_endpoint(
        "startup-advisor-v1",
        {"inputs": "What is the best pricing strategy for legal tech SaaS?"},
    )
    print(f"Response: {result.get('generated_text', '')[:200]}")

    print("\n[3] Bedrock Claude Invocation")
    response = aws.bedrock_invoke(
        "What are the top 3 risks for an AI legal startup?",
        BedrockConfig(model_id="anthropic.claude-3-haiku-20240307-v1:0"),
    )
    print(f"Model: {response.model_id}")
    print(f"Response: {response.text[:200]}")
    print(f"Tokens: {response.input_tokens} in / {response.output_tokens} out")

    print("\n[4] AWS Comprehend Sentiment")
    headlines = [
        "AI legal startup raises $50M to expand platform",
        "Attorney general sues AI company over data breach",
        "Legal tech market grows 19% in 2024",
    ]
    sentiments = aws.analyze_sentiment_comprehend(headlines)
    for s in sentiments:
        print(f"  [{s['sentiment']}:{s.get('confidence', 0):.2f}] {s['text']}")

    print("\n[5] Textract Document Extraction")
    text = aws.extract_text_textract("./data/sample_contract.pdf")
    print(text[:400])

    print("\n[6] Cost Estimation")
    for instance_type in ["ml.t3.medium", "ml.g4dn.xlarge", "ml.p4d.24xlarge"]:
        cfg = SageMakerConfig(instance_type=instance_type)
        cost = aws._estimate_endpoint_cost(cfg)
        print(f"  {instance_type}: ${cost:,.2f}/month")


if __name__ == "__main__":
    demo()
