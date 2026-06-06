# Scikit-learn Interview Questions & Answers

## Core Concepts and Fundamentals

### Q1: What is Scikit-learn and why is it important?

**Answer:**
Scikit-learn is the most popular open-source machine learning library for Python, providing simple and efficient tools for data mining and data analysis. It's built on NumPy, SciPy, and matplotlib.

**Key Importance:**
- **Unified API**: Consistent interface across all algorithms
- **Production-ready**: Well-tested, robust implementations
- **Comprehensive**: Covers classification, regression, clustering, dimensionality reduction
- **Integration**: Works seamlessly with scientific Python ecosystem
- **Performance**: Optimized implementations with good defaults

**Core Philosophy:**
- Estimator API with fit/predict pattern
- Emphasis on code reusability and composition
- Focus on practical machine learning rather than research

### Q2: Explain the Estimator API in Scikit-learn.

**Answer:**
The Estimator API is Scikit-learn's core design pattern that provides a consistent interface for all machine learning algorithms.

**Key Components:**
```python
# All estimators implement these methods
estimator.fit(X, y)           # Train the model
estimator.predict(X)          # Make predictions
estimator.score(X, y)         # Return performance score

# Hyperparameters are public attributes
estimator.hyperparameter_name

# Internal state after fitting
estimator.coef_                # Coefficients (linear models)
estimator.feature_importances_ # Feature importance (trees)
estimator.cluster_centers_     # Cluster centers (clustering)
```

**Benefits:**
- **Consistency**: Same interface for all algorithms
- **Composition**: Easy to build complex pipelines
- **Inspection**: All parameters and state are accessible
- **Extensibility**: Easy to create custom estimators

### Q3: How does Scikit-learn handle different data types?

**Answer:**
Scikit-learn provides tools for preprocessing different data types through the `sklearn.preprocessing` module and `sklearn.compose.ColumnTransformer`.

**Numerical Data:**
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler
scaler = StandardScaler()  # Z-score normalization
X_scaled = scaler.fit_transform(X)
```

**Categorical Data:**
```python
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
encoder = OneHotEncoder()  # For nominal categories
X_encoded = encoder.fit_transform(X_categorical)
```

**Mixed Data:**
```python
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])
```

## Data Preprocessing

### Q4: How do you handle missing values in Scikit-learn?

**Answer:**
Scikit-learn provides `sklearn.impute` module with several strategies:

**Simple Imputation:**
```python
from sklearn.impute import SimpleImputer

# Mean imputation for numerical
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# Most frequent for categorical
imputer = SimpleImputer(strategy='most_frequent')
X_imputed = imputer.fit_transform(X)
```

**Advanced Imputation:**
```python
from sklearn.impute import KNNImputer, IterativeImputer

# KNN imputation
knn_imputer = KNNImputer(n_neighbors=5)
X_imputed = knn_imputer.fit_transform(X)

# Iterative imputation (experimental)
iterative_imputer = IterativeImputer(random_state=42)
X_imputed = iterative_imputer.fit_transform(X)
```

**Best Practices:**
- Use domain knowledge to choose appropriate strategy
- Consider missing value patterns (MCAR, MAR, MNAR)
- Validate imputation doesn't introduce bias
- Use cross-validation to assess imputation impact

### Q5: Explain feature scaling and when to use different scalers.

**Answer:**
Feature scaling transforms features to comparable ranges, crucial for many algorithms.

**StandardScaler (Z-score normalization):**
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()  # μ=0, σ=1
```
- **When to use**: Normally distributed data, algorithms assuming standardized features (SVM, PCA, linear models with regularization)
- **Pros**: Preserves relationships, handles outliers reasonably
- **Cons**: Sensitive to outliers

**MinMaxScaler ([0,1] scaling):**
```python
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()  # [0,1] range
```
- **When to use**: Bounded data needed, neural networks, image processing
- **Pros**: Preserves zero values, bounded output
- **Cons**: Very sensitive to outliers

**RobustScaler (Median & IQR):**
```python
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()  # Uses median and IQR
```
- **When to use**: Outlier-prone data
- **Pros**: Robust to outliers
- **Cons**: Doesn't force specific range

### Q6: How do you encode categorical variables?

**Answer:**
Different encoding strategies for different scenarios:

**Label Encoding (Ordinal):**
```python
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_encoded = le.fit_transform(['cat', 'dog', 'bird'])  # [0, 1, 2]
```
- **Use**: Ordinal categories (small < medium < large)
- **Problem**: Implies order where none exists

**One-Hot Encoding (Nominal):**
```python
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder()
X_encoded = ohe.fit_transform([['red'], ['blue'], ['green']])
# Creates binary columns for each category
```
- **Use**: Nominal categories (no order)
- **Problem**: High cardinality creates many features

**Ordinal Encoding:**
```python
from sklearn.preprocessing import OrdinalEncoder
oe = OrdinalEncoder(categories=[['small', 'medium', 'large']])
X_encoded = oe.fit_transform([['small'], ['large']])
```

## Supervised Learning Algorithms

### Q7: Explain the difference between fit, transform, and fit_transform.

**Answer:**
These methods serve different purposes in the Scikit-learn pipeline:

**fit(X, y=None):**
- Learns parameters from training data
- For transformers: learns scaling parameters, encoding mappings
- For estimators: learns model parameters
- Must be called before transform/predict

**transform(X):**
- Applies learned transformation to data
- Used by transformers (preprocessing steps)
- Returns transformed data

**fit_transform(X, y=None):**
- Convenience method combining fit and transform
- More efficient than calling fit then transform separately
- Only available for transformers

**Example:**
```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit and transform training data
X_test_scaled = scaler.transform(X_test)        # Only transform test data
```

### Q8: How do you choose between different algorithms?

**Answer:**
Algorithm selection depends on data characteristics and problem requirements:

**Data Size:**
- **Small dataset (<1000 samples)**: Simple models (Naive Bayes, Linear models)
- **Medium dataset**: Tree-based models, SVM
- **Large dataset**: Linear models, SGD-based algorithms

**Feature Types:**
- **Numerical features**: Any algorithm
- **Categorical features**: Tree-based models, Naive Bayes
- **Text features**: Linear models with TF-IDF, Neural networks

**Problem Characteristics:**
- **Linear relationship**: Linear Regression, Logistic Regression
- **Non-linear relationship**: Decision Trees, Random Forest, SVM with RBF kernel
- **High dimensionality**: Linear models, dimensionality reduction first
- **Class imbalance**: Tree-based models, ensemble methods

**Performance Requirements:**
- **Interpretability needed**: Linear models, Decision Trees
- **Accuracy most important**: Ensemble methods, Neural networks
- **Speed critical**: Linear models, Naive Bayes

### Q9: Explain regularization in linear models.

**Answer:**
Regularization prevents overfitting by adding penalty terms to the loss function.

**L2 Regularization (Ridge):**
```python
from sklearn.linear_model import Ridge
ridge = Ridge(alpha=1.0)  # λ controls regularization strength
```
- **Penalty**: λ * Σ(θ²)
- **Effect**: Shrinks coefficients toward zero
- **Use**: When all features are potentially useful

**L1 Regularization (Lasso):**
```python
from sklearn.linear_model import Lasso
lasso = Lasso(alpha=1.0)
```
- **Penalty**: λ * Σ|θ|
- **Effect**: Forces some coefficients to exactly zero (feature selection)
- **Use**: When feature selection is desired

**Elastic Net:**
```python
from sklearn.linear_model import ElasticNet
elastic = ElasticNet(alpha=1.0, l1_ratio=0.5)  # Mix of L1 and L2
```
- **Penalty**: λ * (ρ * Σ|θ| + (1-ρ) * Σ(θ²))
- **Use**: When you want both shrinkage and feature selection

### Q10: How do ensemble methods work?

**Answer:**
Ensemble methods combine multiple models to improve performance.

**Bagging (Bootstrap Aggregating):**
```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100)
```
- **How it works**: Trains multiple models on random subsets of data
- **Reduces variance**: Averaging reduces overfitting
- **Example**: Random Forest

**Boosting:**
```python
from sklearn.ensemble import GradientBoostingClassifier
gb = GradientBoostingClassifier(n_estimators=100)
```
- **How it works**: Trains models sequentially, each correcting previous errors
- **Reduces bias**: Focuses on hard-to-classify examples
- **Examples**: AdaBoost, Gradient Boosting, XGBoost

**Stacking:**
```python
from sklearn.ensemble import StackingClassifier
stacking = StackingClassifier(estimators=[...], final_estimator=LogisticRegression())
```
- **How it works**: Uses predictions from base models as features for meta-model
- **Combines strengths**: Different algorithms complement each other

## Model Evaluation and Validation

### Q11: Explain cross-validation and why it's important.

**Answer:**
Cross-validation assesses model performance on unseen data and helps prevent overfitting.

**K-Fold Cross-Validation:**
```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"CV Accuracy: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

**Why Important:**
- **Realistic performance**: Tests on multiple train/test splits
- **Variance estimation**: Provides confidence intervals
- **Hyperparameter tuning**: Prevents overfitting to validation set
- **Data efficiency**: Uses all data for both training and testing

**Common Types:**
- **KFold**: Standard k-fold
- **StratifiedKFold**: Maintains class distribution
- **ShuffleSplit**: Random splits (good for large datasets)
- **TimeSeriesSplit**: For time series data

### Q12: What metrics should you use for classification problems?

**Answer:**
Choice of metric depends on the problem and class distribution:

**For Balanced Classes:**
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

accuracy = accuracy_score(y_true, y_pred)    # Overall correctness
precision = precision_score(y_true, y_pred)  # True positives / predicted positives
recall = recall_score(y_true, y_pred)        # True positives / actual positives
f1 = f1_score(y_true, y_pred)                 # Harmonic mean of precision and recall
```

**For Imbalanced Classes:**
```python
from sklearn.metrics import balanced_accuracy_score, roc_auc_score

balanced_acc = balanced_accuracy_score(y_true, y_pred)  # Average recall per class
auc = roc_auc_score(y_true, y_prob)                     # Area under ROC curve
```

**Confusion Matrix:**
```python
from sklearn.metrics import confusion_matrix, classification_report

cm = confusion_matrix(y_true, y_pred)
print(classification_report(y_true, y_pred))
```

**When to Use Each:**
- **Accuracy**: Balanced classes, equal misclassification costs
- **Precision**: When false positives are costly (spam detection)
- **Recall**: When false negatives are costly (medical diagnosis)
- **F1**: Balance between precision and recall
- **AUC**: Ranking performance, threshold-independent

### Q13: How do you evaluate regression models?

**Answer:**
Regression evaluation focuses on prediction accuracy and error magnitude:

**Common Metrics:**
```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

mae = mean_absolute_error(y_true, y_pred)    # Average absolute error
mse = mean_squared_error(y_true, y_pred)    # Average squared error
rmse = np.sqrt(mse)                          # Root mean squared error
r2 = r2_score(y_true, y_pred)                # Explained variance (0-1)
```

**When to Use:**
- **MAE**: Easy to interpret, robust to outliers
- **MSE/RMSE**: Penalizes large errors, good for optimization
- **R²**: Proportion of variance explained, good for comparison

**Residual Analysis:**
```python
residuals = y_true - y_pred
plt.scatter(y_pred, residuals)  # Check for patterns
plt.axhline(y=0, color='r')     # Should be randomly scattered
```

### Q14: Explain the bias-variance tradeoff.

**Answer:**
The bias-variance tradeoff is fundamental to machine learning model selection:

**Bias:**
- **Definition**: Error from incorrect assumptions
- **High bias**: Underfitting, model too simple
- **Symptoms**: Poor performance on training and test data

**Variance:**
- **Definition**: Error from sensitivity to training data
- **High variance**: Overfitting, model too complex
- **Symptoms**: Good training performance, poor test performance

**Tradeoff:**
- **Simple models**: High bias, low variance
- **Complex models**: Low bias, high variance
- **Goal**: Find optimal balance

**Visualization:**
```python
from sklearn.model_selection import validation_curve

param_range = np.logspace(-3, 3, 10)
train_scores, val_scores = validation_curve(
    estimator, X, y, param_name='C', param_range=param_range, cv=5
)

plt.plot(param_range, train_scores.mean(axis=1), label='Training')
plt.plot(param_range, val_scores.mean(axis=1), label='Validation')
plt.xscale('log')
```

## Hyperparameter Tuning

### Q15: How do you perform hyperparameter tuning?

**Answer:**
Scikit-learn provides several methods for hyperparameter optimization:

**Grid Search:**
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'C': [0.1, 1, 10, 100],
    'kernel': ['linear', 'rbf'],
    'gamma': [0.001, 0.01, 0.1, 1]
}

grid_search = GridSearchCV(SVC(), param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

print("Best params:", grid_search.best_params_)
print("Best score:", grid_search.best_score_)
```

**Random Search:**
```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

param_dist = {
    'C': uniform(0.1, 100),
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': uniform(0.001, 1)
}

random_search = RandomizedSearchCV(SVC(), param_dist, n_iter=50, cv=5)
random_search.fit(X_train, y_train)
```

**Best Practices:**
- Use cross-validation to avoid overfitting
- Start with wide parameter ranges
- Use random search for high-dimensional spaces
- Consider computational cost
- Validate on separate test set

## Pipelines and Production

### Q16: How do you create and use pipelines?

**Answer:**
Pipelines chain preprocessing and modeling steps for reproducible workflows:

**Basic Pipeline:**
```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier())
])

pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

**Column Transformer for Mixed Data:**
```python
from sklearn.compose import ColumnTransformer

preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), numeric_features),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('encoder', OneHotEncoder())
        ]), categorical_features)
    ])

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier())
])
```

**Benefits:**
- **Reproducibility**: Same preprocessing for train/test
- **Convenience**: Single fit/predict interface
- **Safety**: Prevents data leakage
- **Composition**: Easy to modify and extend

### Q17: How do you handle imbalanced datasets?

**Answer:**
Several strategies for dealing with class imbalance:

**Resampling Techniques:**
```python
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# Oversampling minority class
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# Undersampling majority class
rus = RandomUnderSampler(random_state=42)
X_resampled, y_resampled = rus.fit_resample(X_train, y_train)
```

**Class Weights:**
```python
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weight_dict = dict(zip(np.unique(y_train), class_weights))

model = RandomForestClassifier(class_weight=class_weight_dict)
```

**Evaluation Metrics:**
```python
from sklearn.metrics import classification_report

# Use appropriate metrics
print(classification_report(y_true, y_pred))
# Focus on minority class performance
```

### Q18: How do you save and load Scikit-learn models?

**Answer:**
Model persistence for production deployment:

**Using joblib (recommended for large models):**
```python
import joblib

# Save model
joblib.dump(model, 'model.joblib')

# Load model
loaded_model = joblib.load('model.joblib')
```

**Using pickle:**
```python
import pickle

# Save
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Load
with open('model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)
```

**Best Practices:**
- Save the entire pipeline, not just the model
- Include preprocessing steps
- Save model version and training metadata
- Validate loaded model produces same results

## Advanced Topics

### Q19: How do you handle high-dimensional data?

**Answer:**
Techniques for dimensionality reduction and feature selection:

**Feature Selection:**
```python
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif

# Univariate feature selection
selector = SelectKBest(score_func=f_classif, k=100)
X_selected = selector.fit_transform(X, y)

# Feature importance from model
from sklearn.feature_selection import SelectFromModel
selector = SelectFromModel(RandomForestClassifier(), max_features=100)
X_selected = selector.fit_transform(X, y)
```

**Dimensionality Reduction:**
```python
from sklearn.decomposition import PCA

# PCA for linear dimensionality reduction
pca = PCA(n_components=50)
X_reduced = pca.fit_transform(X_scaled)

# Explained variance
explained_variance = pca.explained_variance_ratio_
print(f"Explained variance: {explained_variance.sum():.3f}")
```

**When to Use:**
- **Feature Selection**: When interpretability is important
- **PCA**: When features are correlated, for visualization
- **t-SNE**: For visualization only (not for preprocessing)

### Q20: Explain the difference between supervised and unsupervised learning.

**Answer:**
Fundamental distinction in machine learning approaches:

**Supervised Learning:**
```python
# Has labeled training data
X_train, y_train  # Features and labels
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```
- **Goal**: Learn mapping from inputs to known outputs
- **Examples**: Classification, regression
- **Evaluation**: Compare predictions to true labels
- **Use**: When labeled data is available

**Unsupervised Learning:**
```python
# No labels, only features
X_train  # Only features
model.fit(X_train)
clusters = model.predict(X_test)  # Or transform
```
- **Goal**: Find patterns or structure in data
- **Examples**: Clustering, dimensionality reduction
- **Evaluation**: Internal metrics (silhouette score) or domain knowledge
- **Use**: When labels are expensive/unavailable

**Key Differences:**
- **Data requirements**: Supervised needs labels
- **Goal**: Prediction vs. pattern discovery
- **Evaluation**: Objective metrics vs. subjective assessment
- **Applications**: Prediction vs. exploration

## Common Pitfalls and Best Practices

### Q21: What are common mistakes in Scikit-learn usage?

**Answer:**

**Data Leakage:**
```python
# Wrong: Scaling before train-test split
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Uses entire dataset
X_train, X_test = train_test_split(X_scaled, test_size=0.2)

# Correct: Scale after splitting
X_train, X_test = train_test_split(X, test_size=0.2)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

**Incorrect Cross-Validation:**
```python
# Wrong: Scaling inside CV loop but fitting on each fold
for train_idx, val_idx in kf.split(X):
    scaler = StandardScaler()
    X_train_fold = scaler.fit_transform(X[train_idx])  # Wrong!
    X_val_fold = scaler.transform(X[val_idx])

# Correct: Scale entire dataset first or use pipeline
pipeline = Pipeline([('scaler', StandardScaler()), ('model', SVC())])
scores = cross_val_score(pipeline, X, y, cv=5)
```

**Ignoring Class Imbalance:**
```python
# Wrong: Using accuracy on imbalanced data
accuracy = accuracy_score(y_true, y_pred)  # Misleading

# Correct: Use appropriate metrics
print(classification_report(y_true, y_pred))
```

### Q22: How do you debug machine learning models?

**Answer:**
Systematic approach to model debugging:

**1. Check Data Quality:**
```python
# Data types and missing values
print(X.dtypes)
print(X.isnull().sum())

# Basic statistics
print(X.describe())

# Class distribution
print(y.value_counts())
```

**2. Validate Preprocessing:**
```python
# Check scaling worked
print("Mean:", X_scaled.mean(axis=0))
print("Std:", X_scaled.std(axis=0))

# Check encoding
print("Encoded shape:", X_encoded.shape)
print("Categories:", encoder.categories_)
```

**3. Model Diagnostics:**
```python
# Learning curves
from sklearn.model_selection import learning_curve

train_sizes, train_scores, val_scores = learning_curve(
    model, X, y, cv=5, n_jobs=-1
)

plt.plot(train_sizes, train_scores.mean(axis=1), label='Training')
plt.plot(train_sizes, val_scores.mean(axis=1), label='Validation')
```

**4. Error Analysis:**
```python
# Confusion matrix analysis
cm = confusion_matrix(y_true, y_pred)
# Analyze which classes are confused

# Residual analysis for regression
residuals = y_true - y_pred
plt.scatter(y_pred, residuals)
```

### Q23: How do you handle categorical features with high cardinality?

**Answer:**
Strategies for high-cardinality categorical variables:

**Target Encoding (Mean Encoding):**
```python
# Replace category with mean target value
means = y.groupby(X['category']).mean()
X['category_encoded'] = X['category'].map(means)

# Add smoothing to prevent overfitting
global_mean = y.mean()
category_means = y.groupby(X['category']).agg(['mean', 'count'])
smoothing_factor = 10
smoothed_means = (category_means['mean'] * category_means['count'] +
                 global_mean * smoothing_factor) / (category_means['count'] + smoothing_factor)
```

**Frequency Encoding:**
```python
# Replace with frequency of occurrence
freq_encoding = X['category'].value_counts() / len(X)
X['category_freq'] = X['category'].map(freq_encoding)
```

**Binary Encoding:**
```python
# Convert to binary representation
from category_encoders import BinaryEncoder
encoder = BinaryEncoder(cols=['category'])
X_encoded = encoder.fit_transform(X)
```

**Feature Hashing:**
```python
from sklearn.feature_extraction import FeatureHasher
hasher = FeatureHasher(n_features=100, input_type='string')
hashed_features = hasher.fit_transform(X['category'].astype(str))
```

### Q24: Explain the curse of dimensionality.

**Answer:**
The curse of dimensionality refers to problems that arise in high-dimensional spaces:

**Key Issues:**
- **Data sparsity**: Points become increasingly isolated
- **Distance concentration**: All pairwise distances become similar
- **Computational complexity**: Algorithms become exponentially slower
- **Overfitting**: Models can perfectly fit noise in high dimensions

**Manifestations:**
```python
# Distance concentration example
from sklearn.metrics.pairwise import euclidean_distances

for dim in [2, 10, 100]:
    points = np.random.randn(100, dim)
    distances = euclidean_distances(points)
    # In high dimensions, distances become similar
    print(f"Dim {dim}: Distance std = {distances.std():.4f}")
```

**Solutions:**
- **Dimensionality reduction**: PCA, t-SNE, feature selection
- **Regularization**: Prevent overfitting in high dimensions
- **Local methods**: k-NN becomes less effective
- **Feature engineering**: Create meaningful features

### Q25: How do you handle time series data in Scikit-learn?

**Answer:**
Time series considerations for traditional ML algorithms:

**Feature Engineering:**
```python
# Lag features
df['lag_1'] = df['value'].shift(1)
df['lag_7'] = df['value'].shift(7)

# Rolling statistics
df['rolling_mean_7'] = df['value'].rolling(window=7).mean()
df['rolling_std_7'] = df['value'].rolling(window=7).std()

# Time-based features
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['month'] = df['timestamp'].dt.month
```

**Time Series Cross-Validation:**
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    # Train and validate
```

**Considerations:**
- **No random shuffling**: Preserve temporal order
- **Refit vs online learning**: Choose based on concept drift
- **Seasonality**: Include periodic features
- **Stationarity**: Check and transform if needed

This comprehensive set of interview questions covers Scikit-learn fundamentals, algorithms, best practices, and real-world applications. Focus on understanding the library's design principles and appropriate use cases rather than memorizing specific function signatures.
