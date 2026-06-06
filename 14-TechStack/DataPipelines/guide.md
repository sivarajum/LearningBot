# Data Pipelines Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Simple ETL**
```python
# Extract
data = pd.read_csv("source.csv")

# Transform
data_clean = data.dropna().drop_duplicates()

# Load
data_clean.to_parquet("output.parquet")
```

### 2. **Airflow Pipeline**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def extract():
    return pd.read_csv("source.csv")

def transform(**context):
    data = context['ti'].xcom_pull(task_ids='extract')
    return data.dropna()

def load(**context):
    data = context['ti'].xcom_pull(task_ids='transform')
    data.to_parquet("output.parquet")

dag = DAG('etl_pipeline')
extract_task = PythonOperator(task_id='extract', python_callable=extract, dag=dag)
transform_task = PythonOperator(task_id='transform', python_callable=transform, dag=dag)
load_task = PythonOperator(task_id='load', python_callable=load, dag=dag)

extract_task >> transform_task >> load_task
```

## Level 2 – Production Patterns

### Streaming Pipeline
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Streaming").getOrCreate()

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "topic") \
    .load()

query = df.writeStream \
    .format("parquet") \
    .option("path", "output/") \
    .start()
```

### Error Handling
```python
try:
    process_data()
except Exception as e:
    logger.error(f"Error: {e}")
    send_to_dlq(data, error=str(e))
```

## Level 3 – Architect Playbook

### Medallion Architecture
```python
# Bronze: Raw data
bronze_df = spark.read.format("json").load("bronze/")

# Silver: Cleaned
silver_df = bronze_df.dropna().drop_duplicates()

# Gold: Aggregated
gold_df = silver_df.groupBy("category").agg(sum("amount"))
```

## Ops Cheat Sheet

| Task | Tool | Notes |
| --- | --- | --- |
| Orchestrate | Airflow, Prefect | Schedule pipelines |
| Process | Spark, Pandas | Transform data |
| Monitor | Airflow UI, logs | Track execution |

## Checklist Before Production

- [ ] Implement idempotency
- [ ] Set up error handling
- [ ] Configure monitoring
- [ ] Implement data quality checks
- [ ] Set up alerting
- [ ] Optimize performance
- [ ] Test thoroughly
- [ ] Document pipeline
