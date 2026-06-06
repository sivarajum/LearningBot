# Apache Kafka: Comprehensive Guide

## Overview

Apache Kafka is a distributed event streaming platform designed for high-throughput, fault-tolerant, and scalable real-time data processing. It serves as a central nervous system for modern data architectures, enabling the building of real-time streaming data pipelines and applications.

## Core Concepts

### Event Streaming Fundamentals

```python
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import time

# Event structure
class Event:
    def __init__(self, event_type, payload, timestamp=None, key=None):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp or int(time.time() * 1000)
        self.key = key

    def to_dict(self):
        return {
            'event_type': self.event_type,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'key': self.key
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            event_type=data['event_type'],
            payload=data['payload'],
            timestamp=data.get('timestamp'),
            key=data.get('key')
        )
```

### Topics and Partitions

```python
# Topic management
def create_topic(admin_client, topic_name, num_partitions=3, replication_factor=2):
    """Create a Kafka topic with specified configuration"""

    topic = NewTopic(
        name=topic_name,
        num_partitions=num_partitions,
        replication_factor=replication_factor,
        topic_configs={
            'retention.ms': str(7 * 24 * 60 * 60 * 1000),  # 7 days
            'segment.ms': str(24 * 60 * 60 * 1000),  # 1 day
            'cleanup.policy': 'delete'
        }
    )

    try:
        admin_client.create_topics([topic])
        print(f"Topic '{topic_name}' created successfully")
    except Exception as e:
        print(f"Failed to create topic: {e}")

def list_topics(admin_client):
    """List all available topics"""

    topics = admin_client.list_topics()
    for topic in topics:
        # Get topic details
        topic_details = admin_client.describe_topics([topic])
        partitions = len(topic_details[0]['partitions'])
        print(f"Topic: {topic}, Partitions: {partitions}")

# Partition assignment strategies
def manual_partition_assignment(key, num_partitions):
    """Manual partition assignment based on key"""

    if key is None:
        return None  # Let Kafka assign randomly

    # Hash-based partitioning
    partition = hash(key) % num_partitions
    return partition

def round_robin_partition_assignment(message_count, num_partitions):
    """Round-robin partition assignment"""

    return message_count % num_partitions
```

## Producers

### Basic Producer Implementation

```python
class KafkaEventProducer:
    def __init__(self, bootstrap_servers, topic_name):
        self.topic_name = topic_name
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            retries=3,
            max_in_flight_requests_per_connection=1,  # Ensure ordering
            compression_type='gzip'
        )

    def send_event(self, event, key=None, partition=None):
        """Send an event to Kafka"""

        try:
            future = self.producer.send(
                self.topic_name,
                value=event.to_dict(),
                key=key,
                partition=partition
            )

            # Wait for acknowledgment
            record_metadata = future.get(timeout=10)

            print(f"Event sent to topic: {record_metadata.topic}")
            print(f"Partition: {record_metadata.partition}")
            print(f"Offset: {record_metadata.offset}")

            return record_metadata

        except Exception as e:
            print(f"Failed to send event: {e}")
            return None

    def send_batch(self, events, key_func=None):
        """Send multiple events in batch"""

        for event in events:
            key = key_func(event) if key_func else None
            self.send_event(event, key=key)

        # Force send all pending messages
        self.producer.flush()

    def close(self):
        """Close the producer"""
        self.producer.close()

# Usage example
def user_registration_producer():
    producer = KafkaEventProducer(['localhost:9092'], 'user-events')

    # Create user registration event
    user_event = Event(
        event_type='USER_REGISTERED',
        payload={
            'user_id': '12345',
            'email': 'user@example.com',
            'registration_date': '2024-01-15'
        },
        key='12345'  # Use user_id as key for partitioning
    )

    producer.send_event(user_event)
    producer.close()
```

### Advanced Producer Features

```python
class ReliableKafkaProducer:
    def __init__(self, bootstrap_servers, topic_name):
        self.topic_name = topic_name
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None,
            acks='all',
            retries=5,
            retry_backoff_ms=100,
            max_in_flight_requests_per_connection=1,
            enable_idempotence=True,  # Exactly-once semantics
            transactional_id='user-producer-001' if topic_name == 'user-events' else None,
            compression_type='lz4'
        )

    def send_with_callback(self, event, key=None):
        """Send event with delivery callback"""

        def delivery_callback(record_metadata, exception):
            if exception:
                print(f"Failed to deliver message: {exception}")
            else:
                print(f"Message delivered to {record_metadata.topic} "
                      f"partition {record_metadata.partition} "
                      f"offset {record_metadata.offset}")

        try:
            self.producer.send(
                self.topic_name,
                value=event.to_dict(),
                key=key
            ).add_callback(delivery_callback).add_errback(lambda e: print(f"Error: {e}"))

        except Exception as e:
            print(f"Failed to send: {e}")

    def transactional_send(self, events):
        """Send events transactionally"""

        try:
            self.producer.begin_transaction()

            for event in events:
                self.producer.send(self.topic_name, value=event.to_dict())

            # Commit transaction
            self.producer.commit_transaction()
            print("Transaction committed successfully")

        except Exception as e:
            print(f"Transaction failed: {e}")
            self.producer.abort_transaction()

class BufferedProducer:
    def __init__(self, bootstrap_servers, topic_name, batch_size=100, flush_interval=5):
        self.topic_name = topic_name
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,  # 16KB
            linger_ms=10,  # Wait 10ms for batching
            compression_type='snappy'
        )

    def add_to_buffer(self, event):
        """Add event to buffer"""

        self.buffer.append(event)

        # Check if we should flush
        current_time = time.time()
        if (len(self.buffer) >= self.batch_size or
            current_time - self.last_flush >= self.flush_interval):
            self.flush_buffer()

    def flush_buffer(self):
        """Flush buffered events"""

        if not self.buffer:
            return

        try:
            for event in self.buffer:
                self.producer.send(self.topic_name, value=event.to_dict())

            self.producer.flush()
            print(f"Flushed {len(self.buffer)} events")
            self.buffer.clear()
            self.last_flush = time.time()

        except Exception as e:
            print(f"Failed to flush buffer: {e}")
```

## Consumers

### Basic Consumer Implementation

```python
class KafkaEventConsumer:
    def __init__(self, bootstrap_servers, topic_name, group_id):
        self.topic_name = topic_name
        self.consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',  # Start from beginning
            enable_auto_commit=False,  # Manual commit for reliability
            consumer_timeout_ms=1000
        )

    def consume_events(self, process_func, batch_size=10):
        """Consume and process events"""

        try:
            while True:
                # Poll for messages
                messages = self.consumer.poll(timeout_ms=1000)

                if not messages:
                    continue

                batch = []
                for topic_partition, records in messages.items():
                    for record in records:
                        event = Event.from_dict(record.value)
                        batch.append((record, event))

                        if len(batch) >= batch_size:
                            self._process_batch(batch, process_func)
                            batch = []

                # Process remaining batch
                if batch:
                    self._process_batch(batch, process_func)

        except KeyboardInterrupt:
            print("Consumer stopped")
        finally:
            self.consumer.close()

    def _process_batch(self, batch, process_func):
        """Process a batch of events"""

        try:
            # Process events
            for record, event in batch:
                process_func(event, record)

            # Manual commit after successful processing
            self.consumer.commit()

        except Exception as e:
            print(f"Failed to process batch: {e}")
            # Don't commit on failure - will retry

# Usage example
def user_event_processor(event, record):
    """Process user events"""

    print(f"Processing event: {event.event_type}")
    print(f"User ID: {event.payload.get('user_id')}")
    print(f"Partition: {record.partition}, Offset: {record.offset}")

    # Business logic here
    if event.event_type == 'USER_REGISTERED':
        # Send welcome email, create user profile, etc.
        print("User registration processed")
    elif event.event_type == 'USER_UPDATED':
        # Update user profile
        print("User profile updated")

def start_user_consumer():
    consumer = KafkaEventConsumer(
        ['localhost:9092'],
        'user-events',
        'user-processor-group'
    )

    consumer.consume_events(user_event_processor)
```

### Advanced Consumer Patterns

```python
class BatchConsumer:
    def __init__(self, bootstrap_servers, topic_name, group_id, batch_size=100, timeout=30):
        self.consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False,
            consumer_timeout_ms=1000
        )

        self.batch_size = batch_size
        self.timeout = timeout

    def consume_batch(self):
        """Consume messages in batches"""

        batch = []
        start_time = time.time()

        while len(batch) < self.batch_size:
            if time.time() - start_time > self.timeout:
                break  # Timeout reached

            message = self.consumer.poll(timeout_ms=100)

            if message:
                for topic_partition, records in message.items():
                    for record in records:
                        batch.append(record)

                        if len(batch) >= self.batch_size:
                            break

            if len(batch) >= self.batch_size:
                break

        return batch

    def process_batch_with_retry(self, batch, processor, max_retries=3):
        """Process batch with retry logic"""

        for attempt in range(max_retries):
            try:
                # Process batch
                processor(batch)

                # Commit offsets
                self.consumer.commit()
                return True

            except Exception as e:
                print(f"Batch processing failed (attempt {attempt + 1}): {e}")

                if attempt == max_retries - 1:
                    # Last attempt failed - send to dead letter queue
                    self._send_to_dlq(batch, e)
                    return False

                time.sleep(2 ** attempt)  # Exponential backoff

        return False

    def _send_to_dlq(self, batch, error):
        """Send failed messages to dead letter queue"""

        dlq_producer = KafkaProducer(
            bootstrap_servers=self.consumer.config['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        for record in batch:
            dlq_message = {
                'original_topic': record.topic,
                'original_partition': record.partition,
                'original_offset': record.offset,
                'original_message': record.value,
                'error': str(error),
                'timestamp': int(time.time() * 1000)
            }

            dlq_producer.send('dead-letter-queue', value=dlq_message)

        dlq_producer.close()

class ExactlyOnceConsumer:
    def __init__(self, bootstrap_servers, topic_name, group_id, output_topic):
        self.consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False,
            isolation_level='read_committed'  # Read only committed messages
        )

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            transactional_id=f"{group_id}-processor",
            enable_idempotence=True
        )

        self.output_topic = output_topic

    def process_transactionally(self, processor):
        """Process messages with exactly-once semantics"""

        try:
            while True:
                # Poll for messages
                messages = self.consumer.poll(timeout_ms=1000)

                if not messages:
                    continue

                # Begin transaction
                self.producer.begin_transaction()

                processed_messages = []

                # Process each message
                for topic_partition, records in messages.items():
                    for record in records:
                        # Process message
                        result = processor(record.value)

                        if result:
                            # Send result to output topic
                            self.producer.send(self.output_topic, value=result)

                        processed_messages.append(record)

                # Commit consumer offsets and producer transaction
                offsets = {
                    TopicPartition(record.topic, record.partition): OffsetAndMetadata(record.offset + 1, None)
                    for record in processed_messages
                }

                self.producer.send_offsets_to_transaction(offsets, self.consumer.consumer_group_metadata())
                self.producer.commit_transaction()

                print(f"Processed {len(processed_messages)} messages transactionally")

        except Exception as e:
            print(f"Transaction failed: {e}")
            self.producer.abort_transaction()
```

## Kafka Streams

### Stream Processing Basics

```python
from kafka import KafkaConsumer, KafkaProducer
from collections import defaultdict
import threading
import time

class StreamProcessor:
    def __init__(self, input_topic, output_topic, bootstrap_servers):
        self.input_topic = input_topic
        self.output_topic = output_topic

        self.consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=bootstrap_servers,
            group_id='stream-processor',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False
        )

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def filter_events(self, event_filter):
        """Filter events based on criteria"""

        def processor():
            try:
                while True:
                    messages = self.consumer.poll(timeout_ms=1000)

                    for topic_partition, records in messages.items():
                        for record in records:
                            event = Event.from_dict(record.value)

                            if event_filter(event):
                                # Forward filtered event
                                self.producer.send(self.output_topic, value=record.value)

                    self.consumer.commit()

            except KeyboardInterrupt:
                print("Stream processor stopped")

        return processor

    def aggregate_events(self, window_size=60, slide_interval=10):
        """Aggregate events in sliding windows"""

        windows = defaultdict(list)
        last_slide = time.time()

        def processor():
            try:
                while True:
                    current_time = time.time()

                    # Slide window if needed
                    if current_time - last_slide >= slide_interval:
                        self._slide_window(windows, current_time - window_size)
                        last_slide = current_time

                    messages = self.consumer.poll(timeout_ms=1000)

                    for topic_partition, records in messages.items():
                        for record in records:
                            event = Event.from_dict(record.value)
                            window_key = int(event.timestamp / 1000 / slide_interval) * slide_interval

                            windows[window_key].append(event)

                            # Emit aggregations for completed windows
                            self._emit_aggregations(windows, current_time - window_size)

                    self.consumer.commit()

            except KeyboardInterrupt:
                print("Aggregation processor stopped")

        return processor

    def _slide_window(self, windows, cutoff_time):
        """Remove old windows"""

        to_remove = []
        for window_key, events in windows.items():
            if window_key < cutoff_time:
                to_remove.append(window_key)

        for key in to_remove:
            del windows[key]

    def _emit_aggregations(self, windows, cutoff_time):
        """Emit window aggregations"""

        for window_key, events in windows.items():
            if window_key < cutoff_time:
                continue

            # Calculate aggregations
            event_count = len(events)
            event_types = defaultdict(int)

            for event in events:
                event_types[event.event_type] += 1

            aggregation = {
                'window_start': window_key,
                'window_end': window_key + 60,
                'total_events': event_count,
                'event_types': dict(event_types),
                'timestamp': int(time.time() * 1000)
            }

            self.producer.send(self.output_topic, value=aggregation)

# Usage examples
def filter_user_logins():
    processor = StreamProcessor('user-events', 'user-logins', ['localhost:9092'])

    def login_filter(event):
        return event.event_type == 'USER_LOGIN'

    processor.filter_events(login_filter)()

def aggregate_user_activity():
    processor = StreamProcessor('user-events', 'user-activity-agg', ['localhost:9092'])
    processor.aggregate_events(window_size=300, slide_interval=60)()  # 5-minute windows
```

### Advanced Stream Processing

```python
class KafkaStreamsTopology:
    def __init__(self, application_id, bootstrap_servers):
        self.application_id = application_id
        self.bootstrap_servers = bootstrap_servers
        self.topology = {}

    def add_source(self, topic_name, key_deserializer=None, value_deserializer=None):
        """Add a source topic to the topology"""

        source_config = {
            'topic': topic_name,
            'key_deserializer': key_deserializer,
            'value_deserializer': value_deserializer
        }

        self.topology['source'] = source_config
        return self

    def add_processor(self, processor_name, processor_func, predecessors=None):
        """Add a processing node"""

        processor_config = {
            'name': processor_name,
            'function': processor_func,
            'predecessors': predecessors or []
        }

        if 'processors' not in self.topology:
            self.topology['processors'] = []

        self.topology['processors'].append(processor_config)
        return self

    def add_sink(self, topic_name, key_serializer=None, value_serializer=None):
        """Add a sink topic"""

        sink_config = {
            'topic': topic_name,
            'key_serializer': key_serializer,
            'value_serializer': value_serializer
        }

        self.topology['sink'] = sink_config
        return self

    def build(self):
        """Build the stream processing topology"""

        return StreamProcessingEngine(self.topology, self.bootstrap_servers)

class StreamProcessingEngine:
    def __init__(self, topology, bootstrap_servers):
        self.topology = topology
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.producer = None
        self.processors = {}

    def start(self):
        """Start the stream processing engine"""

        # Initialize consumer
        self.consumer = KafkaConsumer(
            self.topology['source']['topic'],
            bootstrap_servers=self.bootstrap_servers,
            group_id=f"{self.topology.get('application_id', 'stream-app')}-group",
            value_deserializer=self.topology['source'].get('value_deserializer'),
            enable_auto_commit=False
        )

        # Initialize producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=self.topology['sink'].get('value_serializer')
        )

        # Initialize processors
        for processor_config in self.topology.get('processors', []):
            self.processors[processor_config['name']] = processor_config['function']

        # Start processing loop
        self._process_loop()

    def _process_loop(self):
        """Main processing loop"""

        try:
            while True:
                messages = self.consumer.poll(timeout_ms=1000)

                for topic_partition, records in messages.items():
                    for record in records:
                        # Process through topology
                        result = self._process_record(record)

                        if result is not None:
                            # Send to sink
                            self.producer.send(self.topology['sink']['topic'], value=result)

                self.consumer.commit()

        except KeyboardInterrupt:
            print("Stream processing stopped")
        finally:
            self.consumer.close()
            self.producer.close()

    def _process_record(self, record):
        """Process a record through the topology"""

        current_value = record.value

        for processor_config in self.topology.get('processors', []):
            processor_func = self.processors[processor_config['name']]
            current_value = processor_func(current_value)

            if current_value is None:
                return None  # Filter out

        return current_value

# Example topology: User event processing pipeline
def create_user_processing_topology():
    topology = (KafkaStreamsTopology('user-event-processor', ['localhost:9092'])
                .add_source('user-events',
                           value_deserializer=lambda v: json.loads(v.decode('utf-8')))
                .add_processor('filter_active_users',
                             lambda event: event if event.get('user_status') == 'active' else None)
                .add_processor('enrich_user_data',
                             lambda event: enrich_user_profile(event))
                .add_processor('aggregate_session_data',
                             lambda event: aggregate_user_session(event))
                .add_sink('processed-user-events',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8')))

    return topology.build()

def enrich_user_profile(event):
    """Enrich user event with additional profile data"""

    # Simulate database lookup
    user_profile = {
        'user_id': event['user_id'],
        'name': 'John Doe',  # Would come from database
        'preferences': {'theme': 'dark', 'language': 'en'}
    }

    event['user_profile'] = user_profile
    return event

def aggregate_user_session(event):
    """Aggregate user session data"""

    # This would typically use state stores for session management
    session_data = {
        'session_id': f"session_{event['user_id']}_{int(time.time())}",
        'events_in_session': 1,
        'session_start': event['timestamp']
    }

    event['session_data'] = session_data
    return event
```

## Kafka Connect

### Source Connectors

```python
from kafka.connect import SourceConnector
import psycopg2
import json

class PostgreSQLSourceConnector(SourceConnector):
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.last_offset = {}

    def start(self):
        """Initialize the connector"""

        self.connection = psycopg2.connect(
            host=self.config['db_host'],
            port=self.config['db_port'],
            database=self.config['db_name'],
            user=self.config['db_user'],
            password=self.config['db_password']
        )

        # Load last processed offsets
        self._load_offsets()

    def poll(self):
        """Poll for new data"""

        records = []

        with self.connection.cursor() as cursor:
            # Query for new records since last offset
            for table in self.config['tables']:
                last_id = self.last_offset.get(table, 0)

                cursor.execute(f"""
                    SELECT * FROM {table}
                    WHERE id > %s
                    ORDER BY id
                    LIMIT %s
                """, (last_id, self.config.get('batch_size', 100)))

                columns = [desc[0] for desc in cursor.description]

                for row in cursor.fetchall():
                    record = dict(zip(columns, row))

                    # Create Kafka record
                    kafka_record = {
                        'topic': f"{self.config['topic_prefix']}.{table}",
                        'key': str(record['id']),
                        'value': json.dumps(record),
                        'timestamp': None
                    }

                    records.append(kafka_record)

                    # Update offset
                    self.last_offset[table] = max(self.last_offset.get(table, 0), record['id'])

        # Save offsets
        self._save_offsets()

        return records

    def stop(self):
        """Clean up resources"""

        if self.connection:
            self.connection.close()

    def _load_offsets(self):
        """Load offset information"""

        # In production, this would load from a persistent store
        self.last_offset = self.config.get('initial_offsets', {})

    def _save_offsets(self):
        """Save offset information"""

        # In production, this would save to a persistent store
        pass

# Configuration for PostgreSQL source connector
postgres_config = {
    'name': 'postgres-source',
    'connector.class': 'io.confluent.connect.jdbc.JdbcSourceConnector',
    'connection.url': 'jdbc:postgresql://localhost:5432/mydb',
    'connection.user': 'myuser',
    'connection.password': 'mypassword',
    'table.whitelist': 'users,orders',
    'mode': 'incrementing',
    'incrementing.column.name': 'id',
    'topic.prefix': 'postgres',
    'poll.interval.ms': 5000
}
```

### Sink Connectors

```python
from kafka.connect import SinkConnector
import elasticsearch
import json

class ElasticsearchSinkConnector(SinkConnector):
    def __init__(self, config):
        self.config = config
        self.es_client = None
        self.buffer = []
        self.batch_size = config.get('batch_size', 100)

    def start(self):
        """Initialize the connector"""

        self.es_client = elasticsearch.Elasticsearch(
            hosts=[self.config['es_host']],
            http_auth=(self.config['es_user'], self.config['es_password'])
        )

    def put(self, records):
        """Process records for indexing"""

        for record in records:
            # Transform record for Elasticsearch
            doc = {
                '_index': self.config['index_name'],
                '_id': record.key(),
                '_source': json.loads(record.value())
            }

            self.buffer.append(doc)

            # Flush when batch size reached
            if len(self.buffer) >= self.batch_size:
                self._flush_batch()

    def flush(self):
        """Flush any remaining records"""

        if self.buffer:
            self._flush_batch()

    def stop(self):
        """Clean up resources"""

        self.flush()
        if self.es_client:
            self.es_client.close()

    def _flush_batch(self):
        """Flush batch to Elasticsearch"""

        try:
            # Bulk index documents
            bulk_body = []
            for doc in self.buffer:
                bulk_body.append({'index': {'_index': doc['_index'], '_id': doc['_id']}})
                bulk_body.append(doc['_source'])

            response = self.es_client.bulk(body=bulk_body)

            if response['errors']:
                print(f"Elasticsearch bulk indexing errors: {response['errors']}")

            self.buffer.clear()

        except Exception as e:
            print(f"Failed to flush batch to Elasticsearch: {e}")

# Configuration for Elasticsearch sink connector
es_config = {
    'name': 'elasticsearch-sink',
    'connector.class': 'io.confluent.connect.elasticsearch.ElasticsearchSinkConnector',
    'topics': 'user-events,order-events',
    'connection.url': 'http://localhost:9200',
    'connection.username': 'elastic',
    'connection.password': 'password',
    'type.name': '_doc',
    'key.ignore': 'true',
    'schema.ignore': 'true',
    'behavior.on.malformed.documents': 'warn',
    'drop.invalid.message': 'true',
    'batch.size': '100',
    'max.buffered.records': '1000'
}
```

## Schema Registry and Serialization

### Avro Serialization

```python
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import io

# Define Avro schema
user_schema_str = """
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "user_id", "type": "string"},
    {"name": "email", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "registration_date", "type": ["null", "string"], "default": null},
    {"name": "preferences", "type": {
      "type": "map",
      "values": "string"
    }}
  ]
}
"""

class AvroSerializer:
    def __init__(self, schema_str):
        self.schema = avro.schema.parse(schema_str)
        self.writer = DatumWriter(self.schema)
        self.reader = DatumReader(self.schema)

    def serialize(self, data):
        """Serialize data to Avro bytes"""

        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        self.writer.write(data, encoder)
        return bytes_writer.getvalue()

    def deserialize(self, data_bytes):
        """Deserialize Avro bytes to data"""

        bytes_reader = io.BytesIO(data_bytes)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        return self.reader.read(decoder)

# Kafka producer with Avro serialization
class AvroKafkaProducer:
    def __init__(self, bootstrap_servers, schema_registry_url, topic_name):
        from confluent_kafka import Producer
        from confluent_kafka.schema_registry import SchemaRegistryClient
        from confluent_kafka.schema_registry.avro import AvroSerializer

        # Schema registry client
        schema_registry_client = SchemaRegistryClient({
            'url': schema_registry_url
        })

        # Avro serializer
        self.avro_serializer = AvroSerializer(
            schema_registry_client,
            user_schema_str,
            to_dict=lambda obj, ctx: obj.to_dict() if hasattr(obj, 'to_dict') else obj
        )

        # Kafka producer
        self.producer = Producer({
            'bootstrap.servers': ','.join(bootstrap_servers)
        })

        self.topic_name = topic_name

    def send_event(self, event):
        """Send Avro-serialized event"""

        def delivery_callback(err, msg):
            if err:
                print(f"Delivery failed: {err}")
            else:
                print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

        try:
            self.producer.produce(
                topic=self.topic_name,
                value=self.avro_serializer(event, SerializationContext(self.topic_name, MessageField.VALUE)),
                on_delivery=delivery_callback
            )

            self.producer.flush()

        except Exception as e:
            print(f"Failed to send event: {e}")

# Kafka consumer with Avro deserialization
class AvroKafkaConsumer:
    def __init__(self, bootstrap_servers, schema_registry_url, topic_name, group_id):
        from confluent_kafka import Consumer
        from confluent_kafka.schema_registry import SchemaRegistryClient
        from confluent_kafka.schema_registry.avro import AvroDeserializer

        # Schema registry client
        schema_registry_client = SchemaRegistryClient({
            'url': schema_registry_url
        })

        # Avro deserializer
        self.avro_deserializer = AvroDeserializer(
            schema_registry_client,
            user_schema_str,
            from_dict=lambda obj, ctx: Event.from_dict(obj)
        )

        # Kafka consumer
        self.consumer = Consumer({
            'bootstrap.servers': ','.join(bootstrap_servers),
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })

        self.consumer.subscribe([topic_name])

    def consume_events(self):
        """Consume and deserialize events"""

        try:
            while True:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue

                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                # Deserialize Avro message
                event = self.avro_deserializer(
                    msg.value(),
                    SerializationContext(msg.topic(), MessageField.VALUE)
                )

                print(f"Received event: {event.event_type}")

        except KeyboardInterrupt:
            print("Consumer stopped")
        finally:
            self.consumer.close()
```

## Monitoring and Operations

### Metrics Collection

```python
from kafka import KafkaAdminClient
from kafka.metrics import MetricName, Metric
import time
import psutil

class KafkaMonitor:
    def __init__(self, bootstrap_servers):
        self.admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        self.bootstrap_servers = bootstrap_servers

    def get_cluster_info(self):
        """Get basic cluster information"""

        cluster_info = {
            'brokers': [],
            'topics': [],
            'consumer_groups': []
        }

        # Get broker information
        brokers = self.admin_client.describe_cluster()
        for broker in brokers['brokers']:
            cluster_info['brokers'].append({
                'id': broker['node_id'],
                'host': broker['host'],
                'port': broker['port']
            })

        # Get topic information
        topics = self.admin_client.list_topics()
        for topic in topics:
            topic_details = self.admin_client.describe_topics([topic])
            partitions = len(topic_details[0]['partitions'])

            cluster_info['topics'].append({
                'name': topic,
                'partitions': partitions
            })

        return cluster_info

    def get_topic_metrics(self, topic_name):
        """Get detailed metrics for a topic"""

        metrics = {}

        # Get topic description
        topic_info = self.admin_client.describe_topics([topic_name])[0]

        for partition_info in topic_info['partitions']:
            partition_id = partition_info['partition']
            leader = partition_info['leader']
            replicas = partition_info['replicas']
            isr = partition_info['isr']

            metrics[f'partition_{partition_id}'] = {
                'leader': leader,
                'replicas': len(replicas),
                'in_sync_replicas': len(isr),
                'under_replicated': len(replicas) > len(isr)
            }

        return metrics

    def monitor_consumer_lag(self, group_id):
        """Monitor consumer group lag"""

        from kafka import KafkaConsumer

        consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=False
        )

        # Get group offsets
        group_offsets = consumer.committed(consumer.assignment())

        # Get end offsets
        end_offsets = consumer.end_offsets(consumer.assignment())

        lag_info = {}
        total_lag = 0

        for topic_partition in consumer.assignment():
            committed_offset = group_offsets.get(topic_partition, 0)
            end_offset = end_offsets.get(topic_partition, 0)

            lag = end_offset - committed_offset
            total_lag += lag

            lag_info[str(topic_partition)] = {
                'committed': committed_offset,
                'end': end_offset,
                'lag': lag
            }

        consumer.close()

        return {
            'total_lag': total_lag,
            'partition_lags': lag_info
        }

class SystemMonitor:
    def __init__(self):
        self.metrics = {}

    def collect_system_metrics(self):
        """Collect system-level metrics"""

        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_connections': len(psutil.net_connections()),
            'timestamp': int(time.time() * 1000)
        }

    def collect_kafka_metrics(self, kafka_process_name='java'):
        """Collect Kafka-specific system metrics"""

        kafka_metrics = {}

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            if kafka_process_name in proc.info['name']:
                kafka_metrics[f"kafka_pid_{proc.info['pid']}"] = {
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                }

        return kafka_metrics

# Monitoring dashboard
def monitoring_dashboard(bootstrap_servers, group_id):
    """Simple monitoring dashboard"""

    monitor = KafkaMonitor(bootstrap_servers)
    system_monitor = SystemMonitor()

    while True:
        print("\n=== Kafka Monitoring Dashboard ===")

        # Cluster info
        cluster_info = monitor.get_cluster_info()
        print(f"Brokers: {len(cluster_info['brokers'])}")
        print(f"Topics: {len(cluster_info['topics'])}")

        # Consumer lag
        lag_info = monitor.monitor_consumer_lag(group_id)
        print(f"Total Consumer Lag: {lag_info['total_lag']}")

        # System metrics
        system_metrics = system_monitor.collect_system_metrics()
        print(f"CPU Usage: {system_metrics['cpu_percent']}%")
        print(f"Memory Usage: {system_metrics['memory_percent']}%")

        time.sleep(30)  # Update every 30 seconds
```

### Alerting and Health Checks

```python
class KafkaHealthChecker:
    def __init__(self, bootstrap_servers, thresholds=None):
        self.bootstrap_servers = bootstrap_servers
        self.thresholds = thresholds or {
            'max_lag': 10000,
            'min_brokers': 3,
            'max_cpu_percent': 80,
            'max_memory_percent': 85
        }

        self.monitor = KafkaMonitor(bootstrap_servers)
        self.system_monitor = SystemMonitor()

    def perform_health_check(self):
        """Perform comprehensive health check"""

        health_status = {
            'overall': 'healthy',
            'checks': {},
            'timestamp': int(time.time() * 1000)
        }

        # Check broker count
        cluster_info = self.monitor.get_cluster_info()
        broker_count = len(cluster_info['brokers'])

        health_status['checks']['brokers'] = {
            'status': 'healthy' if broker_count >= self.thresholds['min_brokers'] else 'unhealthy',
            'value': broker_count,
            'threshold': self.thresholds['min_brokers']
        }

        # Check consumer lag
        lag_info = self.monitor.monitor_consumer_lag('main-consumer-group')
        total_lag = lag_info['total_lag']

        health_status['checks']['consumer_lag'] = {
            'status': 'healthy' if total_lag <= self.thresholds['max_lag'] else 'unhealthy',
            'value': total_lag,
            'threshold': self.thresholds['max_lag']
        }

        # Check system resources
        system_metrics = self.system_monitor.collect_system_metrics()

        health_status['checks']['cpu_usage'] = {
            'status': 'healthy' if system_metrics['cpu_percent'] <= self.thresholds['max_cpu_percent'] else 'unhealthy',
            'value': system_metrics['cpu_percent'],
            'threshold': self.thresholds['max_cpu_percent']
        }

        health_status['checks']['memory_usage'] = {
            'status': 'healthy' if system_metrics['memory_percent'] <= self.thresholds['max_memory_percent'] else 'unhealthy',
            'value': system_metrics['memory_percent'],
            'threshold': self.thresholds['max_memory_percent']
        }

        # Determine overall health
        unhealthy_checks = [check for check in health_status['checks'].values() if check['status'] == 'unhealthy']
        if unhealthy_checks:
            health_status['overall'] = 'unhealthy'

        return health_status

class AlertManager:
    def __init__(self, alert_rules=None):
        self.alert_rules = alert_rules or []
        self.active_alerts = set()

    def add_alert_rule(self, name, condition_func, message, severity='warning'):
        """Add an alert rule"""

        self.alert_rules.append({
            'name': name,
            'condition': condition_func,
            'message': message,
            'severity': severity
        })

    def check_alerts(self, health_status):
        """Check for alerts based on health status"""

        new_alerts = []

        for rule in self.alert_rules:
            alert_key = rule['name']

            if rule['condition'](health_status):
                if alert_key not in self.active_alerts:
                    new_alerts.append({
                        'name': alert_key,
                        'message': rule['message'],
                        'severity': rule['severity'],
                        'timestamp': int(time.time() * 1000)
                    })
                    self.active_alerts.add(alert_key)
            else:
                # Alert condition cleared
                if alert_key in self.active_alerts:
                    self.active_alerts.remove(alert_key)

        return new_alerts

    def send_alerts(self, alerts):
        """Send alerts (email, Slack, etc.)"""

        for alert in alerts:
            print(f"[{alert['severity'].upper()}] {alert['name']}: {alert['message']}")

            # In production, integrate with alerting systems:
            # - Send email via SMTP
            # - Post to Slack webhook
            # - Send to PagerDuty
            # - Write to monitoring system

# Setup alerting
def setup_kafka_alerting():
    alert_manager = AlertManager()

    # Define alert rules
    alert_manager.add_alert_rule(
        'high_consumer_lag',
        lambda health: health['checks']['consumer_lag']['status'] == 'unhealthy',
        'Consumer lag is too high - processing may be delayed',
        'critical'
    )

    alert_manager.add_alert_rule(
        'broker_down',
        lambda health: health['checks']['brokers']['status'] == 'unhealthy',
        'Insufficient number of brokers available',
        'critical'
    )

    alert_manager.add_alert_rule(
        'high_cpu_usage',
        lambda health: health['checks']['cpu_usage']['status'] == 'unhealthy',
        'CPU usage is critically high',
        'warning'
    )

    return alert_manager

def monitoring_loop(health_checker, alert_manager):
    """Main monitoring loop"""

    while True:
        # Perform health check
        health_status = health_checker.perform_health_check()

        # Check for alerts
        alerts = alert_manager.check_alerts(health_status)

        # Send alerts
        if alerts:
            alert_manager.send_alerts(alerts)

        # Log health status
        print(f"Health Status: {health_status['overall']}")

        time.sleep(60)  # Check every minute
```

## Best Practices

### Performance Optimization

1. **Partitioning Strategy**: Choose appropriate partition keys for even distribution
2. **Batch Processing**: Use batching for high-throughput scenarios
3. **Compression**: Enable compression to reduce network overhead
4. **Message Size**: Keep messages reasonably sized (under 1MB)
5. **Consumer Groups**: Use appropriate consumer group configurations

### Reliability Patterns

1. **Idempotent Processing**: Design consumers to handle duplicate messages
2. **Dead Letter Queues**: Implement DLQs for unprocessable messages
3. **Circuit Breakers**: Implement circuit breakers for downstream failures
4. **Graceful Shutdown**: Handle shutdown signals properly
5. **Monitoring**: Implement comprehensive monitoring and alerting

### Security Considerations

1. **Authentication**: Use SASL/SSL for broker authentication
2. **Authorization**: Implement ACLs for topic access control
3. **Encryption**: Enable SSL/TLS for data in transit
4. **Audit Logging**: Enable audit logs for compliance
5. **Schema Validation**: Use Schema Registry for data validation

### Scalability Patterns

1. **Horizontal Scaling**: Add more brokers as needed
2. **Topic Partitioning**: Increase partitions for higher throughput
3. **Consumer Scaling**: Add more consumers to consumer groups
4. **Multi-Cluster**: Use MirrorMaker for multi-datacenter setups
5. **Tiered Storage**: Implement tiered storage for cost optimization

Apache Kafka provides a robust foundation for building scalable, reliable, and high-performance event streaming applications. Understanding its core concepts, proper configuration, and operational best practices is essential for successful implementation in production environments.