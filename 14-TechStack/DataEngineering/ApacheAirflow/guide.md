# Apache Airflow Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
pip install "apache-airflow==2.9.*" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.0/constraints-3.10.txt"
airflow db init
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
airflow webserver --port 8080
airflow scheduler
```

### 2. First DAG
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data_team",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG("my_first_dag", default_args=default_args, schedule_interval=timedelta(days=1), catchup=False) as dag:
    def extract():
        return "data"
    extract_task = PythonOperator(task_id="extract", python_callable=extract)
```

### 3. Core Concepts
- DAG, Task, Operator, XCom, Scheduler, Executor
- Executors: Local, Celery, Kubernetes
- Connections/Variables; Pools; SLAs; backfill

## Level 2 – Production Patterns

### DAG Design
- Idempotent tasks; retries with jitter; timeouts
- Task groups; sensors deferrable where possible
- Avoid dynamic task explosion; parameterize via variables

### Data & Dependencies
- Use datasets and data-aware scheduling where suitable
- Service accounts/least privilege for external systems
- Push results via XCom only when small; store data externally

### Ops & CI/CD
- DAG linting/tests; unit test operators; dagbag import checks
- Deploy via git-sync or artifact; versioned DAGs

## Level 3 – Architect Playbook

### Scaling & HA
- Celery/K8s executor; autoscale workers
- Database: managed Postgres/MySQL; tuned connections
- Separate logging to object storage

### Reliability & Observability
- SLAs with alerts; on-failure callbacks
- Metrics to Prometheus; logs to centralized store
- Airflow UI RBAC; audit; secrets backend (Vault/SM/KMS)

### Cost & Governance
- Limit parallelism/concurrency; pools for shared resources
- Tagging/ownership metadata; doc_md for tasks

## Ops Cheat Sheet

| Task | Command | Note |
| --- | --- | --- |
| Webserver | `airflow webserver` | UI |
| Scheduler | `airflow scheduler` | run DAGs |
| List DAGs | `airflow dags list` | inventory |
| Trigger | `airflow dags trigger <dag>` | manual |
| Test task | `airflow tasks test <dag> <task> <ds>` | dry run |

## Architecture Patterns

```mermaid
flowchart LR
  Git[Git DAGs] --> Deploy[Deploy (sync/artifact)]
  Deploy --> Web[Webserver/UI]
  Deploy --> Scheduler[Scheduler]
  Scheduler --> Exec[Executors (Celery/K8s)]
  Exec --> Logs[Central Logs]
  Exec --> Metrics[Prom/Alerting]
  Exec --> Data[External Systems]
```

## Checklist Before Production
- [ ] Using Celery/K8s executor for scale; DB tuned, logs externalized
- [ ] DAGs linted/tested; import times acceptable
- [ ] Secrets via backend; RBAC enabled; audit on
- [ ] SLAs/alerts defined; retries/timeouts set; pools configured
- [ ] Resource limits and parallelism tuned; ownership documented

## Learning Path Links
- Tracks: `LearningTracks/Data-Engineer-GCP/track.md`, `LearningTracks/Data-Engineering/track.md`
- Projects: `Projects/GCP-DataEngineer/` and `Projects/Data-Engineering/`
- Mastery: `Mastery/Airflow/` (quiz, scenarios, flashcards)

