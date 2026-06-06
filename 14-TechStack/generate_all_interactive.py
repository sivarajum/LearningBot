#!/usr/bin/env python3
"""
Script to generate all missing interactive HTML files based on Python template
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Read Python template
with open(BASE_DIR / 'Python/interactive-python.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Technology configurations
TECHNOLOGIES = {
    'ApacheKafka': {
        'title': 'Apache Kafka Interactive Demo',
        'name': 'Apache Kafka',
        'icon': 'fas fa-stream',
        'description': 'Event streaming platform for building real-time data pipelines',
        'primary': '#231F20',
        'secondary': '#FFA500',
        'bg_gradient': 'linear-gradient(135deg, #231F20 0%, #FFA500 100%)',
        'flow_gradient': 'linear-gradient(90deg, #231F20, #FFA500)',
        'code_sample': '''# Apache Kafka Producer Example
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Publish message
producer.send('my-topic', {'key': 'value', 'message': 'Hello Kafka'})
producer.flush()

# Apache Kafka Consumer Example
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Consume messages
for message in consumer:
    print(f"Received: {message.value}")'''
    },
    'BigQuery': {
        'title': 'BigQuery Interactive Demo',
        'name': 'BigQuery',
        'icon': 'fab fa-google',
        'description': 'Serverless, highly scalable data warehouse for analytics',
        'primary': '#4285F4',
        'secondary': '#34A853',
        'bg_gradient': 'linear-gradient(135deg, #4285F4 0%, #34A853 100%)',
        'flow_gradient': 'linear-gradient(90deg, #4285F4, #34A853)',
        'code_sample': '''-- BigQuery SQL Examples

-- Create a table
CREATE TABLE my_dataset.my_table (
    id INT64,
    name STRING,
    created_at TIMESTAMP
);

-- Query data
SELECT 
    name,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP() - created_at))) as avg_age
FROM my_dataset.my_table
WHERE created_at > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY name
ORDER BY count DESC;'''
    },
    'LLMOps': {
        'title': 'LLMOps Interactive Demo',
        'name': 'LLMOps',
        'icon': 'fas fa-robot',
        'description': 'Operations for deploying and managing Large Language Models in production',
        'primary': '#9333EA',
        'secondary': '#EC4899',
        'bg_gradient': 'linear-gradient(135deg, #9333EA 0%, #EC4899 100%)',
        'flow_gradient': 'linear-gradient(90deg, #9333EA, #EC4899)',
        'code_sample': '''# LLMOps Pipeline Example
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
import mlflow

# Version prompts
prompt_template = PromptTemplate(
    input_variables=["query"],
    template="Answer this question: {query}"
)

# Log to MLflow
with mlflow.start_run():
    mlflow.log_param("model_type", "gpt-4")
    mlflow.log_param("temperature", 0.7)
    
    # Track prompt version
    mlflow.log_text(prompt_template.template, "prompt.txt")
    
    # Deploy and monitor
    llm = OpenAI(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    result = chain.run("What is LLMOps?")
    mlflow.log_metric("response_length", len(result))'''
    },
    'MachineLearning': {
        'title': 'Machine Learning Interactive Demo',
        'name': 'Machine Learning',
        'icon': 'fas fa-brain',
        'description': 'Build intelligent systems with machine learning algorithms',
        'primary': '#8B5CF6',
        'secondary': '#EC4899',
        'bg_gradient': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
        'flow_gradient': 'linear-gradient(90deg, #8B5CF6, #EC4899)',
        'code_sample': '''# Machine Learning Pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

# Load data
data = pd.read_csv('data.csv')
X = data.drop('target', axis=1)
y = data['target']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy:.2f}")
print(classification_report(y_test, predictions))'''
    },
    'Real-TimeProcessing': {
        'title': 'Real-Time Processing Interactive Demo',
        'name': 'Real-Time Processing',
        'icon': 'fas fa-bolt',
        'description': 'Process and analyze data streams in real-time',
        'primary': '#F59E0B',
        'secondary': '#EF4444',
        'bg_gradient': 'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
        'flow_gradient': 'linear-gradient(90deg, #F59E0B, #EF4444)',
        'code_sample': '''# Real-Time Stream Processing
from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime

# Consumer
consumer = KafkaConsumer(
    'input-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Process stream
for message in consumer:
    data = message.value
    
    # Real-time processing
    processed = {
        'original': data,
        'processed_at': datetime.now().isoformat(),
        'enriched': enrich_data(data)
    }
    
    # Output to next topic
    producer.send('output-topic', processed)'''
    },
    'Scala': {
        'title': 'Scala Interactive Demo',
        'name': 'Scala',
        'icon': 'fab fa-java',
        'description': 'Scalable language for functional and object-oriented programming',
        'primary': '#DC322F',
        'secondary': '#005AA0',
        'bg_gradient': 'linear-gradient(135deg, #DC322F 0%, #005AA0 100%)',
        'flow_gradient': 'linear-gradient(90deg, #DC322F, #005AA0)',
        'code_sample': '''// Scala Example
object HelloWorld extends App {
  println("Hello, World!")
}

// Functional programming
val numbers = List(1, 2, 3, 4, 5)
val doubled = numbers.map(_ * 2)
val evens = numbers.filter(_ % 2 == 0)

// Case classes
case class Person(name: String, age: Int)
val person = Person("Alice", 30)

// Pattern matching
def matchExample(x: Any): String = x match {
  case 1 => "one"
  case "hello" => "greeting"
  case Person(name, age) => s"Person: $name, $age"
  case _ => "unknown"
}'''
    },
    'DataModeling': {
        'title': 'Data Modeling Interactive Demo',
        'name': 'Data Modeling',
        'icon': 'fas fa-sitemap',
        'description': 'Design and structure data for efficient storage and retrieval',
        'primary': '#6366F1',
        'secondary': '#8B5CF6',
        'bg_gradient': 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
        'flow_gradient': 'linear-gradient(90deg, #6366F1, #8B5CF6)',
        'code_sample': '''-- Data Modeling Example
-- Entity-Relationship Model

CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    total_amount DECIMAL(10, 2),
    order_date TIMESTAMP,
    status VARCHAR(20)
);

CREATE TABLE order_items (
    item_id INT PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT,
    quantity INT,
    price DECIMAL(10, 2)
);'''
    },
    'DataPipelines': {
        'title': 'Data Pipelines Interactive Demo',
        'name': 'Data Pipelines',
        'icon': 'fas fa-project-diagram',
        'description': 'ETL/ELT pipelines for data transformation and movement',
        'primary': '#3B82F6',
        'secondary': '#10B981',
        'bg_gradient': 'linear-gradient(135deg, #3B82F6 0%, #10B981 100%)',
        'flow_gradient': 'linear-gradient(90deg, #3B82F6, #10B981)',
        'code_sample': '''# Data Pipeline Example
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def extract_data():
    data = fetch_from_source()
    return data

def transform_data(**context):
    data = context['task_instance'].xcom_pull(task_ids='extract')
    transformed = data.apply(transform_function)
    return transformed

def load_data(**context):
    data = context['task_instance'].xcom_pull(task_ids='transform')
    load_to_destination(data)

dag = DAG(
    'data_pipeline',
    default_args={'start_date': datetime(2024, 1, 1)},
    schedule_interval=timedelta(hours=1)
)

extract = PythonOperator(task_id='extract', python_callable=extract_data, dag=dag)
transform = PythonOperator(task_id='transform', python_callable=transform_data, dag=dag)
load = PythonOperator(task_id='load', python_callable=load_data, dag=dag)

extract >> transform >> load'''
    },
    'DataWarehousing': {
        'title': 'Data Warehousing Interactive Demo',
        'name': 'Data Warehousing',
        'icon': 'fas fa-warehouse',
        'description': 'Centralized repository for integrated data from multiple sources',
        'primary': '#667EEA',
        'secondary': '#764BA2',
        'bg_gradient': 'linear-gradient(135deg, #667EEA 0%, #764BA2 100%)',
        'flow_gradient': 'linear-gradient(90deg, #667EEA, #764BA2)',
        'code_sample': '''-- Data Warehouse Schema
-- Star Schema Example

CREATE TABLE fact_sales (
    sale_id INT PRIMARY KEY,
    product_id INT,
    customer_id INT,
    date_id INT,
    quantity INT,
    amount DECIMAL(10, 2)
);

CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    brand VARCHAR(50)
);

CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50)
);'''
    },
    'VertexAI': {
        'title': 'Vertex AI Interactive Demo',
        'name': 'Vertex AI',
        'icon': 'fab fa-google',
        'description': 'Unified ML platform for training, deploying, and managing ML models',
        'primary': '#4285F4',
        'secondary': '#34A853',
        'bg_gradient': 'linear-gradient(135deg, #4285F4 0%, #34A853 100%)',
        'flow_gradient': 'linear-gradient(90deg, #4285F4, #34A853)',
        'code_sample': '''# Vertex AI Example
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(project='my-project', location='us-central1')

# Create a custom training job
job = aiplatform.CustomTrainingJob(
    display_name='my-training-job',
    script_path='training_script.py',
    container_uri='gcr.io/my-project/trainer:latest'
)

# Run training
model = job.run(
    replica_count=1,
    machine_type='n1-standard-4'
)

# Deploy model
endpoint = model.deploy(
    deployed_model_display_name='my-model',
    machine_type='n1-standard-2',
    min_replica_count=1,
    max_replica_count=3
)'''
    },
    # Tools subdirectories
    'Tools/Git': {
        'title': 'Git Interactive Demo',
        'name': 'Git',
        'icon': 'fab fa-git-alt',
        'description': 'Distributed version control system for tracking changes',
        'primary': '#F05032',
        'secondary': '#F14E32',
        'bg_gradient': 'linear-gradient(135deg, #F05032 0%, #F14E32 100%)',
        'flow_gradient': 'linear-gradient(90deg, #F05032, #F14E32)',
        'code_sample': '''# Git Commands
git init                    # Initialize repository
git add .                   # Stage all files
git commit -m "Initial commit"  # Commit changes
git branch main             # Create branch
git checkout main           # Switch branch
git merge feature           # Merge branches
git push origin main        # Push to remote
git pull origin main        # Pull from remote
git clone <repo-url>        # Clone repository'''
    },
    'Tools/NumPy': {
        'title': 'NumPy Interactive Demo',
        'name': 'NumPy',
        'icon': 'fas fa-calculator',
        'description': 'Fundamental package for scientific computing with Python',
        'primary': '#4DABCF',
        'secondary': '#C13C37',
        'bg_gradient': 'linear-gradient(135deg, #4DABCF 0%, #C13C37 100%)',
        'flow_gradient': 'linear-gradient(90deg, #4DABCF, #C13C37)',
        'code_sample': '''import numpy as np

# Create arrays
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])
zeros = np.zeros((3, 3))
ones = np.ones((2, 4))

# Array operations
result = arr * 2
sum_val = np.sum(arr)
mean_val = np.mean(arr)
std_val = np.std(arr)

# Matrix operations
dot_product = np.dot(matrix, matrix)
transpose = matrix.T

print(f"Array: {arr}")
print(f"Mean: {mean_val}")'''
    },
    'Tools/Pandas': {
        'title': 'Pandas Interactive Demo',
        'name': 'Pandas',
        'icon': 'fas fa-table',
        'description': 'Powerful data manipulation and analysis library',
        'primary': '#150458',
        'secondary': '#130654',
        'bg_gradient': 'linear-gradient(135deg, #150458 0%, #130654 100%)',
        'flow_gradient': 'linear-gradient(90deg, #150458, #130654)',
        'code_sample': '''import pandas as pd

# Create DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['NYC', 'LA', 'Chicago']
}
df = pd.DataFrame(data)

# Data operations
filtered = df[df['Age'] > 25]
grouped = df.groupby('City').mean()
sorted_df = df.sort_values('Age')

# Read/write data
df_csv = pd.read_csv('data.csv')
df_csv.to_csv('output.csv', index=False)

print(df.head())
print(f"\\nFiltered:\\n{filtered}")'''
    },
    'Tools/Matplotlib': {
        'title': 'Matplotlib Interactive Demo',
        'name': 'Matplotlib',
        'icon': 'fas fa-chart-line',
        'description': 'Plotting library for creating static, animated, and interactive visualizations',
        'primary': '#11557C',
        'secondary': '#4584B6',
        'bg_gradient': 'linear-gradient(135deg, #11557C 0%, #4584B6 100%)',
        'flow_gradient': 'linear-gradient(90deg, #11557C, #4584B6)',
        'code_sample': '''import matplotlib.pyplot as plt
import numpy as np

# Create data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='sin(x)')
plt.xlabel('X values')
plt.ylabel('Y values')
plt.title('Sine Wave')
plt.legend()
plt.grid(True)

# Save figure
plt.savefig('plot.png', dpi=300)
plt.show()'''
    },
    # Gen-AI subdirectories
    'Gen-AI/LangChain': {
        'title': 'LangChain Interactive Demo',
        'name': 'LangChain',
        'icon': 'fas fa-link',
        'description': 'Framework for developing applications powered by language models',
        'primary': '#10B981',
        'secondary': '#059669',
        'bg_gradient': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
        'flow_gradient': 'linear-gradient(90deg, #10B981, #059669)',
        'code_sample': '''from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

# Create prompt template
template = "Question: {question}\\nAnswer:"
prompt = PromptTemplate(template=template, input_variables=["question"])

# Create LLM chain
llm = OpenAI(temperature=0.7)
chain = LLMChain(llm=llm, prompt=prompt)

# Run chain
result = chain.run("What is LangChain?")
print(result)'''
    },
    'Gen-AI/Vector-Databases': {
        'title': 'Vector Databases Interactive Demo',
        'name': 'Vector Databases',
        'icon': 'fas fa-database',
        'description': 'Databases optimized for storing and querying vector embeddings',
        'primary': '#6366F1',
        'secondary': '#8B5CF6',
        'bg_gradient': 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
        'flow_gradient': 'linear-gradient(90deg, #6366F1, #8B5CF6)',
        'code_sample': '''# Vector Database Example (Pinecone)
from pinecone import Pinecone
import numpy as np

# Initialize Pinecone
pc = Pinecone(api_key="your-api-key")
index = pc.Index("my-index")

# Create vectors
vectors = [
    ("id1", [0.1, 0.2, 0.3, 0.4]),
    ("id2", [0.2, 0.3, 0.4, 0.5])
]

# Upsert vectors
index.upsert(vectors=vectors)

# Query similar vectors
query_vector = [0.15, 0.25, 0.35, 0.45]
results = index.query(
    vector=query_vector,
    top_k=3,
    include_metadata=True
)'''
    },
    # DataEngineering subdirectories
    'DataEngineering/Kafka': {
        'title': 'Kafka (Data Engineering) Interactive Demo',
        'name': 'Kafka',
        'icon': 'fas fa-stream',
        'description': 'Distributed event streaming platform for real-time data processing',
        'primary': '#231F20',
        'secondary': '#FFA500',
        'bg_gradient': 'linear-gradient(135deg, #231F20 0%, #FFA500 100%)',
        'flow_gradient': 'linear-gradient(90deg, #231F20, #FFA500)',
        'code_sample': '''# Kafka Producer for Data Engineering
from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Stream data
for i in range(100):
    data = {
        'id': i,
        'timestamp': time.time(),
        'value': i * 2
    }
    producer.send('data-stream', data)
    time.sleep(0.1)

producer.flush()'''
    },
    'DataEngineering/SQL': {
        'title': 'SQL (Data Engineering) Interactive Demo',
        'name': 'SQL',
        'icon': 'fas fa-database',
        'description': 'Structured Query Language for managing relational databases',
        'primary': '#336791',
        'secondary': '#CC2927',
        'bg_gradient': 'linear-gradient(135deg, #336791 0%, #CC2927 100%)',
        'flow_gradient': 'linear-gradient(90deg, #336791, #CC2927)',
        'code_sample': '''-- SQL Data Engineering Examples

-- Create table
CREATE TABLE sales (
    sale_id INT PRIMARY KEY,
    product_id INT,
    sale_date DATE,
    amount DECIMAL(10, 2)
);

-- Insert data
INSERT INTO sales VALUES
(1, 101, '2024-01-15', 1500.00),
(2, 102, '2024-01-16', 2300.00);

-- Aggregate queries
SELECT 
    product_id,
    COUNT(*) as total_sales,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_sale
FROM sales
WHERE sale_date >= '2024-01-01'
GROUP BY product_id
ORDER BY total_revenue DESC;'''
    },
    'dbt': {
        'title': 'dbt Interactive Demo',
        'name': 'dbt',
        'icon': 'fas fa-cube',
        'description': 'Data build tool for transforming data in your warehouse',
        'primary': '#FF694B',
        'secondary': '#FFD700',
        'bg_gradient': 'linear-gradient(135deg, #FF694B 0%, #FFD700 100%)',
        'flow_gradient': 'linear-gradient(90deg, #FF694B, #FFD700)',
        'code_sample': '''-- dbt Model Example

{{ config(materialized='table') }}

WITH source_data AS (
    SELECT * FROM {{ source('raw_data', 'orders') }}
),

transformed_data AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        total_amount,
        CASE
            WHEN total_amount > 1000 THEN 'High Value'
            ELSE 'Standard'
        END AS order_category
    FROM source_data
    WHERE order_date >= '2024-01-01'
)

SELECT * FROM transformed_data'''
    },
    # More Tools subdirectories
    'Tools/Jupyter': {
        'title': 'Jupyter Interactive Demo',
        'name': 'Jupyter',
        'icon': 'fas fa-book',
        'description': 'Interactive computing platform for creating computational documents',
        'primary': '#F37626',
        'secondary': '#56B82C',
        'bg_gradient': 'linear-gradient(135deg, #F37626 0%, #56B82C 100%)',
        'flow_gradient': 'linear-gradient(90deg, #F37626, #56B82C)',
        'code_sample': '''# Jupyter Notebook Cell Example
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('data.csv')

# Data analysis
print(df.describe())
print(f"Shape: {df.shape}")

# Visualization
df['column'].hist(bins=50)
plt.title('Distribution')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.show()

# Display results
df.head()'''
    },
    'Tools/Plotly': {
        'title': 'Plotly Interactive Demo',
        'name': 'Plotly',
        'icon': 'fas fa-chart-bar',
        'description': 'Interactive visualization library for creating dynamic graphs',
        'primary': '#3F4F75',
        'secondary': '#00BF96',
        'bg_gradient': 'linear-gradient(135deg, #3F4F75 0%, #00BF96 100%)',
        'flow_gradient': 'linear-gradient(90deg, #3F4F75, #00BF96)',
        'code_sample': '''import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Create interactive plot
df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [1, 4, 9, 16, 25],
    'category': ['A', 'B', 'C', 'D', 'E']
})

# Scatter plot
fig = px.scatter(df, x='x', y='y', color='category',
                 title='Interactive Scatter Plot',
                 labels={'x': 'X Axis', 'y': 'Y Axis'})

# Add hover info
fig.update_traces(hovertemplate='<b>%{fullData.name}</b><br>' +
                                  'X: %{x}<br>' +
                                  'Y: %{y}<extra></extra>')

fig.show()'''
    },
    'Tools/Seaborn': {
        'title': 'Seaborn Interactive Demo',
        'name': 'Seaborn',
        'icon': 'fas fa-chart-line',
        'description': 'Statistical data visualization library built on matplotlib',
        'primary': '#3776AB',
        'secondary': '#FFD43B',
        'bg_gradient': 'linear-gradient(135deg, #3776AB 0%, #FFD43B 100%)',
        'flow_gradient': 'linear-gradient(90deg, #3776AB, #FFD43B)',
        'code_sample': '''import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Set style
sns.set_style('darkgrid')

# Load data
df = pd.read_csv('data.csv')

# Create visualizations
# Distribution plot
sns.distplot(df['column'], bins=30)

# Box plot
sns.boxplot(x='category', y='value', data=df)

# Heatmap
correlation = df.corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm')

# Pair plot
sns.pairplot(df, hue='category')

plt.tight_layout()
plt.show()'''
    },
    'Tools/VS-Code': {
        'title': 'VS Code Interactive Demo',
        'name': 'VS Code',
        'icon': 'fas fa-code',
        'description': 'Lightweight, powerful source code editor with extensive extensions',
        'primary': '#007ACC',
        'secondary': '#0066B8',
        'bg_gradient': 'linear-gradient(135deg, #007ACC 0%, #0066B8 100%)',
        'flow_gradient': 'linear-gradient(90deg, #007ACC, #0066B8)',
        'code_sample': '''// VS Code Configuration Example
{
  "editor.fontSize": 14,
  "editor.tabSize": 2,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  },
  "python.defaultInterpreterPath": "./venv/bin/python",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  },
  "extensions.recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance"
  ]
}

// Keyboard shortcuts
// Ctrl+P: Quick file open
// Ctrl+Shift+P: Command palette
// Ctrl+`: Toggle terminal
// Alt+Up/Down: Move line
// Ctrl+D: Select next occurrence'''
    },
    # Gen-AI subdirectories
    'Gen-AI/Embeddings': {
        'title': 'Embeddings Interactive Demo',
        'name': 'Embeddings',
        'icon': 'fas fa-brain',
        'description': 'Vector representations of text for semantic understanding',
        'primary': '#6366F1',
        'secondary': '#EC4899',
        'bg_gradient': 'linear-gradient(135deg, #6366F1 0%, #EC4899 100%)',
        'flow_gradient': 'linear-gradient(90deg, #6366F1, #EC4899)',
        'code_sample': '''# Embeddings Example
from sentence_transformers import SentenceTransformer
import numpy as np

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings
sentences = [
    "The cat sat on the mat",
    "The dog played in the yard",
    "Machine learning is fascinating"
]

embeddings = model.encode(sentences)

# Compute similarity
from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
print(f"Similarity: {similarity:.2f}")

# Search similar documents
query = "The cat"
query_embedding = model.encode([query])
similarities = cosine_similarity(query_embedding, embeddings)[0]
most_similar = np.argmax(similarities)
print(f"Most similar: {sentences[most_similar]}")'''
    },
    'Gen-AI/OpenAI-GPT': {
        'title': 'OpenAI GPT Interactive Demo',
        'name': 'OpenAI GPT',
        'icon': 'fas fa-robot',
        'description': 'Large language models for natural language understanding and generation',
        'primary': '#10A37F',
        'secondary': '#00A86B',
        'bg_gradient': 'linear-gradient(135deg, #10A37F 0%, #00A86B 100%)',
        'flow_gradient': 'linear-gradient(90deg, #10A37F, #00A86B)',
        'code_sample': '''# OpenAI GPT Example
import openai

# Set API key
openai.api_key = 'your-api-key'

# Generate text
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain machine learning in simple terms."}
    ],
    temperature=0.7,
    max_tokens=500
)

print(response.choices[0].message.content)

# Stream response
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Write a Python function"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.get('content'):
        print(chunk.choices[0].delta.content, end='', flush=True)'''
    },
    # DataEngineering subdirectories
    'DataEngineering/Java': {
        'title': 'Java (Data Engineering) Interactive Demo',
        'name': 'Java',
        'icon': 'fab fa-java',
        'description': 'Enterprise-grade programming language for big data processing',
        'primary': '#ED1C24',
        'secondary': '#007ACC',
        'bg_gradient': 'linear-gradient(135deg, #ED1C24 0%, #007ACC 100%)',
        'flow_gradient': 'linear-gradient(90deg, #ED1C24, #007ACC)',
        'code_sample': '''// Java Data Engineering Example
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

public class DataPipeline {
    public static void main(String[] args) {
        // Create Spark session
        SparkSession spark = SparkSession.builder()
            .appName("DataPipeline")
            .master("local[*]")
            .getOrCreate();
        
        // Read data
        Dataset<Row> df = spark.read()
            .option("header", "true")
            .csv("data.csv");
        
        // Transform data
        Dataset<Row> transformed = df
            .filter(df.col("age").$greater(25))
            .groupBy("department")
            .avg("salary");
        
        // Write output
        transformed.write()
            .mode("overwrite")
            .parquet("output/");
        
        spark.stop();
    }
}'''
    },
    'DataEngineering/Python': {
        'title': 'Python (Data Engineering) Interactive Demo',
        'name': 'Python',
        'icon': 'fab fa-python',
        'description': 'Versatile language for ETL pipelines and data processing',
        'primary': '#3776AB',
        'secondary': '#FFD43B',
        'bg_gradient': 'linear-gradient(135deg, #3776AB 0%, #FFD43B 100%)',
        'flow_gradient': 'linear-gradient(90deg, #3776AB, #FFD43B)',
        'code_sample': '''# Python Data Engineering Pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count

# Create Spark session
spark = SparkSession.builder \\
    .appName("DataPipeline") \\
    .getOrCreate()

# Read data
df = spark.read \\
    .option("header", "true") \\
    .csv("data.csv")

# Transform data
transformed = df \\
    .filter(col("age") > 25) \\
    .groupBy("department") \\
    .agg(
        avg("salary").alias("avg_salary"),
        count("*").alias("count")
    )

# Write output
transformed.write \\
    .mode("overwrite") \\
    .parquet("output/")

spark.stop()'''
    },
    'DataEngineering/Scala': {
        'title': 'Scala (Data Engineering) Interactive Demo',
        'name': 'Scala',
        'icon': 'fab fa-java',
        'description': 'Scalable language for Apache Spark and big data processing',
        'primary': '#DC322F',
        'secondary': '#005AA0',
        'bg_gradient': 'linear-gradient(135deg, #DC322F 0%, #005AA0 100%)',
        'flow_gradient': 'linear-gradient(90deg, #DC322F, #005AA0)',
        'code_sample': '''// Scala Data Engineering Example
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object DataPipeline {
  def main(args: Array[String]): Unit = {
    // Create Spark session
    val spark = SparkSession.builder()
      .appName("DataPipeline")
      .master("local[*]")
      .getOrCreate()
    
    // Read data
    val df = spark.read
      .option("header", "true")
      .csv("data.csv")
    
    // Transform data
    val transformed = df
      .filter(col("age") > 25)
      .groupBy("department")
      .agg(
        avg("salary").alias("avg_salary"),
        count("*").alias("count")
      )
    
    // Write output
    transformed.write
      .mode("overwrite")
      .parquet("output/")
    
    spark.stop()
  }
}'''
    }
}

def generate_interactive_html(tech_dir, tech_key, config, subdir=''):
    """Generate interactive HTML file for a technology"""
    
    # Handle subdirectories
    if subdir:
        tech_dir = tech_dir / subdir
    
    # Check if file already exists
    filename = config.get('filename', f"interactive-{tech_key.lower().replace(' ', '-').replace('/', '-')}.html")
    html_file = tech_dir / filename
    if html_file.exists():
        print(f"  ⏭️  Skipping {html_file.name} (already exists)")
        return False
    
    # Ensure directory exists
    tech_dir.mkdir(parents=True, exist_ok=True)
    
    # Replace template values
    html = template
    
    # Replace title
    html = re.sub(r'<title>.*?</title>', f'<title>{config["title"]}</title>', html, flags=re.DOTALL)
    
    # Replace Python-specific with generic
    html = html.replace('Python Interactive Demo', config['title'])
    html = html.replace('<i className="fab fa-python"></i> Python', f'<i className="{config["icon"]}"></i> {config["name"]}')
    html = html.replace('Powerful, versatile programming language for all your needs', config['description'])
    
    # Replace colors
    html = html.replace('--primary-color: #3776AB;', f'--primary-color: {config["primary"]};')
    html = html.replace('--secondary-color: #FFD43B;', f'--secondary-color: {config["secondary"]};')
    html = html.replace('linear-gradient(135deg, #3776AB 0%, #FFD43B 100%)', config['bg_gradient'])
    html = html.replace('linear-gradient(90deg, #3776AB, #4CAF50)', config['flow_gradient'])
    
    # Replace code sample
    code_pattern = r'const \[code, setCode\] = useState\(`[^`]*`\);'
    html = re.sub(code_pattern, f'const [code, setCode] = useState(`{config["code_sample"]}`);', html, flags=re.DOTALL)
    
    # Replace output message
    html = html.replace('Executing Python code...', f'Executing {config["name"]} code...')
    html = html.replace('Python code executed successfully!', f'{config["name"]} code executed successfully!')
    
    # Replace class names (python -> tech-specific)
    tech_class = tech_key.lower().replace('-', '').replace(' ', '')
    html = html.replace('btn-python', f'btn-{tech_class}')
    html = html.replace('btn-outline-python', f'btn-outline-{tech_class}')
    html = html.replace('python-flow', f'{tech_class}-flow')
    html = html.replace('--python-', f'--{tech_class}-')
    html = html.replace('var(--python-', f'var(--{tech_class}-')
    
    # Write file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  ✅ Created {html_file.name}")
    return True

def main():
    print("🚀 Generating interactive HTML files...\n")
    
    created_count = 0
    skipped_count = 0
    
    for tech_key, config in TECHNOLOGIES.items():
        tech_dir = BASE_DIR / tech_key.split('/')[0]
        subdir = '/'.join(tech_key.split('/')[1:]) if '/' in tech_key else ''
        
        print(f"Processing {tech_key}...")
        
        if generate_interactive_html(tech_dir, tech_key, config, subdir):
            created_count += 1
        else:
            skipped_count += 1
    
    print(f"\n✨ Done! Created {created_count} files, skipped {skipped_count} existing files")

if __name__ == '__main__':
    main()

