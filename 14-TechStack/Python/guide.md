# Python Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Python
# Download from python.org

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 2. **Basic Syntax**
```python
# Variables
name = "John"
age = 30

# Functions
def greet(name):
    return f"Hello, {name}!"

# Classes
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

### 3. **Data Structures**
```python
# Lists
my_list = [1, 2, 3]

# Dictionaries
my_dict = {'key': 'value'}

# Sets
my_set = {1, 2, 3}
```

## Level 2 – Production Patterns

### Object-Oriented Programming
```python
class Employee(Person):
    def __init__(self, name, age, salary):
        super().__init__(name, age)
        self.salary = salary
```

### Error Handling
```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Error: {e}")
finally:
    cleanup()
```

## Level 3 – Architect Playbook

### Async Programming
```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Run | `python script.py` | Run script |
| Install | `pip install package` | Install package |
| Test | `pytest` | Run tests |

## Checklist Before Production

- [ ] Set up virtual environments
- [ ] Implement proper error handling
- [ ] Set up logging
- [ ] Write tests
- [ ] Document code
- [ ] Set up CI/CD
- [ ] Optimize performance
- [ ] Follow PEP 8
