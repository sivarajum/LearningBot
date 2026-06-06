# Kafka - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your Kafka interviews. Critical for real-time streaming.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is Kafka and why use it?

**Answer:**
"Apache Kafka is a distributed event streaming platform for building real-time data pipelines and streaming applications.

I use Kafka because:

1. **Real-Time**: Stream processing with low latency
2. **Scalable**: Handle millions of messages per second
3. **Durable**: Persistent storage, fault-tolerant
4. **Distributed**: Runs on clusters
5. **Industry Standard**: Most common streaming platform

I use Kafka for real-time event streaming, connecting microservices, and building stream processing pipelines."

**Key Points:**
- Event streaming platform
- Real-time processing
- Scalable and durable
- Distributed

---

### Q2: What are topics and partitions?

**Answer:**
"**Topics:**
- Categories for messages
- Named streams of data
- Can have multiple partitions

**Partitions:**
- Topics split into partitions
- Enable parallelism
- Messages ordered within partition
- Replicated for durability

**Benefits:**
- **Scalability**: More partitions = more parallelism
- **Ordering**: Messages ordered within partition
- **Replication**: Fault tolerance

**Example:**
```
Topic: user-events
  Partition 0: [msg1, msg2, msg3]
  Partition 1: [msg4, msg5, msg6]
  Partition 2: [msg7, msg8, msg9]
```

I partition topics by key to ensure related messages stay together and enable parallel processing."

**Key Points:**
- Topics = categories
- Partitions = scalability
- Ordering within partition
- Replication for durability

---

### Q3: What are consumer groups?

**Answer:**
"Consumer groups enable parallel message consumption:

**Properties:**
- Multiple consumers in group
- Each partition consumed by one consumer
- Load balancing across consumers
- Offset tracking per group

**Example:**
```
Topic with 3 partitions
Consumer Group with 2 consumers:
  Consumer 1: Partition 0, 1
  Consumer 2: Partition 2
```

**Benefits:**
- Parallel processing
- Scalability
- Fault tolerance

I use consumer groups to scale message processing, adding consumers as load increases."

**Key Points:**
- Parallel consumption
- Load balancing
- Offset tracking
- Scalability

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How do you ensure exactly-once semantics?

**Answer:**
"**1. Idempotent Producer**
```python
producer = KafkaProducer(
    enable_idempotence=True,
    acks='all'
)
```

**2. Transactions**
```python
producer.begin_transaction()
producer.send('topic1', value='data1')
producer.send('topic2', value='data2')
producer.commit_transaction()
```

**3. Consumer Offset Management**
- Commit offsets after processing
- Idempotent processing
- Handle duplicates

**4. Exactly-Once Processing**
- Idempotent operations
- Transactional writes
- Careful offset management

I implement idempotent producers, transactions, and careful offset management to ensure exactly-once semantics."

**Key Points:**
- Idempotent producer
- Transactions
- Offset management
- Idempotent processing

---

### Q5: How do you handle Kafka failures?

**Answer:**
"**1. Replication**
- Replication factor 3
- Multiple broker copies
- Automatic failover

**2. Producer Retries**
```python
producer = KafkaProducer(
    retries=3,
    acks='all'
)
```

**3. Consumer Error Handling**
- Handle exceptions
- Dead letter queue
- Retry logic

**4. Monitoring**
- Monitor lag
- Track failures
- Alert on issues

**5. Backup**
- Regular backups
- Disaster recovery plan

I implement replication, retries, error handling, and monitoring to ensure reliable operation."

**Key Points:**
- Replication
- Retries
- Error handling
- Monitoring

---

## 🔴 ADVANCED LEVEL Questions

### Q6: How do you design a Kafka-based streaming architecture?

**Answer:**
"**Architecture:**

**1. Producers**
- Multiple producers
- Partition by key
- Idempotent writes

**2. Kafka Cluster**
- Multiple brokers
- Replication factor 3
- Topic partitioning

**3. Stream Processing**
- Kafka Streams
- Spark Streaming
- Flink

**4. Consumers**
- Consumer groups
- Parallel processing
- Offset management

**5. Storage**
- Long retention
- Archive old data
- Data lake integration

**Components:**
- Kafka cluster
- Stream processors
- Consumer applications
- Monitoring

This architecture handles millions of messages per second with high reliability."

**Key Points:**
- Multi-layer architecture
- Stream processing
- Scalable design
- Monitoring

---

## 🎯 Key Takeaways

1. **Kafka = Event Streaming**
2. **Topics = Categories**
3. **Partitions = Scalability**
4. **Consumer Groups = Parallel Processing**
5. **Replication = Durability**

---

## ✅ Practice Checklist

- [ ] Can explain Kafka in 2 minutes
- [ ] Understand topics/partitions
- [ ] Know consumer groups
- [ ] Understand exactly-once
- [ ] Know failure handling
- [ ] Ready for system design questions

---

**Remember**: Kafka is critical for real-time streaming!

