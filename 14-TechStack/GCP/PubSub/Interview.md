# Pub/Sub Interview Questions and Answers

## Beginner Level Questions

### 1. What is Cloud Pub/Sub and why is it used?

**Answer:**
Cloud Pub/Sub is Google Cloud's fully managed messaging service that enables asynchronous communication between applications. It's used for:

- **Decoupling Services**: Separating producers and consumers of messages
- **Event-Driven Architecture**: Building reactive, event-based systems
- **Real-time Data Processing**: Handling streaming data and real-time analytics
- **Scalability**: Supporting high-throughput messaging at global scale

Pub/Sub provides reliable, scalable messaging without requiring infrastructure management.

### 2. Explain the basic components of Pub/Sub.

**Answer:**
The main components are:

- **Topics**: Named channels where publishers send messages
- **Subscriptions**: Named resources that receive messages from topics
- **Publishers**: Applications or services that send messages to topics
- **Subscribers**: Applications or services that receive and process messages
- **Messages**: The data being transmitted, containing payload and metadata

Topics can have multiple subscriptions, enabling fan-out messaging patterns.

### 3. How do you create a topic in Pub/Sub?

**Answer:**
You can create topics through multiple methods:

**Google Cloud Console:**
1. Go to Pub/Sub in the Cloud Console
2. Click "Create Topic"
3. Enter topic ID and configure settings
4. Enable message ordering if needed

**gcloud CLI:**
```bash
gcloud pubsub topics create my-topic
```

**Client Libraries:**
```python
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("my-project", "my-topic")

topic = publisher.create_topic(topic_path)
print(f"Created topic: {topic.name}")
```

### 4. What is the difference between pull and push subscriptions?

**Answer:**
**Pull Subscriptions:**
- Subscribers explicitly request messages from Pub/Sub
- Better for batch processing and controlled consumption
- Requires polling for new messages
- More control over message processing rate

**Push Subscriptions:**
- Pub/Sub automatically pushes messages to subscriber endpoints
- Better for real-time processing and event-driven systems
- Requires HTTP endpoints that can handle incoming requests
- Lower latency but less control over processing

## Intermediate Level Questions

### 5. How does message ordering work in Pub/Sub?

**Answer:**
Message ordering ensures messages with the same ordering key are delivered in publish order:

**How it works:**
- Set `ordering_key` when publishing messages
- Messages with same key delivered in order to same subscriber
- Different keys can be processed in parallel
- Ordering maintained per ordering key, not globally

**Example:**
```python
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project, topic)

# Messages with same ordering key maintain order
publisher.publish(topic_path, b"message 1", ordering_key="user123")
publisher.publish(topic_path, b"message 2", ordering_key="user123")
publisher.publish(topic_path, b"message 3", ordering_key="user456")
```

**Trade-offs:**
- Reduced throughput due to sequential processing
- Increased latency for ordered messages
- Use only when ordering is critical

### 6. How do you handle message processing failures in Pub/Sub?

**Answer:**
Pub/Sub provides several mechanisms for handling failures:

**Acknowledgment:**
- Subscribers must acknowledge successful processing
- Unacknowledged messages are redelivered
- Acknowledgment deadline can be extended

**Dead Letter Topics:**
```python
from google.cloud import pubsub_v1

subscription = pubsub_v1.Subscription(
    name=subscription_path,
    topic=topic_path,
    dead_letter_policy=pubsub_v1.DeadLetterPolicy(
        dead_letter_topic=dead_letter_topic_path,
        max_delivery_attempts=5,
    ),
)
```

**Retry Policies:**
- Exponential backoff for failed deliveries
- Configurable retry delays and maximum attempts
- Circuit breaker patterns for downstream failures

**Error Handling Best Practices:**
- Implement idempotent message processing
- Use dead letter topics for poison messages
- Monitor delivery attempts and failure rates
- Implement proper error logging and alerting

### 7. What are the performance limits of Pub/Sub?

**Answer:**
Pub/Sub has soft limits that can be increased:

**Throughput Limits:**
- **Publishing**: 10 MB/s per topic (soft limit)
- **Subscribing**: 10 MB/s per subscription (soft limit)
- **Global Distribution**: Messages replicated across regions

**Message Limits:**
- **Size**: 10 MB compressed, 100 MB uncompressed
- **Retention**: 31 days maximum
- **Attributes**: 100 attributes per message, 1 KB each

**Quota Limits:**
- **Topics**: 10,000 per project
- **Subscriptions**: 10,000 per topic
- **Concurrent Publishers**: Unlimited
- **Message Rate**: Millions per second globally

### 8. How do you monitor Pub/Sub performance?

**Answer:**
Pub/Sub provides comprehensive monitoring through Cloud Monitoring:

**Key Metrics:**
- **Publish Request Count**: Number of publish requests
- **Subscribe Request Count**: Number of subscribe requests
- **Unacked Message Count**: Messages awaiting acknowledgment
- **Oldest Unacked Message Age**: Age of oldest unacked message

**Monitoring Queries:**
```sql
-- Monitor subscription backlog
SELECT
  subscription_name,
  num_undelivered_messages,
  oldest_unacked_message_age_seconds
FROM `pubsub_subscription_stats`
WHERE subscription_name LIKE '%my-subscription%';
```

**Alerting:**
- Set up alerts for high unacked message counts
- Monitor publish/subscribe error rates
- Track message processing latency
- Alert on dead letter queue growth

**Best Practices:**
- Monitor end-to-end latency
- Track message duplication rates
- Monitor subscription throughput
- Set up proper dashboards and alerts

### 9. How do you implement exactly-once processing with Pub/Sub?

**Answer:**
Exactly-once processing requires careful design:

**Idempotent Processing:**
- Design consumers to handle duplicate messages
- Use message IDs for deduplication
- Implement transactional processing

**State Management:**
- Store processing state externally (database, cache)
- Use message IDs to track processed messages
- Implement proper error handling and rollback

**Example Pattern:**
```python
def process_message(message):
    message_id = message.message_id

    # Check if already processed
    if is_message_processed(message_id):
        message.ack()
        return

    try:
        # Process message
        process_data(message.data)

        # Mark as processed
        mark_message_processed(message_id)

        message.ack()

    except Exception as e:
        # Handle error - don't ack if processing failed
        logger.error(f"Failed to process message {message_id}: {e}")
        # Message will be redelivered
```

**Limitations:**
- Pub/Sub guarantees at-least-once delivery
- Exactly-once requires application-level deduplication
- Network partitions can cause duplicates

### 10. What is a dead letter topic and when to use it?

**Answer:**
A dead letter topic handles messages that cannot be processed successfully:

**Purpose:**
- Store messages that repeatedly fail processing
- Prevent poison messages from blocking subscription
- Enable separate processing of failed messages

**Configuration:**
```python
dead_letter_policy = pubsub_v1.DeadLetterPolicy(
    dead_letter_topic=dead_letter_topic_path,
    max_delivery_attempts=5,
)

subscription = pubsub_v1.Subscription(
    name=subscription_path,
    topic=topic_path,
    dead_letter_policy=dead_letter_policy,
)
```

**Use Cases:**
- Invalid message formats
- Downstream service failures
- Processing logic errors
- Temporary resource constraints

**Management:**
- Monitor dead letter topic growth
- Implement separate processing for failed messages
- Set appropriate retry limits
- Alert on dead letter queue accumulation

## Advanced Level Questions

### 11. How do you design a real-time analytics pipeline with Pub/Sub?

**Answer:**
Real-time analytics pipeline design:

**Architecture:**
1. **Data Ingestion**: Collect data from various sources
2. **Message Queue**: Use Pub/Sub for reliable buffering
3. **Stream Processing**: Process data with Dataflow
4. **Storage**: Store processed data in BigQuery
5. **Analytics**: Create real-time dashboards

**Implementation:**
```python
# Publisher - Ingest data
def publish_sensor_data(sensor_id, temperature, timestamp):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, "sensor-data")

    data = {
        "sensor_id": sensor_id,
        "temperature": temperature,
        "timestamp": timestamp
    }

    message = json.dumps(data).encode("utf-8")
    publisher.publish(topic_path, message)

# Subscriber - Process data
def process_sensor_data(message):
    data = json.loads(message.data.decode("utf-8"))

    # Validate data
    if validate_sensor_reading(data):
        # Store in BigQuery
        store_in_bigquery(data)

        # Check for anomalies
        if detect_anomaly(data):
            trigger_alert(data)

    message.ack()
```

**Considerations:**
- Message ordering requirements
- Exactly-once processing needs
- Scalability and throughput requirements
- Cost optimization strategies

### 12. How do you implement event-driven microservices with Pub/Sub?

**Answer:**
Event-driven microservices architecture:

**Design Principles:**
- Services communicate through events
- Loose coupling between services
- Asynchronous communication
- Event sourcing for state management

**Implementation Pattern:**
```python
# Service publishes events
def create_order(order_data):
    # Create order in database
    order_id = save_order(order_data)

    # Publish order created event
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, "order-events")

    event = {
        "event_type": "order_created",
        "order_id": order_id,
        "customer_id": order_data["customer_id"],
        "amount": order_data["amount"]
    }

    publisher.publish(topic_path, json.dumps(event).encode("utf-8"))

    return order_id

# Other services subscribe to events
def handle_order_events(message):
    event = json.loads(message.data.decode("utf-8"))

    if event["event_type"] == "order_created":
        # Update inventory
        update_inventory(event["order_id"])

        # Send notification
        send_order_notification(event["customer_id"])

    message.ack()
```

**Benefits:**
- Scalable communication between services
- Fault-tolerant and resilient architecture
- Easy to add new consumers
- Supports complex event flows

### 13. What are the cost optimization strategies for Pub/Sub?

**Answer:**
Pub/Sub cost optimization approaches:

**Data Optimization:**
- Compress message payloads
- Use efficient serialization formats
- Minimize message sizes
- Batch multiple events into single messages

**Operation Optimization:**
- Batch publish operations
- Use appropriate retention periods
- Implement subscription filtering
- Minimize seek operations

**Architecture Optimization:**
- Use appropriate subscription types (pull vs push)
- Implement efficient message processing
- Monitor and optimize throughput
- Use dead letter topics appropriately

**Cost Monitoring:**
```sql
-- Monitor Pub/Sub costs
SELECT
  service.description,
  sku.description,
  SUM(cost) as total_cost,
  SUM(usage.amount) as total_usage
FROM `project.billing.gcp_billing_export_v1_xxxxxx`
WHERE service.description = "Cloud Pub/Sub"
  AND DATE(_PARTITIONTIME) >= "2023-01-01"
GROUP BY service.description, sku.description
ORDER BY total_cost DESC;
```

### 14. How do you implement cross-region Pub/Sub architectures?

**Answer:**
Cross-region Pub/Sub implementation:

**Global Topics:**
- Topics are global resources by default
- Messages automatically replicated across regions
- Subscribers can be in any region

**Regional Considerations:**
- Publisher and subscriber proximity affects latency
- Cross-region replication has cost implications
- Compliance requirements may dictate regions

**Best Practices:**
- Place publishers close to data sources
- Locate subscribers near processing resources
- Use global load balancers for cross-region distribution
- Monitor cross-region latency and costs

**High Availability:**
- Topics are highly available across regions
- Automatic failover between regions
- No single point of failure

### 15. How do you handle schema evolution in Pub/Sub?

**Answer:**
Schema evolution strategies:

**Schema Registry:**
- Define message schemas in Pub/Sub Schema Registry
- Support for Protocol Buffers and Avro schemas
- Schema validation at publish time

**Backward Compatibility:**
- Add optional fields for new versions
- Avoid removing required fields
- Use schema versioning

**Implementation:**
```python
# Create schema
from google.cloud import pubsub_v1

schema_client = pubsub_v1.SchemaServiceClient()
schema = pubsub_v1.Schema(
    name=schema_path,
    type_=pubsub_v1.Schema.Type.PROTOCOL_BUFFER,
    definition=proto_definition
)

schema_client.create_schema(schema)

# Use schema in topic
topic = pubsub_v1.Topic(
    name=topic_path,
    schema_settings=pubsub_v1.SchemaSettings(
        schema=schema_path,
        encoding=pubsub_v1.Encoding.JSON
    )
)
```

**Migration Strategies:**
- Gradual rollout of schema changes
- Support multiple schema versions
- Use topic migration patterns
- Implement proper testing

### 16. What are the security best practices for Pub/Sub?

**Answer:**
Pub/Sub security implementation:

**Access Control:**
- Use IAM for fine-grained permissions
- Implement least privilege access
- Use service accounts for applications
- Regular permission audits

**Network Security:**
- Use VPC Service Controls for private access
- Implement Private Google Access
- Use Private Service Connect for secure connections

**Data Protection:**
- Enable CMEK for data encryption
- Implement client-side encryption if needed
- Use TLS 1.2+ for data in transit

**Monitoring:**
- Enable Cloud Audit Logs
- Monitor access patterns
- Implement security alerting
- Regular security assessments

### 17. How do you implement message filtering in Pub/Sub?

**Answer:**
Message filtering allows selective message delivery:

**Subscription Filtering:**
```sql
-- Create filtered subscription
CREATE SUBSCRIPTION my_subscription
  FROM my_topic
  WHERE attributes.event_type = "order_created"
    AND attributes.region = "us-west1";
```

**Filter Syntax:**
- Support for attribute-based filtering
- Boolean operators (AND, OR, NOT)
- Comparison operators (=, !=, >, <, etc.)
- String matching and numeric comparisons

**Use Cases:**
- Route messages to specific consumers
- Reduce unnecessary message processing
- Implement event-driven routing
- Support multi-tenant architectures

**Performance Considerations:**
- Filtering happens server-side
- Reduces network traffic and processing costs
- Complex filters may impact performance
- Monitor filter effectiveness

### 18. How do you implement Pub/Sub in a CI/CD pipeline?

**Answer:**
CI/CD integration for Pub/Sub:

**Infrastructure as Code:**
```yaml
# Terraform for Pub/Sub resources
resource "google_pubsub_topic" "orders" {
  name = "orders-topic"
}

resource "google_pubsub_subscription" "order_processor" {
  name  = "order-processor-sub"
  topic = google_pubsub_topic.orders.name
}
```

**Testing:**
- Unit tests for publishers and subscribers
- Integration tests for end-to-end message flow
- Load testing for performance validation
- Schema validation testing

**Deployment:**
- Blue-green deployments for subscriptions
- Gradual rollout of topic changes
- Rollback strategies for failed deployments
- Monitoring and alerting for deployment issues

**Best Practices:**
- Version control for Pub/Sub configurations
- Automated testing in CI pipelines
- Gradual rollout and rollback capabilities
- Comprehensive monitoring and alerting

### 19. What are the differences between Pub/Sub and other messaging systems?

**Answer:**
Comparison with other messaging systems:

**vs Apache Kafka:**
- **Managed Service**: Pub/Sub is fully managed vs Kafka requires infrastructure
- **Scalability**: Both highly scalable, Pub/Sub has simpler scaling
- **Ecosystem**: Kafka has broader ecosystem, Pub/Sub integrates with GCP
- **Cost**: Pub/Sub pay-per-use vs Kafka infrastructure costs

**vs RabbitMQ:**
- **Cloud-native**: Pub/Sub designed for cloud scale
- **Durability**: Both provide durability, Pub/Sub has better global distribution
- **Management**: Pub/Sub fully managed vs RabbitMQ requires operations
- **Protocols**: Pub/Sub HTTP/REST vs RabbitMQ AMQP

**vs Amazon SQS:**
- **Ordering**: Pub/Sub supports message ordering, SQS does not
- **Throughput**: Pub/Sub higher throughput limits
- **Push Delivery**: Both support push, Pub/Sub has better integration
- **Global**: Both support global distribution

### 20. How do you troubleshoot Pub/Sub issues?

**Answer:**
Pub/Sub troubleshooting methodology:

**Common Issues:**
- Messages not being delivered
- High latency or low throughput
- Permission denied errors
- Message processing failures

**Diagnostic Steps:**
1. **Check Topic/Subscription Status:**
```bash
gcloud pubsub topics describe my-topic
gcloud pubsub subscriptions describe my-subscription
```

2. **Monitor Metrics:**
```sql
-- Check subscription health
SELECT
  subscription_name,
  num_undelivered_messages,
  oldest_unacked_message_age_seconds,
  ack_deadline_seconds
FROM `pubsub_subscription_stats`;
```

3. **Review Logs:**
- Cloud Logging for Pub/Sub operations
- Application logs for processing errors
- Audit logs for access issues

4. **Common Solutions:**
- Check IAM permissions
- Verify subscription configuration
- Monitor resource quotas
- Review message processing logic

**Advanced Debugging:**
- Use Pub/Sub emulator for local testing
- Implement detailed logging
- Monitor end-to-end message flow
- Use distributed tracing

## Scenario-Based Questions

### 21. How would you design a notification system using Pub/Sub?

**Answer:**
Notification system design:

**Requirements:**
- Multiple notification channels (email, SMS, push)
- Reliable delivery with retries
- Scalable to millions of notifications
- Real-time processing

**Architecture:**
```python
# Publisher - Generate notifications
def send_notification(user_id, message_type, data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, "notifications")

    notification = {
        "user_id": user_id,
        "type": message_type,  # email, sms, push
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

    publisher.publish(topic_path, json.dumps(notification).encode("utf-8"))

# Subscribers - Process different notification types
def process_email_notifications(message):
    notification = json.loads(message.data.decode("utf-8"))

    if notification["type"] == "email":
        send_email(notification["user_id"], notification["data"])

    message.ack()

def process_sms_notifications(message):
    notification = json.loads(message.data.decode("utf-8"))

    if notification["type"] == "sms":
        send_sms(notification["user_id"], notification["data"])

    message.ack()
```

**Features:**
- Fan-out to multiple subscribers
- Filtering by notification type
- Dead letter queues for failed deliveries
- Monitoring and alerting

### 22. How would you implement event sourcing with Pub/Sub?

**Answer:**
Event sourcing implementation:

**Principles:**
- Store all changes as events
- Rebuild state from event history
- Immutable event log
- Event-driven architecture

**Implementation:**
```python
# Event publishing
def publish_event(aggregate_id, event_type, event_data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, "events")

    event = {
        "aggregate_id": aggregate_id,
        "event_type": event_type,
        "event_data": event_data,
        "timestamp": datetime.utcnow().isoformat(),
        "version": get_next_version(aggregate_id)
    }

    # Use ordering key for aggregate consistency
    publisher.publish(
        topic_path,
        json.dumps(event).encode("utf-8"),
        ordering_key=str(aggregate_id)
    )

# Event processing
def process_events(message):
    event = json.loads(message.data.decode("utf-8"))

    # Store event in event store
    store_event(event)

    # Update read models/materialized views
    update_read_model(event)

    # Publish integration events if needed
    if should_publish_integration_event(event):
        publish_integration_event(event)

    message.ack()
```

**Benefits:**
- Complete audit trail
- Temporal queries possible
- Easy debugging and analysis
- Scalable event processing

### 23. How would you migrate from another messaging system to Pub/Sub?

**Answer:**
Migration strategy:

**Assessment Phase:**
- Analyze current messaging usage
- Identify publishers and subscribers
- Document message schemas and volumes
- Assess performance requirements

**Planning Phase:**
- Design Pub/Sub topics and subscriptions
- Plan message format conversions
- Design migration rollout strategy
- Prepare rollback procedures

**Implementation Phase:**
1. **Create Pub/Sub Resources:**
```bash
# Create topics
gcloud pubsub topics create user-events
gcloud pubsub topics create order-events

# Create subscriptions
gcloud pubsub subscriptions create user-processor --topic=user-events
gcloud pubsub subscriptions create order-processor --topic=order-events
```

2. **Migrate Publishers:**
- Update publisher code to use Pub/Sub
- Implement message format conversions
- Test publishing functionality

3. **Migrate Subscribers:**
- Update subscriber code for Pub/Sub
- Implement message processing logic
- Test subscription functionality

4. **Gradual Rollout:**
- Use feature flags for gradual migration
- Monitor performance and errors
- Implement proper logging and monitoring

**Post-Migration:**
- Remove old messaging infrastructure
- Optimize Pub/Sub configuration
- Monitor costs and performance
- Document lessons learned

## Summary

Pub/Sub interview questions typically cover:
- Basic concepts and architecture
- Message delivery semantics and ordering
- Error handling and reliability patterns
- Performance monitoring and optimization
- Security and compliance
- Integration patterns and real-world use cases
- Cost optimization strategies
- Migration and operational considerations

Focus on understanding Pub/Sub's role in event-driven architectures, reliability guarantees, and integration with Google Cloud ecosystem rather than just API details.
