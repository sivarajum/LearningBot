# Apache Spark Interview Questions & Answers

## Beginner Level Questions

### 1. What is Apache Spark and why is it called a "unified analytics engine"?
**Answer:** Apache Spark is an open-source, distributed computing system designed for big data processing. It's called a "unified analytics engine" because it provides a single platform for various data processing tasks including:

- **Batch processing**: Large-scale data transformation and analysis
- **Stream processing**: Real-time data processing
- **Machine learning**: ML algorithms and pipelines
- **Graph processing**: Graph computation and analysis
- **Interactive queries**: SQL-like queries on large datasets

**Key Benefits:**
- In-memory processing for faster performance
- Unified API across different workloads
- Support for multiple programming languages (Scala, Java, Python, R)
- Fault tolerance and scalability

### 2. Explain the core components of Apache Spark.
**Answer:** Apache Spark consists of several core components:

1. **Spark Core**: Foundation providing basic functionality like task scheduling, memory management, and fault recovery
2. **Spark SQL**: Module for structured data processing with DataFrame and Dataset APIs
3. **Spark Streaming**: Extension of core Spark API for scalable, high-throughput, fault-tolerant stream processing
4. **MLlib**: Spark's machine learning library containing algorithms and utilities
5. **GraphX**: API for graphs and graph-parallel computation

### 3. What is an RDD in Apache Spark?
**Answer:** RDD (Resilient Distributed Dataset) is the fundamental data structure in Spark. It represents an immutable, partitioned collection of elements that can be operated on in parallel.

**Key Characteristics:**
- **Resilient**: Automatically recovers from node failures
- **Distributed**: Data partitioned across cluster nodes
- **Dataset**: Collection of partitioned data with elements
- **Immutable**: Cannot be changed after creation

**Basic Operations:**
```scala
// Create RDD
val rdd = sc.parallelize(Seq(1, 2, 3, 4, 5))

// Transformations (lazy)
val doubled = rdd.map(_ * 2)

// Actions (eager)
val result = doubled.collect() // Returns: Array(2, 4, 6, 8, 10)
```

### 4. What is the difference between transformations and actions in Spark?
**Answer:**

| Aspect | Transformations | Actions |
|--------|----------------|---------|
| **Execution** | Lazy (not executed immediately) | Eager (executed immediately) |
| **Return Type** | RDD/DataFrame | Result value or side effect |
| **Examples** | `map()`, `filter()`, `join()` | `collect()`, `count()`, `saveAsTextFile()` |
| **Lineage** | Builds DAG for optimization | Triggers execution |

**Example:**
```scala
val rdd = sc.textFile("file.txt")
val filtered = rdd.filter(line => line.contains("error")) // Transformation
val count = filtered.count() // Action - triggers execution
```

### 5. How do you create a Spark application?
**Answer:** A basic Spark application requires:

1. **SparkSession** (Spark 2.x+) or **SparkContext** (Spark 1.x)
2. **Data source** (file, database, streaming source)
3. **Transformations** and **actions**
4. **Resource cleanup**

**Example:**
```scala
import org.apache.spark.sql.SparkSession

val spark = SparkSession.builder()
  .appName("My Spark App")
  .config("spark.master", "local[*]")
  .getOrCreate()

// Read data
val df = spark.read.json("data.json")

// Process data
val result = df.filter($"age" > 21).groupBy($"city").count()

// Show results
result.show()

spark.stop()
```

## Intermediate Level Questions

### 6. Explain DataFrames vs Datasets vs RDDs in Spark.
**Answer:**

| Feature | RDD | DataFrame | Dataset |
|---------|-----|-----------|---------|
| **Type Safety** | No | No | Yes (compile-time) |
| **Optimization** | Manual | Catalyst Optimizer | Catalyst Optimizer |
| **API Style** | Functional | SQL-like | Functional + SQL |
| **Performance** | Good | Better (optimized) | Best (optimized + type-safe) |
| **Language Support** | All | All | Scala/Java only |

**When to use:**
- **RDD**: Low-level control, custom partitioning, non-tabular data
- **DataFrame**: SQL-like operations, structured data, performance
- **Dataset**: Type safety + optimization, Scala/Java applications

### 7. How does Spark SQL's Catalyst optimizer work?
**Answer:** Catalyst is a query optimization framework that uses functional programming constructs to build an extensible optimizer.

**Optimization Pipeline:**
1. **Analysis**: Bind references to tables/columns using Catalog
2. **Logical Optimization**: Apply rule-based optimizations (constant folding, predicate pushdown)
3. **Physical Planning**: Generate multiple physical plans, select optimal one using cost-based optimization
4. **Code Generation**: Generate efficient JVM bytecode (Whole-Stage Code Generation)

**Example Optimizations:**
- **Predicate Pushdown**: Push filters to data source level
- **Column Pruning**: Select only required columns
- **Join Reordering**: Optimize join order for efficiency

### 8. What are the different cluster managers supported by Spark?
**Answer:** Spark supports multiple cluster managers:

1. **Standalone**: Spark's built-in cluster manager
   - Simple setup, good for development
   - Manual scaling of workers

2. **YARN (Yet Another Resource Negotiator)**:
   - Hadoop's resource manager
   - Good integration with Hadoop ecosystem
   - Supports long-running services

3. **Kubernetes**:
   - Container orchestration
   - Declarative configuration
   - Auto-scaling and self-healing

4. **Mesos**:
   - General-purpose cluster manager
   - Fine-grained resource sharing

### 9. How does Spark handle fault tolerance?
**Answer:** Spark achieves fault tolerance through:

1. **RDD Lineage**: Each RDD remembers how it was created from other RDDs
2. **DAG (Directed Acyclic Graph)**: Represents the computation graph
3. **Automatic Recovery**: Failed tasks are re-executed on other nodes
4. **Data Replication**: Important data can be cached/replicated

**Example:**
```scala
val rdd1 = sc.textFile("file.txt")  // Read from HDFS (reliable)
val rdd2 = rdd1.filter(line => line.contains("error"))  // Transformation
val rdd3 = rdd2.map(line => line.length)  // Transformation

// If rdd3 partition is lost, Spark can recompute it from rdd2, rdd1
val result = rdd3.collect()
```

### 10. Explain broadcast variables and accumulators in Spark.
**Answer:**

**Broadcast Variables:**
- Send large read-only data to all executors efficiently
- Data is sent once per executor, cached in memory
- Useful for joining large dataset with small lookup table

```scala
val broadcastVar = sc.broadcast(Map("key1" -> "value1", "key2" -> "value2"))
val result = rdd.map(x => broadcastVar.value.getOrElse(x._1, "default"))
```

**Accumulators:**
- Variables that can be "added" to across executors
- Only driver can read the accumulator value
- Useful for counters and sums across distributed operations

```scala
val counter = sc.longAccumulator("counter")
rdd.foreach(x => if (x > 10) counter.add(1))
println(s"Count: ${counter.value}")
```

## Advanced Level Questions

### 11. How does Spark Streaming work and what are its key concepts?
**Answer:** Spark Streaming processes live data streams by dividing them into small batches and processing each batch as an RDD.

**Key Concepts:**
- **DStreams**: Discretized streams, sequence of RDDs
- **Batches**: Data divided into time intervals (e.g., every 1 second)
- **Windowing**: Operations over sliding windows of data
- **Stateful Operations**: Operations that maintain state across batches

**Example:**
```scala
val ssc = new StreamingContext(spark.sparkContext, Seconds(1))
val lines = ssc.socketTextStream("localhost", 9999)
val words = lines.flatMap(_.split(" "))
val wordCounts = words.map(word => (word, 1)).reduceByKey(_ + _)

// Window operation: count words over last 30 seconds, every 10 seconds
val windowedCounts = wordCounts.window(Seconds(30), Seconds(10))
windowedCounts.print()

ssc.start()
ssc.awaitTermination()
```

### 12. Explain Structured Streaming in Spark 2.x+.
**Answer:** Structured Streaming provides a higher-level API based on DataFrames/Datasets for stream processing.

**Key Features:**
- **DataFrame/Dataset API**: Familiar API for both batch and streaming
- **Event-time processing**: Handle late-arriving data with watermarks
- **Exactly-once semantics**: End-to-end fault tolerance
- **Multiple output modes**: Append, Complete, Update

**Example:**
```scala
val spark = SparkSession.builder().getOrCreate()

val df = spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "localhost:9092")
  .option("subscribe", "topic1")
  .load()

val result = df
  .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
  .groupBy(window($"timestamp", "10 minutes"), $"key")
  .count()

val query = result.writeStream
  .outputMode("complete")
  .format("console")
  .start()

query.awaitTermination()
```

### 13. How do you optimize Spark job performance?
**Answer:** Performance optimization strategies:

1. **Data Partitioning:**
```scala
// Repartition for better parallelism
val repartitioned = df.repartition(100, $"key")

// Co-partition for efficient joins
val df1 = df1.repartition(100, $"joinKey")
val df2 = df2.repartition(100, $"joinKey")
val joined = df1.join(df2, "joinKey")
```

2. **Caching:**
```scala
// Cache frequently used DataFrames
val cachedDF = df.filter($"status" === "active").cache()

// Use appropriate storage levels
df.persist(StorageLevel.MEMORY_AND_DISK_SER)
```

3. **Broadcast Joins:**
```scala
// Broadcast small DataFrame for efficient join
val smallDF = spark.read.parquet("small-table")
val largeDF = spark.read.parquet("large-table")
val broadcasted = broadcast(smallDF)
val result = largeDF.join(broadcasted, "key")
```

4. **Resource Configuration:**
```scala
val spark = SparkSession.builder()
  .config("spark.executor.memory", "8g")
  .config("spark.executor.cores", "4")
  .config("spark.sql.shuffle.partitions", "200")
  .getOrCreate()
```

### 14. Explain the shuffle process in Spark and how to minimize it.
**Answer:** Shuffle is the process of redistributing data across partitions, required for operations like `groupByKey`, `reduceByKey`, and joins.

**Shuffle Process:**
1. **Map phase**: Tasks write intermediate data to local disk
2. **Shuffle phase**: Data transferred across network to appropriate reducers
3. **Reduce phase**: Reducers process the grouped data

**Minimizing Shuffle:**
- Use `reduceByKey` instead of `groupByKey` (uses combiners)
- Use broadcast joins for small tables
- Repartition data appropriately before operations
- Use `coalesce` instead of `repartition` when reducing partitions

**Example:**
```scala
// Bad: Creates shuffle
val grouped = rdd.groupByKey()
val result = grouped.mapValues(_.sum)

// Good: Uses combiner, less shuffle
val result = rdd.reduceByKey(_ + _)
```

### 15. How does Adaptive Query Execution (AQE) work in Spark 3.x?
**Answer:** AQE dynamically adjusts query execution plans based on runtime statistics.

**Key Features:**
- **Dynamic Coalescing**: Combines small partitions at runtime
- **Join Strategy Selection**: Switches between broadcast hash join and sort-merge join
- **Skew Join Optimization**: Splits skewed partitions to balance workload

**Configuration:**
```scala
val spark = SparkSession.builder()
  .config("spark.sql.adaptive.enabled", "true")
  .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
  .config("spark.sql.adaptive.skewJoin.enabled", "true")
  .getOrCreate()
```

### 16. Explain the MLlib Pipeline API.
**Answer:** MLlib Pipeline provides a high-level API for building ML workflows.

**Components:**
- **Transformers**: Convert one DataFrame to another (e.g., StringIndexer, VectorAssembler)
- **Estimators**: Algorithms that can be fit to data (e.g., LogisticRegression)
- **Pipelines**: Chain transformers and estimators
- **Evaluators**: Measure model performance

**Example:**
```scala
import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.classification.LogisticRegression
import org.apache.spark.ml.feature.{VectorAssembler, StringIndexer}
import org.apache.spark.ml.evaluation.BinaryClassificationEvaluator

// Feature engineering
val indexer = new StringIndexer()
  .setInputCol("category")
  .setOutputCol("categoryIndex")

val assembler = new VectorAssembler()
  .setInputCols(Array("feature1", "feature2", "categoryIndex"))
  .setOutputCol("features")

// Model
val lr = new LogisticRegression()
  .setLabelCol("label")
  .setFeaturesCol("features")

// Pipeline
val pipeline = new Pipeline()
  .setStages(Array(indexer, assembler, lr))

// Train
val model = pipeline.fit(trainingData)

// Evaluate
val predictions = model.transform(testData)
val evaluator = new BinaryClassificationEvaluator()
val auc = evaluator.evaluate(predictions)
```

### 17. How do you handle data skew in Spark?
**Answer:** Data skew occurs when some partitions have much more data than others, causing performance issues.

**Solutions:**

1. **Salting Technique:**
```scala
// Add salt to skewed keys
val saltedDF = df.withColumn("salt",
  when($"key" === "skewed-key", floor(rand() * 10))
  .otherwise(lit(0))
)

// Join with salted keys
val joined = saltedDF.join(otherDF,
  saltedDF("key") === otherDF("key") &&
  saltedDF("salt") === otherDF("salt")
)
```

2. **Broadcast Join:**
```scala
// For joining large table with small skewed table
val smallDF = spark.read.parquet("small-table")
val broadcasted = broadcast(smallDF)
val result = largeDF.join(broadcasted, "key")
```

3. **Repartitioning:**
```scala
// Repartition to balance data
val repartitioned = df.repartition(200, $"balancedColumn")
```

### 18. Explain checkpointing in Spark Streaming.
**Answer:** Checkpointing saves the state of streaming application to reliable storage for fault recovery.

**Types:**
- **Metadata Checkpointing**: Saves streaming computation information
- **Data Checkpointing**: Saves RDDs to reliable storage

**Example:**
```scala
val ssc = new StreamingContext(spark.sparkContext, Seconds(1))
ssc.checkpoint("hdfs://checkpoint/dir")  // Enable checkpointing

// Stateful operation with checkpointing
val updateFunc = (values: Seq[Int], state: Option[Int]) => {
  val currentCount = values.sum
  val previousCount = state.getOrElse(0)
  Some(currentCount + previousCount)
}

val statefulStream = wordCounts.updateStateByKey(updateFunc)
statefulStream.checkpoint(Seconds(30))  // Checkpoint every 30 seconds
```

### 19. How do you implement custom partitioning in Spark?
**Answer:** Create a custom partitioner by extending the `Partitioner` class.

```scala
class CustomPartitioner(numParts: Int) extends Partitioner {
  override def numPartitions: Int = numParts

  override def getPartition(key: Any): Int = {
    val k = key.asInstanceOf[String]
    // Custom partitioning logic
    if (k.startsWith("A")) 0
    else if (k.startsWith("B")) 1
    else (k.hashCode % numParts).abs
  }

  override def equals(other: Any): Boolean = {
    other match {
      case cp: CustomPartitioner => cp.numPartitions == numPartitions
      case _ => false
    }
  }
}

// Usage
val partitionedRDD = rdd.partitionBy(new CustomPartitioner(10))
```

### 20. Explain the memory management in Spark executors.
**Answer:** Spark executors manage memory using a unified memory model (Spark 1.6+).

**Memory Regions:**
- **Execution Memory** (60-70%): Used for computations (joins, sorts, aggregations)
- **Storage Memory** (20-30%): Used for cached RDDs/DataFrames
- **Reserved Memory** (300MB): JVM overhead and internal structures

**Dynamic Allocation:**
```scala
val spark = SparkSession.builder()
  .config("spark.memory.fraction", "0.8")  // 80% of heap for unified memory
  .config("spark.memory.storageFraction", "0.5")  // 50% of unified for storage
  .getOrCreate()
```

**Storage Levels:**
- `MEMORY_ONLY`: Fastest, no serialization
- `MEMORY_ONLY_SER`: Serialized, less memory usage
- `MEMORY_AND_DISK`: Spill to disk when memory full
- `DISK_ONLY`: Store only on disk

## Scenario-Based Questions

### 21. How would you design a real-time analytics pipeline using Spark?
**Answer:** Design a comprehensive real-time analytics pipeline:

```scala
val spark = SparkSession.builder()
  .appName("RealTimeAnalytics")
  .getOrCreate()

// 1. Read from Kafka
val kafkaDF = spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "kafka:9092")
  .option("subscribe", "user-events")
  .load()

// 2. Parse JSON data
val parsedDF = kafkaDF
  .selectExpr("CAST(value AS STRING) as json")
  .select(from_json($"json", schema).as("data"))
  .select("data.*")

// 3. Real-time aggregations
val windowedAgg = parsedDF
  .withWatermark("timestamp", "10 minutes")
  .groupBy(
    window($"timestamp", "5 minutes"),
    $"userId"
  )
  .agg(
    count("*").as("eventCount"),
    sum($"revenue").as("totalRevenue")
  )

// 4. Detect anomalies
val anomalies = windowedAgg
  .withColumn("avgRevenue", avg($"totalRevenue").over(Window.partitionBy($"userId")))
  .filter($"totalRevenue" > $"avgRevenue" * 2)

// 5. Write to multiple sinks
val query1 = windowedAgg.writeStream
  .format("delta")
  .option("checkpointLocation", "/tmp/checkpoint1")
  .outputMode("append")
  .start("/data/aggregates")

val query2 = anomalies.writeStream
  .format("console")
  .outputMode("append")
  .start()

spark.streams.awaitAnyTermination()
```

### 22. How do you handle late-arriving data in Structured Streaming?
**Answer:** Use watermarks and windowing to handle late data:

```scala
val spark = SparkSession.builder().getOrCreate()

val df = spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "localhost:9092")
  .option("subscribe", "events")
  .load()

// Parse data with timestamp
val events = df
  .selectExpr("CAST(value AS STRING) as json")
  .select(from_json($"json", schema).as("data"))
  .select($"data.*", $"data.timestamp".cast("timestamp"))

// Watermark for late data handling
val windowedCounts = events
  .withWatermark("timestamp", "10 minutes")  // Allow 10 min late data
  .groupBy(
    window($"timestamp", "5 minutes", "1 minute"),  // 5-min windows, 1-min slide
    $"eventType"
  )
  .count()

// Handle late data based on watermark
val query = windowedCounts.writeStream
  .outputMode("append")  // Only append new data, not update old windows
  .format("console")
  .option("truncate", "false")
  .start()

query.awaitTermination()
```

### 23. How would you implement a machine learning pipeline for fraud detection?
**Answer:** Implement an end-to-end ML pipeline:

```scala
import org.apache.spark.ml.{Pipeline, PipelineModel}
import org.apache.spark.ml.classification.{RandomForestClassifier, RandomForestClassificationModel}
import org.apache.spark.ml.evaluation.BinaryClassificationEvaluator
import org.apache.spark.ml.feature._
import org.apache.spark.ml.tuning.{CrossValidator, ParamGridBuilder}

// 1. Load and prepare data
val data = spark.read.parquet("transactions.parquet")
  .withColumn("label", when($"isFraud" === true, 1.0).otherwise(0.0))

// 2. Feature engineering pipeline
val categoricalCols = Array("merchant", "category", "country")
val numericCols = Array("amount", "hour", "dayOfWeek")

// String indexing for categorical features
val indexers = categoricalCols.map(col =>
  new StringIndexer()
    .setInputCol(col)
    .setOutputCol(s"${col}Index")
    .setHandleInvalid("keep")
)

// One-hot encoding
val encoder = new OneHotEncoder()
  .setInputCols(categoricalCols.map(col => s"${col}Index"))
  .setOutputCols(categoricalCols.map(col => s"${col}Vec"))

// Vector assembler
val assembler = new VectorAssembler()
  .setInputCols(numericCols ++ categoricalCols.map(col => s"${col}Vec"))
  .setOutputCol("features")

// 3. Model training pipeline
val rf = new RandomForestClassifier()
  .setLabelCol("label")
  .setFeaturesCol("features")
  .setNumTrees(100)

// Complete pipeline
val pipeline = new Pipeline()
  .setStages((indexers :+ encoder :+ assembler :+ rf).toArray)

// 4. Hyperparameter tuning
val paramGrid = new ParamGridBuilder()
  .addGrid(rf.numTrees, Array(50, 100, 200))
  .addGrid(rf.maxDepth, Array(5, 10, 15))
  .build()

val evaluator = new BinaryClassificationEvaluator()
  .setLabelCol("label")
  .setRawPredictionCol("rawPrediction")
  .setMetricName("areaUnderROC")

val cv = new CrossValidator()
  .setEstimator(pipeline)
  .setEvaluator(evaluator)
  .setEstimatorParamMaps(paramGrid)
  .setNumFolds(3)

// 5. Train model
val cvModel = cv.fit(data)

// 6. Save model for production
cvModel.bestModel.asInstanceOf[PipelineModel]
  .write.overwrite().save("fraud-detection-model")

// 7. Load and use model for inference
val model = PipelineModel.load("fraud-detection-model")
val predictions = model.transform(newTransactions)
predictions.select("transactionId", "prediction", "probability").show()
```

### 24. How do you implement exactly-once processing in Spark Streaming?
**Answer:** Ensure exactly-once processing through:

1. **Idempotent Operations**: Operations that can be repeated safely
2. **Transactional Sinks**: Sinks that support transactions
3. **Checkpointing**: Save processing state reliably
4. **Offset Management**: Track processed records

**Example with Kafka:**
```scala
// 1. Configure Kafka for exactly-once
val kafkaDF = spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "localhost:9092")
  .option("subscribe", "input-topic")
  .option("startingOffsets", "earliest")
  .option("failOnDataLoss", "false")
  .load()

// 2. Process data (idempotent operations)
val processedDF = kafkaDF
  .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
  .select(from_json($"value", schema).as("data"))
  .select("data.*")
  .withColumn("processed_at", current_timestamp())

// 3. Write to transactional sink (Delta Lake)
val query = processedDF.writeStream
  .format("delta")
  .outputMode("append")
  .option("checkpointLocation", "/tmp/delta-checkpoint")
  .option("mergeSchema", "true")
  .trigger(Trigger.ProcessingTime("30 seconds"))
  .start("/data/processed-events")

// 4. Monitor and handle failures
query.processAllAvailable()
if (query.exception.isDefined) {
  // Handle failure, possibly restart from checkpoint
  println(s"Query failed: ${query.exception.get}")
}
```

### 25. How do you optimize Spark performance for large-scale ETL pipelines?
**Answer:** Comprehensive ETL optimization strategy:

```scala
val spark = SparkSession.builder()
  .appName("OptimizedETL")
  // Memory configuration
  .config("spark.executor.memory", "16g")
  .config("spark.executor.cores", "8")
  .config("spark.sql.shuffle.partitions", "400")
  // Adaptive query execution
  .config("spark.sql.adaptive.enabled", "true")
  .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
  .config("spark.sql.adaptive.skewJoin.enabled", "true")
  // Caching strategy
  .config("spark.sql.inMemoryColumnarStorage.compressed", "true")
  .config("spark.sql.inMemoryColumnarStorage.batchSize", "10000")
  .getOrCreate()

// 1. Optimized data reading
val df = spark.read
  .option("mergeSchema", "true")
  .option("inferSchema", "false")  // Provide schema explicitly
  .parquet("s3://bucket/input-data/")

// 2. Schema optimization
val optimizedDF = df
  .select("required_columns_only")  // Column pruning
  .filter($"date" >= "2023-01-01")   // Predicate pushdown
  .repartition(200, $"partition_key")  // Optimal partitioning

// 3. Caching strategy
val intermediateDF = optimizedDF
  .groupBy($"category")
  .agg(sum($"amount").as("total"))
  .cache()  // Cache for multiple downstream operations

// 4. Join optimization
val lookupDF = spark.read.parquet("lookup-table")
val broadcastedLookup = broadcast(lookupDF)  // Broadcast small table

val joinedDF = intermediateDF
  .join(broadcastedLookup, "category")  // Broadcast hash join

// 5. Output optimization
joinedDF.write
  .mode("overwrite")
  .partitionBy("year", "month")  // Partition output
  .option("compression", "snappy")  // Optimal compression
  .parquet("s3://bucket/output-data/")

// 6. Resource cleanup
intermediateDF.unpersist()
spark.stop()
```

## Summary

Apache Spark interview questions span from basic RDD operations to advanced optimization techniques. Key areas to master include:

- **Core Concepts**: RDDs, DataFrames, transformations vs actions
- **Architecture**: Driver, executors, cluster managers
- **Optimization**: Catalyst optimizer, caching, partitioning
- **Streaming**: DStreams vs Structured Streaming, windowing
- **ML**: Pipeline API, feature engineering, model evaluation
- **Performance**: Memory management, shuffle optimization, data skew
- **Production**: Fault tolerance, monitoring, deployment

Understanding these concepts demonstrates expertise in distributed data processing and the ability to build scalable big data applications.
