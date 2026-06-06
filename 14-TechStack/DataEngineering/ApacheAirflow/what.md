# Apache Airflow for Data Engineering

## Overview

Apache Airflow is an open-source platform for programmatically authoring, scheduling, and monitoring workflows. It's designed to handle complex computational workflows and data processing pipelines, making it a cornerstone of modern data engineering.

## Core Concepts

### 1. Airflow Architecture

**Key Components:**
- **Web Server**: Flask-based UI for monitoring and triggering DAGs
- **Scheduler**: Heart of Airflow, schedules and executes tasks
- **Worker**: Executes individual tasks (can be local or distributed)
- **Metadata Database**: Stores DAG and task metadata (PostgreSQL/MySQL)
- **Executor**: Defines how tasks are executed (Sequential, Local, Celery, Kubernetes)

**Architecture Diagram:**
```
[Web UI] <-> [Scheduler] <-> [Metadata DB]
    ^              ^
    |              |
[Workers] <-- [Executor] --> [Task Queue]
```

### 2. DAGs (Directed Acyclic Graphs)

**DAG Definition:**
- **Directed**: Tasks have dependencies (upstream/downstream)
- **Acyclic**: No cycles allowed (prevents infinite loops)
- **Graph**: Visual representation of task dependencies

**Basic DAG Structure:**
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default arguments for all tasks
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

# Create DAG
dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'daily']
)

# Define tasks
extract_task = BashOperator(
    task_id='extract_data',
    bash_command='python /path/to/extract.py',
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_function,
    dag=dag
)

load_task = BashOperator(
    task_id='load_data',
    bash_command='python /path/to/load.py',
    dag=dag
)

# Set dependencies
extract_task >> transform_task >> load_task
```

### 3. Operators

**Types of Operators:**
- **Action Operators**: Execute actions (BashOperator, PythonOperator)
- **Transfer Operators**: Move data between systems
- **Sensor Operators**: Wait for conditions

**Common Operators:**
```python
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.email import EmailOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.filesystem import FileSensor

# Bash Operator
bash_task = BashOperator(
    task_id='run_script',
    bash_command='echo "Hello World" > /tmp/hello.txt',
    dag=dag
)

# Python Operator
def process_data(**context):
    import pandas as pd
    df = pd.read_csv('/data/input.csv')
    processed_df = df[df['status'] == 'active']
    processed_df.to_csv('/data/output.csv', index=False)
    return 'Data processed'

python_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag
)

# Dummy Operator (for organization)
start_task = DummyOperator(
    task_id='start',
    dag=dag
)

end_task = DummyOperator(
    task_id='end',
    dag=dag
)

# HTTP Operator
api_call = SimpleHttpOperator(
    task_id='call_api',
    http_conn_id='my_api',
    endpoint='api/v1/data',
    method='POST',
    data={"key": "value"},
    headers={"Content-Type": "application/json"},
    dag=dag
)

# Email Operator
send_email = EmailOperator(
    task_id='send_notification',
    to='team@company.com',
    subject='Pipeline Completed',
    html_content='<h3>ETL Pipeline finished successfully</h3>',
    dag=dag
)

# Sensor for file existence
wait_for_file = FileSensor(
    task_id='wait_for_input',
    filepath='/data/input.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,      # Timeout after 1 hour
    dag=dag
)

# Trigger another DAG
trigger_dag = TriggerDagRunOperator(
    task_id='trigger_downstream',
    trigger_dag_id='downstream_pipeline',
    dag=dag
)
```

## Task Dependencies and Flow Control

### 1. Setting Dependencies

**Bitshift Operators:**
```python
# Linear dependency
task1 >> task2 >> task3

# Parallel execution
task1 >> [task2, task3] >> task4

# Complex dependencies
task1 >> task2
task1 >> task3
[task2, task3] >> task4

# Cross-dependencies
start >> extract
extract >> [transform1, transform2]
transform1 >> load1
transform2 >> load2
[load1, load2] >> end
```

**Dependency Methods:**
```python
# set_upstream / set_downstream
task1.set_downstream(task2)
task3.set_upstream(task1)

# Chain method
from airflow.utils.helpers import chain
chain(task1, task2, task3, task4)

# Cross-dependencies with chain
chain(start, [extract1, extract2], transform, [load1, load2], end)
```

### 2. Branching and Conditional Logic

**BranchPythonOperator:**
```python
from airflow.operators.python import BranchPythonOperator

def decide_branch(**context):
    # Check if it's weekend
    execution_date = context['execution_date']
    if execution_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return 'weekend_processing'
    else:
        return 'weekday_processing'

branch_task = BranchPythonOperator(
    task_id='check_day_type',
    python_callable=decide_branch,
    provide_context=True,
    dag=dag
)

weekend_task = DummyOperator(task_id='weekend_processing', dag=dag)
weekday_task = DummyOperator(task_id='weekday_processing', dag=dag)
end_task = DummyOperator(task_id='end', dag=dag)

branch_task >> [weekend_task, weekday_task]
[weekend_task, weekday_task] >> end_task
```

**ShortCircuitOperator:**
```python
from airflow.operators.python import ShortCircuitOperator

def check_data_quality(**context):
    # Check if data meets quality standards
    import pandas as pd
    df = pd.read_csv('/data/input.csv')
    if len(df) < 1000:  # Skip if insufficient data
        print("Insufficient data, skipping pipeline")
        return False
    return True

quality_check = ShortCircuitOperator(
    task_id='data_quality_check',
    python_callable=check_data_quality,
    provide_context=True,
    dag=dag
)

process_task = DummyOperator(task_id='process_data', dag=dag)

quality_check >> process_task
```

## Configuration and Variables

### 1. Airflow Variables

**Using Variables:**
```python
from airflow.models import Variable

# Set variables (can be done via UI or CLI)
# airflow variables set my_var "my_value"

# Get variables in code
my_var = Variable.get("my_var")
db_host = Variable.get("database_host", default_var="localhost")

# JSON variables
config = Variable.get("pipeline_config", deserialize_json=True)
# {"batch_size": 1000, "timeout": 300}

# Variable in operators
bash_task = BashOperator(
    task_id='use_variable',
    bash_command=f'echo {Variable.get("my_message")}',
    dag=dag
)
```

### 2. Connections

**Database Connections:**
```python
from airflow import settings
from airflow.models import Connection

# Create connection programmatically
def create_postgres_connection():
    conn = Connection(
        conn_id='my_postgres',
        conn_type='postgres',
        host='localhost',
        schema='mydb',
        login='user',
        password='password',
        port=5432
    )
    session = settings.Session()
    session.add(conn)
    session.commit()

# Use connection in operators
from airflow.providers.postgres.operators.postgres import PostgresOperator

postgres_task = PostgresOperator(
    task_id='run_query',
    postgres_conn_id='my_postgres',
    sql='SELECT COUNT(*) FROM users;',
    dag=dag
)
```

### 3. Configuration

**airflow.cfg Settings:**
```ini
[core]
dags_folder = /opt/airflow/dags
load_examples = False
execute_tasks_new_python_interpreter = True

[scheduler]
dag_dir_list_interval = 30
job_heartbeat_sec = 5

[webserver]
web_server_host = 0.0.0.0
web_server_port = 8080

[database]
sql_alchemy_conn = postgresql://airflow:airflow@localhost/airflow
```

## Advanced Features

### 1. XComs (Cross-Communication)

**Task Communication:**
```python
def extract_data(**context):
    import pandas as pd
    df = pd.read_csv('/data/input.csv')
    # Push data to XCom
    context['ti'].xcom_push(key='row_count', value=len(df))
    context['ti'].xcom_push(key='columns', value=list(df.columns))
    return df.to_json()

def transform_data(**context):
    # Pull data from XCom
    ti = context['ti']
    row_count = ti.xcom_pull(key='row_count', task_ids='extract')
    columns = ti.xcom_pull(key='columns', task_ids='extract')

    print(f"Processing {row_count} rows with columns: {columns}")

    # Transform logic here
    return 'Transformed data'

extract = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    provide_context=True,
    dag=dag
)

transform = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)

extract >> transform
```

**XCom Best Practices:**
```python
# Use descriptive keys
context['ti'].xcom_push(key='processed_file_path', value='/data/processed/output.csv')

# Clean up large XComs
def cleanup_xcom(**context):
    ti = context['ti']
    # Remove large data from XCom after use
    ti.xcom_push(key='large_data', value=None)

# Use XCom for metadata, not large datasets
# Store file paths, row counts, status messages
# Store actual data in files/databases
```

### 2. Task Groups

**Organizing Complex DAGs:**
```python
from airflow.utils.task_group import TaskGroup

def create_etl_group(group_id, source_table):
    with TaskGroup(group_id=group_id, dag=dag) as tg:
        extract = PythonOperator(
            task_id='extract',
            python_callable=extract_table,
            op_kwargs={'table': source_table},
            dag=dag
        )

        validate = PythonOperator(
            task_id='validate',
            python_callable=validate_data,
            dag=dag
        )

        transform = PythonOperator(
            task_id='transform',
            python_callable=transform_data,
            dag=dag
        )

        load = PythonOperator(
            task_id='load',
            python_callable=load_data,
            op_kwargs={'table': source_table},
            dag=dag
        )

        extract >> validate >> transform >> load

    return tg

# Create multiple ETL groups
customers_etl = create_etl_group('customers_etl', 'customers')
orders_etl = create_etl_group('orders_etl', 'orders')
products_etl = create_etl_group('products_etl', 'products')

# Set dependencies between groups
start >> [customers_etl, orders_etl, products_etl] >> end
```

### 3. Dynamic DAGs

**Generating DAGs Programmatically:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def create_dag(dag_id, schedule, tables):
    dag = DAG(
        dag_id=dag_id,
        start_date=datetime(2023, 1, 1),
        schedule_interval=schedule,
        catchup=False
    )

    with dag:
        start_task = DummyOperator(task_id='start')

        for table in tables:
            task = PythonOperator(
                task_id=f'process_{table}',
                python_callable=process_table,
                op_kwargs={'table_name': table}
            )
            start_task >> task

        end_task = DummyOperator(task_id='end')
        [task for task in dag.tasks if task.task_id.startswith('process_')] >> end_task

    return dag

# Create multiple DAGs
daily_dag = create_dag('daily_etl', '@daily', ['users', 'orders'])
hourly_dag = create_dag('hourly_metrics', '@hourly', ['events', 'logs'])

# Register DAGs globally
globals()['daily_etl'] = daily_dag
globals()['hourly_metrics'] = hourly_dag
```

### 4. Custom Operators

**Creating Custom Operators:**
```python
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import Dict, Any

class DataQualityOperator(BaseOperator):
    @apply_defaults
    def __init__(
        self,
        table_name: str,
        quality_checks: Dict[str, Any],
        conn_id: str = 'default',
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.quality_checks = quality_checks
        self.conn_id = conn_id

    def execute(self, context):
        self.log.info(f"Running quality checks on {self.table_name}")

        # Implement quality checks
        results = {}
        for check_name, check_config in self.quality_checks.items():
            result = self._run_check(check_name, check_config)
            results[check_name] = result

            if not result['passed']:
                raise Exception(f"Quality check {check_name} failed: {result['message']}")

        self.log.info(f"All quality checks passed for {self.table_name}")
        return results

    def _run_check(self, check_name, check_config):
        # Implement specific quality checks
        if check_name == 'row_count':
            # Check minimum row count
            pass
        elif check_name == 'null_check':
            # Check for null values in specified columns
            pass
        # Add more checks as needed

        return {'passed': True, 'message': 'Check passed'}

# Usage
quality_check = DataQualityOperator(
    task_id='check_data_quality',
    table_name='customers',
    quality_checks={
        'row_count': {'min_rows': 1000},
        'null_check': {'columns': ['customer_id', 'email']}
    },
    dag=dag
)
```

## Scheduling and Triggers

### 1. Schedule Intervals

**Common Schedule Patterns:**
```python
# Cron expressions
dag_cron = DAG(
    'cron_example',
    schedule_interval='0 9 * * 1-5',  # 9 AM weekdays
    start_date=datetime(2023, 1, 1),
)

# Predefined intervals
dag_daily = DAG('daily_pipeline', schedule_interval='@daily')
dag_hourly = DAG('hourly_pipeline', schedule_interval='@hourly')
dag_weekly = DAG('weekly_pipeline', schedule_interval='@weekly')

# Timedelta
dag_custom = DAG(
    'custom_interval',
    schedule_interval=timedelta(hours=6),  # Every 6 hours
)

# Complex schedules
dag_complex = DAG(
    'complex_schedule',
    schedule_interval='0 6,18 * * *',  # 6 AM and 6 PM daily
)
```

### 2. Manual Triggers and Backfilling

**Triggering DAGs:**
```bash
# Trigger DAG manually
airflow dags trigger my_dag

# Trigger with configuration
airflow dags trigger my_dag --conf '{"key": "value"}'

# Backfill historical runs
airflow dags backfill my_dag \
    --start-date 2023-01-01 \
    --end-date 2023-01-31
```

**Handling Trigger Configurations:**
```python
def process_trigger_config(**context):
    dag_run = context['dag_run']
    config = dag_run.conf or {}

    # Access trigger configuration
    table_name = config.get('table_name', 'default_table')
    batch_size = config.get('batch_size', 1000)

    print(f"Processing table: {table_name} with batch size: {batch_size}")

    # Process based on configuration
    return f"Processed {table_name}"

trigger_task = PythonOperator(
    task_id='process_config',
    python_callable=process_trigger_config,
    provide_context=True,
    dag=dag
)
```

## Monitoring and Logging

### 1. Logging

**Custom Logging:**
```python
import logging

def my_task(**context):
    logger = logging.getLogger(__name__)

    logger.info("Starting task execution")

    try:
        # Task logic
        result = process_data()
        logger.info(f"Task completed successfully. Processed {result} records")
        return result
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise

task = PythonOperator(
    task_id='my_task',
    python_callable=my_task,
    dag=dag
)
```

### 2. Metrics and Monitoring

**Custom Metrics:**
```python
from airflow.metrics.base import MetricsCollector
from statsd import StatsClient

def send_metrics(**context):
    statsd = StatsClient(host='localhost', port=8125)

    # Send custom metrics
    statsd.gauge('pipeline.batch_size', 1000)
    statsd.increment('pipeline.tasks_completed')
    statsd.timing('pipeline.duration', 3600)

# Add metrics collection to tasks
task_with_metrics = PythonOperator(
    task_id='task_with_metrics',
    python_callable=lambda: None,
    on_success_callback=send_metrics,
    dag=dag
)
```

### 3. Alerting

**Email Alerts:**
```python
def failure_callback(context):
    task_instance = context['task_instance']
    email = EmailOperator(
        task_id='alert_on_failure',
        to=['team@company.com'],
        subject=f"Task Failed: {task_instance.task_id}",
        html_content=f"""
        <h3>Task Failure Alert</h3>
        <p><strong>DAG:</strong> {task_instance.dag_id}</p>
        <p><strong>Task:</strong> {task_instance.task_id}</p>
        <p><strong>Execution Date:</strong> {context['execution_date']}</p>
        <p><strong>Error:</strong> {context.get('exception', 'Unknown error')}</p>
        """,
        dag=dag
    )
    email.execute(context)

task = PythonOperator(
    task_id='critical_task',
    python_callable=my_function,
    on_failure_callback=failure_callback,
    dag=dag
)
```

## Production Deployment

### 1. Docker Deployment

**Docker Compose Setup:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  airflow-webserver:
    image: apache/airflow:2.5.0
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    command: webserver
    depends_on:
      - postgres
      - redis

  airflow-scheduler:
    image: apache/airflow:2.5.0
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: scheduler
    depends_on:
      - postgres
      - redis

  airflow-worker:
    image: apache/airflow:2.5.0
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
    command: celery worker
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

### 2. Kubernetes Deployment

**Kubernetes Manifests:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-webserver
spec:
  replicas: 1
  selector:
    matchLabels:
      component: webserver
  template:
    metadata:
      labels:
        component: webserver
    spec:
      containers:
      - name: webserver
        image: apache/airflow:2.5.0
        env:
        - name: AIRFLOW__CORE__EXECUTOR
          value: KubernetesExecutor
        - name: AIRFLOW__KUBERNETES__NAMESPACE
          value: airflow
        ports:
        - containerPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: airflow-scheduler
spec:
  replicas: 1
  selector:
    matchLabels:
      component: scheduler
  template:
    metadata:
      labels:
        component: scheduler
    spec:
      containers:
      - name: scheduler
        image: apache/airflow:2.5.0
        env:
        - name: AIRFLOW__CORE__EXECUTOR
          value: KubernetesExecutor
```

### 3. Best Practices for Production

**Configuration Management:**
```python
# Use environment variables for sensitive data
import os

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Use Airflow connections for external systems
from airflow.hooks.base import BaseHook

def get_db_connection():
    conn = BaseHook.get_connection('my_database')
    return {
        'host': conn.host,
        'user': conn.login,
        'password': conn.password,
        'database': conn.schema
    }
```

**Error Handling and Recovery:**
```python
from airflow.utils.trigger_rule import TriggerRule

def cleanup_on_failure(**context):
    # Clean up temporary files, connections, etc.
    import shutil
    shutil.rmtree('/tmp/pipeline_data', ignore_errors=True)

task = PythonOperator(
    task_id='main_task',
    python_callable=my_function,
    on_failure_callback=cleanup_on_failure,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup',
    python_callable=cleanup_on_failure,
    trigger_rule=TriggerRule.ALL_FAILED,  # Run only if upstream fails
    dag=dag
)

task >> cleanup_task
```

**Performance Optimization:**
```python
# Use appropriate executor
# LocalExecutor for single machine
# CeleryExecutor for distributed workers
# KubernetesExecutor for containerized environments

# Configure parallelism
dag = DAG(
    'optimized_dag',
    concurrency=10,        # Max concurrent tasks per DAG
    max_active_runs=3,     # Max concurrent DAG runs
    dagrun_timeout=timedelta(hours=2),
)

# Use pools for resource management
task = PythonOperator(
    task_id='resource_intensive_task',
    python_callable=my_function,
    pool='heavy_processing',  # Limit concurrent heavy tasks
    pool_slots=2,
    dag=dag
)
```

## Summary

Apache Airflow provides comprehensive workflow orchestration capabilities:

- **DAGs**: Define complex workflows with dependencies
- **Operators**: Execute various types of tasks and operations
- **Scheduling**: Flexible scheduling with cron expressions and intervals
- **Monitoring**: Web UI for monitoring and managing workflows
- **Extensibility**: Custom operators, hooks, and plugins
- **Scalability**: Distributed execution with various executors

Key features for data engineering:
- **ETL Pipelines**: Orchestrate data extraction, transformation, and loading
- **Dependency Management**: Handle complex task relationships
- **Error Handling**: Robust failure handling and recovery
- **Monitoring**: Comprehensive logging and alerting
- **Integration**: Connect with various data systems and APIs

Airflow enables building reliable, scalable data pipelines that can handle complex business requirements while providing visibility and control over the entire data processing lifecycle.
