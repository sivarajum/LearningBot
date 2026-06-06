# Apache Airflow Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
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
    --email admin@example.com \
    --password admin

# Start webserver
airflow webserver --port 8080

# Start scheduler (new terminal)
airflow scheduler
```

### 2. **First DAG**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'my_first_dag',
    default_args=default_args,
    description='Simple ETL pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False
)

def extract():
    print("Extracting data...")
    return "extracted_data"

def transform(**context):
    data = context['ti'].xcom_pull(task_ids='extract')
    print(f"Transforming {data}...")
    return "transformed_data"

def load(**context):
    data = context['ti'].xcom_pull(task_ids='transform')
    print(f"Loading {data}...")

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

extract_task >> transform_task >> load_task
```

### 3. **Core Concepts**
- **DAG**: Workflow definition
- **Task**: Individual work unit
- **Operator**: Defines what task does
- **XCom**: Cross-task communication
- **Scheduler**: Executes DAGs based on schedule

## Level 2 – Production Patterns

### Parallel Processing
```python
from airflow.utils.task_group import TaskGroup

with DAG('parallel_pipeline', default_args=default_args) as dag:
    with TaskGroup("extraction") as extraction:
        extract_api = PythonOperator(
            task_id='extract_api',
            python_callable=extract_from_api
        )
        extract_db = PythonOperator(
            task_id='extract_db',
            python_callable=extract_from_database
        )
        extract_files = PythonOperator(
            task_id='extract_files',
            python_callable=extract_from_files
        )
    
    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data
    )
    
    extraction >> transform
```

### Sensors & Event-Driven
```python
from airflow.sensors.filesystem import FileSensor

file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input.csv',
    poke_interval=60,
    timeout=3600,
    mode='reschedule',
    dag=dag
)

file_sensor >> extract_task
```

### Error Handling & Retries
```python
def on_failure_callback(context):
    task_instance = context['task_instance']
    error = context.get('exception')
    send_alert(f"Task {task_instance.task_id} failed: {error}")

task = PythonOperator(
    task_id='critical_task',
    python_callable=my_function,
    retries=3,
    retry_delay=timedelta(minutes=5),
    on_failure_callback=on_failure_callback,
    dag=dag
)
```

### Variables & Connections
```python
from airflow.models import Variable
from airflow.hooks.base import BaseHook

# Using Variables
api_key = Variable.get("api_key")
config = Variable.get("pipeline_config", deserialize_json=True)

# Using Connections
conn = BaseHook.get_connection('my_postgres_conn')
hook = PostgresHook(postgres_conn_id='my_postgres_conn')
```

## Level 3 – Architect Playbook

### Dynamic DAG Generation
```python
def create_dag(dag_id, schedule, config):
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

# Generate DAGs from config
for config in pipeline_configs:
    dag_id = f"pipeline_{config['id']}"
    globals()[dag_id] = create_dag(
        dag_id=dag_id,
        schedule=config['schedule'],
        config=config
    )
```

### Custom Operators
```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):
    @apply_defaults
    def __init__(self, conn_id, table_name, checks, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.table_name = table_name
        self.checks = checks
    
    def execute(self, context):
        hook = PostgresHook(postgres_conn_id=self.conn_id)
        for check in self.checks:
            result = hook.get_first(check['query'])[0]
            if result != check['expected']:
                raise ValueError(f"Check failed: {check['name']}")
            self.log.info(f"✓ {check['name']} passed")
```

### Scalable Architecture
```python
# Use Celery Executor for distributed execution
# airflow.cfg
executor = CeleryExecutor
broker_url = redis://localhost:6379/0
result_backend = db+postgresql://user:pass@localhost/airflow

# Task pools for resource management
task = PythonOperator(
    task_id='resource_intensive',
    pool='heavy_compute_pool',
    pool_slots=1,
    dag=dag
)
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| List DAGs | `airflow dags list` | View all DAGs |
| Test task | `airflow tasks test dag_id task_id 2024-01-01` | Test single task |
| Backfill | `airflow dags backfill dag_id -s 2024-01-01 -e 2024-01-31` | Run missed DAG runs |
| Clear task | `airflow tasks clear dag_id -t task_id` | Clear task state |
| Pause DAG | `airflow dags pause dag_id` | Pause DAG execution |
| Unpause DAG | `airflow dags unpause dag_id` | Resume DAG execution |
| View logs | `airflow tasks logs dag_id task_id 2024-01-01` | View task logs |

## Architecture Patterns

```mermaid
graph TB
    subgraph "Scheduler"
        A[Parse DAGs]
        B[Schedule Tasks]
    end
    
    subgraph "Executor"
        C[Celery Executor]
    end
    
    subgraph "Message Queue"
        D[Redis/RabbitMQ]
    end
    
    subgraph "Workers"
        E[Worker 1]
        F[Worker 2]
        G[Worker N]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
```

## Checklist Before Production

- [ ] Use PostgreSQL/MySQL (not SQLite)
- [ ] Set catchup=False for production DAGs
- [ ] Configure appropriate retries and retry_delay
- [ ] Use Variables and Connections (no hardcoded values)
- [ ] Implement proper error handling and callbacks
- [ ] Set up monitoring and alerting
- [ ] Use task pools for resource management
- [ ] Optimize DAG parsing (lazy imports)
- [ ] Set up proper authentication and authorization
- [ ] Configure backup strategy for metadata database
