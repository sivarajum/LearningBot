# Machine Learning: Intelligence Through Data

## What is Machine Learning?

Machine Learning (ML) is a subset of artificial intelligence that enables systems to automatically learn and improve from experience without being explicitly programmed. ML algorithms build mathematical models based on training data to make predictions or decisions.

## Core Concepts

### Types of Machine Learning

```python
# Supervised Learning - Learning with labeled data
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Example: Predicting house prices
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

```python
# Unsupervised Learning - Finding patterns in unlabeled data
from sklearn.cluster import KMeans

# Example: Customer segmentation
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(customer_data)
```

```python
# Reinforcement Learning - Learning through interaction
import gym
import numpy as np

# Example: Training an agent
env = gym.make('CartPole-v1')
state = env.reset()
action = agent.choose_action(state)
next_state, reward, done, info = env.step(action)
agent.learn(state, action, reward, next_state)
```

### Key Components

1. **Data**: The fuel for ML models
2. **Features**: Input variables used for prediction
3. **Models**: Mathematical representations of patterns
4. **Training**: Process of learning from data
5. **Evaluation**: Measuring model performance
6. **Deployment**: Making models available for prediction

## Data Preparation

### Data Collection and Cleaning

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Load and explore data
df = pd.read_csv('data.csv')
print(df.head())
print(df.info())
print(df.describe())

# Handle missing values
df.dropna(inplace=True)  # Remove rows with NaN
df.fillna(df.mean(), inplace=True)  # Fill with mean

# Handle categorical variables
le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['category'])

# Feature scaling
scaler = StandardScaler()
numerical_features = ['feature1', 'feature2', 'feature3']
df[numerical_features] = scaler.fit_transform(df[numerical_features])
```

### Feature Engineering

```python
# Create new features
df['total_area'] = df['length'] * df['width']
df['price_per_sqft'] = df['price'] / df['area']
df['age'] = 2024 - df['year_built']

# Polynomial features
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)

# Feature selection
from sklearn.feature_selection import SelectKBest, f_regression
selector = SelectKBest(score_func=f_regression, k=10)
X_selected = selector.fit_transform(X, y)

# Dimensionality reduction
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)
```

## Supervised Learning Algorithms

### Linear Models

#### Linear Regression
```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score

# Simple Linear Regression
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)

# Regularized Regression
ridge = Ridge(alpha=0.1)
lasso = Lasso(alpha=0.1)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"MSE: {mse:.2f}, R²: {r2:.2f}")
```

#### Logistic Regression
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Binary Classification
log_reg = LogisticRegression(random_state=42)
log_reg.fit(X_train, y_train)
y_pred = log_reg.predict(X_test)

# Multi-class Classification
log_reg_multi = LogisticRegression(multi_class='ovr', random_state=42)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
print(classification_report(y_test, y_pred))
```

### Tree-Based Models

#### Decision Trees
```python
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

# Classification
dt_classifier = DecisionTreeClassifier(
    max_depth=5,
    min_samples_split=10,
    random_state=42
)
dt_classifier.fit(X_train, y_train)

# Regression
dt_regressor = DecisionTreeRegressor(
    max_depth=5,
    min_samples_leaf=5,
    random_state=42
)

# Visualize tree
plt.figure(figsize=(20,10))
plot_tree(dt_classifier, feature_names=feature_names, class_names=class_names, filled=True)
plt.show()
```

#### Random Forest
```python
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# Classification
rf_classifier = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
rf_classifier.fit(X_train, y_train)

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': rf_classifier.feature_importances_
}).sort_values('importance', ascending=False)

# Regression
rf_regressor = RandomForestRegressor(
    n_estimators=200,
    max_features='sqrt',
    random_state=42
)
```

#### Gradient Boosting
```python
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import xgboost as xgb
import lightgbm as lgb

# Scikit-learn Gradient Boosting
gb_classifier = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42
)

# XGBoost
xgb_classifier = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    objective='binary:logistic'
)

# LightGBM
lgb_classifier = lgb.LGBMClassifier(
    n_estimators=100,
    learning_rate=0.1,
    num_leaves=31,
    objective='binary'
)
```

### Support Vector Machines

```python
from sklearn.svm import SVC, SVR
from sklearn.model_selection import GridSearchCV

# Support Vector Classifier
svc = SVC(
    kernel='rbf',
    C=1.0,
    gamma='scale',
    random_state=42
)
svc.fit(X_train, y_train)

# Hyperparameter tuning
param_grid = {
    'C': [0.1, 1, 10, 100],
    'gamma': [1, 0.1, 0.01, 0.001],
    'kernel': ['rbf', 'linear', 'poly']
}

grid_search = GridSearchCV(SVC(), param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.3f}")
```

### Neural Networks

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Simple Neural Network
model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dropout(0.2),
    layers.Dense(32, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(1, activation='sigmoid')  # For binary classification
])

# Compile model
model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Train model
history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    callbacks=[keras.callbacks.EarlyStopping(patience=5)]
)

# Evaluate
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test accuracy: {test_accuracy:.4f}")
```

## Unsupervised Learning Algorithms

### Clustering Algorithms

#### K-Means Clustering
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Determine optimal number of clusters
inertias = []
silhouette_scores = []
K = range(2, 11)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)
    if k > 1:
        silhouette_scores.append(silhouette_score(X, kmeans.labels_))

# Plot elbow curve
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(K, inertias, 'bx-')
plt.xlabel('k')
plt.ylabel('Inertia')
plt.title('Elbow Method')

plt.subplot(1, 2, 2)
plt.plot(K[1:], silhouette_scores, 'rx-')
plt.xlabel('k')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Analysis')
plt.show()

# Final clustering
optimal_k = 4
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
clusters = kmeans.fit_predict(X)
```

#### Hierarchical Clustering
```python
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering

# Create linkage matrix
linkage_matrix = linkage(X, method='ward')

# Plot dendrogram
plt.figure(figsize=(12, 8))
dendrogram(linkage_matrix)
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Sample Index')
plt.ylabel('Distance')
plt.show()

# Agglomerative clustering
agg_clustering = AgglomerativeClustering(n_clusters=4, linkage='ward')
clusters = agg_clustering.fit_predict(X)
```

#### DBSCAN
```python
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Scale data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# DBSCAN clustering
dbscan = DBSCAN(
    eps=0.5,  # Maximum distance between points
    min_samples=5,  # Minimum samples in neighborhood
    metric='euclidean'
)

clusters = dbscan.fit_predict(X_scaled)

# Analyze results
n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
n_noise = list(clusters).count(-1)

print(f"Number of clusters: {n_clusters}")
print(f"Number of noise points: {n_noise}")
```

### Dimensionality Reduction

#### Principal Component Analysis (PCA)
```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# PCA
pca = PCA()
X_pca = pca.fit_transform(X_scaled)

# Explained variance
explained_variance_ratio = pca.explained_variance_ratio_
cumulative_variance = explained_variance_ratio.cumsum()

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.bar(range(1, len(explained_variance_ratio) + 1), explained_variance_ratio)
plt.xlabel('Principal Component')
plt.ylabel('Explained Variance Ratio')
plt.title('Individual Explained Variance')

plt.subplot(1, 2, 2)
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, 'ro-')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance')
plt.title('Cumulative Explained Variance')
plt.show()

# Reduce to 2D for visualization
pca_2d = PCA(n_components=2)
X_pca_2d = pca_2d.fit_transform(X_scaled)
```

#### t-SNE
```python
from sklearn.manifold import TSNE

# t-SNE for visualization
tsne = TSNE(
    n_components=2,
    perplexity=30,
    learning_rate=200,
    random_state=42
)

X_tsne = tsne.fit_transform(X_scaled)

# Plot t-SNE
plt.figure(figsize=(10, 8))
scatter = plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap='viridis', alpha=0.6)
plt.colorbar(scatter)
plt.title('t-SNE Visualization')
plt.xlabel('t-SNE Component 1')
plt.ylabel('t-SNE Component 2')
plt.show()
```

## Model Evaluation and Validation

### Cross-Validation
```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.model_selection import cross_validate

# K-fold cross-validation
scores = cross_val_score(
    estimator=model,
    X=X,
    y=y,
    cv=5,
    scoring='accuracy'
)

print(f"Cross-validation scores: {scores}")
print(f"Mean accuracy: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")

# Multiple metrics
scoring = ['accuracy', 'precision', 'recall', 'f1']
scores = cross_validate(
    estimator=model,
    X=X,
    y=y,
    cv=5,
    scoring=scoring
)

for metric in scoring:
    print(f"{metric}: {scores[f'test_{metric}'].mean():.3f}")
```

### Hyperparameter Tuning
```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from scipy.stats import randint, uniform

# Grid Search
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)
print(f"Best parameters: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.3f}")

# Random Search
param_dist = {
    'n_estimators': randint(50, 200),
    'max_depth': [None] + list(range(10, 31)),
    'min_samples_split': randint(2, 11),
    'min_samples_leaf': randint(1, 5)
}

random_search = RandomizedSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_distributions=param_dist,
    n_iter=100,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    random_state=42
)

random_search.fit(X_train, y_train)
```

### Model Evaluation Metrics

#### Classification Metrics
```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import seaborn as sns

# Predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# Basic metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_proba)

print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1-Score: {f1:.3f}")
print(f"AUC: {auc:.3f}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

# Classification Report
print(classification_report(y_test, y_pred))
```

#### Regression Metrics
```python
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error,
    r2_score, mean_absolute_percentage_error
)

# Predictions
y_pred = model.predict(X_test)

# Regression metrics
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
mape = mean_absolute_percentage_error(y_test, y_pred)

print(f"MAE: {mae:.3f}")
print(f"MSE: {mse:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"R²: {r2:.3f}")
print(f"MAPE: {mape:.3f}")

# Residual plot
residuals = y_test - y_pred
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.scatter(y_pred, residuals, alpha=0.5)
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Residual Plot')
plt.axhline(y=0, color='r', linestyle='--')

plt.subplot(1, 3, 2)
plt.hist(residuals, bins=30, alpha=0.7)
plt.xlabel('Residuals')
plt.ylabel('Frequency')
plt.title('Residual Distribution')

plt.subplot(1, 3, 3)
plt.scatter(y_test, y_pred, alpha=0.5)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Actual vs Predicted')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')

plt.tight_layout()
plt.show()
```

## Deep Learning

### Convolutional Neural Networks (CNN)
```python
# CNN for image classification
cnn_model = keras.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

cnn_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Data augmentation
datagen = keras.preprocessing.image.ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)

# Train with augmentation
history = cnn_model.fit(
    datagen.flow(X_train, y_train, batch_size=32),
    epochs=20,
    validation_data=(X_test, y_test)
)
```

### Recurrent Neural Networks (RNN)
```python
# LSTM for sequence prediction
rnn_model = keras.Sequential([
    layers.Embedding(input_dim=vocab_size, output_dim=128),
    layers.LSTM(128, return_sequences=True),
    layers.LSTM(64),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation='softmax')
])

rnn_model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train with early stopping
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=3,
    restore_best_weights=True
)

history = rnn_model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stopping]
)
```

### Transfer Learning
```python
# Using pre-trained models
from tensorflow.keras.applications import VGG16, ResNet50
from tensorflow.keras.applications.vgg16 import preprocess_input

# Load pre-trained model
base_model = VGG16(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze base model layers
for layer in base_model.layers:
    layer.trainable = False

# Add custom layers
model = keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation='softmax')
])

# Fine-tune last few layers
for layer in base_model.layers[-4:]:
    layer.trainable = True

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)
```

## Model Deployment and Production

### Model Serialization
```python
import joblib
import pickle

# Save scikit-learn model
joblib.dump(model, 'model.joblib')

# Save with pickle
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Load model
loaded_model = joblib.load('model.joblib')
predictions = loaded_model.predict(X_test)
```

### REST API with Flask
```python
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)
model = joblib.load('model.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = np.array(data['features']).reshape(1, -1)
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    return jsonify({
        'prediction': int(prediction),
        'probability': float(max(probability))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Model Monitoring
```python
# Monitor model performance
def monitor_model_performance(model, X_test, y_test, threshold=0.8):
    """
    Monitor model performance and alert if below threshold
    """
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    if accuracy < threshold:
        print(f"ALERT: Model accuracy {accuracy:.3f} below threshold {threshold}")
        # Send alert, retrain model, etc.

    return accuracy

# Data drift detection
from scipy.stats import ks_2samp

def detect_data_drift(reference_data, current_data, threshold=0.05):
    """
    Detect if current data distribution differs from reference
    """
    drift_detected = False

    for column in reference_data.columns:
        stat, p_value = ks_2samp(reference_data[column], current_data[column])
        if p_value < threshold:
            print(f"Data drift detected in column: {column}")
            drift_detected = True

    return drift_detected
```

## MLOps and Best Practices

### Experiment Tracking
```python
import mlflow
import mlflow.sklearn

# Start MLflow run
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)

    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)

    # Log metrics
    accuracy = accuracy_score(y_test, model.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)

    # Log model
    mlflow.sklearn.log_model(model, "model")
```

### Model Versioning
```python
# Model versioning with DVC
import dvc.api

# Track data versions
# dvc add data.csv
# dvc commit

# Version models
def save_model_version(model, version, metrics):
    """
    Save model with version and metadata
    """
    model_info = {
        'version': version,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat(),
        'model_type': type(model).__name__
    }

    # Save model
    joblib.dump(model, f'models/model_v{version}.joblib')

    # Save metadata
    with open(f'models/model_v{version}_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)

# Load specific model version
def load_model_version(version):
    model = joblib.load(f'models/model_v{version}.joblib')
    with open(f'models/model_v{version}_info.json', 'r') as f:
        info = json.load(f)
    return model, info
```

## Advanced Topics

### Ensemble Methods
```python
from sklearn.ensemble import VotingClassifier, BaggingClassifier, AdaBoostClassifier

# Voting Classifier
voting_clf = VotingClassifier(
    estimators=[
        ('rf', RandomForestClassifier(random_state=42)),
        ('svc', SVC(probability=True, random_state=42)),
        ('lr', LogisticRegression(random_state=42))
    ],
    voting='soft'
)

# Bagging
bagging_clf = BaggingClassifier(
    base_estimator=DecisionTreeClassifier(),
    n_estimators=50,
    random_state=42
)

# AdaBoost
ada_clf = AdaBoostClassifier(
    base_estimator=DecisionTreeClassifier(max_depth=1),
    n_estimators=50,
    random_state=42
)
```

### AutoML
```python
# Using Auto-sklearn
import autosklearn.classification

automl = autosklearn.classification.AutoSklearnClassifier(
    time_left_for_this_task=3600,  # 1 hour
    per_run_time_limit=300,       # 5 minutes per model
    memory_limit=8192             # 8GB memory limit
)

automl.fit(X_train, y_train)
print(automl.show_models())

# Make predictions
y_pred = automl.predict(X_test)
```

## Summary

Machine Learning represents the convergence of statistics, computer science, and domain expertise to extract insights from data:

- **Supervised Learning**: Making predictions from labeled data using classification and regression
- **Unsupervised Learning**: Discovering patterns in unlabeled data through clustering and dimensionality reduction
- **Deep Learning**: Neural networks capable of learning complex hierarchical representations
- **Model Evaluation**: Rigorous assessment using cross-validation, metrics, and statistical tests
- **Production Deployment**: Serving models via APIs with monitoring and continuous improvement

The ML workflow encompasses data preparation, model development, evaluation, deployment, and ongoing maintenance, requiring both technical skills and domain knowledge to deliver impactful solutions.
