# Data Pipelines Interview Questions and Answers

## Beginner Level Questions

### Q1: What is a data pipeline and what are its components?

**Answer:**
A data pipeline is a series of data processing steps that move and transform data from source systems to destination systems. It automates the flow of data through extraction, transformation, and loading (ETL) or extraction, loading, and transformation (ELT) processes.

**Components:**
- **Source**: Data origin (databases, APIs, files, streams)
- **Extraction**: Reading data from sources
- **Transformation**: Cleaning, enriching, and transforming data
- **Loading**: Writing data to destinations
- **Orchestration**: Scheduling and coordinating pipeline execution
- **Monitoring**: Tracking pipeline health and performance

**Types:**
- **Batch pipelines**: Process data in batches (scheduled)
- **Stream pipelines**: Process data in real-time (continuous)
- **ETL pipelines**: Extract, Transform, Load
- **ELT pipelines**: Extract, Load, Transform

### Q2: Explain the difference between ETL and ELT.

**Answer:**

**ETL (Extract, Transform, Load):**
- Data transformed before loading into destination
- Transformation happens in intermediate system
- Requires processing power for transformation
- Best for structured data and predefined schemas

**ELT (Extract, Load, Transform):**
- Data loaded first, then transformed in destination
- Transformation happens in destination system
- Leverages destination system's processing power
- Best for cloud data warehouses and flexible schemas

**Comparison:**

| Aspect | ETL | ELT |
|--------|-----|-----|
| Transformation | Before loading | After loading |
| Processing | Intermediate system | Destination system |
| Schema | Predefined | Flexible |
| Use Case | Traditional data warehouses | Cloud data warehouses |

### Q3: What are the common data pipeline patterns?

**Answer:**

**1. Batch Processing:**
- Process data in scheduled batches
- High throughput, higher latency
- Examples: Daily ETL jobs, hourly data loads

**2. Stream Processing:**
- Process data in real-time
- Low latency, continuous processing
- Examples: Real-time analytics, event processing

**3. Lambda Architecture:**
- Combines batch and stream processing
- Batch layer for historical data
- Speed layer for real-time data
- Serving layer for queries

**4. Kappa Architecture:**
- Single stream processing pipeline
- All data as streams
- Simpler than Lambda
- Reprocessing for corrections

### Q4: How do you handle data quality in pipelines?

**Answer:**

**Data Quality Strategies:**

**Validation:**
- Schema validation
- Data type checks
- Range and constraint validation
- Referential integrity checks

**Cleaning:**
- Remove duplicates
- Handle missing values
- Standardize formats
- Correct errors

**Monitoring:**
- Track data quality metrics
- Set up alerts for anomalies
- Log data quality issues
- Report on data quality

**Example:**
```python
def validate_data(df):
    # Schema validation
    assert 'user_id' in df.columns
    assert df['user_id'].dtype == 'int64'
    
    # Data validation
    assert df['user_id'].notna().all()
    assert (df['age'] >= 0).all()
    assert (df['age'] <= 120).all()
    
    # Duplicate check
    assert df['user_id'].duplicated().sum() == 0
    
    return df
```

### Q5: Explain error handling and retry strategies in data pipelines.

**Answer:**

**Error Handling:**

**Retry Strategies:**
- **Exponential backoff**: Increase delay between retries
- **Maximum retries**: Limit number of retry attempts
- **Circuit breaker**: Stop retrying after failures
- **Dead letter queue**: Store failed messages for manual processing

**Error Types:**
- **Transient errors**: Network issues, timeouts (retry)
- **Permanent errors**: Invalid data, schema mismatches (fail)
- **Partial failures**: Some records fail (continue with others)

**Example:**
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def load_data(data):
    # Load data with retry logic
    pass
```

## Intermediate Level Questions

### Q6: How do you design a scalable data pipeline?

**Answer:**

**Scalability Design:**

**Horizontal Scaling:**
- Distribute processing across multiple workers
- Use distributed processing frameworks
- Partition data for parallel processing
- Auto-scale based on workload

**Vertical Scaling:**
- Increase resources for single worker
- Upgrade hardware capabilities
- Optimize resource usage
- Cache frequently accessed data

**Partitioning:**
- Partition data by key or time
- Enable parallel processing
- Distribute load evenly
- Optimize for query patterns

**Example:**
```python
from multiprocessing import Pool

def process_partition(partition):
    # Process data partition
    return transform(partition)

def scalable_pipeline(data):
    # Partition data
    partitions = partition_data(data, num_partitions=10)
    
    # Process in parallel
    with Pool(processes=10) as pool:
        results = pool.map(process_partition, partitions)
    
    # Combine results
    return combine_results(results)
```

### Q7: Explain data pipeline orchestration and scheduling.

**Answer:**

**Orchestration:**
- Coordination of pipeline tasks
- Dependency management
- Error handling and recovery
- Monitoring and alerting

**Scheduling:**
- Time-based scheduling (cron)
- Event-based scheduling (triggers)
- Dependency-based scheduling
- Dynamic scheduling

**Tools:**
- **Airflow**: Workflow orchestration platform
- **Luigi**: Python-based workflow management
- **Prefect**: Modern workflow orchestration
- **Temporal**: Distributed workflow engine

**Example (Airflow):**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extract_data():
    # Extract data
    pass

def transform_data():
    # Transform data
    pass

def load_data():
    # Load data
    pass

dag = DAG('data_pipeline', start_date=datetime(2024, 1, 1))

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load_data,
    dag=dag
)

extract_task >> transform_task >> load_task
```

### Q8: What is data lineage and why is it important?

**Answer:**

**Data Lineage:**
Tracking the origin, transformation, and destination of data through the pipeline.

**Importance:**
- **Traceability**: Track data from source to destination
- **Debugging**: Identify issues in data transformations
- **Compliance**: Meet regulatory requirements
- **Impact Analysis**: Understand effects of changes
- **Documentation**: Document data flow and transformations

**Implementation:**
- Metadata tracking
- Transformation logging
- Dependency mapping
- Version control
- Lineage visualization

## Advanced Level Questions

### Q9: How do you handle schema evolution in data pipelines?

**Answer:**

**Schema Evolution:**
Managing changes to data schemas over time while maintaining backward compatibility.

**Strategies:**

**1. Backward Compatibility:**
- Add new fields as optional
- Don't remove existing fields
- Use default values for new fields
- Version schemas

**2. Schema Registry:**
- Centralized schema management
- Version control for schemas
- Schema validation
- Compatibility checking

**3. Evolution Patterns:**
- **Additive**: Add new fields (backward compatible)
- **Removal**: Remove fields (breaking change)
- **Modification**: Change field types (breaking change)

**Example:**
```python
from avro import schema

# Original schema
original_schema = {
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"}
    ]
}

# Evolved schema (additive)
evolved_schema = {
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        {"name": "email", "type": ["null", "string"], "default": null}
    ]
}
```

### Q10: Explain data pipeline testing strategies.

**Answer:**

**Testing Strategies:**

**Unit Testing:**
- Test individual transformation functions
- Mock data sources and destinations
- Test edge cases and error handling
- Validate transformation logic

**Integration Testing:**
- Test pipeline components together
- Use test data sources
- Validate end-to-end flow
- Test error scenarios

**Data Quality Testing:**
- Validate data quality metrics
- Check data completeness
- Verify data accuracy
- Test data consistency

**Example:**
```python
import pytest
import pandas as pd

def test_transform_data():
    # Test data
    input_data = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [30, 25]
    })
    
    # Transform
    output_data = transform_data(input_data)
    
    # Assertions
    assert 'full_name' in output_data.columns
    assert output_data['age'].dtype == 'int64'
    assert len(output_data) == 2
```

### Q11: How do you monitor and alert on data pipeline health?

**Answer:**

**Monitoring Metrics:**

**Pipeline Metrics:**
- Execution time
- Success/failure rates
- Data volume processed
- Error rates and types

**Data Quality Metrics:**
- Data completeness
- Data accuracy
- Data freshness
- Data consistency

**Infrastructure Metrics:**
- Resource usage (CPU, memory, disk)
- Network throughput
- Queue depths
- Worker availability

**Alerting:**
- Set thresholds for metrics
- Alert on failures and anomalies
- Notify stakeholders
- Escalate critical issues

**Example:**
```python
def monitor_pipeline(pipeline_run):
    metrics = {
        'execution_time': pipeline_run.duration,
        'records_processed': pipeline_run.records_processed,
        'errors': pipeline_run.errors,
        'data_quality_score': pipeline_run.quality_score
    }
    
    # Check thresholds
    if metrics['execution_time'] > 3600:  # 1 hour
        alert('Pipeline execution time exceeded threshold')
    
    if metrics['errors'] > 10:
        alert('High error rate in pipeline')
    
    if metrics['data_quality_score'] < 0.9:
        alert('Data quality below threshold')
    
    return metrics
```

### Q12: Explain data pipeline optimization techniques.

**Answer:**

**Optimization Techniques:**

**1. Parallel Processing:**
- Distribute work across multiple workers
- Partition data for parallel processing
- Use distributed processing frameworks
- Optimize worker allocation

**2. Caching:**
- Cache frequently accessed data
- Cache transformation results
- Use in-memory caching
- Implement cache invalidation

**3. Incremental Processing:**
- Process only new/changed data
- Use change data capture (CDC)
- Track last processed timestamp
- Reduce processing time

**4. Data Compression:**
- Compress data in transit
- Compress data at rest
- Use efficient compression algorithms
- Balance compression and CPU usage

**Example:**
```python
def incremental_load(last_timestamp):
    # Load only new data
    query = f"""
    SELECT * FROM source_table
    WHERE updated_at > '{last_timestamp}'
    """
    return execute_query(query)

def optimize_pipeline():
    # Use incremental loading
    last_timestamp = get_last_timestamp()
    new_data = incremental_load(last_timestamp)
    
    # Process in parallel
    results = process_parallel(new_data)
    
    # Cache results
    cache_results(results)
    
    return results
```

---

## Key Takeaways

1. **Data pipelines** automate data flow from source to destination
2. **ETL vs ELT** differ in when transformation occurs
3. **Error handling** includes retry strategies and dead letter queues
4. **Scalability** requires horizontal scaling and partitioning
5. **Orchestration** coordinates pipeline tasks and dependencies
6. **Schema evolution** manages schema changes over time
7. **Testing** ensures pipeline reliability and data quality
8. **Monitoring** tracks pipeline health and performance

