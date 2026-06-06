# BigQuery Interview Questions and Answers

## Beginner Level Questions

### 1. What is BigQuery and why is it used?

**Answer:**
BigQuery is Google Cloud's fully managed, serverless data warehouse that enables super-fast SQL queries on massive datasets. It's used for:

- **Data Analytics**: Analyzing large volumes of data quickly
- **Business Intelligence**: Creating reports and dashboards
- **Data Warehousing**: Storing and querying structured data
- **Machine Learning**: Training ML models on large datasets

BigQuery separates storage from compute, allowing automatic scaling and pay-per-use pricing.

### 2. What are the main components of BigQuery?

**Answer:**
The main components are:

- **Datasets**: Logical containers that hold tables and views
- **Tables**: Data storage units (native, external, partitioned, clustered)
- **Jobs**: Operations like queries, loads, exports, and copies
- **Views**: Virtual tables defined by SQL queries
- **Materialized Views**: Pre-computed views for better performance

BigQuery also includes BI Engine for sub-second query responses and BigQuery ML for machine learning.

### 3. How do you create a dataset in BigQuery?

**Answer:**
You can create a dataset through:

**Web UI:**
1. Go to BigQuery in Google Cloud Console
2. Click "Create Dataset"
3. Enter dataset ID, location, and settings

**bq Command Line:**
```bash
bq mk --dataset --location=US my_dataset
```

**API:**
```python
from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "my_dataset"
dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"
dataset = client.create_dataset(dataset)
```

### 4. What is the difference between BigQuery and traditional databases?

**Answer:**
Key differences:

**BigQuery:**
- Serverless - no infrastructure management
- Columnar storage optimized for analytics
- Automatic scaling
- Pay per query (bytes processed)
- SQL-based queries on petabyte-scale data

**Traditional Databases:**
- Require server provisioning and management
- Row-based storage
- Fixed scaling limits
- Pay for server uptime
- May have different query languages

## Intermediate Level Questions

### 5. Explain partitioning and clustering in BigQuery.

**Answer:**

**Partitioning:**
- Divides table into segments based on a column
- Types: Time-based (DATE/TIMESTAMP), Integer range
- Improves query performance by scanning only relevant partitions
- Reduces costs by processing less data

```sql
-- Time-based partitioning
CREATE TABLE dataset.sales
PARTITION BY DATE(order_date)
AS SELECT * FROM source_table;
```

**Clustering:**
- Physically sorts data within partitions
- Based on one or more columns
- Further optimizes queries with filters on clustered columns
- Improves compression and query performance

```sql
-- Clustered table
CREATE TABLE dataset.sales
PARTITION BY DATE(order_date)
CLUSTER BY (customer_id, product_category)
AS SELECT * FROM source_table;
```

### 6. How do you load data into BigQuery?

**Answer:**
Multiple methods for loading data:

**Batch Loading:**
```sql
LOAD DATA INTO `project.dataset.table`
FROM FILES (
  format = 'CSV',
  uris = ['gs://bucket/file.csv']
);
```

**Streaming Inserts:**
```python
from google.cloud import bigquery

client = bigquery.Client()
table_id = "project.dataset.table"

rows = [{"column1": "value1", "column2": "value2"}]
client.insert_rows_json(table_id, rows)
```

**Data Transfer Service:**
- Scheduled transfers from Cloud Storage, Google Ads, etc.
- Incremental loading for changed data

**External Tables:**
```sql
CREATE EXTERNAL TABLE dataset.external_table
OPTIONS (
  format = 'CSV',
  uris = ['gs://bucket/*.csv']
);
```

### 7. What are BigQuery slots and how do they affect performance?

**Answer:**
Slots are units of computational capacity in BigQuery:

- **Definition**: Virtual CPUs that execute queries
- **Allocation**: Automatically managed by BigQuery
- **Performance Impact**: More slots = faster query execution
- **Pricing**: On-demand vs. flat-rate pricing

**Monitoring Slots:**
```sql
SELECT
  job_id,
  total_slot_time_ms,
  total_bytes_processed
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);
```

### 8. How do you optimize query performance in BigQuery?

**Answer:**
Query optimization techniques:

**Data Organization:**
- Use partitioning to reduce data scanned
- Apply clustering for sorted data access
- Choose appropriate data types

**Query Structure:**
- Select specific columns instead of SELECT *
- Use WHERE clauses to filter data early
- Avoid complex subqueries when possible

**Caching:**
- Query results are cached automatically
- Use materialized views for frequently accessed data

**Best Practices:**
```sql
-- Optimized query
SELECT
  customer_id,
  SUM(order_amount) as total_amount
FROM `project.dataset.orders`
WHERE order_date >= '2023-01-01'
  AND customer_region = 'US'
GROUP BY customer_id
ORDER BY total_amount DESC
LIMIT 100;
```

### 9. What is BigQuery ML and how does it work?

**Answer:**
BigQuery ML enables creating and executing machine learning models using SQL:

**Features:**
- Train models without exporting data
- Support for linear regression, classification, clustering
- Integration with Vertex AI for advanced models

**Example:**
```sql
-- Create a model
CREATE MODEL `project.dataset.customer_churn_model`
OPTIONS (
  model_type = 'logistic_reg',
  input_label_cols = ['churned']
) AS
SELECT
  tenure,
  monthly_charges,
  total_charges,
  churned
FROM `project.dataset.customers`;

-- Make predictions
SELECT
  customer_id,
  ML.PREDICT(MODEL `project.dataset.customer_churn_model`,
             STRUCT(tenure, monthly_charges, total_charges AS total_charges))
FROM `project.dataset.new_customers`;
```

### 10. How do you handle data security in BigQuery?

**Answer:**
BigQuery security features:

**Access Control:**
- IAM roles at project, dataset, and table levels
- Column-level security for sensitive data
- Row-level security with row access policies

**Encryption:**
- Data encrypted at rest with Google-managed keys
- Customer-managed encryption keys (CMEK)
- Data encrypted in transit

**Audit Logging:**
- Cloud Audit Logs for all operations
- Data access audit logs for query monitoring

**Compliance:**
- SOC 2, HIPAA, PCI DSS compliant
- Regional data residency options

## Advanced Level Questions

### 11. How do you implement real-time analytics with BigQuery?

**Answer:**
Real-time analytics implementation:

**Streaming Data:**
```sql
-- Query streaming data
SELECT
  event_type,
  COUNT(*) as event_count,
  TIMESTAMP_TRUNC(timestamp, MINUTE) as minute
FROM `project.dataset.events`
WHERE _PARTITIONTIME >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY event_type, minute
ORDER BY minute DESC;
```

**BI Engine:**
- In-memory analysis for sub-second queries
- Automatic caching of hot data
- Optimized for dashboard queries

**Real-time Dashboards:**
- Connected Sheets for real-time analysis
- Data Studio with BigQuery data sources
- Custom applications using BigQuery API

**Architecture:**
1. Stream data to BigQuery via Pub/Sub
2. Use streaming buffers for real-time access
3. Query recent data with time filters
4. Use BI Engine for fast aggregations

### 12. What are the cost optimization strategies for BigQuery?

**Answer:**
Cost optimization approaches:

**Query Optimization:**
- Use partitioning to reduce bytes processed
- Apply clustering for better compression
- Avoid SELECT * and use specific columns
- Use approximate functions for large datasets

**Storage Optimization:**
- Use long-term storage for infrequently accessed data
- Delete unnecessary tables and partitions
- Compress data efficiently

**Pricing Models:**
- On-demand for variable workloads
- Flat-rate for predictable, high-volume usage
- Reservations for committed usage

**Monitoring Costs:**
```sql
-- Monitor query costs
SELECT
  job_id,
  user_email,
  total_bytes_billed / POWER(1024, 4) AS tb_billed,
  total_bytes_processed / POWER(1024, 4) AS tb_processed
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) = CURRENT_DATE()
ORDER BY tb_billed DESC;
```

### 13. How do you handle schema evolution in BigQuery?

**Answer:**
Schema evolution strategies:

**Automatic Schema Detection:**
- BigQuery can auto-detect schema for CSV/JSON files
- Schema updates for streaming inserts

**Manual Schema Updates:**
```sql
-- Add columns
ALTER TABLE `project.dataset.table`
ADD COLUMN new_column STRING;

-- Modify columns
ALTER TABLE `project.dataset.table`
ALTER COLUMN existing_column SET DATA TYPE INT64;
```

**Schema Management:**
- Use schema files for consistent schemas
- Version control schema definitions
- Test schema changes in development environments

**Best Practices:**
- Plan schema changes carefully
- Use backward-compatible changes when possible
- Update dependent queries after schema changes
- Document schema evolution history

### 14. What is BigQuery Omni and how does it work?

**Answer:**
BigQuery Omni enables cross-cloud analytics:

**Features:**
- Query data across Google Cloud, AWS, and Azure
- No data movement required
- Unified billing and governance

**How it Works:**
- Federated queries to external data sources
- BigQuery's query engine processes data where it resides
- Results returned to the user's BigQuery project

**Example:**
```sql
-- Query AWS S3 data from BigQuery
SELECT *
FROM EXTERNAL_QUERY(
  "aws-us-east-1",
  "SELECT * FROM s3_table"
);
```

**Use Cases:**
- Multi-cloud data analysis
- Data lake analytics without migration
- Cross-cloud reporting and dashboards

### 15. How do you implement data governance in BigQuery?

**Answer:**
Data governance implementation:

**Data Catalog:**
- Tag datasets and tables with metadata
- Document data lineage and usage
- Maintain data dictionary

**Access Control:**
- Implement least privilege access
- Use groups for role-based access
- Regular access reviews

**Data Quality:**
- Implement data validation rules
- Monitor data freshness and completeness
- Set up data quality alerts

**Compliance:**
- Enable audit logging
- Implement data retention policies
- Support for regulatory compliance (GDPR, CCPA)

**Tools:**
- Dataplex for data governance
- Data Catalog for metadata management
- Cloud DLP for sensitive data protection

### 16. What are the limitations of BigQuery?

**Answer:**
BigQuery limitations to consider:

**Query Limitations:**
- Maximum 6 concurrent interactive queries per user
- Query timeout of 6 hours for interactive queries
- Maximum response size of 10 GB for interactive queries

**Data Loading:**
- Maximum file size of 5 TB for batch loads
- Streaming inserts limited to 1,000 rows per request
- Maximum 10 MB per streaming request

**Storage:**
- Table names limited to 1,024 characters
- Maximum 10,000 columns per table
- Partition limit of 4,000 partitions per partitioned table

**Cost Considerations:**
- Can become expensive for frequent small queries
- No free tier for storage
- Minimum 10 MB billing per query

### 17. How do you monitor BigQuery performance and usage?

**Answer:**
Monitoring BigQuery:

**System Tables:**
```sql
-- Query performance monitoring
SELECT
  job_id,
  query,
  start_time,
  end_time,
  total_bytes_processed,
  total_slot_time_ms,
  cache_hit
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR);
```

**Key Metrics:**
- Query execution time
- Bytes processed vs. billed
- Slot utilization
- Cache hit rates
- Error rates

**Monitoring Tools:**
- Cloud Monitoring for BigQuery metrics
- Custom dashboards in Looker/Data Studio
- Alerting on performance thresholds

**Performance Analysis:**
- Identify slow queries
- Monitor resource usage
- Track cost trends
- Optimize frequently run queries

### 18. How do you implement CI/CD for BigQuery?

**Answer:**
CI/CD for BigQuery:

**Infrastructure as Code:**
```yaml
# Terraform for BigQuery resources
resource "google_bigquery_dataset" "dataset" {
  dataset_id = "analytics"
  location   = "US"
}

resource "google_bigquery_table" "table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "users"
  schema     = file("schemas/users.json")
}
```

**Query Deployment:**
- Store SQL queries in version control
- Use deployment pipelines to update views and procedures
- Test queries in development environments

**Data Pipeline CI/CD:**
- Use Cloud Build for automated testing
- Implement data validation tests
- Automate schema migrations

**Best Practices:**
- Separate development, staging, and production environments
- Use service accounts for automated deployments
- Implement proper testing for data pipelines

### 19. What are materialized views in BigQuery and when to use them?

**Answer:**
Materialized views are pre-computed query results stored as tables:

**Benefits:**
- Faster query performance for complex aggregations
- Automatic refresh based on base table changes
- Cost savings for frequently accessed data

**When to Use:**
- Complex aggregations queried frequently
- Dashboard queries requiring fast response
- Data that changes predictably

**Example:**
```sql
CREATE MATERIALIZED VIEW `project.dataset.sales_summary`
OPTIONS (
  enable_refresh = true,
  refresh_interval_minutes = 60
)
AS SELECT
  customer_id,
  DATE(order_date) as order_date,
  SUM(order_amount) as total_amount,
  COUNT(*) as order_count
FROM `project.dataset.orders`
GROUP BY customer_id, DATE(order_date);
```

**Considerations:**
- Storage costs for the materialized view
- Refresh frequency vs. data freshness needs
- Query patterns that benefit from pre-computation

### 20. How do you handle data quality in BigQuery?

**Answer:**
Data quality management:

**Validation Rules:**
```sql
-- Data quality checks
SELECT
  COUNT(*) as total_rows,
  COUNTIF(column1 IS NULL) as null_count,
  COUNTIF(column1 NOT IN ('valid_value1', 'valid_value2')) as invalid_count,
  AVG(CASE WHEN column2 BETWEEN 0 AND 100 THEN column2 ELSE NULL END) as avg_valid_score
FROM `project.dataset.table`;
```

**Quality Monitoring:**
- Implement automated data quality checks
- Set up alerts for quality threshold breaches
- Monitor data freshness and completeness

**Data Profiling:**
- Analyze data distributions and patterns
- Identify outliers and anomalies
- Document data quality expectations

**Tools:**
- BigQuery Data Quality API
- Custom validation queries
- Integration with external data quality tools

## Scenario-Based Questions

### 21. How would you design a data warehouse for an e-commerce company?

**Answer:**
E-commerce data warehouse design:

**Data Sources:**
- Transaction data from order management system
- Customer data from CRM
- Product catalog data
- Website analytics data
- Inventory management data

**Schema Design:**
```sql
-- Fact table
CREATE TABLE `ecommerce.fact_orders` (
  order_id INT64,
  customer_id INT64,
  product_id INT64,
  order_date DATE,
  quantity INT64,
  unit_price NUMERIC,
  total_amount NUMERIC
)
PARTITION BY order_date
CLUSTER BY customer_id;

-- Dimension tables
CREATE TABLE `ecommerce.dim_customers` (
  customer_id INT64,
  customer_name STRING,
  email STRING,
  registration_date DATE,
  customer_segment STRING
);

CREATE TABLE `ecommerce.dim_products` (
  product_id INT64,
  product_name STRING,
  category STRING,
  brand STRING,
  price NUMERIC
);
```

**ETL Pipeline:**
- Use Dataflow for data processing
- Implement incremental loading
- Add data quality checks

**Analytics Layer:**
- Create aggregated views for reporting
- Implement BigQuery ML for customer segmentation
- Set up real-time dashboards

### 22. How would you optimize a slow BigQuery query?

**Answer:**
Query optimization process:

1. **Analyze Query Execution:**
```sql
SELECT
  job_id,
  query,
  total_bytes_processed,
  total_slot_time_ms,
  TIMESTAMP_DIFF(end_time, start_time, SECOND) as execution_time
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE job_id = 'your_job_id';
```

2. **Identify Bottlenecks:**
- Check bytes processed vs. expected
- Look for full table scans
- Identify expensive operations (JOINs, aggregations)

3. **Apply Optimizations:**
- Add partitioning/clustering
- Rewrite query to be more selective
- Use approximate functions if precision isn't critical
- Consider materialized views for repeated queries

4. **Test and Validate:**
- Compare execution time and cost
- Ensure results remain accurate
- Monitor ongoing performance

### 23. How would you implement GDPR compliance in BigQuery?

**Answer:**
GDPR compliance implementation:

**Data Mapping:**
- Catalog all personal data in BigQuery
- Document data retention periods
- Identify data subjects and controllers

**Access Controls:**
- Implement row-level security for personal data
- Use column-level access for sensitive fields
- Regular access review processes

**Data Subject Rights:**
- Implement data deletion procedures
- Create data export capabilities
- Document data processing purposes

**Technical Implementation:**
```sql
-- Row access policy for GDPR
CREATE ROW ACCESS POLICY gdpr_policy
ON `project.dataset.customer_data`
GRANT TO ("user@example.com")
FILTER USING (consent_given = true AND data_retention_date > CURRENT_DATE());
```

**Audit and Monitoring:**
- Enable comprehensive audit logging
- Monitor data access patterns
- Implement breach notification procedures

## Summary

BigQuery interview questions typically cover:
- Basic concepts and architecture
- Data loading and management
- Query optimization and performance
- Security and compliance
- Integration with Google Cloud ecosystem
- Cost optimization strategies
- Real-world implementation scenarios

Focus on understanding BigQuery's serverless nature, optimization techniques, and integration capabilities rather than just SQL syntax.
