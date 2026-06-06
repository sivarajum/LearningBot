# SQLite Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import sqlite3

# Connect
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
''')

# Insert
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
               ("John", "john@example.com"))
conn.commit()
```

### 2. **Basic Queries**
```python
# Select
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# Update
cursor.execute("UPDATE users SET email = ? WHERE id = ?", 
               ("new@example.com", 1))
conn.commit()
```

## Level 2 – Production Patterns

### Connection Pooling
```python
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect('database.db')
    try:
        yield conn
    finally:
        conn.close()
```

### Full-Text Search
```python
cursor.execute('''
    CREATE VIRTUAL TABLE documents USING fts5(
        title, content
    )
''')

cursor.execute("SELECT * FROM documents WHERE documents MATCH 'query'")
```

## Level 3 – Architect Playbook

### Performance Optimization
```python
# WAL mode
conn.execute("PRAGMA journal_mode=WAL")

# Optimize
conn.execute("PRAGMA optimize")
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Open DB | `sqlite3 database.db` | CLI access |
| Backup | `.backup backup.db` | Backup database |
| Vacuum | `VACUUM` | Optimize database |

## Checklist Before Production

- [ ] Enable WAL mode
- [ ] Set up proper indexing
- [ ] Configure connection pooling
- [ ] Implement proper error handling
- [ ] Set up backup strategy
- [ ] Optimize queries
- [ ] Monitor performance
- [ ] Consider migration to PostgreSQL for scale
