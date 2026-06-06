# Apache Kafka Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Download Kafka
wget https://downloads.apache.org/kafka/2.13-3.5.0/kafka_2.13-3.5.0.tgz
tar -xzf kafka_2.13-3.5.0.tgz

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties
```

### 2. **Basic Operations**
```bash
# Create topic
bin/kafka-topics.sh --create --topic my-topic --bootstrap-server localhost:9092

# Produce
bin/kafka-console-producer.sh --topic my-topic --bootstrap-server localhost:9092

# Consume
bin/kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server localhost:9092
```

### 3. **Python Producer/Consumer**
```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
producer.send('my-topic', {'key': 'value'})

# Consumer
consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
for message in consumer:
    print(message.value)
```

## Level 2 – Production Patterns

### Advanced Producer
```python
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    acks='all',
    retries=3,
    enable_idempotence=True,
    compression_type='snappy'
)
```

### Kafka Streams
```python
from kafka import KafkaStreams

builder = StreamBuilder()
stream = builder.stream('input-topic')
transformed = stream.map_values(lambda v: v.upper())
transformed.to('output-topic')
```

## Level 3 – Architect Playbook

### Exactly-Once Semantics
```python
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    transactional_id='my-transactional-id',
    enable_idempotence=True
)

producer.begin_transaction()
producer.send('topic1', {'key': 'value1'})
producer.send('topic2', {'key': 'value2'})
producer.commit_transaction()
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| List topics | `kafka-topics.sh --list` | View topics |
| Describe | `kafka-topics.sh --describe` | Topic details |
| Consumer groups | `kafka-consumer-groups.sh --list` | List groups |

## Checklist Before Production

- [ ] Configure replication (min 3)
- [ ] Set min.insync.replicas
- [ ] Configure retention policies
- [ ] Set up monitoring
- [ ] Implement security (SASL, SSL)
- [ ] Configure log compaction
- [ ] Set up Schema Registry
- [ ] Implement exactly-once semantics
