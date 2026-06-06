# Java for Data Engineering Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Setup**
```bash
# Install JDK
# Download from oracle.com or use OpenJDK

# Verify
javac -version
java -version
```

### 2. **Basic Spark (Java)**
```java
import org.apache.spark.sql.SparkSession;

SparkSession spark = SparkSession.builder()
    .appName("JavaApp")
    .getOrCreate();

Dataset<Row> df = spark.read().csv("data.csv");
df.show();
```

### 3. **Kafka Producer (Java)**
```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
ProducerRecord<String, String> record = new ProducerRecord<>("topic", "key", "value");
producer.send(record);
```

## Level 2 – Production Patterns

### Spark Transformations
```java
Dataset<Row> result = df
    .filter(col("age").gt(25))
    .groupBy("department")
    .agg(avg("salary").alias("avg_salary"));
```

### Error Handling
```java
try {
    // Data processing
} catch (Exception e) {
    logger.error("Error processing data", e);
    // Handle error
}
```

## Level 3 – Architect Playbook

### Distributed Processing
```java
// Configure Spark for cluster
SparkConf conf = new SparkConf()
    .setMaster("spark://master:7077")
    .setAppName("DistributedApp");
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Compile | `javac Main.java` | Compile Java |
| Run | `java Main` | Run application |
| Build | `mvn package` | Build with Maven |

## Checklist Before Production

- [ ] Set up proper build system (Maven/Gradle)
- [ ] Implement proper error handling
- [ ] Set up logging
- [ ] Configure Spark for production
- [ ] Set up monitoring
- [ ] Optimize performance
- [ ] Set up CI/CD
- [ ] Test thoroughly
