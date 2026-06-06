# Dataflow: Unified Stream and Batch Data Processing

## Overview

Google Cloud Dataflow is a fully managed service for executing Apache Beam pipelines on Google Cloud. It provides a unified programming model for both batch and streaming data processing, automatically handling infrastructure provisioning, scaling, and optimization.

## Core Architecture

### Apache Beam Integration

Dataflow is built on Apache Beam, providing a portable programming model:

```java
// Pipeline definition
Pipeline pipeline = Pipeline.create(options);

// Read from Pub/Sub (streaming)
PCollection<String> messages = pipeline
    .apply("Read from Pub/Sub", PubsubIO.readStrings()
        .fromTopic(options.getInputTopic()));

// Transform data
PCollection<KV<String, Integer>> wordCounts = messages
    .apply("Extract words", ParDo.of(new ExtractWordsFn()))
    .apply("Count words", Count.perElement());

// Write to BigQuery
wordCounts.apply("Write to BigQuery",
    BigQueryIO.<KV<String, Integer>>write()
        .to(options.getOutputTable())
        .withFormatFunction(KV_FORMAT_FUNCTION)
        .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_TRUNCATE)
        .withCreateDisposition(BigQueryIO.Write.CreateDisposition.CREATE_IF_NEEDED));

pipeline.run();
```

### Execution Model

Dataflow uses a sophisticated execution model:

**Graph-Based Processing:**
- Pipelines are compiled into execution graphs
- Operations are distributed across worker instances
- Automatic optimization and fusion of operations

**Worker Architecture:**
```yaml
# Dataflow worker configuration
worker:
  machineType: n1-standard-4
  diskSizeGb: 100
  numWorkers: 2-100  # Auto-scaling
  maxNumWorkers: 1000
```

## Pipeline Development

### Pipeline Lifecycle

1. **Pipeline Construction**
   - Define data sources and sinks
   - Create transformation operations
   - Configure pipeline options

2. **Graph Optimization**
   - Fusion of compatible operations
   - Optimization of data shuffling
   - Memory and network usage optimization

3. **Execution Planning**
   - Distribution across workers
   - Resource allocation
   - Fault tolerance setup

### Core Transforms

#### Source Transforms

**File-based Sources:**
```java
// Text files
PCollection<String> lines = pipeline.apply("Read Lines",
    TextIO.read().from("gs://bucket/input/*.txt"));

// Avro files
PCollection<GenericRecord> records = pipeline.apply("Read Avro",
    AvroIO.readGenericRecords(schema)
        .from("gs://bucket/input/*.avro"));

// Parquet files
PCollection<GenericRecord> parquetRecords = pipeline.apply("Read Parquet",
    ParquetIO.read(schema).from("gs://bucket/input/*.parquet"));
```

**Cloud Service Sources:**
```java
// BigQuery
PCollection<TableRow> rows = pipeline.apply("Read from BigQuery",
    BigQueryIO.readTableRows()
        .fromQuery("SELECT * FROM `project.dataset.table`"));

// Pub/Sub
PCollection<PubsubMessage> messages = pipeline.apply("Read from Pub/Sub",
    PubsubIO.readMessages().fromTopic("projects/project/topics/topic"));

// Cloud Storage
PCollection<String> files = pipeline.apply("Read from GCS",
    FileIO.match().filepattern("gs://bucket/**/*.json")
        .apply(FileIO.readMatches())
        .apply(TextIO.readFiles()));
```

#### Processing Transforms

**Map Operations:**
```java
// ParDo for element-wise transformations
PCollection<String> words = lines.apply("Extract Words",
    ParDo.of(new DoFn<String, String>() {
        @ProcessElement
        public void processElement(ProcessContext c) {
            String[] words = c.element().split("\\s+");
            for (String word : words) {
                c.output(word);
            }
        }
    }));
```

**Aggregation Operations:**
```java
// GroupByKey for key-based grouping
PCollection<KV<String, Integer>> wordCounts = words
    .apply("Create word-count pairs", ParDo.of(new PairWithOneFn()))
    .apply("Group by word", GroupByKey.create())
    .apply("Sum counts", ParDo.of(new SumCountsFn()));

// Combine for efficient aggregation
PCollection<KV<String, Double>> averages = values
    .apply("Compute averages", Combine.perKey(new MeanFn()));
```

**Windowing Operations:**
```java
// Fixed windows
PCollection<KV<String, Integer>> fixedWindowed = wordCounts
    .apply("Fixed windows", Window.into(FixedWindows.of(Duration.standardMinutes(5))));

// Sliding windows
PCollection<KV<String, Integer>> slidingWindowed = wordCounts
    .apply("Sliding windows",
        Window.into(SlidingWindows.of(Duration.standardMinutes(10))
            .every(Duration.standardMinutes(2))));

// Session windows
PCollection<KV<String, Integer>> sessionWindowed = wordCounts
    .apply("Session windows",
        Window.into(Sessions.withGapDuration(Duration.standardMinutes(5))));
```

#### Sink Transforms

**BigQuery Integration:**
```java
// Write to BigQuery
wordCounts.apply("Write to BigQuery",
    BigQueryIO.<KV<String, Integer>>write()
        .to("project:dataset.table")
        .withFormatFunction(new FormatFunction())
        .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_APPEND)
        .withCreateDisposition(BigQueryIO.Write.CreateDisposition.CREATE_IF_NEEDED));
```

**Cloud Storage Integration:**
```java
// Write to Cloud Storage
results.apply("Write to GCS",
    TextIO.write()
        .to("gs://bucket/output/results")
        .withSuffix(".txt")
        .withNumShards(10));
```

## Streaming Data Processing

### Stream Processing Concepts

**Event Time vs Processing Time:**
```java
// Event time windowing
PCollection<KV<String, Integer>> eventTimeWindows = events
    .apply("Add timestamps", WithTimestamps.of(
        (Event event) -> event.getTimestamp()))
    .apply("Event time windows", Window.into(FixedWindows.of(Duration.standardHours(1))));

// Processing time windowing
PCollection<KV<String, Integer>> processingTimeWindows = events
    .apply("Processing time windows", Window.into(FixedWindows.of(Duration.standardHours(1))));
```

**Watermarks and Triggers:**
```java
// Custom trigger for early results
Trigger trigger = AfterWatermark.pastEndOfWindow()
    .withEarlyFirings(AfterProcessingTime.pastFirstElementInPane()
        .plusDelayOf(Duration.standardMinutes(1)))
    .withLateFirings(AfterPane.elementCountAtLeast(1));

PCollection<WindowedData> windowed = data
    .apply("Custom windows", Window.into(FixedWindows.of(Duration.standardHours(1)))
        .triggering(trigger)
        .withAllowedLateness(Duration.standardHours(1)));
```

### State and Timers

**Value State:**
```java
public class StatefulTransform extends DoFn<KV<String, Integer>, String> {
    @StateId("sum")
    private final StateSpec<ValueState<Integer>> sumState = StateSpecs.value();

    @ProcessElement
    public void processElement(
        ProcessContext c,
        @StateId("sum") ValueState<Integer> sumState) {

        Integer current = MoreObjects.firstNonNull(sumState.read(), 0);
        Integer updated = current + c.element().getValue();
        sumState.write(updated);

        c.output("Sum for " + c.element().getKey() + ": " + updated);
    }
}
```

**Event Time Timers:**
```java
public class TimerExample extends DoFn<KV<String, Integer>, String> {
    @TimerId("expiry")
    private final TimerSpec timerSpec = TimerSpecs.timer(TimeDomain.EVENT_TIME);

    @ProcessElement
    public void processElement(
        ProcessContext c,
        @TimerId("expiry") Timer timer) {

        // Set timer to fire 1 hour after the watermark
        timer.set(c.timestamp().plus(Duration.standardHours(1)));
    }

    @OnTimer("expiry")
    public void onExpiry(OnTimerContext c) {
        c.output("Timer fired for key: " + c.key());
    }
}
```

## Batch Processing

### Batch Pipeline Patterns

**ETL Pipelines:**
```java
public static void main(String[] args) {
    PipelineOptions options = PipelineOptionsFactory.fromArgs(args).create();
    Pipeline pipeline = Pipeline.create(options);

    // Extract
    PCollection<String> rawData = pipeline
        .apply("Read CSV", TextIO.read().from(options.getInputFile()));

    // Transform
    PCollection<TableRow> transformedData = rawData
        .apply("Parse CSV", ParDo.of(new ParseCsvFn()))
        .apply("Validate Data", ParDo.of(new ValidateDataFn()))
        .apply("Enrich Data", ParDo.of(new EnrichDataFn()));

    // Load
    transformedData.apply("Write to BigQuery",
        BigQueryIO.writeTableRows()
            .to(options.getOutputTable())
            .withSchema(schema)
            .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_TRUNCATE));

    pipeline.run().waitUntilFinish();
}
```

**Data Validation:**
```java
public class ValidateDataFn extends DoFn<TableRow, TableRow> {
    private final Counter validRecords = Metrics.counter("validation", "valid");
    private final Counter invalidRecords = Metrics.counter("validation", "invalid");

    @ProcessElement
    public void processElement(ProcessContext c) {
        TableRow row = c.element();

        if (isValidRow(row)) {
            validRecords.inc();
            c.output(row);
        } else {
            invalidRecords.inc();
            // Could output to error collection
        }
    }

    private boolean isValidRow(TableRow row) {
        // Validation logic
        return row.get("required_field") != null;
    }
}
```

## Advanced Features

### Side Inputs

Side inputs allow access to additional data during processing:

```java
// Create side input
PCollectionView<Map<String, String>> lookupTable = pipeline
    .apply("Read lookup data", BigQueryIO.readTableRows().fromQuery(query))
    .apply("Create lookup map", ParDo.of(new CreateLookupMapFn()))
    .apply("As map view", View.asMap());

// Use side input in transform
PCollection<EnrichedData> enriched = mainData
    .apply("Enrich with lookup", ParDo.of(new EnrichWithLookupFn())
        .withSideInput("lookup", lookupTable));
```

### Custom Sources and Sinks

**Custom Source:**
```java
public class CustomSource extends BoundedSource<String> {
    @Override
    public List<? extends BoundedSource<String>> split(
        long desiredBundleSizeBytes, PipelineOptions options) {
        // Split source into bundles
        return splitIntoBundles(desiredBundleSizeBytes);
    }

    @Override
    public BoundedReader<String> createReader(PipelineOptions options) {
        return new CustomReader(this);
    }

    @Override
    public Coder<String> getOutputCoder() {
        return StringUtf8Coder.of();
    }
}
```

**Custom Sink:**
```java
public class CustomSink extends PTransform<PCollection<String>, PDone> {
    @Override
    public PDone expand(PCollection<String> input) {
        input.apply("Write to custom sink",
            ParDo.of(new WriteToCustomSinkFn()));
        return PDone.in(input.getPipeline());
    }
}
```

## Performance Optimization

### Pipeline Optimization

**Fusion Optimization:**
- Dataflow automatically fuses compatible operations
- Reduces serialization/deserialization overhead
- Minimizes data shuffling

**Shuffle Optimization:**
```java
// Optimize for large datasets
PCollection<KV<String, Iterable<Integer>>> grouped = data
    .apply("Group efficiently", GroupByKey.create())
    .apply("Optimize shuffle",
        Reshuffle.of()); // Forces shuffle optimization
```

### Resource Management

**Worker Configuration:**
```yaml
# Optimal worker configuration
dataflow:
  jobName: optimized-pipeline
  worker:
    machineType: n1-highmem-8  # Memory-optimized
    diskType: pd-ssd          # SSD for I/O intensive
    numWorkers: 10
    maxNumWorkers: 100
    autoscalingAlgorithm: THROUGHPUT_BASED
```

**Memory Management:**
```java
// Control memory usage
PipelineOptions options = PipelineOptionsFactory.create();
options.setMaxNumWorkers(50);
options.setWorkerMachineType("n1-standard-8");
options.setDiskSizeGb(500);

// Set pipeline-wide options
options.setJobName("memory-optimized-pipeline");
options.setProject("my-project");
options.setRegion("us-central1");
```

## Monitoring and Debugging

### Pipeline Monitoring

**Built-in Metrics:**
```java
// Custom metrics
private static final Counter processedElements =
    Metrics.counter("processing", "elements_processed");

private static final Distribution processingTime =
    Metrics.distribution("processing", "processing_time_ms");

@ProcessElement
public void processElement(ProcessContext c) {
    long startTime = System.currentTimeMillis();

    // Processing logic
    processData(c.element());

    long endTime = System.currentTimeMillis();
    processedElements.inc();
    processingTime.update(endTime - startTime);
}
```

**Dataflow Monitoring Console:**
- Pipeline graph visualization
- Step-by-step execution monitoring
- Resource utilization metrics
- Error and warning tracking

### Debugging Techniques

**Local Testing:**
```java
// Test pipeline locally
public static void main(String[] args) {
    // Create local pipeline
    Pipeline pipeline = Pipeline.create();

    // Add test data
    PCollection<String> testData = pipeline.apply(Create.of(
        "line 1", "line 2", "line 3"));

    // Apply transforms
    PCollection<String> results = testData
        .apply("Process", ParDo.of(new ProcessingFn()));

    // Run locally
    pipeline.run().waitUntilFinish();
}
```

**DirectRunner for Testing:**
```java
// Use DirectRunner for unit testing
PipelineOptions options = PipelineOptionsFactory.create();
options.setRunner(DirectRunner.class);

Pipeline pipeline = Pipeline.create(options);
// ... pipeline definition
```

## Integration Patterns

### Dataflow with Other GCP Services

**BigQuery Integration:**
```java
// Read from BigQuery with partitioning
PCollection<TableRow> data = pipeline.apply("Read partitioned data",
    BigQueryIO.readTableRows()
        .from("project:dataset.table")
        .withMethod(BigQueryIO.Read.Method.DIRECT_READ)
        .withSelectedFields(Arrays.asList("field1", "field2"))
        .withRowRestriction("date >= '2023-01-01'"));
```

**Pub/Sub Integration:**
```java
// Streaming pipeline with Pub/Sub
PCollection<PubsubMessage> messages = pipeline
    .apply("Read from Pub/Sub",
        PubsubIO.readMessages()
            .fromSubscription("projects/project/subscriptions/subscription")
            .withTimestampAttribute("timestamp"));

PCollection<String> payloads = messages
    .apply("Extract payload", ParDo.of(new ExtractPayloadFn()));
```

**Cloud Storage Integration:**
```java
// Process files as they arrive
PCollection<String> fileNotifications = pipeline
    .apply("Watch GCS bucket",
        PubsubIO.readStrings()
            .fromTopic("projects/project/topics/gcs-notifications"));

PCollection<String> fileContents = fileNotifications
    .apply("Read file contents",
        ParDo.of(new ReadFileFn()));
```

## Error Handling and Reliability

### Error Handling Patterns

**Dead Letter Queues:**
```java
// Separate good and bad records
PCollectionTuple results = input
    .apply("Validate records", ParDo.of(new ValidateFn())
        .withOutputTags(VALID_TAG, TupleTagList.of(ERROR_TAG)));

// Process valid records
results.get(VALID_TAG).apply("Process valid", ...);

// Handle errors
results.get(ERROR_TAG).apply("Write errors to DLQ",
    TextIO.write().to("gs://bucket/dlq/errors"));
```

**Retry Logic:**
```java
public class RetryFn extends DoFn<String, String> {
    private static final int MAX_RETRIES = 3;

    @ProcessElement
    public void processElement(ProcessContext c) {
        String element = c.element();
        int retryCount = getRetryCount(element);

        try {
            processWithRetry(element);
            c.output(element);
        } catch (Exception e) {
            if (retryCount < MAX_RETRIES) {
                // Output to retry collection
                c.output(element); // Will be retried
            } else {
                // Send to dead letter queue
                // ... handle permanent failure
            }
        }
    }
}
```

### Fault Tolerance

**Checkpointing:**
- Automatic checkpointing of pipeline state
- Recovery from worker failures
- Exactly-once processing guarantees

**Idempotent Operations:**
```java
// Ensure idempotent writes
data.apply("Idempotent write",
    BigQueryIO.writeTableRows()
        .to(tableSpec)
        .withMethod(BigQueryIO.Write.Method.STORAGE_WRITE_API)
        .withWriteDisposition(BigQueryIO.Write.WriteDisposition.WRITE_APPEND));
```

## Cost Optimization

### Resource Optimization

**Autoscaling Configuration:**
```yaml
# Cost-effective autoscaling
dataflow:
  autoscalingAlgorithm: THROUGHPUT_BASED
  minNumWorkers: 2
  maxNumWorkers: 50
  workerMachineType: n1-standard-2  # Smaller instances
```

**Data Skew Handling:**
```java
// Handle data skew
PCollection<KV<String, Integer>> skewedData = // ... input

// Redistribute skewed data
PCollection<KV<String, Integer>> balancedData = skewedData
    .apply("Balance data", ParDo.of(new BalanceFn()))
    .apply("Reshuffle", Reshuffle.of());
```

### Cost Monitoring

**Cost Tracking:**
- Monitor Dataflow job costs
- Track resource utilization
- Optimize pipeline efficiency
- Use appropriate machine types

## Security and Compliance

### Data Security

**Encryption:**
- Data in transit: TLS encryption
- Data at rest: Google-managed encryption
- Customer-managed encryption keys (CMEK)

**Access Control:**
```bash
# IAM roles for Dataflow
gcloud projects add-iam-policy-binding project-id \
    --member=serviceAccount:service-account@project.iam.gserviceaccount.com \
    --role=roles/dataflow.worker
```

### Compliance Features

**Audit Logging:**
- Cloud Audit Logs integration
- Detailed operation logging
- Compliance reporting

**Data Residency:**
- Regional data processing
- Data sovereignty controls
- Cross-region replication options

## Best Practices

### Pipeline Design

**Modular Design:**
```java
// Break complex pipelines into composable transforms
public class DataProcessingPipeline {
    public static PTransform<PCollection<String>, PCollection<ProcessedData>>
        buildProcessingPipeline() {
        return new ProcessingPipeline();
    }
}

class ProcessingPipeline extends PTransform<PCollection<String>, PCollection<ProcessedData>> {
    @Override
    public PCollection<ProcessedData> expand(PCollection<String> input) {
        return input
            .apply("Parse", new ParseTransform())
            .apply("Validate", new ValidationTransform())
            .apply("Enrich", new EnrichmentTransform())
            .apply("Aggregate", new AggregationTransform());
    }
}
```

**Testing Strategy:**
```java
@Test
public void testPipeline() {
    Pipeline pipeline = TestPipeline.create();

    PCollection<String> input = pipeline.apply(Create.of("test data"));

    PCollection<ProcessedData> output = input.apply(new ProcessingPipeline());

    PAssert.that(output).containsInAnyOrder(expectedResults);

    pipeline.run();
}
```

### Performance Best Practices

**Memory Management:**
- Monitor heap usage
- Use appropriate windowing strategies
- Implement efficient serialization

**Network Optimization:**
- Minimize data shuffling
- Use appropriate coder types
- Optimize bundle sizes

**Resource Allocation:**
- Right-size worker machines
- Configure appropriate parallelism
- Monitor and adjust autoscaling settings

## Migration and Integration

### Migrating from Other Systems

**From Apache Spark:**
```java
// Spark-style operations in Beam
PCollection<KV<String, Integer>> wordCounts = lines
    .flatMap(line -> Arrays.asList(line.split("\\s+")))
    .map(word -> KV.of(word, 1))
    .reduceByKey((a, b) -> a + b);
```

**From Custom ETL:**
- Identify data sources and sinks
- Map existing logic to Beam transforms
- Implement error handling and monitoring
- Test thoroughly before production deployment

### Hybrid Deployments

**On-Premises Integration:**
- Dataflow with VPN/Interconnect
- Hybrid data processing patterns
- Secure data transfer mechanisms

**Multi-Cloud Scenarios:**
- Portable Beam pipelines
- Cloud-agnostic data processing
- Cross-cloud data synchronization
