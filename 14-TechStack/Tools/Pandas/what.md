# Pandas: Comprehensive Guide

## Overview

Pandas is a powerful, flexible, open-source data analysis and manipulation library for Python. Built on top of NumPy, Pandas provides high-performance, easy-to-use data structures and data analysis tools, making it the de facto standard for data manipulation in Python.

## Core Concepts

### What is Pandas?

Pandas provides two primary data structures:
- **Series**: One-dimensional labeled array capable of holding any data type
- **DataFrame**: Two-dimensional labeled data structure with columns of potentially different types

**Key Characteristics:**
- **Labeled axes**: Rows and columns have labels for easy indexing
- **Heterogeneous data**: Different columns can have different data types
- **Size mutable**: Can add/delete columns and rows dynamically
- **Performance**: Built on NumPy for fast operations
- **Data alignment**: Automatic alignment based on labels
- **Missing data**: Built-in handling of missing values

### Pandas Data Structures

**Series:**
```python
import pandas as pd
import numpy as np

# Create Series
s = pd.Series([1, 3, 5, np.nan, 6, 8])
s = pd.Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])

# Access data
print(s['a'])        # Access by label
print(s[0])          # Access by position
print(s.values)      # NumPy array
print(s.index)       # Index object
```

**DataFrame:**
```python
# Create DataFrame from dict
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'Age': [25, 30, 35, 28],
    'City': ['NYC', 'LA', 'Chicago', 'NYC'],
    'Salary': [75000, 85000, 95000, 80000]
}
df = pd.DataFrame(data)

# Create with index
df = pd.DataFrame(data, index=['emp1', 'emp2', 'emp3', 'emp4'])

# DataFrame properties
print(df.shape)      # (4, 4)
print(df.dtypes)     # Column data types
print(df.columns)    # Column names
print(df.index)      # Row index
print(df.info())     # Concise summary
print(df.describe()) # Statistical summary
```

## Data I/O Operations

### Reading Data

```python
import pandas as pd

# Read CSV
df = pd.read_csv('data.csv')
df = pd.read_csv('data.csv', 
                 sep=',',
                 header=0,
                 index_col=0,
                 parse_dates=['date_col'],
                 dtype={'col1': 'str', 'col2': 'int'},
                 na_values=['NULL', 'N/A'])

# Read Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Read JSON
df = pd.read_json('data.json')
df = pd.read_json('data.json', lines=True)  # JSONL format

# Read Parquet
df = pd.read_parquet('data.parquet')

# Read from SQL
import sqlite3
conn = sqlite3.connect('database.db')
df = pd.read_sql('SELECT * FROM table', conn)
df = pd.read_sql_table('table_name', conn)

# Read from URL
df = pd.read_csv('https://example.com/data.csv')
```

### Writing Data

```python
# Write CSV
df.to_csv('output.csv', index=False)

# Write Excel
df.to_excel('output.xlsx', sheet_name='Data', index=False)

# Write JSON
df.to_json('output.json', orient='records')
df.to_json('output.jsonl', orient='records', lines=True)

# Write Parquet
df.to_parquet('output.parquet', compression='snappy')

# Write to SQL
df.to_sql('table_name', conn, if_exists='replace', index=False)
```

## Data Selection and Indexing

### Column Selection

```python
# Single column
df['Name']          # Returns Series
df.Name            # Attribute-style access (when column name is valid)

# Multiple columns
df[['Name', 'Age']]  # Returns DataFrame

# Column operations
df['NewColumn'] = df['Age'] * 2
df['Category'] = df['Salary'].apply(lambda x: 'High' if x > 85000 else 'Low')
```

### Row Selection

```python
# By label (loc)
df.loc[0]           # Single row
df.loc[0:2]         # Range of rows
df.loc[0, 'Name']   # Single value

# By position (iloc)
df.iloc[0]          # First row
df.iloc[0:3]        # First 3 rows
df.iloc[0, 1]       # Row 0, Column 1

# Boolean indexing
df[df['Age'] > 30]
df[(df['Age'] > 30) & (df['Salary'] > 80000)]
df[df['City'].isin(['NYC', 'LA'])]

# Query method
df.query('Age > 30 and Salary > 80000')
df.query('City in ["NYC", "LA"]')
```

## Data Cleaning

### Handling Missing Data

```python
# Check for missing values
df.isnull()         # Boolean DataFrame
df.isnull().sum()   # Count per column
df.isnull().any()   # Any missing values

# Drop missing values
df.dropna()                    # Drop rows with any NaN
df.dropna(subset=['Age'])      # Drop rows where Age is NaN
df.dropna(how='all')           # Drop rows where all values are NaN
df.dropna(axis=1)              # Drop columns with NaN

# Fill missing values
df.fillna(0)                    # Fill with 0
df.fillna(df.mean())            # Fill with column mean
df['Age'].fillna(df['Age'].mean())  # Fill specific column
df.fillna(method='ffill')       # Forward fill
df.fillna(method='bfill')       # Backward fill
df.fillna({'Age': df['Age'].mean(), 'Salary': df['Salary'].median()})

# Interpolation
df.interpolate()                # Linear interpolation
df.interpolate(method='polynomial', order=2)
```

### Handling Duplicates

```python
# Find duplicates
df.duplicated()                 # Boolean Series
df.duplicated(subset=['Name'])  # Check specific columns

# Drop duplicates
df.drop_duplicates()
df.drop_duplicates(subset=['Name'], keep='first')
df.drop_duplicates(subset=['Name'], keep='last')
```

### Data Type Conversion

```python
# Convert data types
df['Age'] = df['Age'].astype('int64')
df['Salary'] = df['Salary'].astype('float32')

# Convert to datetime
df['Date'] = pd.to_datetime(df['Date'])
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

# Convert to categorical
df['City'] = df['City'].astype('category')
df['City'] = pd.Categorical(df['City'], categories=['NYC', 'LA', 'Chicago'], ordered=True)

# Convert numeric columns
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
```

## Data Transformation

### Applying Functions

```python
# Apply function to column
df['Age'] = df['Age'].apply(lambda x: x * 2)

# Apply function to row
df['Total'] = df.apply(lambda row: row['A'] + row['B'], axis=1)

# Apply function to DataFrame
df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)

# Vectorized operations (faster)
df['NewCol'] = df['Age'] * 2 + 10
df['Category'] = np.where(df['Age'] > 30, 'Senior', 'Junior')

# Using map for Series
df['CityCode'] = df['City'].map({'NYC': 1, 'LA': 2, 'Chicago': 3})

# Using replace
df['City'].replace({'NYC': 'New York', 'LA': 'Los Angeles'}, inplace=True)
```

### String Operations

```python
# String accessor
df['Name'].str.upper()
df['Name'].str.lower()
df['Name'].str.strip()
df['Name'].str.split(' ')
df['Name'].str.len()
df['Name'].str.contains('Alice')
df['Name'].str.startswith('A')
df['Name'].str.endswith('e')
df['Name'].str.replace('Alice', 'Alicia')
df['Email'].str.extract(r'(\w+)@(\w+)\.(\w+)')  # Extract with regex
```

### Date/Time Operations

```python
# DateTime index
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Date operations
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['IsWeekend'] = df['Date'].dt.dayofweek.isin([5, 6])

# Time shifting
df.shift(1)           # Shift down by 1
df.shift(-1)          # Shift up by 1
df.shift(1, freq='D') # Shift by 1 day

# Resampling
daily = df.resample('D').mean()
monthly = df.resample('M').sum()
yearly = df.resample('Y').agg({'Sales': 'sum', 'Profit': 'mean'})
```

## Grouping and Aggregation

### GroupBy Operations

```python
# Basic grouping
grouped = df.groupby('City')
grouped = df.groupby(['City', 'Department'])

# Aggregation
df.groupby('City').sum()
df.groupby('City').mean()
df.groupby('City').agg({
    'Age': ['mean', 'std', 'count'],
    'Salary': ['sum', 'max', 'min']
})

# Custom aggregation
def custom_agg(series):
    return series.max() - series.min()

df.groupby('City')['Salary'].agg(custom_agg)

# Multiple functions
df.groupby('City')['Salary'].agg(['mean', 'std', 'count'])

# Transform (keep same shape)
df['MeanSalary'] = df.groupby('City')['Salary'].transform('mean')
df['ZScore'] = (df['Salary'] - df.groupby('City')['Salary'].transform('mean')) / df.groupby('City')['Salary'].transform('std')

# Filter groups
df.groupby('City').filter(lambda x: len(x) > 2)  # Groups with more than 2 rows
```

### Pivot Tables

```python
# Create pivot table
pivot = df.pivot_table(
    values='Sales',
    index='Region',
    columns='Quarter',
    aggfunc='sum',
    fill_value=0,
    margins=True
)

# Multi-level pivot
pivot = df.pivot_table(
    values='Sales',
    index=['Region', 'State'],
    columns='Quarter',
    aggfunc='sum'
)

# Melt (wide to long)
df_long = pd.melt(df, id_vars=['Name'], value_vars=['Q1', 'Q2', 'Q3'], var_name='Quarter', value_name='Sales')

# Pivot (long to wide)
df_wide = df_long.pivot(index='Name', columns='Quarter', values='Sales')
```

## Merging and Joining

### Concatenation

```python
# Concatenate DataFrames
pd.concat([df1, df2])                    # Vertical
pd.concat([df1, df2], axis=1)            # Horizontal
pd.concat([df1, df2], ignore_index=True) # Reset index
pd.concat([df1, df2], keys=['A', 'B'])   # Add keys
```

### Merging

```python
# Inner join
result = pd.merge(df1, df2, on='key')

# Left join
result = pd.merge(df1, df2, on='key', how='left')

# Right join
result = pd.merge(df1, df2, on='key', how='right')

# Outer join
result = pd.merge(df1, df2, on='key', how='outer')

# Join on different column names
result = pd.merge(df1, df2, left_on='key1', right_on='key2')

# Join on index
result = pd.merge(df1, df2, left_index=True, right_index=True)

# Multiple keys
result = pd.merge(df1, df2, on=['key1', 'key2'])

# Indicator for join type
result = pd.merge(df1, df2, on='key', how='outer', indicator=True)
```

### Joining

```python
# Join on index
df1.join(df2)

# Join with different join type
df1.join(df2, how='left')
```

## Performance Optimization

### Memory Optimization

```python
# Check memory usage
df.memory_usage(deep=True)

# Optimize data types
df['Age'] = pd.to_numeric(df['Age'], downcast='integer')
df['Salary'] = pd.to_numeric(df['Salary'], downcast='float')

# Use categorical for repeated strings
df['City'] = df['City'].astype('category')

# Check memory before/after
print(f"Before: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
df_optimized = df.copy()
df_optimized['City'] = df_optimized['City'].astype('category')
print(f"After: {df_optimized.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
```

### Vectorization

```python
# ❌ Slow: Loop
result = []
for value in df['Age']:
    result.append(value * 2)

# ✅ Fast: Vectorized
result = df['Age'] * 2

# ❌ Slow: Apply
df['New'] = df.apply(lambda row: row['A'] + row['B'], axis=1)

# ✅ Fast: Vectorized
df['New'] = df['A'] + df['B']
```

### Chunking for Large Files

```python
# Read large file in chunks
chunk_size = 100000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
    # Or concatenate if needed
    # df = pd.concat([df, chunk], ignore_index=True)
```

## Advanced Features

### MultiIndex

```python
# Create MultiIndex
arrays = [['A', 'A', 'B', 'B'], ['one', 'two', 'one', 'two']]
index = pd.MultiIndex.from_arrays(arrays, names=['first', 'second'])
df_multi = pd.DataFrame(np.random.randn(4, 3), index=index, columns=['X', 'Y', 'Z'])

# Access MultiIndex
df_multi.loc['A']
df_multi.loc[('A', 'one')]
df_multi.loc['A', 'one']
df_multi.xs('one', level='second')

# Stack and unstack
stacked = df_multi.stack()
unstacked = stacked.unstack()
```

### Categorical Data

```python
# Create categorical
df['Size'] = pd.Categorical(['Small', 'Medium', 'Large'], ordered=True)

# Categorical operations
df['Size'].cat.categories
df['Size'].cat.codes
df['Size'].cat.add_categories(['XLarge'])
df['Size'].cat.remove_categories(['Small'])
df['Size'].cat.reorder_categories(['Large', 'Medium', 'Small'], ordered=True)

# Memory benefits
print(df['City'].memory_usage(deep=True))
df['City'] = df['City'].astype('category')
print(df['City'].memory_usage(deep=True))  # Significantly reduced
```

### Window Functions

```python
# Rolling windows
df['RollingMean'] = df['Sales'].rolling(window=7).mean()
df['RollingStd'] = df['Sales'].rolling(window=7).std()
df['RollingSum'] = df['Sales'].rolling(window=30).sum()

# Expanding windows
df['ExpandingMean'] = df['Sales'].expanding().mean()
df['ExpandingSum'] = df['Sales'].expanding().sum()

# Exponential weighted
df['EWM'] = df['Sales'].ewm(span=10).mean()

# Rolling with custom functions
df['RollingMax'] = df['Sales'].rolling(window=7).max()
df['RollingMin'] = df['Sales'].rolling(window=7).min()
```

## Method Chaining

```python
# Chain operations for cleaner code
result = (df
    .query('Age > 25')
    .groupby('City')
    .agg({'Salary': 'mean', 'Age': 'count'})
    .rename(columns={'Salary': 'AvgSalary', 'Age': 'Count'})
    .sort_values('AvgSalary', ascending=False)
    .head(10))
```

## Integration with Other Libraries

### NumPy Integration

```python
# Convert to NumPy array
arr = df.values          # Returns NumPy array
arr = df.to_numpy()      # Preferred method

# NumPy array to DataFrame
df = pd.DataFrame(np.random.randn(5, 3), columns=['A', 'B', 'C'])
```

### Matplotlib Integration

```python
import matplotlib.pyplot as plt

# Plot directly from DataFrame
df.plot(x='Age', y='Salary', kind='scatter')
df.plot(kind='hist', column='Age')
df.groupby('City')['Salary'].mean().plot(kind='bar')
plt.show()
```

## Best Practices

### 1. Use Vectorized Operations

```python
# ❌ Avoid: Loops
for i in range(len(df)):
    df.loc[i, 'New'] = df.loc[i, 'A'] * 2

# ✅ Prefer: Vectorized
df['New'] = df['A'] * 2
```

### 2. Specify Data Types When Reading

```python
# ✅ Specify dtypes to avoid memory waste
df = pd.read_csv('data.csv', dtype={'Age': 'int32', 'Salary': 'float32'})
```

### 3. Use Query for Complex Filtering

```python
# ✅ Clean and readable
df.query('Age > 30 and Salary > 80000')

# ❌ Less readable
df[(df['Age'] > 30) & (df['Salary'] > 80000)]
```

### 4. Leverage Categorical Data Types

```python
# ✅ Memory efficient for repeated strings
df['City'] = df['City'].astype('category')
```

### 5. Use Method Chaining

```python
# ✅ Clean and readable
result = (df
    .filter(['Name', 'Age', 'Salary'])
    .query('Age > 25')
    .sort_values('Salary')
    .head(10))
```

## Common Use Cases

### Data Exploration

```python
# Quick exploration
print(df.head())
print(df.tail())
print(df.shape)
print(df.info())
print(df.describe())
print(df.dtypes)
print(df.nunique())  # Unique values per column
print(df.value_counts())  # Value counts
```

### Data Analysis

```python
# Correlation analysis
correlation = df.corr()
print(correlation)

# Crosstab
pd.crosstab(df['City'], df['Department'])

# Statistical summary
df.groupby('City').describe()
```

## Installation

```bash
# Using pip
pip install pandas

# Using conda
conda install pandas

# With optional dependencies
pip install pandas[excel]      # Excel support
pip install pandas[parquet]    # Parquet support
pip install pandas[sql]        # SQL support

# Verify installation
python -c "import pandas as pd; print(pd.__version__)"
```

## References

- Official documentation: https://pandas.pydata.org/docs/
- Pandas GitHub: https://github.com/pandas-dev/pandas
- User guide: https://pandas.pydata.org/docs/user_guide/index.html
- API reference: https://pandas.pydata.org/docs/reference/index.html
- Tutorials: https://pandas.pydata.org/docs/getting_started/intro_tutorials/index.html













