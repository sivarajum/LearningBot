# SQL for Data Engineering Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Basic Queries**
```sql
-- Select
SELECT name, age FROM users WHERE age > 25;

-- Join
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id;

-- Aggregation
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department;
```

### 2. **Window Functions**
```sql
SELECT 
    name,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employees;
```

### 3. **CTEs**
```sql
WITH ranked_sales AS (
    SELECT 
        region,
        sales,
        RANK() OVER (ORDER BY sales DESC) as rank
    FROM sales_data
)
SELECT * FROM ranked_sales WHERE rank <= 10;
```

## Level 2 – Production Patterns

### Data Quality Checks
```sql
-- Check for duplicates
SELECT id, COUNT(*) as count
FROM table
GROUP BY id
HAVING COUNT(*) > 1;

-- Check for nulls
SELECT COUNT(*) as null_count
FROM table
WHERE important_column IS NULL;
```

### Incremental Loads
```sql
-- Insert only new records
INSERT INTO target_table
SELECT * FROM source_table s
WHERE NOT EXISTS (
    SELECT 1 FROM target_table t
    WHERE t.id = s.id
);
```

## Level 3 – Architect Playbook

### Complex Transformations
```sql
-- Pivot
SELECT 
    region,
    SUM(CASE WHEN month = 'Jan' THEN sales END) as jan_sales,
    SUM(CASE WHEN month = 'Feb' THEN sales END) as feb_sales
FROM sales
GROUP BY region;
```

## Ops Cheat Sheet

| Task | SQL | Notes |
| --- | --- | --- |
| Create table | `CREATE TABLE ...` | Create table |
| Index | `CREATE INDEX ...` | Create index |
| Explain | `EXPLAIN SELECT ...` | View plan |
| Vacuum | `VACUUM table` | Optimize |

## Checklist Before Production

- [ ] Optimize queries with indexes
- [ ] Implement proper data validation
- [ ] Set up incremental loading
- [ ] Optimize joins
- [ ] Set up monitoring
- [ ] Implement proper error handling
- [ ] Document queries
- [ ] Test performance
