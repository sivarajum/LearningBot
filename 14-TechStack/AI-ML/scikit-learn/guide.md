# Scikit-learn Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load data
iris = datasets.load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
```

### 2. **Preprocessing**
```python
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
```

### 3. **Pipeline**
```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier())
])

pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

## Level 2 – Production Patterns

### Cross-Validation
```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(
    model, X, y, cv=5, scoring='accuracy'
)
print(f"Mean accuracy: {scores.mean()}")
```

### Hyperparameter Tuning
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [10, 20]
}

grid_search = GridSearchCV(
    RandomForestClassifier(),
    param_grid,
    cv=5
)
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

### Feature Selection
```python
from sklearn.feature_selection import SelectKBest, f_classif

selector = SelectKBest(f_classif, k=2)
X_selected = selector.fit_transform(X, y)
```

## Level 3 – Architect Playbook

### Custom Estimator
```python
from sklearn.base import BaseEstimator, ClassifierMixin

class CustomClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, param1=1):
        self.param1 = param1
    
    def fit(self, X, y):
        # Training logic
        return self
    
    def predict(self, X):
        # Prediction logic
        return predictions
```

### Model Persistence
```python
import joblib

# Save
joblib.dump(model, 'model.pkl')

# Load
model = joblib.load('model.pkl')
```

### Production Deployment
```python
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)
model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    prediction = model.predict([data['features']])
    return jsonify({'prediction': prediction.tolist()})
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Train | `model.fit(X, y)` | Train model |
| Predict | `model.predict(X)` | Make predictions |
| Score | `model.score(X, y)` | Calculate score |
| Save | `joblib.dump(model, 'file.pkl')` | Save model |
| Load | `joblib.load('file.pkl')` | Load model |

## Checklist Before Production

- [ ] Implement proper preprocessing
- [ ] Use pipelines for consistency
- [ ] Perform hyperparameter tuning
- [ ] Implement proper validation
- [ ] Set up model versioning
- [ ] Implement proper error handling
- [ ] Set up monitoring
- [ ] Test model performance
