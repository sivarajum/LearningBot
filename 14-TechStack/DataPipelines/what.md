# Data Pipelines: Comprehensive Guide

## Core Concepts

### Data Pipeline Fundamentals

Data pipelines are automated workflows that ingest, process, transform, and deliver data from various sources to destinations. They form the backbone of modern data architectures, enabling reliable data flow across systems.

**Key Characteristics:**
- **Automated**: Scheduled or event-triggered execution
- **Reliable**: Fault-tolerant with error handling and recovery
- **Scalable**: Handle varying data volumes and velocities
- **Maintainable**: Well-documented and version-controlled
- **Observable**: Comprehensive monitoring and alerting
- **Testable**: Unit tests and integration tests

### Pipeline Types and Patterns

**Pipeline Categories:**
- **ETL Pipelines**: Extract, Transform, Load - traditional batch processing
- **ELT Pipelines**: Extract, Load, Transform - modern cloud-native approach
- **Streaming Pipelines**: Real-time data processing
- **Batch Pipelines**: Periodic data processing
- **Hybrid Pipelines**: Combination of batch and streaming

**Common Patterns:**
- **Fan-out Pattern**: Single source to multiple destinations
- **Fan-in Pattern**: Multiple sources to single destination
- **Branching Pattern**: Conditional processing paths
- **Retry Pattern**: Automatic retry on failures
- **Circuit Breaker Pattern**: Fail-fast on persistent errors

## Apache Airflow

### Airflow Architecture

Apache Airflow is a platform for programmatically authoring, scheduling, and monitoring workflows. It uses Python to define workflows as Directed Acyclic Graphs (DAGs).

**Core Components:**
- **Web Server**: Flask-based UI for monitoring and triggering DAGs
- **Scheduler**: Parses DAGs and schedules tasks
- **Executor**: Handles task execution (Sequential, Local, Celery, Kubernetes)
- **Worker**: Processes individual tasks
- **Metadata Database**: Stores DAG and task state information
- **DAG Files**: Python files containing workflow definitions

### DAG Definition and Structure

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from airflow.decorators import dag, task

# Traditional DAG definition
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,  # Don't run missed DAGs
}

dag = DAG(
    'data_pipeline_etl',
    default_args=default_args,
    description='ETL pipeline for customer data',
    schedule_interval='@daily',  # Run daily
    max_active_runs=1,
    tags=['etl', 'customers', 'daily'],
)

# Task definitions
def extract_customer_data(**context):
    """Extract customer data from source systems"""
    # Implementation here
    print("Extracting customer data...")
    return "customer_data_extracted"

def transform_customer_data(**context):
    """Transform and clean customer data"""
    # Get data from previous task
    ti = context['ti']
    extracted_data = ti.xcom_pull(task_ids='extract_customers')

    # Transformation logic
    print("Transforming customer data...")
    return "customer_data_transformed"

def load_customer_data(**context):
    """Load transformed data to warehouse"""
    # Get transformed data
    ti = context['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_customers')

    # Load logic
    print("Loading customer data to warehouse...")
    return "customer_data_loaded"

# Task instances
extract_task = PythonOperator(
    task_id='extract_customers',
    python_callable=extract_customer_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_customers',
    python_callable=transform_customer_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_customers',
    python_callable=load_customer_data,
    dag=dag,
)

# Dependencies
extract_task >> transform_task >> load_task

# Using TaskFlow API (Airflow 2.0+)
@dag(
    dag_id='customer_pipeline_taskflow',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=days_ago(1),
    tags=['etl', 'customers', 'taskflow'],
)
def customer_pipeline():
    @task
    def extract_customers():
        """Extract customer data"""
        # Extract logic
        return {"customers": [], "count": 100}

    @task
    def validate_customers(customer_data):
        """Validate extracted data"""
        if customer_data['count'] > 0:
            return customer_data
        raise ValueError("No customer data extracted")

    @task
    def transform_customers(validated_data):
        """Transform customer data"""
        # Transform logic
        return {"transformed_customers": [], "count": validated_data['count']}

    @task
    def load_customers(transformed_data):
        """Load to warehouse"""
        # Load logic
        print(f"Loaded {transformed_data['count']} customers")
        return "success"

    # Define workflow
    raw_data = extract_customers()
    validated_data = validate_customers(raw_data)
    transformed_data = transform_customers(validated_data)
    result = load_customers(transformed_data)

# Create DAG instance
customer_dag = customer_pipeline()
```

### Advanced Airflow Features

```python
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
import random

# Dynamic DAG generation
def create_dynamic_dag(table_name, schedule):
    """Create DAG dynamically for different tables"""

    dag = DAG(
        f'etl_{table_name}',
        start_date=days_ago(1),
        schedule_interval=schedule,
        catchup=False,
    )

    def extract_table(**context):
        print(f"Extracting {table_name}")
        return f"{table_name}_extracted"

    def transform_table(**context):
        ti = context['ti']
        data = ti.xcom_pull(task_ids=f'extract_{table_name}')
        print(f"Transforming {data}")
        return f"{table_name}_transformed"

    extract = PythonOperator(
        task_id=f'extract_{table_name}',
        python_callable=extract_table,
        dag=dag,
    )

    transform = PythonOperator(
        task_id=f'transform_{table_name}',
        python_callable=transform_table,
        dag=dag,
    )

    extract >> transform
    return dag

# Conditional branching
def decide_branch(**context):
    """Decide which branch to take based on conditions"""
    ti = context['ti']
    data_quality = ti.xcom_pull(task_ids='check_data_quality')

    if data_quality['score'] > 0.8:
        return 'process_high_quality'
    elif data_quality['score'] > 0.5:
        return 'process_medium_quality'
    else:
        return 'handle_low_quality'

# Sensor for cross-DAG dependencies
def create_sensor_dag():
    dag = DAG(
        'dependent_pipeline',
        start_date=days_ago(1),
        schedule_interval='@daily',
    )

    # Wait for another DAG to complete
    wait_for_etl = ExternalTaskSensor(
        task_id='wait_for_etl_completion',
        external_dag_id='main_etl_pipeline',
        external_task_id='load_data',
        dag=dag,
    )

    # Trigger another DAG
    trigger_downstream = TriggerDagRunOperator(
        task_id='trigger_reporting',
        trigger_dag_id='daily_reporting',
        dag=dag,
    )

    wait_for_etl >> trigger_downstream
    return dag

# SubDAGs for modular workflows
def create_subdag(parent_dag_name, child_dag_name, start_date):
    """Create a SubDAG"""
    dag = DAG(
        f'{parent_dag_name}.{child_dag_name}',
        start_date=start_date,
        schedule_interval='@daily',
    )

    task_1 = DummyOperator(task_id='sub_task_1', dag=dag)
    task_2 = DummyOperator(task_id='sub_task_2', dag=dag)
    task_3 = DummyOperator(task_id='sub_task_3', dag=dag)

    task_1 >> task_2 >> task_3
    return dag

# Error handling and retries
def create_resilient_dag():
    dag = DAG(
        'resilient_pipeline',
        start_date=days_ago(1),
        schedule_interval='@hourly',
        default_args={
            'retries': 3,
            'retry_delay': timedelta(minutes=5),
            'retry_exponential_backoff': True,
            'max_retry_delay': timedelta(hours=1),
        }
    )

    # Task with custom retry logic
    def risky_operation(**context):
        if random.random() < 0.3:  # 30% failure rate
            raise Exception("Random failure occurred")
        return "success"

    risky_task = PythonOperator(
        task_id='risky_operation',
        python_callable=risky_operation,
        dag=dag,
    )

    # Cleanup task that runs even if upstream fails
    cleanup = PythonOperator(
        task_id='cleanup',
        python_callable=lambda: print("Cleaning up..."),
        trigger_rule=TriggerRule.ALL_DONE,  # Run regardless of upstream status
        dag=dag,
    )

    risky_task >> cleanup
    return dag

# SLA and timeout management
def create_sla_dag():
    dag = DAG(
        'sla_pipeline',
        start_date=days_ago(1),
        schedule_interval='@daily',
        sla_miss_callback=sla_miss_handler,  # Custom SLA callback
        default_args={
            'sla': timedelta(hours=2),  # 2-hour SLA for all tasks
        }
    )

    def sla_miss_handler(dag, task_list, blocking_task_list, slas, blocking_tis):
        """Handle SLA misses"""
        print(f"SLA missed for DAG {dag.dag_id}")
        # Send alerts, notifications, etc.

    # Task with specific SLA
    long_running_task = PythonOperator(
        task_id='long_running_operation',
        python_callable=lambda: time.sleep(3600),  # 1 hour
        sla=timedelta(minutes=30),  # Override default SLA
        execution_timeout=timedelta(hours=1),  # Kill if runs too long
        dag=dag,
    )

    return dag
```

### Airflow Operators and Hooks

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.S3_hook import S3Hook
import pandas as pd

# Database operations
def create_database_pipeline():
    dag = DAG('database_etl', start_date=days_ago(1), schedule_interval='@daily')

    # Direct SQL execution
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        dag=dag,
    )

    # Data extraction with hooks
    def extract_with_hook(**context):
        hook = PostgresHook(postgres_conn_id='postgres_default')
        df = hook.get_pandas_df("SELECT * FROM source_customers WHERE updated_at > '{{ yesterday_ds }}'")
        return df.to_json()

    extract = PythonOperator(
        task_id='extract_customers',
        python_callable=extract_with_hook,
        dag=dag,
    )

    create_table >> extract
    return dag

# Cloud storage operations
def create_cloud_pipeline():
    dag = DAG('cloud_etl', start_date=days_ago(1), schedule_interval='@daily')

    # S3 operations
    copy_to_s3 = S3CopyObjectOperator(
        task_id='copy_to_s3',
        source_bucket_name='source-bucket',
        source_bucket_key='data/input.csv',
        dest_bucket_name='processed-bucket',
        dest_bucket_key='data/processed/{{ ds }}/input.csv',
        aws_conn_id='aws_default',
        dag=dag,
    )

    # BigQuery operations
    bq_query = BigQueryExecuteQueryOperator(
        task_id='bq_transform',
        sql="""
        CREATE OR REPLACE TABLE `project.dataset.processed_customers`
        PARTITION BY DATE(created_at)
        AS SELECT * FROM `project.dataset.raw_customers`
        WHERE created_at >= '{{ yesterday_ds }}'
        """,
        use_legacy_sql=False,
        gcp_conn_id='google_cloud_default',
        dag=dag,
    )

    copy_to_s3 >> bq_query
    return dag

# Spark integration
def create_spark_pipeline():
    dag = DAG('spark_etl', start_date=days_ago(1), schedule_interval='@daily')

    spark_job = SparkSubmitOperator(
        task_id='spark_processing',
        application='/path/to/spark_job.py',
        conn_id='spark_default',
        application_args=['--input', '{{ ds }}', '--output', '{{ ds }}'],
        jars='/path/to/extra/jars',
        driver_memory='2g',
        executor_memory='4g',
        num_executors=4,
        dag=dag,
    )

    return dag

# Custom operators
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):
    """Custom operator for data quality checks"""

    @apply_defaults
    def __init__(self, table_name, quality_checks, conn_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.quality_checks = quality_checks
        self.conn_id = conn_id

    def execute(self, context):
        hook = PostgresHook(postgres_conn_id=self.conn_id)

        results = {}
        for check_name, check_sql in self.quality_checks.items():
            result = hook.get_first(check_sql)
            results[check_name] = result[0] if result else 0

            # Fail task if quality check fails
            if results[check_name] < self.quality_checks[check_name]['threshold']:
                raise ValueError(f"Data quality check '{check_name}' failed")

        context['ti'].xcom_push(key='quality_results', value=results)
        return results

def create_quality_pipeline():
    dag = DAG('data_quality_pipeline', start_date=days_ago(1), schedule_interval='@daily')

    quality_checks = {
        'row_count': {
            'sql': 'SELECT COUNT(*) FROM customers',
            'threshold': 1000
        },
        'null_emails': {
            'sql': 'SELECT COUNT(*) FROM customers WHERE email IS NULL',
            'threshold': 10
        },
        'duplicate_ids': {
            'sql': 'SELECT COUNT(*) FROM (SELECT id, COUNT(*) as cnt FROM customers GROUP BY id HAVING cnt > 1) t',
            'threshold': 1
        }
    }

    quality_check = DataQualityOperator(
        task_id='check_data_quality',
        table_name='customers',
        quality_checks=quality_checks,
        conn_id='postgres_default',
        dag=dag,
    )

    return dag
```

## Prefect

### Prefect Workflows

Prefect is a modern workflow orchestration framework that emphasizes reliability, observability, and developer experience.

**Key Concepts:**
- **Flows**: Container for workflow logic
- **Tasks**: Individual units of work
- **States**: Represent task execution results
- **Parameters**: Dynamic flow inputs
- **Schedules**: When flows should run

```python
from prefect import flow, task, get_run_context
from prefect.states import Completed, Failed
from prefect.logging import get_logger
from prefect.blocks.system import Secret
from typing import List, Dict, Any
import pandas as pd
import requests

# Basic task definition
@task
def extract_data(source_url: str) -> pd.DataFrame:
    """Extract data from a REST API"""
    logger = get_logger()

    try:
        response = requests.get(source_url)
        response.raise_for_status()

        data = response.json()
        df = pd.DataFrame(data)

        logger.info(f"Extracted {len(df)} records from {source_url}")
        return df

    except Exception as e:
        logger.error(f"Failed to extract data: {e}")
        raise

@task
def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate data quality"""
    logger = get_logger()

    # Check for required columns
    required_cols = ['id', 'name', 'email']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Check for null values in critical fields
    null_emails = df['email'].isnull().sum()
    if null_emails > len(df) * 0.1:  # More than 10% null
        raise ValueError(f"Too many null emails: {null_emails}")

    logger.info("Data validation passed")
    return df

@task
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform and clean data"""
    logger = get_logger()

    # Remove duplicates
    original_count = len(df)
    df = df.drop_duplicates(subset=['id'])
    logger.info(f"Removed {original_count - len(df)} duplicates")

    # Clean email addresses
    df['email'] = df['email'].str.lower().str.strip()

    # Add derived columns
    df['domain'] = df['email'].str.split('@').str[1]
    df['created_at'] = pd.Timestamp.now()

    logger.info(f"Transformed data: {len(df)} records")
    return df

@task
def load_data(df: pd.DataFrame, table_name: str) -> int:
    """Load data to database"""
    logger = get_logger()

    # Get database credentials from Prefect blocks
    db_password = Secret.load("db-password").get()

    # Database connection and loading logic
    # (Implementation would depend on your database)

    logger.info(f"Loaded {len(df)} records to {table_name}")
    return len(df)

# Flow definition
@flow(name="ETL Pipeline", description="Extract, transform, and load customer data")
def etl_pipeline(source_url: str = "https://api.example.com/customers",
                table_name: str = "customers") -> Dict[str, Any]:

    logger = get_logger()
    logger.info("Starting ETL pipeline")

    # Execute tasks in sequence
    raw_data = extract_data(source_url)
    validated_data = validate_data(raw_data)
    transformed_data = transform_data(validated_data)
    loaded_count = load_data(transformed_data, table_name)

    # Return summary
    result = {
        'records_processed': loaded_count,
        'pipeline_status': 'completed',
        'execution_time': get_run_context().start_time
    }

    logger.info(f"ETL pipeline completed: {result}")
    return result

# Advanced Prefect features
from prefect import task, flow
from prefect.tasks import task_input_hash
from prefect.cache_policies import InputHashCache
from prefect.utilities.tasks import task
import asyncio

# Cached tasks for performance
@task(cache_policy=InputHashCache())
def expensive_computation(data: pd.DataFrame) -> pd.DataFrame:
    """Expensive computation that should be cached"""
    # Simulate expensive operation
    import time
    time.sleep(5)

    result = data.copy()
    result['computed_column'] = result['value'] * 2
    return result

# Async tasks for I/O operations
@task
async def async_api_call(url: str) -> Dict:
    """Asynchronous API call"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Conditional flows
@task
def check_data_quality(df: pd.DataFrame) -> bool:
    """Check if data meets quality standards"""
    return len(df) > 100 and df['email'].notna().mean() > 0.95

@flow
def conditional_etl_pipeline(source_url: str):
    """ETL pipeline with conditional logic"""

    raw_data = extract_data(source_url)
    validated_data = validate_data(raw_data)

    # Conditional processing
    quality_ok = check_data_quality(validated_data)

    if quality_ok:
        transformed_data = transform_data(validated_data)
        load_data(transformed_data, "customers")
    else:
        # Send alert or handle poor quality data
        handle_poor_quality_data(validated_data)

@task
def handle_poor_quality_data(df: pd.DataFrame):
    """Handle data that doesn't meet quality standards"""
    logger = get_logger()
    logger.warning(f"Poor quality data detected: {len(df)} records")

    # Send alert, quarantine data, etc.
    # Implementation depends on your requirements

# Parallel processing
@flow
def parallel_processing_pipeline(urls: List[str]):
    """Process multiple data sources in parallel"""

    # Create tasks for each URL
    extract_tasks = [extract_data(url) for url in urls]

    # Wait for all extractions to complete
    raw_datasets = extract_tasks

    # Process each dataset
    processed_datasets = []
    for dataset in raw_datasets:
        validated = validate_data(dataset)
        transformed = transform_data(validated)
        processed_datasets.append(transformed)

    # Combine results
    combined_data = pd.concat(processed_datasets, ignore_index=True)

    # Load combined data
    load_data(combined_data, "combined_customers")

# Error handling and retries
from prefect.states import Failed
from typing import Optional

@task(retries=3, retry_delay_seconds=60)
def unreliable_task() -> str:
    """Task that might fail and should be retried"""
    import random

    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("Random failure")

    return "success"

@flow
def resilient_pipeline():
    """Pipeline with error handling"""

    try:
        result = unreliable_task()
        return result
    except Exception as e:
        logger = get_logger()
        logger.error(f"Pipeline failed: {e}")

        # Cleanup or notification logic
        send_failure_notification(e)

        # Re-raise to mark flow as failed
        raise

@task
def send_failure_notification(error: Exception):
    """Send notification about pipeline failure"""
    # Implementation for sending alerts
    pass

# Dynamic workflows
@flow
def dynamic_etl_pipeline(sources: List[Dict[str, str]]):
    """Dynamically create ETL pipeline based on configuration"""

    all_processed_data = []

    for source_config in sources:
        source_type = source_config['type']
        source_url = source_config['url']

        if source_type == 'api':
            data = extract_data(source_url)
        elif source_type == 'file':
            data = extract_from_file(source_url)
        else:
            raise ValueError(f"Unknown source type: {source_type}")

        validated = validate_data(data)
        transformed = transform_data(validated)
        all_processed_data.append(transformed)

    # Combine all sources
    combined = pd.concat(all_processed_data, ignore_index=True)
    load_data(combined, "multi_source_customers")

@task
def extract_from_file(file_path: str) -> pd.DataFrame:
    """Extract data from file"""
    return pd.read_csv(file_path)
```

## Dagster

### Dagster Pipelines

Dagster is a data orchestrator for machine learning, analytics, and ETL. It emphasizes data quality, testing, and developer experience.

**Key Concepts:**
- **Assets**: Observable, testable data assets
- **Ops**: Individual units of computation
- **Jobs**: Executable pipelines
- **Graphs**: Composable computation graphs
- **Resources**: External dependencies (databases, APIs)

```python
from dagster import asset, op, job, graph, repository, resource, AssetMaterialization
from dagster.core.definitions import InputDefinition, OutputDefinition
import pandas as pd
import sqlalchemy as sa
from typing import Dict, Any

# Resources for external dependencies
@resource
def database_resource():
    """Database connection resource"""
    engine = sa.create_engine('postgresql://user:pass@localhost/db')
    return engine

@resource
def api_resource():
    """API client resource"""
    return requests.Session()

# Assets for data products
@asset(
    group_name="raw_data",
    metadata={"source": "external_api", "update_frequency": "daily"}
)
def raw_customers(api_client) -> pd.DataFrame:
    """Raw customer data from API"""
    response = api_client.get("https://api.example.com/customers")
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data)

    # Log asset materialization
    yield AssetMaterialization(
        asset_key="raw_customers",
        metadata={"row_count": len(df), "columns": list(df.columns)}
    )

    return df

@asset(
    group_name="processed_data",
    metadata={"quality_checks": ["not_null", "unique_ids"]}
)
def processed_customers(raw_customers: pd.DataFrame) -> pd.DataFrame:
    """Processed and validated customer data"""

    # Data quality checks
    assert raw_customers['id'].is_unique, "Customer IDs must be unique"
    assert raw_customers['email'].notna().all(), "All customers must have emails"

    # Transformations
    df = raw_customers.copy()
    df['email'] = df['email'].str.lower().str.strip()
    df['domain'] = df['email'].str.split('@').str[1]
    df['processed_at'] = pd.Timestamp.now()

    yield AssetMaterialization(
        asset_key="processed_customers",
        metadata={"processed_rows": len(df), "domains": df['domain'].nunique()}
    )

    return df

@asset(
    group_name="analytics",
    metadata={"type": "aggregation", "grain": "daily"}
)
def customer_analytics(processed_customers: pd.DataFrame) -> pd.DataFrame:
    """Customer analytics and insights"""

    analytics = processed_customers.groupby('domain').agg({
        'id': 'count',
        'created_at': 'min'
    }).rename(columns={
        'id': 'customer_count',
        'created_at': 'first_customer_date'
    }).reset_index()

    yield AssetMaterialization(
        asset_key="customer_analytics",
        metadata={"domain_count": len(analytics), "total_customers": analytics['customer_count'].sum()}
    )

    return analytics

# Ops for complex logic
@op(
    ins={"data": InputDefinition("Raw data to validate")},
    out={"valid_data": OutputDefinition("Validated data"), "errors": OutputDefinition("Validation errors")},
    required_resource_keys={"database"}
)
def validate_and_clean_data(context, data: pd.DataFrame) -> tuple:
    """Validate data and separate valid/invalid records"""

    errors = []

    # Validation rules
    valid_data = data.copy()

    # Check email format
    invalid_emails = ~valid_data['email'].str.contains(r'^[^@]+@[^@]+\.[^@]+$')
    if invalid_emails.any():
        error_records = valid_data[invalid_emails]
        errors.extend([f"Invalid email: {row['email']}" for _, row in error_records.iterrows()])
        valid_data = valid_data[~invalid_emails]

    # Check required fields
    required_fields = ['id', 'name', 'email']
    for field in required_fields:
        null_mask = valid_data[field].isnull()
        if null_mask.any():
            error_records = valid_data[null_mask]
            errors.extend([f"Missing {field}: {row['id']}" for _, row in error_records.iterrows()])
            valid_data = valid_data[~null_mask]

    context.log.info(f"Validated {len(valid_data)} records, found {len(errors)} errors")

    return valid_data, errors

@op(required_resource_keys={"database"})
def load_to_database(context, data: pd.DataFrame, table_name: str):
    """Load data to database"""

    engine = context.resources.database

    # Create table if not exists
    data.to_sql(table_name, engine, if_exists='replace', index=False)

    context.log.info(f"Loaded {len(data)} records to {table_name}")

# Jobs for orchestration
@job(
    resource_defs={
        "database": database_resource,
        "api_client": api_resource
    },
    config={
        "ops": {
            "load_to_database": {"config": {"table_name": "customers"}}
        }
    }
)
def etl_job():
    """Complete ETL job"""

    # Extract
    raw_data = raw_customers()

    # Validate and clean
    valid_data, errors = validate_and_clean_data(raw_data)

    # Load valid data
    load_to_database(valid_data)

    # Handle errors (could be another op)
    if errors:
        context.log.warning(f"Validation errors: {errors}")

# Asset-based job
@job
def asset_based_etl():
    """ETL job using assets"""

    # Assets automatically handle dependencies
    analytics = customer_analytics(processed_customers(raw_customers()))

# Graphs for reusable components
@graph
def data_processing_graph(raw_data):
    """Reusable data processing graph"""

    valid_data, errors = validate_and_clean_data(raw_data)
    processed_data = processed_customers(valid_data)

    return processed_data, errors

@job
def multi_source_etl():
    """ETL job with multiple data sources"""

    # Process multiple sources
    source1_processed, source1_errors = data_processing_graph(raw_customers())
    source2_processed, source2_errors = data_processing_graph(raw_orders())

    # Combine results
    combined_data = combine_datasets(source1_processed, source2_processed)

    # Load combined data
    load_to_database(combined_data)

@op
def combine_datasets(dataset1: pd.DataFrame, dataset2: pd.DataFrame) -> pd.DataFrame:
    """Combine multiple datasets"""
    return pd.concat([dataset1, dataset2], ignore_index=True)

@op
def raw_orders(api_client) -> pd.DataFrame:
    """Raw orders data (similar to raw_customers)"""
    response = api_client.get("https://api.example.com/orders")
    response.raise_for_status()
    return pd.DataFrame(response.json())

# Repository definition
@repository
def data_pipeline_repository():
    """Repository containing all pipelines"""

    return [
        etl_job,
        asset_based_etl,
        multi_source_etl,
        # Include assets
        raw_customers,
        processed_customers,
        customer_analytics
    ]
```

## Data Quality and Validation

### Data Quality Framework

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import pandas as pd
import great_expectations as ge
from pandera import DataFrameSchema, Column, Check
import logging

@dataclass
class QualityCheckResult:
    check_name: str
    passed: bool
    message: str
    details: Dict[str, Any]

class DataQualityChecker(ABC):
    """Abstract base class for data quality checkers"""

    @abstractmethod
    def check(self, data: pd.DataFrame) -> List[QualityCheckResult]:
        pass

class PandasQualityChecker(DataQualityChecker):
    """Data quality checks using pandas"""

    def __init__(self, checks: Dict[str, Callable]):
        self.checks = checks

    def check(self, data: pd.DataFrame) -> List[QualityCheckResult]:
        results = []

        for check_name, check_func in self.checks.items():
            try:
                passed, message, details = check_func(data)
                results.append(QualityCheckResult(
                    check_name=check_name,
                    passed=passed,
                    message=message,
                    details=details
                ))
            except Exception as e:
                results.append(QualityCheckResult(
                    check_name=check_name,
                    passed=False,
                    message=f"Check failed with error: {str(e)}",
                    details={"error": str(e)}
                ))

        return results

class GreatExpectationsChecker(DataQualityChecker):
    """Data quality checks using Great Expectations"""

    def __init__(self, expectation_suite_path: str):
        self.expectation_suite_path = expectation_suite_path

    def check(self, data: pd.DataFrame) -> List[QualityCheckResult]:
        # Convert to Great Expectations dataframe
        ge_df = ge.from_pandas(data)

        # Load expectation suite
        with open(self.expectation_suite_path, 'r') as f:
            suite_config = json.load(f)

        # Run validation
        results = ge_df.validate(expectation_suite=suite_config)

        # Convert to our format
        quality_results = []
        for result in results['results']:
            quality_results.append(QualityCheckResult(
                check_name=result['expectation_config']['expectation_type'],
                passed=result['success'],
                message=result.get('result', {}).get('unexpected_percent', 'N/A'),
                details=result
            ))

        return quality_results

class PanderaSchemaChecker(DataQualityChecker):
    """Data quality checks using Pandera schemas"""

    def __init__(self, schema: DataFrameSchema):
        self.schema = schema

    def check(self, data: pd.DataFrame) -> List[QualityCheckResult]:
        try:
            validated_df = self.schema.validate(data)
            return [QualityCheckResult(
                check_name="pandera_schema_validation",
                passed=True,
                message="All schema validations passed",
                details={"validated_rows": len(validated_df)}
            )]
        except Exception as e:
            return [QualityCheckResult(
                check_name="pandera_schema_validation",
                passed=False,
                message=f"Schema validation failed: {str(e)}",
                details={"error": str(e)}
            )]

# Data quality pipeline integration
def create_quality_checks():
    """Create comprehensive data quality checks"""

    # Pandas-based checks
    pandas_checks = {
        'row_count_check': lambda df: (
            len(df) > 0,
            f"Row count: {len(df)}",
            {"row_count": len(df)}
        ),

        'duplicate_check': lambda df: (
            not df.duplicated().any(),
            f"Found {df.duplicated().sum()} duplicate rows",
            {"duplicate_count": int(df.duplicated().sum())}
        ),

        'null_check': lambda df: (
            df.isnull().sum().sum() == 0,
            f"Found {df.isnull().sum().sum()} null values",
            {"null_counts": df.isnull().sum().to_dict()}
        ),

        'email_format_check': lambda df: (
            df['email'].str.contains(r'^[^@]+@[^@]+\.[^@]+$').all(),
            "All emails are properly formatted",
            {"invalid_emails": (~df['email'].str.contains(r'^[^@]+@[^@]+\.[^@]+$')).sum()}
        )
    }

    # Pandera schema
    customer_schema = DataFrameSchema({
        "id": Column(int, Check(lambda x: x > 0), nullable=False),
        "name": Column(str, Check(lambda x: len(x.strip()) > 0), nullable=False),
        "email": Column(str, Check.str_contains(r'^[^@]+@[^@]+\.[^@]+$'), nullable=False),
        "age": Column(int, Check(lambda x: 18 <= x <= 120), nullable=True),
        "created_at": Column(pd.Timestamp, nullable=False)
    })

    return {
        'pandas_checker': PandasQualityChecker(pandas_checks),
        'pandera_checker': PanderaSchemaChecker(customer_schema)
    }

# Quality gate implementation
class QualityGate:
    """Quality gate that blocks pipeline progression on failures"""

    def __init__(self, checkers: Dict[str, DataQualityChecker], failure_threshold: float = 0.0):
        self.checkers = checkers
        self.failure_threshold = failure_threshold  # 0.0 = no failures allowed

    def validate(self, data: pd.DataFrame) -> tuple:
        """Validate data against all quality checkers"""

        all_results = []
        total_checks = 0
        failed_checks = 0

        for checker_name, checker in self.checkers.items():
            results = checker.check(data)
            all_results.extend(results)

            for result in results:
                total_checks += 1
                if not result.passed:
                    failed_checks += 1

        # Calculate failure rate
        failure_rate = failed_checks / total_checks if total_checks > 0 else 0

        # Determine if pipeline should proceed
        should_proceed = failure_rate <= self.failure_threshold

        return should_proceed, all_results, {
            'total_checks': total_checks,
            'failed_checks': failed_checks,
            'failure_rate': failure_rate
        }

# Integration with Airflow
def quality_check_task(**context):
    """Airflow task for data quality checks"""

    # Get data from previous task
    ti = context['ti']
    data_json = ti.xcom_pull(task_ids='extract_data')
    data = pd.read_json(data_json)

    # Create quality checkers
    checkers = create_quality_checks()

    # Create quality gate
    quality_gate = QualityGate(checkers, failure_threshold=0.1)  # Allow 10% failures

    # Run validation
    should_proceed, results, summary = quality_gate.validate(data)

    # Log results
    logger = logging.getLogger(__name__)
    logger.info(f"Quality check summary: {summary}")

    for result in results:
        if result.passed:
            logger.info(f"✓ {result.check_name}: {result.message}")
        else:
            logger.error(f"✗ {result.check_name}: {result.message}")

    # Store results for downstream tasks
    ti.xcom_push(key='quality_results', value={
        'should_proceed': should_proceed,
        'results': [result.__dict__ for result in results],
        'summary': summary
    })

    if not should_proceed:
        raise Exception(f"Data quality checks failed: {summary}")

    return data

# Integration with Prefect
@task
def prefect_quality_check(data: pd.DataFrame) -> pd.DataFrame:
    """Prefect task for data quality checks"""

    logger = get_logger()

    # Create quality checkers
    checkers = create_quality_checks()
    quality_gate = QualityGate(checkers, failure_threshold=0.1)

    # Run validation
    should_proceed, results, summary = quality_gate.validate(data)

    # Log results
    logger.info(f"Quality check summary: {summary}")

    for result in results:
        if result.passed:
            logger.info(f"✓ {result.check_name}: {result.message}")
        else:
            logger.error(f"✗ {result.check_name}: {result.message}")

    if not should_proceed:
        raise ValueError(f"Data quality checks failed: {summary}")

    return data
```

## Pipeline Monitoring and Alerting

### Comprehensive Monitoring System

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

@dataclass
class PipelineMetrics:
    pipeline_name: str
    run_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    task_metrics: Dict[str, Dict[str, Any]]
    data_metrics: Dict[str, Any]

@dataclass
class Alert:
    alert_id: str
    severity: str
    title: str
    message: str
    pipeline_name: str
    run_id: str
    timestamp: datetime
    context: Dict[str, Any]

class AlertChannel(ABC):
    """Abstract base class for alert channels"""

    @abstractmethod
    def send_alert(self, alert: Alert):
        pass

class EmailAlertChannel(AlertChannel):
    def __init__(self, smtp_config: Dict[str, str], recipients: List[str]):
        self.smtp_config = smtp_config
        self.recipients = recipients

    def send_alert(self, alert: Alert):
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config['username']
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = f"[{alert.severity.upper()}] {alert.title}"

        body = f"""
        Pipeline: {alert.pipeline_name}
        Run ID: {alert.run_id}
        Time: {alert.timestamp}
        Severity: {alert.severity}

        {alert.message}

        Context:
        {json.dumps(alert.context, indent=2)}
        """
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_config['server'], int(self.smtp_config['port']))
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.sendmail(self.smtp_config['username'], self.recipients, text)
            server.quit()
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")

class SlackAlertChannel(AlertChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_alert(self, alert: Alert):
        color_map = {'low': 'good', 'medium': 'warning', 'high': 'danger', 'critical': 'danger'}

        payload = {
            "attachments": [{
                "color": color_map.get(alert.severity, 'danger'),
                "title": alert.title,
                "text": alert.message,
                "fields": [
                    {"title": "Pipeline", "value": alert.pipeline_name, "short": True},
                    {"title": "Run ID", "value": alert.run_id, "short": True},
                    {"title": "Severity", "value": alert.severity.upper(), "short": True},
                    {"title": "Time", "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "short": True}
                ]
            }]
        }

        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {e}")

class PipelineMonitor:
    """Comprehensive pipeline monitoring system"""

    def __init__(self):
        self.metrics_store: Dict[str, PipelineMetrics] = {}
        self.alert_channels: List[AlertChannel] = []
        self.alert_rules: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    def add_alert_channel(self, channel: AlertChannel):
        """Add an alert channel"""
        self.alert_channels.append(channel)

    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add an alert rule"""
        self.alert_rules.append(rule)

    def start_pipeline_run(self, pipeline_name: str, run_id: str) -> str:
        """Start monitoring a pipeline run"""

        metrics = PipelineMetrics(
            pipeline_name=pipeline_name,
            run_id=run_id,
            start_time=datetime.now(),
            end_time=None,
            status='running',
            task_metrics={},
            data_metrics={}
        )

        self.metrics_store[run_id] = metrics
        self.logger.info(f"Started monitoring pipeline {pipeline_name} run {run_id}")

        return run_id

    def update_task_metrics(self, run_id: str, task_name: str, metrics: Dict[str, Any]):
        """Update metrics for a specific task"""

        if run_id not in self.metrics_store:
            self.logger.warning(f"Unknown run ID: {run_id}")
            return

        self.metrics_store[run_id].task_metrics[task_name] = {
            'timestamp': datetime.now(),
            'metrics': metrics
        }

        # Check for task-specific alerts
        self.check_task_alerts(run_id, task_name, metrics)

    def update_data_metrics(self, run_id: str, metrics: Dict[str, Any]):
        """Update data processing metrics"""

        if run_id not in self.metrics_store:
            self.logger.warning(f"Unknown run ID: {run_id}")
            return

        self.metrics_store[run_id].data_metrics.update(metrics)

    def end_pipeline_run(self, run_id: str, status: str):
        """End monitoring a pipeline run"""

        if run_id not in self.metrics_store:
            self.logger.warning(f"Unknown run ID: {run_id}")
            return

        self.metrics_store[run_id].end_time = datetime.now()
        self.metrics_store[run_id].status = status

        # Calculate duration
        duration = self.metrics_store[run_id].end_time - self.metrics_store[run_id].start_time

        self.logger.info(f"Ended pipeline run {run_id} with status {status}, duration: {duration}")

        # Check for pipeline-level alerts
        self.check_pipeline_alerts(run_id)

    def check_task_alerts(self, run_id: str, task_name: str, metrics: Dict[str, Any]):
        """Check for task-specific alerts"""

        for rule in self.alert_rules:
            if rule.get('type') != 'task':
                continue

            # Check if rule applies to this task
            if rule.get('task_pattern') and not rule['task_pattern'] in task_name:
                continue

            # Evaluate condition
            if self.evaluate_condition(metrics, rule['condition']):
                self.trigger_alert(run_id, rule, {
                    'task_name': task_name,
                    'task_metrics': metrics
                })

    def check_pipeline_alerts(self, run_id: str):
        """Check for pipeline-level alerts"""

        pipeline_metrics = self.metrics_store[run_id]

        for rule in self.alert_rules:
            if rule.get('type') != 'pipeline':
                continue

            # Check status-based rules
            if rule.get('status') and pipeline_metrics.status == rule['status']:
                self.trigger_alert(run_id, rule, {
                    'pipeline_status': pipeline_metrics.status,
                    'duration': str(pipeline_metrics.end_time - pipeline_metrics.start_time)
                })

            # Check duration-based rules
            if rule.get('max_duration'):
                duration = pipeline_metrics.end_time - pipeline_metrics.start_time
                if duration > timedelta(seconds=rule['max_duration']):
                    self.trigger_alert(run_id, rule, {
                        'actual_duration': str(duration),
                        'max_duration': rule['max_duration']
                    })

    def evaluate_condition(self, metrics: Dict[str, Any], condition: str) -> bool:
        """Evaluate a condition against metrics"""
        try:
            # Simple condition evaluation (in production, use a proper expression evaluator)
            return eval(condition, {"__builtins__": {}}, metrics)
        except Exception as e:
            self.logger.error(f"Failed to evaluate condition {condition}: {e}")
            return False

    def trigger_alert(self, run_id: str, rule: Dict[str, Any], context: Dict[str, Any]):
        """Trigger an alert"""

        pipeline_metrics = self.metrics_store[run_id]

        alert = Alert(
            alert_id=f"{run_id}_{rule['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            severity=rule['severity'],
            title=rule['title'],
            message=rule['message'],
            pipeline_name=pipeline_metrics.pipeline_name,
            run_id=run_id,
            timestamp=datetime.now(),
            context=context
        )

        # Send to all channels
        for channel in self.alert_channels:
            try:
                channel.send_alert(alert)
            except Exception as e:
                self.logger.error(f"Failed to send alert via {type(channel).__name__}: {e}")

        self.logger.warning(f"Alert triggered: {alert.title}")

    def get_pipeline_metrics(self, run_id: str) -> Optional[PipelineMetrics]:
        """Get metrics for a pipeline run"""
        return self.metrics_store.get(run_id)

    def get_recent_runs(self, pipeline_name: str = None, limit: int = 10) -> List[PipelineMetrics]:
        """Get recent pipeline runs"""

        runs = list(self.metrics_store.values())

        if pipeline_name:
            runs = [r for r in runs if r.pipeline_name == pipeline_name]

        # Sort by start time, most recent first
        runs.sort(key=lambda x: x.start_time, reverse=True)

        return runs[:limit]

# Integration with Airflow
def create_airflow_monitor():
    """Create monitor for Airflow pipelines"""

    monitor = PipelineMonitor()

    # Add alert channels
    email_config = {
        'server': 'smtp.gmail.com',
        'port': '587',
        'username': 'alerts@company.com',
        'password': 'password'
    }
    monitor.add_alert_channel(EmailAlertChannel(email_config, ['team@company.com']))

    # Add alert rules
    monitor.add_alert_rule({
        'name': 'task_failure',
        'type': 'task',
        'severity': 'high',
        'title': 'Task Failed',
        'message': 'A pipeline task has failed',
        'condition': 'status == "failed"'
    })

    monitor.add_alert_rule({
        'name': 'pipeline_timeout',
        'type': 'pipeline',
        'severity': 'critical',
        'title': 'Pipeline Timeout',
        'message': 'Pipeline exceeded maximum duration',
        'max_duration': 3600  # 1 hour
    })

    return monitor

# Usage in Airflow DAG
def monitored_extract_task(**context):
    """Monitored extract task"""

    monitor = create_airflow_monitor()
    run_id = context['dag_run'].run_id
    pipeline_name = context['dag'].dag_id

    # Start monitoring
    monitor.start_pipeline_run(pipeline_name, run_id)

    try:
        # Extract logic here
        data = extract_data()

        # Update metrics
        monitor.update_data_metrics(run_id, {
            'records_extracted': len(data),
            'extract_duration': 10.5
        })

        monitor.update_task_metrics(run_id, 'extract', {
            'status': 'success',
            'duration': 10.5,
            'records': len(data)
        })

        return data

    except Exception as e:
        monitor.update_task_metrics(run_id, 'extract', {
            'status': 'failed',
            'error': str(e)
        })
        raise
    finally:
        monitor.end_pipeline_run(run_id, 'success' if 'data' in locals() else 'failed')
```

This comprehensive guide covers data pipeline fundamentals, implementation with major orchestration tools (Airflow, Prefect, Dagster), data quality frameworks, and monitoring systems. The code examples demonstrate production-ready implementations for ETL/ELT pipelines with proper error handling, monitoring, and alerting capabilities.
