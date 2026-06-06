# Airflow Orchestration

DAG orchestration simulator — 5 DAGs, custom operators/callbacks, runs without Airflow. FastAPI API + Streamlit dashboard.

## What It Does

- **DAG Simulation**: Execute Airflow-style DAG pipelines without a real Airflow cluster
- **5 Production DAGs**: ETL pipeline, dynamic DAG, sensor pipeline, data quality, multi-source ETL
- **Custom Operators**: Validation operator with configurable rules
- **Custom Callbacks**: Success/failure/retry/SLA-miss callback handlers
- **REST API**: FastAPI endpoints for DAG listing, execution, status, task logs
- **Dashboard**: Streamlit UI for DAG monitoring and execution

## Architecture

```
dags/
  dag_01_etl_pipeline.py      # Standard ETL (extract → transform → load)
  dag_02_dynamic_dag.py       # Dynamically generated tasks
  dag_03_sensor_pipeline.py   # Sensor-triggered pipeline
  dag_04_data_quality.py      # DQ validation pipeline
  dag_05_multi_source_etl.py  # Multi-source ingestion
plugins/
  operators/validation_operator.py  # Custom validation operator
  callbacks.py                      # DAG lifecycle callbacks
src/simulator.py              # DAG execution engine
src/api.py                    # FastAPI REST API
src/ui.py                     # Streamlit dashboard
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py simulate    # Run DAG simulation
python main.py api         # API on :8007
python main.py ui          # Dashboard on :8501
python main.py all         # Both API + UI
```

## Testing

```bash
pytest                     # 139 tests
```

## Docker

```bash
docker compose up --build
```

See [RUNNING.md](RUNNING.md) for full build, test, and deployment instructions.
