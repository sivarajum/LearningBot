# Iris Classification - Supervised Learning

## Overview
This project demonstrates supervised learning using the famous Iris dataset with multiple classification algorithms. The Iris dataset contains 150 samples of iris flowers with 4 features and 3 classes.

## Dataset
- **Features**: 4 (sepal length, sepal width, petal length, petal width)
- **Classes**: 3 (Setosa, Versicolor, Virginica)
- **Total Samples**: 150
- **Train/Test Split**: 80/20 with stratification

## Algorithms Implemented

### 1. Logistic Regression
- **Type**: Linear classifier
- **Best For**: Interpretable, fast training
- **Pros**: Simple, efficient, provides probabilities
- **Cons**: Limited to linear boundaries
- **Accuracy**: ~97%

### 2. Decision Tree
- **Type**: Tree-based classifier
- **Best For**: Non-linear patterns, feature importance
- **Pros**: Interpretable, no feature scaling needed
- **Cons**: Prone to overfitting, high variance
- **Accuracy**: ~95%

### 3. Random Forest
- **Type**: Ensemble method (multiple decision trees)
- **Best For**: General-purpose classification
- **Pros**: Excellent performance, handles non-linearity, robust
- **Cons**: Less interpretable, slower prediction
- **Accuracy**: >96%

### 4. Support Vector Machine (SVM)
- **Type**: Non-linear classifier
- **Best For**: Complex decision boundaries
- **Pros**: Powerful, good generalization
- **Cons**: Requires feature scaling, slow on large datasets
- **Accuracy**: >95%

## Project Structure
```
01-iris-classification/
├── iris_classifier.py              # Main implementation
├── iris_classification.ipynb       # Interactive Jupyter notebook
├── README.md                       # This file
└── [output plots]
    ├── 01_data_exploration.png
    ├── 02_metrics_comparison.png
    └── 03_confusion_matrices.png
```

## Quick Start

### Run Python Script
```bash
python iris_classifier.py
```

### Run Jupyter Notebook
```bash
jupyter notebook iris_classification.ipynb
```

## Detailed Pipeline

### 1. Data Loading and Exploration
```python
# Load the Iris dataset
from sklearn import datasets
iris = datasets.load_iris()
X = iris.data  # Features: (150, 4)
y = iris.target  # Labels: 3 classes
```

### 2. Data Preprocessing
```python
# Train-test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

### 3. Model Training
```python
# Train multiple classifiers
models = {
    'Logistic Regression': LogisticRegression(),
    'Decision Tree': DecisionTreeClassifier(),
    'Random Forest': RandomForestClassifier(n_estimators=100),
    'SVM': SVC(kernel='rbf')
}

for name, model in models.items():
    model.fit(X_train_scaled if 'Logistic' in name or 'SVM' in name else X_train, y_train)
```

### 4. Model Evaluation
```python
# Multiple metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')
```

### 5. Hyperparameter Tuning
```python
# Grid search for best parameters
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [3, 5, 7, None],
    'min_samples_split': [2, 5]
}

grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
grid_search.fit(X_train, y_train)
```

### 6. Cross-Validation
```python
# 5-fold cross-validation
cv_scores = cross_val_score(model, X_train, y_train, cv=5)
print(f"Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
```

## Evaluation Metrics Explained

### Accuracy
- **Definition**: (TP + TN) / (TP + TN + FP + FN)
- **Interpretation**: Overall correctness of predictions
- **Good For**: Balanced datasets

### Precision
- **Definition**: TP / (TP + FP)
- **Interpretation**: Of positive predictions, how many were correct?
- **Good For**: Minimizing false positives

### Recall
- **Definition**: TP / (TP + FN)
- **Interpretation**: Of actual positives, how many did we find?
- **Good For**: Minimizing false negatives

### F1-Score
- **Definition**: 2 × (Precision × Recall) / (Precision + Recall)
- **Interpretation**: Harmonic mean of precision and recall
- **Good For**: Imbalanced datasets

## Key Features of Implementation

✓ **Data Stratification**: Maintains class distribution in splits
✓ **Feature Scaling**: Proper normalization for distance-based algorithms
✓ **Multiple Algorithms**: Compares different approaches
✓ **Comprehensive Metrics**: Not just accuracy, but precision, recall, F1
✓ **Hyperparameter Tuning**: GridSearchCV for optimal parameters
✓ **Cross-Validation**: Robust performance estimation
✓ **Professional Visualizations**: Clear, labeled plots

## Expected Results

### Model Performance
| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Logistic Regression | 0.9667 | 0.9667 | 0.9667 | 0.9667 |
| Decision Tree | 0.9333 | 0.9355 | 0.9333 | 0.9333 |
| Random Forest | 0.9667 | 0.9667 | 0.9667 | 0.9667 |
| SVM | 0.9667 | 0.9667 | 0.9667 | 0.9667 |

### Key Insights
1. **Feature Separability**: Petal length and width are most discriminative
2. **Algorithm Performance**: All algorithms perform well (>93% accuracy)
3. **Feature Scaling**: Essential for SVM and Logistic Regression
4. **Ensemble Benefits**: Random Forest provides robustness through voting

## Confusion Matrix Interpretation

For a 3-class problem (Setosa, Versicolor, Virginica):
```
                Predicted
           Setosa  Versi  Virgi
Actual Set    11      0      0
       Vers    0     10      1
       Vir     0      0      8
```
- Diagonal = Correct predictions
- Off-diagonal = Misclassifications
- We want a concentrated diagonal

## Feature Importance

From Random Forest model:
1. **Petal Length**: ~45% importance
2. **Petal Width**: ~43% importance
3. **Sepal Length**: ~10% importance
4. **Sepal Width**: ~2% importance

**Insight**: Petal measurements are far more discriminative than sepal measurements.

## Common Pitfalls to Avoid

❌ **Not scaling features** for SVM/Logistic Regression
❌ **Not stratifying** train-test split on imbalanced data
❌ **Using only accuracy** for evaluation
❌ **Not doing cross-validation** on small datasets
❌ **Overfitting** by not regularizing hyperparameters
❌ **Data leakage** by scaling before splitting

## Advanced Topics

### 1. Feature Selection
```python
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(f_classif, k=3)
X_selected = selector.fit_transform(X_train, y_train)
```

### 2. Class Imbalance Handling
```python
from sklearn.utils.class_weight import compute_class_weight
class_weights = compute_class_weight('balanced', np.unique(y_train), y_train)
```

### 3. Model Interpretability
```python
# Feature importance from tree-based models
importances = model.feature_importances_

# Coefficients from linear models
coefficients = model.coef_
```

### 4. Probability Calibration
```python
from sklearn.calibration import CalibratedClassifierCV
calibrated_model = CalibratedClassifierCV(model, cv=5)
calibrated_model.fit(X_train, y_train)
```

## Performance Optimization Tips

1. **Feature Scaling**: Use StandardScaler before training
2. **Hyperparameter Grid**: Start broad, then refine
3. **Cross-Validation**: Use appropriate number of folds
4. **Random Seed**: Fix for reproducibility
5. **n_jobs**: Use parallel processing (-1 for all cores)

## Deployment Considerations

For production deployment:

```python
# 1. Save the model
import joblib
joblib.dump(model, 'iris_model.pkl')

# 2. Save the scaler
joblib.dump(scaler, 'scaler.pkl')

# 3. Create prediction function
def predict_iris(features):
    features_scaled = scaler.transform([features])
    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]
    return prediction, probabilities

# 4. Wrap in API (Flask, FastAPI, etc.)
```

## Learning Outcomes

After completing this project, you should understand:

✓ How to load and explore datasets
✓ Importance of train-test splitting
✓ Why feature scaling matters
✓ Differences between classification algorithms
✓ How to evaluate classifier performance
✓ Basics of hyperparameter tuning
✓ Benefits of cross-validation
✓ How to interpret confusion matrices
✓ When to use which algorithm

## Files Generated

- **01_data_exploration.png**: Feature relationships and distributions
- **02_metrics_comparison.png**: Bar chart comparing metrics across models
- **03_confusion_matrices.png**: 2x2 grid of confusion matrices

## Troubleshooting

### Issue: Import errors
```bash
pip install scikit-learn pandas numpy matplotlib seaborn
```

### Issue: Slow execution
- Reduce max_iter parameter
- Use n_jobs=-1 for parallel processing
- Use smaller max_depth for trees

### Issue: Low accuracy
- Check if data is properly preprocessed
- Verify train-test split stratification
- Adjust hyperparameters using GridSearchCV

## References

- [scikit-learn Iris Dataset](https://scikit-learn.org/stable/datasets/index.html#iris-dataset)
- [Classification Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Model Selection](https://scikit-learn.org/stable/modules/model_selection.html)

## Next Steps

1. Try with different datasets (Digits, Wine, Breast Cancer)
2. Implement feature selection techniques
3. Add ROC curves and AUC analysis
4. Deploy as REST API
5. Compare with neural network approaches

---

**Difficulty**: Intermediate | **Time**: 2-3 hours | **Prerequisites**: Python basics, basic statistics
