# Python: Comprehensive Guide

## Overview

Python is a high-level, interpreted programming language known for its simplicity, readability, and versatility. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python's extensive standard library and vast ecosystem of third-party packages make it ideal for web development, data science, machine learning, automation, and system administration.

## Core Language Features

### Advanced Data Structures

```python
from collections import defaultdict, Counter, deque, namedtuple
from typing import List, Dict, Tuple, Optional, Union, Any
import heapq
from dataclasses import dataclass, field
from enum import Enum

# Named tuples for structured data
Person = namedtuple('Person', ['name', 'age', 'city'])
person = Person('Alice', 30, 'New York')
print(f"{person.name} is {person.age} years old")

# Default dictionaries
word_counts = defaultdict(int)
words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']
for word in words:
    word_counts[word] += 1
print(dict(word_counts))  # {'apple': 3, 'banana': 2, 'cherry': 1}

# Counters for frequency counting
counter = Counter(words)
print(counter.most_common(2))  # [('apple', 3), ('banana', 2)]

# Deques for efficient appends/pops from both ends
dq = deque([1, 2, 3])
dq.append(4)        # Add to right
dq.appendleft(0)    # Add to left
dq.pop()           # Remove from right
dq.popleft()       # Remove from left
print(list(dq))     # [1, 2, 3]

# Data classes for structured data with less boilerplate
@dataclass
class Employee:
    name: str
    age: int
    salary: float
    department: str = "Engineering"
    skills: List[str] = field(default_factory=list)

    def give_raise(self, percentage: float) -> None:
        self.salary *= (1 + percentage / 100)

    def add_skill(self, skill: str) -> None:
        if skill not in self.skills:
            self.skills.append(skill)

emp = Employee("Bob", 28, 75000.0)
emp.give_raise(10)
emp.add_skill("Python")
emp.add_skill("Machine Learning")
print(emp)

# Enums for constants
class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Priority queues with heapq
class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self):
        return heapq.heappop(self._queue)[-1]

pq = PriorityQueue()
pq.push("low priority", 1)
pq.push("high priority", 5)
pq.push("medium priority", 3)

print(pq.pop())  # high priority
print(pq.pop())  # medium priority
print(pq.pop())  # low priority
```

### Advanced Function Features

```python
from functools import partial, wraps, lru_cache
import time
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

# Decorators
def timing_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def retry_decorator(max_retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# LRU Cache for memoization
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Partial functions
def power(base: float, exponent: float) -> float:
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(3))    # 27

# Function annotations and type hints
def process_data(data: List[Dict[str, Any]], threshold: float = 0.5) -> List[Dict[str, Any]]:
    """Process data with type hints"""
    return [item for item in data if item.get('score', 0) > threshold]

# Generic functions
def find_max(items: List[T]) -> Optional[T]:
    return max(items) if items else None

# Lambda functions with advanced usage
operations = {
    'add': lambda x, y: x + y,
    'subtract': lambda x, y: x - y,
    'multiply': lambda x, y: x * y,
    'divide': lambda x, y: x / y if y != 0 else float('inf')
}

def apply_operation(op_name: str, x: float, y: float) -> float:
    return operations[op_name](x, y)

# Closures
def create_multiplier(factor: int):
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier

double = create_multiplier(2)
triple = create_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15

# Generators for memory-efficient iteration
def fibonacci_generator(limit: int):
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1

# Generator expressions
squares = (x**2 for x in range(10))
even_squares = (x for x in squares if x % 2 == 0)

print(list(even_squares))  # [0, 4, 16, 36, 64]
```

### Object-Oriented Programming

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

# Abstract base classes
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

    def description(self) -> str:
        return f"This is a {self.__class__.__name__}"

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius

# Protocols for structural typing
@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Canvas:
    def __init__(self):
        self.shapes: List[Shape] = []
        self.drawables: List[Drawable] = []

    def add_shape(self, shape: Shape) -> None:
        self.shapes.append(shape)

    def add_drawable(self, drawable: Drawable) -> None:
        self.drawables.append(drawable)

    def render(self) -> None:
        for shape in self.shapes:
            print(f"Shape: {shape.description()}, Area: {shape.area()}")

        for drawable in self.drawables:
            drawable.draw()

# Multiple inheritance and method resolution order
class LoggerMixin:
    def log(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")

class SerializerMixin:
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerializerMixin':
        return cls(**data)

class User(LoggerMixin, SerializerMixin):
    def __init__(self, name: str, email: str, age: int):
        self.name = name
        self.email = email
        self.age = age

    def greet(self) -> str:
        self.log(f"Greeting user {self.name}")
        return f"Hello, {self.name}!"

# Property decorators
class Temperature:
    def __init__(self, celsius: float = 0.0):
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return (self._celsius * 9/5) + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5/9

# Context managers
class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None

    def __enter__(self):
        # Simulate database connection
        self.connection = f"Connected to {self.connection_string}"
        print("Database connection opened")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        print("Database connection closed")
        self.connection = None
        return False  # Don't suppress exceptions

# Using context manager
with DatabaseConnection("postgresql://localhost/mydb") as conn:
    print(f"Using connection: {conn}")
    # Do database operations

# Class decorators
def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class Configuration:
    def __init__(self):
        self.settings = {
            'debug': False,
            'max_connections': 100,
            'timeout': 30
        }

config1 = Configuration()
config2 = Configuration()
print(config1 is config2)  # True - same instance
```

## Data Science and Machine Learning

### NumPy Advanced Operations

```python
import numpy as np

# Advanced array operations
arr = np.random.randn(3, 4, 5)
print(f"Shape: {arr.shape}")
print(f"Size: {arr.size}")
print(f"Number of dimensions: {arr.ndim}")

# Broadcasting
a = np.array([1, 2, 3])
b = np.array([[1], [2], [3]])
result = a + b  # Broadcasting
print(result)
# [[2 3 4]
#  [3 4 5]
#  [4 5 6]]

# Vectorized operations
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def relu(x):
    return np.maximum(0, x)

x = np.random.randn(1000, 1000)
sigmoid_result = sigmoid(x)
relu_result = relu(x)

# Linear algebra operations
A = np.random.randn(100, 100)
B = np.random.randn(100, 100)

# Matrix multiplication
C = np.dot(A, B)
C_alternative = A @ B

# Eigenvalue decomposition
eigenvalues, eigenvectors = np.linalg.eig(A)

# Singular value decomposition
U, s, Vt = np.linalg.svd(A)

# Advanced indexing
arr = np.arange(24).reshape(4, 6)
print(arr)
# [[ 0  1  2  3  4  5]
#  [ 6  7  8  9 10 11]
#  [12 13 14 15 16 17]
#  [18 19 20 21 22 23]]

# Boolean indexing
mask = arr > 10
filtered = arr[mask]

# Fancy indexing
rows = np.array([0, 2, 3])
cols = np.array([1, 3, 5])
selected = arr[rows, cols]  # [1, 15, 23]

# Memory-efficient operations
arr = np.random.randn(10000, 10000)

# In-place operations
arr += 1
arr *= 2

# Memory mapping for large arrays
large_array = np.memmap('large_array.dat', dtype='float64', mode='w+', shape=(100000, 100000))
large_array[:] = np.random.randn(100000, 100000)
large_array.flush()  # Write to disk

# Structured arrays
dt = np.dtype([('name', 'U20'), ('age', 'i4'), ('salary', 'f8')])
employees = np.array([
    ('Alice', 30, 75000.0),
    ('Bob', 25, 65000.0),
    ('Charlie', 35, 85000.0)
], dtype=dt)

print(employees['name'])
print(employees['salary'].mean())
```

### Pandas Advanced Operations

```python
import pandas as pd
import numpy as np

# Advanced DataFrame operations
df = pd.DataFrame({
    'A': np.random.randn(1000),
    'B': np.random.randint(0, 100, 1000),
    'C': pd.date_range('2020-01-01', periods=1000),
    'D': pd.Categorical(np.random.choice(['X', 'Y', 'Z'], 1000))
})

# GroupBy operations with multiple aggregations
grouped = df.groupby('D').agg({
    'A': ['mean', 'std', 'count'],
    'B': ['sum', 'max', 'min']
})
print(grouped)

# Window operations
df['A_rolling_mean'] = df['A'].rolling(window=30).mean()
df['A_expanding_mean'] = df['A'].expanding().mean()

# Time series operations
df.set_index('C', inplace=True)
monthly_data = df.resample('M').agg({
    'A': 'mean',
    'B': 'sum'
})

# Pivot tables
pivot = df.pivot_table(
    values='A',
    index=df.index.month,
    columns='D',
    aggfunc='mean'
)

# MultiIndex operations
arrays = [['A', 'A', 'B', 'B'], ['one', 'two', 'one', 'two']]
index = pd.MultiIndex.from_arrays(arrays, names=['first', 'second'])
df_multi = pd.DataFrame(np.random.randn(4, 3), index=index, columns=['X', 'Y', 'Z'])

print(df_multi.loc['A'])
print(df_multi.loc[('A', 'one')])

# Advanced merging and joining
df1 = pd.DataFrame({'key': ['A', 'B', 'C'], 'value1': [1, 2, 3]})
df2 = pd.DataFrame({'key': ['A', 'B', 'D'], 'value2': [4, 5, 6]})

# Different join types
inner_join = pd.merge(df1, df2, on='key', how='inner')
left_join = pd.merge(df1, df2, on='key', how='left')
outer_join = pd.merge(df1, df2, on='key', how='outer')

# Melt and pivot for reshaping
df_wide = pd.DataFrame({
    'student': ['Alice', 'Bob', 'Charlie'],
    'math': [90, 85, 95],
    'science': [88, 92, 87],
    'english': [85, 88, 90]
})

# Melt to long format
df_long = pd.melt(df_wide, id_vars=['student'], var_name='subject', value_name='score')

# Pivot back to wide format
df_wide_again = df_long.pivot(index='student', columns='subject', values='score')

# Advanced string operations
df_text = pd.DataFrame({
    'text': [
        'Hello World Python',
        'Machine Learning AI',
        'Data Science Analytics',
        'Web Development Flask'
    ]
})

df_text['word_count'] = df_text['text'].str.split().str.len()
df_text['contains_python'] = df_text['text'].str.contains('Python', case=False)
df_text['first_word'] = df_text['text'].str.split().str[0]

# Categorical data operations
df['D'] = df['D'].astype('category')
print(df['D'].cat.categories)
print(df['D'].cat.codes)

# Memory optimization
df_optimized = df.copy()
df_optimized['B'] = df_optimized['B'].astype('int32')  # Downcast integers
df_optimized['A'] = df_optimized['A'].astype('float32')  # Downcast floats

print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
print(f"Optimized memory usage: {df_optimized.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
```

### Scikit-learn Advanced Usage

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# Sample dataset
from sklearn.datasets import make_classification
X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Advanced pipeline with feature engineering
numeric_features = [0, 1, 2, 3, 4]  # Assuming first 5 features are numeric
categorical_features = [5, 6, 7]     # Assuming next 3 features are categorical

numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler()),
    ('poly', PolynomialFeatures(degree=2, include_bias=False))
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Complete pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Hyperparameter tuning with GridSearchCV
param_grid = {
    'classifier__n_estimators': [100, 200, 300],
    'classifier__max_depth': [10, 20, None],
    'classifier__min_samples_split': [2, 5, 10],
    'preprocessor__num__poly__degree': [1, 2]
}

grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)
print(f"Best parameters: {grid_search.best_params_}")
print(f"Best cross-validation score: {grid_search.best_score_:.3f}")

# Ensemble methods
rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
lr_clf = LogisticRegression(random_state=42)
svm_clf = SVC(probability=True, random_state=42)

voting_clf = VotingClassifier(
    estimators=[('rf', rf_clf), ('lr', lr_clf), ('svm', svm_clf)],
    voting='soft'  # Use probability-based voting
)

# Cross-validation scores
cv_scores = cross_val_score(voting_clf, X_train, y_train, cv=5, scoring='accuracy')
print(f"Cross-validation scores: {cv_scores}")
print(f"Mean CV score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

# Fit and evaluate
voting_clf.fit(X_train, y_train)
y_pred = voting_clf.predict(X_test)
y_pred_proba = voting_clf.predict_proba(X_test)[:, 1]

print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print(f"AUC-ROC Score: {roc_auc_score(y_test, y_pred_proba):.3f}")

# Feature importance analysis
feature_importance = grid_search.best_estimator_.named_steps['classifier'].feature_importances_
print(f"Feature importances shape: {feature_importance.shape}")

# Custom transformers
from sklearn.base import BaseEstimator, TransformerMixin

class OutlierRemover(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=3.0):
        self.threshold = threshold

    def fit(self, X, y=None):
        # Calculate z-scores for each feature
        self.mean_ = np.mean(X, axis=0)
        self.std_ = np.std(X, axis=0)
        return self

    def transform(self, X):
        # Remove outliers based on z-score
        z_scores = np.abs((X - self.mean_) / self.std_)
        mask = (z_scores < self.threshold).all(axis=1)
        return X[mask]

class FeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, k=10):
        self.k = k

    def fit(self, X, y):
        from sklearn.feature_selection import SelectKBest, f_classif
        self.selector = SelectKBest(score_func=f_classif, k=self.k)
        self.selector.fit(X, y)
        return self

    def transform(self, X):
        return self.selector.transform(X)

# Advanced pipeline with custom transformers
advanced_pipeline = Pipeline(steps=[
    ('outlier_removal', OutlierRemover(threshold=3.0)),
    ('feature_selection', FeatureSelector(k=15)),
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Model persistence
import joblib

# Save the best model
joblib.dump(grid_search.best_estimator_, 'best_model.pkl')

# Load the model
loaded_model = joblib.load('best_model.pkl')

# Make predictions with loaded model
predictions = loaded_model.predict(X_test)
print(f"Loaded model accuracy: {(predictions == y_test).mean():.3f}")
```

## Web Development

### Flask Advanced Features

```python
from flask import Flask, request, jsonify, g, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import time
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Logging configuration
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != 'admin':
            flash('Admin access required')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def timing_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        app.logger.info(f'{f.__name__} took {end - start:.4f} seconds')
        return result
    return decorated_function

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

# Request hooks
@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start
    app.logger.info(f'Request took {diff:.4f} seconds')
    return response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Routes
@app.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).limit(10).all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
        'author': post.author.username,
        'timestamp': post.timestamp.isoformat()
    } for post in posts])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('Invalid username or password')

    return jsonify({'message': 'Login required'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            return jsonify({'error': 'Username already exists'}), 400

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Registration successful'}), 201

    return jsonify({'errors': form.errors}), 400

@app.route('/posts', methods=['POST'])
@login_required
@timing_decorator
def create_post():
    data = request.get_json()

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content required'}), 400

    post = Post(title=data['title'], content=data['content'], author=current_user)
    db.session.add(post)
    db.session.commit()

    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'timestamp': post.timestamp.isoformat()
    }), 201

@app.route('/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'GET':
        return jsonify({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'timestamp': post.timestamp.isoformat()
        })

    if request.method == 'PUT':
        if post.author != current_user:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']

        db.session.commit()
        return jsonify({'message': 'Post updated'})

    if request.method == 'DELETE':
        if post.author != current_user:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted'})

# API versioning
@app.route('/api/v1/users')
@login_required
@admin_required
def get_users_v1():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email
    } for user in users])

@app.route('/api/v2/users')
@login_required
@admin_required
def get_users_v2():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'post_count': user.posts.count(),
        'registered_date': user.id  # Simplified for example
    } for user in users])

# Blueprint for modular organization
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Advanced Features

```python
from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uvicorn
import asyncio
from datetime import datetime, timedelta
import jwt
import aiofiles
import databases
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Database setup
DATABASE_URL = "sqlite:///./app.db"
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("hashed_password", sqlalchemy.String),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow),
)

posts_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("content", sqlalchemy.Text),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# Pydantic models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    author: User

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception

    query = users_table.select().where(users_table.c.username == token_data.username)
    user = await database.fetch_one(query)
    if user is None:
        raise credentials_exception
    return user

# FastAPI app
app = FastAPI(
    title="Advanced FastAPI App",
    description="A comprehensive FastAPI application with advanced features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Authentication routes
@app.post("/auth/register", response_model=User)
async def register(user: UserCreate):
    # Check if user exists
    query = users_table.select().where(users_table.c.username == user.username)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash password
    hashed_password = user.password + "hashed"  # Use proper hashing in production

    # Create user
    query = users_table.insert().values(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    user_id = await database.execute(query)

    return {**user.dict(), "id": user_id, "created_at": datetime.utcnow()}

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserCreate):
    query = users_table.select().where(users_table.c.username == user_credentials.username)
    user = await database.fetch_one(query)

    if not user or user.hashed_password != user_credentials.password + "hashed":
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# API routes
@app.get("/users/me", response_model=User)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

@app.get("/users/", response_model=List[User])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    query = users_table.select().offset(skip).limit(limit)
    users = await database.fetch_all(query)
    return users

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int = Path(..., gt=0), current_user = Depends(get_current_user)):
    query = users_table.select().where(users_table.c.id == user_id)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/posts/", response_model=Post)
async def create_post(
    post: PostCreate,
    current_user = Depends(get_current_user)
):
    query = posts_table.insert().values(
        title=post.title,
        content=post.content,
        user_id=current_user.id
    )
    post_id = await database.execute(query)

    # Fetch the created post with author info
    query = posts_table.select().where(posts_table.c.id == post_id)
    created_post = await database.fetch_one(query)

    return {**created_post, "author": current_user}

@app.get("/posts/", response_model=List[Post])
async def read_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    query = (
        posts_table.select()
        .select_from(posts_table.join(users_table))
        .offset(skip)
        .limit(limit)
    )
    posts = await database.fetch_all(query)
    return posts

@app.get("/posts/{post_id}", response_model=Post)
async def read_post(
    post_id: int = Path(..., gt=0),
    current_user = Depends(get_current_user)
):
    query = (
        posts_table.select()
        .select_from(posts_table.join(users_table))
        .where(posts_table.c.id == post_id)
    )
    post = await database.fetch_one(query)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# File upload
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    async with aiofiles.open(f"uploads/{file.filename}", 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return {"filename": file.filename}

# Streaming response
@app.get("/stream-data/")
async def stream_data():
    async def generate_data():
        for i in range(100):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(
        generate_data(),
        media_type="text/plain"
    )

# Background tasks
from fastapi import BackgroundTasks

def send_email_notification(email: str, message: str):
    # Simulate sending email
    print(f"Sending email to {email}: {message}")

@app.post("/send-notification/")
async def send_notification(
    email: str = Body(...),
    message: str = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    background_tasks.add_task(send_email_notification, email, message)
    return {"message": "Notification will be sent in the background"}

# Dependency injection
def get_database():
    return database

async def get_db():
    db = get_database()
    try:
        yield db
    finally:
        pass  # Connection cleanup if needed

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

## Automation and System Administration

### Advanced File Operations

```python
import os
import shutil
import pathlib
import glob
from pathlib import Path
import tempfile
import zipfile
import tarfile
import gzip
import bz2
import lzma

# Path operations with pathlib
def organize_files_by_extension(source_dir: str, target_dir: str):
    """Organize files by extension using pathlib"""

    source_path = Path(source_dir)
    target_path = Path(target_dir)

    for file_path in source_path.rglob('*'):
        if file_path.is_file():
            extension = file_path.suffix.lower()

            # Create extension directory
            ext_dir = target_path / extension[1:] if extension else 'no_extension'
            ext_dir.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(file_path), str(ext_dir / file_path.name))

def find_large_files(directory: str, min_size_mb: float = 100):
    """Find files larger than specified size"""

    min_size_bytes = min_size_mb * 1024 * 1024
    large_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > min_size_bytes:
                    large_files.append((file_path, size))
            except OSError:
                continue

    return sorted(large_files, key=lambda x: x[1], reverse=True)

def create_backup(source_dir: str, backup_dir: str, compression: str = 'gzip'):
    """Create compressed backup of directory"""

    source_path = Path(source_dir)
    backup_path = Path(backup_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{timestamp}"

    if compression == 'zip':
        backup_file = backup_path / f"{backup_name}.zip"
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(source_path))

    elif compression == 'tar':
        backup_file = backup_path / f"{backup_name}.tar.gz"
        with tarfile.open(backup_file, 'w:gz') as tarf:
            tarf.add(source_path, arcname=source_path.name)

    return backup_file

# Temporary files and directories
def process_with_temp_file(data: bytes):
    """Process data using temporary file"""

    with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
        temp_file.write(data)
        temp_file.flush()

        # Process the temporary file
        process_file(temp_file.name)

    # Clean up
    os.unlink(temp_file.name)

def create_temp_directory():
    """Create and use temporary directory"""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create some files
        (temp_path / 'file1.txt').write_text('Hello World')
        (temp_path / 'file2.txt').write_text('Python Automation')

        # Process files
        for file_path in temp_path.glob('*.txt'):
            print(f"Processing {file_path.name}")

# File monitoring
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback('modified', event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.callback('created', event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.callback('deleted', event.src_path)

def monitor_directory(directory: str, callback):
    """Monitor directory for file changes"""

    event_handler = FileChangeHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

# Advanced glob patterns
def find_files_with_patterns(directory: str, patterns: List[str]):
    """Find files matching multiple patterns"""

    all_files = []
    for pattern in patterns:
        files = glob.glob(os.path.join(directory, '**', pattern), recursive=True)
        all_files.extend(files)

    return list(set(all_files))  # Remove duplicates

# File compression and decompression
def compress_file(input_file: str, output_file: str, compression: str = 'gzip'):
    """Compress a file using different algorithms"""

    compressors = {
        'gzip': gzip.open,
        'bz2': bz2.open,
        'lzma': lzma.open
    }

    with open(input_file, 'rb') as f_in:
        with compressors[compression](output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def decompress_file(input_file: str, output_file: str):
    """Decompress a file (auto-detect format)"""

    if input_file.endswith('.gz'):
        opener = gzip.open
    elif input_file.endswith('.bz2'):
        opener = bz2.open
    elif input_file.endswith(('.xz', '.lzma')):
        opener = lzma.open
    else:
        raise ValueError("Unsupported compression format")

    with opener(input_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
```

### Process Management

```python
import subprocess
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import queue
import signal
import psutil

# Process execution with advanced options
def run_command(command: List[str], timeout: int = 30, cwd: str = None):
    """Run command with timeout and error handling"""

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            check=True
        )
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timed out',
            'stdout': '',
            'stderr': ''
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'error': f'Command failed with return code {e.returncode}',
            'stdout': e.stdout,
            'stderr': e.stderr,
            'returncode': e.returncode
        }

# Multiprocessing
def cpu_intensive_task(data_chunk):
    """CPU-intensive task for multiprocessing"""
    result = sum(x * x for x in data_chunk)
    return result

def parallel_processing(data: List[int], num_processes: int = None):
    """Process data in parallel using multiprocessing"""

    if num_processes is None:
        num_processes = multiprocessing.cpu_count()

    # Split data into chunks
    chunk_size = len(data) // num_processes
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        results = list(executor.map(cpu_intensive_task, chunks))

    return sum(results)

# Threading with queues
def producer(queue: queue.Queue, items: List[Any]):
    """Producer function for threading"""

    for item in items:
        queue.put(item)
        time.sleep(0.1)  # Simulate work

    queue.put(None)  # Signal end of items

def consumer(queue: queue.Queue, results: List[Any]):
    """Consumer function for threading"""

    while True:
        item = queue.get()
        if item is None:
            break

        # Process item
        result = item * item
        results.append(result)
        queue.task_done()

def threaded_processing(items: List[int], num_threads: int = 4):
    """Process items using multiple threads"""

    work_queue = queue.Queue()
    results = []
    results_lock = threading.Lock()

    # Start producer thread
    producer_thread = threading.Thread(
        target=producer,
        args=(work_queue, items)
    )
    producer_thread.start()

    # Start consumer threads
    consumer_threads = []
    for _ in range(num_threads):
        thread = threading.Thread(
            target=consumer,
            args=(work_queue, results)
        )
        thread.start()
        consumer_threads.append(thread)

    # Wait for producer to finish
    producer_thread.join()

    # Wait for all consumers to finish
    for thread in consumer_threads:
        thread.join()

    return results

# Process monitoring and management
class ProcessManager:
    def __init__(self):
        self.processes = {}

    def start_process(self, name: str, command: List[str], cwd: str = None):
        """Start a background process"""

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )

        self.processes[name] = {
            'process': process,
            'command': command,
            'start_time': time.time()
        }

        return process.pid

    def stop_process(self, name: str):
        """Stop a background process"""

        if name in self.processes:
            process_info = self.processes[name]
            process = process_info['process']

            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            del self.processes[name]
            return True

        return False

    def get_process_status(self, name: str):
        """Get status of a managed process"""

        if name not in self.processes:
            return None

        process_info = self.processes[name]
        process = process_info['process']

        if process.poll() is None:
            status = 'running'
        else:
            status = 'stopped'

        return {
            'name': name,
            'status': status,
            'pid': process.pid,
            'command': process_info['command'],
            'runtime': time.time() - process_info['start_time']
        }

    def list_processes(self):
        """List all managed processes"""

        return [self.get_process_status(name) for name in self.processes]

# System monitoring
def get_system_info():
    """Get comprehensive system information"""

    return {
        'cpu': {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'count_logical': psutil.cpu_count(logical=True)
        },
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        },
        'network': {
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv
        },
        'processes': len(psutil.pids())
    }

def monitor_processes():
    """Monitor running processes"""

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_percent': proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)

# Signal handling
def signal_handler(signum, frame):
    """Handle system signals"""

    print(f"Received signal {signum}")
    # Perform cleanup
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

## Best Practices

### Code Quality and Testing

```python
import pytest
from hypothesis import given, strategies as st
import unittest
from unittest.mock import Mock, patch, MagicMock
import coverage
import pylint
import black
import isort

# Unit testing with pytest
class TestCalculator:
    def test_addition(self):
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0

    def test_subtraction(self):
        assert subtract(5, 3) == 2
        assert subtract(1, 1) == 0
        assert subtract(0, 5) == -5

    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 5),
        (-1, 1, 0),
        (0, 0, 0),
        (10, -5, 5)
    ])
    def test_addition_parametrized(self, a, b, expected):
        assert add(a, b) == expected

    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            divide(5, 0)

# Property-based testing with Hypothesis
@given(
    st.lists(st.integers(), min_size=1),
    st.integers(min_value=1, max_value=100)
)
def test_list_chunking_properties(data, chunk_size):
    chunks = chunk_list(data, chunk_size)
    # Properties that should always hold
    assert all(len(chunk) <= chunk_size for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) == len(data)
    assert len(chunks) <= len(data)

# Mocking and patching
def test_api_call_with_mock():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {'key': 'value'}
        mock_get.return_value = mock_response

        result = api_call('http://example.com')
        assert result == {'key': 'value'}
        mock_get.assert_called_once_with('http://example.com')

# Integration testing
class TestUserAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_create_user(self):
        response = self.client.post('/users', json={
            'username': 'testuser',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)

    def test_get_user(self):
        # Create user first
        response = self.client.post('/users', json={
            'username': 'testuser',
            'email': 'test@example.com'
        })
        user_id = response.get_json()['id']

        # Get user
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')

# Code quality tools
def run_code_quality_checks():
    """Run various code quality checks"""

    # Run pylint
    result = subprocess.run(['pylint', 'my_module.py'], capture_output=True, text=True)
    print("Pylint output:")
    print(result.stdout)

    # Run black for code formatting
    subprocess.run(['black', 'my_module.py'])

    # Run isort for import sorting
    subprocess.run(['isort', 'my_module.py'])

    # Run coverage
    subprocess.run(['coverage', 'run', '-m', 'pytest'])
    subprocess.run(['coverage', 'report'])

# Type checking with mypy
def typed_function(x: int, y: str) -> Dict[str, int]:
    """Function with type hints"""
    return {'x': x, 'y': len(y)}

# Performance testing
import cProfile
import pstats
from io import StringIO

def profile_function(func, *args, **kwargs):
    """Profile a function's performance"""

    pr = cProfile.Profile()
    pr.enable()

    result = func(*args, **kwargs)

    pr.disable()

    s = StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()

    print(s.getvalue())
    return result

# Benchmarking
import timeit

def benchmark_function(func, *args, iterations=1000, **kwargs):
    """Benchmark a function's execution time"""

    def wrapper():
        return func(*args, **kwargs)

    times = timeit.repeat(wrapper, number=1, repeat=iterations)
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"Average time: {avg_time:.6f} seconds")
    print(f"Min time: {min_time:.6f} seconds")
    print(f"Max time: {max_time:.6f} seconds")

    return avg_time, min_time, max_time
```

### Performance Optimization

```python
import cython
import numba
from functools import lru_cache
import multiprocessing
import asyncio

# Cython for performance-critical code
# Save this as .pyx file and compile
"""
cdef int fibonacci_cython(int n):
    if n < 2:
        return n
    return fibonacci_cython(n-1) + fibonacci_cython(n-2)

def fibonacci_list_cython(int n):
    cdef int i
    cdef list result = []
    for i in range(n):
        result.append(fibonacci_cython(i))
    return result
"""

# Numba for JIT compilation
@numba.jit(nopython=True)
def fibonacci_numba(n):
    if n < 2:
        return n
    return fibonacci_numba(n-1) + fibonacci_numba(n-2)

@numba.jit(nopython=True, parallel=True)
def matrix_multiply_numba(A, B):
    m, n = A.shape
    n, p = B.shape
    C = np.zeros((m, p))

    for i in numba.prange(m):
        for j in range(p):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]

    return C

# Memory optimization
def process_large_file_efficiently(file_path):
    """Process large file without loading it entirely into memory"""

    with open(file_path, 'r') as file:
        for line in file:
            # Process line by line
            process_line(line.strip())

def chunked_file_processing(file_path, chunk_size=8192):
    """Process file in chunks"""

    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            process_chunk(chunk)

# Async programming
async def async_api_call(url):
    """Asynchronous API call"""

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_multiple_requests(urls):
    """Process multiple requests concurrently"""

    tasks = [async_api_call(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Memory profiling
import tracemalloc

def profile_memory_usage(func, *args, **kwargs):
    """Profile memory usage of a function"""

    tracemalloc.start()

    result = func(*args, **kwargs)

    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

    tracemalloc.stop()
    return result

# CPU profiling
import cProfile
import pstats

def profile_cpu_usage(func, *args, **kwargs):
    """Profile CPU usage of a function"""

    profiler = cProfile.Profile()
    profiler.enable()

    result = func(*args, **kwargs)

    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

    return result

# Database optimization
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

def create_optimized_engine(database_url):
    """Create optimized SQLAlchemy engine"""

    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        echo=False  # Disable SQL logging in production
    )

# Connection pooling for HTTP requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_resilient_session():
    """Create HTTP session with retry logic and connection pooling"""

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

# Caching strategies
from cachetools import TTLCache, LRUCache
import redis

# In-memory caching
ttl_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes TTL

@lru_cache(maxsize=128)
def expensive_computation(x, y):
    # Simulate expensive computation
    time.sleep(1)
    return x + y

# Redis caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key, ttl=3600):
    """Get data from Redis cache"""

    data = redis_client.get(key)
    if data:
        return json.loads(data)

    # Compute data
    data = compute_expensive_data()

    # Cache result
    redis_client.setex(key, ttl, json.dumps(data))

    return data

# Lazy loading
class LazyLoader:
    def __init__(self, loader_func):
        self.loader_func = loader_func
        self._data = None
        self._loaded = False

    @property
    def data(self):
        if not self._loaded:
            self._data = self.loader_func()
            self._loaded = True
        return self._data

# Generator-based lazy evaluation
def lazy_range(n):
    """Memory-efficient range generator"""

    i = 0
    while i < n:
        yield i
        i += 1

# Context managers for resource management
class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def __enter__(self):
        self.connection = create_connection(self.connection_string)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

# Using context manager for resource safety
with DatabaseConnection("postgresql://localhost/mydb") as conn:
    results = conn.execute("SELECT * FROM users")
    # Connection automatically closed
```

Python's versatility, extensive ecosystem, and focus on readability make it an excellent choice for a wide range of applications. Mastering its advanced features, best practices, and ecosystem enables developers to build robust, scalable, and maintainable software systems across domains.
