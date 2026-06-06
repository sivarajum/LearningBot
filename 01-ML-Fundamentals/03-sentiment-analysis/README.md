# Sentiment Analysis - Text Classification

## Overview
This project implements a comprehensive sentiment analysis system for classifying text as positive or negative. It demonstrates text preprocessing, feature extraction, and multiple classification algorithms.

## Problem Statement
**Goal**: Automatically classify social media text as positive or negative sentiment

**Challenges**:
- Unstructured text data (URLs, emojis, slang)
- Misspellings and informal language
- Sarcasm and context dependency
- Limited labeled training data

## Sentiment Analysis Pipeline

```
Raw Text
    ↓
Preprocessing (clean, tokenize, remove stopwords)
    ↓
Feature Extraction (BoW or TF-IDF)
    ↓
Classification (Naive Bayes, SVM, Logistic Regression, Random Forest)
    ↓
Evaluation & Prediction
```

## Text Preprocessing

### 1. Cleaning
**Goal**: Remove noise and normalize text

```python
def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Convert to lowercase
    text = text.lower()

    return text
```

### 2. Tokenization
**Convert text to words**:
```
"I love this product!" → ["I", "love", "this", "product"]
```

### 3. Stop Word Removal
**Remove common, non-informative words**:
```
"I love this product" → "love product"
```

Common stopwords: a, an, and, are, as, at, be, by, for, from, has, he, in, is, it, of, on, or, that, the, to, was, will, with

### 4. Stemming/Lemmatization
**Reduce words to root form**:
```
"running", "runs", "ran" → "run"
"easily", "easier", "easy" → "easy"
```

## Feature Extraction Methods

### 1. Bag of Words (BoW)
**Idea**: Count how many times each word appears

**Example**:
```
Text 1: "I love this movie"
Text 2: "I hate this movie"

Vocabulary: [I, love, hate, this, movie]

Text 1 vector: [1, 1, 0, 1, 1]
Text 2 vector: [1, 0, 1, 1, 1]
```

**Implementation**:
```python
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(max_features=100)
X = vectorizer.fit_transform(texts)

# Result: sparse matrix (n_samples, n_features)
# Each cell = word count
```

**Pros**:
- Simple and fast
- Preserves word frequency information
- Works well for many applications

**Cons**:
- Ignores word order
- Ignores word importance
- Creates large, sparse matrices
- Equal weight to all words (common words dominate)

### 2. TF-IDF (Term Frequency-Inverse Document Frequency)
**Idea**: Weight words by their importance, not just frequency

**Formula**:
```
TF-IDF(word, doc) = TF(word, doc) × IDF(word)

TF = (frequency of word in doc) / (total words in doc)

IDF = log(total docs / docs containing word)
```

**Example**:
```
"love" appears in 80% of positive reviews → low IDF (common)
"movie" appears in 50% of all reviews → medium IDF (medium importance)
"cinematography" appears in 2% of reviews → high IDF (discriminative)
```

**Implementation**:
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(max_features=100)
X = vectorizer.fit_transform(texts)

# Result: weighted matrix where important words have higher values
```

**Pros**:
- Accounts for word importance
- Reduces impact of common words
- Better discriminative power
- Standard in NLP

**Cons**:
- Still ignores word order
- Ignores negation ("not good" = "good")
- Computationally more expensive

### Comparison
| Feature | BoW | TF-IDF |
|---------|-----|--------|
| **Speed** | Fast | Slower |
| **Sparsity** | High | High |
| **Common Words** | Dominate | Reduced |
| **Information** | Frequency | Importance |
| **Typical Accuracy** | 85% | 90% |

## Classification Algorithms

### 1. Naive Bayes
**Probabilistic Classifier**

**Principle**: Assume independence between features
```
P(positive|words) = P(words|positive) × P(positive) / P(words)
```

**Pros**:
- Fast training and prediction
- Works well with small datasets
- Provides probability estimates
- Good baseline

**Cons**:
- Independence assumption is unrealistic
- Ignores feature correlations
- Can underestimate confidence

**Typical Accuracy**: 85-88%

```python
from sklearn.naive_bayes import MultinomialNB

model = MultinomialNB()
model.fit(X_train, y_train)
```

### 2. Logistic Regression
**Linear Probabilistic Model**

**Principle**: Learn linear decision boundary, output probability
```
P(positive|x) = 1 / (1 + e^(-z))
where z = β₀ + β₁x₁ + β₂x₂ + ...
```

**Pros**:
- Interpretable (see feature coefficients)
- Fast training
- Good regularization options
- Outputs probabilities

**Cons**:
- Assumes linear separability
- Sensitive to outliers
- Needs feature scaling

**Typical Accuracy**: 88-92%

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# View which words are most positive/negative
coefficients = model.coef_[0]
```

### 3. Support Vector Machine (SVM)
**Non-Linear Classifier**

**Principle**: Find optimal hyperplane maximizing margin
```
Decision function: f(x) = Σ(αᵢ × y_i × K(x_i, x))
```

**Pros**:
- Handles non-linear patterns
- Good generalization
- Works in high dimensions
- Robust to outliers

**Cons**:
- Slow on large datasets
- Requires feature scaling
- Less interpretable
- Sensitive to hyperparameters

**Typical Accuracy**: 90-93%

```python
from sklearn.svm import SVC

model = SVC(kernel='linear', probability=True)
model.fit(X_train, y_train)
```

### 4. Random Forest
**Ensemble Tree Method**

**Principle**: Build many decision trees, vote on prediction
```
Prediction = majority_vote([Tree₁(x), Tree₂(x), ..., Tree_n(x)])
```

**Pros**:
- Excellent performance
- Handles non-linearity well
- Robust to noise
- Feature importance available

**Cons**:
- Slower prediction
- Black box (hard to interpret)
- Overfitting risk if not tuned

**Typical Accuracy**: 90-94%

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=50)
model.fit(X_train, y_train)

# Feature importance (which words matter most?)
importance = model.feature_importances_
```

## Project Structure
```
03-sentiment-analysis/
├── sentiment_analysis.py           # Main implementation
├── sentiment_analysis.ipynb        # Interactive notebook
├── README.md                       # This file
└── [output plots]
    ├── 01_feature_importance.png
    ├── 02_model_comparison.png
    └── 03_confusion_matrices.png
```

## Dataset

### Characteristics
- **Samples**: 40 (20 positive, 20 negative)
- **Balance**: Perfectly balanced (50/50)
- **Language**: English social media reviews
- **Vocabulary**: ~200 unique words (after preprocessing)

### Sample Data
```
Positive Examples:
- "I love this product! It's amazing and works perfectly."
- "Best purchase ever! Highly recommend it."
- "Excellent quality and fast shipping. Very satisfied!"

Negative Examples:
- "This product is terrible. Complete waste of money."
- "Horrible quality. Very disappointed."
- "Worst purchase ever. Don't waste your time."
```

## Model Evaluation

### Confusion Matrix for Binary Classification
```
                Predicted
           Positive  Negative
Actual Pos    TP        FN
       Neg    FP        TN
```

### Key Metrics

**Accuracy**:
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
When to use: Balanced datasets
```

**Precision** (False Positive Focus):
```
Precision = TP / (TP + FP)
When to use: Minimize false positives (cost of false positive is high)
Example: Spam detection - wrongly classifying good email as spam is bad
```

**Recall** (False Negative Focus):
```
Recall = TP / (TP + FN)
When to use: Minimize false negatives (cost of missing actual positives)
Example: Disease detection - missing a patient with disease is very bad
```

**F1-Score** (Harmonic Mean):
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
When to use: Balance precision and recall, imbalanced datasets
```

## Implementation Walkthrough

### Step 1: Load and Preprocess Data
```python
# Load data
texts, labels = load_sentiment_data()

# Preprocess
cleaned_texts = []
for text in texts:
    text = clean_text(text)
    text = remove_stopwords(text)
    cleaned_texts.append(text)
```

### Step 2: Feature Extraction
```python
# Extract TF-IDF features
vectorizer = TfidfVectorizer(max_features=100)
X = vectorizer.fit_transform(cleaned_texts)

# Result: (40, 100) matrix
# 40 samples, 100 features (top 100 words)
```

### Step 3: Train-Test Split
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, labels, test_size=0.2, random_state=42, stratify=labels
)

# 32 training samples, 8 test samples
```

### Step 4: Train Models
```python
models = {
    'Naive Bayes': MultinomialNB(),
    'Logistic Regression': LogisticRegression(),
    'SVM': SVC(kernel='linear'),
    'Random Forest': RandomForestClassifier(n_estimators=50)
}

for name, model in models.items():
    model.fit(X_train, y_train)
```

### Step 5: Evaluate
```python
for name, model in models.items():
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"{name}: Accuracy={accuracy:.2%}, Precision={precision:.2%}")
```

### Step 6: Predict on New Text
```python
def predict_sentiment(text, model, vectorizer):
    # Preprocess
    text = clean_text(text)
    text = remove_stopwords(text)

    # Vectorize
    X = vectorizer.transform([text])

    # Predict
    prediction = model.predict(X)[0]
    confidence = model.predict_proba(X).max()

    sentiment = "Positive" if prediction == 1 else "Negative"
    return sentiment, confidence

# Usage
sentiment, conf = predict_sentiment("I love this!", model, vectorizer)
print(f"{sentiment} ({conf:.1%} confidence)")
```

## Quick Start

### Run Python Script
```bash
python sentiment_analysis.py
```

### Run Jupyter Notebook
```bash
jupyter notebook sentiment_analysis.ipynb
```

## Interpretation of Results

### Feature Importance
Top positive words: love, amazing, excellent, perfect, great, wonderful
Top negative words: terrible, hate, worst, horrible, awful, disappointment

### Word Clouds
Create visualizations of positive vs negative words:
```python
from wordcloud import WordCloud

positive_text = ' '.join([t for t, l in zip(texts, labels) if l == 1])
positive_cloud = WordCloud().generate(positive_text)
positive_cloud.to_file('positive_wordcloud.png')
```

## Common Challenges in Sentiment Analysis

### 1. Sarcasm
```
Text: "Oh, great, another boring meeting"
Literal: Positive ("great")
Actual: Negative (sarcasm)
```

### 2. Negation Handling
```
Text: "not good"
BoW/TF-IDF: treats as separate words
Better: "not_good" (bigram)
```

### 3. Aspect-Based Sentiment
```
Text: "Great design but poor battery life"
Overall Sentiment: Mixed
Need: Aspect extraction + sentiment per aspect
```

### 4. Domain Variation
```
"python" = snake (negative in wildlife)
         = programming language (neutral in tech)
Context matters!
```

## Advanced Techniques

### 1. N-grams (Bigrams, Trigrams)
```python
# Include word pairs and triplets
vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=100)

# "not good" → ["not", "good", "not_good"]
# Better captures phrases
```

### 2. Word Embeddings (Word2Vec, GloVe)
```python
from gensim.models import Word2Vec

# Learn word representations
model = Word2Vec(sentences, vector_size=100)

# "amazing", "excellent", "great" → similar vectors
# Captures semantic meaning
```

### 3. Deep Learning (LSTM, BERT)
```python
from transformers import pipeline

# Pre-trained sentiment classifier
classifier = pipeline("sentiment-analysis")

# State-of-the-art performance
result = classifier("I love this product")
```

### 4. Aspect-Based Sentiment Analysis
```python
# Separate extraction and sentiment
aspects = extract_aspects(text)  # e.g., [quality, price, service]
sentiments = {}
for aspect in aspects:
    sentiments[aspect] = classify_sentiment(aspect, text)
```

## Performance Optimization

### Dataset Size Matters
```
|Dataset Size | Typical Accuracy | Model Complexity |
|100 samples  | 75-80%          | Simple models OK |
|1K samples   | 85-90%          | Ensemble OK      |
|10K samples  | 90-95%          | Neural nets OK   |
|100K+ samples| 95%+            | Deep learning    |
```

### Vocabulary Size
```python
# Balance between coverage and noise
vectorizer = TfidfVectorizer(
    max_features=100,      # Too small: miss info, too large: noise
    min_df=2,              # Ignore words in <2 docs
    max_df=0.8             # Ignore words in >80% of docs
)
```

## Practical Deployment Example

### Flask REST API
```python
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

# Load model
model = joblib.load('sentiment_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data['text']

    # Preprocess
    X = vectorizer.transform([text])

    # Predict
    sentiment = 'Positive' if model.predict(X)[0] else 'Negative'
    confidence = model.predict_proba(X).max()

    return jsonify({
        'sentiment': sentiment,
        'confidence': float(confidence)
    })

if __name__ == '__main__':
    app.run(debug=True)
```

Usage:
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product"}'

# Response: {"sentiment": "Positive", "confidence": 0.95}
```

## Files Generated

- **01_feature_importance.png**: Top sentiment-bearing words
- **02_model_comparison.png**: Model performance comparison
- **03_confusion_matrices.png**: Detailed error analysis

## Learning Outcomes

After completing this project, you should understand:

✓ Text preprocessing techniques
✓ Difference between BoW and TF-IDF
✓ How classification algorithms work
✓ Evaluation metrics for classification
✓ Binary classification problems
✓ Text feature engineering
✓ How to handle sentiment analysis
✓ Real-time prediction systems
✓ Practical NLP applications

## Next Steps

1. **Real Data**: Use Twitter API or IMDB reviews
2. **Multi-Class**: 5-class sentiment (1-5 stars)
3. **Multi-Lingual**: Support multiple languages
4. **Aspect-Based**: Sentiment for different aspects
5. **Deep Learning**: Use LSTM or BERT
6. **Deployment**: REST API or production system

## References

- NLTK Documentation: https://www.nltk.org/
- scikit-learn Text Feature Extraction: https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction
- "Speech and Language Processing" - Jurafsky & Martin
- Stanford CS 224N: NLP with Deep Learning

## Common Issues

### Issue: Very low accuracy
**Cause**: Dataset too small or imbalanced
**Solution**: Get more data, balance classes, use proper validation

### Issue: All predictions are same class
**Cause**: Severe class imbalance
**Solution**: Use SMOTE, class weights, or balanced sampling

### Issue: Slow predictions
**Cause**: Large vocabulary or complex model
**Solution**: Reduce max_features, use simpler model, cache predictions

---

**Difficulty**: Intermediate | **Time**: 3-4 hours | **Prerequisites**: Python basics, NLP concepts
