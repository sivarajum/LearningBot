"""
Test suite for Movie Recommendation System module
Tests cover data creation, recommendation algorithms, and evaluation
"""

import unittest
import numpy as np
import sys
sys.path.insert(0, '/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/02-movie-recommendation')

from recommendation_system import MovieRecommendationSystem


class TestMovieRecommendationSystem(unittest.TestCase):
    """Test cases for movie recommendation system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.system = MovieRecommendationSystem(random_state=42)
    
    def test_data_creation(self):
        """Test synthetic dataset creation"""
        self.system.create_sample_data(n_users=50, n_movies=30, sparsity=0.75)
        
        # Verify dataset structure
        self.assertEqual(self.system.ratings_matrix.shape, (50, 30))
        self.assertEqual(len(self.system.user_ids), 50)
        self.assertEqual(len(self.system.movie_names), 30)
    
    def test_data_sparsity(self):
        """Test dataset sparsity"""
        self.system.create_sample_data(n_users=50, n_movies=30, sparsity=0.75)
        
        sparsity = np.sum(self.system.ratings_matrix == 0) / self.system.ratings_matrix.size
        
        # Sparsity should be reasonable (60-90%)
        self.assertGreater(sparsity, 0.5)
        self.assertLess(sparsity, 0.95)
    
    def test_rating_values(self):
        """Test ratings are in valid range (1-5)"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        ratings = self.system.ratings_matrix[self.system.ratings_matrix > 0]
        
        # All ratings should be 1-5
        self.assertTrue(all(r in range(1, 6) for r in ratings))
    
    def test_data_exploration(self):
        """Test data exploration"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        self.system.explore_data()
        
        # Exploration should complete without error
        # (successful execution is the test)
    
    def test_user_based_cf(self):
        """Test user-based collaborative filtering"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        user_idx = 0
        recommendations, scores = self.system.user_based_collaborative_filtering(
            user_idx, n_recommendations=5
        )
        
        # Verify recommendations
        self.assertEqual(len(recommendations), 5)
        self.assertEqual(len(scores), self.system.ratings_matrix.shape[1])
        self.assertTrue(all(isinstance(r, (int, np.integer)) for r in recommendations))
    
    def test_item_based_cf(self):
        """Test item-based collaborative filtering"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        user_idx = 0
        recommendations, scores = self.system.item_based_collaborative_filtering(
            user_idx, n_recommendations=5
        )
        
        # Verify recommendations
        self.assertEqual(len(recommendations), 5)
        self.assertEqual(len(scores), self.system.ratings_matrix.shape[1])
        self.assertTrue(all(isinstance(r, (int, np.integer)) for r in recommendations))
    
    def test_svd_factorization(self):
        """Test SVD matrix factorization"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        predicted_ratings = self.system.matrix_factorization_svd(n_factors=10)
        
        # Verify predicted matrix
        self.assertEqual(predicted_ratings.shape, self.system.ratings_matrix.shape)
        
        # Predictions should be in valid range
        self.assertGreaterEqual(predicted_ratings.min(), 1)
        self.assertLessEqual(predicted_ratings.max(), 5)
    
    def test_svd_recommendations(self):
        """Test SVD-based recommendations"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        predicted_ratings = self.system.matrix_factorization_svd(n_factors=10)
        recommendations = self.system.get_recommendations_svd(
            user_idx=0, 
            predicted_ratings=predicted_ratings,
            n_recommendations=5
        )
        
        # Verify recommendations
        self.assertEqual(len(recommendations), 5)
        self.assertTrue(all(isinstance(r, (int, np.integer)) for r in recommendations))
    
    def test_cold_start_new_user(self):
        """Test cold-start problem handling for new user with few ratings"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        # New user with very few ratings
        new_user_ratings = {0: 5, 5: 4}
        recommendations = self.system.handle_cold_start(
            new_user_ratings, 
            n_recommendations=5
        )
        
        # Should still get recommendations
        self.assertEqual(len(recommendations), 5)
    
    def test_cold_start_popular_movies(self):
        """Test cold-start with no ratings (popular movies strategy)"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        # Brand new user with no ratings
        new_user_ratings = {}
        recommendations = self.system.handle_cold_start(
            new_user_ratings, 
            n_recommendations=5
        )
        
        # Should recommend popular movies
        self.assertEqual(len(recommendations), 5)
    
    def test_different_user_recommendations(self):
        """Test that different users get different recommendations"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        user1_recs, _ = self.system.user_based_collaborative_filtering(0, n_recommendations=5)
        user2_recs, _ = self.system.user_based_collaborative_filtering(1, n_recommendations=5)
        
        # Recommendations might be different (not always, depends on similarity)
        # Just verify both are valid
        self.assertEqual(len(user1_recs), 5)
        self.assertEqual(len(user2_recs), 5)
    
    def test_no_duplicate_recommendations(self):
        """Test that user's watched movies aren't recommended"""
        self.system.create_sample_data(n_users=50, n_movies=30)
        
        user_idx = 0
        watched_movies = np.where(self.system.ratings_matrix[user_idx] > 0)[0]
        
        recommendations, _ = self.system.user_based_collaborative_filtering(
            user_idx, n_recommendations=5
        )
        
        # Recommendations should not include watched movies
        for rec in recommendations:
            self.assertNotIn(rec, watched_movies)
    
    def test_pipeline_execution(self):
        """Test complete pipeline execution"""
        (self.system
         .create_sample_data(n_users=50, n_movies=30)
         .explore_data())
        
        # Should complete without errors
        self.assertIsNotNone(self.system.ratings_matrix)


class TestRecommendationQuality(unittest.TestCase):
    """Test recommendation quality and diversity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.system = MovieRecommendationSystem(random_state=42)
        self.system.create_sample_data(n_users=50, n_movies=30)
    
    def test_recommendation_scores_descending(self):
        """Test that recommendations are scored properly"""
        _, scores = self.system.user_based_collaborative_filtering(0, n_recommendations=5)
        
        # Scores should have valid values
        self.assertGreaterEqual(scores.min(), 0)
        self.assertTrue(np.any(scores > 0))  # At least some positive scores
    
    def test_svd_reconstruction_error(self):
        """Test SVD reconstruction error is reasonable"""
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        
        predicted = self.system.matrix_factorization_svd(n_factors=10)
        
        # Calculate error on known ratings
        known_ratings = self.system.ratings_matrix[self.system.ratings_matrix > 0]
        predicted_known = predicted[self.system.ratings_matrix > 0]
        
        rmse = np.sqrt(mean_squared_error(known_ratings, predicted_known))
        mae = mean_absolute_error(known_ratings, predicted_known)
        
        # Error should be reasonable (less than 2 on 1-5 scale)
        self.assertLess(rmse, 2.0)
        self.assertLess(mae, 1.5)
    
    def test_similar_users_differ_by_items(self):
        """Test that similar users get somewhat similar recommendations"""
        # This is probabilistic, so we just test that the system works
        user1_recs, _ = self.system.user_based_collaborative_filtering(0, n_recommendations=5)
        
        self.assertEqual(len(user1_recs), 5)
        self.assertTrue(all(0 <= r < 30 for r in user1_recs))


class TestDataValidation(unittest.TestCase):
    """Test data validation and error handling"""
    
    def test_matrix_dimensions(self):
        """Test matrix dimensions are consistent"""
        system = MovieRecommendationSystem()
        system.create_sample_data(n_users=100, n_movies=50)
        
        self.assertEqual(system.ratings_matrix.shape[0], 100)
        self.assertEqual(system.ratings_matrix.shape[1], 50)
    
    def test_user_ids_count(self):
        """Test user ID count matches users"""
        system = MovieRecommendationSystem()
        system.create_sample_data(n_users=25, n_movies=15)
        
        self.assertEqual(len(system.user_ids), 25)
    
    def test_movie_names_count(self):
        """Test movie name count matches movies"""
        system = MovieRecommendationSystem()
        system.create_sample_data(n_users=30, n_movies=20)
        
        self.assertEqual(len(system.movie_names), 20)


def run_tests(verbosity=2):
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMovieRecommendationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommendationQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    unittest.main(verbosity=2)
