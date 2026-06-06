# Pandas Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import pandas as pd
import numpy as np

# Create DataFrame
df = pd.DataFrame({
    'name': ['John', 'Jane'],
    'age': [30, 25],
    'salary': [50000, 60000]
})
```

### 2. **Basic Operations**
```python
# Read data
df = pd.read_csv("data.csv")

# Select columns
df[['name', 'age']]

# Filter
df[df['age'] > 25]

# Group by
df.groupby('department')['salary'].mean()
```

### 3. **Data Cleaning**
```python
# Handle missing values
df.dropna()
df.fillna(0)

# Remove duplicates
df.drop_duplicates()

# Change types
df['age'] = df['age'].astype(int)
```

## Level 2 – Production Patterns

### Advanced Operations
```python
# Merge
pd.merge(df1, df2, on='id', how='inner')

# Pivot
df.pivot_table(values='sales', index='region', columns='month')

# Apply functions
df['new_col'] = df['col'].apply(lambda x: x * 2)
```

### Performance
```python
# Use vectorization
df['new'] = df['col1'] + df['col2']  # Fast

# Avoid iterrows
# Bad: for index, row in df.iterrows()
# Good: df.apply() or vectorized
```

## Level 3 – Architect Playbook

### Large Datasets
```python
# Chunking
chunk_size = 10000
for chunk in pd.read_csv("large.csv", chunksize=chunk_size):
    process(chunk)

# Dask for larger than memory
import dask.dataframe as dd
df = dd.read_csv("very_large.csv")
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Read CSV | `pd.read_csv()` | Read CSV file |
| Read Parquet | `pd.read_parquet()` | Read Parquet |
| Write | `df.to_csv()` | Write to file |
| Info | `df.info()` | DataFrame info |

## Checklist Before Production

- [ ] Optimize data types
- [ ] Use vectorized operations
- [ ] Implement proper error handling
- [ ] Handle large datasets efficiently
- [ ] Set up proper logging
- [ ] Test data transformations
- [ ] Document data processing logic
