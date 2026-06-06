# ML Fundamentals - Complete Implementation Guide

## Overview
This repository contains three comprehensive mini-projects demonstrating core machine learning concepts:

1. **Iris Classification** - Supervised Learning
2. **Movie Recommendation System** - Collaborative Filtering
3. **Sentiment Analysis** - Text Classification

## Project Structure
```
01-ML-Fundamentals/
├── requirements.txt                              # All required packages
├── 01-iris-classification/
│   ├── iris_classifier.py                       # Complete Iris classification pipeline
│   ├── iris_classification.ipynb                # Interactive Jupyter notebook
│   ├── README.md                                # Project documentation
│   └── [visualizations]                         # Generated plots
├── 02-movie-recommendation/
│   ├── recommendation_system.py                 # Recommendation algorithms
│   ├── movie_recommendation.ipynb               # Interactive notebook
│   ├── README.md                                # Project documentation
│   └── [visualizations]                         # Generated plots
├── 03-sentiment-analysis/
│   ├── sentiment_analysis.py                    # Sentiment analysis pipeline
│   ├── sentiment_analysis.ipynb                 # Interactive notebook
│   ├── README.md                                # Project documentation
│   └── [visualizations]                         # Generated plots
└── README.md                                     # This file
```

## Installation

### 1. Clone the Repository
```bash
cd /Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Project 1: Iris Classification

### Overview
Demonstrates supervised learning with multiple classification algorithms on the famous Iris dataset.

### What You'll Learn
- Loading and exploring datasets with pandas
- Data preprocessing and feature scaling
- Implementing multiple classifiers:
  - Logistic Regression (linear classifier)
  - Decision Tree (tree-based classifier)
  - Random Forest (ensemble method)
  - Support Vector Machine (non-linear classifier)
- Model evaluation metrics (accuracy, precision, recall, F1)
- Confusion matrices and classification reports
- Hyperparameter tuning with GridSearchCV
- Cross-validation for robust evaluation

### Key Features
✓ 80/20 train-test split with stratification
✓ Feature normalization using StandardScaler
✓ 4 different classification algorithms
✓ Comprehensive evaluation metrics
✓ Hyperparameter tuning and optimization
✓ 5-fold cross-validation
✓ Professional visualizations

### Expected Results
- All models achieve >90% accuracy on test set
- Best model typically: Random Forest with tuned parameters
- See: `01-iris-classification/iris_classifier.py`

### Running the Project
```bash
# Run the Python script
python 01-iris-classification/iris_classifier.py

# Or use the Jupyter notebook for interactive exploration
jupyter notebook 01-iris-classification/iris_classification.ipynb
```

### Output Files
- `01_data_exploration.png` - Feature relationships and distributions
- `02_metrics_comparison.png` - Model performance comparison
- `03_confusion_matrices.png` - Prediction error analysis

---

## Project 2: Movie Recommendation System

### Overview
Implements collaborative filtering algorithms to recommend movies based on user preferences.

### What You'll Learn
- Building user-item rating matrices
- Similarity metrics (cosine similarity)
- Collaborative Filtering Approaches:
  - **User-Based CF**: Find similar users and recommend their favorite movies
  - **Item-Based CF**: Find similar movies to those user rated highly
  - **Matrix Factorization (SVD)**: Decompose rating matrix to latent factors
- Evaluation metrics (RMSE, MAE)
- Cold-start problem handling
- Recommendation strategies for new users

### Key Features
✓ Synthetic realistic rating dataset (50 users, 30 movies)
✓ User-based collaborative filtering
✓ Item-based collaborative filtering
✓ SVD-based matrix factorization
✓ Cold-start problem solutions
✓ Multiple recommendation strategies
✓ Performance visualization

### Algorithm Details

#### User-Based CF
1. Find users with similar rating patterns
2. Get movies highly rated by similar users
3. Recommend unwatched movies

#### Item-Based CF
1. Find movies similar to ones user rated highly
2. Use movie similarity and user ratings
3. Weighted recommendation scores

#### Matrix Factorization (SVD)
1. Decompose rating matrix: R ≈ U × Σ × V^T
2. Latent factors represent hidden user/movie features
3. Predict missing ratings

### Running the Project
```bash
python 02-movie-recommendation/recommendation_system.py

# Interactive exploration
jupyter notebook 02-movie-recommendation/movie_recommendation.ipynb
```

### Output Files
- `01_data_exploration.png` - Dataset statistics and distributions
- `02_recommendations_comparison.png` - Recommendations from different methods

---

## Project 3: Sentiment Analysis

### Overview
Text classification system for analyzing sentiment (positive/negative) of social media data.

### What You'll Learn
- Text preprocessing techniques:
  - Lowercasing, URL/email removal
  - Punctuation and whitespace handling
  - Stopword removal
- Feature Extraction Methods:
  - **Bag of Words (BoW)**: Simple word count vectors
  - **TF-IDF**: Term frequency-inverse document frequency
- Classification Algorithms:
  - Naive Bayes (probabilistic classifier)
  - Logistic Regression
  - Support Vector Machine
  - Random Forest
- Evaluation and hyperparameter tuning
- Real-time sentiment prediction

### Key Features
✓ Text preprocessing pipeline
✓ Multiple feature extraction methods
✓ 4 different classification algorithms
✓ Comprehensive evaluation metrics
✓ Feature importance analysis
✓ Real-time prediction demo
✓ Professional visualizations

### Text Preprocessing Pipeline
1. **Cleaning**: Remove URLs, emails, punctuation
2. **Normalization**: Convert to lowercase
3. **Tokenization**: Split into words
4. **Stop Word Removal**: Remove common words
5. **Vectorization**: Convert to numerical features

### Running the Project
```bash
python 03-sentiment-analysis/sentiment_analysis.py

# Interactive exploration
jupyter notebook 03-sentiment-analysis/sentiment_analysis.ipynb
```

### Output Files
- `01_feature_importance.png` - Most important sentiment-bearing words
- `02_model_comparison.png` - Model performance comparison
- `03_confusion_matrices.png` - Prediction error analysis

---

## Technical Stack

### Core Libraries
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning algorithms
- **matplotlib**: Static visualization
- **seaborn**: Statistical data visualization
- **scipy**: Scientific computing

### Algorithms Implemented
- Classification: Logistic Regression, Decision Tree, Random Forest, SVM
- Clustering/Filtering: Collaborative Filtering, SVD, Cosine Similarity
- Text Processing: TF-IDF, Bag of Words, Tokenization

### Evaluation Metrics
- **Accuracy**: Overall correctness
- **Precision**: True Positives / (True Positives + False Positives)
- **Recall**: True Positives / (True Positives + False Negatives)
- **F1-Score**: Harmonic mean of Precision and Recall
- **Confusion Matrix**: Detailed error analysis
- **Cross-Validation**: Robust performance estimation

---

## Common ML Concepts Covered

### 1. Data Handling
- [ ] Dataset loading and exploration
- [ ] Train-test splitting
- [ ] Stratified sampling
- [ ] Feature scaling and normalization

### 2. Feature Engineering
- [ ] Feature extraction (numerical and text)
- [ ] Feature importance analysis
- [ ] Dimensionality reduction (via SVD)

### 3. Model Development
- [ ] Multiple algorithm comparison
- [ ] Hyperparameter tuning
- [ ] Cross-validation
- [ ] Performance optimization

### 4. Evaluation
- [ ] Multiple metrics comparison
- [ ] Confusion matrices
- [ ] Classification reports
- [ ] ROC curves and AUC

### 5. Deployment Ready
- [ ] Clean, documented code
- [ ] Error handling
- [ ] Modular design
- [ ] Example predictions

---

## Best Practices Demonstrated

✓ **Code Quality**
  - Clear function documentation
  - Type hints and docstrings
  - Modular, reusable code
  - Proper error handling

✓ **Data Science**
  - Proper train-test splitting
  - Feature scaling for distance-based models
  - Cross-validation for robust evaluation
  - Multiple metrics for comprehensive assessment

✓ **Reproducibility**
  - Fixed random seeds
  - Stratified sampling
  - Version control ready
  - Documented parameters

✓ **Visualization**
  - Clear, labeled plots
  - Multiple perspectives on results
  - Professional styling
  - Saved high-resolution images

---

## Performance Summary

| Project | Best Model | Accuracy |
|---------|-----------|----------|
| Iris | Random Forest | >96% |
| Movie Rec | SVD + Hybrid | RMSE <0.8 |
| Sentiment | Logistic Reg | >90% |

---

## Learning Path

### Week 1: Iris Classification
- [ ] Run `iris_classifier.py`
- [ ] Study the pipeline class
- [ ] Examine visualizations
- [ ] Modify hyperparameters
- [ ] Try different train-test splits

### Week 2: Movie Recommendation
- [ ] Run `recommendation_system.py`
- [ ] Understand collaborative filtering
- [ ] Compare recommendation methods
- [ ] Test cold-start handling
- [ ] Create your own dataset

### Week 3: Sentiment Analysis
- [ ] Run `sentiment_analysis.py`
- [ ] Test text preprocessing
- [ ] Compare feature extraction methods
- [ ] Predict sentiment on custom texts
- [ ] Extend with more data

### Week 4: Advanced Topics
- [ ] Combine techniques across projects
- [ ] Implement ensemble methods
- [ ] Add deep learning models
- [ ] Deploy as API
- [ ] Optimize for production

---

## Troubleshooting

### Import Errors
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Memory Issues with Large Datasets
```python
# Use sparse matrices for text data
from scipy.sparse import csr_matrix
```

### Slow Training
```python
# Use n_jobs parameter
RandomForestClassifier(n_estimators=100, n_jobs=-1)
```

---

## Extensions and Ideas

1. **Iris Classification**
   - Add cross-validation plots
   - Implement feature selection
   - Try deep learning models
   - Deploy as REST API

2. **Movie Recommendation**
   - Use real MovieLens dataset
   - Implement implicit feedback
   - Add content-based filtering
   - Create web interface

3. **Sentiment Analysis**
   - Use pre-trained embeddings (Word2Vec, GloVe)
   - Implement deep learning (LSTM, BERT)
   - Multi-class classification (5 sentiments)
   - Domain-specific fine-tuning

---

## Resources

### Documentation
- [scikit-learn](https://scikit-learn.org/stable/documentation.html)
- [pandas](https://pandas.pydata.org/docs/)
- [numpy](https://numpy.org/doc/)

### Books
- "Hands-On Machine Learning" - Aurélien Géron
- "Introduction to Statistical Learning" - James, Witten, et al.
- "Natural Language Processing with Python" - Bird, Klein, Loper

### Online Courses
- Andrew Ng's Machine Learning Specialization (Coursera)
- Fast.ai - Practical Deep Learning for Coders
- Kaggle Learn - Free mini-courses

---

## Success Criteria

✓ All 3 projects implemented and working
✓ Models achieve >85% accuracy
✓ Clean, well-documented code
✓ Professional visualizations
✓ Working demos for each project
✓ Comprehensive documentation

---

## Next Steps After Completion

1. **Combine Techniques**: Use sentiment analysis features for recommendation
2. **Real Datasets**: Replace synthetic data with real-world datasets
3. **Deep Learning**: Upgrade algorithms to neural networks
4. **Production Deployment**: Package as Docker container
5. **Advanced Topics**: Explore reinforcement learning, unsupervised learning

---

## Support

For questions or issues:
1. Check the individual project README files
2. Review the Jupyter notebooks for detailed explanations
3. Consult scikit-learn documentation
4. Visit Stack Overflow for specific error messages

---

**Last Updated**: November 2025
**Difficulty Level**: Intermediate
**Estimated Time**: 30-40 hours
**Prerequisites**: Python basics, basic statistics

**Happy Learning! 🚀**
