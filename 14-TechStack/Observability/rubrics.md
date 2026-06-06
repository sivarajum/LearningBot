# Learning Rubrics (Observable Skills)

Copy the template per technology/track and mark evidence.

## Template (per tech)
- Beginner:
  - [ ] Can explain purpose and core concepts.
  - [ ] Can run a hello-world/sample.
  - [ ] Can read logs/errors and fix basic issues.
- Intermediate:
  - [ ] Can deploy to an environment with config/secrets handled.
  - [ ] Can add observability (logs/metrics) and basic alerts.
  - [ ] Can optimize cost/latency for a common workload.
- Advanced:
  - [ ] Can design for reliability (rollout/rollback, retries, idempotency).
  - [ ] Can secure access (IAM/least privilege) and handle compliance needs.
  - [ ] Can document/run runbooks; handle on-call scenarios.

## Track Examples
- **Data Engineer GCP**: ingest (GCS/BQ), Dataflow streaming/batch, dbt tests, Airflow orchestration, lag/freshness SLOs, replay playbooks.
- **Backend GCP**: Cloud Build CI/CD, Cloud Run canary/rollback, Cloud SQL private IP, LB + SSL, log-based metrics + burn alerts.
- **MLOps**: Vertex Pipelines, canary endpoints, drift monitoring, model registry/versioning, RAG with safety filters.
- **DevOps Full**: Docker slim/sign, K8s deploy with HPA/ingress/TLS, Terraform with policy checks, GitOps, admission controls.
- **Data Engineering Stack**: Spark batch/streaming, Kafka offsets/replay, Airflow DAGs with retries, dbt incremental with tests, dq SLOs.

