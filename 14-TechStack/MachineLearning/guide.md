# Machine Learning Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Basic Model**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
```

### 2. **Preprocessing**
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### 3. **Evaluation**
```python
from sklearn.metrics import accuracy_score, classification_report

accuracy = accuracy_score(y_test, predictions)
print(classification_report(y_test, predictions))
```

## Level 2 – Production Patterns

### Pipeline
```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier())
])

pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

### Hyperparameter Tuning
```python
from sklearn.model_selection import GridSearchCV

param_grid = {'n_estimators': [100, 200], 'max_depth': [10, 20]}
grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
grid_search.fit(X_train, y_train)
```

## Level 3 – Architect Playbook

### MLOps
```python
import mlflow

with mlflow.start_run():
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.sklearn.log_model(model, "model")
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Train | `model.fit()` | Train model |
| Predict | `model.predict()` | Make predictions |
| Save | `joblib.dump()` | Save model |

## Checklist Before Production

- [ ] Implement proper preprocessing
- [ ] Perform hyperparameter tuning
- [ ] Set up model versioning
- [ ] Implement monitoring
- [ ] Set up deployment pipeline
- [ ] Test thoroughly
- [ ] Document model
- [ ] Monitor performance
