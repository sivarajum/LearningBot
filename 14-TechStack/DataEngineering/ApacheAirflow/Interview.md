# Apache Airflow Data Engineering Interview Questions & Answers

## Beginner Level Questions

### 1. What is Apache Airflow and why is it used in data engineering?
**Answer:** Apache Airflow is an open-source platform for programmatically authoring, scheduling, and monitoring workflows. It's designed to handle complex computational workflows and data processing pipelines.

**Key Uses in Data Engineering:**
- **ETL Pipeline Orchestration**: Automate extract, transform, load processes
- **Data Pipeline Scheduling**: Run pipelines on schedules or triggers
- **Dependency Management**: Handle complex task relationships and dependencies
- **Monitoring and Alerting**: Track pipeline health and send notifications
- **Workflow as Code**: Define pipelines programmatically for version control

**Basic Example:**
```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG('simple_etl', start_date=datetime(2023, 1, 1))

extract = BashOperator(
    task_id='extract',
    bash_command='echo "Extracting data"',
    dag=dag
)

transform = BashOperator(
    task_id='transform',
    bash_command='echo "Transforming data"',
    dag=dag
)

extract >> transform  # Set dependency
```

### 2. Explain the basic components of an Airflow DAG.
**Answer:** A DAG (Directed Acyclic Graph) is the core concept in Airflow, representing a workflow as a collection of tasks with dependencies.

**Essential Components:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# 1. DAG Definition
dag = DAG(
    'example_dag',                          # Unique DAG identifier
    start_date=datetime(2023, 1, 1),       # When DAG starts being scheduled
    schedule_interval='@daily',             # How often to run (cron syntax)
    catchup=False,                          # Whether to backfill missed runs
    default_args={                          # Default arguments for all tasks
        'owner': 'data_team',
        'retries': 3,
        'retry_delay': timedelta(minutes=5)
    }
)

# 2. Tasks (using Operators)
def extract_data():
    print("Extracting data from source")
    return "extracted_data"

extract_task = PythonOperator(
    task_id='extract',                      # Unique task identifier
    python_callable=extract_data,           # Function to execute
    dag=dag                                 # DAG this task belongs to
)

# 3. Dependencies (create the graph)
extract_task >> transform_task >> load_task
```

**Key Properties:**
- **dag_id**: Unique identifier for the DAG
- **start_date**: Earliest date for DAG runs
- **schedule_interval**: How often the DAG runs
- **catchup**: Whether to run missed intervals
- **default_args**: Common arguments for all tasks

### 3. What are Operators in Airflow and give examples?
**Answer:** Operators are the building blocks of Airflow tasks. They define what actually gets executed when a task runs.

**Types of Operators:**

**Action Operators:**
```python
# BashOperator - Execute bash commands
bash_task = BashOperator(
    task_id='run_script',
    bash_command='python /path/to/script.py --date {{ ds }}',
    dag=dag
)

# PythonOperator - Execute Python functions
def process_data(**context):
    import pandas as pd
    df = pd.read_csv('/data/input.csv')
    # Process data
    return 'Processed'

python_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag
)

# EmailOperator - Send emails
email_task = EmailOperator(
    task_id='send_alert',
    to='team@company.com',
    subject='Pipeline Complete',
    html_content='<h3>ETL finished successfully</h3>',
    dag=dag
)
```

**Transfer Operators:**
```python
# Move data between systems
from airflow.providers.postgres.operators.postgres import PostgresOperator

postgres_task = PostgresOperator(
    task_id='run_query',
    postgres_conn_id='my_postgres',
    sql='SELECT COUNT(*) FROM users;',
    dag=dag
)
```

**Sensor Operators:**
```python
# Wait for conditions
from airflow.sensors.filesystem import FileSensor

file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,      # Give up after 1 hour
    dag=dag
)
```

## Intermediate Level Questions

### 4. How do you handle task dependencies in Airflow?
**Answer:** Task dependencies define the execution order and relationships between tasks in a DAG.

**Setting Dependencies:**
```python
# Method 1: Bitshift operators (most common)
task1 >> task2 >> task3  # Linear chain

# Method 2: set_downstream / set_upstream
task1.set_downstream(task2)
task3.set_upstream(task1)

# Method 3: Chain utility
from airflow.utils.helpers import chain
chain(task1, task2, task3)
```

**Complex Dependency Patterns:**
```python
# Fan-out pattern (one task to many)
extract >> [transform1, transform2, transform3]

# Fan-in pattern (many tasks to one)
[transform1, transform2, transform3] >> load

# Diamond pattern
extract >> validate
validate >> [clean_data, enrich_data]
[clean_data, enrich_data] >> merge >> load

# Cross-dependencies
start >> extract_customers
start >> extract_orders
extract_customers >> transform_customers
extract_orders >> transform_orders
[transform_customers, transform_orders] >> create_reports
```

**Trigger Rules:**
```python
from airflow.utils.trigger_rule import TriggerRule

# Run only if all upstream tasks succeed (default)
normal_task = BashOperator(
    task_id='normal_task',
    bash_command='echo "Success"',
    dag=dag
)

# Run only if upstream task fails
cleanup_task = BashOperator(
    task_id='cleanup',
    bash_command='rm -rf /tmp/temp_data',
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag
)

# Run regardless of upstream status
always_run_task = BashOperator(
    task_id='always_run',
    bash_command='echo "Pipeline finished"',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag
)

failed_task >> cleanup_task
[normal_task, cleanup_task] >> always_run_task
```

### 5. Explain XComs and how to use them for inter-task communication.
**Answer:** XComs (Cross-Communications) allow tasks to exchange small amounts of data.

**Basic XCom Usage:**
```python
def producer_task(**context):
    # Push data to XCom
    context['ti'].xcom_push(key='my_data', value='Hello from producer')
    context['ti'].xcom_pull(key='rows_processed', task_ids='other_task')
    return 'Task completed'

def consumer_task(**context):
    # Pull data from XCom
    ti = context['ti']
    data = ti.xcom_pull(key='my_data', task_ids='producer_task')
    print(f"Received: {data}")
    return f"Processed: {data}"

producer = PythonOperator(
    task_id='producer',
    python_callable=producer_task,
    provide_context=True,
    dag=dag
)

consumer = PythonOperator(
    task_id='consumer',
    python_callable=consumer_task,
    provide_context=True,
    dag=dag
)

producer >> consumer
```

**XCom Best Practices:**
```python
# Use descriptive keys
context['ti'].xcom_push(key='processed_file_path', value='/data/output.csv')
context['ti'].xcom_push(key='records_count', value=1000)

# Don't store large data in XCom
# Store file paths instead of file contents
# Store metadata instead of actual data

# Clean up XComs when done
def cleanup_xcom(**context):
    ti = context['ti']
    # Remove large data
    ti.xcom_push(key='large_dataset', value=None)

# Use XCom for coordination, not data transfer
# Good: File paths, row counts, status flags
# Bad: Large DataFrames, binary data
```

**Advanced XCom Patterns:**
```python
# Pull from multiple tasks
def aggregate_results(**context):
    ti = context['ti']

    # Get results from multiple upstream tasks
    results = []
    upstream_tasks = ['task1', 'task2', 'task3']

    for task_id in upstream_tasks:
        result = ti.xcom_pull(key='result', task_ids=task_id)
        if result:
            results.append(result)

    # Aggregate and return
    return sum(results)

# Conditional logic based on XCom
def conditional_task(**context):
    ti = context['ti']
    status = ti.xcom_pull(key='validation_status', task_ids='validate')

    if status == 'PASSED':
        # Proceed with processing
        return 'Continue processing'
    else:
        # Handle validation failure
        raise Exception('Validation failed')
```

### 6. How do you handle errors and retries in Airflow?
**Answer:** Airflow provides robust error handling and retry mechanisms.

**Task-Level Retry Configuration:**
```python
# Configure retries in default_args
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30)
}

# Override for specific tasks
critical_task = BashOperator(
    task_id='critical_task',
    bash_command='high_risk_command',
    retries=5,
    retry_delay=timedelta(seconds=30),
    dag=dag
)
```

**Error Handling Patterns:**
```python
# Callback functions
def failure_callback(context):
    task_instance = context['task_instance']

    # Log failure details
    print(f"Task {task_instance.task_id} failed")

    # Send alert
    send_alert_email(
        subject=f"Task Failed: {task_instance.task_id}",
        body=f"DAG: {task_instance.dag_id}\nTask: {task_instance.task_id}\nExecution Date: {context['execution_date']}"
    )

def success_callback(context):
    print(f"Task {context['task_instance'].task_id} completed successfully")

task = PythonOperator(
    task_id='error_prone_task',
    python_callable=my_function,
    on_failure_callback=failure_callback,
    on_success_callback=success_callback,
    dag=dag
)
```

**Exception Handling in Tasks:**
```python
def robust_task(**context):
    try:
        # Main processing logic
        result = process_data()

        # Validate result
        if not result:
            raise ValueError("Processing returned empty result")

        return result

    except FileNotFoundError as e:
        print(f"Input file not found: {e}")
        raise  # Re-raise to trigger retry

    except ValueError as e:
        print(f"Validation error: {e}")
        # Custom handling for validation errors
        context['ti'].xcom_push(key='error_type', value='validation')
        raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Log to external system
        log_to_monitoring_system(error=str(e))
        raise

task = PythonOperator(
    task_id='robust_task',
    python_callable=robust_task,
    provide_context=True,
    dag=dag
)
```

**Deadlock and Timeout Handling:**
```python
# Task timeout
long_running_task = BashOperator(
    task_id='long_task',
    bash_command='sleep 3600',  # 1 hour
    execution_timeout=timedelta(minutes=30),  # Kill after 30 minutes
    dag=dag
)

# SLA (Service Level Agreement)
dag = DAG(
    'sla_dag',
    sla_miss_callback=sla_miss_callback,
    default_args={
        'sla': timedelta(hours=2)  # Expected completion time
    }
)

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    # Handle SLA violations
    send_sla_alert(dag.dag_id, task_list)
```

### 7. Explain Airflow Variables and Connections.
**Answer:** Variables and Connections provide configuration management for Airflow deployments.

**Airflow Variables:**
```python
from airflow.models import Variable

# Set variables (via UI or CLI)
# airflow variables set my_var "my_value"

# Get variables in code
my_var = Variable.get("my_var")
db_host = Variable.get("database_host", default_var="localhost")

# JSON variables
config = Variable.get("pipeline_config", deserialize_json=True)
# {"batch_size": 1000, "timeout": 300}

# Use in operators
bash_task = BashOperator(
    task_id='use_variable',
    bash_command=f'echo {Variable.get("my_message")}',
    dag=dag
)

# Variable types
string_var = Variable.get("string_var")  # String
int_var = int(Variable.get("int_var"))   # Convert to int
bool_var = Variable.get("bool_var").lower() == 'true'  # Convert to bool
```

**Airflow Connections:**
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

# Use connections in operators
from airflow.providers.postgres.operators.postgres import PostgresOperator

postgres_task = PostgresOperator(
    task_id='run_query',
    postgres_conn_id='my_postgres',
    sql='SELECT COUNT(*) FROM users;',
    dag=dag
)

# Access connection details in Python
def use_connection(**context):
    from airflow.hooks.base import BaseHook

    conn = BaseHook.get_connection('my_postgres')
    print(f"Host: {conn.host}")
    print(f"Schema: {conn.schema}")

    # Use connection for custom logic
    # conn.login, conn.password, etc.
```

**Best Practices:**
```python
# Use descriptive names
# my_postgres_prod vs postgres_conn

# Store sensitive data in connections, not variables
# Passwords in connections, configuration in variables

# Environment-specific connections
# dev_postgres, staging_postgres, prod_postgres

# Test connections
from airflow.utils.db import provide_session

@provide_session
def test_connection(session=None):
    from airflow.models import Connection

    conn = session.query(Connection).filter(
        Connection.conn_id == 'my_postgres'
    ).first()

    if not conn:
        raise Exception("Connection not found")
```

## Advanced Level Questions

### 8. How do you implement dynamic DAGs in Airflow?
**Answer:** Dynamic DAGs allow creating DAGs programmatically based on configuration or external data.

**Configuration-Driven DAGs:**
```python
# config.yaml
pipelines:
  - name: customer_pipeline
    schedule: "@daily"
    tasks:
      - name: extract
        type: bash
        command: "echo extract customers"
      - name: transform
        type: python
        function: transform_customers
      - name: load
        type: bash
        command: "echo load customers"

  - name: product_pipeline
    schedule: "@hourly"
    tasks:
      - name: extract
        type: bash
        command: "echo extract products"
      - name: load
        type: bash
        command: "echo load products"

# Dynamic DAG creation
import yaml
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

def create_dag_from_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    dags = []

    for pipeline_config in config['pipelines']:
        dag = DAG(
            dag_id=pipeline_config['name'],
            start_date=datetime(2023, 1, 1),
            schedule_interval=pipeline_config['schedule'],
            catchup=False
        )

        previous_task = None

        for task_config in pipeline_config['tasks']:
            if task_config['type'] == 'bash':
                task = BashOperator(
                    task_id=task_config['name'],
                    bash_command=task_config['command'],
                    dag=dag
                )
            elif task_config['type'] == 'python':
                task = PythonOperator(
                    task_id=task_config['name'],
                    python_callable=globals()[task_config['function']],
                    dag=dag
                )

            if previous_task:
                previous_task >> task
            previous_task = task

        dags.append(dag)

    return dags

# Create DAGs
dags = create_dag_from_config('/path/to/config.yaml')

# Register DAGs globally
for dag in dags:
    globals()[dag.dag_id] = dag
```

**Database-Driven DAGs:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd

def get_pipeline_configs():
    # Query database for pipeline configurations
    query = """
    SELECT pipeline_name, schedule_interval, task_sequence
    FROM pipeline_configs
    WHERE active = true
    """

    # Return list of pipeline configs
    return [
        {
            'name': 'dynamic_pipeline_1',
            'schedule': '@daily',
            'tasks': ['extract', 'transform', 'load']
        }
    ]

def create_dynamic_dags():
    configs = get_pipeline_configs()
    dags = []

    for config in configs:
        dag = DAG(
            dag_id=config['name'],
            start_date=datetime(2023, 1, 1),
            schedule_interval=config['schedule'],
            catchup=False
        )

        # Create tasks based on configuration
        tasks = {}
        for task_name in config['tasks']:
            task = PythonOperator(
                task_id=task_name,
                python_callable=globals()[f'{task_name}_function'],
                dag=dag
            )
            tasks[task_name] = task

        # Set dependencies
        if 'extract' in tasks and 'transform' in tasks:
            tasks['extract'] >> tasks['transform']
        if 'transform' in tasks and 'load' in tasks:
            tasks['transform'] >> tasks['load']

        dags.append(dag)

    return dags

# Generate DAGs
dynamic_dags = create_dynamic_dags()
for dag in dynamic_dags:
    globals()[dag.dag_id] = dag
```

### 9. Explain Task Groups and when to use them.
**Answer:** Task Groups organize related tasks into collapsible groups for better DAG visualization and management.

**Basic Task Groups:**
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

        # Set dependencies within group
        extract >> validate >> transform >> load

    return tg

# Use task groups
customers_etl = create_etl_group('customers_etl', 'customers')
orders_etl = create_etl_group('orders_etl', 'orders')

# Set dependencies between groups
start >> [customers_etl, orders_etl] >> end
```

**Nested Task Groups:**
```python
def create_data_pipeline():
    with TaskGroup('data_pipeline', dag=dag) as pipeline_group:

        # Extract phase
        with TaskGroup('extract_phase') as extract_group:
            extract_customers = DummyOperator(task_id='extract_customers')
            extract_orders = DummyOperator(task_id='extract_orders')
            extract_products = DummyOperator(task_id='extract_products')

        # Transform phase
        with TaskGroup('transform_phase') as transform_group:
            transform_customers = DummyOperator(task_id='transform_customers')
            transform_orders = DummyOperator(task_id='transform_orders')
            transform_products = DummyOperator(task_id='transform_products')

        # Load phase
        with TaskGroup('load_phase') as load_group:
            load_customers = DummyOperator(task_id='load_customers')
            load_orders = DummyOperator(task_id='load_orders')
            load_products = DummyOperator(task_id='load_products')

        # Set dependencies between phases
        extract_group >> transform_group >> load_group

        # Set dependencies within phases
        [extract_customers, extract_orders, extract_products] >> transform_group
        transform_group >> [load_customers, load_orders, load_products]

    return pipeline_group

pipeline = create_data_pipeline()
start >> pipeline >> end
```

**Task Group Benefits:**
- **Organization**: Logical grouping of related tasks
- **Visualization**: Cleaner DAG view in UI
- **Reusability**: Create reusable pipeline components
- **Maintenance**: Easier to modify related tasks together
- **Parallelism**: Control parallelism at group level

**When to Use Task Groups:**
- Complex DAGs with many tasks
- Reusable pipeline patterns
- Logical separation of concerns
- Teams working on different pipeline stages
- Better organization for large workflows

### 10. How do you implement data quality checks in Airflow?
**Answer:** Data quality checks ensure pipeline reliability and data integrity.

**Custom Data Quality Operator:**
```python
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import Dict, Any
import pandas as pd

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
            return self._check_row_count(check_config)
        elif check_name == 'null_check':
            return self._check_null_values(check_config)
        elif check_name == 'duplicate_check':
            return self._check_duplicates(check_config)
        # Add more checks as needed

    def _check_row_count(self, config):
        # Implementation for row count check
        min_rows = config.get('min_rows', 0)
        # Query database and check count
        return {'passed': True, 'message': f'Row count >= {min_rows}'}

    def _check_null_values(self, config):
        # Implementation for null check
        columns = config.get('columns', [])
        # Check null values in specified columns
        return {'passed': True, 'message': 'No null values found'}

    def _check_duplicates(self, config):
        # Implementation for duplicate check
        columns = config.get('columns', [])
        # Check for duplicates
        return {'passed': True, 'message': 'No duplicates found'}

# Usage
quality_check = DataQualityOperator(
    task_id='check_data_quality',
    table_name='customers',
    quality_checks={
        'row_count': {'min_rows': 1000},
        'null_check': {'columns': ['customer_id', 'email']},
        'duplicate_check': {'columns': ['customer_id']}
    },
    dag=dag
)
```

**Great Expectations Integration:**
```python
def run_ge_checks(**context):
    import great_expectations as ge

    # Load data
    df = pd.read_csv('/data/input.csv')

    # Create GE dataframe
    df_ge = ge.from_pandas(df)

    # Define expectations
    expectations = [
        df_ge.expect_column_values_to_not_be_null('customer_id'),
        df_ge.expect_column_values_to_be_between('amount', 0, 10000),
        df_ge.expect_column_proportion_of_unique_values_to_be_between('customer_id', 0.9, 1.0)
    ]

    # Run validations
    results = [exp.run() for exp in expectations]
    failed = [r for r in results if not r.success]

    if failed:
        raise Exception(f"Data quality checks failed: {len(failed)} expectations not met")

    return "Data quality checks passed"

ge_check = PythonOperator(
    task_id='great_expectations_check',
    python_callable=run_ge_checks,
    dag=dag
)
```

### 11. Explain different Airflow Executors and when to use them.
**Answer:** Executors determine how tasks are executed in Airflow.

**SequentialExecutor:**
```python
# airflow.cfg
[core]
executor = SequentialExecutor

# Characteristics:
# - Runs one task at a time
# - Simple, no external dependencies
# - Good for development/testing
# - Not suitable for production

# When to use:
# - Local development
# - Testing DAGs
# - Simple workflows
# - Resource-constrained environments
```

**LocalExecutor:**
```python
# airflow.cfg
[core]
executor = LocalExecutor

# Characteristics:
# - Runs tasks in parallel on local machine
# - Uses multiprocessing
# - Good for small-scale production
# - Limited by local machine resources

# When to use:
# - Single machine deployment
# - Moderate parallelism needs
# - Cost-effective for small teams
```

**CeleryExecutor:**
```python
# airflow.cfg
[core]
executor = CeleryExecutor
[celery]
broker_url = redis://localhost:6379/0
result_backend = db+postgresql://airflow:airflow@localhost/airflow

# Characteristics:
# - Distributed execution
# - Horizontal scaling
# - Message queue based
# - Fault tolerant

# When to use:
# - Large-scale production
# - High parallelism requirements
# - Multiple worker machines
# - 24/7 operation requirements
```

**KubernetesExecutor:**
```python
# airflow.cfg
[core]
executor = KubernetesExecutor
[kubernetes]
namespace = airflow
worker_container_repository = apache/airflow
worker_container_tag = 2.5.0

# Characteristics:
# - Container-based execution
# - Auto-scaling workers
# - Kubernetes native
# - Resource isolation

# When to use:
# - Kubernetes environments
# - Dynamic scaling needs
# - Multi-tenant deployments
# - Cloud-native architectures
```

**Executor Comparison:**
```python
# Decision factors:
# - Scale requirements
# - Infrastructure preferences
# - Operational complexity
# - Cost considerations

# SequentialExecutor: Development, testing, simple workflows
# LocalExecutor: Small production, single machine
# CeleryExecutor: Large production, distributed workers
# KubernetesExecutor: Cloud-native, containerized, auto-scaling
```

### 12. How do you monitor and troubleshoot Airflow pipelines?
**Answer:** Monitoring and troubleshooting are crucial for production Airflow deployments.

**Web UI Monitoring:**
```python
# Key UI sections:
# - DAGs view: Overall DAG status
# - Tree view: Task status over time
# - Graph view: Task dependencies
# - Task Duration: Performance monitoring
# - Gantt view: Timeline visualization
# - Variable/Connection views: Configuration

# Status indicators:
# - Success: Green
# - Failed: Red
# - Running: Blue
# - Queued: Gray
# - Up for retry: Yellow
```

**Logging and Debugging:**
```python
# Task logging
def debug_task(**context):
    import logging
    logger = logging.getLogger(__name__)

    logger.info("Starting task execution")
    logger.debug(f"Context: {context}")

    try:
        result = process_data()
        logger.info(f"Task completed successfully. Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        raise

task = PythonOperator(
    task_id='debug_task',
    python_callable=debug_task,
    dag=dag
)

# Log location: /opt/airflow/logs/dag_id/task_id/execution_date.log
```

**Performance Monitoring:**
```python
# Task duration monitoring
from airflow.utils.db import provide_session

@provide_session
def get_slow_tasks(session=None):
    # Query for slow-running tasks
    query = """
    SELECT dag_id, task_id, AVG(duration) as avg_duration
    FROM task_instance
    WHERE state = 'success'
      AND execution_date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY dag_id, task_id
    HAVING AVG(duration) > 300  -- 5 minutes
    ORDER BY avg_duration DESC
    """

    return session.execute(query).fetchall()

# SLA monitoring
dag = DAG(
    'sla_monitored_dag',
    sla_miss_callback=lambda dag, **kwargs: send_sla_alert(dag.dag_id),
    default_args={
        'sla': timedelta(hours=2)
    }
)
```

**Troubleshooting Common Issues:**
```python
# 1. DAG not appearing in UI
# - Check DAG folder path
# - Verify Python syntax
# - Check scheduler logs

# 2. Tasks stuck in queued state
# - Check executor configuration
# - Verify worker processes running
# - Check queue backend connectivity

# 3. Import errors
# - Check Python path
# - Verify dependencies installed
# - Check custom module locations

# 4. Task failures
# - Check task logs
# - Verify connections working
# - Test task logic independently

# 5. Performance issues
# - Monitor task durations
# - Check resource utilization
# - Optimize query performance
# - Consider task parallelism
```

**Alerting Setup:**
```python
# Email alerts
from airflow.operators.email import EmailOperator

def failure_alert(context):
    task_instance = context['task_instance']

    alert = EmailOperator(
        task_id='failure_alert',
        to=['team@company.com'],
        subject=f'Airflow Task Failed: {task_instance.task_id}',
        html_content=f"""
        <h3>Task Failure Alert</h3>
        <p><strong>DAG:</strong> {task_instance.dag_id}</p>
        <p><strong>Task:</strong> {task_instance.task_id}</p>
        <p><strong>Execution Date:</strong> {context['execution_date']}</p>
        <p><strong>Log URL:</strong> {task_instance.log_url}</p>
        """,
        dag=dag
    )

    alert.execute(context)

task = PythonOperator(
    task_id='monitored_task',
    python_callable=my_function,
    on_failure_callback=failure_alert,
    dag=dag
)
```

## Scenario-Based Questions

### 13. How would you design a real-time data pipeline using Airflow?
**Answer:** Designing a real-time pipeline with Airflow requires careful consideration of scheduling and data flow patterns.

**Near Real-Time Pipeline Design:**
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

# High-frequency DAG for near real-time processing
dag = DAG(
    'realtime_pipeline',
    start_date=datetime(2023, 1, 1),
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    catchup=False,
    max_active_runs=1,  # Only one instance running
    concurrency=5  # Allow parallel tasks
)

def ingest_streaming_data(**context):
    """Ingest data from streaming sources (Kafka, Kinesis, etc.)"""
    # Connect to streaming source
    # Process micro-batches
    # Store in staging area
    pass

def validate_realtime_data(**context):
    """Lightweight validation for speed"""
    # Basic checks only (not comprehensive validation)
    # Flag suspicious data for later review
    pass

def enrich_realtime_data(**context):
    """Add reference data and enrichments"""
    # Join with dimension tables
    # Add calculated fields
    # Minimal transformations for speed
    pass

def load_realtime_warehouse(**context):
    """Load to real-time serving layer"""
    # Load to Redis/Elasticsearch
    # Update real-time dashboards
    # Trigger downstream alerts
    pass

# Tasks
ingest = PythonOperator(
    task_id='ingest_streaming',
    python_callable=ingest_streaming_data,
    execution_timeout=timedelta(minutes=10),
    dag=dag
)

validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_realtime_data,
    dag=dag
)

enrich = PythonOperator(
    task_id='enrich_data',
    python_callable=enrich_realtime_data,
    dag=dag
)

load = PythonOperator(
    task_id='load_realtime',
    python_callable=load_realtime_warehouse,
    dag=dag
)

# Dependencies
ingest >> validate >> enrich >> load
```

**Real-Time Considerations:**
```python
# 1. Frequent Scheduling
# Use short intervals: '*/5 * * * *' (every 5 minutes)
# Consider sensor-based triggering for event-driven pipelines

# 2. Idempotent Operations
def idempotent_load(**context):
    """Ensure operations can be rerun safely"""
    execution_date = context['execution_date']

    # Use execution_date as watermark
    # Check for existing data before processing
    # Implement upsert logic
    pass

# 3. Error Handling for Real-Time
def realtime_error_handler(**context):
    """Handle errors without stopping pipeline"""
    try:
        # Main processing
        process_realtime_data()
    except Exception as e:
        # Log error but don't fail DAG
        log_error(e)

        # Store failed records for later processing
        quarantine_failed_records()

        # Continue with next batch
        return 'partial_success'

# 4. Monitoring for Real-Time SLAs
def check_realtime_sla(**context):
    """Monitor data freshness"""
    last_update = get_last_update_time()
    now = datetime.now()

    latency = (now - last_update).total_seconds()

    if latency > 300:  # 5 minutes SLA
        send_sla_alert(f"Data latency: {latency} seconds")

    return latency
```

**Hybrid Approach (Real-Time + Batch):**
```python
# Real-time pipeline for immediate insights
realtime_dag = DAG('realtime_insights', schedule_interval='*/5 * * * *')

# Batch pipeline for comprehensive processing
batch_dag = DAG('batch_processing', schedule_interval='@hourly')

# Coordination between pipelines
batch_wait_sensor = ExternalTaskSensor(
    task_id='wait_for_batch_completion',
    external_dag_id='batch_processing',
    external_task_id='final_load',
    execution_delta=timedelta(hours=1),  # Wait for previous hour's batch
    dag=realtime_dag
)

# Real-time depends on batch completion for reference data
batch_wait_sensor >> realtime_processing_task
```

### 14. How do you implement CI/CD for Airflow DAGs?
**Answer:** Implementing CI/CD ensures reliable DAG deployment and testing.

**Git-Based Workflow:**
```bash
# Repository structure
airflow-dags/
├── dags/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── utils.py
│   │   └── constants.py
│   ├── pipeline1.py
│   ├── pipeline2.py
│   └── __init__.py
├── tests/
│   ├── test_pipeline1.py
│   ├── test_pipeline2.py
│   └── conftest.py
├── requirements.txt
└── Dockerfile
```

**Testing Strategy:**
```python
# tests/test_pipeline1.py
import pytest
from datetime import datetime
from airflow import DAG
from dags.pipeline1 import create_pipeline_dag

class TestPipeline1:

    def test_dag_creation(self):
        """Test DAG is created correctly"""
        dag = create_pipeline_dag()

        assert dag.dag_id == 'pipeline1'
        assert len(dag.tasks) == 3  # extract, transform, load

        # Check task dependencies
        extract_task = dag.get_task('extract')
        transform_task = dag.get_task('transform')
        load_task = dag.get_task('load')

        assert transform_task in extract_task.downstream_list
        assert load_task in transform_task.downstream_list

    def test_task_execution(self, mocker):
        """Test individual task logic"""
        mock_extract = mocker.patch('dags.pipeline1.extract_data')
        mock_extract.return_value = 'test_data'

        # Test extract function
        result = extract_data()
        assert result == 'test_data'
        mock_extract.assert_called_once()

    @pytest.mark.parametrize("input_data,expected", [
        ({'amount': 100}, {'amount': 100, 'category': 'small'}),
        ({'amount': 1000}, {'amount': 1000, 'category': 'medium'}),
        ({'amount': 10000}, {'amount': 10000, 'category': 'large'})
    ])
    def test_data_transformation(self, input_data, expected):
        """Test transformation logic with multiple scenarios"""
        result = transform_data(input_data)
        assert result == expected

# conftest.py
import pytest
from airflow import settings
from airflow.utils.db import initdb

@pytest.fixture(scope="session", autouse=True)
def initialize_airflow_db():
    """Initialize Airflow database for testing"""
    initdb()
    yield
    # Cleanup if needed
```

**CI/CD Pipeline (GitHub Actions):**
```yaml
# .github/workflows/ci-cd.yml
name: Airflow DAGs CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest tests/ --cov=dags/ --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Deploy to staging
      run: |
        # Copy DAGs to staging environment
        scp -r dags/ user@staging-airflow:/opt/airflow/dags/

        # Restart scheduler and webserver
        ssh user@staging-airflow "docker-compose restart scheduler webserver"

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    environment: production

    steps:
    - uses: actions/checkout@v2

    - name: Deploy to production
      run: |
        # Backup current DAGs
        ssh user@prod-airflow "cp -r /opt/airflow/dags /opt/airflow/dags.backup"

        # Deploy new DAGs
        scp -r dags/ user@prod-airflow:/opt/airflow/dags/

        # Validate DAGs
        ssh user@prod-airflow "python -c 'from airflow.utils.dag_processing import list_py_file_paths; print(list_py_file_paths(\"/opt/airflow/dags\"))'"

        # Restart services
        ssh user@prod-airflow "docker-compose restart scheduler webserver"

        # Rollback on failure
        # ssh user@prod-airflow "if [ \$? -ne 0 ]; then mv /opt/airflow/dags.backup /opt/airflow/dags; docker-compose restart scheduler webserver; fi"
```

**Deployment Best Practices:**
```python
# Version control for DAGs
# Include version in DAG ID for compatibility
dag = DAG(
    f'pipeline_v2.1.0_{datetime.now().strftime("%Y%m%d")}',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily'
)

# Feature flags for gradual rollout
USE_NEW_FEATURE = Variable.get('use_new_feature', default_var='false').lower() == 'true'

if USE_NEW_FEATURE:
    # New implementation
    new_task = PythonOperator(task_id='new_task', ...)
else:
    # Old implementation
    old_task = PythonOperator(task_id='old_task', ...)

# DAG versioning and compatibility
# Test DAGs in isolated environment before production
# Implement canary deployments for critical pipelines
# Monitor DAG parsing errors and task failures post-deployment
```

## Summary

Airflow interview questions cover:

- **Core Concepts**: DAGs, tasks, operators, dependencies
- **Execution**: Executors, scheduling, error handling
- **Communication**: XComs, variables, connections
- **Advanced Features**: Dynamic DAGs, task groups, custom operators
- **Production**: Monitoring, troubleshooting, CI/CD
- **Real-Time**: Streaming data pipelines, SLA monitoring
- **Quality**: Data validation, testing strategies

Key areas to master:
- **DAG Design**: Proper structure, dependencies, error handling
- **Operators**: Choosing right operators for different use cases
- **Execution Models**: Understanding different executors and their use cases
- **Monitoring**: UI usage, logging, alerting, troubleshooting
- **Production Deployment**: Scaling, reliability, CI/CD integration
- **Data Quality**: Validation, testing, quality gates

Understanding these concepts enables building robust, scalable data pipelines that can handle complex business requirements while maintaining reliability and observability in production environments.
