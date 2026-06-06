#!/usr/bin/env python3
"""
Comprehensive script to generate all missing documentation files
Based on DOCUMENTATION_PLAN.md and DOCUMENTATION_STATUS.md
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent

# Comprehensive technology metadata
TECH_METADATA = {
    # Phase 1: Tools & Libraries
    'Tools/Jupyter': {
        'name': 'Jupyter',
        'full_name': 'Jupyter Notebook',
        'description': 'Jupyter Notebook is an open-source web application that allows you to create and share documents containing live code, equations, visualizations, and narrative text. It supports over 40 programming languages and is widely used for data science, machine learning, and scientific computing.',
        'category': 'Development Tools',
        'icon': '📓',
        'features': [
            '**Interactive Computing**: Execute code cells and see results immediately',
            '**Rich Output**: Display HTML, images, videos, LaTeX, and more',
            '**Kernel Support**: Support for Python, R, Julia, Scala, and many more',
            '**Widgets**: Interactive widgets for data exploration',
            '**Extensions**: Extensible with JupyterLab extensions',
            '**Sharing**: Export to HTML, PDF, slides, and more'
        ],
        'installation': '''# Install Jupyter Notebook
pip install notebook

# Install JupyterLab (next-gen interface)
pip install jupyterlab

# Install with conda
conda install -c conda-forge notebook

# Start Jupyter Notebook
jupyter notebook

# Start JupyterLab
jupyter lab''',
        'code_examples': '''```python
# Create a new notebook cell
# Cell 1: Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cell 2: Load data
df = pd.read_csv('data.csv')
print(df.head())

# Cell 3: Visualize
df.plot(kind='bar', x='category', y='value')
plt.show()

# Cell 4: Markdown cell
# ## Analysis Results
# The data shows significant trends...
```''',
        'advanced_examples': '''```python
# Magic commands
%timeit sum(range(1000))  # Time execution
%matplotlib inline         # Inline plots
%load_ext autoreload       # Auto-reload modules
%autoreload 2

# Widgets for interactivity
from ipywidgets import interact
@interact(x=(0, 10))
def square(x):
    return x**2

# Export to different formats
# jupyter nbconvert --to html notebook.ipynb
# jupyter nbconvert --to pdf notebook.ipynb
```''',
        'best_practices': [
            '1. Keep cells focused and small - one concept per cell',
            '2. Use markdown cells for documentation and explanations',
            '3. Clear output before committing to version control',
            '4. Use virtual environments to manage dependencies',
            '5. Restart kernel and run all cells before sharing',
            '6. Use descriptive cell titles and section headers',
            '7. Avoid hardcoding paths - use relative paths or environment variables'
        ]
    },
    'Tools/Plotly': {
        'name': 'Plotly',
        'full_name': 'Plotly',
        'description': 'Plotly is an interactive, open-source plotting library that supports over 40 chart types. It provides both Python and JavaScript APIs for creating publication-quality graphs, dashboards, and data visualization applications.',
        'category': 'Data Visualization',
        'icon': '📊',
        'features': [
            '**Interactive Charts**: Zoom, pan, hover, and click interactions',
            '**Multiple Chart Types**: Line, bar, scatter, 3D, maps, and more',
            '**Dash Integration**: Build interactive web applications',
            '**Export Options**: Export to PNG, SVG, HTML, and more',
            '**Real-time Updates**: Support for streaming and real-time data',
            '**Collaboration**: Share and collaborate on charts online'
        ],
        'installation': '''# Install Plotly
pip install plotly

# Install with Dash for web apps
pip install plotly dash

# Install Kaleido for static image export
pip install kaleido

# For Jupyter support
pip install plotly jupyterlab''',
        'code_examples': '''```python
import plotly.graph_objects as go
import plotly.express as px

# Simple line chart
fig = px.line(x=[1, 2, 3, 4], y=[10, 11, 12, 13], 
              title='Simple Line Chart')
fig.show()

# Bar chart
df = px.data.tips()
fig = px.bar(df, x='day', y='total_bill', color='sex')
fig.show()

# 3D scatter plot
fig = px.scatter_3d(df, x='total_bill', y='tip', z='size', 
                    color='day')
fig.show()
```''',
        'advanced_examples': '''```python
# Custom interactive dashboard
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Sales', 'Revenue', 'Profit', 'Growth'),
    specs=[[{'type': 'bar'}, {'type': 'scatter'}],
           [{'type': 'box'}, {'type': 'histogram'}]]
)

# Add traces
fig.add_trace(go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3]), row=1, col=1)
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]), row=1, col=2)

fig.update_layout(height=600, title_text="Dashboard")
fig.show()
```''',
        'best_practices': [
            '1. Use plotly.express for quick, simple charts',
            '2. Use plotly.graph_objects for advanced customization',
            '3. Add meaningful titles and axis labels',
            '4. Use color scales that are colorblind-friendly',
            '5. Optimize performance for large datasets with downsampling',
            '6. Export static images for presentations and papers',
            '7. Use Dash for interactive web applications'
        ]
    },
    'Tools/Seaborn': {
        'name': 'Seaborn',
        'full_name': 'Seaborn',
        'description': 'Seaborn is a Python data visualization library based on matplotlib. It provides a high-level interface for drawing attractive and informative statistical graphics, making it easier to create complex visualizations with less code.',
        'category': 'Data Visualization',
        'icon': '🎨',
        'features': [
            '**Statistical Plots**: Built-in support for statistical visualizations',
            '**Beautiful Defaults**: Attractive default styles and color palettes',
            '**Pandas Integration**: Works seamlessly with Pandas DataFrames',
            '**Categorical Plots**: Specialized plots for categorical data',
            '**Distribution Plots**: Easy visualization of distributions',
            '**Regression Plots**: Built-in regression and correlation plots'
        ],
        'installation': '''# Install Seaborn
pip install seaborn

# Install with dependencies
pip install seaborn matplotlib pandas numpy

# Verify installation
python -c "import seaborn; print(seaborn.__version__)"''',
        'code_examples': '''```python
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Load sample data
tips = sns.load_dataset('tips')

# Basic plot
sns.scatterplot(data=tips, x='total_bill', y='tip', hue='smoker')
plt.show()

# Distribution plot
sns.histplot(data=tips, x='total_bill', kde=True)
plt.show()

# Categorical plot
sns.boxplot(data=tips, x='day', y='total_bill', hue='sex')
plt.show()
```''',
        'advanced_examples': '''```python
# Complex multi-panel figure
g = sns.FacetGrid(tips, col='time', row='smoker')
g.map(sns.scatterplot, 'total_bill', 'tip')

# Pair plot for correlations
sns.pairplot(tips, hue='sex', diag_kind='kde')

# Heatmap
correlation = tips.corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm')

# Custom styling
sns.set_style('darkgrid')
sns.set_palette('husl')
```''',
        'best_practices': [
            '1. Use Seaborn for statistical visualizations',
            '2. Leverage built-in datasets for learning and examples',
            '3. Combine with matplotlib for fine-grained control',
            '4. Use appropriate plot types for your data (categorical vs continuous)',
            '5. Choose color palettes that match your data (sequential, diverging, categorical)',
            '6. Use FacetGrid for multi-panel visualizations',
            '7. Set context and style for different output formats (paper, talk, poster)'
        ]
    },
    'Tools/Git': {
        'name': 'Git',
        'full_name': 'Git Version Control',
        'description': 'Git is a distributed version control system for tracking changes in source code during software development. It is designed for coordinating work among programmers, but it can be used to track changes in any set of files.',
        'category': 'Version Control',
        'icon': '🔀',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is Git and how does it differ from other version control systems?',
                'a': 'Git is a distributed version control system (DVCS) that allows multiple developers to work on the same project simultaneously. Unlike centralized systems like SVN, Git gives every developer a complete copy of the repository, enabling offline work and faster operations. Key differences: distributed architecture, branching and merging capabilities, cryptographic integrity, and performance.'
            },
            {
                'level': 'Beginner',
                'q': 'Explain the difference between Git and GitHub.',
                'a': 'Git is the version control software that runs locally on your machine, while GitHub is a cloud-based hosting service for Git repositories. Git handles version control operations (commit, branch, merge), while GitHub provides remote storage, collaboration features (pull requests, issues), and web-based interface for Git repositories.'
            },
            {
                'level': 'Intermediate',
                'q': 'What is the difference between git merge and git rebase?',
                'a': 'Git merge creates a merge commit that combines two branches, preserving the complete history. Git rebase replays commits from one branch onto another, creating a linear history. Merge preserves context but creates a more complex history. Rebase creates cleaner history but rewrites commit history. Use merge for public branches, rebase for local feature branches.'
            },
            {
                'level': 'Intermediate',
                'q': 'How do you resolve merge conflicts?',
                'a': '1. Identify conflicted files with `git status`. 2. Open files and look for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`). 3. Manually edit to resolve conflicts, keeping desired changes. 4. Stage resolved files with `git add`. 5. Complete merge with `git commit`. Use `git merge --abort` to cancel merge, or tools like `git mergetool` for visual resolution.'
            },
            {
                'level': 'Advanced',
                'q': 'Explain Git internals: objects, refs, and the index.',
                'a': 'Git stores data as objects: blobs (file content), trees (directory structure), commits (snapshots), and tags. Refs are pointers to commits (branches, HEAD). The index (staging area) is a binary file that stores information about what will go into the next commit. Objects are stored in `.git/objects/`, refs in `.git/refs/`, and the index is `.git/index`.'
            }
        ]
    },
    'Tools/VS-Code': {
        'name': 'VS Code',
        'full_name': 'Visual Studio Code',
        'description': 'Visual Studio Code is a free, open-source code editor developed by Microsoft. It provides a rich development experience with built-in support for debugging, task running, version control, and extensions for additional languages and tools.',
        'category': 'IDE',
        'icon': '💻',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is VS Code and what are its key features?',
                'a': 'VS Code is a lightweight, cross-platform code editor with powerful features: IntelliSense (smart code completion), integrated terminal, Git support, debugging, extensions marketplace, integrated terminal, multi-cursor editing, and customizable themes. It strikes a balance between a simple text editor and a full IDE.'
            },
            {
                'level': 'Beginner',
                'q': 'How do you customize VS Code for Python development?',
                'a': 'Install Python extension, configure Python interpreter path, set up linting (pylint/flake8), configure formatting (black/autopep8), enable auto-save, set up virtual environment, configure debugger, and install useful extensions like Python Docstring Generator, Jupyter, and Pylance for enhanced IntelliSense.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain VS Code tasks and how to configure them.',
                'a': 'Tasks automate common development workflows. Configure in `.vscode/tasks.json`. Tasks can run scripts, build commands, or any shell command. Use `Ctrl+Shift+P` > "Tasks: Run Task" to execute. Tasks can have dependencies, be run on folder open, and integrate with problem matchers for error detection.'
            },
            {
                'level': 'Intermediate',
                'q': 'How do you debug Python code in VS Code?',
                'a': '1. Set breakpoints by clicking left margin. 2. Press F5 or go to Run > Start Debugging. 3. Select Python debugger. 4. Use debug toolbar (continue, step over, step into, step out). 5. Inspect variables in Variables panel. 6. Use Debug Console for expressions. Configure launch.json for custom debug configurations.'
            },
            {
                'level': 'Advanced',
                'q': 'How do you create a VS Code extension?',
                'a': '1. Install Yeoman and VS Code Extension Generator. 2. Run `yo code` to scaffold extension. 3. Extension structure includes package.json (manifest), extension.ts (main code), and README. 4. Implement activation events and commands. 5. Use VS Code API for editor interactions. 6. Test with F5 (Extension Development Host). 7. Package with `vsce package` and publish to marketplace.'
            }
        ]
    },
    # Phase 2: Data Engineering Core
    'DataEngineering/Java': {
        'name': 'Java',
        'full_name': 'Java for Data Engineering',
        'description': 'Java is a high-level, object-oriented programming language widely used in enterprise data engineering. It provides strong typing, excellent performance, and extensive libraries for building scalable data processing systems, particularly with frameworks like Apache Spark, Kafka, and Hadoop.',
        'category': 'Programming Language',
        'icon': '☕',
        'features': [
            '**Platform Independence**: Write once, run anywhere (JVM)',
            '**Strong Typing**: Compile-time type checking for reliability',
            '**Rich Ecosystem**: Extensive libraries and frameworks',
            '**Performance**: JVM optimization and garbage collection',
            '**Concurrency**: Built-in support for multi-threading',
            '**Enterprise Ready**: Widely used in large-scale systems'
        ],
        'installation': '''# Install Java JDK
# macOS
brew install openjdk@11

# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# Verify installation
java -version
javac -version

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64''',
        'code_examples': '''```java
// Basic Java class
public class DataProcessor {
    private String name;
    
    public DataProcessor(String name) {
        this.name = name;
    }
    
    public void processData(List<String> data) {
        data.stream()
            .filter(s -> s.length() > 5)
            .map(String::toUpperCase)
            .forEach(System.out::println);
    }
}
```''',
        'advanced_examples': '''```java
// Spark with Java
import org.apache.spark.sql.SparkSession;

SparkSession spark = SparkSession.builder()
    .appName("DataProcessing")
    .master("local[*]")
    .getOrCreate();

Dataset<Row> df = spark.read()
    .option("header", "true")
    .csv("data.csv");

df.filter(col("age").gt(18))
  .groupBy("city")
  .agg(avg("salary"))
  .show();
```''',
        'best_practices': [
            '1. Use Maven or Gradle for dependency management',
            '2. Follow Java naming conventions and coding standards',
            '3. Leverage Streams API for functional programming',
            '4. Use appropriate data structures (ArrayList, HashMap, etc.)',
            '5. Handle exceptions properly with try-catch-finally',
            '6. Use interfaces for abstraction and testability',
            '7. Optimize for JVM performance (avoid premature optimization)'
        ]
    },
    'DataEngineering/Kafka': {
        'name': 'Kafka',
        'full_name': 'Apache Kafka',
        'description': 'Apache Kafka is a distributed event streaming platform capable of handling trillions of events per day. It is used for building real-time data pipelines and streaming applications, providing high throughput, fault tolerance, and horizontal scalability.',
        'category': 'Streaming Platform',
        'icon': '⚡',
        'features': [
            '**High Throughput**: Handle millions of messages per second',
            '**Scalability**: Horizontal scaling with partitioning',
            '**Durability**: Persistent storage with configurable retention',
            '**Fault Tolerance**: Replication and leader election',
            '**Real-time Processing**: Low latency message delivery',
            '**Stream Processing**: Kafka Streams for real-time transformations'
        ],
        'installation': '''# Download Kafka
wget https://downloads.apache.org/kafka/2.13-3.5.0/kafka_2.13-3.5.0.tgz
tar -xzf kafka_2.13-3.5.0.tgz
cd kafka_2.13-3.5.0

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties

# Create topic
bin/kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092

# Python client
pip install kafka-python''',
        'code_examples': '''```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('test-topic', {'key': 'value'})
producer.flush()

# Consumer
consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(message.value)
```''',
        'advanced_examples': '''```python
# Kafka Streams processing
from kafka import KafkaConsumer
from collections import defaultdict

consumer = KafkaConsumer(
    'events',
    bootstrap_servers=['localhost:9092'],
    group_id='processor-group',
    enable_auto_commit=True,
    auto_offset_reset='earliest'
)

# Process stream
counts = defaultdict(int)
for message in consumer:
    event = json.loads(message.value)
    counts[event['type']] += 1
    if counts[event['type']] % 100 == 0:
        print(f"Processed {counts[event['type']]} events of type {event['type']}")
```''',
        'best_practices': [
            '1. Choose appropriate partition keys for even distribution',
            '2. Configure replication factor (minimum 3 for production)',
            '3. Set appropriate retention policies based on use case',
            '4. Use consumer groups for parallel processing',
            '5. Monitor lag and throughput metrics',
            '6. Handle serialization/deserialization errors gracefully',
            '7. Use idempotent producers for exactly-once semantics'
        ]
    },
    'DataEngineering/Python': {
        'name': 'Python',
        'full_name': 'Python for Data Engineering',
        'description': 'Python is a high-level, interpreted programming language widely used in data engineering for ETL pipelines, data processing, API development, and automation. Its simplicity, extensive libraries, and strong community make it ideal for data engineering tasks.',
        'category': 'Programming Language',
        'icon': '🐍',
        'features': [
            '**Simple Syntax**: Easy to read and write',
            '**Rich Libraries**: Pandas, NumPy, Apache Airflow, etc.',
            '**Rapid Development**: Fast prototyping and iteration',
            '**Integration**: Easy integration with databases and APIs',
            '**Community**: Large community and extensive documentation',
            '**Versatility**: Scripting, web development, data science'
        ],
        'installation': '''# Install Python
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install packages
pip install pandas numpy apache-airflow''',
        'code_examples': '''```python
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
```''',
        'advanced_examples': '''```python
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
```''',
        'best_practices': [
            '1. Use virtual environments for project isolation',
            '2. Follow PEP 8 style guide',
            '3. Use type hints for better code documentation',
            '4. Handle exceptions properly',
            '5. Use list comprehensions and generators for efficiency',
            '6. Leverage libraries instead of reinventing the wheel',
            '7. Write unit tests for critical functions'
        ]
    },
    'DataEngineering/Scala': {
        'name': 'Scala',
        'full_name': 'Scala for Data Engineering',
        'description': 'Scala is a modern multi-paradigm programming language that combines object-oriented and functional programming. It runs on the JVM and is the primary language for Apache Spark, making it essential for big data processing and distributed computing.',
        'category': 'Programming Language',
        'icon': '🔷',
        'features': [
            '**JVM Compatibility**: Runs on Java Virtual Machine',
            '**Functional Programming**: Immutability and higher-order functions',
            '**Type Safety**: Strong static typing with type inference',
            '**Spark Integration**: Native support for Apache Spark',
            '**Concurrency**: Actor model with Akka',
            '**Expressiveness**: Concise syntax for complex operations'
        ],
        'installation': '''# Install Scala
# macOS
brew install scala

# Ubuntu/Debian
sudo apt install scala

# Install sbt (Scala Build Tool)
# macOS
brew install sbt

# Ubuntu/Debian
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt update
sudo apt install sbt

# Verify
scala -version
sbt sbtVersion''',
        'code_examples': '''```scala
// Basic Scala class
case class Person(name: String, age: Int)

// Functional programming
val numbers = List(1, 2, 3, 4, 5)
val doubled = numbers.map(_ * 2)
val evens = numbers.filter(_ % 2 == 0)
val sum = numbers.reduce(_ + _)

// Pattern matching
def process(person: Person): String = person match {
  case Person(name, age) if age < 18 => s"$name is a minor"
  case Person(name, age) => s"$name is an adult"
}
```''',
        'advanced_examples': '''```scala
// Spark with Scala
import org.apache.spark.sql.SparkSession

val spark = SparkSession.builder()
  .appName("DataProcessing")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

val df = spark.read
  .option("header", "true")
  .csv("data.csv")

df.filter($"age" > 18)
  .groupBy("city")
  .agg(avg("salary"))
  .show()
```''',
        'best_practices': [
            '1. Prefer immutability (val over var, case classes)',
            '2. Use pattern matching for control flow',
            '3. Leverage higher-order functions (map, filter, reduce)',
            '4. Use Option for nullable values',
            '5. Follow functional programming principles',
            '6. Use sbt for dependency management',
            '7. Write idiomatic Scala code, not Java in Scala syntax'
        ]
    },
    # Phase 3: Gen-AI
    'Gen-AI/Embeddings': {
        'name': 'Embeddings',
        'full_name': 'Vector Embeddings',
        'description': 'Embeddings are dense vector representations of text, images, or other data that capture semantic meaning. They enable machine learning models to understand relationships and similarities between data points, powering applications like semantic search, recommendation systems, and RAG (Retrieval-Augmented Generation).',
        'category': 'Machine Learning',
        'icon': '🧮',
        'features': [
            '**Semantic Understanding**: Capture meaning and context',
            '**Similarity Search**: Find similar items using vector distance',
            '**Dimensionality**: High-dimensional dense representations',
            '**Transfer Learning**: Pre-trained models for various domains',
            '**Multi-modal**: Support for text, images, audio, and more',
            '**RAG Integration**: Essential for retrieval-augmented generation'
        ],
        'installation': '''# Install embedding libraries
pip install sentence-transformers
pip install openai
pip install transformers

# For vector databases
pip install chromadb
pip install pinecone-client
pip install faiss-cpu''',
        'code_examples': '''```python
from sentence_transformers import SentenceTransformer

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
texts = ["Hello world", "Machine learning", "Data science"]
embeddings = model.encode(texts)

print(embeddings.shape)  # (3, 384)

# Find similar texts
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity([embeddings[0]], embeddings[1:])
print(similarity)
```''',
        'advanced_examples': '''```python
# OpenAI embeddings
import openai

embeddings = openai.Embedding.create(
    input=["text to embed"],
    model="text-embedding-ada-002"
)

# Custom fine-tuning
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

model = SentenceTransformer('all-MiniLM-L6-v2')
train_examples = [
    InputExample(texts=['Query', 'Positive passage']),
    InputExample(texts=['Query', 'Negative passage'])
]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)
model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=1)
```''',
        'best_practices': [
            '1. Choose appropriate embedding model for your domain',
            '2. Normalize embeddings for cosine similarity',
            '3. Use batch processing for efficiency',
            '4. Cache embeddings to avoid recomputation',
            '5. Consider dimensionality vs. quality trade-offs',
            '6. Fine-tune models on domain-specific data when needed',
            '7. Use appropriate distance metrics (cosine, euclidean, dot product)'
        ]
    },
    'Gen-AI/LangChain': {
        'name': 'LangChain',
        'full_name': 'LangChain',
        'description': 'LangChain is a framework for developing applications powered by language models. It provides tools for chaining together different components like LLMs, vector stores, and tools to build sophisticated AI applications including chatbots, agents, and RAG systems.',
        'category': 'AI Framework',
        'icon': '🔗',
        'features': [
            '**LLM Integration**: Support for OpenAI, Anthropic, and open-source models',
            '**Chains**: Compose multiple components together',
            '**Agents**: Build autonomous agents with tools',
            '**Memory**: Maintain conversation context',
            '**Vector Stores**: Integration with embedding databases',
            '**Tools**: Connect LLMs to external APIs and functions'
        ],
        'installation': '''# Install LangChain
pip install langchain

# With OpenAI
pip install langchain openai

# With vector stores
pip install langchain chromadb

# With document loaders
pip install langchain pypdf

# All components
pip install langchain[all]''',
        'code_examples': '''```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = OpenAI(temperature=0.9)
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a short poem about {topic}?"
)
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("data science"))
```''',
        'advanced_examples': '''```python
# RAG with LangChain
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

loader = TextLoader("document.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings)

qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

result = qa_chain.run("What is the main topic?")
```''',
        'best_practices': [
            '1. Use appropriate chunk sizes for document splitting',
            '2. Implement proper error handling for LLM calls',
            '3. Use streaming for better user experience',
            '4. Cache LLM responses when possible',
            '5. Implement retry logic for API calls',
            '6. Use prompt templates for consistency',
            '7. Monitor token usage and costs'
        ]
    },
    'Gen-AI/OpenAI-GPT': {
        'name': 'OpenAI GPT',
        'full_name': 'OpenAI GPT Models',
        'description': 'OpenAI GPT (Generative Pre-trained Transformer) models are large language models that can generate human-like text, answer questions, write code, and perform various language tasks. GPT-4 and GPT-3.5 are widely used for building AI applications, chatbots, and content generation systems.',
        'category': 'AI Model',
        'icon': '🤖',
        'features': [
            '**Text Generation**: Generate coherent, context-aware text',
            '**Conversation**: Multi-turn dialogue capabilities',
            '**Code Generation**: Write and debug code',
            '**Translation**: Translate between languages',
            '**Summarization**: Summarize long texts',
            '**Question Answering**: Answer questions based on context'
        ],
        'installation': '''# Install OpenAI Python library
pip install openai

# Set API key
export OPENAI_API_KEY='your-api-key-here'

# Or in code
import openai
openai.api_key = 'your-api-key-here''',
        'code_examples': '''```python
import openai

# Text completion
response = openai.Completion.create(
    model="text-davinci-003",
    prompt="Explain machine learning in simple terms:",
    max_tokens=150,
    temperature=0.7
)
print(response.choices[0].text)

# Chat completion (GPT-3.5/4)
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ]
)
print(response.choices[0].message.content)
```''',
        'advanced_examples': '''```python
# Streaming responses
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta.content, end="")

# Function calling
functions = [{
    "name": "get_weather",
    "description": "Get current weather",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        }
    }
}]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    functions=functions
)
```''',
        'best_practices': [
            '1. Use appropriate temperature settings (0.7 for creative, 0 for deterministic)',
            '2. Set max_tokens to control response length',
            '3. Implement retry logic for rate limits',
            '4. Use system messages to set behavior',
            '5. Monitor token usage and costs',
            '6. Handle errors gracefully',
            '7. Use streaming for better UX in production'
        ]
    },
    'Gen-AI/Vector-Databases': {
        'name': 'Vector Databases',
        'full_name': 'Vector Databases',
        'description': 'Vector databases are specialized databases designed to store, index, and query high-dimensional vector embeddings. They enable efficient similarity search and are essential for RAG systems, recommendation engines, and semantic search applications.',
        'category': 'Database',
        'icon': '🗄️',
        'features': [
            '**Similarity Search**: Fast nearest neighbor search',
            '**Scalability**: Handle millions of vectors',
            '**Indexing**: Efficient indexing algorithms (HNSW, IVF)',
            '**Metadata Filtering**: Combine vector search with metadata',
            '**Real-time Updates**: Add/update vectors in real-time',
            '**Multi-modal**: Support for various embedding types'
        ],
        'installation': '''# ChromaDB
pip install chromadb

# Pinecone
pip install pinecone-client

# Weaviate
pip install weaviate-client

# Qdrant
pip install qdrant-client

# FAISS (Facebook AI Similarity Search)
pip install faiss-cpu  # or faiss-gpu
''',
        'code_examples': '''```python
# ChromaDB example
import chromadb

client = chromadb.Client()
collection = client.create_collection("documents")

# Add documents
collection.add(
    documents=["Document 1 text", "Document 2 text"],
    ids=["id1", "id2"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]]
)

# Query
results = collection.query(
    query_embeddings=[[0.15, 0.25, ...]],
    n_results=2
)
```''',
        'advanced_examples': '''```python
# Pinecone with metadata filtering
import pinecone

pinecone.init(api_key="your-key", environment="us-west1-gcp")
index = pinecone.Index("my-index")

# Upsert with metadata
index.upsert([
    ("vec1", [0.1, 0.2, ...], {"category": "tech", "year": 2023}),
    ("vec2", [0.3, 0.4, ...], {"category": "science", "year": 2023})
])

# Query with metadata filter
results = index.query(
    vector=[0.15, 0.25, ...],
    top_k=5,
    filter={"category": "tech", "year": 2023}
)
```''',
        'best_practices': [
            '1. Choose appropriate index type for your use case',
            '2. Normalize vectors before storing',
            '3. Use metadata filtering to narrow search space',
            '4. Monitor index size and performance',
            '5. Implement proper error handling',
            '6. Use batch operations for efficiency',
            '7. Consider hybrid search (vector + keyword) for better results'
        ]
    },
    # Phase 4: Frontend
    'Frontend/D3.js': {
        'name': 'D3.js',
        'full_name': 'D3.js',
        'description': 'D3.js (Data-Driven Documents) is a JavaScript library for producing dynamic, interactive data visualizations in web browsers. It uses HTML, SVG, and CSS to bring data to life through powerful visualization components.',
        'category': 'Data Visualization',
        'icon': '📊',
        'features': [
            '**Data Binding**: Bind data to DOM elements',
            '**Transitions**: Smooth animations and transitions',
            '**Scales**: Map data to visual properties',
            '**Selections**: Powerful DOM manipulation',
            '**Layouts**: Built-in layouts for complex visualizations',
            '**Customizable**: Full control over visual elements'
        ],
        'installation': '''# Install via npm
npm install d3

# Or use CDN
<script src="https://d3js.org/d3.v7.min.js"></script>

# Import in ES6
import * as d3 from 'd3';''',
        'code_examples': '''```javascript
// Basic bar chart
const data = [4, 8, 15, 16, 23, 42];
const svg = d3.select('body').append('svg')
    .attr('width', 400)
    .attr('height', 300);

svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('x', (d, i) => i * 40)
    .attr('y', d => 300 - d * 5)
    .attr('width', 35)
    .attr('height', d => d * 5);
```''',
        'advanced_examples': '''```javascript
// Interactive scatter plot with scales
const xScale = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.x)])
    .range([0, width]);

const yScale = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.y)])
    .range([height, 0]);

svg.selectAll('circle')
    .data(data)
    .enter()
    .append('circle')
    .attr('cx', d => xScale(d.x))
    .attr('cy', d => yScale(d.y))
    .attr('r', 5)
    .on('mouseover', handleMouseOver)
    .on('mouseout', handleMouseOut);
```''',
        'best_practices': [
            '1. Use scales to map data to visual properties',
            '2. Leverage enter/update/exit pattern for data binding',
            '3. Use transitions for smooth animations',
            '4. Optimize performance for large datasets',
            '5. Make visualizations responsive and accessible',
            '6. Use D3 layouts for complex visualizations',
            '7. Clean up event listeners and timers'
        ]
    },
    'Frontend/Material-UI': {
        'name': 'Material-UI',
        'full_name': 'Material-UI (MUI)',
        'description': 'Material-UI is a popular React component library that implements Google\'s Material Design principles. It provides a comprehensive set of pre-built, customizable components for building modern web applications.',
        'category': 'UI Framework',
        'icon': '🎨',
        'features': [
            '**Component Library**: 50+ pre-built components',
            '**Material Design**: Follows Google Material Design',
            '**Customizable**: Theming and styling system',
            '**Accessible**: WCAG compliant components',
            '**TypeScript**: Full TypeScript support',
            '**Responsive**: Mobile-first responsive design'
        ],
        'installation': '''# Install Material-UI
npm install @mui/material @emotion/react @emotion/styled

# Install icons
npm install @mui/icons-material

# Install fonts
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" />''',
        'code_examples': '''```jsx
import { Button, TextField, Card } from '@mui/material';

function App() {
  return (
    <Card>
      <TextField label="Name" variant="outlined" />
      <Button variant="contained" color="primary">
        Submit
      </Button>
    </Card>
  );
}
```''',
        'advanced_examples': '''```jsx
// Custom theme
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' }
  }
});

<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>
```''',
        'best_practices': [
            '1. Use the theme system for consistent styling',
            '2. Leverage component composition',
            '3. Use responsive breakpoints',
            '4. Follow Material Design guidelines',
            '5. Optimize bundle size with tree shaking',
            '6. Use TypeScript for type safety',
            '7. Test components with React Testing Library'
        ]
    },
    'Frontend/Streamlit': {
        'name': 'Streamlit',
        'full_name': 'Streamlit',
        'description': 'Streamlit is an open-source Python framework for building interactive web applications for data science and machine learning. It allows you to create beautiful, custom web apps with just Python, no frontend knowledge required.',
        'category': 'Web Framework',
        'icon': '🚀',
        'features': [
            '**Python Only**: Build apps with pure Python',
            '**Interactive Widgets**: Sliders, buttons, inputs, and more',
            '**Data Visualization**: Built-in support for charts and graphs',
            '**Fast Development**: Rapid prototyping and deployment',
            '**Deployment**: Easy deployment to Streamlit Cloud',
            '**Customizable**: Custom themes and components'
        ],
        'installation': '''# Install Streamlit
pip install streamlit

# Run app
streamlit run app.py

# Create requirements.txt
streamlit
pandas
numpy
matplotlib''',
        'code_examples': '''```python
import streamlit as st
import pandas as pd

st.title('My Data App')
st.write('Welcome to Streamlit!')

# Interactive widget
name = st.text_input('Enter your name')
if name:
    st.write(f'Hello, {name}!')

# Data visualization
df = pd.read_csv('data.csv')
st.dataframe(df)
st.line_chart(df)
```''',
        'advanced_examples': '''```python
# Multi-page app
import streamlit as st

st.sidebar.title('Navigation')
page = st.sidebar.selectbox('Choose a page', ['Home', 'Data', 'Visualization'])

if page == 'Home':
    st.title('Home Page')
elif page == 'Data':
    st.title('Data Explorer')
    # Data exploration code
elif page == 'Visualization':
    st.title('Visualizations')
    # Visualization code
```''',
        'best_practices': [
            '1. Use caching (@st.cache) for expensive computations',
            '2. Organize code with functions and classes',
            '3. Use session state for maintaining state',
            '4. Optimize data loading and processing',
            '5. Use columns and containers for layout',
            '6. Add error handling and user feedback',
            '7. Deploy to Streamlit Cloud for sharing'
        ]
    },
    'Frontend/TypeScript': {
        'name': 'TypeScript',
        'full_name': 'TypeScript',
        'description': 'TypeScript is a typed superset of JavaScript that compiles to plain JavaScript. It adds static type definitions to JavaScript, enabling better tooling, error detection, and code documentation.',
        'category': 'Programming Language',
        'icon': '📘',
        'features': [
            '**Static Typing**: Type checking at compile time',
            '**JavaScript Compatible**: All JavaScript is valid TypeScript',
            '**Tooling**: Better IDE support and autocomplete',
            '**Modern Features**: Support for latest ECMAScript features',
            '**Gradual Adoption**: Can be adopted incrementally',
            '**Large Ecosystem**: Works with all JavaScript libraries'
        ],
        'installation': '''# Install TypeScript
npm install -g typescript

# Initialize project
tsc --init

# Compile TypeScript
tsc app.ts

# With ts-node for development
npm install -g ts-node
ts-node app.ts''',
        'code_examples': '''```typescript
// Basic types
let name: string = "John";
let age: number = 30;
let isActive: boolean = true;

// Function with types
function greet(name: string): string {
    return `Hello, ${name}!`;
}

// Interface
interface User {
    id: number;
    name: string;
    email?: string;  // Optional
}

const user: User = {
    id: 1,
    name: "John"
};
```''',
        'advanced_examples': '''```typescript
// Generics
function identity<T>(arg: T): T {
    return arg;
}

// Union types
type Status = 'pending' | 'approved' | 'rejected';

// Type guards
function isString(value: unknown): value is string {
    return typeof value === 'string';
}

// Utility types
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
```''',
        'best_practices': [
            '1. Enable strict mode in tsconfig.json',
            '2. Use interfaces for object shapes',
            '3. Avoid using "any" type',
            '4. Use type guards for runtime type checking',
            '5. Leverage utility types (Partial, Pick, Omit)',
            '6. Use generics for reusable code',
            '7. Enable noImplicitAny and strictNullChecks'
        ]
    },
    'Frontend/React': {
        'name': 'React',
        'full_name': 'React',
        'description': 'React is a JavaScript library for building user interfaces, particularly web applications. It uses a component-based architecture and a virtual DOM for efficient rendering.',
        'category': 'UI Library',
        'icon': '⚛️',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is React and what are its key features?',
                'a': 'React is a JavaScript library for building user interfaces. Key features include: component-based architecture, virtual DOM for performance, one-way data binding, JSX syntax, and a rich ecosystem. React allows developers to build reusable UI components and manage application state efficiently.'
            },
            {
                'level': 'Beginner',
                'q': 'What is JSX and why is it used?',
                'a': 'JSX (JavaScript XML) is a syntax extension that allows writing HTML-like code in JavaScript. It makes React code more readable and expressive. JSX is transpiled to React.createElement() calls. It allows embedding expressions, using JavaScript logic, and creating component trees in a declarative way.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain the difference between state and props in React.',
                'a': 'Props (properties) are read-only data passed from parent to child components. They are immutable and used for configuration. State is mutable data managed within a component using useState hook. State changes trigger re-renders. Props flow down, state is managed locally. Use props for configuration, state for dynamic data.'
            },
            {
                'level': 'Intermediate',
                'q': 'What are React Hooks and why were they introduced?',
                'a': 'Hooks are functions that let you use state and other React features in functional components. They were introduced to allow functional components to have state and lifecycle methods. Common hooks: useState (state), useEffect (side effects), useContext (context), useMemo (memoization), useCallback (callback memoization).'
            },
            {
                'level': 'Advanced',
                'q': 'Explain React\'s reconciliation algorithm and virtual DOM.',
                'a': 'React uses a virtual DOM (in-memory representation) to optimize rendering. When state changes, React creates a new virtual DOM tree and compares it with the previous one (diffing). It then updates only the changed nodes in the real DOM (reconciliation). This minimizes expensive DOM operations and improves performance.'
            }
        ]
    },
    # Phase 5: Backend & Databases (Interview.md only)
    'Backend/FastAPI': {
        'name': 'FastAPI',
        'full_name': 'FastAPI',
        'description': 'FastAPI is a modern, fast web framework for building APIs with Python based on standard Python type hints. It provides automatic API documentation, high performance, and easy-to-use features.',
        'category': 'Web Framework',
        'icon': '⚡',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is FastAPI and what are its main advantages?',
                'a': 'FastAPI is a modern Python web framework for building APIs. Advantages: automatic API documentation (OpenAPI/Swagger), high performance (comparable to Node.js), type hints for validation, async/await support, dependency injection, and easy to learn. It\'s built on Starlette and Pydantic.'
            },
            {
                'level': 'Intermediate',
                'q': 'How does FastAPI handle request validation?',
                'a': 'FastAPI uses Pydantic models for automatic request validation. Define models with type hints, and FastAPI validates incoming data, converts types, and returns 422 errors for invalid data. It also generates JSON Schema automatically for API documentation.'
            },
            {
                'level': 'Advanced',
                'q': 'Explain FastAPI\'s dependency injection system.',
                'a': 'FastAPI\'s dependency injection allows reusable components (dependencies) that can be shared across routes. Dependencies can depend on other dependencies, creating a dependency graph. Use Depends() to inject dependencies. Useful for database sessions, authentication, authorization, and shared logic.'
            }
        ]
    },
    'Backend/Node.js': {
        'name': 'Node.js',
        'full_name': 'Node.js',
        'description': 'Node.js is a JavaScript runtime built on Chrome\'s V8 engine that enables server-side JavaScript execution. It uses an event-driven, non-blocking I/O model, making it efficient for building scalable network applications.',
        'category': 'Runtime',
        'icon': '🟢',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is Node.js and how does it differ from browser JavaScript?',
                'a': 'Node.js is a JavaScript runtime for server-side development. Differences: Node.js has access to file system, network, and OS APIs; uses CommonJS modules (require/module.exports); runs in a single process; designed for I/O-intensive applications. Browser JavaScript is sandboxed and uses ES modules.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain Node.js event loop and how it handles asynchronous operations.',
                'a': 'The event loop is Node.js\'s mechanism for handling asynchronous operations. It has phases: timers, pending callbacks, idle/prepare, poll, check, close callbacks. Callbacks are queued and processed in phases. Non-blocking I/O operations are handled by libuv, allowing Node.js to handle many concurrent connections efficiently.'
            }
        ]
    },
    'Backend/Python': {
        'name': 'Python',
        'full_name': 'Python Backend',
        'description': 'Python is widely used for backend development with frameworks like Django, Flask, and FastAPI. It provides simplicity, extensive libraries, and strong community support for building web applications and APIs.',
        'category': 'Programming Language',
        'icon': '🐍',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What are the main Python web frameworks and their use cases?',
                'a': 'Django: Full-featured framework for complex applications (admin panel, ORM, authentication). Flask: Lightweight, flexible microframework for simple apps and APIs. FastAPI: Modern, fast framework for APIs with automatic documentation. Choose Django for full-stack apps, Flask for flexibility, FastAPI for high-performance APIs.'
            }
        ]
    },
    'Backend/Redis': {
        'name': 'Redis',
        'full_name': 'Redis',
        'description': 'Redis is an in-memory data structure store used as a database, cache, and message broker. It supports various data structures and provides high performance for caching and real-time applications.',
        'category': 'Database',
        'icon': '🔴',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is Redis and what are its main use cases?',
                'a': 'Redis is an in-memory key-value store. Use cases: caching (reduce database load), session storage, real-time analytics, message queues (pub/sub), leaderboards, rate limiting. It provides sub-millisecond latency and supports strings, hashes, lists, sets, sorted sets, and more.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain Redis persistence options (RDB vs AOF).',
                'a': 'RDB (Redis Database): Point-in-time snapshots, compact file size, faster recovery, but may lose data between snapshots. AOF (Append Only File): Logs every write operation, more durable, larger files, slower recovery. Can use both for maximum durability.'
            }
        ]
    },
    'Backend/SQLite': {
        'name': 'SQLite',
        'full_name': 'SQLite',
        'description': 'SQLite is a self-contained, serverless, zero-configuration SQL database engine. It stores the entire database in a single file and is ideal for embedded applications, development, and small to medium applications.',
        'category': 'Database',
        'icon': '🗄️',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is SQLite and when should you use it?',
                'a': 'SQLite is a file-based, serverless SQL database. Use it for: development/testing, embedded applications, mobile apps, small to medium applications, read-heavy workloads, and when you don\'t need concurrent writes. Avoid for: high-concurrency write scenarios, large datasets requiring distribution, or when you need advanced features like stored procedures.'
            }
        ]
    },
    'Databases/Elasticsearch': {
        'name': 'Elasticsearch',
        'full_name': 'Elasticsearch',
        'description': 'Elasticsearch is a distributed search and analytics engine built on Apache Lucene. It provides real-time search, analytics, and data storage capabilities, commonly used for log analysis, full-text search, and business intelligence.',
        'category': 'Search Engine',
        'icon': '🔍',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is Elasticsearch and what are its main features?',
                'a': 'Elasticsearch is a distributed search and analytics engine. Features: full-text search, real-time indexing, horizontal scalability, RESTful API, JSON documents, aggregations for analytics, and integration with Logstash and Kibana (ELK stack). It\'s built on Apache Lucene.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain Elasticsearch indexing and sharding.',
                'a': 'Indexing: Documents are stored in indices (like databases). Each document has a type and unique ID. Sharding: Indices are divided into shards for distribution across nodes. Primary shards are set at index creation, replica shards provide redundancy and read scaling. Shards enable horizontal scaling.'
            }
        ]
    },
    'Databases/MongoDB': {
        'name': 'MongoDB',
        'full_name': 'MongoDB',
        'description': 'MongoDB is a NoSQL document database that stores data in flexible, JSON-like documents. It provides horizontal scalability, flexible schema, and rich querying capabilities.',
        'category': 'NoSQL Database',
        'icon': '🍃',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is MongoDB and how does it differ from relational databases?',
                'a': 'MongoDB is a NoSQL document database. Differences: stores documents (BSON) vs tables/rows, flexible schema vs fixed schema, horizontal scaling vs vertical scaling, embedded documents vs normalized tables, JavaScript query language vs SQL. Use MongoDB for flexible schemas, rapid development, and horizontal scaling needs.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain MongoDB indexing and how to optimize queries.',
                'a': 'MongoDB uses B-tree indexes. Create indexes on frequently queried fields, compound indexes for multi-field queries, text indexes for full-text search. Use explain() to analyze query performance. Indexes improve read performance but slow writes. Monitor index usage and remove unused indexes.'
            }
        ]
    },
    'Databases/Neo4j': {
        'name': 'Neo4j',
        'full_name': 'Neo4j',
        'description': 'Neo4j is a graph database that stores data as nodes and relationships. It excels at querying complex relationships and is ideal for social networks, recommendation engines, and fraud detection.',
        'category': 'Graph Database',
        'icon': '🕸️',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is Neo4j and when should you use a graph database?',
                'a': 'Neo4j is a graph database storing data as nodes (entities) and relationships (edges). Use it for: social networks, recommendation engines, fraud detection, knowledge graphs, network analysis, and when relationships are as important as data. It excels at traversing complex relationships efficiently.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain Cypher query language basics.',
                'a': 'Cypher is Neo4j\'s query language. Syntax: (node:Label) for nodes, -[relationship:TYPE]-> for relationships. MATCH finds patterns, WHERE filters, RETURN specifies output. Example: MATCH (p:Person)-[:KNOWS]->(f:Person) WHERE p.name = "Alice" RETURN f.name. It\'s declarative and pattern-matching based.'
            }
        ]
    },
    'Databases/PostgreSQL': {
        'name': 'PostgreSQL',
        'full_name': 'PostgreSQL',
        'description': 'PostgreSQL is a powerful, open-source relational database system with advanced features like JSON support, full-text search, and extensibility. It\'s known for standards compliance and reliability.',
        'category': 'Relational Database',
        'icon': '🐘',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is PostgreSQL and what are its key features?',
                'a': 'PostgreSQL is an advanced open-source relational database. Features: ACID compliance, JSON/JSONB support, full-text search, array and hstore data types, extensibility (custom functions, data types), foreign data wrappers, and strong standards compliance. It\'s known for reliability and feature richness.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain PostgreSQL indexing strategies.',
                'a': 'PostgreSQL supports B-tree (default, general purpose), Hash (equality), GiST (geometric, full-text), GIN (array, full-text, JSONB), BRIN (large tables, sorted data). Choose index based on query patterns. Use EXPLAIN ANALYZE to analyze query plans. Indexes improve read performance but slow writes.'
            }
        ]
    },
    # Phase 6: GCP Services
    'GCP/Build': {
        'name': 'Cloud Build',
        'full_name': 'Google Cloud Build',
        'description': 'Google Cloud Build is a fully managed CI/CD platform that executes builds on Google Cloud. It can import source code from various repositories, execute builds, and produce artifacts like Docker containers or application archives.',
        'category': 'CI/CD',
        'icon': '🔨',
        'features': [
            '**Fully Managed**: No infrastructure to manage',
            '**Docker Support**: Native Docker container builds',
            '**Multi-language**: Support for various languages and frameworks',
            '**Integration**: Works with GitHub, Bitbucket, Cloud Source Repositories',
            '**Parallel Builds**: Execute multiple builds simultaneously',
            '**Customizable**: Define build steps with cloudbuild.yaml'
        ],
        'installation': '''# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login

# Set project
gcloud config set project PROJECT_ID

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com''',
        'code_examples': '''```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-app', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-app']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'my-app', '--image', 'gcr.io/$PROJECT_ID/my-app']
```''',
        'advanced_examples': '''```yaml
# Multi-stage build with caching
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--cache-from'
      - 'gcr.io/$PROJECT_ID/my-app:latest'
      - '-t'
      - 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA'
      - '.'
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-app:$SHORT_SHA']
```''',
        'best_practices': [
            '1. Use cloudbuild.yaml for build configuration',
            '2. Leverage build caching for faster builds',
            '3. Use substitution variables for flexibility',
            '4. Set appropriate timeout and machine types',
            '5. Use build triggers for automated builds',
            '6. Store secrets in Secret Manager',
            '7. Monitor build logs and metrics'
        ]
    },
    'GCP/Run': {
        'name': 'Cloud Run',
        'full_name': 'Google Cloud Run',
        'description': 'Cloud Run is a fully managed serverless platform that automatically scales stateless containers. It abstracts away infrastructure management, allowing you to focus on code while paying only for what you use.',
        'category': 'Serverless',
        'icon': '🚀',
        'features': [
            '**Serverless**: No infrastructure management',
            '**Auto-scaling**: Scales to zero and up automatically',
            '**Container-based**: Run any containerized application',
            '**Pay-per-use**: Pay only for request processing time',
            '**HTTPS**: Automatic SSL certificates',
            '**Integration**: Works with Cloud Build and other GCP services'
        ],
        'installation': '''# Deploy container to Cloud Run
gcloud run deploy SERVICE_NAME \\
    --image gcr.io/PROJECT_ID/IMAGE \\
    --platform managed \\
    --region us-central1

# Deploy from source
gcloud run deploy SERVICE_NAME \\
    --source . \\
    --platform managed''',
        'code_examples': '''```python
# Flask app for Cloud Run
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Cloud Run!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
```''',
        'advanced_examples': '''```yaml
# Cloud Run service configuration
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/my-app
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
```''',
        'best_practices': [
            '1. Make containers stateless',
            '2. Use environment variables for configuration',
            '3. Set appropriate CPU and memory limits',
            '4. Implement health checks',
            '5. Use Cloud Run Jobs for batch processing',
            '6. Configure concurrency appropriately',
            '7. Use Cloud Run for both HTTP and gRPC services'
        ]
    },
    'GCP/Storage': {
        'name': 'Cloud Storage',
        'full_name': 'Google Cloud Storage',
        'description': 'Google Cloud Storage is a unified object storage service for storing and accessing data. It offers industry-leading scalability, data availability, security, and performance for objects of any size.',
        'category': 'Storage',
        'icon': '☁️',
        'features': [
            '**Object Storage**: Store any type of data',
            '**Scalability**: Unlimited storage capacity',
            '**Durability**: 99.999999999% (11 9\'s) durability',
            '**Access Control**: Fine-grained IAM and ACLs',
            '**Lifecycle Management**: Automatic data lifecycle policies',
            '**Multi-region**: Global distribution options'
        ],
        'installation': '''# Create bucket
gsutil mb gs://BUCKET_NAME

# Upload file
gsutil cp file.txt gs://BUCKET_NAME/

# Download file
gsutil cp gs://BUCKET_NAME/file.txt .

# List buckets
gsutil ls''',
        'code_examples': '''```python
from google.cloud import storage

# Initialize client
client = storage.Client()
bucket = client.bucket('my-bucket')

# Upload file
blob = bucket.blob('path/to/file.txt')
blob.upload_from_filename('local-file.txt')

# Download file
blob.download_to_filename('downloaded-file.txt')

# List files
blobs = bucket.list_blobs()
for blob in blobs:
    print(blob.name)
```''',
        'advanced_examples': '''```python
# Signed URLs
from datetime import timedelta

url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(hours=1),
    method="GET"
)

# Lifecycle management
lifecycle = {
    "lifecycle": {
        "rule": [{
            "action": {"type": "Delete"},
            "condition": {"age": 30}
        }]
    }
}
bucket.lifecycle_rules = lifecycle
```''',
        'best_practices': [
            '1. Choose appropriate storage class (Standard, Nearline, Coldline, Archive)',
            '2. Use lifecycle policies for cost optimization',
            '3. Enable versioning for important data',
            '4. Use appropriate access controls (IAM, ACLs)',
            '5. Enable object retention and holds when needed',
            '6. Use Cloud CDN for frequently accessed content',
            '7. Monitor storage usage and costs'
        ]
    },
    'GCP/pro': {
        'name': 'Cloud Profiler',
        'full_name': 'Google Cloud Profiler',
        'description': 'Cloud Profiler is a statistical, low-overhead profiler that continuously gathers CPU and memory allocation information from production applications. It helps identify performance bottlenecks and optimize application performance.',
        'category': 'Monitoring',
        'icon': '📊',
        'features': [
            '**Low Overhead**: Minimal performance impact',
            '**Continuous Profiling**: Always-on profiling',
            '**Multi-language**: Support for Java, Python, Go, Node.js',
            '**CPU & Memory**: Profile both CPU and memory usage',
            '**Production Safe**: Designed for production environments',
            '**Integration**: Works with Cloud Monitoring and Logging'
        ],
        'installation': '''# Install profiler agent
pip install google-cloud-profiler

# Enable Profiler API
gcloud services enable cloudprofiler.googleapis.com

# Configure in application
import googlecloudprofiler
googlecloudprofiler.start(service='my-service')''',
        'code_examples': '''```python
# Python profiler setup
import googlecloudprofiler

def main():
    try:
        googlecloudprofiler.start(
            service='my-service',
            service_version='1.0.0',
            verbose=1
        )
    except Exception:
        pass  # Log error but continue
    
    # Your application code
    app.run()
```''',
        'advanced_examples': '''```python
# Custom profiling
import googlecloudprofiler

profiler = googlecloudprofiler.Profiler()
profiler.start()

# Profile specific functions
@profiler.profile
def expensive_function():
    # Code to profile
    pass
```''',
        'best_practices': [
            '1. Enable profiler in production for continuous insights',
            '2. Use appropriate service and version labels',
            '3. Monitor profiler overhead',
            '4. Analyze profiles regularly for optimization opportunities',
            '5. Use with Cloud Monitoring for comprehensive observability',
            '6. Profile both CPU and memory',
            '7. Compare profiles over time to track improvements'
        ]
    },
    # Phase 7: DevOps & Others
    'DevOps/GitHub-Actions': {
        'name': 'GitHub Actions',
        'full_name': 'GitHub Actions',
        'description': 'GitHub Actions is a CI/CD platform that enables automation of software workflows directly in GitHub repositories. It allows you to build, test, and deploy code with custom workflows defined in YAML files.',
        'category': 'CI/CD',
        'icon': '⚙️',
        'features': [
            '**Workflow Automation**: Automate any software workflow',
            '**CI/CD**: Continuous integration and deployment',
            '**Event-driven**: Trigger on push, PR, issues, and more',
            '**Matrix Builds**: Test across multiple versions',
            '**Secrets Management**: Secure storage of sensitive data',
            '**Marketplace**: Thousands of pre-built actions'
        ],
        'installation': '''# Create .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest''',
        'code_examples': '''```yaml
# Complete CI/CD workflow
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        run: ./deploy.sh
```''',
        'advanced_examples': '''```yaml
# Matrix build
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]
    os: [ubuntu-latest, windows-latest, macos-latest]

# Secrets
env:
  API_KEY: ${{ secrets.API_KEY }}

# Caching
- uses: actions/cache@v3
  with:
    path: ~/.pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```''',
        'best_practices': [
            '1. Use reusable workflows for common patterns',
            '2. Cache dependencies to speed up builds',
            '3. Use matrix builds for testing multiple versions',
            '4. Store secrets in GitHub Secrets',
            '5. Use appropriate triggers (push, PR, schedule)',
            '6. Set up branch protection rules',
            '7. Monitor workflow runs and optimize execution time'
        ]
    },
    'DataWarehousing': {
        'name': 'Data Warehousing',
        'full_name': 'Data Warehousing',
        'description': 'Data warehousing is the process of collecting, storing, and managing data from various sources to support business intelligence and analytics. Modern data warehouses use cloud-based solutions for scalability and performance.',
        'category': 'Data Architecture',
        'icon': '🏢',
        'features': [
            '**Centralized Storage**: Single source of truth for analytics',
            '**ETL/ELT**: Extract, transform, and load processes',
            '**OLAP**: Optimized for analytical queries',
            '**Scalability**: Handle large volumes of data',
            '**Historical Data**: Store historical data for trend analysis',
            '**Integration**: Connect multiple data sources'
        ],
        'installation': '''# BigQuery (GCP data warehouse)
# Use gcloud CLI or web console
gcloud auth login
gcloud config set project PROJECT_ID

# Create dataset
bq mk --dataset PROJECT_ID:DATASET_NAME

# Load data
bq load --source_format=CSV DATASET.TABLE gs://bucket/data.csv''',
        'code_examples': '''```sql
-- Create table
CREATE TABLE `project.dataset.sales` (
  date DATE,
  product_id STRING,
  revenue FLOAT64,
  quantity INT64
);

-- Load data
LOAD DATA INTO `project.dataset.sales`
FROM FILES (
  format = 'CSV',
  uris = ['gs://bucket/sales.csv']
);

-- Query
SELECT 
  DATE_TRUNC(date, MONTH) as month,
  SUM(revenue) as total_revenue
FROM `project.dataset.sales`
GROUP BY month
ORDER BY month;
```''',
        'advanced_examples': '''```sql
-- Partitioned table
CREATE TABLE `project.dataset.sales_partitioned`
PARTITION BY DATE(date)
AS SELECT * FROM `project.dataset.sales`;

-- Clustered table
CREATE TABLE `project.dataset.sales_clustered`
PARTITION BY DATE(date)
CLUSTER BY product_id
AS SELECT * FROM `project.dataset.sales`;
```''',
        'best_practices': [
            '1. Design schema for analytical queries (star/snowflake schema)',
            '2. Use partitioning for large tables',
            '3. Implement clustering for query optimization',
            '4. Normalize or denormalize based on query patterns',
            '5. Implement data quality checks',
            '6. Use incremental loads for efficiency',
            '7. Document data lineage and transformations'
        ]
    },
    'MachineLearning': {
        'name': 'Machine Learning',
        'full_name': 'Machine Learning',
        'description': 'Machine Learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It includes supervised, unsupervised, and reinforcement learning approaches.',
        'category': 'AI/ML',
        'icon': '🤖',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is machine learning and how does it differ from traditional programming?',
                'a': 'Machine learning is a method where algorithms learn patterns from data to make predictions or decisions, rather than following explicit instructions. Traditional programming: input + rules → output. ML: input + output → rules (model). ML adapts and improves with more data.'
            },
            {
                'level': 'Intermediate',
                'q': 'Explain the difference between supervised, unsupervised, and reinforcement learning.',
                'a': 'Supervised: Learn from labeled data (input-output pairs). Examples: classification, regression. Unsupervised: Find patterns in unlabeled data. Examples: clustering, dimensionality reduction. Reinforcement: Learn through interaction with environment, receiving rewards/penalties. Examples: game playing, robotics.'
            }
        ]
    },
    'VertexAI': {
        'name': 'Vertex AI',
        'full_name': 'Google Vertex AI',
        'description': 'Vertex AI is Google Cloud\'s unified machine learning platform that helps you build, deploy, and scale ML models. It provides tools for the entire ML lifecycle from data preparation to model deployment.',
        'category': 'ML Platform',
        'icon': '🧠',
        'interview_questions': [
            {
                'level': 'Beginner',
                'q': 'What is Vertex AI and what are its main components?',
                'a': 'Vertex AI is Google Cloud\'s unified ML platform. Components: AutoML (no-code ML), Custom Training (custom models), Vertex AI Workbench (Jupyter notebooks), Feature Store (feature management), Model Registry (model versioning), Endpoints (model serving), Pipelines (ML workflows), and Explainable AI.'
            },
            {
                'level': 'Intermediate',
                'q': 'How do you deploy a model to Vertex AI?',
                'a': '1. Train model locally or on Vertex AI. 2. Upload model to Model Registry. 3. Create endpoint. 4. Deploy model to endpoint with traffic splitting. 5. Send prediction requests. Use Vertex AI SDK or gcloud CLI. Can deploy multiple model versions with A/B testing.'
            }
        ]
    },
}

def create_what_md(tech_dir, tech_key, metadata):
    """Create comprehensive what.md file"""
    name = metadata.get('name', tech_key.split('/')[-1])
    full_name = metadata.get('full_name', name)
    description = metadata.get('description', f'{full_name} comprehensive guide')
    features = metadata.get('features', [])
    installation = metadata.get('installation', '```bash\n# Installation instructions\n```')
    code_examples = metadata.get('code_examples', '```python\n# Code examples\n```')
    advanced_examples = metadata.get('advanced_examples', '```python\n# Advanced examples\n```')
    best_practices = metadata.get('best_practices', [])
    
    content = f"""# {full_name}: Comprehensive Guide

## Overview

{description}

## Core Concepts

### What is {full_name}?

{description}

## Key Features

"""
    for feature in features:
        content += f"{feature}\n\n"
    
    content += f"""## Installation

{installation}

## Getting Started

{code_examples}

## Advanced Usage

{advanced_examples}

## Best Practices

"""
    for practice in best_practices:
        content += f"{practice}\n"
    
    content += f"""
## References

- Official documentation: 
- GitHub repository:
"""
    return content

def create_visual_md(tech_dir, tech_key, metadata):
    """Create Visual.md file with Mermaid diagrams"""
    name = metadata.get('name', tech_key.split('/')[-1])
    full_name = metadata.get('full_name', name)
    category = metadata.get('category', 'Technology')
    
    content = f"""# {full_name}: Visual Guide

## Architecture Diagrams

### {full_name} Architecture

```mermaid
graph TD
    A[{full_name}] --> B[Component 1]
    A --> C[Component 2]
    A --> D[Component 3]
    B --> E[Feature 1]
    C --> F[Feature 2]
    D --> G[Feature 3]
    
    style A fill:#150458
    style B fill:#C13C37
    style C fill:#F7931E
```

### Data Flow

```mermaid
graph LR
    A[Input] --> B[Process]
    B --> C[Transform]
    C --> D[Output]
    
    style A fill:#4A90E2
    style D fill:#50C878
```

### Workflow

```mermaid
flowchart TD
    Start([Start]) --> Step1[Step 1]
    Step1 --> Step2[Step 2]
    Step2 --> Step3[Step 3]
    Step3 --> End([End])
    
    style Start fill:#4A90E2
    style End fill:#50C878
```

### Component Interaction

```mermaid
sequenceDiagram
    participant A as Client
    participant B as {full_name}
    participant C as Backend
    
    A->>B: Request
    B->>C: Process
    C-->>B: Response
    B-->>A: Result
```
"""
    return content

def create_interview_md(tech_dir, tech_key, metadata):
    """Create Interview.md file"""
    name = metadata.get('name', tech_key.split('/')[-1])
    full_name = metadata.get('full_name', name)
    description = metadata.get('description', f'{full_name} comprehensive guide')
    interview_questions = metadata.get('interview_questions', [])
    features = metadata.get('features', [])
    
    content = f"""# {full_name} Interview Questions and Answers

## Beginner Level Questions

### Q1: What is {full_name} and what problem does it solve?

**Answer:**

{description}

**Key Use Cases:**
- Use case 1
- Use case 2
- Use case 3

### Q2: What are the core features of {full_name}?

**Answer:**

The core features include:

"""
    for feature in features[:5]:  # Limit to first 5
        content += f"{feature}\n\n"
    
    if interview_questions:
        # Group questions by level
        questions_by_level = {}
        for qa in interview_questions:
            level = qa.get('level', 'Intermediate')
            if level not in questions_by_level:
                questions_by_level[level] = []
            questions_by_level[level].append(qa)
        
        # Add questions grouped by level
        level_order = ['Beginner', 'Intermediate', 'Advanced']
        for level in level_order:
            if level in questions_by_level:
                # Only add header if not already in Beginner section
                if level != 'Beginner':
                    content += f"\n## {level} Level Questions\n\n"
                for qa in questions_by_level[level]:
                    question = qa.get('q', '')
                    answer = qa.get('a', '')
                    content += f"""### {question}

**Answer:**

{answer}

"""
    else:
        # Default questions
        content += f"""### Q3: How do you get started with {full_name}?

**Answer:**

```bash
# Installation and setup steps
```

## Intermediate Level Questions

### Q4: What are the best practices for using {full_name}?

**Answer:**

1. Best practice 1
2. Best practice 2
3. Best practice 3

## Advanced Level Questions

### Q5: How does {full_name} handle [advanced topic]?

**Answer:**

Advanced explanation with code examples.

```python
# Example code
```
"""
    
    content += """
## References

- Official documentation
- Community resources
"""
    return content

def main():
    print("🚀 Generating all missing documentation files...\n")
    
    # Define all directories that need files according to DOCUMENTATION_PLAN.md
    directories_to_process = [
        # Phase 1: Tools (need all 3 files)
        ('Tools/Jupyter', ['what.md', 'Visual.md', 'Interview.md']),
        ('Tools/Plotly', ['what.md', 'Visual.md', 'Interview.md']),
        ('Tools/Seaborn', ['what.md', 'Visual.md', 'Interview.md']),
        # Phase 1: Tools (need Interview.md only)
        ('Tools/Git', ['Interview.md']),
        ('Tools/VS-Code', ['Interview.md']),
        # Phase 2: Data Engineering
        ('DataEngineering/Java', ['what.md', 'Visual.md', 'Interview.md']),
        ('DataEngineering/Kafka', ['what.md', 'Visual.md', 'Interview.md']),
        ('DataEngineering/Python', ['what.md', 'Visual.md', 'Interview.md']),
        ('DataEngineering/Scala', ['what.md', 'Visual.md', 'Interview.md']),
        # Phase 3: Gen-AI
        ('Gen-AI/Embeddings', ['what.md', 'Visual.md', 'Interview.md']),
        ('Gen-AI/LangChain', ['what.md', 'Visual.md', 'Interview.md']),
        ('Gen-AI/OpenAI-GPT', ['what.md', 'Visual.md', 'Interview.md']),
        ('Gen-AI/Vector-Databases', ['what.md', 'Visual.md', 'Interview.md']),
        # Phase 4: Frontend (need all 3 files)
        ('Frontend/D3.js', ['what.md', 'Visual.md', 'Interview.md']),
        ('Frontend/Material-UI', ['what.md', 'Visual.md', 'Interview.md']),
        ('Frontend/Streamlit', ['what.md', 'Visual.md', 'Interview.md']),
        ('Frontend/TypeScript', ['what.md', 'Visual.md', 'Interview.md']),
        # Phase 4: Frontend (need Interview.md only)
        ('Frontend/React', ['Interview.md']),
        # Phase 5: Backend & Databases (need Interview.md only)
        ('Backend/FastAPI', ['Interview.md']),
        ('Backend/Node.js', ['Interview.md']),
        ('Backend/Python', ['Interview.md']),
        ('Backend/Redis', ['Interview.md']),
        ('Backend/SQLite', ['Interview.md']),
        ('Databases/Elasticsearch', ['Interview.md']),
        ('Databases/MongoDB', ['Interview.md']),
        ('Databases/Neo4j', ['Interview.md']),
        ('Databases/PostgreSQL', ['Interview.md']),
        # Phase 6: GCP Services
        ('GCP/Build', ['what.md', 'Visual.md', 'Interview.md']),
        ('GCP/Run', ['what.md', 'Visual.md', 'Interview.md']),
        ('GCP/Storage', ['what.md', 'Visual.md', 'Interview.md']),
        ('GCP/pro', ['what.md', 'Visual.md', 'Interview.md']),
        # Phase 7: DevOps & Others
        ('DevOps/GitHub-Actions', ['what.md', 'Visual.md', 'Interview.md']),
        ('DataWarehousing', ['what.md', 'Visual.md', 'Interview.md']),
        ('MachineLearning', ['Interview.md']),
        ('VertexAI', ['Interview.md']),
    ]
    
    created = 0
    skipped = 0
    
    for tech_key, files_needed in directories_to_process:
        tech_dir = BASE_DIR / tech_key
        tech_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = TECH_METADATA.get(tech_key, {
            'name': tech_key.split('/')[-1],
            'full_name': tech_key.split('/')[-1],
            'description': f'{tech_key.split("/")[-1]} comprehensive guide',
            'features': [],
            'best_practices': []
        })
        
        for file_type in files_needed:
            file_path = tech_dir / file_type
            
            if file_path.exists():
                print(f"  ⏭️  Skipped {tech_key}/{file_type} (already exists)")
                skipped += 1
                continue
            
            if file_type == 'what.md':
                content = create_what_md(tech_dir, tech_key, metadata)
            elif file_type == 'Visual.md':
                content = create_visual_md(tech_dir, tech_key, metadata)
            elif file_type == 'Interview.md':
                content = create_interview_md(tech_dir, tech_key, metadata)
            else:
                continue
            
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ Created {tech_key}/{file_type}")
            created += 1
    
    print(f"\n✨ Done! Created {created} files, skipped {skipped} existing files")

if __name__ == '__main__':
    main()

