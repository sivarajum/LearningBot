# NumPy Interview Questions and Answers

## Beginner Level Questions

### Q1: What is NumPy and why is it important for data science?

**Answer:**

NumPy (Numerical Python) is the fundamental package for scientific computing in Python. It provides a high-performance multidimensional array object (`ndarray`) and tools for working with these arrays. NumPy is crucial for data science because:

**Key Importance:**
- **Performance**: C-based implementation provides 100-1000x speedup over Python lists
- **Foundation**: Core dependency for pandas, matplotlib, scikit-learn, and most scientific Python libraries
- **Efficiency**: Memory-efficient contiguous memory allocation for arrays
- **Vectorization**: Enables fast element-wise operations without Python loops
- **Integration**: Seamless integration with C/C++ and Fortran code

**Use Cases:**
- Numerical computations and mathematical operations
- Data preprocessing and feature engineering
- Linear algebra and matrix operations
- Statistical analysis and data manipulation
- Image and signal processing

### Q2: What is the difference between NumPy arrays and Python lists?

**Answer:**

**NumPy Arrays:**
- Homogeneous data types (all elements same type)
- Fixed size once created (but can reshape)
- Contiguous memory allocation (cache-friendly)
- Vectorized operations (C-level implementation)
- Broadcasting capabilities
- Memory efficient
- Fast mathematical operations

**Python Lists:**
- Heterogeneous data types (can mix types)
- Dynamic size (can append/remove)
- Non-contiguous memory (pointers to objects)
- Element-by-element operations (Python loops)
- No built-in broadcasting
- More memory overhead
- Slower mathematical operations

**Example:**
```python
import numpy as np
import time

# Python list
py_list = list(range(1000000))

# NumPy array
np_array = np.array(py_list)

# Performance comparison
start = time.time()
result1 = [x * 2 for x in py_list]
time1 = time.time() - start

start = time.time()
result2 = np_array * 2
time2 = time.time() - start

print(f"Python list: {time1:.4f}s")
print(f"NumPy array: {time2:.4f}s")
print(f"Speedup: {time1/time2:.1f}x")
```

### Q3: Explain NumPy array creation methods.

**Answer:**

NumPy provides various methods to create arrays:

**From Python Lists:**
```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])
```

**Common Creation Functions:**
```python
# Zeros array
zeros = np.zeros((3, 4))  # 3x4 array of zeros

# Ones array
ones = np.ones((2, 3))    # 2x3 array of ones

# Full array
full = np.full((3, 3), 7)  # 3x3 array filled with 7

# Identity matrix
identity = np.eye(3)      # 3x3 identity matrix

# Range array
arange = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]

# Linear space
linspace = np.linspace(0, 1, 5)  # 5 evenly spaced values from 0 to 1

# Random array
random_arr = np.random.rand(3, 3)  # 3x3 random floats [0, 1)
random_int = np.random.randint(0, 10, (3, 3))  # Random integers

# Empty array (uninitialized)
empty = np.empty((2, 2))  # Fast, but contains garbage values
```

### Q4: What is broadcasting in NumPy and how does it work?

**Answer:**

Broadcasting is NumPy's mechanism for performing element-wise operations on arrays of different shapes, without explicitly copying data.

**Broadcasting Rules:**
1. **Shape compatibility**: Two arrays are compatible if their dimensions are equal or one has size 1
2. **Dimension expansion**: Missing dimensions are treated as size 1
3. **Size 1 dimensions**: Arrays with size 1 in a dimension are stretched to match

**Examples:**
```python
import numpy as np

# Scalar broadcasting
arr = np.array([[1, 2, 3], [4, 5, 6]])
result = arr + 10  # Broadcasts scalar 10 to all elements

# Array broadcasting
a = np.array([[1, 2, 3], [4, 5, 6]])  # Shape: (2, 3)
b = np.array([10, 20, 30])            # Shape: (3,)
result = a + b  # Broadcasts b to each row of a

# 2D broadcasting
c = np.array([[1], [2], [3]])  # Shape: (3, 1)
d = np.array([1, 2, 3])        # Shape: (3,)
result = c + d  # Broadcasts both to shape (3, 3)

# Invalid broadcasting
e = np.array([[1, 2], [3, 4]])  # Shape: (2, 2)
f = np.array([1, 2, 3])         # Shape: (3,)
# e + f  # Error: shapes are not compatible
```

### Q5: How do you perform indexing and slicing on NumPy arrays?

**Answer:**

NumPy supports various indexing methods:

**Basic Indexing:**
```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Single element
print(arr[0])        # 1
print(arr[-1])       # 10

# Slicing
print(arr[2:5])      # [3, 4, 5]
print(arr[:5])       # [1, 2, 3, 4, 5]
print(arr[5:])       # [6, 7, 8, 9, 10]
print(arr[::2])      # [1, 3, 5, 7, 9]
print(arr[::-1])     # [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
```

**Multidimensional Indexing:**
```python
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Element access
print(matrix[1, 2])      # 6

# Row access
print(matrix[1])         # [4, 5, 6]
print(matrix[1, :])      # [4, 5, 6]

# Column access
print(matrix[:, 1])      # [2, 5, 8]

# Subarray
print(matrix[1:, :2])    # [[4, 5], [7, 8]]
```

**Boolean Indexing:**
```python
arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Boolean mask
mask = arr > 5
print(arr[mask])         # [6, 7, 8, 9, 10]

# Multiple conditions
mask = (arr > 3) & (arr < 8)
print(arr[mask])         # [4, 5, 6, 7]
```

**Fancy Indexing:**
```python
arr = np.array([10, 20, 30, 40, 50])
indices = [0, 2, 4]
print(arr[indices])      # [10, 30, 50]

matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
rows = [0, 2]
cols = [1, 2]
print(matrix[rows, cols])  # [2, 9]
```

## Intermediate Level Questions

### Q6: Explain NumPy's ufuncs (universal functions) and their importance.

**Answer:**

Universal functions (ufuncs) are NumPy functions that operate element-wise on arrays, implemented in C for performance.

**Key Characteristics:**
- **Element-wise operations**: Apply function to each element
- **Vectorized**: Fast C-level implementation
- **Broadcasting**: Automatically handle different shapes
- **Output control**: Can specify output array

**Categories of ufuncs:**
```python
import numpy as np

# Mathematical functions
arr = np.array([1, 4, 9, 16])
print(np.sqrt(arr))      # [1. 2. 3. 4.]
print(np.exp(arr))       # Exponential
print(np.log(arr))       # Natural logarithm
print(np.sin(arr))       # Trigonometric functions

# Arithmetic functions
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(np.add(a, b))      # [5, 7, 9]
print(np.multiply(a, b)) # [4, 10, 18]
print(np.power(a, 2))    # [1, 4, 9]

# Comparison functions
print(np.greater(a, b))  # [False, False, False]
print(np.equal(a, b))    # Element-wise equality

# Logical functions
print(np.logical_and(a > 1, a < 3))  # [False, True, False]

# Custom ufuncs
def double(x):
    return x * 2

double_ufunc = np.frompyfunc(double, 1, 1)
result = double_ufunc(arr)
```

### Q7: How do you perform linear algebra operations with NumPy?

**Answer:**

NumPy's `numpy.linalg` module provides linear algebra functions:

```python
import numpy as np

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

# Matrix multiplication
result = np.dot(a, b)
result = a @ b  # Python 3.5+ syntax

# Matrix inverse
inv_a = np.linalg.inv(a)

# Determinant
det = np.linalg.det(a)

# Eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(a)

# Singular Value Decomposition (SVD)
U, s, Vt = np.linalg.svd(a)

# QR decomposition
Q, R = np.linalg.qr(a)

# Matrix rank
rank = np.linalg.matrix_rank(a)

# Solve linear system: Ax = b
x = np.linalg.solve(a, b)

# Least squares solution
x, residuals, rank, s = np.linalg.lstsq(a, b)
```

### Q8: What are the best practices for NumPy performance optimization?

**Answer:**

**1. Use Vectorization Instead of Loops:**
```python
# ❌ Slow: Python loop
result = []
for x in arr:
    result.append(x * 2)

# ✅ Fast: NumPy vectorization
result = arr * 2
```

**2. Avoid Unnecessary Copies:**
```python
# Use views when possible
view = arr[1:5]          # View, no copy

# Use copy only when needed
copy = arr.copy()        # Explicit copy
```

**3. Use Appropriate Data Types:**
```python
# Default float64 uses 8 bytes per element
arr1 = np.array([1.0, 2.0, 3.0])  # float64

# Use float32 if precision allows (4 bytes per element)
arr2 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
```

**4. Use In-place Operations:**
```python
# ✅ In-place operations (faster, less memory)
arr += 1
arr *= 2

# ❌ Creates new array (slower, more memory)
arr = arr + 1
arr = arr * 2
```

**5. Use np.where() Instead of Loops:**
```python
# ❌ Slow: Loop
result = []
for x in arr:
    if x > 0:
        result.append(x)
    else:
        result.append(0)

# ✅ Fast: np.where
result = np.where(arr > 0, arr, 0)
```

**6. Use Broadcasting:**
```python
# ✅ Efficient broadcasting
result = arr + 10

# ❌ Inefficient explicit expansion
result = arr + np.array([10] * len(arr))
```

### Q9: Explain NumPy's memory layout and why it matters.

**Answer:**

NumPy arrays use contiguous memory blocks for performance:

**Memory Layout:**
- **Contiguous memory**: Array elements stored in a single block
- **Cache-friendly**: Modern CPUs can cache contiguous blocks efficiently
- **SIMD support**: Enables vectorized CPU instructions
- **C-compatible**: Easy integration with C libraries

**Memory Structure:**
```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])

# Memory information
print(arr.flags)         # Memory layout flags
print(arr.data)          # Memory buffer pointer
print(arr.strides)       # Bytes to step in each dimension
print(arr.itemsize)      # Size of each element in bytes
print(arr.nbytes)        # Total memory usage

# C-contiguous vs Fortran-contiguous
c_arr = np.array([[1, 2], [3, 4]], order='C')
f_arr = np.array([[1, 2], [3, 4]], order='F')

print(c_arr.flags['C_CONTIGUOUS'])  # True
print(f_arr.flags['F_CONTIGUOUS'])  # True
```

**Performance Impact:**
- Contiguous arrays: Fast operations (cache hits)
- Non-contiguous arrays: Slower operations (cache misses)
- Memory alignment: Affects SIMD performance

### Q10: How do you handle missing data and NaN values in NumPy?

**Answer:**

NumPy provides functions for handling missing data:

```python
import numpy as np

# Create array with NaN
arr = np.array([1, 2, np.nan, 4, np.nan, 6])

# Check for NaN
print(np.isnan(arr))     # [False, False, True, False, True, False]

# Remove NaN values
cleaned = arr[~np.isnan(arr)]  # [1, 2, 4, 6]

# Replace NaN with value
arr_filled = np.nan_to_num(arr, nan=0)  # Replace NaN with 0

# Operations with NaN
print(np.nansum(arr))    # Sum ignoring NaN
print(np.nanmean(arr))   # Mean ignoring NaN
print(np.nanstd(arr))    # Standard deviation ignoring NaN

# Infinity handling
arr_inf = np.array([1, 2, np.inf, 4])
print(np.isinf(arr_inf))  # Check for infinity
print(np.isfinite(arr_inf))  # Check for finite values
```

## Advanced Level Questions

### Q11: How do you use NumPy with GPU acceleration (CuPy)?

**Answer:**

While NumPy itself doesn't support GPU, CuPy provides a NumPy-compatible interface for GPU:

```python
import cupy as cp  # CuPy (GPU-accelerated NumPy)

# Create GPU array
gpu_arr = cp.array([1, 2, 3, 4, 5])

# Operations on GPU
result = gpu_arr * 2  # Computed on GPU

# Transfer to CPU
cpu_arr = cp.asnumpy(gpu_arr)

# Comparison with NumPy
import numpy as np

cpu_data = np.random.randn(10000, 10000)
gpu_data = cp.random.randn(10000, 10000)

# NumPy (CPU)
result_cpu = np.dot(cpu_data, cpu_data)

# CuPy (GPU)
result_gpu = cp.dot(gpu_data, gpu_data)
result_cpu = cp.asnumpy(result_gpu)
```

### Q12: Explain advanced NumPy features like structured arrays and record arrays.

**Answer:**

**Structured Arrays:**
```python
import numpy as np

# Define structured dtype
dtype = np.dtype([
    ('name', 'U20'),      # Unicode string, 20 chars
    ('age', 'i4'),        # 32-bit integer
    ('salary', 'f8')      # 64-bit float
])

# Create structured array
employees = np.array([
    ('Alice', 30, 75000.0),
    ('Bob', 25, 65000.0),
    ('Charlie', 35, 85000.0)
], dtype=dtype)

# Access fields
print(employees['name'])      # ['Alice' 'Bob' 'Charlie']
print(employees['age'])       # [30 25 35]
print(employees['salary'])    # [75000. 65000. 85000.]

# Filter by field
young = employees[employees['age'] < 30]
print(young['name'])          # ['Bob']
```

**Record Arrays:**
```python
# Record array (allows attribute access)
rec_array = np.rec.array([
    ('Alice', 30, 75000.0),
    ('Bob', 25, 65000.0)
], dtype=[('name', 'U20'), ('age', 'i4'), ('salary', 'f8')])

# Attribute access
print(rec_array.name)    # ['Alice' 'Bob']
print(rec_array.age)     # [30 25]
```

### Q13: How does NumPy integrate with Pandas, Matplotlib, and other libraries?

**Answer:**

**NumPy and Pandas:**
```python
import pandas as pd
import numpy as np

# NumPy arrays from Pandas
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
arr = df.values           # Convert DataFrame to NumPy array
print(arr)

# NumPy arrays in Pandas
arr = np.random.randn(100)
series = pd.Series(arr)   # Create Series from NumPy array
print(series.describe())
```

**NumPy and Matplotlib:**
```python
import matplotlib.pyplot as plt
import numpy as np

# Create data with NumPy
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Plot
plt.plot(x, y)
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.title('Sine Wave')
plt.show()
```

**NumPy and scikit-learn:**
```python
from sklearn.preprocessing import StandardScaler
import numpy as np

X = np.random.randn(100, 5)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Returns NumPy array
```

### Q14: What are the limitations of NumPy and when should you use alternatives?

**Answer:**

**NumPy Limitations:**
- **Single-threaded operations**: Most operations use single CPU core
- **Memory constraints**: Arrays must fit in RAM
- **No GPU support**: NumPy doesn't support GPU acceleration natively
- **Homogeneous data**: All elements must be same type

**When to Use Alternatives:**
- **GPU computing**: Use CuPy for GPU-accelerated operations
- **Large-scale data**: Use Dask or PySpark for out-of-core computation
- **Sparse data**: Use scipy.sparse for sparse matrices
- **Mixed data types**: Use Pandas DataFrame
- **Multi-threading**: Use Numba for JIT compilation and parallelization

**Alternatives:**
```python
# Dask for large arrays
import dask.array as da
large_array = da.random.randn(10000, 10000, chunks=(1000, 1000))
result = large_array.sum().compute()

# Numba for JIT compilation
from numba import jit, prange
import numpy as np

@jit(nopython=True, parallel=True)
def parallel_sum(arr):
    result = 0.0
    for i in prange(len(arr)):
        result += arr[i]
    return result

arr = np.random.randn(1000000)
result = parallel_sum(arr)
```

### Q15: Explain NumPy's random number generation and seeding.

**Answer:**

```python
import numpy as np

# Generate random numbers
random_floats = np.random.rand(3, 3)  # Uniform [0, 1)
random_ints = np.random.randint(0, 10, (3, 3))  # Integers [0, 10)
normal_dist = np.random.randn(100)    # Standard normal distribution

# Seeding for reproducibility
np.random.seed(42)  # Global random state
arr1 = np.random.rand(5)

np.random.seed(42)  # Reset seed
arr2 = np.random.rand(5)
print(np.array_equal(arr1, arr2))  # True

# Using RandomState for independent streams
rng1 = np.random.RandomState(42)
rng2 = np.random.RandomState(42)
print(np.array_equal(rng1.rand(5), rng2.rand(5)))  # True

# Modern approach (NumPy 1.17+)
from numpy.random import default_rng
rng = default_rng(42)
random_values = rng.random(5)
```

## Practical Coding Questions

### Q16: Write a function to normalize a NumPy array.

**Answer:**

```python
import numpy as np

def normalize(arr):
    """Normalize array to [0, 1] range"""
    arr_min = arr.min()
    arr_max = arr.max()
    if arr_max == arr_min:
        return np.zeros_like(arr)
    return (arr - arr_min) / (arr_max - arr_min)

# Standardize (mean=0, std=1)
def standardize(arr):
    """Standardize array (z-score normalization)"""
    mean = arr.mean()
    std = arr.std()
    if std == 0:
        return np.zeros_like(arr)
    return (arr - mean) / std

# Example
arr = np.array([1, 2, 3, 4, 5, 100])
normalized = normalize(arr)
standardized = standardize(arr)

print(f"Original: {arr}")
print(f"Normalized: {normalized}")
print(f"Standardized: {standardized}")
```

### Q17: How do you implement efficient element-wise operations on large arrays?

**Answer:**

```python
import numpy as np
import time

def apply_function_slow(arr, func):
    """Slow: Python loop"""
    result = np.empty_like(arr)
    for i in range(len(arr)):
        result[i] = func(arr[i])
    return result

def apply_function_fast(arr, func):
    """Fast: NumPy vectorization"""
    return func(arr)  # If func is vectorized

def apply_function_vectorized(arr, func):
    """Fast: Custom vectorized function"""
    func_vec = np.vectorize(func, otypes=[arr.dtype])
    return func_vec(arr)

# Benchmark
large_arr = np.random.randn(1000000)

# Vectorized operation
start = time.time()
result1 = np.sin(large_arr) + np.cos(large_arr)
time1 = time.time() - start

# Vectorized function
start = time.time()
result2 = apply_function_vectorized(large_arr, lambda x: np.sin(x) + np.cos(x))
time2 = time.time() - start

print(f"Direct vectorization: {time1:.4f}s")
print(f"Vectorized function: {time2:.4f}s")
```

## References

- Official NumPy documentation: https://numpy.org/doc/
- NumPy user guide: https://numpy.org/doc/stable/user/
- NumPy API reference: https://numpy.org/doc/stable/reference/
- NumPy GitHub: https://github.com/numpy/numpy
- NumPy tutorials: https://numpy.org/devdocs/user/quickstart.html













