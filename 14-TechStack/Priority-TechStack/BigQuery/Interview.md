# BigQuery - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your BigQuery interviews. Answers connect to your POC projects.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is BigQuery and why use it?

**Answer:**
"BigQuery is Google Cloud's fully managed, serverless data warehouse. It enables super-fast SQL queries on massive datasets without managing infrastructure.

I used it in Modules 02 and 04 because:

1. **Serverless**: No infrastructure to manage
2. **Fast**: Queries petabytes in seconds
3. **Scalable**: Automatic scaling
4. **Cost-Effective**: Pay only for storage and queries
5. **Integrated**: Works seamlessly with other GCP services

In Module 04, I use BigQuery as my data warehouse, storing customer data and features. It integrates perfectly with Vertex AI for ML training."

**Key Points:**
- Serverless data warehouse
- Fast SQL queries
- Automatic scaling
- Cost-effective

---

### Q2: How does BigQuery achieve fast query performance?

**Answer:**
"BigQuery uses several techniques:

**1. Columnar Storage**
- Data stored in columns, not rows
- Only reads needed columns
- Better compression

**2. Distributed Processing**
- Queries split across many workers
- Parallel processing
- Automatic scaling

**3. Partitioning**
- Data split into partitions (by date, etc.)
- Only scans relevant partitions
- Reduces data scanned

**4. Clustering**
- Data sorted within partitions
- Faster filtering and joins
- Better compression

**5. Automatic Optimization**
- Query optimizer chooses best plan
- Caching of results
- Predicate pushdown

In Module 04, I partition my customer data by date and cluster by customer_id, which makes queries 10x faster."

**Key Points:**
- Columnar storage
- Distributed processing
- Partitioning
- Clustering
- Query optimization

---

### Q3: What's the difference between partitioning and clustering?

**Answer:**
"**Partitioning**: Divides table into segments (usually by date or integer range). When you query with a partition filter, BigQuery only scans that partition.

**Example:**
```sql
-- Partitioned by date
SELECT * FROM transactions
WHERE date = '2024-01-01'  -- Only scans Jan 1 partition
```

**Clustering**: Sorts data within partitions by specified columns. Improves filtering and joins on those columns.

**Example:**
```sql
-- Clustered by customer_id
SELECT * FROM transactions
WHERE customer_id = '123'  -- Fast lookup due to clustering
```

**Best Practice**: Use both - partition by time, cluster by frequently filtered columns.

In Module 04, I partition by timestamp and cluster by customer_id, giving me fast time-range queries and fast customer lookups."

**Key Points:**
- Partitioning = divides table
- Clustering = sorts within partitions
- Use both for best performance

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How do you optimize BigQuery queries for cost and performance?

**Answer:**
"**Cost Optimization:**

**1. Reduce Data Scanned**
```sql
-- Use WHERE to filter early
SELECT * FROM large_table
WHERE date = '2024-01-01'  -- Filters before processing

-- Use LIMIT
SELECT * FROM table LIMIT 100

-- Avoid SELECT *
SELECT customer_id, amount  -- Only needed columns
```

**2. Use Partitioning**
```sql
-- Partitioned table scans less data
SELECT * FROM partitioned_table
WHERE date BETWEEN '2024-01-01' AND '2024-01-31'
```

**3. Use Query Cache**
```python
job_config.use_query_cache = True  # Reuse results
```

**4. Set Limits**
```python
job_config.maximum_bytes_billed = 1000000000  # 1GB limit
```

**Performance Optimization:**

**1. Use Clustering**
- Cluster by frequently filtered columns
- Improves filter performance

**2. Use Appropriate Data Types**
- DATE instead of STRING for dates
- INT64 for integers
- NUMERIC for precise decimals

**3. Avoid Nested Loops**
- Use JOINs instead of subqueries when possible
- Use window functions efficiently

In Module 04, I optimize by partitioning by date, clustering by customer_id, and always using WHERE clauses to minimize data scanned."

**Key Points:**
- Reduce data scanned
- Use partitioning/clustering
- Query cache
- Appropriate data types

---

### Q5: How does BigQuery handle streaming data?

**Answer:**
"BigQuery supports streaming inserts for real-time data:

**Streaming Insert:**
```python
rows = [{"customer_id": "123", "amount": 100.0}]
errors = client.insert_rows_json(table_id, rows)
```

**Characteristics:**
- **Low Latency**: Data available within seconds
- **Exactly-Once**: Guaranteed delivery
- **High Throughput**: Millions of rows per second
- **Buffering**: Data buffered before queryable

**Use Cases:**
- Real-time analytics
- Event tracking
- IoT data ingestion

**Limitations:**
- Slightly higher cost than batch
- Data not immediately queryable (few seconds delay)

In Module 04, I use streaming inserts for real-time customer events, which then get processed in my ML pipeline."

**Key Points:**
- Real-time insertion
- Low latency
- High throughput
- Slight delay before queryable

---

### Q6: Explain BigQuery ML.

**Answer:**
"BigQuery ML allows you to train and use ML models directly in BigQuery using SQL:

**Training:**
```sql
CREATE MODEL `dataset.churn_model`
OPTIONS(model_type='logistic_reg') AS
SELECT
    total_spent,
    num_orders,
    is_churn
FROM training_data;
```

**Prediction:**
```sql
SELECT
    customer_id,
    predicted_is_churn
FROM ML.PREDICT(
    MODEL `dataset.churn_model`,
    (SELECT * FROM prediction_data)
)
```

**Benefits:**
- No data movement (train where data lives)
- SQL-based (familiar interface)
- Integrated with BigQuery
- Fast for large datasets

**Limitations:**
- Limited model types
- Less control than custom training

I use BigQuery ML for quick prototypes, then move to Vertex AI for production models with more control."

**Key Points:**
- Train ML in SQL
- No data movement
- Limited model types
- Good for prototypes

---

## 🔴 ADVANCED LEVEL Questions

### Q7: How would you design a data warehouse architecture using BigQuery?

**Answer:**
"**Medallion Architecture:**

**Bronze Layer (Raw):**
- Store raw data as-is
- No transformations
- Partitioned by ingestion date
- Long retention

**Silver Layer (Cleaned):**
- Cleaned and validated data
- Standardized schemas
- Partitioned by business date
- Data quality checks

**Gold Layer (Analytics):**
- Aggregated and enriched
- Business-ready tables
- Optimized for queries
- Partitioned and clustered

**Implementation:**
```sql
-- Bronze: Raw data
CREATE TABLE bronze.events
PARTITION BY DATE(timestamp)
AS SELECT * FROM source;

-- Silver: Cleaned
CREATE TABLE silver.events
PARTITION BY DATE(timestamp)
CLUSTER BY customer_id
AS 
SELECT 
    customer_id,
    event_type,
    timestamp,
    -- Cleaned fields
FROM bronze.events
WHERE timestamp IS NOT NULL;

-- Gold: Analytics
CREATE TABLE gold.customer_daily_stats
PARTITION BY DATE(date)
CLUSTER BY customer_id
AS
SELECT 
    customer_id,
    DATE(timestamp) as date,
    COUNT(*) as event_count,
    SUM(amount) as total_amount
FROM silver.events
GROUP BY customer_id, DATE(timestamp);
```

**Benefits:**
- Clear data lineage
- Incremental processing
- Easy debugging
- Optimized for different use cases

In Module 04, I implement this pattern for my ML pipeline data."

**Key Points:**
- Bronze/Silver/Gold layers
- Incremental processing
- Data quality
- Optimization per layer

---

### Q8: How do you handle data quality and validation in BigQuery?

**Answer:**
"**Data Quality Strategies:**

**1. Schema Validation**
```python
# Define strict schema
schema = [
    bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("amount", "FLOAT", mode="REQUIRED"),
]

job_config.schema = schema
job_config.write_disposition = "WRITE_APPEND"
```

**2. Data Quality Checks**
```sql
-- Check for nulls
SELECT COUNT(*) as null_count
FROM table
WHERE customer_id IS NULL;

-- Check for duplicates
SELECT customer_id, COUNT(*) as count
FROM table
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check ranges
SELECT COUNT(*) as invalid_amounts
FROM table
WHERE amount < 0 OR amount > 1000000;
```

**3. Validation Queries**
```python
# Run validation before loading
validation_query = """
SELECT 
    COUNT(*) as total_rows,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(CASE WHEN amount < 0 THEN 1 ELSE 0 END) as negative_amounts
FROM staging_table
"""

results = client.query(validation_query).result()
if results.negative_amounts > 0:
    raise ValueError("Data quality check failed")
```

**4. Data Quality Views**
```sql
-- Create data quality dashboard
CREATE VIEW data_quality_metrics AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_rows,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(amount) as avg_amount,
    COUNT(CASE WHEN amount IS NULL THEN 1 END) as null_amounts
FROM transactions
GROUP BY DATE(timestamp);
```

In Module 04, I implement validation checks before feature engineering to ensure data quality."

**Key Points:**
- Schema validation
- Data quality checks
- Validation queries
- Monitoring

---

### Q9: How would you optimize BigQuery for a high-volume analytics workload?

**Answer:**
"**Optimization Strategies:**

**1. Table Design**
- Partition by time (daily)
- Cluster by frequently filtered columns
- Use appropriate data types
- Denormalize for read performance

**2. Query Optimization**
- Use materialized views for common queries
- Pre-aggregate data in gold layer
- Use query cache
- Batch similar queries

**3. Cost Management**
- Use dry run to estimate costs
- Set maximum_bytes_billed
- Use scheduled queries for reports
- Archive old data

**4. Performance Tuning**
```sql
-- Materialized view for common aggregations
CREATE MATERIALIZED VIEW gold.daily_stats AS
SELECT 
    DATE(timestamp) as date,
    customer_id,
    SUM(amount) as daily_total,
    COUNT(*) as daily_count
FROM silver.transactions
GROUP BY DATE(timestamp), customer_id;

-- Query uses materialized view (faster)
SELECT * FROM gold.daily_stats
WHERE date = '2024-01-01';
```

**5. Monitoring**
- Track query performance
- Monitor costs
- Identify slow queries
- Optimize based on usage patterns

**Architecture:**
- Bronze: Raw data (partitioned)
- Silver: Cleaned (partitioned + clustered)
- Gold: Aggregated (materialized views)

This architecture handles high-volume analytics efficiently."

**Key Points:**
- Table design
- Materialized views
- Cost management
- Performance monitoring

---

### Q10: How do you handle data updates and deletes in BigQuery?

**Answer:**
"BigQuery handles updates/deletes differently:

**1. DML Statements (UPDATE/DELETE)**
```sql
-- Update
UPDATE dataset.table
SET amount = 200.0
WHERE customer_id = '123';

-- Delete
DELETE FROM dataset.table
WHERE date < '2024-01-01';
```

**2. Merge for Upserts**
```sql
MERGE dataset.target_table T
USING dataset.source_table S
ON T.customer_id = S.customer_id
WHEN MATCHED THEN
    UPDATE SET amount = S.amount
WHEN NOT MATCHED THEN
    INSERT (customer_id, amount) VALUES (S.customer_id, S.amount);
```

**3. Partition Replacement**
```python
# Replace entire partition
job_config.write_disposition = "WRITE_TRUNCATE"
job_config.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="date"
)
```

**4. Best Practices**
- Use MERGE for upserts
- Replace partitions for full refresh
- Use expiration for automatic cleanup
- Consider append-only design

**Append-Only Pattern:**
- Never update/delete
- Add new records with timestamps
- Query latest version using window functions
- More efficient for large datasets

In Module 04, I use append-only for events and MERGE for customer master data."

**Key Points:**
- DML for updates/deletes
- MERGE for upserts
- Partition replacement
- Append-only pattern

---

## 🎯 System Design Questions

### Q11: Design a data pipeline using BigQuery.

**Answer:**
"**Architecture:**

**1. Ingestion Layer**
- Batch: Cloud Storage → BigQuery Load
- Streaming: Pub/Sub → BigQuery Streaming
- External: Data Transfer Service

**2. Processing Layer**
- Bronze: Raw data storage
- Silver: Transformation queries
- Gold: Aggregated analytics tables

**3. Serving Layer**
- Direct queries for analytics
- Materialized views for dashboards
- Export to other systems

**4. Monitoring**
- Query performance tracking
- Cost monitoring
- Data quality checks

**Flow:**
```
Data Sources → Ingestion → Bronze → 
  → Transform → Silver → Aggregate → Gold →
  → Analytics/ML
```

**Optimization:**
- Partitioning at each layer
- Clustering for performance
- Materialized views for common queries
- Scheduled queries for ETL

This is the architecture I use in Module 04 for my ML pipeline."

---

## 💡 STAR Framework Examples

### Situation: Optimizing BigQuery Queries

**Situation**: Queries were slow and expensive on large dataset.

**Task**: Optimize BigQuery queries for performance and cost.

**Action**: 
- Implemented partitioning by date
- Added clustering by customer_id
- Created materialized views for common queries
- Optimized SQL (WHERE clauses, LIMIT)
- Used query cache

**Result**: 
- Query time reduced from 30s to 2s
- Cost reduced by 80%
- Better user experience

---

## 📊 Quick Reference

### Key Concepts
1. **Serverless**: No infrastructure
2. **Columnar**: Fast analytics
3. **Partitioning**: Faster queries
4. **Clustering**: Better filtering
5. **SQL**: Standard queries
6. **Cost**: Pay per query

### Common Interview Topics
- Query optimization
- Partitioning/clustering
- Cost optimization
- Data warehouse design
- Streaming data

---

## ✅ Practice Checklist

- [ ] Can explain BigQuery in 2 minutes
- [ ] Understand partitioning/clustering
- [ ] Know query optimization
- [ ] Understand cost optimization
- [ ] Know data warehouse patterns
- [ ] Can explain your POC usage
- [ ] Ready for system design questions

---

**Remember**: Connect answers to your actual POC projects (Modules 02, 04).

