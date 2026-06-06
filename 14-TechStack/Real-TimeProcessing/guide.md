# Real-Time Processing Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Kafka Streaming**
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group'
)

for message in consumer:
    process_message(message.value)
```

### 2. **Spark Streaming**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("StreamingApp").getOrCreate()

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "topic") \
    .load()

query = df.writeStream \
    .format("console") \
    .start()
```

## Level 2 – Production Patterns

### Stateful Processing
```python
from pyspark.sql.functions import window, sum

windowed = df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window("timestamp", "5 minutes"),
        "category"
    ) \
    .agg(sum("amount").alias("total"))
```

### Exactly-Once Semantics
```python
query = df.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("checkpointLocation", "/checkpoint") \
    .option("enable.idempotence", "true") \
    .start()
```

## Level 3 – Architect Playbook

### Complex Event Processing
```python
# Pattern matching
from flink import Pattern

pattern = Pattern.begin("start") \
    .where(lambda e: e.type == "A") \
    .next("middle") \
    .where(lambda e: e.type == "B") \
    .followed_by("end") \
    .where(lambda e: e.type == "C")
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Start stream | `query.start()` | Start streaming |
| Stop | `query.stop()` | Stop streaming |
| Checkpoint | Set checkpoint location | Enable recovery |

## Checklist Before Production

- [ ] Configure proper watermarking
- [ ] Set up checkpointing
- [ ] Implement exactly-once semantics
- [ ] Set up monitoring
- [ ] Configure fault tolerance
- [ ] Optimize performance
- [ ] Test recovery scenarios
- [ ] Set up alerting
