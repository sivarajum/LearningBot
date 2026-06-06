# NumPy: Comprehensive Guide

## Overview

NumPy (Numerical Python) is the fundamental package for scientific computing in Python. It provides a high-performance multidimensional array object and tools for working with these arrays. NumPy is essential for numerical computations, data analysis, and serves as the foundation for many other scientific Python libraries.

## Core Concepts

### What is NumPy?

NumPy is an open-source library that provides:
- **Multidimensional arrays (ndarray)**: Homogeneous n-dimensional array objects
- **Vectorized operations**: Fast mathematical operations on arrays
- **Mathematical functions**: Comprehensive collection of mathematical routines
- **Linear algebra**: Built-in linear algebra operations
- **Integration**: Foundation for pandas, matplotlib, scikit-learn, and more

### Key Characteristics

- **Performance**: C-based implementation for fast computations
- **Memory efficiency**: Contiguous memory allocation
- **Broadcasting**: Efficient element-wise operations
- **Integration**: Core dependency for scientific Python ecosystem
- **Open source**: Free and actively maintained

### NumPy Array Fundamentals

```python
import numpy as np

# Creating arrays
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Array properties
print(arr.shape)        # (5,)
print(arr.dtype)        # int64
print(arr.ndim)         # 1 (dimensions)
print(matrix.shape)     # (3, 3)

# Array creation functions
zeros = np.zeros((3, 4))
ones = np.ones((2, 3))
full = np.full((2, 2), 7)
identity = np.eye(3)
random_arr = np.random.rand(3, 3)
arange = np.arange(0, 10, 2)
linspace = np.linspace(0, 1, 5)
```

## Array Operations

### Indexing and Slicing

```python
arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Basic indexing
print(arr[0])           # 1
print(arr[-1])          # 10

# Slicing
print(arr[2:5])         # [3, 4, 5]
print(arr[::2])         # [1, 3, 5, 7, 9]
print(arr[::-1])        # [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

# Multidimensional indexing
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(matrix[1, 2])     # 6
print(matrix[:, 1])     # [2, 5, 8] (second column)
print(matrix[1:, :2])   # [[4, 5], [7, 8]]

# Boolean indexing
print(arr[arr > 5])     # [6, 7, 8, 9, 10]
print(arr[(arr > 3) & (arr < 8)])  # [4, 5, 6, 7]
```

### Array Mathematics

```python
a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])

# Element-wise operations
print(a + b)            # [6, 8, 10, 12]
print(a * b)            # [5, 12, 21, 32]
print(a ** 2)           # [1, 4, 9, 16]
print(np.sin(a))        # Trigonometric functions

# Universal functions (ufuncs)
print(np.sqrt(a))       # Square root
print(np.exp(a))        # Exponential
print(np.log(a))        # Natural logarithm
print(np.abs(a))        # Absolute value

# Aggregations
print(np.sum(a))        # 10
print(np.mean(a))       # 2.5
print(np.std(a))        # Standard deviation
print(np.max(a))        # 4
print(np.min(a))        # 1
print(np.argmax(a))     # Index of max: 3
```

### Broadcasting

```python
# Broadcasting allows operations on arrays of different shapes
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Scalar broadcasting
print(arr + 10)         # Adds 10 to each element
print(arr * 2)          # Multiplies each element by 2

# Array broadcasting
row = np.array([10, 20, 30])
print(arr + row)        # Broadcasts row to each row of arr

col = np.array([[1], [2], [3]])
print(arr + col)        # Broadcasts column to each column of arr
```

### Linear Algebra

```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

# Matrix multiplication
print(np.dot(a, b))
print(a @ b)            # Python 3.5+ syntax

# Matrix operations
print(np.linalg.inv(a))    # Matrix inverse
print(np.linalg.det(a))    # Determinant
print(np.linalg.eig(a))    # Eigenvalues and eigenvectors
print(np.linalg.solve(a, b))  # Solve linear system

# Matrix properties
print(np.transpose(a))
print(a.T)              # Shorthand for transpose
```

## Advanced Features

### Array Manipulation

```python
arr = np.array([1, 2, 3, 4, 5])

# Reshaping
print(arr.reshape(5, 1))
print(arr.reshape(-1, 1))  # -1 means infer dimension

# Concatenation
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(np.concatenate([a, b]))
print(np.vstack([a, b]))   # Vertical stack
print(np.hstack([a, b]))   # Horizontal stack

# Splitting
arr = np.arange(12).reshape(3, 4)
print(np.split(arr, 3))    # Split into 3 arrays
print(np.hsplit(arr, 2))   # Horizontal split

# Adding/removing dimensions
arr = np.array([1, 2, 3])
print(arr[np.newaxis, :])  # Add dimension: shape (1, 3)
print(arr[:, np.newaxis])  # Add dimension: shape (3, 1)
print(arr.squeeze())       # Remove dimensions of size 1
```

### Sorting and Searching

```python
arr = np.array([3, 1, 4, 1, 5, 9, 2, 6])

# Sorting
print(np.sort(arr))        # Returns sorted copy
arr.sort()                 # In-place sort
print(np.argsort(arr))     # Returns indices that would sort array

# Searching
print(np.where(arr > 5))   # Indices where condition is True
print(np.searchsorted(arr, 5))  # Insert index to maintain sorted order

# Finding elements
print(np.argmax(arr))      # Index of maximum
print(np.argmin(arr))      # Index of minimum
print(np.nonzero(arr))     # Indices of non-zero elements
```

### Statistical Functions

```python
arr = np.random.randn(100)  # 100 random numbers from normal distribution

# Basic statistics
print(np.mean(arr))
print(np.median(arr))
print(np.std(arr))         # Standard deviation
print(np.var(arr))         # Variance
print(np.percentile(arr, [25, 50, 75]))  # Quartiles

# Correlation
a = np.random.randn(100)
b = np.random.randn(100)
print(np.corrcoef(a, b))   # Correlation coefficient

# Histogram
counts, bins = np.histogram(arr, bins=10)
print(counts)
print(bins)
```

## Performance Optimization

### Vectorization

```python
import time

# Slow: Python loops
def slow_sum(arr):
    result = 0
    for x in arr:
        result += x
    return result

# Fast: NumPy vectorization
def fast_sum(arr):
    return np.sum(arr)

arr = np.random.rand(1000000)

# Time comparison
start = time.time()
result1 = slow_sum(arr)
time1 = time.time() - start

start = time.time()
result2 = fast_sum(arr)
time2 = time.time() - start

print(f"Python loop: {time1:.4f}s")
print(f"NumPy vectorized: {time2:.4f}s")
print(f"Speedup: {time1/time2:.1f}x")
```

### Memory Efficiency

```python
# Contiguous memory allocation
arr = np.arange(12)
print(arr.flags)          # Memory layout information
print(arr.data)           # Memory buffer

# Views vs copies
view = arr.view()         # View shares memory
copy = arr.copy()         # Copy has separate memory

arr[0] = 999
print(view[0])            # 999 (changed because view shares memory)
print(copy[0])            # 0 (unchanged because copy has separate memory)
```

## Integration with Other Libraries

### NumPy and Pandas

```python
import pandas as pd

# NumPy arrays from pandas
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
arr = df.values           # Convert DataFrame to NumPy array
print(arr)

# NumPy arrays in pandas
arr = np.random.randn(100)
series = pd.Series(arr)   # Create Series from NumPy array
print(series.describe())
```

### NumPy and Matplotlib

```python
import matplotlib.pyplot as plt

# Create data with NumPy
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Plot with matplotlib
plt.plot(x, y)
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.title('Sine Wave')
plt.show()
```

## Best Practices

### 1. Use Vectorized Operations

```python
# ❌ Avoid: Python loops
result = []
for x in arr:
    result.append(x * 2)

# ✅ Prefer: NumPy vectorization
result = arr * 2
```

### 2. Avoid Unnecessary Copies

```python
# ✅ Use views when possible
view = arr[1:5]          # View, no copy

# Use copy only when needed
copy = arr[1:5].copy()   # Explicit copy
```

### 3. Specify dtypes for Memory Efficiency

```python
# Default float64 uses 8 bytes per element
arr1 = np.array([1.0, 2.0, 3.0])  # float64

# Use float32 if precision allows (4 bytes per element)
arr2 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
```

### 4. Use Broadcasting Efficiently

```python
# ✅ Efficient broadcasting
result = arr + 10        # Broadcast scalar

# ✅ Efficient array operations
mean = np.mean(arr, axis=0)  # Mean along axis
```

## Common Use Cases

### Image Processing

```python
# Represent image as NumPy array
image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

# Image operations
gray = np.mean(image, axis=2)  # Grayscale conversion
flipped = np.flip(image, axis=1)  # Flip horizontally
rotated = np.rot90(image)      # Rotate 90 degrees
```

### Signal Processing

```python
# Generate signal
t = np.linspace(0, 1, 1000)
signal = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 10 * t)

# FFT analysis
fft = np.fft.fft(signal)
frequencies = np.fft.fftfreq(len(signal))
```

### Data Analysis

```python
# Load and analyze data
data = np.random.randn(1000, 10)

# Statistical analysis
means = np.mean(data, axis=0)
stds = np.std(data, axis=0)
correlation = np.corrcoef(data.T)

# Filtering
filtered = data[data[:, 0] > 0]  # Filter by first column
```

## Installation

```bash
# Using pip
pip install numpy

# Using conda
conda install numpy

# Verify installation
python -c "import numpy as np; print(np.__version__)"
```

## References

- Official documentation: https://numpy.org/doc/
- NumPy GitHub: https://github.com/numpy/numpy
- NumPy user guide: https://numpy.org/doc/stable/user/
- NumPy API reference: https://numpy.org/doc/stable/reference/













