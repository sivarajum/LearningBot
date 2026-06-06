# Data Warehousing Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Star Schema**
```sql
-- Fact table
CREATE TABLE sales_fact (
    sale_id INT,
    date_id INT,
    product_id INT,
    customer_id INT,
    amount DECIMAL
);

-- Dimension tables
CREATE TABLE date_dim (
    date_id INT PRIMARY KEY,
    date DATE,
    year INT,
    month INT
);

CREATE TABLE product_dim (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50)
);
```

### 2. **ETL Process**
```sql
-- Extract from source
-- Transform (clean, aggregate)
-- Load to warehouse
```

## Level 2 – Production Patterns

### Modern Data Warehouse
```python
# Snowflake
# BigQuery
# Redshift
# All support SQL, cloud-native, scalable
```

### Data Lake Integration
```sql
-- Query external data
SELECT * FROM EXTERNAL TABLE (
    LOCATION='s3://bucket/data/',
    FORMAT='PARQUET'
)
```

## Level 3 – Architect Playbook

### Lakehouse Architecture
```python
# Combine data lake and warehouse
# Delta Lake for ACID transactions
# Query with SQL
# Support for ML workloads
```

## Ops Cheat Sheet

| Task | Tool | Notes |
| --- | --- | --- |
| Design | Kimball methodology | Design schema |
| Load | ETL tools | Load data |
| Query | SQL | Query warehouse |

## Checklist Before Production

- [ ] Design proper schema
- [ ] Set up ETL processes
- [ ] Configure partitioning
- [ ] Set up monitoring
- [ ] Implement proper security
- [ ] Optimize queries
- [ ] Set up backup
- [ ] Document architecture
