# Apache Airflow Roadmap – 6 Weeks

## Weeks 1-2: Foundations (🟢)
- [ ] Day 1: Install; webserver/scheduler basics
- [ ] Day 2: DAG/Task/Operator; first DAG
- [ ] Day 3: Scheduling, catchup, backfill
- [ ] Day 4: XCom basics; Variables/Connections
- [ ] Day 5: Sensors; deferrable intro
- [ ] Day 6: Pools, priorities, concurrency
- [ ] Day 7: Task retries/timeouts; SLAs basics
- [ ] Day 8: CLI vs UI operations
- [ ] Day 9: Logging configuration; remote logs
- [ ] Day 10: Mini-project: simple ETL DAG
- [ ] Day 11-12: DAG import time tuning
- [ ] Day 13-14: Review + refactor

**Milestone**: Confident authoring/running simple DAGs with basic ops hygiene.

## Weeks 3-4: Intermediate (🟡)
- [ ] Day 15: Executors (Local vs Celery vs K8s)
- [ ] Day 16: TaskGroup, dynamic tasks (controlled)
- [ ] Day 17: Data-aware scheduling/datasets
- [ ] Day 18: Idempotency, backfill strategy, reruns
- [ ] Day 19: Secrets backend (Vault/SM/KMS)
- [ ] Day 20: Testing DAGs (pytest, dagbag import)
- [ ] Day 21: Linting/style; ownership/doc_md
- [ ] Day 22: SLAs + Alerting via Alertmanager/PagerDuty
- [ ] Day 23-24: Mini-project: multi-dag pipeline with datasets
- [ ] Day 25-27: Performance: scheduler/db tuning; log storage external
- [ ] Day 28: Deploy via git-sync or artifact

**Milestone**: Production patterns for scale, secrets, testing, alerting.

## Weeks 5-6: Advanced (🔴)
- [ ] Day 29: K8s/Celery executor HA; autoscaling workers
- [ ] Day 30: Concurrency controls; pools for shared systems
- [ ] Day 31: Robust retries with jitter; timeouts; circuit breakers
- [ ] Day 32: Observability: metrics to Prometheus, trace tasks
- [ ] Day 33: Governance: RBAC, audit, tagging/ownership
- [ ] Day 34: Cost controls; stop noisy DAGs; retention policies
- [ ] Day 35: Disaster recovery: DB backups, log retention
- [ ] Day 36: Blue/green for Airflow upgrades
- [ ] Day 37-38: Capstone: complex pipeline with datasets, HA executor, alerts
- [ ] Day 39-42: Documentation, runbooks, handover

**Milestone**: HA, observable Airflow with governance and cost controls.

## Resources
- Docs: https://airflow.apache.org/docs/
- Providers: https://airflow.apache.org/docs/apache-airflow-providers/
- Testing: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html

