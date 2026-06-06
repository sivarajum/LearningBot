# Kafka - Complete Guide (Basic to Advanced)

## 🎯 What is Kafka?

**Apache Kafka** is a distributed event streaming platform. Critical for real-time data processing, with high demand in architect roles.

### Why Kafka?
- **Real-Time**: Stream processing
- **Scalable**: Handle millions of messages
- **Durable**: Persistent storage
- **Distributed**: Fault-tolerant
- **Industry Standard**: Most common streaming platform

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic Concepts

```python
from kafka import KafkaProducer, KafkaConsumer

# Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send message
producer.send('my-topic', {'key': 'value'})

# Consumer
consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Consume messages
for message in consumer:
    print(message.value)
```

### Key Concepts

#### 1. **Topics**
- Categories for messages
- Partitioned for scalability
- Replicated for durability

#### 2. **Producers**
- Send messages to topics
- Can specify partition
- Async or sync

#### 3. **Consumers**
- Read messages from topics
- Consumer groups for parallel processing
- Offset management

#### 4. **Brokers**
- Kafka servers
- Store messages
- Handle requests

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Producer Patterns

```python
# Async with callback
def on_send_success(record_metadata):
    print(f"Sent to {record_metadata.topic}")

def on_send_error(exception):
    print(f"Error: {exception}")

producer.send(
    'my-topic',
    value={'key': 'value'}
).add_callback(on_send_success).add_errback(on_send_error)

# Batch sending
producer = KafkaProducer(
    batch_size=16384,
    linger_ms=10
)
```

### Consumer Patterns

```python
# Consumer group
consumer = KafkaConsumer(
    'my-topic',
    group_id='my-group',
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

# Manual offset commit
consumer = KafkaConsumer(
    'my-topic',
    group_id='my-group',
    enable_auto_commit=False
)

for message in consumer:
    process(message)
    consumer.commit()
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### Exactly-Once Semantics

```python
# Idempotent producer
producer = KafkaProducer(
    enable_idempotence=True,
    acks='all',
    retries=3
)

# Transactional producer
producer = KafkaProducer(
    transactional_id='my-transaction',
    enable_idempotence=True
)

producer.begin_transaction()
try:
    producer.send('topic1', value='data1')
    producer.send('topic2', value='data2')
    producer.commit_transaction()
except:
    producer.abort_transaction()
```

### Schema Registry

```python
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

schema_registry = SchemaRegistryClient({'url': 'http://localhost:8081'})
avro_serializer = AvroSerializer(
    schema_registry_client=schema_registry,
    schema_str=schema
)

producer = KafkaProducer(
    value_serializer=avro_serializer
)
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Event Streaming
```
Producer → Kafka Topic → Consumer
```

### Pattern 2: Stream Processing
```
Kafka → Stream Processor (Kafka Streams/Spark) → Output
```

### Pattern 3: Event Sourcing
```
Events → Kafka → Event Store → Replay
```

---

## 📊 Best Practices

### 1. **Partitioning**
- Partition by key for ordering
- More partitions = more parallelism
- Balance partition count

### 2. **Replication**
- Replication factor 3 for production
- Ensures durability
- Handles broker failures

### 3. **Retention**
- Set retention policy
- Delete old messages
- Archive if needed

### 4. **Monitoring**
- Monitor lag
- Track throughput
- Alert on failures

---

## 🎯 Key Takeaways

1. **Kafka = Event Streaming**
2. **Topics = Message Categories**
3. **Partitions = Scalability**
4. **Consumer Groups = Parallel Processing**
5. **Replication = Durability**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build streaming pipelines
5. 🎯 Explain it confidently

