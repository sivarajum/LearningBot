# PostgreSQL Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install PostgreSQL
# macOS: brew install postgresql
# Linux: apt-get install postgresql

# Start service
sudo service postgresql start

# Connect
psql -U postgres
```

### 2. **Basic Operations**
```sql
-- Create database
CREATE DATABASE mydb;

-- Create table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

-- Insert
INSERT INTO users (name, email) VALUES ('John', 'john@example.com');

-- Query
SELECT * FROM users WHERE id = 1;
```

### 3. **Python Integration**
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="password"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
```

## Level 2 – Production Patterns

### Advanced Features
```sql
-- JSON support
CREATE TABLE data (
    id SERIAL PRIMARY KEY,
    metadata JSONB
);

-- Arrays
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    tags TEXT[]
);

-- Full-text search
CREATE INDEX idx_search ON documents USING gin(to_tsvector('english', content));
```

### Performance
```sql
-- Indexes
CREATE INDEX idx_email ON users(email);

-- Explain
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'john@example.com';

-- Vacuum
VACUUM ANALYZE users;
```

## Level 3 – Architect Playbook

### Replication
```sql
-- Master
-- postgresql.conf
wal_level = replica
max_wal_senders = 3

-- Replica
-- recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=master port=5432 user=replicator'
```

### Partitioning
```sql
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE,
    amount DECIMAL
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2024_01 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Connect | `psql -U user -d database` | Connect to DB |
| Backup | `pg_dump database > backup.sql` | Backup database |
| Restore | `psql database < backup.sql` | Restore database |
| Vacuum | `VACUUM ANALYZE table` | Optimize table |

## Checklist Before Production

- [ ] Set up proper indexing
- [ ] Configure connection pooling
- [ ] Set up replication
- [ ] Configure backup strategy
- [ ] Set up monitoring
- [ ] Implement proper security
- [ ] Optimize queries
- [ ] Set up partitioning if needed
