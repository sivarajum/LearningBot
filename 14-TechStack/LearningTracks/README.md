# Learning Tracks Overview

## Tracks
- **Data Engineer on GCP** — 3 weeks — GCS → BQ → Dataflow → Pub/Sub → Airflow/dbt → Monitoring
- **Backend Engineer on GCP** — 3 weeks — Cloud Build → Cloud Run → Cloud SQL/Spanner → IAM/VPC → LB → Observability
- **MLOps/LLMOps Engineer** — 4 weeks — Vertex/AutoML/BQML → Pipelines → Registry → Monitoring → RAG/LLMs
- **Full DevOps Stack** — 4 weeks — Docker → Kubernetes → Terraform → CI/CD (GHA/Jenkins) → Monitoring/Security
- **Data Engineering Stack** — 4 weeks — Spark → Kafka → Airflow → dbt → Data Quality → Observability

## How to Choose
- New to cloud + data: start **Data Engineer on GCP**.
- Backend services on GCP: pick **Backend Engineer on GCP**.
- Shipping ML/LLM to prod: pick **MLOps/LLMOps Engineer**.
- Platform/infra focus: pick **Full DevOps Stack**.
- Broad data engineering (non-cloud-specific): pick **Data Engineering Stack**.

## Prerequisite Dependency Graph
```mermaid
flowchart LR
  Python[Python Basics] --> PyAdv[Python + Packaging/Testing]
  SQL[SQL Fundamentals] --> BQ[BigQuery]
  Git[Git & CI Basics] --> CI[CI/CD]

  PyAdv --> Spark
  PyAdv --> Airflow
  SQL --> dbt
  BQ --> Dataflow
  Git --> Docker
  Docker --> K8s[Kubernetes]
  K8s --> DevOpsTrack[DevOps-Full Track]
  BQ --> DataEngGCP[Data-Engineer-GCP Track]
  Dataflow --> DataEngGCP
  Airflow --> DataEngTrack[Data-Engineering Track]
  Spark --> DataEngTrack
  Kafka --> DataEngTrack
  Docker --> BackendGCP[Backend-GCP Track]
  CI --> BackendGCP
  CloudRun --> BackendGCP
  VertexAI --> MLOpsTrack[MLOps-GCP Track]
  BQ --> MLOpsTrack
```

## What’s Inside Each Track
- Prerequisites, duration, day-by-day tasks
- Milestones per week
- Capstone project description
- Links to relevant guides/roadmaps

## Next Steps
1) Pick a track above.
2) Follow the track’s daily plan in its `track.md`.
3) Do the linked projects (starter → intermediate → capstone) as they land in `Projects/`.
4) Validate with mastery checkpoints (quizzes, scenarios, flashcards) once available.

