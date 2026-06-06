# MLOps / LLMOps Engineer on GCP — 4-Week Track

## Overview
- Duration: 28 days
- Goal: Ship governed ML/LLM workloads with pipelines, monitoring, and safe rollout.
- Stack: Vertex AI (AutoML, custom, endpoints, batch), BigQueryML, Pipelines, Feature Store, Model Registry, Monitoring, Cloud Run for services, RAG/LLMs (OpenAI/Vertex), Logging/Monitoring.
- Prerequisites: Python, ML basics, basic SQL.

## Week 1 — Data & Modeling Foundations
- Day 1: Vertex setup; IAM/service accounts; enable APIs; regions.
- Day 2: Data prep in BQ; leakage checks; partitions/clusters; train/val/test splits.
- Day 3: AutoML (Vision/NLP/Tables): train/eval; per-class metrics; thresholding.
- Day 4: BigQueryML quick wins: CREATE MODEL, EVALUATE, PREDICT; explainability.
- Day 5: Model cards, lineage, versioning conventions.
- Day 6: Batch vs online predictions; cost/latency trade-offs.
- Day 7: Mini-project: AutoML model + BQML baseline; compare metrics.
- Milestone: Clean data, baseline + AutoML models evaluated with documented metrics.

## Week 2 — Pipelines & Deployment
- Day 8: Vertex Pipelines basics; components; caching; parameters.
- Day 9: CI/CD for models: build → train → evaluate → compare-to-baseline → register.
- Day 10: Endpoints: deploy, traffic split, rollback; autoscaling; latency SLOs.
- Day 11: Batch predictions to BQ/GCS; scheduling with Cloud Scheduler/Workflows.
- Day 12: Feature consistency: Feature Store basics; online/offline parity.
- Day 13: Model Registry: versions, approvals, promotion flow.
- Day 14: Mini-project: pipeline that trains + evaluates + registers + deploys canary.
- Milestone: Automated train/eval/register/deploy pipeline with rollback.

## Week 3 — Monitoring, Safety, Governance
- Day 15: Monitoring: drift, skew, data quality checks; log-based metrics; alerts.
- Day 16: A/B tests and champion/challenger; canary rollout for endpoints.
- Day 17: Security: IAM least privilege; CMEK; VPC-SC considerations; PII handling.
- Day 18: Compliance: audit logs, retention, approvals; model risk notes.
- Day 19: Cost optimization: right-size training; schedule batches; delete stale assets.
- Day 20: Runbooks: incident response for bad models; rollback scripts.
- Day 21: Mini-project: monitored endpoint with drift alert + rollback drill.
- Milestone: Monitored, governed deployment with rollback and cost controls.

## Week 4 — LLMOps & RAG
- Day 22: LLM APIs (Vertex PaLM/GPT) vs hosted OSS (on Run/GKE); choose path.
- Day 23: RAG basics: embeddings, vector store, chunking, retrieval; eval.
- Day 24: Safety/guardrails: moderation, prompt filters, PII scrubbing, rate limits.
- Day 25: Latency/cost tuning: caching, batching, grounding vs generation; token budgets.
- Day 26: Evaluation: answer quality, factuality, toxicity; eval sets; harness.
- Day 27: Deploy RAG service on Cloud Run with tracing and logging.
- Day 28: Capstone build + review.
- Milestone: Production RAG/LLM service with monitoring, safety, and cost guardrails.

## Capstone (Week 4)
**Churn Prediction + RAG Assistant**  
- Pipeline: Vertex Pipelines trains BQML + AutoML baseline; registers; deploys endpoint.  
- Serving: Endpoint with traffic split; canary + rollback; batch predictions to BQ.  
- RAG: Cloud Run service using embeddings + vector DB (e.g., pgvector/Vertex Match).  
- Monitoring: Drift/skew alerts; log-based metrics; latency/error SLOs; model cards.  
- Governance: IAM, CMEK where available, audit logs, approval workflow, artifact cleanup.  
- Acceptance: Meets SLOs; rollback tested; eval set shows improved quality; safety filters on.

## Links to Core Docs
- Vertex: `GCP/Vertex-AI/guide.md`, `.../roadmap.md`
- AutoML: `GCP/AutoML/guide.md`, `.../roadmap.md`
- BQML: `GCP/BigQueryML/guide.md`, `.../roadmap.md`
- Pipelines: `GCP/Vertex-AI/guide.md` (pipeline section)
- Monitoring: `GCP/CloudMonitoring/guide.md`, `GCP/CloudLogging/guide.md`
- RAG/LLMs: `LLMs/guide.md`, `Gen-AI/RAG/guide.md`, `Gen-AI/LangChain/guide.md`

