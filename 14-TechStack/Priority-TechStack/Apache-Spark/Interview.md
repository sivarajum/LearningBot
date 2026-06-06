# Apache Spark - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your Spark interviews. Critical for Data + AI + Cloud Architect roles.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is Apache Spark and why use it?

**Answer:**
"Apache Spark is a unified analytics engine for large-scale data processing. It's 100x faster than Hadoop MapReduce and supports batch, streaming, ML, and graph processing in one framework.

I use Spark because:

1. **Speed**: In-memory processing, 100x faster than MapReduce
2. **Unified**: One framework for batch, streaming, ML, SQL
3. **Scalable**: Handles petabytes of data across clusters
4. **Cloud-Native**: Works on AWS EMR, Azure Databricks, GCP Dataproc
5. **Industry Standard**: 94% of data architect roles require it

In production, I use Spark for ETL pipelines, real-time streaming, and ML feature engineering, processing terabytes of data daily."

**Key Points:**
- Unified analytics engine
- 100x faster than MapReduce
- Supports multiple workloads
- Industry standard

---

### Q2: What's the difference between RDD, DataFrame, and Dataset?

**Answer:**
"**RDD (Resilient Distributed Dataset)**: Low-level API, unstructured data, manual optimization.

**DataFrame**: Structured data (rows/columns), SQL-like operations, Catalyst optimizer, most commonly used.

**Dataset**: Type-safe DataFrames (Scala/Java), compile-time type checking.

**Evolution:**
- RDD → DataFrame (Spark 1.3) → Dataset (Spark 1.6)

**When to Use:**
- **DataFrame**: Most common, Python-friendly, good performance
- **Dataset**: Type safety needed (Scala/Java)
- **RDD**: Legacy code, custom operations

In practice, I use DataFrames 95% of the time because they're easier to use and automatically optimized."

**Key Points:**
- RDD = Low-level
- DataFrame = Structured, most common
- Dataset = Type-safe
- DataFrame recommended

---

### Q3: Explain lazy evaluation in Spark.

**Answer:**
"Lazy evaluation means transformations are not executed immediately. Spark builds an execution plan and only executes when an action is called.

**Transformations (Lazy):**
- filter, select, groupBy, join
- Return new DataFrame
- Not executed until action

**Actions (Eager):**
- show, count, collect, write
- Trigger execution
- Return results

**Benefits:**
- **Optimization**: Catalyst optimizer can optimize entire plan
- **Efficiency**: Only execute what's needed
- **Fault Tolerance**: Can recompute from lineage

**Example:**
```python
# No execution yet
df = spark.read.csv("data.csv")
filtered = df.filter(df.age > 25)
grouped = filtered.groupBy("region")

# Now execution happens
grouped.count()  # Action triggers execution
```

This allows Spark to optimize the entire query plan before execution."

**Key Points:**
- Transformations = lazy
- Actions = eager
- Optimization benefit
- Fault tolerance

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How does Spark handle data partitioning?

**Answer:**
"Spark partitions data across the cluster for parallel processing.

**Partitioning:**
- Data split into partitions
- Each partition processed by one executor
- More partitions = more parallelism

**Default Partitioning:**
- Based on input format
- HDFS: One partition per block
- Files: Based on file size

**Repartitioning:**
```python
# Increase partitions
df = df.repartition(200)

# Decrease partitions
df = df.coalesce(10)
```

**Best Practices:**
- 2-3x number of cores
- Too few: Underutilized resources
- Too many: Overhead

**Partitioning for Performance:**
```python
# Partition by key for joins
df.write.partitionBy("date").parquet("output/")
```

In production, I repartition based on data size and cluster resources, typically 200-500 partitions for large datasets."

**Key Points:**
- Data split into partitions
- Parallel processing
- Optimal: 2-3x cores
- Partition for joins

---

### Q5: What is a shuffle operation and how do you minimize it?

**Answer:**
"Shuffle is data redistribution across partitions, expensive operation.

**When Shuffle Happens:**
- groupBy, join, repartition
- Data moved across network
- Expensive I/O operation

**Minimizing Shuffle:**

**1. Use Broadcast Join**
```python
# For small DataFrames
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
```

**2. Pre-partition Data**
```python
# Partition by join key
df.write.partitionBy("customer_id").parquet("output/")
```

**3. Use Coalesce Instead of Repartition**
```python
# Coalesce doesn't shuffle
df = df.coalesce(10)  # No shuffle
```

**4. Filter Early**
```python
# Filter before join
df1.filter(...).join(df2.filter(...))
```

**5. Use Bucketing**
```python
df.write.bucketBy(10, "customer_id").saveAsTable("bucketed")
```

In production, I always use broadcast joins for small lookup tables and pre-partition data by join keys to minimize shuffles."

**Key Points:**
- Shuffle = expensive
- Broadcast for small tables
- Pre-partition data
- Filter early

---

### Q6: How do you optimize Spark performance?

**Answer:**
"**1. Partitioning**
```python
# Optimal partition count
df = df.repartition(200)  # 2-3x cores
```

**2. Caching**
```python
# Cache if used multiple times
df.cache()
# Use it
result1 = df.filter(...)
result2 = df.groupBy(...)
df.unpersist()  # When done
```

**3. Broadcast Small DataFrames**
```python
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
```

**4. Use Column Expressions**
```python
# Good: Column expressions (optimized)
df = df.withColumn("total", col("price") * col("quantity"))

# Avoid: UDFs when possible (slower)
```

**5. Avoid Collect()**
```python
# Bad: Collects all data to driver
data = df.collect()

# Good: Write to storage
df.write.parquet("output/")
```

**6. Tune Spark Config**
```python
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

In production, I use adaptive execution, optimal partitioning, and broadcast joins, achieving 5-10x performance improvements."

**Key Points:**
- Optimal partitioning
- Strategic caching
- Broadcast joins
- Avoid collect()
- Tune configs

---

## 🔴 ADVANCED LEVEL Questions

### Q7: Explain Spark's execution model and DAG.

**Answer:**
"**Execution Model:**

**1. DAG (Directed Acyclic Graph)**
- Spark builds DAG of transformations
- Represents execution plan
- Optimized by Catalyst

**2. Stages**
- DAG split into stages
- Stages separated by shuffle boundaries
- Stages executed sequentially

**3. Tasks**
- Each stage has tasks
- One task per partition
- Tasks executed in parallel

**Example:**
```python
df.filter(...)  # Stage 1
  .groupBy(...)  # Shuffle → Stage 2
  .agg(...)      # Stage 2
```

**Execution Flow:**
1. Build DAG
2. Optimize with Catalyst
3. Split into stages
4. Create tasks
5. Schedule tasks on executors
6. Execute in parallel

**Benefits:**
- Fault tolerance (recompute from DAG)
- Optimization (Catalyst optimizer)
- Parallel execution

I monitor DAGs in Spark UI to identify bottlenecks and optimize stages."

**Key Points:**
- DAG = execution plan
- Stages = shuffle boundaries
- Tasks = parallel execution
- Catalyst optimization

---

### Q8: How do you handle Spark streaming with exactly-once semantics?

**Answer:**
"**Exactly-Once Semantics:**

**1. Checkpointing**
```python
stream_df.writeStream \
    .option("checkpointLocation", "/checkpoint") \
    .start()
```

**2. Idempotent Writes**
- Write operations are idempotent
- Can retry safely
- Use unique keys

**3. Transactional Writes**
```python
# Use foreachBatch for transactional writes
def write_batch(batch_df, batch_id):
    batch_df.write \
        .mode("overwrite") \
        .saveAsTable("output_table")

stream_df.writeStream \
    .foreachBatch(write_batch) \
    .option("checkpointLocation", "/checkpoint") \
    .start()
```

**4. Offset Management**
- Kafka: Track offsets in checkpoint
- Exactly-once: Process each record once

**Best Practices:**
- Always use checkpointing
- Idempotent sink operations
- Monitor for duplicates
- Handle failures gracefully

In production, I use checkpointing with idempotent writes to ensure exactly-once processing, critical for financial transactions."

**Key Points:**
- Checkpointing required
- Idempotent writes
- Transactional operations
- Offset management

---

### Q9: How would you design a Spark-based data pipeline?

**Answer:**
"**Architecture:**

**1. Data Ingestion**
```python
# Batch: Read from various sources
df = spark.read.parquet("s3://bucket/data/")

# Streaming: Kafka/Kinesis
stream_df = spark.readStream.format("kafka")...
```

**2. Data Transformation**
```python
# Clean and transform
df = df.filter(...) \
    .withColumn(...) \
    .groupBy(...) \
    .agg(...)
```

**3. Data Quality**
```python
# Validate data
assert df.filter(col("amount").isNull()).count() == 0
```

**4. Data Storage**
```python
# Write to data lake
df.write \
    .partitionBy("date") \
    .mode("overwrite") \
    .parquet("s3://output/")
```

**5. Orchestration**
- Airflow for scheduling
- Retry logic
- Monitoring

**6. Optimization**
- Partitioning
- Caching
- Broadcast joins

**Components:**
- Spark for processing
- Airflow for orchestration
- S3/GCS for storage
- Monitoring for observability

This is the architecture I use in production, processing terabytes daily with 99.9% reliability."

**Key Points:**
- Multi-stage pipeline
- Data quality checks
- Optimized storage
- Orchestration
- Monitoring

---

### Q10: How do you handle Spark memory management?

**Answer:**
"**Memory Components:**

**1. Executor Memory**
```python
spark.conf.set("spark.executor.memory", "8g")
```

**2. Storage Memory**
- For cached DataFrames
- Configurable fraction

**3. Execution Memory**
- For shuffles, joins, aggregations
- Shared with storage

**4. Off-Heap Memory**
- For large datasets
- Slower but more capacity

**Tuning:**
```python
# Allocate more to execution
spark.conf.set("spark.memory.fraction", "0.8")
spark.conf.set("spark.memory.storageFraction", "0.3")
```

**Common Issues:**
- **OOM Errors**: Increase executor memory
- **Spill to Disk**: Increase memory or partitions
- **GC Pauses**: Tune garbage collection

**Best Practices:**
- Monitor memory usage
- Tune based on workload
- Use off-heap for large data
- Avoid caching too much

In production, I allocate 60% to execution, 20% to storage, and monitor for spills to optimize performance."

**Key Points:**
- Executor vs storage memory
- Tuning parameters
- Monitor for issues
- Optimize based on workload

---

## 🎯 System Design Questions

### Q11: Design a Spark-based data lake architecture.

**Answer:**
"**Architecture:**

**1. Ingestion Layer**
- Batch: Spark jobs from various sources
- Streaming: Spark Streaming from Kafka
- Storage: Raw data in data lake (S3/GCS)

**2. Processing Layer**
- Spark for ETL
- Partitioned by date
- Bronze → Silver → Gold layers

**3. Storage Layer**
- Parquet format
- Partitioned and bucketed
- Optimized for queries

**4. Serving Layer**
- Spark SQL for analytics
- Presto/Athena for ad-hoc queries
- APIs for applications

**5. Orchestration**
- Airflow for scheduling
- Retry and monitoring

**Components:**
- Spark for processing
- Data lake (S3/GCS)
- Airflow for orchestration
- Monitoring

This architecture handles petabytes of data with Spark as the processing engine."

---

## 💡 STAR Framework Examples

### Situation: Optimizing Spark Job Performance

**Situation**: Spark job taking 4 hours, needed to reduce to 30 minutes.

**Task**: Optimize Spark job for better performance.

**Action**: 
- Analyzed DAG in Spark UI
- Identified shuffle bottlenecks
- Implemented broadcast joins
- Optimized partitioning (200 partitions)
- Added caching for reused DataFrames
- Tuned Spark configs

**Result**: 
- Reduced execution time from 4 hours to 25 minutes
- 10x performance improvement
- Cost reduction by 80%

---

## 📊 Quick Reference

### Key Concepts
1. **RDD/DataFrame/Dataset**: Data abstractions
2. **Lazy Evaluation**: Optimize before execution
3. **Partitioning**: Parallel processing
4. **Shuffle**: Expensive operation
5. **Broadcast**: Optimize joins
6. **Caching**: Reuse data
7. **Streaming**: Real-time processing

### Common Interview Topics
- Lazy evaluation
- Partitioning strategies
- Shuffle minimization
- Performance optimization
- Streaming architecture
- Memory management

---

## ✅ Practice Checklist

- [ ] Can explain Spark in 2 minutes
- [ ] Understand RDD/DataFrame/Dataset
- [ ] Know lazy evaluation
- [ ] Understand partitioning
- [ ] Know optimization techniques
- [ ] Understand streaming
- [ ] Ready for system design questions

---

**Remember**: Spark is critical for Data + AI + Cloud Architect roles. Master it!

