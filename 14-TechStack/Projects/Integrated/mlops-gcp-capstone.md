# Capstone: Churn Prediction + RAG Assistant
- Pipelines: Vertex Pipelines trains BQML + AutoML; evaluate; register; deploy canary.
- Serving: Endpoint with traffic split; batch predictions to BQ; rollback path.
- RAG: Cloud Run service with embeddings + vector DB; safety filters; caching.
- Monitoring: drift/skew alerts; latency/error SLOs; model cards; approvals.
- Governance: IAM, CMEK where applicable, artifact cleanup, retention.
