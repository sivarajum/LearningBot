# SQLite Database Guide

## What is SQLite?

SQLite is a self-contained, serverless, zero-configuration, transactional SQL database engine. It's the most widely deployed database engine in the world, used in mobile devices, desktop applications, and embedded systems.

### Key Characteristics

- **Serverless**: No separate server process required
- **Zero-configuration**: No setup or administration needed
- **Transactional**: ACID-compliant transactions
- **Self-contained**: Single library with no dependencies
- **Cross-platform**: Works on all major operating systems
- **Public domain**: Free for any use
- **Small footprint**: Less than 500KB in size
- **Reliable**: Extensive testing and production use

## Core Concepts

### Database Connection

```python
import sqlite3

# Create/connect to database
conn = sqlite3.connect('example.db')

# Connection with options
conn = sqlite3.connect(
    'example.db',
    timeout=5.0,              # Connection timeout
    isolation_level=None,     # Autocommit mode
    check_same_thread=False   # Allow multi-threading
)

# In-memory database
conn = sqlite3.connect(':memory:')

# Close connection
conn.close()
```

### Creating Tables

```python
import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Create employees table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT,
        salary REAL,
        hire_date DATE,
        is_active BOOLEAN DEFAULT 1
    )
''')

# Create departments table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        manager_id INTEGER,
        budget REAL,
        FOREIGN KEY (manager_id) REFERENCES employees (id)
    )
''')

# Create projects table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        start_date DATE,
        end_date DATE,
        budget REAL,
        department_id INTEGER,
        FOREIGN KEY (department_id) REFERENCES departments (id)
    )
''')

# Create employee_projects junction table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee_projects (
        employee_id INTEGER,
        project_id INTEGER,
        role TEXT,
        hours_allocated REAL,
        PRIMARY KEY (employee_id, project_id),
        FOREIGN KEY (employee_id) REFERENCES employees (id),
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
''')

conn.commit()
conn.close()
```

### Data Types

SQLite supports the following data types:

- **INTEGER**: Signed integer (1, 2, 3, 4, 6, or 8 bytes)
- **REAL**: Floating-point number (8-byte IEEE floating point)
- **TEXT**: Text string (UTF-8, UTF-16BE, or UTF-16LE)
- **BLOB**: Binary data
- **NUMERIC**: Special type for exact decimal arithmetic

```python
import sqlite3

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create table with various data types
cursor.execute('''
    CREATE TABLE data_types_demo (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        salary REAL,
        is_manager BOOLEAN,
        hire_date TEXT,  -- ISO 8601 format: YYYY-MM-DD
        profile_image BLOB,
        metadata TEXT   -- JSON string
    )
''')

# Insert sample data
cursor.execute('''
    INSERT INTO data_types_demo (name, age, salary, is_manager, hire_date, metadata)
    VALUES (?, ?, ?, ?, ?, ?)
''', (
    'John Doe',
    30,
    75000.50,
    True,
    '2023-01-15',
    '{"skills": ["Python", "SQL"], "location": "New York"}'
))

conn.commit()

# Query with type detection
cursor.execute('SELECT * FROM data_types_demo')
row = cursor.fetchone()

print(f"ID: {row[0]} (type: {type(row[0])})")
print(f"Name: {row[1]} (type: {type(row[1])})")
print(f"Age: {row[2]} (type: {type(row[2])})")
print(f"Salary: {row[3]} (type: {type(row[3])})")
print(f"Is Manager: {row[4]} (type: {type(row[4])})")

conn.close()
```

## CRUD Operations

### Create (INSERT)

```python
import sqlite3
from datetime import datetime

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Single row insert
cursor.execute('''
    INSERT INTO employees (first_name, last_name, email, department, salary, hire_date)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('John', 'Doe', 'john.doe@company.com', 'Engineering', 85000.00, '2023-01-15'))

# Multiple rows insert
employees_data = [
    ('Jane', 'Smith', 'jane.smith@company.com', 'Marketing', 65000.00, '2023-02-01'),
    ('Bob', 'Johnson', 'bob.johnson@company.com', 'Sales', 55000.00, '2023-03-10'),
    ('Alice', 'Brown', 'alice.brown@company.com', 'HR', 60000.00, '2023-01-20'),
]

cursor.executemany('''
    INSERT INTO employees (first_name, last_name, email, department, salary, hire_date)
    VALUES (?, ?, ?, ?, ?, ?)
''', employees_data)

# Insert with subquery
cursor.execute('''
    INSERT INTO departments (name, manager_id, budget)
    SELECT 'New Department', id, 100000.00
    FROM employees
    WHERE first_name = 'John' AND last_name = 'Doe'
''')

# Get last inserted row ID
last_id = cursor.lastrowid
print(f"Last inserted ID: {last_id}")

conn.commit()
conn.close()
```

### Read (SELECT)

```python
import sqlite3
import json

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Basic SELECT
cursor.execute('SELECT * FROM employees')
all_employees = cursor.fetchall()
print("All employees:")
for employee in all_employees:
    print(employee)

# SELECT with specific columns
cursor.execute('SELECT first_name, last_name, email FROM employees WHERE department = ?', ('Engineering',))
engineers = cursor.fetchall()
print("\nEngineers:")
for engineer in engineers:
    print(f"{engineer[0]} {engineer[1]} - {engineer[2]}")

# SELECT with JOIN
cursor.execute('''
    SELECT e.first_name, e.last_name, d.name as department_name
    FROM employees e
    LEFT JOIN departments d ON e.department = d.name
    ORDER BY e.last_name
''')
employee_departments = cursor.fetchall()
print("\nEmployees with departments:")
for emp in employee_departments:
    print(f"{emp[0]} {emp[1]} - {emp[2] or 'No Department'}")

# SELECT with aggregation
cursor.execute('''
    SELECT department, COUNT(*) as count, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department
    HAVING COUNT(*) > 1
    ORDER BY avg_salary DESC
''')
dept_stats = cursor.fetchall()
print("\nDepartment statistics:")
for stat in dept_stats:
    print(f"{stat[0]}: {stat[1]} employees, avg salary: ${stat[2]:.2f}")

# SELECT with LIMIT and OFFSET
cursor.execute('SELECT * FROM employees ORDER BY hire_date DESC LIMIT 5 OFFSET 0')
recent_hires = cursor.fetchall()
print("\nRecent hires:")
for hire in recent_hires:
    print(hire)

# Using row factory for named access
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT * FROM employees WHERE salary > ?', (70000,))
high_earners = cursor.fetchall()

print("\nHigh earners (named access):")
for earner in high_earners:
    print(f"{earner['first_name']} {earner['last_name']}: ${earner['salary']}")

conn.close()
```

### Update (UPDATE)

```python
import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Basic UPDATE
cursor.execute('''
    UPDATE employees
    SET salary = salary * 1.10
    WHERE department = ?
''', ('Engineering',))

print(f"Rows updated: {cursor.rowcount}")

# UPDATE with multiple conditions
cursor.execute('''
    UPDATE employees
    SET department = ?, salary = ?
    WHERE first_name = ? AND last_name = ?
''', ('Management', 95000.00, 'John', 'Doe'))

# UPDATE with subquery
cursor.execute('''
    UPDATE employees
    SET is_active = 0
    WHERE id IN (
        SELECT employee_id
        FROM employee_projects
        GROUP BY employee_id
        HAVING COUNT(*) = 0
    )
''')

# UPDATE with CASE statement
cursor.execute('''
    UPDATE employees
    SET salary = CASE
        WHEN department = 'Engineering' THEN salary * 1.15
        WHEN department = 'Sales' THEN salary * 1.10
        WHEN department = 'Marketing' THEN salary * 1.08
        ELSE salary * 1.05
    END
''')

conn.commit()
conn.close()
```

### Delete (DELETE)

```python
import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Basic DELETE
cursor.execute('DELETE FROM employees WHERE is_active = 0')
print(f"Inactive employees removed: {cursor.rowcount}")

# DELETE with subquery
cursor.execute('''
    DELETE FROM employee_projects
    WHERE project_id IN (
        SELECT id FROM projects WHERE end_date < date('now')
    )
''')

# DELETE with JOIN (using subquery)
cursor.execute('''
    DELETE FROM employees
    WHERE id IN (
        SELECT e.id
        FROM employees e
        LEFT JOIN employee_projects ep ON e.id = ep.employee_id
        WHERE ep.employee_id IS NULL
        AND e.hire_date < date('now', '-1 year')
    )
''')

# TRUNCATE equivalent (delete all rows)
cursor.execute('DELETE FROM employee_projects')

# Reset auto-increment counter
cursor.execute('DELETE FROM sqlite_sequence WHERE name = ?', ('employee_projects',))

conn.commit()
conn.close()
```

## Advanced Queries

### Window Functions

```python
import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# ROW_NUMBER()
cursor.execute('''
    SELECT
        first_name,
        last_name,
        department,
        salary,
        ROW_NUMBER() OVER (ORDER BY salary DESC) as salary_rank
    FROM employees
''')
ranked_employees = cursor.fetchall()
print("Employees ranked by salary:")
for emp in ranked_employees:
    print(f"{emp[3]}: {emp[0]} {emp[1]} (Rank {emp[4]})")

# RANK() and DENSE_RANK()
cursor.execute('''
    SELECT
        department,
        first_name,
        last_name,
        salary,
        RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank,
        DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dense_rank
    FROM employees
''')
dept_rankings = cursor.fetchall()
print("\nDepartment salary rankings:")
for emp in dept_rankings:
    print(f"{emp[0]}: {emp[1]} {emp[2]} - ${emp[3]} (Rank {emp[4]}, Dense {emp[5]})")

# LAG() and LEAD()
cursor.execute('''
    SELECT
        first_name,
        last_name,
        hire_date,
        salary,
        LAG(salary) OVER (ORDER BY hire_date) as prev_salary,
        LEAD(salary) OVER (ORDER BY hire_date) as next_salary
    FROM employees
    ORDER BY hire_date
''')
salary_progression = cursor.fetchall()
print("\nSalary progression by hire date:")
for emp in salary_progression:
    prev = f"${emp[4]}" if emp[4] else "N/A"
    next_ = f"${emp[5]}" if emp[5] else "N/A"
    print(f"{emp[0]} {emp[1]} ({emp[2]}): ${emp[3]} (Prev: {prev}, Next: {next_})")

conn.close()
```

### Common Table Expressions (CTEs)

```python
import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Recursive CTE for organizational hierarchy
cursor.execute('''
    WITH RECURSIVE employee_hierarchy AS (
        -- Base case: top-level employees (no manager)
        SELECT id, first_name, last_name, department, 0 as level, first_name || ' ' || last_name as path
        FROM employees
        WHERE id NOT IN (
            SELECT DISTINCT manager_id
            FROM departments
            WHERE manager_id IS NOT NULL
        )

        UNION ALL

        -- Recursive case: employees who report to someone
        SELECT e.id, e.first_name, e.last_name, e.department, eh.level + 1, eh.path || ' -> ' || e.first_name || ' ' || e.last_name
        FROM employees e
        JOIN departments d ON e.id = d.manager_id
        JOIN employee_hierarchy eh ON d.id = (
            SELECT id FROM departments WHERE manager_id = e.id LIMIT 1
        )
    )
    SELECT * FROM employee_hierarchy ORDER BY level, last_name
''')

hierarchy = cursor.fetchall()
print("Employee hierarchy:")
for emp in hierarchy:
    indent = "  " * emp[4]
    print(f"{indent}{emp[5]} (Level {emp[4]})")

# CTE for department statistics
cursor.execute('''
    WITH dept_stats AS (
        SELECT
            department,
            COUNT(*) as employee_count,
            AVG(salary) as avg_salary,
            MIN(salary) as min_salary,
            MAX(salary) as max_salary
        FROM employees
        GROUP BY department
    ),
    dept_projects AS (
        SELECT
            d.name as department,
            COUNT(p.id) as project_count,
            SUM(p.budget) as total_budget
        FROM departments d
        LEFT JOIN projects p ON d.id = p.department_id
        GROUP BY d.name
    )
    SELECT
        ds.department,
        ds.employee_count,
        ds.avg_salary,
        ds.min_salary,
        ds.max_salary,
        COALESCE(dp.project_count, 0) as project_count,
        COALESCE(dp.total_budget, 0) as total_budget
    FROM dept_stats ds
    LEFT JOIN dept_projects dp ON ds.department = dp.department
    ORDER BY ds.avg_salary DESC
''')

dept_report = cursor.fetchall()
print("\nDepartment report:")
for dept in dept_report:
    print(f"{dept[0]}: {dept[1]} employees, avg salary ${dept[2]:.2f}, {dept[5]} projects, total budget ${dept[6]:.2f}")

conn.close()
```

### Full-Text Search

```python
import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Create FTS5 virtual table
cursor.execute('''
    CREATE VIRTUAL TABLE employee_search USING fts5(
        first_name, last_name, email, department, description,
        content='employees',
        content_rowid='id'
    )
''')

# Populate FTS table
cursor.execute('''
    INSERT INTO employee_search(rowid, first_name, last_name, email, department, description)
    SELECT id, first_name, last_name, email, department,
           first_name || ' ' || last_name || ' ' || email || ' ' || COALESCE(department, '')
    FROM employees
''')

# Search queries
search_queries = [
    'john',           # Single term
    'engineering',    # Department search
    'john OR jane',   # OR search
    'engineer*',      # Prefix search
    '"john doe"',     # Phrase search
    'first_name:john', # Column-specific search
]

for query in search_queries:
    print(f"\nSearch: {query}")
    cursor.execute('''
        SELECT e.first_name, e.last_name, e.email, e.department, es.rank
        FROM employee_search es
        JOIN employees e ON es.rowid = e.id
        WHERE employee_search MATCH ?
        ORDER BY es.rank
    ''', (query,))

    results = cursor.fetchall()
    for result in results:
        print(f"  {result[0]} {result[1]} ({result[2]}) - {result[3]}")

# Highlight search terms
cursor.execute('''
    SELECT highlight(employee_search, 4, '<b>', '</b>') as highlighted
    FROM employee_search
    WHERE employee_search MATCH 'john'
''')

highlights = cursor.fetchall()
print("\nHighlighted results:")
for highlight in highlights:
    print(f"  {highlight[0]}")

conn.commit()
conn.close()
```

## Transactions and Concurrency

### Transaction Management

```python
import sqlite3

conn = sqlite3.connect('company.db')

# Automatic transaction (default)
cursor = conn.cursor()
cursor.execute('UPDATE employees SET salary = salary * 1.05')
conn.commit()  # Explicit commit

# Manual transaction control
conn.execute('BEGIN')

try:
    conn.execute('UPDATE employees SET salary = salary * 1.10 WHERE department = ?', ('Engineering',))
    conn.execute('UPDATE employees SET salary = salary * 1.05 WHERE department = ?', ('Sales',))

    # Check if everything looks good
    cursor = conn.execute('SELECT COUNT(*) FROM employees WHERE salary > 100000')
    high_earners = cursor.fetchone()[0]

    if high_earners > 5:
        raise Exception("Too many high earners!")

    conn.commit()
    print("Transaction committed successfully")

except Exception as e:
    conn.rollback()
    print(f"Transaction rolled back: {e}")

# Using context manager
with conn:
    conn.execute('INSERT INTO employees (first_name, last_name, email) VALUES (?, ?, ?)',
                ('Test', 'User', 'test@example.com'))

# This commit happens automatically if no exception

conn.close()
```

### Isolation Levels

```python
import sqlite3
import threading
import time

# SQLite supports different isolation levels through connection configuration

# Autocommit mode (isolation_level=None)
conn1 = sqlite3.connect('company.db', isolation_level=None)

# Deferred transactions (default)
conn2 = sqlite3.connect('company.db')  # isolation_level='' (deferred)

# Immediate transactions
conn3 = sqlite3.connect('company.db', isolation_level='IMMEDIATE')

# Exclusive transactions
conn4 = sqlite3.connect('company.db', isolation_level='EXCLUSIVE')

# Example of concurrent access
def worker(worker_id, isolation_level):
    conn = sqlite3.connect('company.db', isolation_level=isolation_level)
    cursor = conn.cursor()

    try:
        cursor.execute('BEGIN')
        cursor.execute('SELECT salary FROM employees WHERE id = 1')
        salary = cursor.fetchone()[0]

        time.sleep(0.1)  # Simulate work

        cursor.execute('UPDATE employees SET salary = ? WHERE id = 1', (salary + 100,))
        conn.commit()

        print(f"Worker {worker_id}: Updated salary to {salary + 100}")

    except sqlite3.OperationalError as e:
        print(f"Worker {worker_id}: {e}")
        conn.rollback()
    finally:
        conn.close()

# Test concurrent updates
threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(i+1, None))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Database Schema Management

### Schema Migrations

```python
import sqlite3
import os
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.migrations_dir = 'migrations'

    def init_migrations(self):
        """Initialize migrations table"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def create_migration(self, name):
        """Create a new migration file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{name}.sql"

        os.makedirs(self.migrations_dir, exist_ok=True)

        with open(os.path.join(self.migrations_dir, filename), 'w') as f:
            f.write(f"-- Migration: {name}\n")
            f.write(f"-- Created: {datetime.now()}\n\n")
            f.write("-- Add your SQL statements here\n")

        print(f"Created migration: {filename}")

    def apply_migrations(self):
        """Apply pending migrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get applied migrations
        cursor.execute('SELECT name FROM migrations')
        applied = {row[0] for row in cursor.fetchall()}

        # Get migration files
        if not os.path.exists(self.migrations_dir):
            return

        migration_files = sorted(os.listdir(self.migrations_dir))

        for filename in migration_files:
            if not filename.endswith('.sql'):
                continue

            if filename in applied:
                continue

            print(f"Applying migration: {filename}")

            with open(os.path.join(self.migrations_dir, filename), 'r') as f:
                sql = f.read()

            try:
                conn.executescript(sql)
                conn.execute('INSERT INTO migrations (name) VALUES (?)', (filename,))
                conn.commit()
                print(f"✓ Applied {filename}")
            except Exception as e:
                conn.rollback()
                print(f"✗ Failed to apply {filename}: {e}")
                break

        conn.close()

# Usage
migrator = DatabaseMigrator('company.db')
migrator.init_migrations()

# Create a new migration
migrator.create_migration('add_employee_status')

# Apply migrations
migrator.apply_migrations()
```

### Schema Introspection

```python
import sqlite3

def inspect_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("Database Schema:")
    print("=" * 50)

    for table_name, in tables:
        if table_name.startswith('sqlite_'):
            continue

        print(f"\nTable: {table_name}")
        print("-" * 30)

        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        print("Columns:")
        for col in columns:
            cid, name, type_, notnull, default, pk = col
            constraints = []
            if pk:
                constraints.append("PRIMARY KEY")
            if notnull:
                constraints.append("NOT NULL")
            if default is not None:
                constraints.append(f"DEFAULT {default}")

            constraint_str = " ".join(constraints)
            print(f"  {name} {type_} {constraint_str}".strip())

        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()

        if fks:
            print("Foreign Keys:")
            for fk in fks:
                id_, seq, table, from_col, to_col, on_update, on_delete, match = fk
                print(f"  {from_col} -> {table}.{to_col}")

        # Get indexes
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()

        if indexes:
            print("Indexes:")
            for idx in indexes:
                seq, name, unique, origin, partial = idx[:5]
                if not name.startswith('sqlite_'):
                    unique_str = "UNIQUE " if unique else ""
                    print(f"  {unique_str}INDEX {name}")

    conn.close()

# Inspect the database
inspect_database('company.db')
```

## Performance Optimization

### Indexing Strategies

```python
import sqlite3
import time

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Create indexes for better performance
indexes = [
    'CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department)',
    'CREATE INDEX IF NOT EXISTS idx_employees_salary ON employees(salary)',
    'CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees(hire_date)',
    'CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email)',
    'CREATE INDEX IF NOT EXISTS idx_projects_department_id ON projects(department_id)',
    'CREATE INDEX IF NOT EXISTS idx_employee_projects_employee_id ON employee_projects(employee_id)',
    'CREATE INDEX IF NOT EXISTS idx_employee_projects_project_id ON employee_projects(project_id)',
]

for index_sql in indexes:
    cursor.execute(index_sql)

conn.commit()

# Test query performance
def time_query(query, params=()):
    start_time = time.time()
    cursor.execute(query, params)
    results = cursor.fetchall()
    end_time = time.time()
    return results, end_time - start_time

# Test queries with and without indexes
queries = [
    ('SELECT * FROM employees WHERE department = ?', ('Engineering',)),
    ('SELECT * FROM employees WHERE salary > ?', (70000,)),
    ('SELECT * FROM employees WHERE hire_date > ?', ('2023-01-01',)),
    ('SELECT e.* FROM employees e JOIN departments d ON e.department = d.name WHERE d.budget > ?', (50000,)),
]

print("Query Performance Test:")
print("=" * 50)

for query, params in queries:
    results, duration = time_query(query, params)
    print(f"Query: {query}")
    print(f"Results: {len(results)} rows")
    print(f"Time: {duration:.4f} seconds")
    print()

conn.close()
```

### Query Optimization

```python
import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Enable query execution plan
cursor.execute('EXPLAIN QUERY PLAN SELECT * FROM employees WHERE department = ? AND salary > ?', ('Engineering', 70000))

plan = cursor.fetchall()
print("Query Execution Plan:")
for step in plan:
    print(f"  {step}")

# Analyze table statistics
cursor.execute('ANALYZE employees')
cursor.execute('ANALYZE departments')

# Get table statistics
cursor.execute("SELECT * FROM sqlite_stat1 WHERE tbl = 'employees'")
stats = cursor.fetchall()
print("\nTable Statistics:")
for stat in stats:
    print(f"  {stat}")

# Optimize with composite indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_dept_salary ON employees(department, salary)')

# Test optimized query
cursor.execute('EXPLAIN QUERY PLAN SELECT * FROM employees WHERE department = ? AND salary > ?', ('Engineering', 70000))

optimized_plan = cursor.fetchall()
print("\nOptimized Query Plan:")
for step in optimized_plan:
    print(f"  {step}")

conn.commit()
conn.close()
```

## Backup and Recovery

### Database Backup

```python
import sqlite3
import shutil
from datetime import datetime
import os

def backup_database(db_path, backup_dir='backups'):
    """Create a backup of the SQLite database"""
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)

    # SQLite backup using SQL
    conn = sqlite3.connect(db_path)
    backup_conn = sqlite3.connect(backup_path)

    with backup_conn:
        conn.backup(backup_conn)

    conn.close()
    backup_conn.close()

    print(f"Backup created: {backup_path}")
    return backup_path

def incremental_backup(db_path, last_backup_path, changes_only_dir='incremental'):
    """Create incremental backup (simplified)"""
    os.makedirs(changes_only_dir, exist_ok=True)

    # Get changes since last backup
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # This is a simplified example - in practice, you'd track changes more carefully
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]

    changes = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        changes[table] = count

    conn.close()

    # Save changes info
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    changes_file = os.path.join(changes_only_dir, f"changes_{timestamp}.json")

    import json
    with open(changes_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'last_backup': last_backup_path,
            'changes': changes
        }, f, indent=2)

    print(f"Incremental changes saved: {changes_file}")
    return changes_file

def restore_database(backup_path, target_path):
    """Restore database from backup"""
    if os.path.exists(target_path):
        os.remove(target_path)

    backup_conn = sqlite3.connect(backup_path)
    restore_conn = sqlite3.connect(target_path)

    with restore_conn:
        backup_conn.backup(restore_conn)

    backup_conn.close()
    restore_conn.close()

    print(f"Database restored to: {target_path}")

# Usage
if __name__ == '__main__':
    # Full backup
    backup_path = backup_database('company.db')

    # Incremental backup
    incremental_backup('company.db', backup_path)

    # Restore
    restore_database(backup_path, 'company_restored.db')
```

## Advanced Features

### JSON Support

```python
import sqlite3
import json

# Enable JSON functions (SQLite 3.38+)
conn = sqlite3.connect('company.db')
conn.enable_load_extension(True)
# Note: json1 extension is built into SQLite 3.38+

# Create table with JSON column
conn.execute('''
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        profile_data TEXT,  -- JSON string
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES employees (id)
    )
''')

# Insert JSON data
profile_data = {
    'personal': {
        'age': 30,
        'location': 'New York',
        'interests': ['programming', 'music', 'sports']
    },
    'professional': {
        'skills': ['Python', 'SQL', 'JavaScript'],
        'experience_years': 5,
        'certifications': ['AWS Developer', ' Scrum Master']
    },
    'preferences': {
        'theme': 'dark',
        'notifications': True,
        'language': 'en'
    }
}

conn.execute('''
    INSERT INTO user_profiles (user_id, profile_data)
    VALUES (?, ?)
''', (1, json.dumps(profile_data)))

# Query JSON data
cursor = conn.execute('''
    SELECT user_id, json_extract(profile_data, '$.personal.age') as age,
           json_extract(profile_data, '$.professional.experience_years') as experience
    FROM user_profiles
    WHERE json_extract(profile_data, '$.preferences.theme') = ?
''', ('dark',))

results = cursor.fetchall()
print("Users with dark theme:")
for result in results:
    print(f"User {result[0]}: Age {result[1]}, Experience {result[2]} years")

# Update JSON data
conn.execute('''
    UPDATE user_profiles
    SET profile_data = json_set(profile_data, '$.professional.experience_years',
                               json_extract(profile_data, '$.professional.experience_years') + 1)
    WHERE user_id = 1
''')

# Query array elements
cursor = conn.execute('''
    SELECT user_id, json_extract(profile_data, '$.personal.interests[0]') as first_interest
    FROM user_profiles
    WHERE json_array_length(json_extract(profile_data, '$.personal.interests')) > 1
''')

results = cursor.fetchall()
print("\nUsers with multiple interests:")
for result in results:
    print(f"User {result[0]}: First interest - {result[1]}")

conn.commit()
conn.close()
```

### Custom Functions

```python
import sqlite3
import hashlib
import re

def create_custom_functions(conn):
    """Create custom SQLite functions"""

    # Hash function
    def sha256_hash(text):
        if text is None:
            return None
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    # Email validation function
    def is_valid_email(email):
        if email is None:
            return None
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return 1 if re.match(pattern, email) else 0

    # String similarity function (simple)
    def string_similarity(s1, s2):
        if s1 is None or s2 is None:
            return None
        s1, s2 = s1.lower(), s2.lower()
        return len(set(s1) & set(s2)) / len(set(s1) | set(s2))

    # Register functions
    conn.create_function('sha256', 1, sha256_hash)
    conn.create_function('is_valid_email', 1, is_valid_email)
    conn.create_function('string_similarity', 2, string_similarity)

# Usage
conn = sqlite3.connect('company.db')
create_custom_functions(conn)
cursor = conn.cursor()

# Use custom functions in queries
cursor.execute('''
    SELECT first_name, last_name, email,
           sha256(email) as email_hash,
           is_valid_email(email) as email_valid
    FROM employees
''')

results = cursor.fetchall()
print("Employee email validation:")
for result in results:
    valid = "Valid" if result[3] else "Invalid"
    print(f"{result[0]} {result[1]}: {result[2]} - {valid} (Hash: {result[3][:16]}...)")

# Find similar names
cursor.execute('''
    SELECT e1.first_name || ' ' || e1.last_name as name1,
           e2.first_name || ' ' || e2.last_name as name2,
           string_similarity(e1.first_name, e2.first_name) as similarity
    FROM employees e1
    JOIN employees e2 ON e1.id < e2.id
    WHERE string_similarity(e1.first_name, e2.first_name) > 0.5
    ORDER BY similarity DESC
''')

similar_names = cursor.fetchall()
print("\nSimilar first names:")
for name1, name2, sim in similar_names:
    print(f"{name1} ~ {name2} (similarity: {sim:.2f})")

conn.close()
```

This comprehensive guide covers SQLite fundamentals, advanced features, performance optimization, and practical usage patterns for building robust database applications.
