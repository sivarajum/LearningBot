# Data Modeling Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **ER Diagrams**
```sql
-- Entities
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

### 2. **Normalization**
```sql
-- 1NF: Atomic values
-- 2NF: Remove partial dependencies
-- 3NF: Remove transitive dependencies
```

### 3. **Dimensional Modeling**
```sql
-- Fact table
CREATE TABLE sales_fact (
    sale_id INT,
    date_id INT,
    product_id INT,
    customer_id INT,
    amount DECIMAL
);

-- Dimension table
CREATE TABLE date_dim (
    date_id INT PRIMARY KEY,
    date DATE,
    year INT,
    month INT,
    day INT
);
```

## Level 2 – Production Patterns

### Star Schema
```sql
-- Central fact table
-- Multiple dimension tables
-- Denormalized for performance
```

### Snowflake Schema
```sql
-- Normalized dimensions
-- Better for storage
-- More complex queries
```

## Level 3 – Architect Playbook

### Data Vault
```sql
-- Hub
CREATE TABLE hub_customer (
    customer_hk VARCHAR(50) PRIMARY KEY,
    load_date TIMESTAMP
);

-- Satellite
CREATE TABLE sat_customer (
    customer_hk VARCHAR(50),
    load_date TIMESTAMP,
    name VARCHAR(100),
    email VARCHAR(100)
);
```

## Ops Cheat Sheet

| Task | Tool | Notes |
| --- | --- | --- |
| Design | ER/Studio, draw.io | Design models |
| Validate | Database constraints | Ensure integrity |
| Document | Data dictionary | Document schema |

## Checklist Before Production

- [ ] Design proper ER diagrams
- [ ] Normalize appropriately
- [ ] Choose schema type (star/snowflake)
- [ ] Set up proper indexing
- [ ] Document data model
- [ ] Validate relationships
- [ ] Optimize for queries
- [ ] Set up version control
