# Scala for Data Engineering Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Setup**
```bash
# Install Scala
# Download from scala-lang.org or use sbt

# Create project
sbt new scala/hello-world.g8
```

### 2. **Spark (Scala)**
```scala
import org.apache.spark.sql.SparkSession

val spark = SparkSession.builder()
  .appName("ScalaApp")
  .getOrCreate()

val df = spark.read.csv("data.csv")
df.show()
```

### 3. **Kafka (Scala)**
```scala
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerRecord}

val props = new Properties()
props.put("bootstrap.servers", "localhost:9092")
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer")
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer")

val producer = new KafkaProducer[String, String](props)
val record = new ProducerRecord[String, String]("topic", "key", "value")
producer.send(record)
```

## Level 2 – Production Patterns

### Functional Programming
```scala
val result = data
  .filter(_.age > 25)
  .groupBy(_.department)
  .mapValues(_.map(_.salary).sum)
```

### Error Handling
```scala
import scala.util.{Try, Success, Failure}

val result = Try {
  // Data processing
} match {
  case Success(value) => value
  case Failure(exception) => 
    logger.error("Error", exception)
    // Handle error
}
```

## Level 3 – Architect Playbook

### Akka Streams
```scala
import akka.stream.scaladsl.{Source, Sink}

Source(1 to 10)
  .map(_ * 2)
  .runWith(Sink.foreach(println))
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Compile | `sbt compile` | Compile project |
| Run | `sbt run` | Run application |
| Test | `sbt test` | Run tests |

## Checklist Before Production

- [ ] Set up sbt project structure
- [ ] Implement proper error handling
- [ ] Set up logging
- [ ] Optimize Spark jobs
- [ ] Set up monitoring
- [ ] Implement proper testing
- [ ] Set up CI/CD
- [ ] Document code
