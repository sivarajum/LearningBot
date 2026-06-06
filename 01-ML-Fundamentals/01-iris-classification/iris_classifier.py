"""
Iris Classification - Supervised Learning with Multiple Classifiers
This module demonstrates supervised learning using the Iris dataset with multiple
classification algorithms and comprehensive evaluation metrics.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import datasets
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix, classification_report,
                              roc_auc_score, roc_curve, auc)
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class IrisClassificationPipeline:
    """
    A comprehensive pipeline for Iris dataset classification using multiple algorithms.
    """

    def __init__(self, random_state=42):
        """Initialize the pipeline with a random state for reproducibility."""
        self.random_state = random_state
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}

    def load_data(self):
        """Load the Iris dataset."""
        print("Loading Iris dataset...")
        iris = datasets.load_iris()
        self.X = iris.data
        self.y = iris.target
        self.feature_names = iris.feature_names
        self.target_names = iris.target_names
        print(f"Dataset shape: {self.X.shape}")
        print(f"Classes: {self.target_names}")
        print(f"Features: {self.feature_names}\n")
        return self

    def explore_data(self):
        """Explore the dataset characteristics."""
        print("Dataset Exploration:")
        print(f"Total samples: {len(self.X)}")
        print(f"Number of features: {self.X.shape[1]}")
        print(f"Number of classes: {len(np.unique(self.y))}")
        print(f"\nClass distribution:")
        unique, counts = np.unique(self.y, return_counts=True)
        for name, count in zip(self.target_names, counts):
            print(f"  {name}: {count} samples")

        # Create DataFrame for analysis
        df = pd.DataFrame(self.X, columns=self.feature_names)
        df['target'] = self.y
        print(f"\nStatistical Summary:\n{df.describe()}\n")
        return self

    def preprocess_data(self, test_size=0.2):
        """
        Preprocess data: split and normalize.

        Parameters:
        -----------
        test_size : float
            Proportion of test set (default 0.2 for 80/20 split)
        """
        print("Preprocessing data...")
        # Train-test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=self.random_state, stratify=self.y
        )

        # Normalize features using StandardScaler
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)

        print(f"Training set size: {len(self.X_train)}")
        print(f"Test set size: {len(self.X_test)}")
        print(f"Features normalized (mean=0, std=1)\n")
        return self

    def visualize_data(self):
        """Create data visualization plots."""
        print("Creating data visualization plots...")

        # Create DataFrame for visualization
        df = pd.DataFrame(self.X, columns=self.feature_names)
        df['Species'] = [self.target_names[i] for i in self.y]

        # 1. Pairplot
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # Sepal Length vs Sepal Width
        for i, species in enumerate(self.target_names):
            mask = self.y == i
            axes[0, 0].scatter(self.X[mask, 0], self.X[mask, 1],
                             label=species, alpha=0.7, s=50)
        axes[0, 0].set_xlabel('Sepal Length (cm)')
        axes[0, 0].set_ylabel('Sepal Width (cm)')
        axes[0, 0].set_title('Sepal Length vs Sepal Width')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Petal Length vs Petal Width
        for i, species in enumerate(self.target_names):
            mask = self.y == i
            axes[0, 1].scatter(self.X[mask, 2], self.X[mask, 3],
                             label=species, alpha=0.7, s=50)
        axes[0, 1].set_xlabel('Petal Length (cm)')
        axes[0, 1].set_ylabel('Petal Width (cm)')
        axes[0, 1].set_title('Petal Length vs Petal Width')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Feature distributions
        for i, feature in enumerate(self.feature_names[:2]):
            for j, species in enumerate(self.target_names):
                mask = self.y == j
                axes[1, 0].hist(self.X[mask, i], alpha=0.5, label=species, bins=15)
        axes[1, 0].set_xlabel('Sepal Length (cm)')
        axes[1, 0].set_title('Feature Distribution - Sepal')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        for i, feature in enumerate(self.feature_names[2:], start=2):
            for j, species in enumerate(self.target_names):
                mask = self.y == j
                axes[1, 1].hist(self.X[mask, i], alpha=0.5, label=species, bins=15)
        axes[1, 1].set_xlabel('Petal Length (cm)')
        axes[1, 1].set_title('Feature Distribution - Petal')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/01-iris-classification/01_data_exploration.png', dpi=300, bbox_inches='tight')
        print("Saved: 01_data_exploration.png\n")
        return self

    def train_models(self):
        """Train all classification models."""
        print("Training models...")

        # 1. Logistic Regression
        print("  - Training Logistic Regression...")
        lr = LogisticRegression(max_iter=200, random_state=self.random_state)
        lr.fit(self.X_train_scaled, self.y_train)
        self.models['Logistic Regression'] = lr

        # 2. Decision Tree
        print("  - Training Decision Tree...")
        dt = DecisionTreeClassifier(random_state=self.random_state, max_depth=5)
        dt.fit(self.X_train, self.y_train)
        self.models['Decision Tree'] = dt

        # 3. Random Forest
        print("  - Training Random Forest...")
        rf = RandomForestClassifier(n_estimators=100, random_state=self.random_state, max_depth=5)
        rf.fit(self.X_train, self.y_train)
        self.models['Random Forest'] = rf

        # 4. SVM
        print("  - Training SVM...")
        svm = SVC(kernel='rbf', random_state=self.random_state, probability=True)
        svm.fit(self.X_train_scaled, self.y_train)
        self.models['SVM'] = svm

        print("All models trained successfully!\n")
        return self

    def evaluate_models(self):
        """Evaluate all models using multiple metrics."""
        print("Evaluating models...\n")

        for model_name, model in self.models.items():
            # Make predictions
            if model_name in ['Logistic Regression', 'SVM']:
                y_pred = model.predict(self.X_test_scaled)
            else:
                y_pred = model.predict(self.X_test)

            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted')
            recall = recall_score(self.y_test, y_pred, average='weighted')
            f1 = f1_score(self.y_test, y_pred, average='weighted')

            self.results[model_name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'y_pred': y_pred,
                'confusion_matrix': confusion_matrix(self.y_test, y_pred)
            }

            print(f"{model_name}:")
            print(f"  Accuracy:  {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall:    {recall:.4f}")
            print(f"  F1-Score:  {f1:.4f}\n")

        return self

    def visualize_results(self):
        """Visualize model performance."""
        print("Creating performance visualizations...")

        # 1. Metrics comparison
        metrics_data = {model: [self.results[model][metric]
                               for metric in ['accuracy', 'precision', 'recall', 'f1']]
                       for model in self.models.keys()}

        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(self.models))
        width = 0.2

        for i, metric in enumerate(['accuracy', 'precision', 'recall', 'f1']):
            values = [self.results[model][metric] for model in self.models.keys()]
            ax.bar(x + i*width, values, width, label=metric.capitalize())

        ax.set_xlabel('Models')
        ax.set_ylabel('Score')
        ax.set_title('Model Performance Comparison')
        ax.set_xticks(x + 1.5*width)
        ax.set_xticklabels(self.models.keys())
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/01-iris-classification/02_metrics_comparison.png', dpi=300, bbox_inches='tight')
        print("Saved: 02_metrics_comparison.png")

        # 2. Confusion matrices
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()

        for idx, (model_name, model) in enumerate(self.models.items()):
            cm = self.results[model_name]['confusion_matrix']
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                       xticklabels=self.target_names, yticklabels=self.target_names)
            axes[idx].set_title(f'{model_name} Confusion Matrix')
            axes[idx].set_ylabel('True Label')
            axes[idx].set_xlabel('Predicted Label')

        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/01-iris-classification/03_confusion_matrices.png', dpi=300, bbox_inches='tight')
        print("Saved: 03_confusion_matrices.png\n")
        return self

    def hyperparameter_tuning(self):
        """Perform hyperparameter tuning for selected models."""
        print("Performing hyperparameter tuning...\n")

        # Random Forest tuning
        print("Tuning Random Forest parameters...")
        param_grid_rf = {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7, None],
            'min_samples_split': [2, 5]
        }

        rf = RandomForestClassifier(random_state=self.random_state)
        grid_search_rf = GridSearchCV(rf, param_grid_rf, cv=5, n_jobs=-1, verbose=0)
        grid_search_rf.fit(self.X_train, self.y_train)

        best_rf = grid_search_rf.best_estimator_
        y_pred_best_rf = best_rf.predict(self.X_test)
        accuracy_best_rf = accuracy_score(self.y_test, y_pred_best_rf)

        print(f"Best parameters for Random Forest: {grid_search_rf.best_params_}")
        print(f"Best accuracy: {accuracy_best_rf:.4f}\n")

        # SVM tuning
        print("Tuning SVM parameters...")
        param_grid_svm = {
            'C': [0.1, 1, 10],
            'kernel': ['rbf', 'poly'],
            'gamma': ['scale', 'auto', 0.001, 0.01]
        }

        svm = SVC(random_state=self.random_state, probability=True)
        grid_search_svm = GridSearchCV(svm, param_grid_svm, cv=5, n_jobs=-1, verbose=0)
        grid_search_svm.fit(self.X_train_scaled, self.y_train)

        best_svm = grid_search_svm.best_estimator_
        y_pred_best_svm = best_svm.predict(self.X_test_scaled)
        accuracy_best_svm = accuracy_score(self.y_test, y_pred_best_svm)

        print(f"Best parameters for SVM: {grid_search_svm.best_params_}")
        print(f"Best accuracy: {accuracy_best_svm:.4f}\n")

        # Update models with best versions
        self.models['Random Forest'] = best_rf
        self.models['SVM'] = best_svm

        return self

    def cross_validation(self):
        """Perform cross-validation for all models."""
        print("Performing 5-fold cross-validation...\n")

        for model_name, model in self.models.items():
            if model_name in ['Logistic Regression', 'SVM']:
                cv_scores = cross_val_score(model, self.X_train_scaled, self.y_train, cv=5)
            else:
                cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5)

            print(f"{model_name}:")
            print(f"  CV Scores: {cv_scores}")
            print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})\n")

        return self

    def generate_report(self):
        """Generate a comprehensive classification report."""
        print("\n" + "="*80)
        print("IRIS CLASSIFICATION - COMPREHENSIVE REPORT")
        print("="*80 + "\n")

        for model_name, model in self.models.items():
            if model_name in ['Logistic Regression', 'SVM']:
                y_pred = model.predict(self.X_test_scaled)
            else:
                y_pred = model.predict(self.X_test)

            print(f"\n{model_name.upper()}")
            print("-" * 80)
            print(classification_report(self.y_test, y_pred, target_names=self.target_names))

        print("="*80)
        return self


def main():
    """Main execution function."""
    # Initialize pipeline
    pipeline = IrisClassificationPipeline()

    # Execute pipeline
    (pipeline
     .load_data()
     .explore_data()
     .preprocess_data(test_size=0.2)
     .visualize_data()
     .train_models()
     .evaluate_models()
     .visualize_results()
     .hyperparameter_tuning()
     .cross_validation()
     .generate_report())

    print("\n✓ Iris Classification Pipeline Completed Successfully!")
    print("Generated files:")
    print("  - 01_data_exploration.png")
    print("  - 02_metrics_comparison.png")
    print("  - 03_confusion_matrices.png")


if __name__ == "__main__":
    main()
