# Pandas Interview Questions and Answers

## Beginner Level Questions

### Q1: What is Pandas and why is it important for data science?

**Answer:**

Pandas is an open-source data analysis and manipulation library for Python, built on top of NumPy. It provides high-performance, easy-to-use data structures and data analysis tools, making it the de facto standard for data manipulation in Python.

**Key Importance:**
- **Data structures**: DataFrame and Series for structured data manipulation
- **Data I/O**: Read/write data from CSV, Excel, JSON, SQL, Parquet, and more
- **Data cleaning**: Built-in functions for handling missing data, duplicates, outliers
- **Data transformation**: Grouping, pivoting, merging, reshaping operations
- **Time series**: Comprehensive support for time-series data analysis
- **Performance**: Built on NumPy for fast, vectorized operations

**Key Use Cases:**
- Data exploration and analysis
- Data cleaning and preprocessing
- ETL (Extract, Transform, Load) pipelines
- Feature engineering for machine learning
- Time series analysis
- Data visualization preparation

### Q2: What is the difference between a Pandas Series and DataFrame?

**Answer:**

**Series:**
- **One-dimensional**: Single column of data
- **Single data type**: All elements must be same type (unless object)
- **Indexed**: Has an index for labeling
- **Homogeneous**: Typically one data type per Series

**DataFrame:**
- **Two-dimensional**: Multiple columns and rows
- **Multiple data types**: Different columns can have different types
- **Labeled**: Has both row index and column labels
- **Heterogeneous**: Can mix data types across columns

**Relationship:**
- DataFrame is a collection of Series objects
- Each column in a DataFrame is a Series
- Series can become a column in a DataFrame

**Example:**
```python
import pandas as pd

# Series
s = pd.Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])
print(s.shape)  # (4,)

# DataFrame
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df.shape)  # (3, 2)

# DataFrame columns are Series
print(type(df['A']))  # <class 'pandas.core.series.Series'>
```

### Q3: How do you read data from different file formats in Pandas?

**Answer:**

```python
import pandas as pd

# CSV
df = pd.read_csv('data.csv')
df = pd.read_csv('data.csv', sep=',', header=0, index_col=0)

# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# JSON
df = pd.read_json('data.json')
df = pd.read_json('data.json', lines=True)  # JSONL

# Parquet
df = pd.read_parquet('data.parquet')

# SQL
import sqlite3
conn = sqlite3.connect('database.db')
df = pd.read_sql('SELECT * FROM table', conn)
df = pd.read_sql_table('table_name', conn)

# HTML tables
df = pd.read_html('https://example.com/table.html')[0]

# URL
df = pd.read_csv('https://example.com/data.csv')

# With options
df = pd.read_csv('data.csv',
                 parse_dates=['date_col'],
                 dtype={'col1': 'str'},
                 na_values=['NULL', 'N/A'],
                 nrows=1000,  # Read only first 1000 rows
                 chunksize=10000)  # Read in chunks
```

### Q4: How do you handle missing data in Pandas?

**Answer:**

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'A': [1, 2, np.nan, 4],
    'B': [5, np.nan, 7, 8],
    'C': [9, 10, 11, 12]
})

# Check for missing values
print(df.isnull())        # Boolean DataFrame
print(df.isnull().sum())  # Count per column
print(df.isnull().any())  # Any missing values

# Drop missing values
df.dropna()                     # Drop rows with any NaN
df.dropna(subset=['A'])        # Drop rows where A is NaN
df.dropna(how='all')           # Drop rows where all are NaN
df.dropna(axis=1)              # Drop columns with NaN
df.dropna(thresh=2)            # Drop rows with < 2 non-NaN values

# Fill missing values
df.fillna(0)                    # Fill with 0
df.fillna(df.mean())           # Fill with column mean
df['A'].fillna(df['A'].mean()) # Fill specific column
df.fillna(method='ffill')      # Forward fill
df.fillna(method='bfill')      # Backward fill

# Fill with dictionary
df.fillna({'A': df['A'].mean(), 'B': df['B'].median()})

# Interpolation
df.interpolate()                # Linear interpolation
df.interpolate(method='polynomial', order=2)

# Replace values
df.replace(np.nan, 0)
df.replace([np.nan, -1], 0)    # Replace multiple values
```

### Q5: Explain the difference between loc, iloc, and boolean indexing.

**Answer:**

**loc - Label-based indexing:**
```python
# Uses labels/index names
df.loc[0]              # Row with index label 0
df.loc[0:5]            # Rows 0 to 5 (inclusive)
df.loc[0, 'Name']      # Single value
df.loc[0:5, 'Name':'Age']  # Slice of rows and columns
df.loc[df['Age'] > 30]     # Boolean indexing with loc
```

**iloc - Integer position-based indexing:**
```python
# Uses integer positions
df.iloc[0]             # First row (position 0)
df.iloc[0:5]           # Rows 0 to 4 (exclusive, like Python slicing)
df.iloc[0, 1]          # Row 0, Column 1
df.iloc[0:5, 0:3]      # Slice of rows and columns
df.iloc[[0, 2, 4]]     # Specific rows
```

**Boolean Indexing:**
```python
# Filter rows based on conditions
df[df['Age'] > 30]                    # Simple condition
df[(df['Age'] > 30) & (df['Salary'] > 50000)]  # Multiple conditions
df[df['City'].isin(['NYC', 'LA'])]   # Isin check
df[df['Name'].str.contains('John')]  # String contains

# Using query() method
df.query('Age > 30')
df.query('Age > 30 and Salary > 50000')
df.query('City in ["NYC", "LA"]')
```

## Intermediate Level Questions

### Q6: How do you perform groupby operations in Pandas?

**Answer:**

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'City': ['NYC', 'NYC', 'LA', 'LA', 'Chicago', 'Chicago'],
    'Department': ['Sales', 'IT', 'Sales', 'IT', 'Sales', 'IT'],
    'Salary': [75000, 85000, 70000, 90000, 72000, 88000],
    'Age': [25, 30, 28, 32, 26, 31]
})

# Basic grouping
grouped = df.groupby('City')
grouped = df.groupby(['City', 'Department'])

# Aggregation
df.groupby('City').sum()
df.groupby('City').mean()
df.groupby('City').agg({
    'Salary': ['mean', 'sum', 'count'],
    'Age': ['mean', 'std']
})

# Multiple aggregations
df.groupby('City')['Salary'].agg(['mean', 'sum', 'count', 'std'])

# Custom aggregation function
def salary_range(series):
    return series.max() - series.min()

df.groupby('City')['Salary'].agg(salary_range)

# Transform (keep same shape)
df['CityMeanSalary'] = df.groupby('City')['Salary'].transform('mean')
df['ZScore'] = (df['Salary'] - df.groupby('City')['Salary'].transform('mean')) / df.groupby('City')['Salary'].transform('std')

# Filter groups
df.groupby('City').filter(lambda x: len(x) > 1)  # Groups with more than 1 row

# Apply custom function
df.groupby('City').apply(lambda x: x.nlargest(2, 'Salary'))
```

### Q7: How do you merge and join DataFrames in Pandas?

**Answer:**

```python
import pandas as pd

df1 = pd.DataFrame({'key': ['A', 'B', 'C'], 'value1': [1, 2, 3]})
df2 = pd.DataFrame({'key': ['A', 'B', 'D'], 'value2': [4, 5, 6]})

# Inner join (common keys only)
inner = pd.merge(df1, df2, on='key', how='inner')

# Left join (all left + matching right)
left = pd.merge(df1, df2, on='key', how='left')

# Right join (all right + matching left)
right = pd.merge(df1, df2, on='key', how='right')

# Outer join (all keys from both)
outer = pd.merge(df1, df2, on='key', how='outer')

# Join on different column names
df1 = pd.DataFrame({'key1': ['A', 'B'], 'value1': [1, 2]})
df2 = pd.DataFrame({'key2': ['A', 'B'], 'value2': [3, 4]})
result = pd.merge(df1, df2, left_on='key1', right_on='key2')

# Join on index
df1.set_index('key', inplace=True)
df2.set_index('key', inplace=True)
result = df1.join(df2, how='left')

# Multiple keys
df1 = pd.DataFrame({'key1': ['A', 'A'], 'key2': [1, 2], 'value1': [1, 2]})
df2 = pd.DataFrame({'key1': ['A', 'A'], 'key2': [1, 3], 'value2': [3, 4]})
result = pd.merge(df1, df2, on=['key1', 'key2'])

# Suffixes for overlapping columns
result = pd.merge(df1, df2, on='key', suffixes=('_left', '_right'))

# Indicator for join type
result = pd.merge(df1, df2, on='key', how='outer', indicator=True)
```

### Q8: How do you create and work with pivot tables in Pandas?

**Answer:**

```python
import pandas as pd

df = pd.DataFrame({
    'Region': ['North', 'North', 'South', 'South', 'East', 'East'],
    'Quarter': ['Q1', 'Q2', 'Q1', 'Q2', 'Q1', 'Q2'],
    'Sales': [100, 120, 90, 110, 95, 105],
    'Profit': [20, 25, 18, 22, 19, 21]
})

# Create pivot table
pivot = df.pivot_table(
    values='Sales',
    index='Region',
    columns='Quarter',
    aggfunc='sum'
)

# Multiple values
pivot = df.pivot_table(
    values=['Sales', 'Profit'],
    index='Region',
    columns='Quarter',
    aggfunc={'Sales': 'sum', 'Profit': 'mean'}
)

# Multiple aggregation functions
pivot = df.pivot_table(
    values='Sales',
    index='Region',
    columns='Quarter',
    aggfunc=['sum', 'mean']
)

# Fill missing values
pivot = df.pivot_table(
    values='Sales',
    index='Region',
    columns='Quarter',
    aggfunc='sum',
    fill_value=0
)

# Add margins
pivot = df.pivot_table(
    values='Sales',
    index='Region',
    columns='Quarter',
    aggfunc='sum',
    margins=True
)

# Melt (wide to long)
df_long = pd.melt(df, id_vars=['Region', 'Quarter'], value_vars=['Sales', 'Profit'], var_name='Metric', value_name='Value')

# Pivot back (long to wide)
df_wide = df_long.pivot(index='Region', columns='Quarter', values='Value')
```

### Q9: What are the best practices for Pandas performance optimization?

**Answer:**

**1. Use Vectorized Operations:**
```python
# ❌ Slow: Loop
for i in range(len(df)):
    df.loc[i, 'New'] = df.loc[i, 'A'] * 2

# ✅ Fast: Vectorized
df['New'] = df['A'] * 2
```

**2. Specify Data Types When Reading:**
```python
# ✅ Specify dtypes to avoid memory waste
df = pd.read_csv('data.csv', dtype={'Age': 'int32', 'Salary': 'float32'})
```

**3. Use Categorical for Repeated Strings:**
```python
# ✅ Memory efficient
df['City'] = df['City'].astype('category')

# Check memory savings
print(f"Memory: {df['City'].memory_usage(deep=True)}")
```

**4. Use Query for Complex Filtering:**
```python
# ✅ Cleaner and often faster
df.query('Age > 30 and Salary > 50000')

# ❌ Less readable
df[(df['Age'] > 30) & (df['Salary'] > 50000)]
```

**5. Use Method Chaining:**
```python
# ✅ Clean and efficient
result = (df
    .query('Age > 25')
    .groupby('City')
    .agg({'Salary': 'mean'})
    .sort_values('Salary')
    .head(10))
```

**6. Read Large Files in Chunks:**
```python
# ✅ For large files
chunk_size = 100000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

**7. Use eval() for Complex Expressions:**
```python
# ✅ Faster for complex expressions
df.eval('C = A + B', inplace=True)
```

### Q10: How do you work with time series data in Pandas?

**Answer:**

```python
import pandas as pd
import numpy as np

# Create time series data
dates = pd.date_range('2024-01-01', periods=365, freq='D')
df = pd.DataFrame({
    'Date': dates,
    'Sales': np.random.randn(365).cumsum() + 100,
    'Profit': np.random.randn(365).cumsum() + 20
})

# Set Date as index
df.set_index('Date', inplace=True)

# Date operations
df['Year'] = df.index.year
df['Month'] = df.index.month
df['Day'] = df.index.day
df['DayOfWeek'] = df.index.dayofweek
df['IsWeekend'] = df.index.dayofweek.isin([5, 6])

# Resampling
daily = df.resample('D').mean()
weekly = df.resample('W').sum()
monthly = df.resample('M').agg({'Sales': 'sum', 'Profit': 'mean'})
yearly = df.resample('Y').sum()

# Time shifting
df['Sales_Lag1'] = df['Sales'].shift(1)      # Previous day
df['Sales_Lead1'] = df['Sales'].shift(-1)    # Next day
df['Sales_Diff'] = df['Sales'].diff()        # Difference

# Rolling windows
df['RollingMean_7'] = df['Sales'].rolling(window=7).mean()
df['RollingStd_30'] = df['Sales'].rolling(window=30).std()
df['ExpandingMean'] = df['Sales'].expanding().mean()

# Time zone handling
df.index = df.index.tz_localize('UTC')
df.index = df.index.tz_convert('America/New_York')

# Time-based selection
df['2024-01']                           # January 2024
df['2024-01-01':'2024-01-31']          # Date range
df.between_time('09:00', '17:00')      # Time range
```

## Advanced Level Questions

### Q11: How do you optimize memory usage in Pandas?

**Answer:**

```python
import pandas as pd

# Check memory usage
print(df.memory_usage(deep=True))
print(f"Total: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Optimize integer columns
df['Age'] = pd.to_numeric(df['Age'], downcast='integer')
# int64 -> int8/int16/int32 if possible

# Optimize float columns
df['Salary'] = pd.to_numeric(df['Salary'], downcast='float')
# float64 -> float32 if precision allows

# Use categorical for repeated strings
df['City'] = df['City'].astype('category')
# Can reduce memory by 80-90% for repeated strings

# Use sparse for mostly zero columns
df['SparseCol'] = df['SparseCol'].astype('Sparse[int]')

# Check optimization results
print(f"Before: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
df_optimized = df.copy()
df_optimized['City'] = df_optimized['City'].astype('category')
df_optimized['Age'] = pd.to_numeric(df_optimized['Age'], downcast='integer')
print(f"After: {df_optimized.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
```

### Q12: Explain MultiIndex and how to work with it.

**Answer:**

```python
import pandas as pd
import numpy as np

# Create MultiIndex
arrays = [['A', 'A', 'B', 'B'], ['one', 'two', 'one', 'two']]
index = pd.MultiIndex.from_arrays(arrays, names=['first', 'second'])
df = pd.DataFrame(np.random.randn(4, 3), index=index, columns=['X', 'Y', 'Z'])

# Access MultiIndex
df.loc['A']                  # All rows with first level 'A'
df.loc[('A', 'one')]         # Specific row
df.loc['A', 'one']           # Alternative syntax
df.xs('one', level='second') # Cross-section

# Stack and unstack
stacked = df.stack()         # Convert columns to index levels
unstacked = stacked.unstack() # Convert index level to columns

# Swap levels
df.swaplevel('first', 'second')

# Reset index
df.reset_index()             # Convert index to columns

# Set index
df.set_index(['first', 'second'])

# MultiIndex columns
df.columns = pd.MultiIndex.from_tuples([('A', 'X'), ('A', 'Y'), ('B', 'Z')])
df.loc[:, ('A', 'X')]        # Access column
```

### Q13: How do you handle large datasets that don't fit in memory?

**Answer:**

```python
import pandas as pd
import dask.dataframe as dd

# Option 1: Read in chunks
chunk_size = 100000
results = []
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    processed = process_chunk(chunk)
    results.append(processed)
    
final_df = pd.concat(results, ignore_index=True)

# Option 2: Use Dask
dask_df = dd.read_csv('large_file.csv')
result = dask_df.groupby('City').agg({'Sales': 'sum'}).compute()

# Option 3: Filter early
df = pd.read_csv('large_file.csv', 
                 usecols=['Name', 'Age', 'Salary'],  # Only needed columns
                 nrows=1000000)  # Limit rows

# Option 4: Specify data types
df = pd.read_csv('large_file.csv', 
                 dtype={'Age': 'int32', 'Salary': 'float32'})

# Option 5: Use iterator for large files
df_iterator = pd.read_csv('large_file.csv', iterator=True, chunksize=10000)
chunk = df_iterator.get_chunk(10000)

# Option 6: Use Parquet format (compressed)
df.to_parquet('data.parquet', compression='snappy')
df = pd.read_parquet('data.parquet')  # Faster and smaller
```

### Q14: How do you use Pandas with SQL databases?

**Answer:**

```python
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

# SQLite connection
conn = sqlite3.connect('database.db')

# Read from SQL
df = pd.read_sql('SELECT * FROM employees WHERE age > 30', conn)
df = pd.read_sql_table('employees', conn)
df = pd.read_sql_query('SELECT * FROM employees', conn)

# Write to SQL
df.to_sql('employees', conn, if_exists='replace', index=False)
df.to_sql('employees', conn, if_exists='append', index=False)

# Using SQLAlchemy
engine = create_engine('postgresql://user:pass@localhost/dbname')
df = pd.read_sql('SELECT * FROM table', engine)
df.to_sql('table', engine, if_exists='replace')

# PostgreSQL
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/dbname')
df = pd.read_sql_query('SELECT * FROM table', engine)

# MySQL
engine = create_engine('mysql+pymysql://user:pass@localhost/dbname')
df = pd.read_sql_query('SELECT * FROM table', engine)
```

### Q15: How do you handle duplicate data in Pandas?

**Answer:

```python
import pandas as pd

df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob'],
    'Age': [25, 30, 25, 35, 30],
    'City': ['NYC', 'LA', 'NYC', 'Chicago', 'LA']
})

# Find duplicates
df.duplicated()                      # Boolean Series
df.duplicated(subset=['Name'])      # Check specific columns
df.duplicated(subset=['Name', 'Age'], keep='first')

# Drop duplicates
df.drop_duplicates()                 # Drop all duplicate rows
df.drop_duplicates(subset=['Name'])  # Drop based on specific columns
df.drop_duplicates(keep='first')     # Keep first occurrence
df.drop_duplicates(keep='last')      # Keep last occurrence
df.drop_duplicates(keep=False)       # Drop all duplicates

# Count duplicates
df.duplicated().sum()

# View duplicates
df[df.duplicated(keep=False)]       # Show all duplicate rows
```

## Practical Coding Questions

### Q16: Write a function to clean a DataFrame: handle missing values, duplicates, and type conversions.

**Answer:**

```python
import pandas as pd
import numpy as np

def clean_dataframe(df, missing_strategy='mean', drop_duplicates=True):
    """
    Clean DataFrame: handle missing values, duplicates, and type conversions
    """
    df_clean = df.copy()
    
    # Handle missing values
    if missing_strategy == 'mean':
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
    elif missing_strategy == 'drop':
        df_clean = df_clean.dropna()
    elif missing_strategy == 'forward':
        df_clean = df_clean.fillna(method='ffill')
    
    # Drop duplicates
    if drop_duplicates:
        df_clean = df_clean.drop_duplicates()
    
    # Optimize data types
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            # Try to convert to numeric
            try:
                df_clean[col] = pd.to_numeric(df_clean[col], downcast='integer')
            except:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col])
                except:
                    # Check if categorical makes sense
                    if df_clean[col].nunique() / len(df_clean) < 0.5:
                        df_clean[col] = df_clean[col].astype('category')
    
    return df_clean

# Usage
df_cleaned = clean_dataframe(df, missing_strategy='mean', drop_duplicates=True)
```

## References

- Official Pandas documentation: https://pandas.pydata.org/docs/
- Pandas GitHub: https://github.com/pandas-dev/pandas
- User guide: https://pandas.pydata.org/docs/user_guide/index.html
- API reference: https://pandas.pydata.org/docs/reference/index.html
- 10 minutes to pandas: https://pandas.pydata.org/docs/user_guide/10min.html













