# Apache Spark - Complete Guide (Basic to Advanced)

## 🎯 What is Apache Spark?

**Apache Spark** is a unified analytics engine for large-scale data processing. It's the most critical skill for Data + AI + Cloud Architect roles, with 94% of positions requiring it.

### Why Spark?
- **Speed**: 100x faster than Hadoop MapReduce
- **Unified**: Batch, streaming, ML, graph processing
- **Scalable**: Handles petabytes of data
- **Cloud-Native**: Works on AWS, Azure, GCP
- **Industry Standard**: Most common big data tool

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic Spark Concepts

```python
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("MyApp") \
    .getOrCreate()

# Read data
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# Transform
df_filtered = df.filter(df.age > 25)

# Show results
df_filtered.show()
```

### Key Concepts

#### 1. **SparkSession**
- Entry point to Spark
- Manages Spark context
- Creates DataFrames

#### 2. **DataFrames**
- Distributed collection of data
- Structured (columns, rows)
- Lazy evaluation

#### 3. **Transformations**
- Lazy operations (not executed immediately)
- Examples: filter, select, groupBy

#### 4. **Actions**
- Trigger execution
- Examples: show, count, collect

### Basic Example: Data Processing

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum

spark = SparkSession.builder.appName("SalesAnalysis").getOrCreate()

# Read data
sales_df = spark.read.csv("sales.csv", header=True, inferSchema=True)

# Transform
result = sales_df \
    .filter(col("amount") > 100) \
    .groupBy("region") \
    .agg(
        sum("amount").alias("total_sales"),
        avg("amount").alias("avg_sale")
    )

# Action (executes)
result.show()
```

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Advanced Transformations

```python
from pyspark.sql.functions import col, when, lit, window

# Conditional logic
df = df.withColumn(
    "category",
    when(col("amount") > 1000, "High")
    .when(col("amount") > 500, "Medium")
    .otherwise("Low")
)

# Window functions
from pyspark.sql.window import Window

window_spec = Window.partitionBy("customer_id").orderBy("date")
df = df.withColumn("running_total", sum("amount").over(window_spec))
```

### Joins

```python
# Inner join
result = df1.join(df2, on="customer_id", how="inner")

# Left join
result = df1.join(df2, on="customer_id", how="left")

# Complex join
result = df1.join(
    df2,
    (df1.customer_id == df2.customer_id) & (df1.date == df2.date),
    how="inner"
)
```

### Caching

```python
# Cache DataFrame for reuse
df.cache()
# or
df.persist(StorageLevel.MEMORY_AND_DISK)

# Unpersist when done
df.unpersist()
```

### Broadcast Variables

```python
# Small lookup table
lookup_dict = {"A": "Active", "I": "Inactive"}
broadcast_var = spark.sparkContext.broadcast(lookup_dict)

# Use in transformations
df = df.withColumn(
    "status",
    udf(lambda x: broadcast_var.value.get(x))(col("code"))
)
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Spark Streaming

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import window, count

spark = SparkSession.builder \
    .appName("StreamingApp") \
    .config("spark.sql.streaming.checkpointLocation", "/checkpoint") \
    .getOrCreate()

# Read stream
stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "topic") \
    .load()

# Process
result = stream_df \
    .selectExpr("CAST(value AS STRING)") \
    .groupBy(window("timestamp", "1 minute")) \
    .agg(count("*").alias("count"))

# Write stream
query = result.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
```

### Performance Optimization

```python
# Repartition for better parallelism
df = df.repartition(200)  # 200 partitions

# Coalesce to reduce partitions
df = df.coalesce(10)

# Bucketing
df.write \
    .bucketBy(10, "customer_id") \
    .sortBy("date") \
    .saveAsTable("bucketed_table")

# Partitioning
df.write \
    .partitionBy("date") \
    .parquet("output/")
```

### Spark SQL

```python
# Register DataFrame as table
df.createOrReplaceTempView("sales")

# Run SQL queries
result = spark.sql("""
    SELECT 
        region,
        SUM(amount) as total,
        AVG(amount) as avg_amount
    FROM sales
    WHERE date >= '2024-01-01'
    GROUP BY region
    ORDER BY total DESC
""")
```

### UDFs (User Defined Functions)

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# Define UDF
def categorize(amount):
    if amount > 1000:
        return "High"
    elif amount > 500:
        return "Medium"
    else:
        return "Low"

categorize_udf = udf(categorize, StringType())

# Use UDF
df = df.withColumn("category", categorize_udf(col("amount")))
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Batch Processing
```
Data Source → Spark → Transformations → Actions → Output
```

### Pattern 2: Streaming
```
Kafka → Spark Streaming → Processing → Output (Kafka/DB)
```

### Pattern 3: ML Pipeline
```
Data → Feature Engineering → Model Training → Predictions
```

---

## 🔗 Cloud Integration

### GCP Dataproc

```python
# Submit Spark job to Dataproc
gcloud dataproc jobs submit pyspark \
    --cluster=my-cluster \
    --region=us-central1 \
    spark_job.py
```

### AWS EMR

```python
# EMR automatically provides Spark
# Just use SparkSession as normal
spark = SparkSession.builder.appName("EMRJob").getOrCreate()
```

### Azure Databricks

```python
# Databricks provides optimized Spark
# Use SparkSession
spark = SparkSession.builder.getOrCreate()
```

---

## 📊 Best Practices

### 1. **Avoid Collect() on Large Data**
```python
# Bad: Collects all data to driver
data = df.collect()

# Good: Use show() or write to storage
df.show(100)
df.write.parquet("output/")
```

### 2. **Use Broadcast for Small Lookups**
```python
# Broadcast small DataFrames
small_df = spark.read.csv("lookup.csv")
broadcast_df = broadcast(small_df)
result = large_df.join(broadcast_df, "key")
```

### 3. **Optimize Partitions**
```python
# Repartition based on data size
# Rule: 2-3x number of cores
df = df.repartition(200)
```

### 4. **Cache Strategically**
```python
# Cache if used multiple times
df.cache()
# Use it
result1 = df.filter(...)
result2 = df.groupBy(...)
# Unpersist when done
df.unpersist()
```

### 5. **Use Column Expressions**
```python
# Good: Column expressions
df = df.withColumn("total", col("price") * col("quantity"))

# Avoid: UDFs when possible (slower)
```

---

## 🎯 Key Takeaways

1. **Spark = Unified Analytics Engine**
2. **DataFrames = Structured Data**
3. **Lazy Evaluation = Optimized Execution**
4. **Transformations = Lazy, Actions = Eager**
5. **Partitioning = Performance**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with your projects
5. 🎯 Explain it confidently

