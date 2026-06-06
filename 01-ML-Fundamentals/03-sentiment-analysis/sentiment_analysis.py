"""
Sentiment Analysis - Text Classification for Social Media Data
This module implements sentiment analysis using various feature extraction
methods and classification algorithms.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import string
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                              f1_score, confusion_matrix, classification_report,
                              roc_auc_score, roc_curve)
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class TextPreprocessor:
    """Text preprocessing utilities."""
    
    @staticmethod
    def load_sample_data():
        """Load sample sentiment data."""
        # Sample sentiment data (positive and negative reviews)
        positive_texts = [
            "I love this product! It's amazing and works perfectly.",
            "Best purchase ever! Highly recommend it.",
            "Excellent quality and fast shipping. Very satisfied!",
            "This is fantastic! Exceeded my expectations.",
            "Great movie! Loved every minute of it.",
            "Wonderful experience, will buy again!",
            "Perfect! Exactly what I was looking for.",
            "Outstanding service and great product!",
            "I'm so happy with this purchase!",
            "Absolutely fantastic! 5 stars!",
            "This is the best thing ever!",
            "Incredible! I'm amazed by the quality.",
            "Love it! Can't recommend enough.",
            "Perfect product, perfect service!",
            "Extremely satisfied with everything.",
            "This exceeded all my expectations!",
            "Wonderful! Best decision ever made.",
            "Fantastic quality at great price!",
            "I'm thrilled with this purchase!",
            "Best experience of my life!"
        ]
        
        negative_texts = [
            "This product is terrible. Complete waste of money.",
            "Horrible quality. Very disappointed.",
            "Worst purchase ever. Don't waste your time.",
            "Absolutely terrible. Stopped working immediately.",
            "Terrible movie. Fell asleep halfway through.",
            "Awful! Not worth the price at all.",
            "Poor quality and bad customer service.",
            "Completely useless. Total disappointment.",
            "I hate this! Returning immediately.",
            "Terrible! Worst quality ever.",
            "This is garbage. Absolutely useless.",
            "Horrible experience. Very unhappy.",
            "Terrible service and low quality.",
            "Disappointing and defective product.",
            "Waste of money. Very regretful purchase.",
            "Absolutely horrible and unreliable.",
            "Poor quality and broke after one day.",
            "Terrible! Complete disaster.",
            "This product is useless and expensive.",
            "Very bad quality. Highly dissatisfied."
        ]
        
        texts = positive_texts + negative_texts
        labels = [1] * len(positive_texts) + [0] * len(negative_texts)  # 1: positive, 0: negative
        
        return texts, labels
    
    @staticmethod
    def clean_text(text):
        """
        Clean and preprocess text.
        
        Parameters:
        -----------
        text : str
            Raw text to clean
        
        Returns:
        --------
        str : Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def remove_stopwords(text, stopwords=None):
        """
        Remove common stopwords from text.
        
        Parameters:
        -----------
        text : str
            Text with potential stopwords
        stopwords : set
            Set of stopwords to remove
        
        Returns:
        --------
        str : Text without stopwords
        """
        if stopwords is None:
            # Common English stopwords
            stopwords = {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
                'the', 'to', 'was', 'will', 'with', 'i', 'me', 'my', 'you',
                'your', 'this', 'but', 'not', 'have', 'do', 'does', 'did'
            }
        
        words = text.split()
        filtered_words = [w for w in words if w not in stopwords]
        return ' '.join(filtered_words)


class SentimentAnalysisSystem:
    """Comprehensive sentiment analysis system."""
    
    def __init__(self, random_state=42):
        """Initialize the system."""
        self.random_state = random_state
        self.texts = None
        self.labels = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}
        self.preprocessor = TextPreprocessor()
        
    def load_data(self):
        """Load sample sentiment data."""
        print("Loading sentiment analysis dataset...")
        self.texts, self.labels = self.preprocessor.load_sample_data()
        
        print(f"Dataset loaded:")
        print(f"  Total samples: {len(self.texts)}")
        print(f"  Positive: {sum(self.labels)}")
        print(f"  Negative: {len(self.labels) - sum(self.labels)}")
        print(f"  Balanced: {sum(self.labels) == len(self.labels) - sum(self.labels)}\n")
        
        return self
    
    def preprocess_texts(self):
        """Preprocess all texts."""
        print("Preprocessing texts...")
        
        cleaned_texts = []
        for text in self.texts:
            # Clean text
            text = self.preprocessor.clean_text(text)
            # Remove stopwords
            text = self.preprocessor.remove_stopwords(text)
            cleaned_texts.append(text)
        
        self.texts = cleaned_texts
        print(f"  Cleaned {len(self.texts)} texts\n")
        
        return self
    
    def explore_texts(self):
        """Explore text characteristics."""
        print("Text Exploration:")
        
        # Text length statistics
        text_lengths = [len(text.split()) for text in self.texts]
        print(f"  Average text length: {np.mean(text_lengths):.1f} words")
        print(f"  Min text length: {np.min(text_lengths)} words")
        print(f"  Max text length: {np.max(text_lengths)} words")
        
        # Word frequency
        all_words = ' '.join(self.texts).split()
        print(f"  Total words: {len(all_words)}")
        print(f"  Unique words: {len(set(all_words))}")
        
        # Most common words (positive vs negative)
        positive_words = ' '.join([t for t, l in zip(self.texts, self.labels) if l == 1]).split()
        negative_words = ' '.join([t for t, l in zip(self.texts, self.labels) if l == 0]).split()
        
        print(f"\n  Top words in positive texts:")
        for word, count in Counter(positive_words).most_common(5):
            print(f"    {word}: {count}")
        
        print(f"\n  Top words in negative texts:")
        for word, count in Counter(negative_words).most_common(5):
            print(f"    {word}: {count}")
        
        print()
        return self
    
    def extract_bow_features(self):
        """Extract Bag of Words features."""
        print("Extracting Bag of Words features...")
        
        vectorizer = CountVectorizer(max_features=100)
        X_bow = vectorizer.fit_transform(self.texts)
        
        print(f"  BOW feature matrix shape: {X_bow.shape}")
        print(f"  Vocabulary size: {len(vectorizer.get_feature_names_out())}\n")
        
        self.bow_vectorizer = vectorizer
        return X_bow
    
    def extract_tfidf_features(self):
        """Extract TF-IDF features."""
        print("Extracting TF-IDF features...")
        
        vectorizer = TfidfVectorizer(max_features=100)
        X_tfidf = vectorizer.fit_transform(self.texts)
        
        print(f"  TF-IDF feature matrix shape: {X_tfidf.shape}\n")
        
        self.tfidf_vectorizer = vectorizer
        return X_tfidf
    
    def split_data(self, X_features, test_size=0.2):
        """Split data for training and testing."""
        X_train, X_test, y_train, y_test = train_test_split(
            X_features, self.labels, test_size=test_size, random_state=self.random_state, stratify=self.labels
        )
        
        return X_train, X_test, y_train, y_test
    
    def train_models(self, X_train, y_train, feature_type='TF-IDF'):
        """Train sentiment classification models."""
        print(f"Training models with {feature_type} features...")
        
        models = {}
        
        # Naive Bayes
        print("  - Training Naive Bayes...")
        nb = MultinomialNB()
        nb.fit(X_train, y_train)
        models['Naive Bayes'] = nb
        
        # Logistic Regression
        print("  - Training Logistic Regression...")
        lr = LogisticRegression(max_iter=200, random_state=self.random_state)
        lr.fit(X_train, y_train)
        models['Logistic Regression'] = lr
        
        # SVM
        print("  - Training SVM...")
        svm = SVC(kernel='linear', probability=True, random_state=self.random_state)
        svm.fit(X_train, y_train)
        models['SVM'] = svm
        
        # Random Forest
        print("  - Training Random Forest...")
        rf = RandomForestClassifier(n_estimators=50, random_state=self.random_state)
        rf.fit(X_train, y_train)
        models['Random Forest'] = rf
        
        print("All models trained!\n")
        
        return models
    
    def evaluate_models(self, models, X_test, y_test):
        """Evaluate all models."""
        print("Evaluating models...\n")
        
        results = {}
        
        for model_name, model in models.items():
            y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            results[model_name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'y_pred': y_pred,
                'confusion_matrix': confusion_matrix(y_test, y_pred)
            }
            
            print(f"{model_name}:")
            print(f"  Accuracy:  {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall:    {recall:.4f}")
            print(f"  F1-Score:  {f1:.4f}\n")
        
        return results
    
    def visualize_feature_importance(self, X_features, feature_names):
        """Visualize important features."""
        print("Creating feature importance visualization...")
        
        # Get top features (TF-IDF weights)
        feature_importance = np.asarray(X_features.mean(axis=0)).ravel()
        top_indices = np.argsort(feature_importance)[::-1][:15]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        top_features = [feature_names[i] for i in top_indices]
        top_importance = feature_importance[top_indices]
        
        ax.barh(top_features, top_importance, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Average TF-IDF Weight')
        ax.set_title('Top 15 Most Important Features')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/03-sentiment-analysis/01_feature_importance.png', dpi=300, bbox_inches='tight')
        print("Saved: 01_feature_importance.png\n")
        
        return self
    
    def visualize_results(self, results):
        """Visualize model performance."""
        print("Creating performance visualization...")
        
        # Metrics comparison
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(results))
        width = 0.2
        
        for i, metric in enumerate(['accuracy', 'precision', 'recall', 'f1']):
            values = [results[model][metric] for model in results.keys()]
            ax.bar(x + i*width, values, width, label=metric.capitalize())
        
        ax.set_xlabel('Models')
        ax.set_ylabel('Score')
        ax.set_title('Sentiment Classification - Model Performance Comparison')
        ax.set_xticks(x + 1.5*width)
        ax.set_xticklabels(results.keys(), rotation=15, ha='right')
        ax.legend()
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/03-sentiment-analysis/02_model_comparison.png', dpi=300, bbox_inches='tight')
        print("Saved: 02_model_comparison.png")
        
        # Confusion matrices
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()
        
        for idx, (model_name, model_results) in enumerate(results.items()):
            cm = model_results['confusion_matrix']
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                       xticklabels=['Negative', 'Positive'],
                       yticklabels=['Negative', 'Positive'], cbar=True)
            axes[idx].set_title(f'{model_name} Confusion Matrix')
            axes[idx].set_ylabel('True Label')
            axes[idx].set_xlabel('Predicted Label')
        
        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/03-sentiment-analysis/03_confusion_matrices.png', dpi=300, bbox_inches='tight')
        print("Saved: 03_confusion_matrices.png\n")
        
        return self
    
    def predict_sentiment(self, model, vectorizer, text):
        """
        Predict sentiment for a new text.
        
        Parameters:
        -----------
        model : sklearn model
            Trained sentiment classifier
        vectorizer : sklearn vectorizer
            Text vectorizer (BOW or TF-IDF)
        text : str
            Text to classify
        
        Returns:
        --------
        int : Predicted sentiment (1: positive, 0: negative)
        float : Confidence score
        """
        # Preprocess
        text = self.preprocessor.clean_text(text)
        text = self.preprocessor.remove_stopwords(text)
        
        # Vectorize
        X = vectorizer.transform([text])
        
        # Predict
        prediction = model.predict(X)[0]
        confidence = model.predict_proba(X).max()
        
        return prediction, confidence
    
    def generate_report(self):
        """Generate comprehensive report."""
        print("\n" + "="*80)
        print("SENTIMENT ANALYSIS - COMPREHENSIVE REPORT")
        print("="*80 + "\n")
        
        print("Dataset Statistics:")
        print(f"  Total samples: {len(self.texts)}")
        print(f"  Positive: {sum(self.labels)}")
        print(f"  Negative: {len(self.labels) - sum(self.labels)}")
        
        print("\nMethods Implemented:")
        print("  ✓ Text Preprocessing (cleaning, stopword removal)")
        print("  ✓ Feature Extraction (Bag of Words, TF-IDF)")
        print("  ✓ Multiple Classifiers (Naive Bayes, Logistic Regression, SVM, Random Forest)")
        print("  ✓ Comprehensive Evaluation (Accuracy, Precision, Recall, F1)")
        print("  ✓ Real-time Prediction")
        
        print("\n" + "="*80)


def main():
    """Main execution function."""
    # Initialize system
    system = SentimentAnalysisSystem()
    
    # Load and preprocess data
    (system
     .load_data()
     .preprocess_texts()
     .explore_texts())
    
    # Extract features
    X_tfidf = system.extract_tfidf_features()
    
    # Split data
    X_train, X_test, y_train, y_test = system.split_data(X_tfidf, test_size=0.2)
    
    # Train models
    models = system.train_models(X_train, y_train, feature_type='TF-IDF')
    
    # Evaluate models
    results = system.evaluate_models(models, X_test, y_test)
    
    # Visualize
    system.visualize_feature_importance(X_tfidf, system.tfidf_vectorizer.get_feature_names_out())
    system.visualize_results(results)
    
    # Test predictions on new texts
    print("Testing predictions on new texts:\n")
    
    test_texts = [
        "This product is amazing! I love it.",
        "Terrible quality, very disappointed.",
        "Best experience ever!",
        "Waste of money, completely useless."
    ]
    
    best_model = models['Logistic Regression']
    for text in test_texts:
        pred, conf = system.predict_sentiment(best_model, system.tfidf_vectorizer, text)
        sentiment = "Positive" if pred == 1 else "Negative"
        print(f"  Text: '{text}'")
        print(f"  Prediction: {sentiment} (confidence: {conf:.2%})\n")
    
    # Generate report
    system.generate_report()
    
    print("\n✓ Sentiment Analysis System Completed Successfully!")
    print("Generated files:")
    print("  - 01_feature_importance.png")
    print("  - 02_model_comparison.png")
    print("  - 03_confusion_matrices.png")


if __name__ == "__main__":
    main()
