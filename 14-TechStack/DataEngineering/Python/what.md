# Python for Data Engineering: Comprehensive Guide

## Overview

Python is a high-level, interpreted programming language widely used in data engineering for ETL pipelines, data processing, API development, and automation. Its simplicity, extensive libraries, and strong community make it ideal for data engineering tasks.

## Core Concepts

### What is Python for Data Engineering?

Python is a high-level, interpreted programming language widely used in data engineering for ETL pipelines, data processing, API development, and automation. Its simplicity, extensive libraries, and strong community make it ideal for data engineering tasks.

## Key Features

**Simple Syntax**: Easy to read and write

**Rich Libraries**: Pandas, NumPy, Apache Airflow, etc.

**Rapid Development**: Fast prototyping and iteration

**Integration**: Easy integration with databases and APIs

**Community**: Large community and extensive documentation

**Versatility**: Scripting, web development, data science

## Installation

# Install Python
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install pandas numpy apache-airflow

## Getting Started

```python
# ETL Pipeline
import pandas as pd
from sqlalchemy import create_engine

# Extract
df = pd.read_csv('data.csv')

# Transform
df['processed_date'] = pd.to_datetime(df['date'])
df = df[df['value'] > 0]
df = df.groupby('category').agg({'value': 'sum'}).reset_index()

# Load
engine = create_engine('postgresql://user:pass@localhost/db')
df.to_sql('results', engine, if_exists='replace', index=False)
```

## Advanced Usage

```python
# Async data processing
import asyncio
import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_multiple_sources(urls):
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Airflow DAG
from airflow import DAG
from airflow.operators.python import PythonOperator

def process_data():
    # Data processing logic
    pass

dag = DAG('data_pipeline', schedule_interval='@daily')
task = PythonOperator(task_id='process', python_callable=process_data, dag=dag)
```

## Best Practices

1. Use virtual environments for project isolation
2. Follow PEP 8 style guide
3. Use type hints for better code documentation
4. Handle exceptions properly
5. Use list comprehensions and generators for efficiency
6. Leverage libraries instead of reinventing the wheel
7. Write unit tests for critical functions

## References

- Official documentation: 
- GitHub repository:
