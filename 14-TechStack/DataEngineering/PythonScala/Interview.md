# Python & Scala Data Engineering Interview Questions & Answers

## Beginner Level Questions

### 1. What are the main differences between Python and Scala for data engineering?
**Answer:** Python and Scala serve different purposes in data engineering:

**Python Advantages:**
- Easier learning curve and more readable syntax
- Rich ecosystem (pandas, numpy, scikit-learn)
- Excellent for data analysis, prototyping, and scripting
- Strong in machine learning and AI workflows
- Dynamic typing allows for flexible development

**Scala Advantages:**
- Strong static typing prevents runtime errors
- Better performance, especially with Apache Spark
- Functional programming paradigm
- Immutable data structures by default
- Excellent for building large-scale distributed systems

**When to choose:**
- **Python**: Data exploration, ETL scripting, ML pipelines, smaller teams
- **Scala**: Production Spark applications, type safety requirements, larger teams

### 2. How do you read a CSV file in pandas?
**Answer:**
```python
import pandas as pd

# Basic reading
df = pd.read_csv('data.csv')

# With options
df = pd.read_csv('data.csv',
                 sep=',',                    # delimiter
                 header=0,                   # header row
                 index_col=0,                # index column
                 parse_dates=['date_col'],   # parse dates
                 dtype={'col1': 'str', 'col2': 'int'})  # data types

# Read in chunks for large files
chunks = pd.read_csv('large_file.csv', chunksize=100000)
for chunk in chunks:
    process_chunk(chunk)
```

### 3. What is a pandas DataFrame?
**Answer:** A DataFrame is a 2-dimensional labeled data structure in pandas, similar to a spreadsheet or SQL table.

**Key Characteristics:**
- **Labeled axes**: Rows and columns have labels
- **Heterogeneous data**: Different data types in different columns
- **Size mutable**: Can add/delete columns and rows
- **Operations**: Supports arithmetic operations, grouping, pivoting

**Basic operations:**
```python
# Create DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago']
})

# Access data
df['name']        # Column access
df.loc[0]         # Row access by label
df.iloc[0]        # Row access by position
df.head()         # First 5 rows
df.shape          # Dimensions
```

### 4. How do you handle missing values in pandas?
**Answer:**
```python
# Check for missing values
df.isnull().sum()          # Count nulls per column
df.isnull().any()          # Check if any nulls exist

# Remove missing values
df.dropna()                 # Remove rows with any null
df.dropna(subset=['col'])   # Remove rows where specific column is null

# Fill missing values
df.fillna(0)                              # Fill with 0
df.fillna(df.mean())                      # Fill with column mean
df.fillna(method='ffill')                 # Forward fill
df.fillna(method='bfill')                 # Backward fill
df['col'].fillna(df['col'].mode()[0])     # Fill with mode

# Interpolate missing values
df.interpolate(method='linear')
```

### 5. What are case classes in Scala?
**Answer:** Case classes are immutable data structures in Scala that provide:

**Features:**
- **Automatic methods**: equals, hashCode, toString, copy
- **Pattern matching support**: Can be used in match expressions
- **Immutable by default**: All parameters are val
- **Companion object**: Automatically generated with apply/unapply

**Example:**
```scala
// Define case class
case class Person(name: String, age: Int, city: String)

// Create instances
val alice = Person("Alice", 25, "NYC")
val bob = Person("Bob", 30, "LA")

// Automatic methods
alice.copy(age = 26)  // Create modified copy
alice == Person("Alice", 25, "NYC")  // true

// Pattern matching
def greet(person: Person): String = person match {
  case Person(name, age, _) if age < 18 => s"Hi $name, you're young!"
  case Person(name, _, "NYC") => s"Hello $name from NYC!"
  case Person(name, _, _) => s"Hello $name!"
}
```

## Intermediate Level Questions

### 6. How do you perform data aggregation in pandas?
**Answer:**
```python
# Group by and aggregate
result = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'price': 'max'
})

# Multiple aggregations
df.groupby('category')['sales'].agg(['sum', 'mean', 'std'])

# Custom aggregation functions
def range_func(x):
    return x.max() - x.min()

df.groupby('category')['sales'].agg(['sum', 'mean', range_func])

# Pivot tables
pivot = df.pivot_table(
    values='sales',
    index='month',
    columns='category',
    aggfunc='sum',
    fill_value=0
)

# Rolling windows
df['rolling_avg'] = df.groupby('category')['sales']
    .rolling(window=7)
    .mean()
    .reset_index(0, drop=True)
```

### 7. Explain Apache Airflow DAGs and how to create them.
**Answer:**
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Define default arguments
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

# Create DAG
dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'daily']
)

# Define tasks
def extract_data():
    import pandas as pd
    df = pd.read_csv('source.csv')
    df.to_parquet('staging/extracted.parquet')
    return 'Data extracted'

def transform_data():
    import pandas as pd
    df = pd.read_parquet('staging/extracted.parquet')
    # Transform logic
    df['processed_date'] = pd.Timestamp.now()
    df.to_parquet('staging/transformed.parquet')
    return 'Data transformed'

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

load_task = BashOperator(
    task_id='load',
    bash_command='cp staging/transformed.parquet data/warehouse/',
    dag=dag
)

# Set dependencies
extract_task >> transform_task >> load_task
```

### 8. How do you implement data validation in Python?
**Answer:** Using Great Expectations and Pandera:

**Great Expectations:**
```python
import great_expectations as ge
import pandas as pd

df = pd.read_csv('data.csv')
df_ge = ge.from_pandas(df)

# Define expectations
expectations = [
    df_ge.expect_column_values_to_not_be_null('customer_id'),
    df_ge.expect_column_values_to_be_between('amount', 0, 10000),
    df_ge.expect_column_values_to_match_regex('email', r'^[\w\.-]+@[\w\.-]+\.\w+$'),
    df_ge.expect_column_proportion_of_unique_values_to_be_between('customer_id', 0.9, 1.0)
]

# Validate
results = [exp.run() for exp in expectations]
failed = [r for r in results if not r.success]

if failed:
    raise ValueError(f"Data validation failed: {len(failed)} expectations not met")
```

**Pandera:**
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
    "order_date": pa.Column(pa.DateTime, nullable=False)
})

# Validate
@pa.check_input(schema)
def process_orders(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(df['order_date'].dt.month)['amount'].sum()

# Usage
df = pd.read_csv('orders.csv')
result = process_orders(df)
```

### 9. Explain pattern matching in Scala.
**Answer:** Pattern matching is a powerful feature in Scala for checking values against patterns:

```scala
// Basic pattern matching
def describe(x: Any): String = x match {
  case 1 => "one"
  case "hello" => "greeting"
  case List(1, 2, _) => "list starting with 1, 2"
  case Person(name, age) if age < 18 => s"$name is a minor"
  case _ => "something else"
}

// Case class pattern matching
case class Order(id: Int, amount: Double, status: String)

def processOrder(order: Order): String = order match {
  case Order(id, amount, "completed") if amount > 1000 =>
    s"High value completed order $id"
  case Order(_, _, "pending") =>
    "Order is pending"
  case Order(id, _, "cancelled") =>
    s"Order $id was cancelled"
}

// Extractor patterns
object HighValueOrder {
  def unapply(order: Order): Option[(Int, Double)] = {
    if (order.amount > 1000) Some((order.id, order.amount))
    else None
  }
}

val order = Order(123, 1500.0, "completed")
order match {
  case HighValueOrder(id, amount) => println(s"Process high value order $id: $$$amount")
  case _ => println("Regular order")
}
```

### 10. How do you handle errors in Scala?
**Answer:** Scala provides several mechanisms for error handling:

**Option for nullable values:**
```scala
def findUser(id: Int): Option[User] = {
  // Database lookup
  if (id > 0) Some(User(id, "John")) else None
}

// Usage
findUser(123) match {
  case Some(user) => println(s"Found: ${user.name}")
  case None => println("User not found")
}

// With for comprehensions
def getUserName(id: Int): Option[String] = {
  for {
    user <- findUser(id)
    name = user.name.toUpperCase
    if name.startsWith("J")
  } yield name
}
```

**Either for errors:**
```scala
def validateEmail(email: String): Either[String, String] = {
  if (email.contains("@")) Right(email.toLowerCase)
  else Left("Invalid email format")
}

def processUser(email: String): Either[String, User] = {
  validateEmail(email).map(validEmail => User(validEmail))
}

// Usage
processUser("john@example.com") match {
  case Right(user) => println(s"Created user: ${user.email}")
  case Left(error) => println(s"Error: $error")
}
```

**Try for exceptions:**
```scala
import scala.util.{Try, Success, Failure}

def parseInt(s: String): Try[Int] = Try(s.toInt)

def divide(a: Int, b: Int): Try[Int] = {
  Try {
    if (b == 0) throw new IllegalArgumentException("Division by zero")
    else a / b
  }
}

// Usage
parseInt("123") match {
  case Success(value) => println(s"Parsed: $value")
  case Failure(ex) => println(s"Parse error: ${ex.getMessage}")
}
```

## Advanced Level Questions

### 11. How do you optimize pandas performance for large datasets?
**Answer:**

**Memory Optimization:**
```python
# Use appropriate data types
df = pd.read_csv('data.csv', dtype={
    'id': 'int32',        # Smaller than int64
    'category': 'category',  # Categorical for repeated strings
    'flag': 'bool'        # Boolean instead of object
})

# Downcast numeric types
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')
df['float_col'] = pd.to_numeric(df['float_col'], downcast='float')

# Use chunks for large files
def process_large_file(file_path: str, chunk_size: int = 100000):
    results = []
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        processed_chunk = transform_chunk(chunk)
        results.append(processed_chunk)
    return pd.concat(results, ignore_index=True)
```

**Performance Optimization:**
```python
# Vectorized operations (fast)
df['total'] = df['price'] * df['quantity']

# Avoid loops (slow)
# DON'T DO THIS:
# for idx, row in df.iterrows():
#     df.loc[idx, 'total'] = row['price'] * row['quantity']

# Use apply only when necessary
df['category'] = df['score'].apply(lambda x:
    'High' if x > 0.8 else 'Medium' if x > 0.5 else 'Low')

# Efficient filtering
mask = (df['status'] == 'active') & (df['amount'] > 100)
filtered_df = df[mask]

# Use eval for complex operations
df.eval('profit = revenue - cost', inplace=True)
```

**Parallel Processing:**
```python
from multiprocessing import Pool
import pandas as pd

def process_chunk(chunk):
    # Process chunk logic
    return chunk.groupby('category')['amount'].sum()

def parallel_process(df, num_partitions=4):
    df_split = np.array_split(df, num_partitions)
    with Pool(num_partitions) as pool:
        results = pool.map(process_chunk, df_split)
    return pd.concat(results)
```

### 12. Explain functional programming concepts in Scala for data engineering.
**Answer:**

**Immutability:**
```scala
// Immutable collections
val numbers = List(1, 2, 3, 4, 5)

// Transformations return new collections
val doubled = numbers.map(_ * 2)      // List(2, 4, 6, 8, 10)
val filtered = numbers.filter(_ > 3)  // List(4, 5)
val sum = numbers.reduce(_ + _)       // 15

// Original list unchanged
println(numbers)  // List(1, 2, 3, 4, 5)
```

**Higher-order functions:**
```scala
// Functions that take functions as parameters
def processData(data: List[Int], func: Int => Int): List[Int] = {
  data.map(func)
}

val data = List(1, 2, 3, 4, 5)
val doubled = processData(data, _ * 2)
val squared = processData(data, x => x * x)

// Currying
def add(x: Int)(y: Int): Int = x + y
val add5 = add(5)  // Partially applied function
val result = add5(3)  // 8
```

**Function composition:**
```scala
// Compose functions
def double(x: Int): Int = x * 2
def increment(x: Int): Int = x + 1

val doubleThenIncrement = double _ andThen increment  // 2x + 1
val incrementThenDouble = increment _ andThen double  // 2(x + 1)

val result1 = doubleThenIncrement(5)  // 11
val result2 = incrementThenDouble(5)  // 12
```

**For comprehensions:**
```scala
case class Employee(name: String, dept: String, salary: Int)

val employees = List(
  Employee("Alice", "Engineering", 100000),
  Employee("Bob", "Sales", 80000),
  Employee("Charlie", "Engineering", 120000)
)

// Complex queries with for comprehensions
val highPaidEngineers = for {
  emp <- employees
  if emp.dept == "Engineering"
  if emp.salary > 110000
} yield emp.name

// Equivalent to:
val highPaidEngineers2 = employees
  .filter(_.dept == "Engineering")
  .filter(_.salary > 110000)
  .map(_.name)
```

### 13. How do you implement a robust ETL pipeline in Python?
**Answer:** Building a production-ready ETL pipeline:

```python
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager
import pandas as pd
from sqlalchemy import create_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineConfig:
    source_table: str
    target_table: str
    batch_size: int = 10000
    retry_count: int = 3

class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._engine = None

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_engine(self.connection_string)
        return self._engine

    @contextmanager
    def get_connection(self):
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

class ETLPipeline:
    def __init__(self, config: PipelineConfig, db: DatabaseConnection):
        self.config = config
        self.db = db
        self.logger = logging.getLogger(__name__)

    def extract(self) -> pd.DataFrame:
        """Extract data from source"""
        query = f"SELECT * FROM {self.config.source_table}"
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql(query, conn)
            self.logger.info(f"Extracted {len(df)} records from {self.config.source_table}")
            return df
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate data quality"""
        # Check for required columns
        required_cols = ['id', 'amount', 'date']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Check data types
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'])

        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['id'])
        if len(df) < initial_count:
            self.logger.warning(f"Removed {initial_count - len(df)} duplicate records")

        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data"""
        df = df.copy()

        # Add derived columns
        df['month'] = df['date'].dt.to_period('M')
        df['amount_category'] = pd.cut(df['amount'],
                                     bins=[0, 100, 1000, float('inf')],
                                     labels=['Small', 'Medium', 'Large'])

        # Data enrichment
        df['processed_at'] = pd.Timestamp.now()
        df['batch_id'] = hash(str(df['date'].min()) + str(df['date'].max()))

        return df

    def load(self, df: pd.DataFrame) -> None:
        """Load data to target table"""
        try:
            with self.db.get_connection() as conn:
                df.to_sql(
                    self.config.target_table,
                    conn,
                    if_exists='append',
                    index=False,
                    chunksize=self.config.batch_size
                )
            self.logger.info(f"Loaded {len(df)} records to {self.config.target_table}")
        except Exception as e:
            self.logger.error(f"Loading failed: {e}")
            raise

    def run(self) -> bool:
        """Run the complete ETL pipeline"""
        try:
            # Extract
            raw_data = self.extract()

            # Validate
            validated_data = self.validate(raw_data)

            # Transform
            transformed_data = self.transform(validated_data)

            # Load
            self.load(transformed_data)

            self.logger.info("ETL pipeline completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"ETL pipeline failed: {e}")
            return False

# Usage
config = PipelineConfig(
    source_table="raw_orders",
    target_table="processed_orders",
    batch_size=5000
)

db = DatabaseConnection("postgresql://user:pass@localhost/db")
pipeline = ETLPipeline(config, db)

success = pipeline.run()
if not success:
    # Handle failure - send alerts, retry, etc.
    pass
```

### 14. How do you implement type-safe data processing in Scala?
**Answer:** Using Scala's type system for data engineering:

```scala
// Define domain models
sealed trait OrderStatus
case object Pending extends OrderStatus
case object Completed extends OrderStatus
case object Cancelled extends OrderStatus

case class Customer(id: Int, name: String, email: String)
case class Order(id: Int, customerId: Int, amount: BigDecimal, status: OrderStatus, date: LocalDate)

case class ValidationError(field: String, message: String)
case class ValidatedOrder(order: Order)

// Type-safe validation
def validateOrder(order: Order): Either[List[ValidationError], ValidatedOrder] = {
  val errors = List(
    if (order.amount <= 0) Some(ValidationError("amount", "Amount must be positive")) else None,
    if (order.customerId <= 0) Some(ValidationError("customerId", "Invalid customer ID")) else None,
    if (!order.email.contains("@")) Some(ValidationError("email", "Invalid email format")) else None
  ).flatten

  if (errors.isEmpty) Right(ValidatedOrder(order))
  else Left(errors)
}

// Type-safe transformations
def enrichOrder(order: Order, customer: Option[Customer]): Either[String, EnrichedOrder] = {
  customer match {
    case Some(cust) => Right(EnrichedOrder(order, cust))
    case None => Left(s"Customer not found for order ${order.id}")
  }
}

// Type-safe aggregation
case class OrderSummary(
  totalOrders: Int,
  totalAmount: BigDecimal,
  averageAmount: BigDecimal,
  statusBreakdown: Map[OrderStatus, Int]
)

def calculateSummary(orders: List[Order]): OrderSummary = {
  val totalOrders = orders.length
  val totalAmount = orders.map(_.amount).sum
  val averageAmount = if (totalOrders > 0) totalAmount / totalOrders else BigDecimal(0)
  val statusBreakdown = orders.groupBy(_.status).mapValues(_.length)

  OrderSummary(totalOrders, totalAmount, averageAmount, statusBreakdown)
}

// Type-safe data processing pipeline
def processOrders(rawOrders: List[Order], customers: Map[Int, Customer])
    : (List[ValidatedOrder], List[String]) = {

  val (validOrders, errors) = rawOrders.map { order =>
    for {
      validated <- validateOrder(order)
      customer = customers.get(order.customerId)
      enriched <- enrichOrder(validated.order, customer)
    } yield enriched
  }.partition(_.isRight)

  val successful = validOrders.collect { case Right(order) => ValidatedOrder(order) }
  val failures = errors.collect { case Left(error) => error }

  (successful, failures)
}
```

### 15. Explain advanced pandas techniques for data engineering.
**Answer:**

**Method Chaining:**
```python
# Fluent API with method chaining
result = (df
    .query('status == "active" and amount > 0')
    .assign(
        total_cost=lambda x: x['base_cost'] + x['tax'],
        profit_margin=lambda x: (x['revenue'] - x['total_cost']) / x['revenue']
    )
    .groupby(['category', 'month'])
    .agg({
        'revenue': 'sum',
        'total_cost': 'sum',
        'profit_margin': 'mean'
    })
    .round(2)
    .reset_index()
    .sort_values(['category', 'revenue'], ascending=[True, False])
)
```

**Advanced Window Functions:**
```python
# Rolling statistics
df['rolling_avg_7d'] = df.groupby('product')['sales'].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)

# Expanding statistics
df['cumulative_sales'] = df.groupby('product')['sales'].expanding().sum()

# Rank within groups
df['sales_rank'] = df.groupby('category')['sales'].rank(method='dense', ascending=False)

# Lag/Lead operations
df['prev_month_sales'] = df.groupby('product')['sales'].shift(1)
df['next_month_sales'] = df.groupby('product')['sales'].shift(-1)
df['sales_change'] = (df['sales'] - df['prev_month_sales']) / df['prev_month_sales']
```

**Memory-efficient Operations:**
```python
# Process large files in chunks with progress tracking
from tqdm import tqdm

def process_large_csv(file_path: str, chunk_size: int = 100000):
    results = []
    total_rows = sum(1 for _ in open(file_path)) - 1  # Skip header

    with tqdm(total=total_rows, desc="Processing") as pbar:
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            processed_chunk = (chunk
                .pipe(clean_data)
                .pipe(enrich_data)
                .pipe(validate_data)
            )
            results.append(processed_chunk)
            pbar.update(len(chunk))

    return pd.concat(results, ignore_index=True)

# Custom pipe functions
def clean_data(df):
    return (df
        .dropna(subset=['required_col'])
        .assign(date=lambda x: pd.to_datetime(x['date']))
    )

def enrich_data(df):
    return (df
        .assign(month=lambda x: x['date'].dt.month)
        .assign(amount_category=lambda x: pd.cut(x['amount'],
            bins=[0, 100, 1000, np.inf],
            labels=['Small', 'Medium', 'Large']))
    )

def validate_data(df):
    # Validation logic
    return df
```

**Performance Monitoring:**
```python
import time
import psutil
import os

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.start_memory = None

    def start(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

    def report(self, operation_name: str):
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        duration = end_time - self.start_time
        memory_used = end_memory - self.start_memory

        print(f"{operation_name}:")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Memory used: {memory_used:.2f} MB")
        print(f"  Memory peak: {end_memory:.2f} MB")

# Usage
monitor = PerformanceMonitor()
monitor.start()

df = pd.read_csv('large_file.csv')
df = df.groupby('category').agg({'amount': 'sum'})

monitor.report("Data processing")
```

## Scenario-Based Questions

### 16. How would you design a real-time data pipeline using Python?
**Answer:** Designing a real-time analytics pipeline:

```python
from kafka import KafkaConsumer, KafkaProducer
import json
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
from collections import defaultdict

class RealTimeAnalyticsPipeline:
    def __init__(self, kafka_bootstrap_servers: str):
        self.consumer = KafkaConsumer(
            'user-events',
            bootstrap_servers=kafka_bootstrap_servers,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

        # In-memory aggregations
        self.hourly_stats = defaultdict(lambda: defaultdict(int))
        self.daily_totals = defaultdict(int)

        # Start background processor
        self.processor_thread = threading.Thread(target=self._process_aggregations)
        self.processor_thread.daemon = True
        self.processor_thread.start()

    def consume_events(self):
        """Consume and process events in real-time"""
        batch = []
        batch_start = time.time()

        for message in self.consumer:
            event = message.value
            batch.append(event)

            # Process in micro-batches
            if len(batch) >= 100 or (time.time() - batch_start) >= 1.0:
                self._process_batch(batch)
                batch = []
                batch_start = time.time()

    def _process_batch(self, batch: list):
        """Process a batch of events"""
        if not batch:
            return

        df = pd.DataFrame(batch)

        # Real-time transformations
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.floor('H')

        # Update aggregations
        for _, row in df.iterrows():
            hour_key = row['hour'].isoformat()
            event_type = row['event_type']

            self.hourly_stats[hour_key][event_type] += 1
            self.daily_totals[event_type] += 1

        # Publish enriched events
        enriched_events = self._enrich_events(df)
        for event in enriched_events.to_dict('records'):
            self.producer.send('enriched-events', event)

    def _enrich_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich events with additional data"""
        # Add user demographics (mock)
        user_demographics = {
            'user123': {'age_group': '25-34', 'location': 'US'},
            'user456': {'age_group': '35-44', 'location': 'EU'}
        }

        df['age_group'] = df['user_id'].map(lambda x: user_demographics.get(x, {}).get('age_group', 'Unknown'))
        df['location'] = df['user_id'].map(lambda x: user_demographics.get(x, {}).get('location', 'Unknown'))

        return df

    def _process_aggregations(self):
        """Background process for aggregations"""
        while True:
            time.sleep(300)  # Every 5 minutes

            # Publish hourly stats
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)

            for hour_str, stats in self.hourly_stats.items():
                hour = datetime.fromisoformat(hour_str)
                if hour < current_hour:
                    # Publish to Kafka
                    stat_event = {
                        'hour': hour_str,
                        'stats': dict(stats),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.producer.send('hourly-stats', stat_event)

                    # Clean up old data
                    del self.hourly_stats[hour_str]

    def get_current_stats(self):
        """Get current statistics"""
        return {
            'hourly': dict(self.hourly_stats),
            'daily_totals': dict(self.daily_totals)
        }

# Usage
pipeline = RealTimeAnalyticsPipeline('localhost:9092')

# Start consuming in a separate thread
consumer_thread = threading.Thread(target=pipeline.consume_events)
consumer_thread.daemon = True
consumer_thread.start()

# Monitor stats
while True:
    time.sleep(60)
    stats = pipeline.get_current_stats()
    print(f"Current stats: {stats}")
```

### 17. How do you implement data lineage tracking in Scala?
**Answer:** Implementing data lineage for auditability:

```scala
import scala.collection.mutable
import java.time.LocalDateTime

// Data lineage model
case class DataSource(id: String, name: String, sourceType: String)
case class Transformation(id: String, name: String, inputs: List[String], operation: String)
case class DataArtifact(id: String, name: String, schema: Map[String, String])

case class LineageNode(
  id: String,
  nodeType: String,  // "source", "transformation", "artifact"
  name: String,
  inputs: List[String] = Nil,
  outputs: List[String] = Nil,
  metadata: Map[String, String] = Map.empty,
  timestamp: LocalDateTime = LocalDateTime.now()
)

class DataLineageTracker {
  private val nodes = mutable.Map[String, LineageNode]()
  private val graph = mutable.Map[String, List[String]]()  // node -> downstream nodes

  def addSource(source: DataSource): Unit = {
    val node = LineageNode(
      id = source.id,
      nodeType = "source",
      name = source.name,
      metadata = Map("type" -> source.sourceType)
    )
    nodes(source.id) = node
  }

  def addTransformation(transformation: Transformation): Unit = {
    val node = LineageNode(
      id = transformation.id,
      nodeType = "transformation",
      name = transformation.name,
      inputs = transformation.inputs,
      metadata = Map("operation" -> transformation.operation)
    )
    nodes(transformation.id) = node

    // Update graph
    transformation.inputs.foreach { inputId =>
      val downstream = graph.getOrElse(inputId, Nil)
      graph(inputId) = transformation.id :: downstream
    }
  }

  def addArtifact(artifact: DataArtifact): Unit = {
    val node = LineageNode(
      id = artifact.id,
      nodeType = "artifact",
      name = artifact.name,
      metadata = artifact.schema.map { case (k, v) => s"schema.$k" -> v }
    )
    nodes(artifact.id) = node
  }

  def recordDataFlow(fromId: String, toId: String): Unit = {
    nodes.get(fromId).foreach { fromNode =>
      val updatedFrom = fromNode.copy(outputs = toId :: fromNode.outputs)
      nodes(fromId) = updatedFrom
    }

    nodes.get(toId).foreach { toNode =>
      val updatedTo = toNode.copy(inputs = fromId :: toNode.inputs)
      nodes(toId) = updatedTo
    }

    val downstream = graph.getOrElse(fromId, Nil)
    graph(fromId) = toId :: downstream
  }

  def getLineage(nodeId: String): List[LineageNode] = {
    def traverseUpstream(currentId: String, visited: Set[String] = Set.empty): List[LineageNode] = {
      if (visited.contains(currentId)) return Nil

      nodes.get(currentId) match {
        case Some(node) =>
          val upstreamNodes = node.inputs.flatMap(inputId =>
            traverseUpstream(inputId, visited + currentId)
          )
          upstreamNodes :+ node
        case None => Nil
      }
    }

    traverseUpstream(nodeId)
  }

  def getDownstreamLineage(nodeId: String): List[LineageNode] = {
    def traverseDownstream(currentId: String, visited: Set[String] = Set.empty): List[LineageNode] = {
      if (visited.contains(currentId)) return Nil

      nodes.get(currentId) match {
        case Some(node) =>
          node :: graph.getOrElse(currentId, Nil).flatMap(downstreamId =>
            traverseDownstream(downstreamId, visited + currentId)
          )
        case None => Nil
      }
    }

    traverseDownstream(nodeId).distinct
  }

  def exportLineage(): String = {
    val lineageJson = nodes.values.map { node =>
      s"""{
         |  "id": "${node.id}",
         |  "type": "${node.nodeType}",
         |  "name": "${node.name}",
         |  "inputs": ${node.inputs.mkString("[\"", "\", \"", "\"]")},
         |  "outputs": ${node.outputs.mkString("[\"", "\", \"", "\"]")},
         |  "timestamp": "${node.timestamp}"
         |}""".stripMargin
    }.mkString("[", ",", "]")

    s"""{"lineage": $lineageJson}"""
  }
}

// Usage example
val tracker = new DataLineageTracker()

// Add sources
tracker.addSource(DataSource("src1", "customer_data", "database"))
tracker.addSource(DataSource("src2", "order_data", "api"))

// Add transformations
tracker.addTransformation(Transformation(
  id = "trans1",
  name = "join_customer_order",
  inputs = List("src1", "src2"),
  operation = "inner_join"
))

tracker.addTransformation(Transformation(
  id = "trans2",
  name = "calculate_metrics",
  inputs = List("trans1"),
  operation = "aggregation"
))

// Add artifacts
tracker.addArtifact(DataArtifact(
  id = "art1",
  name = "customer_order_summary",
  schema = Map("customer_id" -> "string", "total_orders" -> "integer", "total_amount" -> "decimal")
))

// Record data flows
tracker.recordDataFlow("src1", "trans1")
tracker.recordDataFlow("src2", "trans1")
tracker.recordDataFlow("trans1", "trans2")
tracker.recordDataFlow("trans2", "art1")

// Query lineage
val upstreamLineage = tracker.getLineage("art1")
val downstreamLineage = tracker.getDownstreamLineage("src1")

println(s"Upstream lineage for art1: ${upstreamLineage.map(_.name)}")
println(s"Downstream lineage for src1: ${downstreamLineage.map(_.name)}")
```

## Summary

Python and Scala interview questions for data engineering cover:

- **Python Focus**: pandas operations, ETL frameworks (Airflow), data validation, performance optimization
- **Scala Focus**: Functional programming, type safety, pattern matching, Spark integration
- **Common Themes**: Data processing patterns, error handling, performance optimization, production readiness

Key areas to master:
- **Data Structures**: DataFrames, RDDs, collections
- **ETL Patterns**: Extract, transform, load with error handling
- **Performance**: Vectorization, caching, parallel processing
- **Quality**: Validation, testing, monitoring
- **Architecture**: Pipeline design, lineage tracking, real-time processing

Understanding both languages enables building robust, scalable data engineering solutions that leverage the strengths of each ecosystem.
