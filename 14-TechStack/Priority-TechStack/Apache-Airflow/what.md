# Apache Airflow - Complete Guide (Basic to Advanced)

## 🎯 What is Apache Airflow?

**Apache Airflow** is an open-source platform for programmatically authoring, scheduling, and monitoring workflows. It's the industry standard for data pipeline orchestration, used by 80%+ of data engineering teams.

### Why Airflow?
- **Workflow Orchestration**: Define complex DAGs with dependencies
- **Scheduling**: Cron-like scheduling with timezone support
- **Monitoring**: Built-in UI for real-time monitoring
- **Extensible**: 200+ operators and hooks
- **Industry Standard**: Most common orchestration tool
- **Python-Native**: Code-as-configuration approach
- **Scalable**: Supports distributed execution

### Problem It Solves
- Manual pipeline scheduling and monitoring
- Complex dependency management
- Workflow versioning and reproducibility
- Multi-team collaboration on pipelines
- Error handling and retry logic

---

## 📚 Learning Path: Basic → Intermediate → Advanced

### Roadmap Overview
1. **Week 1-2: Foundations** - DAGs, Operators, Basic Scheduling
2. **Week 3-4: Intermediate** - XComs, Sensors, Task Dependencies
3. **Week 5-6: Production** - Error Handling, Monitoring, Best Practices
4. **Week 7-8: Advanced** - Dynamic DAGs, Custom Operators, Scaling

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Installation & Setup

```bash
# Install Airflow
pip install apache-airflow

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start webserver
airflow webserver --port 8080

# Start scheduler (new terminal)
airflow scheduler
```

### Basic DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='Simple ETL pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['etl', 'daily']
)

def extract():
    print("Extracting data from source...")
    # Your extraction logic
    return "extracted_data"

def transform(**context):
    # Pull data from previous task
    extracted_data = context['ti'].xcom_pull(task_ids='extract')
    print(f"Transforming {extracted_data}...")
    # Your transformation logic
    return "transformed_data"

def load(**context):
    transformed_data = context['ti'].xcom_pull(task_ids='transform')
    print(f"Loading {transformed_data} to destination...")
    # Your loading logic

# Define tasks
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag
)

# Define dependencies
extract_task >> transform_task >> load_task
```

### Key Concepts

#### 1. **DAG (Directed Acyclic Graph)**
- **Directed**: Tasks have dependencies (arrows show flow)
- **Acyclic**: No cycles (can't loop back to previous task)
- **Graph**: Network of tasks and dependencies
- **Properties**: Must have start_date, schedule_interval

#### 2. **Tasks**
- Individual work units in a DAG
- Operators define what the task does
- Can have upstream/downstream dependencies
- Each task runs independently

#### 3. **Operators**
- **PythonOperator**: Execute Python functions
- **BashOperator**: Execute bash commands
- **SQLOperator**: Execute SQL queries
- **EmailOperator**: Send emails
- **Sensor**: Wait for conditions (files, APIs, etc.)

#### 4. **Scheduling**
- **Cron expressions**: `0 0 * * *` (daily at midnight)
- **Timedelta**: `timedelta(days=1)`
- **Preset**: `@daily`, `@hourly`, `@weekly`
- **None**: Manual trigger only

#### 5. **Execution Context**
- **start_date**: When DAG starts running
- **schedule_interval**: How often to run
- **catchup**: Whether to backfill missed runs
- **max_active_runs**: Concurrent DAG runs

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Complex DAG with Parallel Tasks

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

dag = DAG(
    'complex_pipeline',
    default_args=default_args,
    schedule_interval='@daily'
)

# Parallel extraction tasks
with TaskGroup("extraction_group") as extraction:
    extract_api = PythonOperator(
        task_id='extract_api',
        python_callable=extract_from_api
    )
    
    extract_database = PythonOperator(
        task_id='extract_database',
        python_callable=extract_from_database
    )
    
    extract_files = PythonOperator(
        task_id='extract_files',
        python_callable=extract_from_files
    )

# Transformation task (waits for all extractions)
transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform_data
)

# Parallel loading tasks
with TaskGroup("loading_group") as loading:
    load_warehouse = PythonOperator(
        task_id='load_warehouse',
        python_callable=load_to_warehouse
    )
    
    load_analytics = PythonOperator(
        task_id='load_analytics',
        python_callable=load_to_analytics
    )

# Define dependencies
extraction >> transform_task >> loading
```

### XComs (Cross-Communication)

```python
def push_data(**context):
    """Push data to XCom"""
    data = {
        'records': 1000,
        'status': 'success',
        'file_path': '/data/output.csv'
    }
    return data

def pull_and_process(**context):
    """Pull data from XCom and process"""
    # Pull from specific task
    data = context['ti'].xcom_pull(
        task_ids='push_task',
        key='return_value'  # or custom key
    )
    
    # Process data
    records = data['records']
    print(f"Processing {records} records...")
    
    # Push new data
    context['ti'].xcom_push(key='processed_count', value=records)

push_task = PythonOperator(
    task_id='push_task',
    python_callable=push_data,
    dag=dag
)

process_task = PythonOperator(
    task_id='process_task',
    python_callable=pull_and_process,
    dag=dag
)

push_task >> process_task
```

### Sensors (Wait for Conditions)

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.http import HttpSensor
from airflow.sensors.sql import SqlSensor

# File Sensor - Wait for file
file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,  # Timeout after 1 hour
    mode='poke',  # or 'reschedule'
    dag=dag
)

# HTTP Sensor - Wait for API
http_sensor = HttpSensor(
    task_id='wait_for_api',
    http_conn_id='my_api',
    endpoint='/health',
    timeout=300,
    dag=dag
)

# SQL Sensor - Wait for data
sql_sensor = SqlSensor(
    task_id='wait_for_data',
    conn_id='my_database',
    sql="SELECT COUNT(*) FROM staging_table WHERE status='ready'",
    poke_interval=30,
    timeout=600,
    dag=dag
)
```

### Variables and Connections

```python
from airflow.models import Variable
from airflow.hooks.base import BaseHook

# Using Variables
api_key = Variable.get("api_key", default_var=None)
config = Variable.get("pipeline_config", deserialize_json=True)

# Using Connections
def use_connection():
    conn = BaseHook.get_connection('my_postgres_conn')
    host = conn.host
    login = conn.login
    password = conn.password
    # Use connection
```

### Branching (Conditional Logic)

```python
from airflow.operators.python import BranchPythonOperator

def choose_branch(**context):
    """Decide which branch to take"""
    condition = context['ti'].xcom_pull(task_ids='check_condition')
    if condition == 'high_volume':
        return 'process_high_volume'
    else:
        return 'process_normal'

branch_task = BranchPythonOperator(
    task_id='branch',
    python_callable=choose_branch,
    dag=dag
)

high_volume_task = PythonOperator(
    task_id='process_high_volume',
    python_callable=process_high_volume,
    dag=dag
)

normal_task = PythonOperator(
    task_id='process_normal',
    python_callable=process_normal,
    dag=dag
)

check_task >> branch_task
branch_task >> [high_volume_task, normal_task]
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Dynamic DAG Generation

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def create_dag(dag_id, schedule, default_args, config):
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
            python_callable=lambda: extract_data(config['source'])
        )
        
        transform = PythonOperator(
            task_id='transform',
            python_callable=lambda: transform_data(config['rules'])
        )
        
        load = PythonOperator(
            task_id='load',
            python_callable=lambda: load_data(config['destination'])
        )
        
        extract >> transform >> load
    
    return dag

# Generate DAGs from configuration
for config in pipeline_configs:
    dag_id = f"pipeline_{config['id']}"
    globals()[dag_id] = create_dag(
        dag_id=dag_id,
        schedule=config['schedule'],
        default_args=default_args,
        config=config
    )
```

### Custom Operators

```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):
    """Custom operator for data quality checks"""
    
    @apply_defaults
    def __init__(
        self,
        table_name,
        quality_checks,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.quality_checks = quality_checks
    
    def execute(self, context):
        """Execute data quality checks"""
        from airflow.hooks.postgres_hook import PostgresHook
        
        hook = PostgresHook(postgres_conn_id='postgres_default')
        
        for check in self.quality_checks:
            query = check['query']
            expected_result = check['expected']
            
            result = hook.get_first(query)[0]
            
            if result != expected_result:
                raise ValueError(
                    f"Data quality check failed: {check['name']}. "
                    f"Expected {expected_result}, got {result}"
                )
            
            self.log.info(f"✓ {check['name']} passed")

# Use custom operator
quality_check = DataQualityOperator(
    task_id='data_quality',
    table_name='staging_table',
    quality_checks=[
        {
            'name': 'row_count',
            'query': 'SELECT COUNT(*) FROM staging_table',
            'expected': 1000
        },
        {
            'name': 'null_check',
            'query': 'SELECT COUNT(*) FROM staging_table WHERE id IS NULL',
            'expected': 0
        }
    ],
    dag=dag
)
```

### Task Groups for Organization

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
    
    ingestion >> processing >> loading
```

### SubDAGs (Legacy - Use Task Groups Instead)

```python
# Note: SubDAGs are deprecated, use Task Groups
# Shown for reference only

def subdag(parent_dag_name, child_dag_name, args):
    dag_subdag = DAG(
        dag_id=f'{parent_dag_name}.{child_dag_name}',
        default_args=args,
        schedule_interval="@daily"
    )
    
    with dag_subdag:
        # Define subdag tasks
        pass
    
    return dag_subdag
```

### Hooks for External Systems

```python
from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.S3_hook import S3Hook
from airflow.providers.http.hooks.http import HttpHook

# PostgreSQL Hook
def use_postgres(**context):
    hook = PostgresHook(postgres_conn_id='postgres_default')
    records = hook.get_records("SELECT * FROM table")
    return records

# S3 Hook
def use_s3(**context):
    hook = S3Hook(aws_conn_id='aws_default')
    hook.load_file(
        filename='/local/file.csv',
        key='s3_key/file.csv',
        bucket_name='my-bucket'
    )

# HTTP Hook
def use_http(**context):
    hook = HttpHook(http_conn_id='my_api', method='GET')
    response = hook.run(endpoint='/data')
    return response.json()
```

### Callbacks and Notifications

```python
def success_callback(context):
    """Called when task succeeds"""
    print(f"Task {context['task_instance'].task_id} succeeded!")
    # Send notification, log, etc.

def failure_callback(context):
    """Called when task fails"""
    print(f"Task {context['task_instance'].task_id} failed!")
    # Send alert, log error, etc.

def retry_callback(context):
    """Called when task retries"""
    print(f"Task {context['task_instance'].task_id} retrying...")

task = PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    on_success_callback=success_callback,
    on_failure_callback=failure_callback,
    on_retry_callback=retry_callback,
    dag=dag
)
```

### SLAs and Timeouts

```python
from datetime import timedelta

dag = DAG(
    'sla_dag',
    default_args={
        **default_args,
        'sla': timedelta(hours=2),  # SLA for entire DAG
    }
)

task = PythonOperator(
    task_id='critical_task',
    python_callable=critical_function,
    sla=timedelta(minutes=30),  # SLA for this task
    execution_timeout=timedelta(hours=1),  # Task timeout
    dag=dag
)
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Simple Linear Pipeline
```
Extract → Transform → Load
```
**Use Case**: Simple ETL jobs, data migration

### Pattern 2: Parallel Processing
```
Extract A ──┐
            ├→ Transform → Load
Extract B ──┘
```
**Use Case**: Multiple data sources, independent extractions

### Pattern 3: Conditional Branching
```
Extract → Check → [If True: Process A, If False: Process B] → Load
```
**Use Case**: Different processing based on data characteristics

### Pattern 4: Fan-Out Fan-In
```
Extract → [Process 1, Process 2, Process 3] → Aggregate → Load
```
**Use Case**: Parallel processing with aggregation

### Pattern 5: Event-Driven
```
Sensor → Trigger → Process → Notify
```
**Use Case**: File-based pipelines, API-driven workflows

---

## 📊 Best Practices

### 1. **Idempotency**
- Tasks should produce same result when run multiple times
- Use deterministic logic
- Handle partial failures gracefully
- Example: Use `INSERT ... ON CONFLICT` in SQL

### 2. **Task Granularity**
- Keep tasks focused (single responsibility)
- One task = one logical operation
- Easier to debug and monitor
- Better for parallelization

### 3. **Error Handling**
- Set appropriate retries
- Use exponential backoff
- Implement proper exception handling
- Log errors with context

### 4. **Resource Management**
- Use task pools to limit concurrent tasks
- Set appropriate resource limits
- Monitor resource usage
- Use different executors for different workloads

### 5. **Configuration Management**
- Use Variables for configuration
- Use Connections for credentials
- Avoid hardcoding values
- Use environment-specific configs

### 6. **Monitoring and Alerting**
- Set up SLAs
- Monitor task duration
- Track failure rates
- Set up alerts for critical failures

### 7. **Code Organization**
- Use Task Groups for organization
- Modularize common logic
- Use shared code libraries
- Version control DAGs

### 8. **Performance Optimization**
- Use lazy imports in DAG files
- Minimize DAG parsing time
- Optimize task execution
- Use appropriate operators

---

## ⚠️ Common Pitfalls and Solutions

### Pitfall 1: Catchup Issues
**Problem**: Running catchup=True on long-running DAGs
```python
# Bad
dag = DAG('my_dag', catchup=True, start_date=datetime(2020, 1, 1))

# Good
dag = DAG('my_dag', catchup=False, start_date=datetime(2024, 1, 1))
```

### Pitfall 2: Heavy Imports in DAG File
**Problem**: Slow DAG parsing
```python
# Bad - imports at top level
import pandas as pd
import numpy as np

# Good - lazy imports
def my_task():
    import pandas as pd
    import numpy as np
    # Use libraries
```

### Pitfall 3: Not Using XComs Properly
**Problem**: Large data in XComs
```python
# Bad - large data in XCom
return large_dataframe  # Can cause memory issues

# Good - store in external storage, pass reference
def store_and_return_path():
    path = '/data/processed.parquet'
    df.to_parquet(path)
    return path
```

### Pitfall 4: Missing Dependencies
**Problem**: Tasks running out of order
```python
# Bad - implicit dependencies
task1
task2
task3

# Good - explicit dependencies
task1 >> task2 >> task3
```

---

## 🔄 Comparison with Alternatives

### Airflow vs Prefect
| Feature | Airflow | Prefect |
|---------|---------|---------|
| Maturity | Very mature | Newer |
| UI | Built-in | Modern UI |
| Python | Code-as-config | Pure Python |
| Scheduling | Cron-based | Flexible |
| Community | Large | Growing |

### Airflow vs Dagster
| Feature | Airflow | Dagster |
|---------|---------|---------|
| Focus | Orchestration | Data-aware |
| Testing | External | Built-in |
| Lineage | Limited | Strong |
| Development | Code-first | Asset-first |

### Airflow vs Luigi
| Feature | Airflow | Luigi |
|---------|---------|-------|
| UI | Rich | Basic |
| Complexity | Higher | Lower |
| Adoption | High | Lower |
| Features | More | Fewer |

---

## 🎯 Real-World Use Cases

### 1. **ETL Pipelines**
- Extract from multiple sources
- Transform and clean data
- Load to data warehouse
- Schedule daily/hourly runs

### 2. **Data Quality Monitoring**
- Run data quality checks
- Alert on failures
- Generate reports
- Track data lineage

### 3. **ML Pipeline Orchestration**
- Feature engineering
- Model training
- Model evaluation
- Model deployment
- A/B testing

### 4. **Report Generation**
- Aggregate data
- Generate reports
- Send notifications
- Archive reports

### 5. **Data Lake Management**
- Ingest from sources
- Partition data
- Run transformations
- Update metadata

---

## 🚀 Performance Considerations

### 1. **Executor Selection**
- **SequentialExecutor**: Development only
- **LocalExecutor**: Single machine, parallel tasks
- **CeleryExecutor**: Distributed, scalable
- **KubernetesExecutor**: Cloud-native, auto-scaling

### 2. **Database Optimization**
- Use PostgreSQL/MySQL (not SQLite for production)
- Connection pooling
- Regular maintenance
- Monitor query performance

### 3. **Worker Management**
- Scale workers based on load
- Use different worker pools
- Monitor worker utilization
- Auto-scale with K8s

### 4. **DAG Optimization**
- Minimize DAG parsing time
- Use lazy imports
- Optimize task execution
- Cache frequently used data

---

## 📈 Market Positioning

### Industry Adoption
- **80%+ of data teams** use Airflow
- **Standard for orchestration** in data engineering
- **Strong community** support
- **Active development** and updates

### Job Market
- **High demand** for Airflow skills
- **Critical skill** for data engineers
- **Often required** in job postings
- **Career growth** opportunity

### Learning Resources
- Official documentation
- Community tutorials
- Online courses
- Conference talks

---

## 🎓 Learning Roadmap

### Week 1-2: Foundations
- [ ] Install and setup Airflow
- [ ] Create first DAG
- [ ] Understand operators
- [ ] Learn scheduling
- [ ] Explore UI

### Week 3-4: Intermediate
- [ ] XComs and task communication
- [ ] Sensors and waiting
- [ ] Variables and connections
- [ ] Error handling
- [ ] Task dependencies

### Week 5-6: Production
- [ ] Best practices
- [ ] Monitoring and alerting
- [ ] Performance optimization
- [ ] Security
- [ ] Testing

### Week 7-8: Advanced
- [ ] Dynamic DAGs
- [ ] Custom operators
- [ ] Task groups
- [ ] Scaling strategies
- [ ] Advanced patterns

---

## 🎯 Key Takeaways

1. **Airflow = Workflow Orchestration** - Industry standard tool
2. **DAG = Workflow Definition** - Code-as-configuration
3. **Tasks = Work Units** - Individual operations
4. **Operators = Task Types** - Reusable components
5. **Scheduling = Automation** - Time-based or event-driven
6. **Idempotency = Reliability** - Safe to rerun
7. **Monitoring = Observability** - Track and debug
8. **Scalability = Growth** - Handle increasing load

---

## 📚 Next Steps

1. ✅ Read this comprehensive guide
2. 📊 Review `Visual.md` for architecture diagrams
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build real pipelines
5. 🎯 Explain confidently in interviews
6. 🚀 Deploy to production
7. 📈 Monitor and optimize

---

## 🔗 Additional Resources

- **Official Docs**: https://airflow.apache.org/docs/
- **GitHub**: https://github.com/apache/airflow
- **Community**: https://airflow.apache.org/community/
- **Best Practices**: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html

---

**Remember**: Airflow mastery = Data Engineering excellence! 🚀
