"""
Test suite for Iris Classification module
Tests cover data loading, preprocessing, model training, and evaluation
"""

import unittest
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import sys
sys.path.insert(0, '/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/01-iris-classification')

from iris_classifier import IrisClassificationPipeline


class TestIrisClassification(unittest.TestCase):
    """Test cases for Iris classification pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = IrisClassificationPipeline(random_state=42)
    
    def test_data_loading(self):
        """Test dataset loading"""
        self.pipeline.load_data()
        
        # Verify dataset loaded correctly
        self.assertEqual(self.pipeline.X.shape, (150, 4))
        self.assertEqual(len(self.pipeline.y), 150)
        self.assertEqual(len(self.pipeline.target_names), 3)
        self.assertEqual(len(self.pipeline.feature_names), 4)
    
    def test_data_exploration(self):
        """Test data exploration"""
        self.pipeline.load_data()
        self.pipeline.explore_data()
        
        # Verify feature statistics
        self.assertGreater(self.pipeline.X.mean(), 0)
        self.assertGreater(self.pipeline.X.std(), 0)
    
    def test_preprocessing(self):
        """Test data preprocessing"""
        self.pipeline.load_data()
        self.pipeline.preprocess_data(test_size=0.2)
        
        # Verify train-test split
        self.assertEqual(len(self.pipeline.X_train) + len(self.pipeline.X_test), 150)
        self.assertAlmostEqual(len(self.pipeline.X_test) / 150, 0.2, places=1)
        
        # Verify scaled data has mean ~0 and std ~1
        self.assertAlmostEqual(self.pipeline.X_train_scaled.mean(), 0, places=1)
        self.assertAlmostEqual(self.pipeline.X_train_scaled.std(), 1, places=1)
    
    def test_model_training(self):
        """Test model training"""
        self.pipeline.load_data()
        self.pipeline.preprocess_data()
        self.pipeline.train_models()
        
        # Verify all models are trained
        self.assertEqual(len(self.pipeline.models), 4)
        self.assertIn('Logistic Regression', self.pipeline.models)
        self.assertIn('Decision Tree', self.pipeline.models)
        self.assertIn('Random Forest', self.pipeline.models)
        self.assertIn('SVM', self.pipeline.models)
    
    def test_model_prediction(self):
        """Test model predictions"""
        self.pipeline.load_data()
        self.pipeline.preprocess_data()
        self.pipeline.train_models()
        
        # Make predictions
        X_test_scaled = self.pipeline.scaler.transform(self.pipeline.X_test)
        
        for model_name, model in self.pipeline.models.items():
            if model_name in ['Logistic Regression', 'SVM']:
                X_pred = X_test_scaled
            else:
                X_pred = self.pipeline.X_test
            
            predictions = model.predict(X_pred)
            
            # Verify predictions are valid class labels
            self.assertTrue(all(p in [0, 1, 2] for p in predictions))
            self.assertEqual(len(predictions), len(self.pipeline.y_test))
    
    def test_model_evaluation(self):
        """Test model evaluation"""
        self.pipeline.load_data()
        self.pipeline.preprocess_data()
        self.pipeline.train_models()
        self.pipeline.evaluate_models()
        
        # Verify all models are evaluated
        self.assertEqual(len(self.pipeline.results), 4)
        
        # Verify metrics are in valid range
        for model_name, result in self.pipeline.results.items():
            self.assertGreaterEqual(result['accuracy'], 0)
            self.assertLessEqual(result['accuracy'], 1)
            self.assertGreaterEqual(result['precision'], 0)
            self.assertLessEqual(result['precision'], 1)
            self.assertGreaterEqual(result['f1'], 0)
            self.assertLessEqual(result['f1'], 1)
    
    def test_accuracy_threshold(self):
        """Test that all models achieve >85% accuracy"""
        self.pipeline.load_data()
        self.pipeline.preprocess_data()
        self.pipeline.train_models()
        self.pipeline.evaluate_models()
        
        # Verify all models meet accuracy threshold
        for model_name, result in self.pipeline.results.items():
            self.assertGreater(
                result['accuracy'], 0.85,
                f"{model_name} accuracy {result['accuracy']:.2%} below 85% threshold"
            )
    
    def test_cross_validation(self):
        """Test cross-validation"""
        self.pipeline.load_data()
        self.pipeline.preprocess_data()
        self.pipeline.train_models()
        self.pipeline.cross_validation()
        
        # Cross-validation should be completed without errors
        # (tested through successful execution)
    
    def test_hyperparameter_tuning(self):
        """Test hyperparameter tuning"""
        self.pipeline.load_data()
        self.pipeline.preprocess_data()
        self.pipeline.train_models()
        self.pipeline.hyperparameter_tuning()
        
        # Models should be updated after tuning
        self.assertIsNotNone(self.pipeline.models['Random Forest'])
        self.assertIsNotNone(self.pipeline.models['SVM'])
    
    def test_pipeline_execution(self):
        """Test complete pipeline execution"""
        (self.pipeline
         .load_data()
         .explore_data()
         .preprocess_data()
         .train_models()
         .evaluate_models())
        
        # Verify pipeline completed successfully
        self.assertIsNotNone(self.pipeline.X_train)
        self.assertIsNotNone(self.pipeline.X_test)
        self.assertEqual(len(self.pipeline.models), 4)
        self.assertEqual(len(self.pipeline.results), 4)


class TestIrisData(unittest.TestCase):
    """Test Iris dataset properties"""
    
    def test_iris_dataset_shape(self):
        """Test Iris dataset shape"""
        iris = datasets.load_iris()
        self.assertEqual(iris.data.shape, (150, 4))
        self.assertEqual(len(iris.target), 150)
        self.assertEqual(len(iris.target_names), 3)
    
    def test_iris_dataset_values(self):
        """Test Iris dataset value ranges"""
        iris = datasets.load_iris()
        X = iris.data
        
        # Features should be in reasonable range (cm measurements)
        self.assertGreater(X.min(), 0)
        self.assertLess(X.max(), 100)
    
    def test_iris_class_balance(self):
        """Test Iris dataset is balanced"""
        iris = datasets.load_iris()
        unique, counts = np.unique(iris.target, return_counts=True)
        
        # All classes should have same count
        self.assertTrue(all(count == 50 for count in counts))


class TestModelComparison(unittest.TestCase):
    """Test model comparison and relative performance"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = IrisClassificationPipeline(random_state=42)
        (self.pipeline
         .load_data()
         .preprocess_data()
         .train_models()
         .evaluate_models())
    
    def test_models_ranked_by_accuracy(self):
        """Test models can be ranked by accuracy"""
        accuracies = {model: result['accuracy'] 
                     for model, result in self.pipeline.results.items()}
        
        sorted_models = sorted(accuracies.items(), key=lambda x: x[1], reverse=True)
        
        # Verify sorting worked
        for i in range(len(sorted_models) - 1):
            self.assertGreaterEqual(sorted_models[i][1], sorted_models[i+1][1])
    
    def test_best_model_identification(self):
        """Test identifying best model"""
        accuracies = {model: result['accuracy'] 
                     for model, result in self.pipeline.results.items()}
        
        best_model = max(accuracies, key=accuracies.get)
        
        # Best model should have highest accuracy
        self.assertIsNotNone(best_model)
        self.assertIn(best_model, ['Logistic Regression', 'Decision Tree', 
                                   'Random Forest', 'SVM'])


def run_tests(verbosity=2):
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestIrisClassification))
    suite.addTests(loader.loadTestsFromTestCase(TestIrisData))
    suite.addTests(loader.loadTestsFromTestCase(TestModelComparison))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    unittest.main(verbosity=2)
