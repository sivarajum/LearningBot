# BigQuery - Complete Guide (Basic to Advanced)

## 🎯 What is BigQuery?

**BigQuery** is Google Cloud's fully managed, serverless data warehouse. It enables super-fast SQL queries on massive datasets without managing infrastructure. You use it in Modules 02 and 04 for data storage and analytics.

### Why BigQuery?
- **Serverless**: No infrastructure management
- **Fast**: Queries petabytes in seconds
- **Scalable**: Automatic scaling
- **Cost-Effective**: Pay only for storage and queries
- **Integrated**: Works with GCP services

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic BigQuery Usage

```python
from google.cloud import bigquery

# Initialize client
client = bigquery.Client(project="your-project")

# Run query
query = """
SELECT 
    customer_id,
    total_spent,
    num_orders
FROM `project.dataset.customers`
WHERE total_spent > 1000
LIMIT 10
"""

results = client.query(query)
for row in results:
    print(row.customer_id, row.total_spent)
```

### Key Concepts

#### 1. **Datasets**
- Logical containers for tables
- Organize related data
- Set access controls

#### 2. **Tables**
- Store data in columnar format
- Partitioned for performance
- Clustered for optimization

#### 3. **Queries**
- Standard SQL
- Fast execution
- Automatic optimization

#### 4. **Jobs**
- Query jobs
- Load jobs
- Export jobs

### Basic Example: Load Data

```python
from google.cloud import bigquery

client = bigquery.Client()

# Create dataset
dataset_id = "customer_data"
dataset = bigquery.Dataset(f"{client.project}.{dataset_id}")
dataset.location = "US"
dataset = client.create_dataset(dataset, exists_ok=True)

# Load data from CSV
table_id = f"{dataset_id}.customers"
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True
)

with open("customers.csv", "rb") as source_file:
    job = client.load_table_from_file(
        source_file, table_id, job_config=job_config
    )

job.result()  # Wait for job to complete
```

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Partitioning

```python
# Create partitioned table
table = bigquery.Table(table_ref)
table.schema = [
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("amount", "FLOAT"),
]

# Partition by date
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="timestamp"
)

table = client.create_table(table)
```

### Clustering

```python
# Create clustered table
table.clustering_fields = ["customer_id", "product_category"]

# Improves query performance for filters on these fields
```

### Query Optimization

```python
# Use query job configuration
job_config = bigquery.QueryJobConfig(
    use_query_cache=True,  # Use cached results
    use_legacy_sql=False,  # Use standard SQL
    maximum_bytes_billed=1000000000  # Limit query cost
)

query_job = client.query(query, job_config=job_config)
```

### Streaming Inserts

```python
# Real-time data insertion
rows_to_insert = [
    {"customer_id": "123", "amount": 100.0, "timestamp": "2024-01-01"},
    {"customer_id": "456", "amount": 200.0, "timestamp": "2024-01-01"},
]

errors = client.insert_rows_json(table_id, rows_to_insert)
if errors:
    print(f"Encountered errors: {errors}")
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Advanced Queries

```sql
-- Window functions
SELECT 
    customer_id,
    amount,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY timestamp) as running_total,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY timestamp DESC) as rn
FROM transactions
```

### BigQuery ML

```sql
-- Train ML model in BigQuery
CREATE OR REPLACE MODEL `dataset.churn_model`
OPTIONS(
    model_type='logistic_reg',
    input_label_cols=['is_churn']
) AS
SELECT
    total_spent,
    num_orders,
    days_since_last_order,
    is_churn
FROM training_data;

-- Make predictions
SELECT
    customer_id,
    predicted_is_churn,
    predicted_is_churn_probs[OFFSET(0)].prob as churn_probability
FROM ML.PREDICT(
    MODEL `dataset.churn_model`,
    (SELECT * FROM prediction_data)
)
```

### Data Transfer

```python
# Scheduled data transfer
from google.cloud import bigquery_datatransfer

transfer_client = bigquery_datatransfer.DataTransferServiceClient()

transfer_config = bigquery_datatransfer.TransferConfig(
    destination_dataset_id="target_dataset",
    display_name="Daily Transfer",
    data_source_id="google_cloud_storage",
    schedule="every 24 hours"
)

transfer_config = transfer_client.create_transfer_config(
    parent=parent,
    transfer_config=transfer_config
)
```

### Cost Optimization

```python
# Use dry run to estimate cost
job_config = bigquery.QueryJobConfig(dry_run=True)
query_job = client.query(query, job_config=job_config)
print(f"Query will process {query_job.total_bytes_processed} bytes")

# Use query cache
job_config.use_query_cache = True

# Limit bytes billed
job_config.maximum_bytes_billed = 1000000000  # 1GB limit
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Data Warehouse
```
Data Sources → BigQuery → Analytics
```

### Pattern 2: ETL Pipeline
```
Raw Data → BigQuery → Transform → Analytics Tables
```

### Pattern 3: Real-Time Analytics
```
Streaming Data → BigQuery → Real-Time Queries
```

---

## 🔗 Integration with Your POCs

### Module 02: Cloud AI Platform
- **Usage**: Store training data
- **Features**: Load data, query for training

### Module 04: ML Pipeline
- **Usage**: Data warehouse, feature store
- **Features**: Partitioning, clustering, streaming inserts

---

## 📊 Best Practices

### 1. **Use Partitioning**
```python
# Partition by date for time-series data
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="timestamp"
)
```

### 2. **Use Clustering**
```python
# Cluster by frequently filtered columns
table.clustering_fields = ["customer_id", "product_id"]
```

### 3. **Optimize Queries**
```sql
-- Use WHERE to filter early
-- Use LIMIT when possible
-- Avoid SELECT *
```

### 4. **Monitor Costs**
```python
# Use dry run
# Set maximum_bytes_billed
# Use query cache
```

### 5. **Use Appropriate Data Types**
```python
# Use DATE instead of STRING for dates
# Use NUMERIC for precise decimals
# Use INT64 for integers
```

---

## 🎯 Key Takeaways

1. **BigQuery = Serverless Data Warehouse**
2. **Partitioning = Faster Queries**
3. **Clustering = Better Performance**
4. **SQL = Standard Queries**
5. **Cost = Pay per Query**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with Module 02/04
5. 🎯 Explain it confidently

