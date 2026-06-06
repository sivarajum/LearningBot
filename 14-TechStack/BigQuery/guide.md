# BigQuery Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Setup**
```python
from google.cloud import bigquery

client = bigquery.Client(project="my-project")
```

### 2. **Basic Queries**
```python
query = """
    SELECT name, COUNT(*) as count
    FROM `my-project.dataset.table`
    GROUP BY name
    LIMIT 10
"""

results = client.query(query)
for row in results:
    print(row.name, row.count)
```

### 3. **Load Data**
```python
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True
)

with open("data.csv", "rb") as source_file:
    job = client.load_table_from_file(
        source_file,
        "my-project.dataset.table",
        job_config=job_config
    )
job.result()
```

## Level 2 – Production Patterns

### Partitioning
```sql
CREATE TABLE `my-project.dataset.events`
(
    event_date DATE,
    event_id STRING,
    value FLOAT64
)
PARTITION BY event_date
CLUSTER BY event_id;
```

### BigQuery ML
```sql
CREATE MODEL `my-project.dataset.churn_model`
OPTIONS(model_type='logistic_reg') AS
SELECT age, tenure, churned
FROM `my-project.dataset.customers`;
```

## Level 3 – Architect Playbook

### External Tables
```sql
CREATE EXTERNAL TABLE `my-project.dataset.external`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://bucket/data/*.parquet']
);
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Query | `client.query()` | Run query |
| Load | `client.load_table_from_file()` | Load data |
| Export | `client.extract_table()` | Export data |

## Checklist Before Production

- [ ] Set up proper dataset organization
- [ ] Configure partitioning and clustering
- [ ] Implement proper access controls
- [ ] Set up cost monitoring
- [ ] Optimize queries
- [ ] Set up scheduled queries
- [ ] Configure data retention
- [ ] Set up monitoring
