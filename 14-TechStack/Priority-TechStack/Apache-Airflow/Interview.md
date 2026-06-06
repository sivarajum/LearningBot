# Apache Airflow - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your Airflow interviews. Critical for data pipeline orchestration roles.

---

## 🟢 BASIC LEVEL Questions (5-8 questions)

### Q1: What is Apache Airflow and why is it important?

**Answer:**
"Apache Airflow is an open-source platform for programmatically authoring, scheduling, and monitoring workflows. It's the industry standard for data pipeline orchestration, used by 80%+ of data engineering teams.

**Why Airflow?**
1. **Workflow Orchestration**: Define complex DAGs with dependencies
2. **Scheduling**: Cron-like scheduling with timezone support
3. **Monitoring**: Built-in UI for real-time monitoring
4. **Extensible**: 200+ operators and hooks for various systems
5. **Python-Native**: Code-as-configuration approach
6. **Scalable**: Supports distributed execution with multiple executors

**Real-world use:**
I use Airflow to orchestrate ETL pipelines, scheduling daily data processing jobs with complex dependencies, error handling, and monitoring. For example, I built a pipeline that extracts data from 5 different sources, transforms it in parallel, and loads it into a data warehouse with data quality checks."

**Key Points:**
- Workflow orchestration platform
- DAG-based workflow definition
- Scheduling and monitoring
- Industry standard tool

---

### Q2: What is a DAG? Explain with an example.

**Answer:**
"DAG stands for Directed Acyclic Graph. It's a workflow definition in Airflow that represents tasks and their dependencies.

**Properties:**
- **Directed**: Tasks have dependencies (arrows show execution flow)
- **Acyclic**: No cycles (can't loop back to previous tasks)
- **Graph**: Network of tasks connected by dependencies

**Example:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG('etl_pipeline', schedule_interval='@daily')

extract = PythonOperator(task_id='extract', python_callable=extract_data, dag=dag)
transform = PythonOperator(task_id='transform', python_callable=transform_data, dag=dag)
load = PythonOperator(task_id='load', python_callable=load_data, dag=dag)

extract >> transform >> load
```

**Why DAGs?**
- Visual representation of workflow
- Automatic dependency management
- Enables parallel execution
- Built-in error handling and retries

I define DAGs to represent data pipelines, with tasks for extract, transform, and load operations, ensuring proper execution order."

**Key Points:**
- Directed Acyclic Graph
- Task dependencies
- No cycles allowed
- Workflow definition

---

### Q3: What are operators in Airflow? Name the most common ones.

**Answer:**
"Operators define what a task does. They're reusable components that encapsulate work units.

**Most Common Operators:**

1. **PythonOperator**: Execute Python functions
```python
def my_function():
    print("Hello from Airflow")

task = PythonOperator(
    task_id='python_task',
    python_callable=my_function,
    dag=dag
)
```

2. **BashOperator**: Execute bash commands
```python
task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World"',
    dag=dag
)
```

3. **SQLOperator**: Execute SQL queries
```python
task = SqlOperator(
    task_id='sql_task',
    sql='SELECT * FROM table',
    dag=dag
)
```

4. **Sensor**: Wait for conditions (files, APIs, databases)
```python
file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input.csv',
    poke_interval=60,
    dag=dag
)
```

**Benefits:**
- Reusable components
- Type-specific operations
- Easy to extend
- Rich ecosystem (200+ operators)

I use PythonOperator for data processing, BashOperator for file operations, Sensors for waiting on external conditions, and custom operators for specific use cases."

**Key Points:**
- Define task behavior
- Type-specific operations
- Reusable components
- Extensible framework

---

### Q4: How does Airflow scheduling work?

**Answer:**
"Airflow scheduling determines when DAGs run based on schedule_interval.

**Scheduling Options:**

1. **Cron Expressions**: `0 0 * * *` (daily at midnight)
```python
dag = DAG('daily_dag', schedule_interval='0 0 * * *')
```

2. **Preset Strings**: `@daily`, `@hourly`, `@weekly`
```python
dag = DAG('daily_dag', schedule_interval='@daily')
```

3. **Timedelta**: `timedelta(days=1)`
```python
from datetime import timedelta
dag = DAG('daily_dag', schedule_interval=timedelta(days=1))
```

4. **None**: Manual trigger only
```python
dag = DAG('manual_dag', schedule_interval=None)
```

**Key Concepts:**
- **start_date**: When DAG starts running
- **schedule_interval**: How often to run
- **catchup**: Whether to backfill missed runs
- **max_active_runs**: Limit concurrent DAG runs

**Example:**
```python
dag = DAG(
    'my_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False,  # Don't backfill
    max_active_runs=1
)
```

I configure scheduling based on business requirements - daily for reports, hourly for real-time data, and manual triggers for ad-hoc analysis."

**Key Points:**
- Cron expressions or presets
- start_date and schedule_interval
- catchup for backfilling
- max_active_runs for concurrency

---

### Q5: What is the Airflow UI and what can you do with it?

**Answer:**
"The Airflow UI is a web-based interface for monitoring and managing workflows.

**Key Features:**

1. **DAG View**: See all DAGs, their status, and schedules
2. **Tree View**: Visual representation of task dependencies
3. **Graph View**: Interactive DAG visualization
4. **Task Instance Details**: Logs, duration, retries
5. **Gantt Chart**: Timeline view of task execution
6. **Code View**: View DAG source code
7. **Admin**: Manage users, connections, variables

**Common Operations:**
- Trigger DAG runs manually
- View task logs
- Monitor task status
- Rerun failed tasks
- Clear task states
- View task duration and performance

**Access:**
```bash
airflow webserver --port 8080
# Access at http://localhost:8080
```

I use the UI daily to monitor pipeline health, debug failures, view logs, and trigger manual runs for testing."

**Key Points:**
- Web-based monitoring interface
- DAG visualization
- Task management
- Log viewing

---

### Q6: Explain the difference between a task and a DAG.

**Answer:**
"**DAG (Directed Acyclic Graph):**
- Workflow definition containing multiple tasks
- Defines overall pipeline structure
- Has schedule, start_date, and metadata
- Example: ETL pipeline DAG

**Task:**
- Individual work unit within a DAG
- Executes a specific operation
- Defined by an operator
- Has dependencies on other tasks
- Example: Extract task, Transform task

**Relationship:**
```python
dag = DAG('etl_pipeline')  # DAG definition

extract = PythonOperator(task_id='extract', ...)  # Task 1
transform = PythonOperator(task_id='transform', ...)  # Task 2
load = PythonOperator(task_id='load', ...)  # Task 3

extract >> transform >> load  # Tasks with dependencies in DAG
```

**Analogy:**
- DAG = Recipe (overall workflow)
- Task = Ingredient/Step (individual operation)

I design DAGs to represent complete pipelines, with tasks as individual operations that can be monitored and debugged independently."

**Key Points:**
- DAG = Workflow container
- Task = Individual operation
- Tasks belong to DAGs
- Clear separation of concerns

---

### Q7: What is catchup in Airflow?

**Answer:**
"Catchup determines whether Airflow should backfill missed DAG runs.

**Catchup=True (Default):**
- Runs all missed DAG runs from start_date
- Can create many runs if start_date is old
- Useful for initial setup
- Can overwhelm system

**Catchup=False:**
- Only runs current and future runs
- Skips missed runs
- Recommended for production
- Prevents backfill issues

**Example:**
```python
# Bad - will backfill from 2020
dag = DAG(
    'my_dag',
    start_date=datetime(2020, 1, 1),
    schedule_interval='@daily',
    catchup=True  # Will create 1000+ runs!
)

# Good - only runs from now
dag = DAG(
    'my_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False  # Only current runs
)
```

**Best Practice:**
Always set `catchup=False` for production DAGs to avoid unexpected backfills.

I always set catchup=False in production to prevent accidental backfills that could overwhelm the system."

**Key Points:**
- Controls backfilling behavior
- catchup=True creates missed runs
- catchup=False skips missed runs
- Best practice: catchup=False for production

---

### Q8: How do you install and set up Airflow?

**Answer:**
"**Installation Steps:**

1. **Install Airflow:**
```bash
pip install apache-airflow
```

2. **Initialize Database:**
```bash
airflow db init
```

3. **Create Admin User:**
```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

4. **Start Webserver:**
```bash
airflow webserver --port 8080
```

5. **Start Scheduler (new terminal):**
```bash
airflow scheduler
```

**Access UI:**
- Open browser: http://localhost:8080
- Login with admin credentials

**Production Setup:**
- Use PostgreSQL/MySQL (not SQLite)
- Set up CeleryExecutor or KubernetesExecutor
- Configure workers
- Set up monitoring and alerting

I set up Airflow for development locally and use managed services (like AWS MWAA) for production."

**Key Points:**
- Install via pip
- Initialize database
- Create admin user
- Start webserver and scheduler
- Use proper database for production

---

## 🟡 INTERMEDIATE LEVEL Questions (5-8 questions)

### Q9: How do you handle task dependencies in Airflow?

**Answer:**
"**Dependency Operators:**

1. **`>>` (Right Shift)**: Set downstream dependency
```python
task1 >> task2  # task1 runs before task2
```

2. **`<<` (Left Shift)**: Set upstream dependency
```python
task2 << task1  # Same as above
```

3. **Multiple Upstream**: List of tasks
```python
[task1, task2] >> task3  # task3 waits for both
```

4. **Multiple Downstream**: List of tasks
```python
task1 >> [task2, task3]  # task2 and task3 run after task1
```

**Examples:**

**Sequential:**
```python
extract >> transform >> load
```

**Parallel:**
```python
[extract_api, extract_db, extract_files] >> transform
```

**Complex:**
```python
extract >> [validate, clean] >> transform >> [load_warehouse, load_analytics]
```

**Best Practices:**
- Use explicit dependencies (avoid implicit)
- Use task groups for organization
- Document complex dependencies
- Test dependency logic

I use dependency operators to define clear execution order, enabling parallel processing where possible while maintaining data integrity."

**Key Points:**
- `>>` and `<<` operators
- Multiple dependencies supported
- Enables parallel execution
- Clear execution order

---

### Q10: What are XComs and how do you use them?

**Answer:**
"XComs (Cross-Communication) allow tasks to exchange small amounts of data.

**Basic Usage:**

**Push Data:**
```python
def push_data(**context):
    data = {'key': 'value', 'count': 100}
    return data  # Automatically pushed to XCom

task1 = PythonOperator(
    task_id='push_task',
    python_callable=push_data,
    dag=dag
)
```

**Pull Data:**
```python
def pull_data(**context):
    # Pull from previous task
    data = context['ti'].xcom_pull(task_ids='push_task')
    print(data)  # {'key': 'value', 'count': 100}
    
    # Pull specific key
    count = context['ti'].xcom_pull(task_ids='push_task', key='count')

task2 = PythonOperator(
    task_id='pull_task',
    python_callable=pull_data,
    dag=dag
)

task1 >> task2
```

**Explicit Push:**
```python
def explicit_push(**context):
    context['ti'].xcom_push(key='custom_key', value='custom_value')
```

**Best Practices:**
- Keep data small (< 48KB by default)
- Use for metadata, not large datasets
- Store large data externally, pass paths via XCom
- Use meaningful keys

**Limitations:**
- Not for large data (use external storage)
- Stored in metadata database
- Can impact database performance if overused

I use XComs to pass configuration, file paths, and small metadata between tasks, while storing large datasets in S3 or databases."

**Key Points:**
- Cross-task communication
- Small data only
- Push and pull methods
- Use external storage for large data

---

### Q11: What are Sensors and when do you use them?

**Answer:**
"Sensors are special operators that wait for a condition to be met before proceeding.

**Common Sensors:**

1. **FileSensor**: Wait for file to appear
```python
from airflow.sensors.filesystem import FileSensor

file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,  # Timeout after 1 hour
    mode='poke',  # or 'reschedule'
    dag=dag
)
```

2. **HttpSensor**: Wait for API endpoint
```python
from airflow.sensors.http import HttpSensor

http_sensor = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='my_api',
    endpoint='/health',
    timeout=300,
    dag=dag
)
```

3. **SqlSensor**: Wait for SQL condition
```python
from airflow.sensors.sql import SqlSensor

sql_sensor = SqlSensor(
    task_id='wait_for_data',
    conn_id='my_database',
    sql="SELECT COUNT(*) FROM staging WHERE status='ready'",
    poke_interval=30,
    timeout=600,
    dag=dag
)
```

**Modes:**
- **poke**: Worker keeps checking (uses slot)
- **reschedule**: Worker released, rescheduled later (better for long waits)

**Use Cases:**
- Wait for file uploads
- Wait for API responses
- Wait for database updates
- Wait for external system readiness

I use Sensors to make pipelines event-driven, waiting for data files or API responses before processing."

**Key Points:**
- Wait for conditions
- Multiple sensor types
- poke vs reschedule modes
- Event-driven workflows

---

### Q12: How do you handle errors and retries in Airflow?

**Answer:**
"**Error Handling Strategies:**

1. **Retries Configuration:**
```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('my_dag', default_args=default_args)
```

2. **Task-Level Retries:**
```python
task = PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    retries=3,
    retry_delay=timedelta(minutes=5),
    dag=dag
)
```

3. **Exception Handling:**
```python
def robust_task(**context):
    try:
        # Task logic
        result = process_data()
        return result
    except TransientError as e:
        # Retry on transient errors
        raise
    except PermanentError as e:
        # Don't retry on permanent errors
        context['ti'].xcom_push(key='error', value=str(e))
        return None
```

4. **Callbacks:**
```python
def on_failure_callback(context):
    task_instance = context['task_instance']
    error = context.get('exception')
    # Send alert, log error, etc.
    send_alert(f"Task {task_instance.task_id} failed: {error}")

task = PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    on_failure_callback=on_failure_callback,
    on_success_callback=on_success_callback,
    on_retry_callback=on_retry_callback,
    dag=dag
)
```

5. **Exponential Backoff:**
```python
def retry_delay_callback(context):
    return timedelta(seconds=2 ** context['task_instance'].try_number)
```

**Best Practices:**
- Set appropriate retries (3-5 for transient errors)
- Use exponential backoff
- Distinguish transient vs permanent errors
- Implement proper logging
- Set up alerting

I implement comprehensive error handling with retries, callbacks, and proper exception handling to ensure robust pipeline execution."

**Key Points:**
- Retry configuration
- Exception handling
- Callbacks for notifications
- Exponential backoff
- Proper logging

---

### Q13: What are Variables and Connections in Airflow?

**Answer:**
"**Variables:**
Store configuration values that can be accessed across DAGs.

**Using Variables:**
```python
from airflow.models import Variable

# Get variable
api_key = Variable.get("api_key")
config = Variable.get("pipeline_config", deserialize_json=True)

# Set variable (via UI or CLI)
# airflow variables set api_key "your-key"
```

**Connections:**
Store credentials and connection information for external systems.

**Using Connections:**
```python
from airflow.hooks.base import BaseHook

# Get connection
conn = BaseHook.get_connection('my_postgres_conn')
host = conn.host
login = conn.login
password = conn.password
schema = conn.schema
port = conn.port

# Use with hooks
from airflow.hooks.postgres_hook import PostgresHook
hook = PostgresHook(postgres_conn_id='my_postgres_conn')
```

**Best Practices:**
- Use Variables for configuration
- Use Connections for credentials (never hardcode)
- Store sensitive data in Connections
- Use JSON Variables for complex configs
- Set via UI, CLI, or environment variables

**Security:**
- Connections encrypt passwords
- Variables are plain text (don't store secrets)
- Use Secrets Backend for production

I use Variables for pipeline configuration and Connections for database/API credentials, ensuring security and maintainability."

**Key Points:**
- Variables for configuration
- Connections for credentials
- Security considerations
- Best practices

---

### Q14: Explain branching in Airflow with an example.

**Answer:**
"Branching allows conditional task execution based on runtime conditions.

**BranchPythonOperator:**
```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    """Decide which branch to take"""
    # Get data from previous task
    data_volume = context['ti'].xcom_pull(task_ids='check_volume')
    
    if data_volume > 1000000:
        return 'process_high_volume'
    elif data_volume > 100000:
        return 'process_medium_volume'
    else:
        return 'process_low_volume'

# Branch task
branch_task = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_branch,
    dag=dag
)

# Branch options
high_volume = PythonOperator(
    task_id='process_high_volume',
    python_callable=process_high_volume,
    dag=dag
)

medium_volume = PythonOperator(
    task_id='process_medium_volume',
    python_callable=process_medium_volume,
    dag=dag
)

low_volume = PythonOperator(
    task_id='process_low_volume',
    python_callable=process_low_volume,
    dag=dag
)

# Join after branches
join_task = PythonOperator(
    task_id='join',
    python_callable=join_results,
    trigger_rule='none_failed_or_skipped',  # Important!
    dag=dag
)

# Define flow
check_task >> branch_task
branch_task >> [high_volume, medium_volume, low_volume]
[high_volume, medium_volume, low_volume] >> join_task
```

**Key Points:**
- Use `trigger_rule` for join tasks
- `trigger_rule='none_failed_or_skipped'` allows skipped branches
- Only one branch executes
- Other branches are skipped

I use branching to handle different processing paths based on data characteristics, ensuring efficient resource usage."

**Key Points:**
- Conditional execution
- BranchPythonOperator
- Trigger rules for joins
- Only one branch executes

---

### Q15: What are Task Groups and when should you use them?

**Answer:**
"Task Groups organize related tasks into logical units, improving DAG readability.

**Basic Usage:**
```python
from airflow.utils.task_group import TaskGroup

with DAG('organized_pipeline', default_args=default_args) as dag:
    with TaskGroup("data_ingestion") as ingestion:
        extract_api = PythonOperator(
            task_id='extract_api',
            python_callable=extract_api
        )
        extract_db = PythonOperator(
            task_id='extract_db',
            python_callable=extract_db
        )
        extract_files = PythonOperator(
            task_id='extract_files',
            python_callable=extract_files
        )
        extract_api >> extract_db >> extract_files
    
    with TaskGroup("data_processing") as processing:
        validate = PythonOperator(
            task_id='validate',
            python_callable=validate_data
        )
        transform = PythonOperator(
            task_id='transform',
            python_callable=transform_data
        )
        validate >> transform
    
    with TaskGroup("data_loading") as loading:
        load_warehouse = PythonOperator(
            task_id='load_warehouse',
            python_callable=load_warehouse
        )
        load_analytics = PythonOperator(
            task_id='load_analytics',
            python_callable=load_analytics
        )
    
    # Group-level dependencies
    ingestion >> processing >> loading
```

**Benefits:**
- Better organization
- Improved UI visualization
- Easier to understand complex DAGs
- Can collapse/expand in UI
- Reusable patterns

**When to Use:**
- Complex DAGs with many tasks
- Logical grouping of related tasks
- Reusable workflow patterns
- Better UI navigation

I use Task Groups to organize complex pipelines into logical sections, making them easier to understand and maintain."

**Key Points:**
- Organize related tasks
- Improve readability
- Better UI visualization
- Logical grouping

---

## 🔴 ADVANCED LEVEL Questions (5-8 questions)

### Q16: How do you design scalable Airflow architecture?

**Answer:**
"**Architecture Components:**

1. **Executor Choice:**
   - **SequentialExecutor**: Development only (single task)
   - **LocalExecutor**: Single machine, parallel tasks
   - **CeleryExecutor**: Distributed, scalable (recommended)
   - **KubernetesExecutor**: Cloud-native, auto-scaling (best for cloud)

2. **Worker Scaling:**
```python
# Celery configuration
celery_app_name = airflow.executors.celery_executor.app
worker_concurrency = 16  # Tasks per worker
```

3. **Database:**
   - Use PostgreSQL/MySQL (not SQLite)
   - Connection pooling
   - Regular maintenance
   - Backup strategy

4. **Monitoring:**
   - Airflow UI
   - External monitoring (Prometheus, Grafana)
   - Log aggregation
   - Alerting (PagerDuty, Slack)

5. **DAG Organization:**
   - Modular DAGs
   - Shared code libraries
   - Version control
   - CI/CD for DAGs

**Scalability Patterns:**
```python
# Use task pools to limit resource usage
task = PythonOperator(
    task_id='resource_intensive_task',
    pool='heavy_compute_pool',
    pool_slots=1,
    dag=dag
)

# Use different queues for different workloads
task = PythonOperator(
    task_id='high_priority_task',
    queue='high_priority',
    dag=dag
)
```

**Best Practices:**
- Use Celery/K8s executor for scale
- Monitor worker utilization
- Optimize DAG structure
- Use task pools for resource management
- Implement proper monitoring

I design scalable architecture with Celery executor, multiple workers, PostgreSQL database, and comprehensive monitoring."

**Key Points:**
- Executor selection
- Worker scaling
- Database optimization
- Monitoring and alerting
- Resource management

---

### Q17: How do you create dynamic DAGs in Airflow?

**Answer:**
"Dynamic DAG generation creates DAGs programmatically based on configuration.

**Pattern 1: Configuration-Driven**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

# Configuration
pipeline_configs = [
    {'id': 'pipeline_1', 'source': 'api_1', 'schedule': '@daily'},
    {'id': 'pipeline_2', 'source': 'api_2', 'schedule': '@hourly'},
    {'id': 'pipeline_3', 'source': 'database', 'schedule': '@weekly'},
]

def create_dag(dag_id, schedule, source):
    """Dynamically create DAG"""
    dag = DAG(
        dag_id,
        schedule_interval=schedule,
        default_args=default_args,
        catchup=False
    )
    
    with dag:
        extract = PythonOperator(
            task_id='extract',
            python_callable=lambda: extract_from_source(source)
        )
        
        transform = PythonOperator(
            task_id='transform',
            python_callable=transform_data
        )
        
        load = PythonOperator(
            task_id='load',
            python_callable=load_data
        )
        
        extract >> transform >> load
    
    return dag

# Generate DAGs
for config in pipeline_configs:
    dag_id = f"pipeline_{config['id']}"
    globals()[dag_id] = create_dag(
        dag_id=dag_id,
        schedule=config['schedule'],
        source=config['source']
    )
```

**Pattern 2: File-Based**
```python
import os
from pathlib import Path

dag_folder = Path('/dags/configs')

for config_file in dag_folder.glob('*.json'):
    config = json.loads(config_file.read_text())
    dag_id = config['dag_id']
    globals()[dag_id] = create_dag_from_config(config)
```

**Best Practices:**
- Keep DAG parsing fast
- Use lazy imports
- Validate configuration
- Document dynamic patterns
- Test thoroughly

I use dynamic DAGs to manage hundreds of similar pipelines with different configurations, reducing code duplication."

**Key Points:**
- Programmatic DAG creation
- Configuration-driven
- Reduces code duplication
- Keep parsing fast

---

### Q18: How do you create custom operators in Airflow?

**Answer:**
"Custom operators extend BaseOperator to create reusable, domain-specific operators.

**Example: Data Quality Operator**
```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook

class DataQualityOperator(BaseOperator):
    """Custom operator for data quality checks"""
    
    template_fields = ('sql',)  # Allow templating
    
    @apply_defaults
    def __init__(
        self,
        conn_id,
        table_name,
        quality_checks,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.table_name = table_name
        self.quality_checks = quality_checks
    
    def execute(self, context):
        """Execute data quality checks"""
        hook = PostgresHook(postgres_conn_id=self.conn_id)
        
        for check in self.quality_checks:
            query = check['query'].format(table=self.table_name)
            expected_result = check['expected']
            
            result = hook.get_first(query)[0]
            
            if result != expected_result:
                raise ValueError(
                    f"Data quality check failed: {check['name']}. "
                    f"Expected {expected_result}, got {result}"
                )
            
            self.log.info(f"✓ {check['name']} passed")
        
        self.log.info("All data quality checks passed")

# Usage
quality_check = DataQualityOperator(
    task_id='data_quality',
    conn_id='postgres_default',
    table_name='staging_table',
    quality_checks=[
        {
            'name': 'row_count',
            'query': 'SELECT COUNT(*) FROM {table}',
            'expected': 1000
        },
        {
            'name': 'null_check',
            'query': 'SELECT COUNT(*) FROM {table} WHERE id IS NULL',
            'expected': 0
        }
    ],
    dag=dag
)
```

**Key Concepts:**
- Inherit from BaseOperator
- Implement `execute()` method
- Use `template_fields` for templating
- Use `@apply_defaults` decorator
- Proper logging

I create custom operators for domain-specific operations, improving code reuse and maintainability."

**Key Points:**
- Extend BaseOperator
- Implement execute method
- Template fields support
- Domain-specific logic

---

### Q19: Explain Airflow executors and when to use each.

**Answer:**
"Executors determine how tasks are executed.

**1. SequentialExecutor (Default):**
- Runs one task at a time
- Uses SQLite (limitations)
- **Use**: Development only
- **Limitations**: No parallelism, SQLite constraints

**2. LocalExecutor:**
- Parallel tasks on single machine
- Uses multiprocessing
- **Use**: Small-scale production
- **Limitations**: Single machine, no distribution

**3. CeleryExecutor:**
- Distributed execution
- Multiple workers
- **Use**: Medium to large scale
- **Setup:**
```python
# airflow.cfg
executor = CeleryExecutor
broker_url = redis://localhost:6379/0
result_backend = db+postgresql://user:pass@localhost/airflow
```

**4. KubernetesExecutor:**
- Kubernetes-native
- Auto-scaling
- **Use**: Cloud-native, large scale
- **Benefits**: Resource isolation, auto-scaling, cloud-native

**5. LocalKubernetesExecutor:**
- Hybrid approach
- **Use**: Transition period

**Comparison:**
| Executor | Scale | Complexity | Use Case |
|----------|-------|------------|----------|
| Sequential | 1 task | Low | Development |
| Local | Single machine | Low | Small production |
| Celery | Distributed | Medium | Medium-large scale |
| K8s | Cloud-native | High | Large scale, cloud |

I use CeleryExecutor for distributed execution with multiple workers, scaling based on workload."

**Key Points:**
- Multiple executor types
- Scale and complexity trade-offs
- Choose based on requirements
- K8s for cloud-native

---

### Q20: How do you test Airflow DAGs?

**Answer:**
"**Testing Strategies:**

1. **DAG Validation:**
```python
# Test DAG structure
def test_dag_loaded():
    from airflow.models import DagBag
    dagbag = DagBag()
    assert len(dagbag.dags) > 0
    assert 'my_dag' in dagbag.dags

# Test no import errors
def test_no_import_errors():
    from airflow.models import DagBag
    dagbag = DagBag()
    assert len(dagbag.import_errors) == 0
```

2. **Task Testing:**
```python
# Test task function
def test_extract_task():
    result = extract_function()
    assert result is not None
    assert isinstance(result, dict)

# Test with context
def test_task_with_context():
    from airflow.models import TaskInstance
    from datetime import datetime
    
    context = {
        'ds': '2024-01-01',
        'ti': MockTaskInstance()
    }
    result = my_task_function(**context)
    assert result == expected
```

3. **Integration Testing:**
```python
# Test DAG execution
def test_dag_execution():
    from airflow.models import DagBag, DagRun
    from airflow.utils.state import State
    
    dagbag = DagBag()
    dag = dagbag.get_dag('my_dag')
    
    dagrun = dag.create_dagrun(
        run_id='test_run',
        state=State.RUNNING,
        execution_date=datetime.now()
    )
    
    # Execute tasks
    for task in dag.tasks:
        task.run(
            start_date=dagrun.execution_date,
            end_date=dagrun.execution_date
        )
```

4. **Mock External Dependencies:**
```python
from unittest.mock import patch, MagicMock

@patch('airflow.hooks.postgres_hook.PostgresHook')
def test_task_with_mock(mock_hook):
    mock_hook.return_value.get_records.return_value = [(1, 2, 3)]
    result = my_task_function()
    assert result is not None
```

**Best Practices:**
- Test DAG structure
- Test task functions
- Mock external dependencies
- Test error handling
- Use pytest for testing

I implement comprehensive testing including DAG validation, unit tests for tasks, and integration tests for end-to-end workflows."

**Key Points:**
- DAG validation
- Task unit testing
- Integration testing
- Mock external dependencies
- Use pytest

---

### Q21: How do you monitor and optimize Airflow performance?

**Answer:**
"**Monitoring:**

1. **Airflow Metrics:**
   - Task duration
   - DAG run duration
   - Task success/failure rates
   - Scheduler lag
   - Queue depth

2. **External Monitoring:**
```python
# Prometheus metrics
from airflow.configuration import conf
from prometheus_client import Counter, Histogram

task_duration = Histogram('airflow_task_duration', 'Task duration')
task_failures = Counter('airflow_task_failures', 'Task failures')
```

3. **Logging:**
```python
# Structured logging
import logging
logger = logging.getLogger(__name__)

def my_task(**context):
    logger.info("Starting task", extra={
        'dag_id': context['dag'].dag_id,
        'task_id': context['task_instance'].task_id
    })
```

**Optimization:**

1. **DAG Parsing:**
```python
# Lazy imports
def my_task():
    import pandas as pd  # Import inside function
    # Use pandas
```

2. **Task Execution:**
```python
# Use task pools
task = PythonOperator(
    task_id='task',
    pool='compute_pool',
    pool_slots=1,
    dag=dag
)

# Use queues
task = PythonOperator(
    task_id='task',
    queue='high_priority',
    dag=dag
)
```

3. **Database:**
   - Connection pooling
   - Regular VACUUM
   - Index optimization
   - Archive old data

4. **Scheduler:**
   - Optimize parsing time
   - Reduce DAG file complexity
   - Use file processors efficiently

I monitor Airflow with Prometheus, optimize DAG parsing with lazy imports, and use task pools for resource management."

**Key Points:**
- Comprehensive monitoring
- Performance optimization
- Database tuning
- Scheduler optimization

---

### Q22: Explain Airflow's task lifecycle and states.

**Answer:**
"**Task States:**

1. **None**: Task not yet scheduled
2. **Scheduled**: Task scheduled but not yet queued
3. **Queued**: Task queued, waiting for worker
4. **Running**: Task currently executing
5. **Success**: Task completed successfully
6. **Failed**: Task failed
7. **Skipped**: Task skipped (branching)
8. **Retry**: Task retrying after failure
9. **Upstream Failed**: Upstream task failed
10. **Up for Retry**: Task waiting to retry
11. **Deferred**: Task deferred (new in 2.2+)
12. **Removed**: Task removed from DAG

**State Transitions:**
```
None → Scheduled → Queued → Running → Success
                              ↓
                           Failed → Retry → Running
                              ↓
                           Skipped (if upstream failed)
```

**Task Lifecycle:**
1. **Scheduling**: Scheduler determines task should run
2. **Queuing**: Task added to executor queue
3. **Execution**: Worker picks up task and executes
4. **Completion**: Task finishes (success/failure)
5. **Retry**: If failed and retries available

**Monitoring States:**
```python
# Check task state
task_instance = context['task_instance']
state = task_instance.state
if state == 'failed':
    # Handle failure
    pass
```

I monitor task states to understand pipeline health and debug issues, using state information for alerting and reporting."

**Key Points:**
- Multiple task states
- State transitions
- Lifecycle management
- Monitoring and debugging

---

## 🎯 Key Takeaways

1. **Airflow = Orchestration** - Industry standard workflow tool
2. **DAG = Workflow** - Code-as-configuration
3. **Tasks = Work Units** - Individual operations
4. **Operators = Task Types** - Reusable components
5. **Dependencies = Execution Order** - Clear task flow
6. **XComs = Communication** - Small data exchange
7. **Sensors = Event-Driven** - Wait for conditions
8. **Error Handling = Reliability** - Retries and callbacks
9. **Scalability = Architecture** - Executor choice matters
10. **Testing = Quality** - Comprehensive test coverage

---

## ✅ Practice Checklist

- [ ] Can explain Airflow in 2 minutes
- [ ] Understand DAGs and tasks
- [ ] Know common operators
- [ ] Understand dependencies and XComs
- [ ] Know error handling and retries
- [ ] Understand Sensors and branching
- [ ] Know Variables and Connections
- [ ] Understand executors and scaling
- [ ] Can create custom operators
- [ ] Know testing strategies
- [ ] Ready for system design questions

---

**Remember**: Airflow mastery = Data Engineering excellence! 🚀
