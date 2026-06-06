# NumPy Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import numpy as np

# Create arrays
a = np.array([1, 2, 3])
b = np.zeros((3, 4))
c = np.ones((2, 3))
d = np.random.randn(3, 4)
```

### 2. **Basic Operations**
```python
# Arithmetic
a + b
a * b
np.dot(a, b)

# Indexing
a[0]
b[0, 1]
c[:, 1]
```

### 3. **Array Manipulation**
```python
# Reshape
a.reshape(2, 2)

# Concatenate
np.concatenate([a, b], axis=0)

# Split
np.split(a, 3)
```

## Level 2 – Production Patterns

### Mathematical Operations
```python
# Statistics
np.mean(a)
np.std(a)
np.sum(a)

# Linear algebra
np.linalg.inv(matrix)
np.linalg.eig(matrix)
```

### Broadcasting
```python
# Broadcast operations
a = np.array([[1, 2, 3]])
b = np.array([1, 2, 3])
result = a + b  # Broadcasting
```

## Level 3 – Architect Playbook

### Performance
```python
# Vectorized operations (fast)
result = np.sum(array)

# Avoid Python loops (slow)
# Bad: for i in range(len(array)): sum += array[i]
# Good: np.sum(array)
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Create array | `np.array()` | Create array |
| Zeros | `np.zeros()` | Array of zeros |
| Random | `np.random.randn()` | Random array |
| Shape | `array.shape` | Array shape |

## Checklist Before Production

- [ ] Use vectorized operations
- [ ] Optimize memory usage
- [ ] Choose appropriate dtypes
- [ ] Avoid unnecessary copies
- [ ] Profile performance
- [ ] Test numerical accuracy
