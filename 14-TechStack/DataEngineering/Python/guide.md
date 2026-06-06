# Python for Data Engineering Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install packages
pip install pandas pyspark
```

### 2. **Pandas Basics**
```python
import pandas as pd

# Read data
df = pd.read_csv("data.csv")

# Transform
df_filtered = df[df['age'] > 25]
df_grouped = df.groupby('department')['salary'].mean()

# Write
df_filtered.to_parquet("output.parquet")
```

### 3. **PySpark Basics**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MyApp").getOrCreate()
df = spark.read.csv("data.csv", header=True, inferSchema=True)
df.filter(df.age > 25).show()
```

## Level 2 – Production Patterns

### ETL Pipeline
```python
def extract():
    return pd.read_csv("source.csv")

def transform(df):
    return df.dropna().drop_duplicates()

def load(df):
    df.to_parquet("output.parquet")

# Execute
df = extract()
df = transform(df)
load(df)
```

### Airflow Integration
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def etl_task():
    # ETL logic
    pass

dag = DAG('etl_pipeline')
task = PythonOperator(task_id='etl', python_callable=etl_task, dag=dag)
```

## Level 3 – Architect Playbook

### Performance Optimization
```python
# Use vectorization
df['new_col'] = df['col1'] + df['col2']  # Fast

# Avoid loops
# Bad: for row in df.iterrows()
# Good: df.apply() or vectorized operations
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Install | `pip install package` | Install package |
| Freeze | `pip freeze > requirements.txt` | Save dependencies |
| Test | `pytest` | Run tests |

## Checklist Before Production

- [ ] Set up virtual environments
- [ ] Implement proper error handling
- [ ] Set up logging
- [ ] Optimize data processing
- [ ] Set up monitoring
- [ ] Implement proper testing
- [ ] Set up CI/CD
- [ ] Document code
