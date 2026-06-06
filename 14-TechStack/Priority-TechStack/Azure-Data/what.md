# Azure Data Services - Complete Guide (Basic to Advanced)

## 🎯 What are Azure Data Services?

**Azure Data Services** provide comprehensive data and AI capabilities on Microsoft Azure. Critical for multi-cloud expertise, with 94% of architect roles requiring Azure knowledge.

### Why Azure?
- **Enterprise Integration**: Seamless with Microsoft ecosystem
- **Comprehensive**: Complete data and AI stack
- **Scalable**: Auto-scaling and serverless
- **Integrated**: Services work together
- **Industry Standard**: Required for enterprise roles

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Core Services Overview

```python
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

# Azure Data Lake Storage
blob_service = BlobServiceClient(
    account_url="https://mystorage.blob.core.windows.net",
    credential=DefaultAzureCredential()
)

# Upload data
blob_client = blob_service.get_blob_client(
    container="data-lake",
    blob="raw/data.csv"
)
with open("data.csv", "rb") as data:
    blob_client.upload_blob(data)
```

### Key Services

#### 1. **Azure Data Lake Storage (ADLS)**
- Scalable data lake
- HDFS-compatible
- Integrated with Azure services

#### 2. **Azure Data Factory (ADF)**
- ETL orchestration
- Visual pipelines
- 90+ connectors

#### 3. **Azure Synapse Analytics**
- Data warehouse + Big Data
- SQL + Spark
- Integrated analytics

#### 4. **Azure Functions**
- Serverless compute
- Event-driven
- Pay per execution

#### 5. **Azure Event Hubs**
- Real-time streaming
- High throughput
- Kafka-compatible

#### 6. **Azure Key Vault**
- Secrets management
- Encryption keys
- Security

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Azure Data Factory Pipelines

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient

# Create pipeline
pipeline = {
    "name": "ETLPipeline",
    "properties": {
        "activities": [
            {
                "name": "CopyData",
                "type": "Copy",
                "inputs": [{"referenceName": "SourceDataset"}],
                "outputs": [{"referenceName": "SinkDataset"}],
                "typeProperties": {
                    "source": {"type": "BlobSource"},
                    "sink": {"type": "BlobSink"}
                }
            }
        ]
    }
}
```

### Azure Synapse Analytics

```python
from azure.synapse.spark import SparkClient
from azure.identity import DefaultAzureCredential

# Spark in Synapse
spark_client = SparkClient(
    credential=DefaultAzureCredential(),
    endpoint="https://mysynapse.dev.azuresynapse.net"
)

# Run Spark job
spark_client.spark_batch.create_spark_batch_job(
    workspace_name="mysynapse",
    spark_pool_name="sparkpool",
    livy_api_version="2019-11-01-preview",
    spark_batch_job_options={
        "name": "ETLJob",
        "file": "abfss://container@storage.dfs.core.windows.net/job.py"
    }
)
```

### Azure Functions

```python
import azure.functions as func
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Process HTTP request
    name = req.params.get('name')
    
    # Process data
    result = process_data(name)
    
    return func.HttpResponse(
        f"Processed: {result}",
        status_code=200
    )
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Data Lake Architecture

```python
# Data Lake Gen2 structure
# abfss://container@storage.dfs.core.windows.net/
#   raw/          # Raw data
#   processed/    # Processed data
#   curated/      # Analytics-ready
```

### Synapse SQL Pools

```sql
-- Dedicated SQL Pool
CREATE TABLE sales (
    id INT,
    amount DECIMAL(10,2),
    date DATE
)
WITH (
    DISTRIBUTION = HASH(id),
    CLUSTERED COLUMNSTORE INDEX
);

-- Serverless SQL Pool
SELECT *
FROM OPENROWSET(
    BULK 'https://storage.dfs.core.windows.net/container/data.parquet',
    FORMAT = 'PARQUET'
) AS [result]
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Data Lake
```
ADLS (Raw) → ADF (ETL) → ADLS (Processed) → Synapse (Analytics)
```

### Pattern 2: Data Warehouse
```
ADLS → ADF → Synapse SQL Pool → Power BI
```

### Pattern 3: Real-Time
```
Event Hubs → Stream Analytics → ADLS/Synapse
```

---

## 📊 Best Practices

### 1. **Data Lake Organization**
```
abfss://container@storage.dfs.core.windows.net/
  raw/
  processed/
  curated/
```

### 2. **Cost Optimization**
- Use appropriate storage tiers
- Compress data (Parquet)
- Partition data
- Use serverless SQL when possible

### 3. **Security**
- Managed Identity
- Key Vault for secrets
- Network isolation
- Encryption

---

## 🎯 Key Takeaways

1. **ADLS = Data Lake**
2. **ADF = ETL Orchestration**
3. **Synapse = Data Warehouse + Big Data**
4. **Functions = Serverless**
5. **Event Hubs = Streaming**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with Azure
5. 🎯 Explain it confidently

