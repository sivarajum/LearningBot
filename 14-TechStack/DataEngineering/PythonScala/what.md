# Python & Scala for Data Engineering

## Overview

Python and Scala are the primary programming languages for data engineering, each offering unique strengths in building scalable data pipelines, ETL processes, and data processing systems. Python excels in ease of use and rich ecosystem, while Scala provides strong typing and performance advantages, particularly with Apache Spark.

## Python in Data Engineering

### Core Data Processing Libraries

#### Pandas: DataFrame Operations
Pandas provides high-performance, easy-to-use data structures and data analysis tools.

```python
import pandas as pd
import numpy as np

# Data ingestion
df = pd.read_csv('data.csv', parse_dates=['date'])
df = pd.read_parquet('data.parquet')
df = pd.read_json('data.json', lines=True)

# Data exploration
print(df.head())
print(df.info())
print(df.describe())

# Data cleaning
df = df.dropna(subset=['critical_column'])
df['date'] = pd.to_datetime(df['date'])
df = df.drop_duplicates()

# Data transformation
df['year'] = df['date'].dt.year
df['revenue_category'] = pd.cut(df['revenue'],
                               bins=[0, 1000, 10000, np.inf],
                               labels=['Small', 'Medium', 'Large'])

# Grouping and aggregation
result = df.groupby(['year', 'category']).agg({
    'revenue': ['sum', 'mean', 'count'],
    'customers': 'nunique'
}).round(2)

# Pivot tables
pivot = df.pivot_table(
    values='revenue',
    index='month',
    columns='category',
    aggfunc='sum',
    fill_value=0
)
```

#### NumPy: Numerical Computing
NumPy provides support for large, multi-dimensional arrays and matrices.

```python
import numpy as np

# Array operations
data = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])

# Vectorized operations (efficient)
result = data * 2 + 10
filtered = data[data > 3]

# Statistical operations
mean = np.mean(data)
std = np.std(data)
percentiles = np.percentile(data, [25, 50, 75])

# Broadcasting
matrix = np.array([[1, 2, 3], [4, 5, 6]])
vector = np.array([10, 20, 30])
result = matrix + vector  # Broadcasting
```

### ETL Frameworks

#### Apache Airflow: Workflow Orchestration
Airflow is a platform for programmatically authoring, scheduling, and monitoring workflows.

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline',
    schedule_interval='@daily',
    catchup=False
)

def extract_data():
    """Extract data from source"""
    import pandas as pd
    # Extract logic here
    return "Data extracted"

def transform_data():
    """Transform extracted data"""
    # Transform logic here
    return "Data transformed"

def load_data():
    """Load data to destination"""
    # Load logic here
    return "Data loaded"

# Define tasks
extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load_data,
    dag=dag
)

# Define dependencies
extract_task >> transform_task >> load_task

# Database operation
create_table = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS sales_summary (
        date DATE PRIMARY KEY,
        total_sales DECIMAL(10,2),
        total_orders INTEGER
    );
    """,
    dag=dag
)

create_table >> extract_task
```

#### Prefect: Modern Workflow Orchestration
Prefect provides a modern approach to workflow orchestration with better error handling.

```python
from prefect import flow, task
from prefect.tasks import task
import pandas as pd

@task
def extract_data(source: str):
    """Extract data from various sources"""
    if source == 'csv':
        return pd.read_csv('data.csv')
    elif source == 'api':
        # API extraction logic
        return pd.DataFrame()
    else:
        raise ValueError(f"Unsupported source: {source}")

@task
def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate data quality"""
    if df.empty:
        raise ValueError("DataFrame is empty")

    # Check for required columns
    required_cols = ['date', 'amount']
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    return df

@task
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform data"""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    df['amount_clean'] = df['amount'].fillna(0)

    return df.groupby('month')['amount_clean'].sum().reset_index()

@task
def load_data(df: pd.DataFrame, table_name: str):
    """Load data to database"""
    from sqlalchemy import create_engine

    engine = create_engine('postgresql://user:pass@localhost/db')
    df.to_sql(table_name, engine, if_exists='replace', index=False)

@flow
def etl_pipeline(source: str = 'csv', table_name: str = 'monthly_sales'):
    """Main ETL pipeline"""
    raw_data = extract_data(source)
    validated_data = validate_data(raw_data)
    transformed_data = transform_data(validated_data)
    load_data(transformed_data, table_name)

# Run the pipeline
if __name__ == "__main__":
    etl_pipeline()
```

### Data Validation and Quality

#### Great Expectations: Data Validation
Great Expectations provides comprehensive data validation and documentation.

```python
import great_expectations as ge
import pandas as pd

# Load data
df = pd.read_csv('sales_data.csv')
df_ge = ge.from_pandas(df)

# Define expectations
result = df_ge.expect_column_values_to_not_be_null('customer_id')
result = df_ge.expect_column_values_to_be_between('amount', 0, 10000)
result = df_ge.expect_column_values_to_match_regex('email', r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Custom expectation
def expect_column_values_to_be_valid_dates(column):
    def is_valid_date(value):
        try:
            pd.to_datetime(value)
            return True
        except:
            return False

    return column.apply(is_valid_date).all()

result = df_ge.expect_column_values_to_be_valid_dates('order_date')

# Generate data documentation
suite = df_ge.get_expectation_suite()
print(suite)
```

#### Pandera: DataFrame Schema Validation
Pandera provides runtime data validation for pandas DataFrames.

```python
import pandas as pd
import pandera as pa

# Define schema
schema = pa.DataFrameSchema({
    "customer_id": pa.Column(int, nullable=False, unique=True),
    "email": pa.Column(str, nullable=False,
                      checks=pa.Check.str_matches(r'^[\w\.-]+@[\w\.-]+\.\w+$')),
    "amount": pa.Column(float, nullable=False,
                       checks=pa.Check(lambda x: x > 0)),
    "order_date": pa.Column(pa.DateTime, nullable=False),
    "status": pa.Column(str, nullable=False,
                       checks=pa.Check.isin(['pending', 'completed', 'cancelled']))
})

# Validate data
@pa.check_input(schema)
def process_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Process orders with validation"""
    return df.groupby('status')['amount'].sum()

# Usage
df = pd.read_csv('orders.csv')
result = process_orders(df)
```

### Database Operations

#### SQLAlchemy: ORM and SQL Toolkit
SQLAlchemy provides a comprehensive SQL toolkit and ORM.

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

Base = declarative_base()

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    product = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    sale_date = Column(DateTime, nullable=False)

# Create engine
engine = create_engine('postgresql://user:password@localhost/sales_db')

# Create tables
Base.metadata.create_all(engine)

# Bulk insert using pandas
df = pd.read_csv('sales_data.csv')
df.to_sql('sales', engine, if_exists='append', index=False)

# ORM operations
Session = sessionmaker(bind=engine)
session = Session()

# Query with pandas
query = """
SELECT
    DATE_TRUNC('month', sale_date) as month,
    SUM(amount) as total_sales,
    COUNT(*) as num_sales
FROM sales
WHERE sale_date >= '2023-01-01'
GROUP BY DATE_TRUNC('month', sale_date)
ORDER BY month
"""

df_result = pd.read_sql(query, engine)
print(df_result)
```

### Streaming Data Processing

#### Kafka-Python: Kafka Integration
Kafka-Python provides Kafka client for Python.

```python
from kafka import KafkaProducer, KafkaConsumer
import json
import pandas as pd

# Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_data(topic: str, data: dict):
    """Send data to Kafka topic"""
    future = producer.send(topic, data)
    record_metadata = future.get(timeout=10)
    print(f"Sent to {record_metadata.topic} partition {record_metadata.partition}")

# Consumer
consumer = KafkaConsumer(
    'sales-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='data-engineering-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def process_stream():
    """Process streaming data"""
    batch_data = []

    for message in consumer:
        data = message.value
        batch_data.append(data)

        # Process in batches
        if len(batch_data) >= 100:
            df = pd.DataFrame(batch_data)
            # Process batch
            process_batch(df)
            batch_data = []

# Streaming analytics
def process_batch(df: pd.DataFrame):
    """Process batch of streaming data"""
    # Real-time aggregations
    result = df.groupby('product_category').agg({
        'revenue': 'sum',
        'quantity': 'sum'
    }).reset_index()

    # Store results
    result.to_sql('realtime_aggregates',
                  engine, if_exists='replace', index=False)
```

## Scala in Data Engineering

### Scala Fundamentals for Data Engineering

#### Case Classes and Pattern Matching
Scala provides powerful data modeling capabilities.

```scala
// Case classes for data modeling
case class Customer(id: Int, name: String, email: String)
case class Order(id: Int, customerId: Int, amount: Double, date: LocalDate)
case class OrderWithCustomer(order: Order, customer: Customer)

// Pattern matching for data processing
def processOrder(order: Order): String = order match {
  case Order(_, _, amount, _) if amount > 1000 => "High Value"
  case Order(_, _, amount, _) if amount > 100 => "Medium Value"
  case _ => "Low Value"
}

// Extractor patterns
object HighValueOrder {
  def unapply(order: Order): Option[(Int, Double)] = {
    if (order.amount > 1000) Some((order.id, order.amount))
    else None
  }
}

val order = Order(1, 100, 1500.0, LocalDate.now())
order match {
  case HighValueOrder(id, amount) => println(s"High value order: $id, $$$amount")
  case _ => println("Regular order")
}
```

#### Collections and Functional Programming
Scala's rich collection library enables functional data processing.

```scala
// Immutable collections
val numbers = List(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

// Functional operations
val evenNumbers = numbers.filter(_ % 2 == 0)
val doubled = numbers.map(_ * 2)
val sum = numbers.reduce(_ + _)

// Advanced operations
val grouped = numbers.groupBy(_ % 3)
val sorted = numbers.sorted(Ordering[Int].reverse)
val distinct = numbers.distinct

// Working with Options
def safeDivision(a: Double, b: Double): Option[Double] = {
  if (b != 0) Some(a / b) else None
}

val result = safeDivision(10, 2).map(_ * 2).getOrElse(0.0)

// For comprehensions
case class Person(name: String, age: Int, city: String)

val people = List(
  Person("Alice", 25, "NYC"),
  Person("Bob", 30, "LA"),
  Person("Charlie", 35, "NYC")
)

val nycAdults = for {
  person <- people
  if person.age >= 18 && person.city == "NYC"
} yield person.name
```

### Apache Spark with Scala

#### DataFrame Operations in Scala
Scala provides type-safe DataFrame operations.

```scala
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

val spark = SparkSession.builder()
  .appName("DataEngineering")
  .getOrCreate()

// Define schema
val schema = StructType(Array(
  StructField("id", IntegerType, false),
  StructField("name", StringType, false),
  StructField("amount", DoubleType, false),
  StructField("date", DateType, false)
))

// Read data
val df = spark.read
  .schema(schema)
  .parquet("data/transactions")

// Type-safe operations with Datasets
case class Transaction(id: Int, name: String, amount: Double, date: java.sql.Date)

val ds = df.as[Transaction]

// Type-safe filtering
val highValueTransactions = ds.filter(_.amount > 1000)

// Type-safe aggregations
val summary = ds.groupByKey(_.name)
  .agg(sum[Transaction](_.amount).as[Double])
  .mapGroups { case (name, transactions) =>
    val total = transactions.sum
    val count = transactions.size
    (name, total, count)
  }

// Complex transformations
val enrichedDF = df
  .withColumn("month", month($"date"))
  .withColumn("year", year($"date"))
  .withColumn("amount_category",
    when($"amount" > 1000, "High")
    .when($"amount" > 100, "Medium")
    .otherwise("Low"))
  .withColumn("is_weekend",
    $"date".isin("Saturday", "Sunday": _*))

// Window functions
val windowSpec = Window
  .partitionBy("name")
  .orderBy("date")
  .rowsBetween(Window.unboundedPreceding, Window.currentRow)

val runningTotal = df
  .withColumn("running_total", sum($"amount").over(windowSpec))
```

#### Custom UDFs and UDAFs
User-defined functions for custom logic.

```scala
// UDF - User Defined Function
val categorizeAmount = udf((amount: Double) => {
  if (amount > 1000) "High"
  else if (amount > 100) "Medium"
  else "Low"
})

val result = df.withColumn("category", categorizeAmount($"amount"))

// UDAF - User Defined Aggregate Function
class AverageUDAF extends Aggregator[Double, (Double, Long), Double] {
  override def zero: (Double, Long) = (0.0, 0L)

  override def reduce(buffer: (Double, Long), data: Double): (Double, Long) = {
    (buffer._1 + data, buffer._2 + 1)
  }

  override def merge(buffer1: (Double, Long), buffer2: (Double, Long)): (Double, Long) = {
    (buffer1._1 + buffer2._1, buffer1._2 + buffer2._2)
  }

  override def finish(reduction: (Double, Long)): Double = {
    if (reduction._2 == 0) 0.0 else reduction._1 / reduction._2
  }

  override def bufferEncoder: Encoder[(Double, Long)] = Encoders.tuple(Encoders.scalaDouble, Encoders.scalaLong)

  override def outputEncoder: Encoder[Double] = Encoders.scalaDouble
}

// Register UDAF
val averageUDAF = udf(new AverageUDAF())
val avgByGroup = df.groupBy("category")
  .agg(averageUDAF($"amount").as("avg_amount"))
```

### ETL Pipelines in Scala

#### Akka Streams: Reactive Stream Processing
Akka Streams provides reactive stream processing capabilities.

```scala
import akka.actor.ActorSystem
import akka.stream.scaladsl._
import scala.concurrent.Future

implicit val system = ActorSystem("ETLSystem")
implicit val ec = system.dispatcher

// Source from database
val source = Source.fromPublisher(databasePublisher)

// Processing stages
val processedSource = source
  .map(extractFields)
  .filter(isValidRecord)
  .grouped(100)  // Process in batches
  .mapAsync(4)(processBatch)  // Parallel processing
  .mapConcat(identity)  // Flatten results

// Sink to multiple destinations
val sink = Sink.foreachParallel(4)(writeToDatabase)

val graph = processedSource.to(sink)

// Run the stream
val future = graph.run()

future.onComplete {
  case Success(_) => println("ETL completed successfully")
  case Failure(ex) => println(s"ETL failed: ${ex.getMessage}")
}
```

#### Type-Safe Configuration
Scala provides type-safe configuration management.

```scala
import pureconfig._
import pureconfig.generic.auto._

case class DatabaseConfig(
  host: String,
  port: Int,
  database: String,
  username: String,
  password: String,
  maxConnections: Int = 10
)

case class KafkaConfig(
  bootstrapServers: String,
  topic: String,
  groupId: String,
  autoOffsetReset: String = "earliest"
)

case class AppConfig(
  database: DatabaseConfig,
  kafka: KafkaConfig,
  batchSize: Int = 1000,
  parallelism: Int = 4
)

// Load configuration
val config = ConfigSource.default.load[AppConfig] match {
  case Right(cfg) => cfg
  case Left(errors) =>
    throw new RuntimeException(s"Failed to load config: $errors")
}

// Use configuration
val dbConnection = createConnection(config.database)
val kafkaConsumer = createConsumer(config.kafka)
```

### Testing Data Pipelines

#### ScalaTest with Spark
Comprehensive testing for data pipelines.

```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._

class DataPipelineSpec extends AnyFlatSpec with Matchers {

  lazy val spark: SparkSession = SparkSession.builder()
    .master("local[2]")
    .appName("DataPipelineTest")
    .getOrCreate()

  "Data transformation pipeline" should "correctly categorize amounts" in {
    // Create test data
    val testData = Seq(
      (1, "Product A", 50.0),
      (2, "Product B", 500.0),
      (3, "Product C", 1500.0)
    )

    val df = spark.createDataFrame(testData)
      .toDF("id", "product", "amount")

    // Apply transformation
    val result = df.withColumn("category",
      when($"amount" > 1000, "High")
      .when($"amount" > 100, "Medium")
      .otherwise("Low"))

    // Verify results
    val categories = result.select("category").collect().map(_.getString(0))

    categories should contain allOf ("Low", "Medium", "High")
    categories.count(_ == "High") shouldBe 1
    categories.count(_ == "Medium") shouldBe 1
    categories.count(_ == "Low") shouldBe 1
  }

  it should "handle null values correctly" in {
    val testData = Seq(
      (1, "Product A", Some(100.0)),
      (2, "Product B", None),
      (3, "Product C", Some(200.0))
    )

    val df = spark.createDataFrame(testData)
      .toDF("id", "product", "amount")

    val result = df.withColumn("amount_clean",
      coalesce($"amount", lit(0.0)))

    val nullCount = result.filter($"amount_clean".isNull).count()
    nullCount shouldBe 0
  }
}
```

## Best Practices

### Python Best Practices

#### Code Organization
```python
# project/
# ├── src/
# │   ├── __init__.py
# │   ├── etl/
# │   │   ├── __init__.py
# │   │   ├── extract.py
# │   │   ├── transform.py
# │   │   └── load.py
# │   └── utils/
# │       ├── __init__.py
# │       └── validation.py
# ├── tests/
# │   ├── test_etl.py
# │   └── test_validation.py
# ├── config/
# │   └── config.yaml
# └── requirements.txt

# ETL pipeline structure
from typing import Dict, Any
import logging
from dataclasses import dataclass

@dataclass
class ETLConfig:
    source_path: str
    destination_table: str
    batch_size: int = 1000

class ETLProcessor:
    def __init__(self, config: ETLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def extract(self) -> pd.DataFrame:
        """Extract data from source"""
        try:
            df = pd.read_parquet(self.config.source_path)
            self.logger.info(f"Extracted {len(df)} records")
            return df
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data"""
        df = df.copy()
        df = self._clean_data(df)
        df = self._enrich_data(df)
        return df

    def load(self, df: pd.DataFrame) -> None:
        """Load data to destination"""
        try:
            df.to_sql(
                self.config.destination_table,
                engine,
                if_exists='append',
                index=False,
                chunksize=self.config.batch_size
            )
            self.logger.info(f"Loaded {len(df)} records")
        except Exception as e:
            self.logger.error(f"Loading failed: {e}")
            raise

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Data cleaning logic"""
        return df.dropna(subset=['required_column'])

    def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Data enrichment logic"""
        df['processed_at'] = pd.Timestamp.now()
        return df
```

#### Error Handling and Logging
```python
import logging
from typing import Optional
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl.log'),
        logging.StreamHandler()
    ]
)

class DataPipelineError(Exception):
    """Custom exception for data pipeline errors"""
    pass

def process_with_error_handling(func):
    """Decorator for error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Custom error handling
            if isinstance(e, pd.errors.EmptyDataError):
                logger.warning("Empty data file encountered")
                return pd.DataFrame()
            elif isinstance(e, sqlalchemy.exc.OperationalError):
                logger.error("Database connection error")
                raise DataPipelineError("Database unavailable") from e
            else:
                raise DataPipelineError(f"Unexpected error: {str(e)}") from e
    return wrapper

@process_with_error_handling
def extract_data(source: str) -> pd.DataFrame:
    """Extract with error handling"""
    return pd.read_csv(source)
```

### Scala Best Practices

#### Functional Programming Patterns
```scala
// Using Either for error handling
def validateData(df: DataFrame): Either[String, DataFrame] = {
  val rowCount = df.count()
  val nullCount = df.filter($"critical_column".isNull).count()

  if (rowCount == 0) {
    Left("DataFrame is empty")
  } else if (nullCount > rowCount * 0.1) {
    Left(s"Too many null values: $nullCount out of $rowCount")
  } else {
    Right(df)
  }
}

// Using Try for exception handling
import scala.util.{Try, Success, Failure}

def processFile(path: String): Try[DataFrame] = {
  Try {
    spark.read.parquet(path)
  }.recoverWith {
    case e: Exception =>
      logger.error(s"Failed to read file $path: ${e.getMessage}")
      Failure(e)
  }
}

// Composable transformations
type DataTransformation = DataFrame => DataFrame

val cleanData: DataTransformation = df =>
  df.na.drop(Seq("required_column"))

val addMetadata: DataTransformation = df =>
  df.withColumn("processed_at", current_timestamp())

val enrichData: DataTransformation = df =>
  df.withColumn("category",
    when($"amount" > 1000, "High")
    .otherwise("Normal"))

val pipeline: DataTransformation = cleanData andThen addMetadata andThen enrichData

val result = pipeline(rawData)
```

#### Type Safety and Immutability
```scala
// Sealed traits for type safety
sealed trait DataSource
case class FileSource(path: String, format: String) extends DataSource
case class DatabaseSource(url: String, table: String) extends DataSource
case class KafkaSource(topic: String, brokers: String) extends DataSource

sealed trait ProcessingResult
case class Success(data: DataFrame, recordCount: Long) extends ProcessingResult
case class Failure(error: String, retryable: Boolean) extends ProcessingResult

// Immutable configuration
case class PipelineConfig(
  name: String,
  source: DataSource,
  transformations: List[String],
  sink: String,
  retryCount: Int = 3,
  batchSize: Int = 1000
)

// Pure functions
def calculateRevenue(df: DataFrame): DataFrame = {
  df.withColumn("total_revenue",
    $"quantity" * $"unit_price" * (lit(1.0) - $"discount"))
}

def addProcessingTimestamp(df: DataFrame): DataFrame = {
  df.withColumn("processed_at", current_timestamp())
}
```

## Performance Optimization

### Python Performance Tips

#### Vectorized Operations
```python
import pandas as pd
import numpy as np

# Efficient operations
df = pd.DataFrame({
    'a': np.random.randn(1000000),
    'b': np.random.randn(1000000),
    'c': np.random.randn(1000000)
})

# Vectorized operations (fast)
df['result'] = df['a'] * df['b'] + df['c']

# Avoid loops (slow)
# DON'T DO THIS:
# for idx, row in df.iterrows():
#     df.loc[idx, 'result'] = row['a'] * row['b'] + row['c']

# Use apply only when necessary
df['category'] = df['score'].apply(lambda x:
    'High' if x > 0.8 else 'Medium' if x > 0.5 else 'Low')
```

#### Memory Optimization
```python
# Read large files in chunks
chunk_size = 100000
chunks = pd.read_csv('large_file.csv', chunksize=chunk_size)

processed_chunks = []
for chunk in chunks:
    # Process chunk
    processed_chunk = transform_chunk(chunk)
    processed_chunks.append(processed_chunk)

result = pd.concat(processed_chunks, ignore_index=True)

# Use appropriate data types
df = pd.read_csv('data.csv', dtype={
    'id': 'int32',          # Smaller than int64
    'category': 'category', # Categorical for repeated strings
    'flag': 'bool'          # Boolean instead of object
})

# Delete unused DataFrames
del intermediate_df
import gc
gc.collect()
```

### Scala Performance Tips

#### Avoiding Boxing/Unboxing
```scala
// Use primitive types when possible
val numbers: Array[Int] = Array(1, 2, 3, 4, 5)
val sum = numbers.sum  // No boxing

// Avoid collections when primitives suffice
val data = (1 to 1000000).toArray
val filtered = data.filter(_ % 2 == 0)  // Array[Int], not Seq[Int]
```

#### Efficient DataFrame Operations
```scala
// Cache strategically
val intermediate = df
  .filter($"status" === "active")
  .cache()  // Cache for multiple operations

val result1 = intermediate.groupBy("category").count()
val result2 = intermediate.agg(avg("amount"))
val result3 = intermediate.select("id", "amount")

intermediate.unpersist()  // Don't forget to unpersist

// Use columnar operations
val result = df.select(
  $"id",
  $"amount" * 1.1 as "amount_with_tax",
  when($"category" === "premium", $"amount" * 0.9)
    .otherwise($"amount") as "discounted_amount"
)

// Prefer DataFrame over RDD when possible
val dfResult = df.filter($"amount" > 100).groupBy("category").sum("amount")
val rddResult = df.rdd.filter(_.amount > 100).groupBy(_.category).mapValues(_.sum)  // Less efficient
```

## Summary

Python and Scala provide complementary strengths for data engineering:

**Python Advantages:**
- Rich ecosystem (pandas, numpy, scikit-learn)
- Easy to learn and use
- Excellent for prototyping and scripting
- Strong in data analysis and visualization
- Great for ML and AI workflows

**Scala Advantages:**
- Strong static typing and functional programming
- Excellent performance with Spark
- Type safety prevents runtime errors
- Great for large-scale distributed systems
- Strong concurrency support

**Best Practices:**
- Choose Python for data analysis, exploration, and ML
- Choose Scala for production Spark applications and type safety
- Use both languages together (Python for analysis, Scala for production pipelines)
- Focus on functional programming patterns
- Implement comprehensive error handling and logging
- Optimize for performance using vectorized operations and efficient data structures
- Write testable, maintainable code with proper separation of concerns