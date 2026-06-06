# AWS Core Services - Complete Guide (Basic to Advanced)

## 🎯 What are AWS Core Services?

**AWS Core Services** are essential cloud services for data and AI workloads. Critical for multi-cloud expertise, with 94% of architect roles requiring AWS knowledge.

### Why AWS?
- **Market Leader**: Most widely used cloud platform
- **Comprehensive**: Complete data and AI stack
- **Scalable**: Auto-scaling and serverless
- **Integrated**: Services work together seamlessly
- **Industry Standard**: Required for most roles

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Core Services Overview

```python
import boto3

# Initialize clients
s3 = boto3.client('s3')
glue = boto3.client('glue')
lambda_client = boto3.client('lambda')

# S3: Object storage
s3.upload_file('data.csv', 'my-bucket', 'data/data.csv')

# Glue: ETL service
# Lambda: Serverless functions
```

### Key Services

#### 1. **S3 (Simple Storage Service)**
- Object storage
- Scalable, durable
- Data lake foundation

#### 2. **Glue**
- Serverless ETL
- Data catalog
- Spark-based processing

#### 3. **EMR (Elastic MapReduce)**
- Managed Spark/Hadoop
- Big data processing
- Auto-scaling clusters

#### 4. **Redshift**
- Data warehouse
- Columnar storage
- SQL analytics

#### 5. **Lambda**
- Serverless functions
- Event-driven
- Pay per execution

#### 6. **Athena**
- Serverless SQL queries
- Query S3 data
- Pay per query

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### S3 Data Lake

```python
import boto3

s3 = boto3.client('s3')

# Upload data
s3.upload_file('data.csv', 'data-lake', 'raw/2024/01/data.csv')

# List objects
response = s3.list_objects_v2(
    Bucket='data-lake',
    Prefix='raw/2024/01/'
)

# Download
s3.download_file('data-lake', 'processed/data.parquet', 'local.parquet')

# Lifecycle policies (automated)
# Move to Glacier after 30 days
```

### Glue ETL Jobs

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read from S3
datasource = glueContext.create_dynamic_frame.from_catalog(
    database="my_database",
    table_name="raw_table"
)

# Transform
transformed = ApplyMapping.apply(
    frame=datasource,
    mappings=[("id", "long", "customer_id", "long")]
)

# Write to S3
glueContext.write_dynamic_frame.from_options(
    frame=transformed,
    connection_type="s3",
    connection_options={"path": "s3://output-bucket/processed/"},
    format="parquet"
)
```

### EMR Spark Jobs

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EMRJob") \
    .getOrCreate()

# Read from S3
df = spark.read.parquet("s3://data-lake/raw/")

# Process
result = df.filter(df.amount > 100) \
    .groupBy("region") \
    .agg({"amount": "sum"})

# Write to S3
result.write.parquet("s3://data-lake/processed/")
```

### Lambda Functions

```python
import json
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Process S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Read file
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8')
    
    # Process
    processed = process_data(data)
    
    # Write result
    s3.put_object(
        Bucket='output-bucket',
        Key=f'processed/{key}',
        Body=processed
    )
    
    return {'statusCode': 200}
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Redshift Data Warehouse

```python
import psycopg2
import pandas as pd

# Connect
conn = psycopg2.connect(
    host='redshift-cluster.region.redshift.amazonaws.com',
    port=5439,
    database='dev',
    user='admin',
    password='password'
)

# Query
df = pd.read_sql("""
    SELECT 
        region,
        SUM(amount) as total
    FROM sales
    WHERE date >= '2024-01-01'
    GROUP BY region
""", conn)

# Load data
df.to_sql('results', conn, if_exists='replace', index=False)
```

### Step Functions (Orchestration)

```python
import boto3

sfn = boto3.client('stepfunctions')

# Define state machine
state_machine = {
    "Comment": "ETL Pipeline",
    "StartAt": "ProcessData",
    "States": {
        "ProcessData": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...",
            "Next": "LoadData"
        },
        "LoadData": {
            "Type": "Task",
            "Resource": "arn:aws:glue:...",
            "End": True
        }
    }
}

# Create state machine
sfn.create_state_machine(
    name="ETLPipeline",
    definition=json.dumps(state_machine),
    roleArn="arn:aws:iam::..."
)
```

### Athena Queries

```python
import boto3

athena = boto3.client('athena')

# Execute query
response = athena.start_query_execution(
    QueryString="""
        SELECT region, SUM(amount) as total
        FROM sales
        WHERE date >= '2024-01-01'
        GROUP BY region
    """,
    QueryExecutionContext={'Database': 'my_database'},
    ResultConfiguration={'OutputLocation': 's3://query-results/'}
)

query_id = response['QueryExecutionId']

# Get results
results = athena.get_query_results(QueryExecutionId=query_id)
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Data Lake
```
S3 (Raw) → Glue (ETL) → S3 (Processed) → Athena (Query)
```

### Pattern 2: Data Warehouse
```
S3 → Glue → Redshift → BI Tools
```

### Pattern 3: Serverless ETL
```
S3 Event → Lambda → Glue → S3
```

---

## 📊 Best Practices

### 1. **S3 Organization**
```
s3://bucket/
  raw/          # Raw data
  processed/    # Processed data
  curated/      # Analytics-ready
  archive/      # Archived data
```

### 2. **Cost Optimization**
- Use S3 lifecycle policies
- Choose right storage class
- Compress data (Parquet)
- Use Athena for ad-hoc queries

### 3. **Security**
- IAM roles and policies
- Encryption at rest and in transit
- VPC for private resources
- CloudTrail for auditing

### 4. **Monitoring**
- CloudWatch for metrics
- CloudWatch Logs for logs
- S3 access logging
- Cost monitoring

---

## 🎯 Key Takeaways

1. **S3 = Data Lake Foundation**
2. **Glue = Serverless ETL**
3. **EMR = Managed Spark**
4. **Redshift = Data Warehouse**
5. **Lambda = Serverless Compute**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with AWS
5. 🎯 Explain it confidently

