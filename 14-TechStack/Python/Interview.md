# Python Interview Questions and Answers

## Beginner Level Questions

### Q1: What are the key features of Python?

**Answer:**
Python is a high-level, interpreted programming language known for:

**Key Features:**
- **Simple syntax**: Easy to read and write
- **Interpreted**: No compilation step, immediate execution
- **Dynamic typing**: Variable types determined at runtime
- **Object-oriented**: Supports OOP paradigms
- **Functional**: Supports functional programming
- **Extensive libraries**: Rich standard library and ecosystem
- **Cross-platform**: Runs on multiple operating systems
- **Memory management**: Automatic garbage collection

**Use Cases:**
- Web development (Django, Flask)
- Data science and analytics (Pandas, NumPy)
- Machine learning (TensorFlow, PyTorch)
- Automation and scripting
- System administration

### Q2: Explain Python's data structures: lists, tuples, dictionaries, and sets.

**Answer:**

**Lists:**
- Ordered, mutable collections
- Allow duplicates
- Indexed by integers
- Support slicing and various methods

**Tuples:**
- Ordered, immutable collections
- Allow duplicates
- Faster than lists
- Used for fixed data

**Dictionaries:**
- Key-value pairs
- Unordered (Python 3.7+ maintains insertion order)
- Keys must be immutable
- Fast lookups

**Sets:**
- Unordered collections of unique elements
- No duplicates
- Fast membership testing
- Set operations (union, intersection, etc.)

**Example:**
```python
# Lists
my_list = [1, 2, 3, 4, 5]
my_list.append(6)
my_list[0] = 10

# Tuples
my_tuple = (1, 2, 3, 4, 5)
# my_tuple[0] = 10  # Error: tuples are immutable

# Dictionaries
my_dict = {'name': 'Alice', 'age': 30}
my_dict['city'] = 'New York'

# Sets
my_set = {1, 2, 3, 4, 5}
my_set.add(6)
my_set.remove(1)
```

### Q3: What is the difference between lists and tuples?

**Answer:**

**Lists:**
- Mutable (can be modified)
- Slower than tuples
- More memory overhead
- Use when data needs to change

**Tuples:**
- Immutable (cannot be modified)
- Faster than lists
- Less memory overhead
- Use when data should not change

**Example:**
```python
# List - mutable
my_list = [1, 2, 3]
my_list[0] = 10  # OK
my_list.append(4)  # OK

# Tuple - immutable
my_tuple = (1, 2, 3)
# my_tuple[0] = 10  # Error: 'tuple' object does not support item assignment
```

### Q4: Explain Python's list comprehensions and generator expressions.

**Answer:**

**List Comprehensions:**
- Concise way to create lists
- More readable than loops
- Faster than loops in many cases

**Generator Expressions:**
- Similar to list comprehensions
- Lazy evaluation (memory efficient)
- Use parentheses instead of brackets

**Example:**
```python
# List comprehension
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Generator expression
squares_gen = (x**2 for x in range(10))
even_squares_gen = (x**2 for x in range(10) if x % 2 == 0)

# List comprehension creates list immediately
# Generator expression creates iterator (lazy)
```

### Q5: What are decorators in Python?

**Answer:**

**Decorators:**
- Functions that modify other functions
- Allow adding functionality without changing function code
- Use @ syntax for application
- Commonly used for logging, timing, authentication

**Example:**
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Before calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"After calling {func.__name__}")
        return result
    return wrapper

@my_decorator
def my_function():
    print("Inside my_function")

my_function()
```

## Intermediate Level Questions

### Q6: Explain Python's memory management and garbage collection.

**Answer:**

**Memory Management:**
- Automatic memory management
- Reference counting for immediate deallocation
- Cycle detector for circular references
- Generational garbage collection

**Garbage Collection:**
- Reference counting: Immediate deallocation when count reaches 0
- Cycle detector: Handles circular references
- Generational GC: Three generations (young, middle, old)

**Example:**
```python
import gc

# Check object references
import sys
x = [1, 2, 3]
print(sys.getrefcount(x))  # Reference count

# Manual garbage collection
gc.collect()  # Force garbage collection
```

### Q7: What is the difference between == and is in Python?

**Answer:**

**== (Equality):**
- Compares values
- Can be overridden with __eq__ method
- Returns True if values are equal

**is (Identity):**
- Compares object identity (memory address)
- Cannot be overridden
- Returns True if same object

**Example:**
```python
# == compares values
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True (same values)
print(a is b)  # False (different objects)

# is compares identity
c = a
print(a is c)  # True (same object)
```

### Q8: Explain Python's context managers and the with statement.

**Answer:**

**Context Managers:**
- Manage resources (files, connections, locks)
- Ensure proper cleanup
- Use with statement
- Implement __enter__ and __exit__ methods

**Example:**
```python
# File context manager
with open('file.txt', 'r') as f:
    content = f.read()
# File automatically closed

# Custom context manager
class MyContextManager:
    def __enter__(self):
        print("Entering context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context")
        return False

with MyContextManager() as cm:
    print("Inside context")
```

## Advanced Level Questions

### Q9: Explain Python's Global Interpreter Lock (GIL).

**Answer:**

**GIL:**
- Mutex that protects access to Python objects
- Allows only one thread to execute Python bytecode at a time
- Prevents true parallelism in multi-threaded CPU-bound tasks
- Does not affect I/O-bound tasks

**Implications:**
- Multi-threading: Not effective for CPU-bound tasks
- Multi-processing: Use for CPU-bound parallelism
- I/O-bound tasks: Threading works well

**Example:**
```python
import threading
import multiprocessing

# Multi-threading (GIL limits CPU-bound tasks)
def cpu_bound_task():
    result = sum(i*i for i in range(1000000))
    return result

# Multi-processing (bypasses GIL)
if __name__ == '__main__':
    with multiprocessing.Pool() as pool:
        results = pool.map(cpu_bound_task, range(4))
```

### Q10: Explain Python's async/await and asynchronous programming.

**Answer:**

**Async/Await:**
- Enables asynchronous programming
- Non-blocking I/O operations
- Efficient for I/O-bound tasks
- Uses event loop for scheduling

**Example:**
```python
import asyncio

async def fetch_data(url):
    # Simulate async I/O
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    tasks = [
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3")
    ]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(main())
```

---

## Key Takeaways

1. **Python is versatile** with simple syntax and extensive libraries
2. **Data structures** include lists, tuples, dictionaries, and sets
3. **List comprehensions** provide concise list creation
4. **Decorators** modify functions without changing code
5. **Memory management** is automatic with garbage collection
6. **GIL** limits multi-threading for CPU-bound tasks
7. **Async/await** enables asynchronous programming for I/O-bound tasks

