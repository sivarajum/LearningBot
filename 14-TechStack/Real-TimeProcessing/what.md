# Real-Time Processing: Comprehensive Guide

## Core Concepts

### Real-Time Processing Fundamentals

Real-time processing refers to the ability to process and analyze data streams as they arrive, providing immediate insights and responses. Unlike batch processing which handles data in chunks, real-time processing deals with continuous data flows.

**Key Characteristics:**
- **Low Latency**: Processing happens within milliseconds to seconds
- **Continuous Processing**: Data streams are processed as they arrive
- **Event-Driven**: Systems react to events as they occur
- **Scalability**: Handle varying data volumes and velocities
- **Fault Tolerance**: Maintain processing continuity despite failures

### Stream Processing vs Batch Processing

```python
# Batch Processing Example
def batch_process_data(data_files):
    """Process data in batches at scheduled intervals"""
    for file in data_files:
        # Load entire dataset
        data = load_data(file)

        # Process all data at once
        processed_data = process_data(data)

        # Store results
        save_results(processed_data)

# Stream Processing Example
def stream_process_data(data_stream):
    """Process data as it arrives in real-time"""
    for event in data_stream:
        # Process each event immediately
        processed_event = process_event(event)

        # Emit results in real-time
        emit_result(processed_event)
```

### Event Types and Processing Models

**Event Types:**
- **Simple Events**: Single data points (sensor readings, clicks)
- **Complex Events**: Aggregated or correlated events
- **Temporal Events**: Time-windowed events
- **Pattern Events**: Events matching specific patterns

**Processing Models:**
- **Record-at-a-Time**: Process each event individually
- **Micro-batching**: Process small batches of events
- **Windowed Processing**: Process events within time windows
- **Session Processing**: Process events within user sessions

## Apache Kafka

### Kafka Architecture

Apache Kafka is a distributed event streaming platform capable of handling trillions of events per day. It provides high-throughput, low-latency platform for handling real-time data feeds.

**Core Components:**
- **Producer**: Applications that publish data to Kafka topics
- **Consumer**: Applications that subscribe to topics and process data
- **Broker**: Kafka servers that store and serve data
- **Zookeeper**: Coordinates Kafka brokers and maintains cluster state
- **Topic**: Category or feed name to which records are published
- **Partition**: Topics are split into partitions for parallelism

### Kafka Producer Implementation

```python
from kafka import KafkaProducer
import json
from datetime import datetime

class RealTimeProducer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            retries=3,
            max_in_flight_requests_per_connection=1
        )

    def send_user_event(self, user_id, event_type, event_data):
        """Send user interaction event"""
        event = {
            'user_id': user_id,
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': event_data
        }

        # Send with user_id as key for partitioning
        future = self.producer.send('user_events', key=user_id, value=event)

        # Add callback for delivery confirmation
        future.add_callback(self.on_send_success)
        future.add_errback(self.on_send_error)

        return future

    def send_sensor_data(self, sensor_id, readings):
        """Send IoT sensor readings"""
        sensor_event = {
            'sensor_id': sensor_id,
            'timestamp': datetime.utcnow().isoformat(),
            'readings': readings
        }

        self.producer.send('sensor_data', key=sensor_id, value=sensor_event)

    def on_send_success(self, record_metadata):
        print(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")

    def on_send_error(self, excp):
        print(f"Failed to send message: {excp}")

    def close(self):
        self.producer.close()
```

### Kafka Consumer Implementation

```python
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
import json

class RealTimeConsumer:
    def __init__(self, topic, group_id, bootstrap_servers=['localhost:9092']):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset='earliest',  # Start from beginning if no offset
            enable_auto_commit=False,  # Manual commit for exactly-once processing
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None,
            consumer_timeout_ms=1000  # Timeout for polling
        )

    def consume_events(self):
        """Consume and process events"""
        try:
            while True:
                # Poll for messages
                message_batch = self.consumer.poll(timeout_ms=1000)

                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            # Process message
                            self.process_message(message)

                            # Manual commit after successful processing
                            self.consumer.commit({
                                topic_partition: message.offset + 1
                            })

                        except Exception as e:
                            print(f"Error processing message: {e}")
                            # Handle error (retry, dead letter queue, etc.)

        except KeyboardInterrupt:
            print("Stopping consumer...")
        finally:
            self.consumer.close()

    def process_message(self, message):
        """Process individual message"""
        print(f"Received: topic={message.topic}, partition={message.partition}, "
              f"offset={message.offset}, key={message.key}")

        # Process based on topic
        if message.topic == 'user_events':
            self.process_user_event(message.value)
        elif message.topic == 'sensor_data':
            self.process_sensor_data(message.value)

    def process_user_event(self, event):
        """Process user interaction events"""
        user_id = event['user_id']
        event_type = event['event_type']

        if event_type == 'page_view':
            self.update_user_analytics(user_id, event['data'])
        elif event_type == 'purchase':
            self.process_purchase(user_id, event['data'])

    def process_sensor_data(self, sensor_data):
        """Process IoT sensor readings"""
        sensor_id = sensor_data['sensor_id']
        readings = sensor_data['readings']

        # Check for anomalies
        if self.detect_anomaly(readings):
            self.alert_anomaly(sensor_id, readings)

        # Update sensor analytics
        self.update_sensor_stats(sensor_id, readings)

    def detect_anomaly(self, readings):
        """Simple anomaly detection"""
        # Implement anomaly detection logic
        return False

    def update_user_analytics(self, user_id, data):
        """Update user analytics in real-time"""
        # Update real-time dashboards, recommendations, etc.
        pass

    def process_purchase(self, user_id, data):
        """Process purchase events"""
        # Update inventory, send notifications, etc.
        pass

    def alert_anomaly(self, sensor_id, readings):
        """Send anomaly alerts"""
        # Send alerts to monitoring systems
        pass

    def update_sensor_stats(self, sensor_id, readings):
        """Update sensor statistics"""
        # Update real-time sensor dashboards
        pass
```

### Kafka Streams for Stream Processing

```python
from kafka import KafkaStreams
from kafka.streams import StreamsBuilder
from kafka.streams.kstream import KStream
import json

class RealTimeStreamProcessor:
    def __init__(self):
        self.builder = StreamsBuilder()

        # Define input streams
        user_events = self.builder.stream('user_events')
        sensor_data = self.builder.stream('sensor_data')

        # Process user events
        self.process_user_events(user_events)

        # Process sensor data
        self.process_sensor_data(sensor_data)

    def process_user_events(self, user_events_stream):
        """Process user events stream"""

        # Filter purchase events
        purchases = user_events_stream.filter(
            lambda k, v: v['event_type'] == 'purchase'
        )

        # Group by user and count purchases in 1-hour windows
        purchase_counts = purchases.group_by_key().windowed_by(
            TimeWindows.of(3600000)  # 1 hour
        ).count()

        # Send to output topic
        purchase_counts.to_stream().to('user_purchase_counts')

        # Calculate user spending in sliding windows
        spending = purchases.map_values(
            lambda v: v['data']['amount']
        ).group_by_key().windowed_by(
            TimeWindows.of(1800000).advance_by(300000)  # 30-min windows, 5-min advance
        ).sum()

        spending.to_stream().to('user_spending_trends')

    def process_sensor_data(self, sensor_stream):
        """Process sensor data stream"""

        # Filter temperature readings
        temperature_readings = sensor_stream.filter(
            lambda k, v: 'temperature' in v['readings']
        )

        # Calculate average temperature per sensor per minute
        avg_temp = temperature_readings.map_values(
            lambda v: v['readings']['temperature']
        ).group_by_key().windowed_by(
            TimeWindows.of(60000)  # 1 minute
        ).aggregate(
            lambda: {'sum': 0, 'count': 0},
            lambda k, v, agg: {
                'sum': agg['sum'] + v,
                'count': agg['count'] + 1
            },
            lambda k, agg: agg['sum'] / agg['count'] if agg['count'] > 0 else 0
        )

        avg_temp.to_stream().to('sensor_temperature_avg')

        # Detect temperature anomalies
        anomalies = temperature_readings.filter(
            lambda k, v: self.is_temperature_anomaly(v['readings']['temperature'])
        )

        anomalies.to('temperature_anomalies')

    def is_temperature_anomaly(self, temperature):
        """Check if temperature reading is anomalous"""
        # Implement anomaly detection logic
        return temperature > 100 or temperature < -50

    def start_processing(self):
        """Start the stream processing"""
        streams = KafkaStreams(self.builder, self.get_streams_config())
        streams.start()

        # Add shutdown hook
        import atexit
        atexit.register(streams.close)

    def get_streams_config(self):
        """Get Kafka Streams configuration"""
        return {
            'application.id': 'real-time-processor',
            'bootstrap.servers': 'localhost:9092',
            'default.key.serde': 'org.apache.kafka.common.serialization.Serdes$StringSerde',
            'default.value.serde': 'org.apache.kafka.common.serialization.Serdes$StringSerde',
            'commit.interval.ms': 1000,
            'auto.offset.reset': 'earliest'
        }
```

## Apache Flink

### Flink Architecture and Concepts

Apache Flink is a framework and distributed processing engine for stateful computations over unbounded and bounded data streams. It provides low-latency, high-throughput data processing.

**Key Concepts:**
- **DataStream API**: For processing continuous data streams
- **DataSet API**: For batch processing on bounded data
- **Table API & SQL**: Declarative APIs for data processing
- **State Management**: Fault-tolerant state handling
- **Time Characteristics**: Processing time, event time, ingestion time
- **Windows**: Time-based and count-based windowing

### Flink DataStream Processing

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import MapFunction, FilterFunction
from pyflink.datastream.window import TumblingProcessingTimeWindows, SlidingEventTimeWindows
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
import json

class RealTimeFlinkProcessor:
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()

        # Configure checkpointing for fault tolerance
        self.env.enable_checkpointing(10000)  # 10 seconds
        self.env.get_checkpoint_config().set_max_concurrent_checkpoints(1)

        # Set parallelism
        self.env.set_parallelism(4)

    def create_kafka_consumer(self, topic, group_id):
        """Create Kafka consumer for Flink"""
        properties = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }

        consumer = FlinkKafkaConsumer(
            topics=[topic],
            deserialization_schema=SimpleStringSchema(),
            properties=properties
        )

        return consumer

    def create_kafka_producer(self, topic):
        """Create Kafka producer for Flink"""
        properties = {
            'bootstrap.servers': 'localhost:9092'
        }

        producer = FlinkKafkaProducer(
            topic=topic,
            serialization_schema=SimpleStringSchema(),
            producer_config=properties
        )

        return producer

    def process_user_events(self):
        """Process user events with Flink"""

        # Create consumer
        consumer = self.create_kafka_consumer('user_events', 'flink_processor')

        # Parse JSON events
        parsed_events = self.env.add_source(consumer).map(
            lambda event: json.loads(event),
            output_type=Types.MAP(Types.STRING(), Types.PICKLED_BYTE_ARRAY())
        )

        # Filter purchase events
        purchases = parsed_events.filter(
            lambda event: event['event_type'] == 'purchase'
        )

        # Key by user_id for stateful processing
        keyed_purchases = purchases.key_by(
            lambda event: event['user_id']
        )

        # Calculate user spending in tumbling windows
        user_spending = keyed_purchases.window(
            TumblingProcessingTimeWindows.of(Time.minutes(5))
        ).reduce(
            lambda acc, event: {
                'user_id': acc['user_id'],
                'total_spent': acc.get('total_spent', 0) + event['data']['amount'],
                'purchase_count': acc.get('purchase_count', 0) + 1,
                'window_start': acc.get('window_start', event['timestamp'])
            }
        )

        # Create producer and sink results
        producer = self.create_kafka_producer('user_spending_aggregated')
        user_spending.map(lambda x: json.dumps(x)).add_sink(producer)

        return user_spending

    def process_sensor_data(self):
        """Process sensor data with event time windows"""

        consumer = self.create_kafka_consumer('sensor_data', 'sensor_processor')

        # Parse sensor events
        sensor_events = self.env.add_source(consumer).map(
            lambda event: json.loads(event)
        )

        # Assign event time timestamps
        timed_events = sensor_events.assign_timestamps_and_watermarks(
            WatermarkStrategy.for_bounded_out_of_orderness(
                Duration.of_seconds(10)
            ).with_timestamp_assigner(
                lambda event, timestamp: event['timestamp']
            )
        )

        # Key by sensor_id
        keyed_sensors = timed_events.key_by(
            lambda event: event['sensor_id']
        )

        # Calculate average temperature in sliding windows
        temp_averages = keyed_sensors.window(
            SlidingEventTimeWindows.of(
                Time.minutes(10),  # Window size
                Time.minutes(1)    # Slide interval
            )
        ).aggregate(
            TemperatureAverageAggregate(),
            output_type=Types.TUPLE([Types.STRING(), Types.DOUBLE(), Types.LONG()])
        )

        # Sink to output topic
        producer = self.create_kafka_producer('sensor_temp_averages')
        temp_averages.map(lambda x: f"{x[0]},{x[1]},{x[2]}").add_sink(producer)

        return temp_averages

    def process_clickstream_data(self):
        """Process clickstream data with session windows"""

        consumer = self.create_kafka_consumer('clickstream', 'click_processor')

        click_events = self.env.add_source(consumer).map(json.loads)

        # Assign event time
        timed_clicks = click_events.assign_timestamps_and_watermarks(
            WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5))
        )

        # Key by user_id
        keyed_clicks = timed_clicks.key_by(lambda event: event['user_id'])

        # Session windows with 30-minute gap
        session_clicks = keyed_clicks.window(
            ProcessingTimeSessionWindows.with_gap(Time.minutes(30))
        ).aggregate(
            SessionClickAggregate(),
            output_type=Types.TUPLE([Types.STRING(), Types.INT(), Types.LONG(), Types.LONG()])
        )

        # Output session analytics
        producer = self.create_kafka_producer('user_sessions')
        session_clicks.map(lambda x: f"{x[0]},{x[1]},{x[2]},{x[3]}").add_sink(producer)

        return session_clicks

    def run_processing(self):
        """Execute all processing pipelines"""
        self.process_user_events()
        self.process_sensor_data()
        self.process_clickstream_data()

        # Execute the job
        self.env.execute("Real-Time Data Processing")

class TemperatureAverageAggregate(AggregateFunction):
    def create_accumulator(self):
        return (0.0, 0)  # (sum, count)

    def add(self, value, accumulator):
        temp = value['readings']['temperature']
        return (accumulator[0] + temp, accumulator[1] + 1)

    def get_result(self, accumulator):
        return accumulator[0] / accumulator[1] if accumulator[1] > 0 else 0.0

    def merge(self, a, b):
        return (a[0] + b[0], a[1] + b[1])

class SessionClickAggregate(AggregateFunction):
    def create_accumulator(self):
        return (0, 0, 0)  # (click_count, session_start, session_end)

    def add(self, value, accumulator):
        click_count = accumulator[0] + 1
        timestamp = value['timestamp']

        session_start = min(accumulator[1], timestamp) if accumulator[1] > 0 else timestamp
        session_end = max(accumulator[2], timestamp)

        return (click_count, session_start, session_end)

    def get_result(self, accumulator):
        return accumulator

    def merge(self, a, b):
        total_clicks = a[0] + b[0]
        start_time = min(a[1], b[1])
        end_time = max(a[2], b[2])
        return (total_clicks, start_time, end_time)
```

## Real-Time Analytics

### Real-Time Dashboard Implementation

```python
from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta

class RealTimeDashboard:
    def __init__(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Data storage for real-time metrics
        self.metrics = {
            'active_users': 0,
            'total_events': 0,
            'events_per_second': 0,
            'top_pages': defaultdict(int),
            'user_sessions': defaultdict(dict),
            'error_rate': 0.0
        }

        # Time-series data (last 24 hours)
        self.time_series = {
            'user_count': deque(maxlen=1440),  # 1 reading per minute
            'event_count': deque(maxlen=1440),
            'error_count': deque(maxlen=1440)
        }

        # Setup routes
        self.setup_routes()

        # Setup WebSocket events
        self.setup_socket_events()

    def setup_routes(self):
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')

        @self.app.route('/api/metrics')
        def get_metrics():
            return jsonify(self.metrics)

        @self.app.route('/api/time-series')
        def get_time_series():
            return jsonify({
                'timestamps': [i for i in range(len(self.time_series['user_count']))],
                'user_count': list(self.time_series['user_count']),
                'event_count': list(self.time_series['event_count']),
                'error_count': list(self.time_series['error_count'])
            })

    def setup_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')
            # Send current metrics on connect
            emit('metrics_update', self.metrics)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')

    def update_metrics(self, event_data):
        """Update metrics based on incoming events"""

        # Update basic counters
        self.metrics['total_events'] += 1

        # Update user activity
        user_id = event_data.get('user_id')
        if user_id:
            if event_data['event_type'] == 'page_view':
                self.metrics['active_users'] = len(self.metrics['user_sessions'])

                # Update page popularity
                page = event_data['data'].get('page', 'unknown')
                self.metrics['top_pages'][page] += 1

            elif event_data['event_type'] == 'session_start':
                self.metrics['user_sessions'][user_id] = {
                    'start_time': datetime.now(),
                    'page_views': 0,
                    'events': []
                }

            elif event_data['event_type'] == 'session_end':
                if user_id in self.metrics['user_sessions']:
                    session = self.metrics['user_sessions'][user_id]
                    session['end_time'] = datetime.now()
                    session['duration'] = (session['end_time'] - session['start_time']).seconds

        # Calculate events per second (rolling average)
        self.calculate_eps()

        # Update error rate
        if event_data.get('event_type') == 'error':
            self.metrics['error_rate'] = self.calculate_error_rate()

        # Broadcast updates to connected clients
        self.socketio.emit('metrics_update', self.metrics)

    def calculate_eps(self):
        """Calculate events per second"""
        # Simple implementation - in production, use sliding window
        current_time = time.time()
        # This would need more sophisticated tracking for accurate EPS
        pass

    def calculate_error_rate(self):
        """Calculate error rate from recent events"""
        # Implementation would track errors over time window
        return 0.05  # 5% error rate

    def update_time_series(self):
        """Update time-series data every minute"""
        while True:
            current_time = datetime.now()

            # Add current metrics to time series
            self.time_series['user_count'].append(self.metrics['active_users'])
            self.time_series['event_count'].append(self.metrics['total_events'])
            self.time_series['error_count'].append(int(self.metrics['error_rate'] * 100))

            # Sleep for 1 minute
            time.sleep(60)

    def start_background_tasks(self):
        """Start background tasks"""
        # Start time-series update thread
        time_series_thread = threading.Thread(target=self.update_time_series)
        time_series_thread.daemon = True
        time_series_thread.start()

    def run(self, host='0.0.0.0', port=5000):
        """Run the dashboard"""
        self.start_background_tasks()
        self.socketio.run(self.app, host=host, port=port, debug=False)

# Usage example
if __name__ == '__main__':
    dashboard = RealTimeDashboard()

    # Simulate receiving events (in real app, this would come from Kafka consumer)
    def simulate_events():
        import random

        event_types = ['page_view', 'purchase', 'error', 'session_start', 'session_end']
        pages = ['/home', '/products', '/cart', '/checkout']

        while True:
            event = {
                'user_id': f'user_{random.randint(1, 1000)}',
                'event_type': random.choice(event_types),
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'page': random.choice(pages) if random.choice(event_types) == 'page_view' else {}
                }
            }

            dashboard.update_metrics(event)
            time.sleep(random.uniform(0.1, 2.0))  # Random delay between events

    # Start event simulation in background
    event_thread = threading.Thread(target=simulate_events)
    event_thread.daemon = True
    event_thread.start()

    # Run dashboard
    dashboard.run()
```

### Real-Time Recommendation Engine

```python
from collections import defaultdict
import heapq
from datetime import datetime, timedelta
import json

class RealTimeRecommendationEngine:
    def __init__(self):
        # User-item interaction matrix
        self.user_item_matrix = defaultdict(lambda: defaultdict(float))

        # Item-item similarity matrix
        self.item_similarity = defaultdict(lambda: defaultdict(float))

        # User preferences (categories/genres)
        self.user_preferences = defaultdict(lambda: defaultdict(float))

        # Recent user actions (for recency weighting)
        self.recent_actions = defaultdict(list)  # user_id -> [(timestamp, item_id, action_type)]

        # Popular items (fallback recommendations)
        self.popular_items = defaultdict(float)

        # Item metadata
        self.item_metadata = {}  # item_id -> {'category': '', 'tags': []}

    def process_user_action(self, user_id, item_id, action_type, timestamp=None):
        """Process user action in real-time"""

        if timestamp is None:
            timestamp = datetime.now()

        # Update user-item matrix
        weight = self.get_action_weight(action_type)
        self.user_item_matrix[user_id][item_id] += weight

        # Update recent actions (keep last 100 actions per user)
        self.recent_actions[user_id].append((timestamp, item_id, action_type))
        if len(self.recent_actions[user_id]) > 100:
            self.recent_actions[user_id].pop(0)

        # Update user preferences based on item metadata
        if item_id in self.item_metadata:
            category = self.item_metadata[item_id]['category']
            self.user_preferences[user_id][category] += weight

        # Update popular items
        self.popular_items[item_id] += weight

        # Update item similarity (simplified collaborative filtering)
        self.update_item_similarity(user_id, item_id, weight)

    def get_action_weight(self, action_type):
        """Get weight for different action types"""
        weights = {
            'view': 1.0,
            'click': 2.0,
            'add_to_cart': 3.0,
            'purchase': 5.0,
            'share': 4.0,
            'favorite': 4.0
        }
        return weights.get(action_type, 1.0)

    def update_item_similarity(self, user_id, item_id, weight):
        """Update item-item similarity based on user actions"""
        # Simplified co-occurrence based similarity
        user_items = list(self.user_item_matrix[user_id].keys())

        for other_item in user_items:
            if other_item != item_id:
                self.item_similarity[item_id][other_item] += weight
                self.item_similarity[other_item][item_id] += weight

    def get_recommendations(self, user_id, n_recommendations=10):
        """Get real-time recommendations for user"""

        # Get user's recent items (last 24 hours)
        recent_items = self.get_recent_items(user_id, hours=24)

        # Collaborative filtering recommendations
        cf_scores = self.collaborative_filtering(user_id, recent_items)

        # Content-based recommendations
        cb_scores = self.content_based_filtering(user_id)

        # Popularity-based recommendations (fallback)
        pop_scores = self.popularity_based_filtering()

        # Combine recommendations
        combined_scores = self.combine_recommendations(cf_scores, cb_scores, pop_scores)

        # Remove already interacted items
        interacted_items = set(self.user_item_matrix[user_id].keys())
        filtered_recommendations = {
            item: score for item, score in combined_scores.items()
            if item not in interacted_items
        }

        # Return top N recommendations
        return heapq.nlargest(
            n_recommendations,
            filtered_recommendations.items(),
            key=lambda x: x[1]
        )

    def get_recent_items(self, user_id, hours=24):
        """Get items user interacted with recently"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_items = []

        for timestamp, item_id, action_type in self.recent_actions[user_id]:
            if timestamp > cutoff_time:
                recent_items.append(item_id)

        return list(set(recent_items))  # Remove duplicates

    def collaborative_filtering(self, user_id, recent_items):
        """Collaborative filtering based recommendations"""
        scores = defaultdict(float)

        for item in recent_items:
            similar_items = self.item_similarity.get(item, {})
            for similar_item, similarity in similar_items.items():
                scores[similar_item] += similarity

        return scores

    def content_based_filtering(self, user_id):
        """Content-based filtering recommendations"""
        scores = defaultdict(float)

        user_prefs = self.user_preferences[user_id]
        for item_id, metadata in self.item_metadata.items():
            category = metadata['category']
            if category in user_prefs:
                scores[item_id] += user_prefs[category]

        return scores

    def popularity_based_filtering(self):
        """Popularity-based recommendations"""
        # Return top popular items
        return dict(heapq.nlargest(50, self.popular_items.items(), key=lambda x: x[1]))

    def combine_recommendations(self, cf_scores, cb_scores, pop_scores, weights=None):
        """Combine different recommendation approaches"""
        if weights is None:
            weights = {'cf': 0.5, 'cb': 0.3, 'pop': 0.2}

        combined = defaultdict(float)

        # Normalize scores to 0-1 range
        def normalize_scores(scores):
            if not scores:
                return scores
            max_score = max(scores.values())
            if max_score == 0:
                return scores
            return {k: v/max_score for k, v in scores.items()}

        cf_norm = normalize_scores(cf_scores)
        cb_norm = normalize_scores(cb_scores)
        pop_norm = normalize_scores(pop_scores)

        # Combine all items
        all_items = set(cf_norm.keys()) | set(cb_norm.keys()) | set(pop_norm.keys())

        for item in all_items:
            combined[item] = (
                weights['cf'] * cf_norm.get(item, 0) +
                weights['cb'] * cb_norm.get(item, 0) +
                weights['pop'] * pop_norm.get(item, 0)
            )

        return combined

    def add_item_metadata(self, item_id, category, tags=None):
        """Add metadata for an item"""
        self.item_metadata[item_id] = {
            'category': category,
            'tags': tags or []
        }

# Usage example
if __name__ == '__main__':
    engine = RealTimeRecommendationEngine()

    # Add some item metadata
    engine.add_item_metadata('book_1', 'fiction', ['mystery', 'thriller'])
    engine.add_item_metadata('book_2', 'fiction', ['romance', 'drama'])
    engine.add_item_metadata('book_3', 'non-fiction', ['technology', 'programming'])
    engine.add_item_metadata('book_4', 'fiction', ['sci-fi', 'adventure'])

    # Simulate user actions
    engine.process_user_action('user_1', 'book_1', 'purchase')
    engine.process_user_action('user_1', 'book_3', 'view')
    engine.process_user_action('user_1', 'book_4', 'click')

    # Get recommendations
    recommendations = engine.get_recommendations('user_1', 5)
    print("Recommendations for user_1:", recommendations)
```

## Real-Time Monitoring and Alerting

### Real-Time Alerting System

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Callable, Any
from datetime import datetime, timedelta
from collections import deque
import threading
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

@dataclass
class AlertRule:
    name: str
    condition: Callable[[Dict], bool]
    severity: str  # 'low', 'medium', 'high', 'critical'
    cooldown_minutes: int = 5
    description: str = ""

@dataclass
class Alert:
    rule_name: str
    severity: str
    message: str
    timestamp: datetime
    data: Dict[str, Any]

class AlertChannel(ABC):
    @abstractmethod
    def send_alert(self, alert: Alert):
        pass

class EmailAlertChannel(AlertChannel):
    def __init__(self, smtp_server, smtp_port, username, password, recipients):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients

    def send_alert(self, alert: Alert):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = f"[{alert.severity.upper()}] {alert.rule_name}"

        body = f"""
        Alert: {alert.rule_name}
        Severity: {alert.severity}
        Time: {alert.timestamp}
        Message: {alert.message}

        Data: {json.dumps(alert.data, indent=2)}
        """
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, self.recipients, text)
            server.quit()
            print(f"Email alert sent for {alert.rule_name}")
        except Exception as e:
            print(f"Failed to send email alert: {e}")

class SlackAlertChannel(AlertChannel):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_alert(self, alert: Alert):
        import requests

        color_map = {
            'low': 'good',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'danger'
        }

        payload = {
            "attachments": [
                {
                    "color": color_map.get(alert.severity, 'danger'),
                    "title": f"Alert: {alert.rule_name}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.upper(),
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                            "short": True
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                print(f"Slack alert sent for {alert.rule_name}")
            else:
                print(f"Failed to send Slack alert: {response.status_code}")
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")

class RealTimeMonitoringSystem:
    def __init__(self):
        self.metrics = {}
        self.alert_rules: List[AlertRule] = []
        self.alert_channels: List[AlertChannel] = []
        self.active_alerts = set()  # Track active alerts to prevent spam
        self.alert_history = deque(maxlen=1000)  # Keep last 1000 alerts

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def add_metric(self, name: str, initial_value=0):
        """Add a metric to monitor"""
        self.metrics[name] = {
            'value': initial_value,
            'history': deque(maxlen=100),  # Keep last 100 values
            'last_update': datetime.now()
        }

    def update_metric(self, name: str, value: Any):
        """Update metric value"""
        if name in self.metrics:
            self.metrics[name]['value'] = value
            self.metrics[name]['history'].append((datetime.now(), value))
            self.metrics[name]['last_update'] = datetime.now()

    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.alert_rules.append(rule)

    def add_alert_channel(self, channel: AlertChannel):
        """Add an alert channel"""
        self.alert_channels.append(channel)

    def monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                self.check_alerts()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in monitoring loop: {e}")

    def check_alerts(self):
        """Check all alert rules"""
        current_data = {name: metric['value'] for name, metric in self.metrics.items()}

        for rule in self.alert_rules:
            try:
                if rule.condition(current_data):
                    alert_key = f"{rule.name}_{datetime.now().strftime('%Y%m%d_%H%M')}"

                    # Check if alert is in cooldown
                    if alert_key not in self.active_alerts:
                        self.trigger_alert(rule, current_data)
                        self.active_alerts.add(alert_key)

                        # Remove from active alerts after cooldown
                        threading.Timer(
                            rule.cooldown_minutes * 60,
                            lambda: self.active_alerts.discard(alert_key)
                        ).start()

            except Exception as e:
                print(f"Error checking rule {rule.name}: {e}")

    def trigger_alert(self, rule: AlertRule, data: Dict):
        """Trigger an alert"""
        alert = Alert(
            rule_name=rule.name,
            severity=rule.severity,
            message=rule.description,
            timestamp=datetime.now(),
            data=data
        )

        # Add to history
        self.alert_history.append(alert)

        # Send to all channels
        for channel in self.alert_channels:
            try:
                channel.send_alert(alert)
            except Exception as e:
                print(f"Failed to send alert via {type(channel).__name__}: {e}")

    def get_metrics_summary(self):
        """Get summary of current metrics"""
        return {
            name: {
                'value': metric['value'],
                'last_update': metric['last_update'].isoformat(),
                'history_length': len(metric['history'])
            }
            for name, metric in self.metrics.items()
        }

    def get_recent_alerts(self, limit=10):
        """Get recent alerts"""
        return list(self.alert_history)[-limit:]

# Usage example
def setup_monitoring():
    monitoring = RealTimeMonitoringSystem()

    # Add metrics
    monitoring.add_metric('cpu_usage', 0.0)
    monitoring.add_metric('memory_usage', 0.0)
    monitoring.add_metric('active_users', 0)
    monitoring.add_metric('error_rate', 0.0)
    monitoring.add_metric('response_time', 0.0)

    # Add alert rules
    monitoring.add_alert_rule(AlertRule(
        name="High CPU Usage",
        condition=lambda data: data.get('cpu_usage', 0) > 90,
        severity="high",
        description="CPU usage is above 90%"
    ))

    monitoring.add_alert_rule(AlertRule(
        name="High Memory Usage",
        condition=lambda data: data.get('memory_usage', 0) > 95,
        severity="critical",
        description="Memory usage is above 95%"
    ))

    monitoring.add_alert_rule(AlertRule(
        name="High Error Rate",
        condition=lambda data: data.get('error_rate', 0) > 0.05,
        severity="medium",
        description="Error rate is above 5%"
    ))

    monitoring.add_alert_rule(AlertRule(
        name="Slow Response Time",
        condition=lambda data: data.get('response_time', 0) > 5000,  # 5 seconds
        severity="medium",
        description="Average response time is above 5 seconds"
    ))

    # Add alert channels (example configurations)
    # email_channel = EmailAlertChannel(
    #     smtp_server="smtp.gmail.com",
    #     smtp_port=587,
    #     username="alerts@company.com",
    #     password="password",
    #     recipients=["admin@company.com", "devops@company.com"]
    # )
    # monitoring.add_alert_channel(email_channel)

    # slack_channel = SlackAlertChannel("https://hooks.slack.com/services/.../...")
    # monitoring.add_alert_channel(slack_channel)

    return monitoring

# Simulate metric updates
def simulate_metrics(monitoring):
    import random
    import psutil

    while True:
        # Update with real system metrics
        monitoring.update_metric('cpu_usage', psutil.cpu_percent())
        monitoring.update_metric('memory_usage', psutil.virtual_memory().percent)
        monitoring.update_metric('active_users', random.randint(100, 1000))
        monitoring.update_metric('error_rate', random.uniform(0, 0.1))
        monitoring.update_metric('response_time', random.uniform(100, 10000))

        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    monitoring = setup_monitoring()

    # Start metric simulation
    sim_thread = threading.Thread(target=simulate_metrics, args=(monitoring,))
    sim_thread.daemon = True
    sim_thread.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Monitoring system stopped")
```

## Best Practices and Patterns

### Real-Time Processing Best Practices

1. **Event-Driven Architecture**
   - Design systems around events rather than requests
   - Use asynchronous processing wherever possible
   - Implement event sourcing for audit trails

2. **Data Partitioning and Scaling**
   - Partition data by key for parallel processing
   - Use consistent hashing for load distribution
   - Implement auto-scaling based on throughput

3. **Fault Tolerance and Reliability**
   - Implement exactly-once processing semantics
   - Use checkpointing for state recovery
   - Design for graceful degradation

4. **Performance Optimization**
   - Minimize serialization overhead
   - Use efficient data structures
   - Implement backpressure mechanisms

5. **Monitoring and Observability**
   - Track latency, throughput, and error rates
   - Implement distributed tracing
   - Set up comprehensive alerting

### Common Real-Time Processing Patterns

**Event Sourcing Pattern:**
```python
class EventStore:
    def __init__(self):
        self.events = defaultdict(list)  # entity_id -> [events]
        self.snapshots = {}  # entity_id -> snapshot

    def append_event(self, entity_id, event):
        """Append event to entity's event stream"""
        self.events[entity_id].append(event)

        # Create snapshot periodically
        if len(self.events[entity_id]) % 100 == 0:
            self.create_snapshot(entity_id)

    def get_events(self, entity_id, from_version=0):
        """Get events for entity from specific version"""
        return self.events[entity_id][from_version:]

    def create_snapshot(self, entity_id):
        """Create snapshot of current entity state"""
        # Rebuild state from events
        state = {}
        for event in self.events[entity_id]:
            self.apply_event(state, event)

        self.snapshots[entity_id] = {
            'state': state,
            'version': len(self.events[entity_id])
        }

    def get_current_state(self, entity_id):
        """Get current state of entity"""
        if entity_id in self.snapshots:
            snapshot = self.snapshots[entity_id]
            state = snapshot['state'].copy()

            # Apply events after snapshot
            for event in self.events[entity_id][snapshot['version']:]:
                self.apply_event(state, event)

            return state
        else:
            # Build state from all events
            state = {}
            for event in self.events[entity_id]:
                self.apply_event(state, event)
            return state

    def apply_event(self, state, event):
        """Apply event to state"""
        event_type = event['type']

        if event_type == 'user_created':
            state.update(event['data'])
        elif event_type == 'user_updated':
            state.update(event['data'])
        elif event_type == 'user_deleted':
            state['deleted'] = True
```

**CQRS Pattern (Command Query Responsibility Segregation):**
```python
class CommandHandler:
    def __init__(self, event_store, read_model):
        self.event_store = event_store
        self.read_model = read_model

    def handle_create_user(self, command):
        """Handle create user command"""
        user_id = command['user_id']

        # Validate command
        if self.event_store.get_current_state(user_id):
            raise ValueError(f"User {user_id} already exists")

        # Create event
        event = {
            'type': 'user_created',
            'user_id': user_id,
            'data': command['data'],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store event
        self.event_store.append_event(user_id, event)

        # Update read model
        self.read_model.update_user(event)

    def handle_update_user(self, command):
        """Handle update user command"""
        user_id = command['user_id']

        # Validate command
        current_state = self.event_store.get_current_state(user_id)
        if not current_state or current_state.get('deleted'):
            raise ValueError(f"User {user_id} does not exist")

        # Create event
        event = {
            'type': 'user_updated',
            'user_id': user_id,
            'data': command['data'],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store event
        self.event_store.append_event(user_id, event)

        # Update read model
        self.read_model.update_user(event)

class ReadModel:
    def __init__(self):
        self.users = {}  # user_id -> user_data

    def update_user(self, event):
        """Update read model based on event"""
        user_id = event['user_id']

        if event['type'] == 'user_created':
            self.users[user_id] = event['data']
        elif event['type'] == 'user_updated':
            if user_id in self.users:
                self.users[user_id].update(event['data'])
        elif event['type'] == 'user_deleted':
            self.users[user_id]['deleted'] = True

    def get_user(self, user_id):
        """Get user from read model"""
        return self.users.get(user_id)

    def search_users(self, criteria):
        """Search users in read model"""
        # Implement search logic
        return [user for user in self.users.values() if self.matches_criteria(user, criteria)]

    def matches_criteria(self, user, criteria):
        """Check if user matches search criteria"""
        # Implement matching logic
        return True
```

This comprehensive guide covers the fundamentals of real-time processing, implementation with major frameworks like Apache Kafka and Flink, real-time analytics, monitoring, and best practices. The code examples demonstrate practical implementations for production systems.
