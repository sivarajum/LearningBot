# BigQuery Interview Questions and Answers

## Beginner Level Questions

### Q1: What is BigQuery and what are its key features?

**Answer:**
BigQuery is Google Cloud's fully managed, serverless data warehouse designed for large-scale analytics. It enables super-fast SQL queries using the processing power of Google's infrastructure.

**Key Features:**
- **Serverless**: No infrastructure management, automatic scaling
- **Fast queries**: Processes petabytes of data in seconds
- **SQL-based**: Standard SQL queries with extensions
- **Cost-effective**: Pay only for data stored and queries run
- **Integration**: Works with Google Cloud services and third-party tools
- **Real-time analytics**: Supports streaming data and real-time queries

**Use Cases:**
- Data warehousing and analytics
- Business intelligence and reporting
- Log analysis and monitoring
- Machine learning with BigQuery ML
- Real-time data processing

### Q2: Explain BigQuery's architecture and how it stores data.

**Answer:**

**Architecture:**
- **Columnar storage**: Data stored in columns for efficient analytics
- **Distributed processing**: Queries run across thousands of machines
- **Separation of storage and compute**: Storage and compute scale independently
- **Dremel engine**: Google's distributed query engine

**Storage:**
- **Datasets**: Containers for tables (like databases)
- **Tables**: Collections of rows and columns
- **Partitions**: Divide tables by date or integer ranges
- **Clusters**: Organize data within partitions for optimization

**Data Formats:**
- Native BigQuery storage (columnar format)
- External tables (Cloud Storage, Drive, etc.)
- Streaming inserts for real-time data

### Q3: What is the difference between a dataset and a table in BigQuery?

**Answer:**

**Dataset:**
- Container for tables, views, and models
- Similar to a database in traditional systems
- Defines access control and location
- Can contain multiple tables

**Table:**
- Collection of rows and columns
- Stores actual data
- Can be partitioned and clustered
- Supports schema definition

**Example:**
```sql
-- Create dataset
CREATE SCHEMA IF NOT EXISTS `my-project.my_dataset`
OPTIONS(
  location='US',
  description='My dataset for analytics'
);

-- Create table
CREATE TABLE `my-project.my_dataset.my_table` (
  id INT64,
  name STRING,
  created_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY id;
```

### Q4: How does BigQuery handle large-scale data processing?

**Answer:**

**Processing Mechanisms:**

**Columnar Storage:**
- Data stored by column, not by row
- Enables efficient compression and scanning
- Only reads required columns for queries

**Distributed Execution:**
- Queries parallelized across thousands of machines
- Automatic query optimization and execution planning
- Dynamic resource allocation based on query complexity

**Caching:**
- Results cached for repeated queries
- Metadata caching for faster schema access
- Query result caching for identical queries

**Example:**
```sql
-- BigQuery automatically optimizes this query
SELECT 
  user_id,
  COUNT(*) as event_count
FROM `my-project.my_dataset.events`
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY user_id
ORDER BY event_count DESC
LIMIT 100;
```

### Q5: Explain BigQuery partitioning and clustering.

**Answer:**

**Partitioning:**
- Divides tables into segments based on partition key
- Improves query performance and reduces costs
- Types: Date, timestamp, integer range, ingestion time

**Clustering:**
- Organizes data within partitions by cluster keys
- Improves query performance for filtered queries
- Up to 4 clustering columns
- Works with partitioning for optimal performance

**Example:**
```sql
CREATE TABLE `my-project.my_dataset.events` (
  event_id STRING,
  user_id INT64,
  event_type STRING,
  event_timestamp TIMESTAMP,
  event_data JSON
)
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_id, event_type;
```

## Intermediate Level Questions

### Q6: What are the cost optimization strategies in BigQuery?

**Answer:**

**Cost Optimization:**

**Storage Costs:**
- Use partitioning to reduce scanned data
- Set appropriate expiration times
- Use clustering for frequently queried columns
- Compress data before loading

**Query Costs:**
- Use SELECT * only when necessary
- Filter early in the query
- Use partitioned columns in WHERE clauses
- Leverage query result caching
- Use approximate aggregation functions

**Best Practices:**
```sql
-- Good: Filter on partitioned column
SELECT * FROM events
WHERE event_date = '2024-01-01';

-- Better: Select only needed columns
SELECT user_id, event_type, event_timestamp
FROM events
WHERE event_date = '2024-01-01'
  AND event_type = 'purchase';
```

### Q7: Explain BigQuery's streaming inserts and batch loading.

**Answer:**

**Streaming Inserts:**
- Real-time data insertion via API
- Low latency (seconds to minutes)
- Higher cost than batch loading
- Best for real-time analytics

**Batch Loading:**
- Bulk data loading from Cloud Storage
- Lower cost than streaming
- Higher latency (minutes to hours)
- Best for historical data and ETL

**Example:**
```python
from google.cloud import bigquery

# Streaming insert
client = bigquery.Client()
table = client.get_table('my-project.my_dataset.my_table')

rows_to_insert = [
    {'id': 1, 'name': 'Alice', 'timestamp': '2024-01-01 10:00:00'},
    {'id': 2, 'name': 'Bob', 'timestamp': '2024-01-01 11:00:00'}
]

errors = client.insert_rows(table, rows_to_insert)
```

### Q8: What is BigQuery ML and how does it work?

**Answer:**

**BigQuery ML:**
- Enables machine learning using SQL
- Trains and deploys models directly in BigQuery
- No need to export data or use external ML tools
- Supports various model types

**Supported Models:**
- Linear regression
- Logistic regression
- K-means clustering
- Matrix factorization
- TensorFlow models (imported)

**Example:**
```sql
-- Create model
CREATE MODEL `my-project.my_dataset.my_model`
OPTIONS(
  model_type='linear_reg',
  input_label_cols=['price']
) AS
SELECT
  features,
  price
FROM `my-project.my_dataset.training_data`;

-- Make predictions
SELECT
  predicted_price
FROM ML.PREDICT(
  MODEL `my-project.my_dataset.my_model`,
  (SELECT features FROM `my-project.my_dataset.test_data`)
);
```

## Advanced Level Questions

### Q9: How do you handle data quality and validation in BigQuery?

**Answer:**

**Data Quality Strategies:**

**Schema Validation:**
- Define strict schemas for tables
- Use data type constraints
- Validate data on ingestion

**Data Validation Queries:**
```sql
-- Check for duplicates
SELECT 
  user_id,
  COUNT(*) as count
FROM users
GROUP BY user_id
HAVING COUNT(*) > 1;

-- Check for null values
SELECT 
  COUNT(*) as total_rows,
  COUNT(user_id) as non_null_user_id,
  COUNT(email) as non_null_email
FROM users;
```

**Data Quality Monitoring:**
- Set up scheduled queries for data quality checks
- Use Dataform for data transformation and validation
- Implement data profiling and monitoring
- Create alerts for data quality issues

### Q10: Explain BigQuery's security and access control.

**Answer:**

**Access Control:**
- **IAM roles**: Project, dataset, and table-level permissions
- **Row-level security**: Filter data at row level
- **Column-level security**: Mask sensitive columns
- **Authorized views**: Limit data access through views

**Security Features:**
- **Encryption**: Data encrypted at rest and in transit
- **VPC Service Controls**: Network-level security
- **Audit logging**: Track all data access
- **Data residency**: Control data location

**Example:**
```sql
-- Row-level security
CREATE ROW ACCESS POLICY user_data_policy
ON `my-project.my_dataset.users`
GRANT TO ('user@example.com')
FILTER USING (user_id = SESSION_USER());

-- Authorized view
CREATE VIEW `my-project.my_dataset.user_summary`
OPTIONS(
  description='Authorized view for user summaries'
) AS
SELECT 
  user_id,
  COUNT(*) as event_count
FROM `my-project.my_dataset.events`
GROUP BY user_id;
```

### Q11: How do you optimize BigQuery queries for performance?

**Answer:**

**Performance Optimization:**

**Query Optimization:**
- Use partitioned columns in WHERE clauses
- Leverage clustering for filtered queries
- Avoid SELECT * - select only needed columns
- Use approximate functions when exactness isn't required
- Optimize JOIN operations

**Example:**
```sql
-- Optimized query
SELECT 
  user_id,
  event_type,
  COUNT(*) as event_count
FROM `my-project.my_dataset.events`
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
  AND user_id IN (1, 2, 3)  -- Uses clustering
GROUP BY user_id, event_type;
```

**Table Optimization:**
- Partition large tables by date or integer
- Cluster tables by frequently filtered columns
- Use appropriate data types
- Compress data before loading

### Q12: Explain BigQuery's integration with other Google Cloud services.

**Answer:**

**Integration Points:**

**Cloud Storage:**
- Load data from Cloud Storage buckets
- Export query results to Cloud Storage
- Use external tables for Cloud Storage data

**Dataflow:**
- Stream processing with Dataflow
- Write results to BigQuery
- Real-time data pipeline integration

**Cloud Functions:**
- Trigger functions on BigQuery events
- Process data and write back to BigQuery
- Event-driven data processing

**Looker/Data Studio:**
- Connect for visualization and reporting
- Real-time dashboards
- Business intelligence integration

**Example:**
```python
from google.cloud import bigquery
from google.cloud import storage

# Load from Cloud Storage
client = bigquery.Client()
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True
)

uri = 'gs://my-bucket/data.csv'
table_id = 'my-project.my_dataset.my_table'

load_job = client.load_table_from_uri(
    uri, table_id, job_config=job_config
)
load_job.result()
```

---

## Key Takeaways

1. **BigQuery is a serverless data warehouse** for large-scale analytics
2. **Columnar storage and distributed processing** enable fast queries
3. **Partitioning and clustering** optimize query performance and costs
4. **BigQuery ML enables ML with SQL** without exporting data
5. **Cost optimization** through efficient querying and data management
6. **Integration with Google Cloud services** for complete data solutions
7. **Security and access control** at multiple levels (IAM, row-level, column-level)

