# BigQuery: Serverless Data Warehouse

## Overview

BigQuery is Google's fully managed, serverless data warehouse that enables super-fast SQL queries using the processing power of Google's infrastructure. It can handle petabytes of data and provides real-time analytics with zero operational overhead.

## Core Concepts

### Architecture
- **Serverless**: No infrastructure management required
- **Columnar Storage**: Optimized for analytical queries
- **Distributed Processing**: Automatic scaling across thousands of nodes
- **Multi-cloud**: Available on GCP, AWS, and Azure

### Key Components
- **Datasets**: Logical containers for tables
- **Tables**: Structured data storage
- **Views**: Virtual tables based on SQL queries
- **Materialized Views**: Pre-computed views for performance
- **Partitions**: Data organization by date/time or range
- **Clusters**: Column-based sorting for query optimization

## Getting Started

### Basic Setup

```python
from google.cloud import bigquery
import pandas as pd

# Initialize BigQuery client
client = bigquery.Client()

# Define project and dataset
project_id = 'your-project-id'
dataset_id = 'your_dataset'
table_id = f'{project_id}.{dataset_id}.your_table'
```

### Creating Datasets and Tables

```sql
-- Create dataset
CREATE SCHEMA `your-project-id.your_dataset`
OPTIONS (
  location = 'US',
  description = 'Dataset for analytics'
);

-- Create table with schema
CREATE TABLE `your-project-id.your_dataset.sales` (
  order_id INT64,
  customer_id INT64,
  product_id INT64,
  quantity INT64,
  unit_price FLOAT64,
  order_date DATE,
  created_at TIMESTAMP
)
PARTITION BY DATE(order_date)
CLUSTER BY customer_id;
```

## Data Ingestion

### Batch Loading

```python
# Load data from Cloud Storage
def load_csv_from_gcs(uri, table_id):
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )

    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )

    load_job.result()  # Wait for the job to complete
    print(f"Loaded {load_job.output_rows} rows")

# Usage
uri = "gs://your-bucket/sales_data.csv"
table_id = "your-project-id.your_dataset.sales"
load_csv_from_gcs(uri, table_id)
```

### Streaming Inserts

```python
def stream_data_to_bigquery(rows_to_insert, table_id):
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Errors occurred: {errors}")
    else:
        print("Data streamed successfully")

# Usage
rows_to_insert = [
    {
        "order_id": 1001,
        "customer_id": 12345,
        "product_id": 67890,
        "quantity": 2,
        "unit_price": 29.99,
        "order_date": "2024-01-15",
        "created_at": "2024-01-15T10:30:00Z"
    }
]

table_id = "your-project-id.your_dataset.sales"
stream_data_to_bigquery(rows_to_insert, table_id)
```

### Data Transfer Service

```python
from google.cloud import bigquery_datatransfer_v1

def create_data_transfer_config():
    client = bigquery_datatransfer_v1.DataTransferServiceClient()

    transfer_config = bigquery_datatransfer_v1.TransferConfig(
        display_name="Daily Sales Data Transfer",
        data_source_id="google_cloud_storage",
        params={
            "data_path_template": "gs://your-bucket/sales_{run_date}.csv",
            "destination_table_name_template": "sales_{run_date}",
            "file_format": "CSV",
            "skip_leading_rows": "1",
            "allow_quoted_newlines": "true"
        },
        destination_dataset_id="your_dataset",
        schedule="every 24 hours",
        data_refresh_window_days=30,
    )

    response = client.create_transfer_config(
        parent=f"projects/{project_id}/locations/us",
        transfer_config=transfer_config,
    )

    return response
```

## Querying Data

### Basic SQL Queries

```sql
-- Simple SELECT
SELECT
  customer_id,
  COUNT(*) as order_count,
  SUM(quantity * unit_price) as total_revenue
FROM `your-project-id.your_dataset.sales`
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;

-- Time-based analysis
SELECT
  DATE(order_date) as order_day,
  COUNT(*) as daily_orders,
  SUM(quantity * unit_price) as daily_revenue
FROM `your-project-id.your_dataset.sales`
WHERE order_date >= '2024-01-01'
GROUP BY DATE(order_date)
ORDER BY order_day;
```

### Advanced Analytics

```sql
-- Window functions
SELECT
  customer_id,
  order_date,
  quantity * unit_price as order_value,
  SUM(quantity * unit_price) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) as cumulative_revenue,
  AVG(quantity * unit_price) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
    ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
  ) as moving_avg_5_orders
FROM `your-project-id.your_dataset.sales`
ORDER BY customer_id, order_date;

-- Statistical analysis
SELECT
  product_id,
  COUNT(*) as total_orders,
  AVG(quantity) as avg_quantity,
  STDDEV(quantity) as quantity_stddev,
  APPROX_COUNT_DISTINCT(customer_id) as unique_customers,
  PERCENTILE_CONT(quantity * unit_price, 0.5) OVER () as median_order_value
FROM `your-project-id.your_dataset.sales`
GROUP BY product_id;
```

### Geospatial Queries

```sql
-- Create table with geospatial data
CREATE TABLE `your-project-id.your_dataset.store_locations` (
  store_id INT64,
  store_name STRING,
  location GEOGRAPHY,
  city STRING,
  state STRING
);

-- Geospatial queries
SELECT
  store_name,
  city,
  state,
  ST_DISTANCE(
    location,
    ST_GEOGPOINT(-122.4194, 37.7749)  -- San Francisco
  ) / 1000 as distance_km
FROM `your-project-id.your_dataset.store_locations`
ORDER BY distance_km
LIMIT 5;
```

## Performance Optimization

### Partitioning Strategies

```sql
-- Time-based partitioning
CREATE TABLE `your-project-id.your_dataset.events` (
  event_id INT64,
  user_id INT64,
  event_type STRING,
  event_data JSON,
  timestamp TIMESTAMP
)
PARTITION BY DATE(timestamp)
OPTIONS (
  partition_expiration_days = 365
);

-- Range partitioning
CREATE TABLE `your-project-id.your_dataset.user_scores` (
  user_id INT64,
  score INT64,
  category STRING,
  created_at TIMESTAMP
)
PARTITION BY RANGE_BUCKET(user_id, GENERATE_ARRAY(0, 1000000, 100000))
CLUSTER BY category;
```

### Clustering

```sql
-- Clustering for query optimization
CREATE TABLE `your-project-id.your_dataset.user_activity` (
  user_id INT64,
  activity_type STRING,
  page_url STRING,
  session_id STRING,
  timestamp TIMESTAMP
)
PARTITION BY DATE(timestamp)
CLUSTER BY user_id, activity_type;
```

### Materialized Views

```sql
-- Create materialized view for performance
CREATE MATERIALIZED VIEW `your-project-id.your_dataset.daily_sales_summary`
OPTIONS (
  enable_refresh = true,
  refresh_interval_minutes = 60
)
AS
SELECT
  DATE(order_date) as sales_date,
  COUNT(DISTINCT customer_id) as unique_customers,
  COUNT(*) as total_orders,
  SUM(quantity * unit_price) as total_revenue,
  AVG(quantity * unit_price) as avg_order_value
FROM `your-project-id.your_dataset.sales`
GROUP BY DATE(order_date);
```

## Machine Learning Integration

### BigQuery ML

```sql
-- Create logistic regression model
CREATE OR REPLACE MODEL `your-project-id.your_dataset.customer_churn_model`
OPTIONS (
  model_type = 'logistic_reg',
  input_label_cols = ['churned'],
  data_split_method = 'AUTO_SPLIT'
) AS
SELECT
  customer_id,
  tenure_months,
  monthly_charges,
  total_charges,
  contract_type,
  payment_method,
  churned
FROM `your-project-id.your_dataset.customer_data`;

-- Make predictions
SELECT
  customer_id,
  predicted_churned,
  predicted_churned_probs[OFFSET(0)].prob as churn_probability
FROM ML.PREDICT(
  MODEL `your-project-id.your_dataset.customer_churn_model`,
  (
    SELECT
      customer_id,
      tenure_months,
      monthly_charges,
      total_charges,
      contract_type,
      payment_method
    FROM `your-project-id.your_dataset.customer_data`
    WHERE customer_id = 12345
  )
);
```

### AutoML Tables

```python
from google.cloud import automl_v1beta1 as automl

def create_automl_dataset():
    client = automl.AutoMlClient()
    location_path = client.location_path(project_id, "us-central1")

    dataset = automl.Dataset(
        display_name="customer_churn_dataset",
        tables_dataset_metadata=automl.TablesDatasetMetadata(
            target_column_spec_name="churned"
        )
    )

    response = client.create_dataset(parent=location_path, dataset=dataset)
    return response.name

def train_automl_model(dataset_name, model_name):
    client = automl.AutoMlClient()

    model = automl.Model(
        display_name=model_name,
        dataset_id=dataset_name.split("/")[-1],
        tables_model_metadata=automl.TablesModelMetadata(
            target_column_spec_name="churned",
            train_budget_milli_node_hours=1000,
            optimization_objective="MAXIMIZE_AU_ROC"
        )
    )

    response = client.create_model(parent=dataset_name.rsplit("/", 1)[0], model=model)
    return response.result()
```

## Security and Governance

### Row-Level Security

```sql
-- Create authorized view with RLS
CREATE ROW ACCESS POLICY us_customers_only
ON `your-project-id.your_dataset.customer_data`
GRANT TO ("user:analyst@company.com")
FILTER USING (country = 'US');
```

### Data Masking

```sql
-- Mask sensitive data
CREATE OR REPLACE TABLE `your-project-id.your_dataset.masked_customers`
AS
SELECT
  customer_id,
  CASE
    WHEN CURRENT_USER() IN ('admin@company.com', 'compliance@company.com')
    THEN ssn
    ELSE CONCAT('XXX-XX-', SUBSTR(ssn, -4))
  END as masked_ssn,
  first_name,
  last_name,
  email
FROM `your-project-id.your_dataset.customers`;
```

### Audit Logging

```sql
-- Query audit logs
SELECT
  timestamp,
  resource.labels.project_id,
  protopayload_auditlog.authenticationInfo.principalEmail,
  protopayload_auditlog.requestMetadata.callerIp,
  protopayload_auditlog.serviceName,
  protopayload_auditlog.methodName
FROM `your-project-id.audit_logs.cloudaudit_googleapis_com_data_access`
WHERE
  timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND resource.type = "bigquery_dataset"
ORDER BY timestamp DESC;
```

## Advanced Features

### BI Engine

```python
from google.cloud import bigquery_connection_v1

def create_bi_engine_connection():
    client = bigquery_connection_v1.ConnectionServiceClient()

    connection = bigquery_connection_v1.Connection(
        friendly_name="BI Engine Connection",
        description="High-performance connection for BI tools",
        bigquery_connection=bigquery_connection_v1.BigQueryConnection(
            use_bi_engine=True
        )
    )

    response = client.create_connection(
        parent=f"projects/{project_id}/locations/US",
        connection_id="bi_engine_conn",
        connection=connection
    )

    return response
```

### BigQuery Omni

```sql
-- Query data across clouds
SELECT
  customer_id,
  SUM(amount) as total_amount,
  COUNT(*) as transaction_count
FROM `aws-us-east-1.your-project-id.cross_cloud_data.transactions`
WHERE transaction_date >= '2024-01-01'
GROUP BY customer_id
ORDER BY total_amount DESC;
```

### Continuous Queries

```sql
-- Create continuous query for real-time aggregation
CREATE CONTINUOUS QUERY `your-project-id.your_dataset.realtime_metrics`
OPTIONS (
  refresh_interval_minutes = 5,
  allow_non_incremental_definition = false
)
AS
SELECT
  TIMESTAMP_TRUNC(timestamp, MINUTE) as minute,
  COUNT(*) as events_per_minute,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(value) as avg_value
FROM `your-project-id.your_dataset.events`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY TIMESTAMP_TRUNC(timestamp, MINUTE);
```

## Cost Optimization

### Query Optimization

```sql
-- Use approximate functions for large datasets
SELECT
  APPROX_COUNT_DISTINCT(customer_id) as approx_unique_customers,
  APPROX_TOP_COUNT(product_id, 10) as top_products,
  APPROX_TOP_SUM(product_id, quantity, 10) as top_products_by_quantity
FROM `your-project-id.your_dataset.sales`;

-- Use table decorators for time-based queries
SELECT *
FROM `your-project-id.your_dataset.events@-86400000--3600000`  -- Last 24-1 hours
WHERE event_type = 'purchase';
```

### Storage Optimization

```python
def optimize_storage():
    # Convert to columnar format
    query = """
    CREATE OR REPLACE TABLE `your-project-id.your_dataset.optimized_sales`
    PARTITION BY DATE(order_date)
    CLUSTER BY (customer_id, product_id)
    AS SELECT * FROM `your-project-id.your_dataset.sales`
    """

    job = client.query(query)
    job.result()

    # Set table expiration
    table = client.get_table("your-project-id.your_dataset.temp_data")
    table.expires = datetime.datetime.now() + datetime.timedelta(days=7)
    client.update_table(table, ["expires"])
```

### Reservation Management

```python
from google.cloud import bigquery_reservation_v1

def create_capacity_commitment():
    client = bigquery_reservation_v1.ReservationServiceClient()

    commitment = bigquery_reservation_v1.CapacityCommitment(
        slot_count=100,
        commitment_plan=bigquery_reservation_v1.CapacityCommitment.CommitmentPlan.FLEX
    )

    response = client.create_capacity_commitment(
        parent=f"projects/{project_id}/locations/US",
        capacity_commitment=commitment
    )

    return response
```

## Monitoring and Alerting

### Query Monitoring

```python
def monitor_query_performance():
    # Get recent jobs
    jobs = client.list_jobs(
        max_results=10,
        all_users=True,
        state_filter=["DONE"]
    )

    for job in jobs:
        print(f"Job ID: {job.job_id}")
        print(f"Query: {job.query}")
        print(f"Duration: {job.ended - job.started}")
        print(f"Bytes processed: {job.total_bytes_processed}")
        print(f"Bytes billed: {job.total_bytes_billed}")
        print("---")
```

### Cost Monitoring

```sql
-- Monitor query costs
SELECT
  job_id,
  user_email,
  query,
  total_bytes_billed / POWER(2, 40) as tb_billed,
  total_slot_ms / 1000 as slot_seconds,
  TIMESTAMP_DIFF(end_time, start_time, SECOND) as duration_seconds,
  (total_bytes_billed / POWER(2, 40)) * 5 as estimated_cost_usd
FROM `your-project-id.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND state = 'DONE'
ORDER BY total_bytes_billed DESC
LIMIT 20;
```

## Integration Patterns

### Data Pipeline Orchestration

```python
from google.cloud import dataflow

def create_dataflow_pipeline():
    pipeline_options = {
        'project': project_id,
        'region': 'us-central1',
        'staging_location': 'gs://your-bucket/staging',
        'temp_location': 'gs://your-bucket/temp',
        'template_location': 'gs://your-bucket/templates/bq_pipeline'
    }

    pipeline = dataflow.Pipeline(options=pipeline_options)

    # Read from BigQuery
    sales_data = (
        pipeline
        | 'Read from BigQuery' >> beam.io.ReadFromBigQuery(
            query='SELECT * FROM `your-project-id.your_dataset.sales`',
            use_standard_sql=True
        )
    )

    # Transform data
    transformed_data = (
        sales_data
        | 'Transform' >> beam.Map(transform_function)
    )

    # Write back to BigQuery
    transformed_data | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
        table='your-project-id.your_dataset.processed_sales',
        schema=schema,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
    )

    pipeline.run()
```

### Real-time Analytics

```python
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

def process_realtime_data():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, 'sales-events-sub')

    def callback(message):
        # Process message
        data = json.loads(message.data)

        # Insert into BigQuery
        rows_to_insert = [{
            'order_id': data['order_id'],
            'customer_id': data['customer_id'],
            'amount': data['amount'],
            'timestamp': data['timestamp']
        }]

        errors = client.insert_rows_json(
            'your-project-id.your_dataset.realtime_sales',
            rows_to_insert
        )

        if not errors:
            message.ack()
        else:
            print(f"Errors: {errors}")
            message.nack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print("Listening for messages...")

    try:
        streaming_pull_future.result(timeout=300)  # 5 minutes
    except TimeoutError:
        streaming_pull_future.cancel()
        streaming_pull_future.result()
```

## Best Practices

### Performance Optimization
1. Use partitioning and clustering appropriately
2. Leverage materialized views for frequently queried data
3. Use approximate functions for large datasets
4. Optimize query structure and join patterns
5. Monitor and tune query performance regularly

### Cost Management
1. Use table decorators for time-based queries
2. Implement data lifecycle policies
3. Choose appropriate storage classes
4. Monitor query costs and optimize expensive queries
5. Use reservations for predictable workloads

### Security
1. Implement least privilege access
2. Use row-level security for sensitive data
3. Enable audit logging
4. Regularly review access patterns
5. Encrypt sensitive data at rest and in transit

### Data Governance
1. Establish data quality checks
2. Document data lineage
3. Implement data retention policies
4. Create data catalogs
5. Establish data stewardship processes

BigQuery represents the evolution of data warehousing - a fully managed, scalable, and intelligent platform that democratizes access to powerful analytics capabilities while maintaining enterprise-grade security and governance.
