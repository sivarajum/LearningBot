# Databricks - Complete Guide (Basic to Advanced)

## 🎯 What is Databricks?

**Databricks** is a unified analytics platform built on Apache Spark. It provides a collaborative environment for data engineering, data science, and ML.

### Why Databricks?
- **Unified Platform**: Data engineering + ML in one place
- **Optimized Spark**: Faster than open-source Spark
- **Collaborative**: Team collaboration features
- **MLflow Integration**: Built-in ML lifecycle
- **Lakehouse**: Data lake + data warehouse

---

## 📚 Learning Path: Basic → Intermediate → Advanced

---

## 🟢 LEVEL 1: BASIC (Getting Started)

### Basic Usage

```python
# Databricks notebooks (similar to Jupyter)
# Read data
df = spark.read.parquet("/mnt/data/raw/")

# Process
result = df.filter(df.amount > 100) \
    .groupBy("region") \
    .agg({"amount": "sum"})

# Write
result.write.parquet("/mnt/data/processed/")
```

### Key Features

#### 1. **Notebooks**
- Collaborative notebooks
- Multiple languages (Python, SQL, Scala, R)
- Version control

#### 2. **Delta Lake**
- ACID transactions
- Time travel
- Schema evolution

#### 3. **Unity Catalog**
- Data governance
- Centralized metadata
- Access control

#### 4. **MLflow Integration**
- Built-in experiment tracking
- Model registry
- Model serving

---

## 🟡 LEVEL 2: INTERMEDIATE (Production Patterns)

### Delta Lake

```python
# Write as Delta
df.write.format("delta").save("/mnt/data/delta/")

# Read Delta
df = spark.read.format("delta").load("/mnt/data/delta/")

# Time travel
df = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("/mnt/data/delta/")

# Update Delta
from delta.tables import DeltaTable
delta_table = DeltaTable.forPath(spark, "/mnt/data/delta/")
delta_table.update("amount < 0", {"amount": 0})
```

### Jobs and Workflows

```python
# Create job
job = {
    "name": "ETL Job",
    "tasks": [{
        "task_key": "etl_task",
        "spark_python_task": {
            "python_file": "dbfs:/jobs/etl.py"
        }
    }]
}
```

---

## 🔴 LEVEL 3: ADVANCED (Production Excellence)

### MLflow Integration

```python
import mlflow

# Track experiment
with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    model = train_model()
    mlflow.sklearn.log_model(model, "model")
```

### Unity Catalog

```python
# Create catalog
spark.sql("CREATE CATALOG IF NOT EXISTS production")

# Create schema
spark.sql("CREATE SCHEMA IF NOT EXISTS production.sales")

# Create table
spark.sql("""
    CREATE TABLE production.sales.transactions
    USING DELTA
    LOCATION '/mnt/data/delta/transactions'
""")
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Lakehouse
```
Data Lake (Delta) → Databricks → Analytics + ML
```

### Pattern 2: ETL Pipeline
```
Raw Data → Databricks (ETL) → Delta Lake → Analytics
```

---

## 📊 Best Practices

### 1. **Use Delta Lake**
- ACID transactions
- Better performance
- Time travel

### 2. **Unity Catalog**
- Centralized governance
- Access control
- Metadata management

### 3. **Cluster Management**
- Auto-scaling
- Right-sizing
- Spot instances

---

## 🎯 Key Takeaways

1. **Databricks = Unified Analytics Platform**
2. **Delta Lake = ACID Data Lake**
3. **Unity Catalog = Data Governance**
4. **MLflow = ML Lifecycle**
5. **Optimized Spark = Better Performance**

---

## 📚 Next Steps

1. ✅ Read this guide
2. 📊 Review `Visual.md` for flows
3. 💬 Practice `Interview.md` questions
4. 🏗️ Build with Databricks
5. 🎯 Explain it confidently

