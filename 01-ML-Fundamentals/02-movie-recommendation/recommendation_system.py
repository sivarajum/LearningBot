"""
Movie Recommendation System - Collaborative Filtering
This module implements user-based and item-based collaborative filtering
with matrix factorization (SVD) for movie recommendations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import cosine, euclidean
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class MovieRecommendationSystem:
    """
    Collaborative filtering system for movie recommendations.
    Supports user-based, item-based, and matrix factorization approaches.
    """
    
    def __init__(self, random_state=42):
        """Initialize the recommendation system."""
        self.random_state = random_state
        self.ratings_matrix = None
        self.user_item_matrix = None
        self.user_similarity = None
        self.item_similarity = None
        self.predictions = {}
        
    def create_sample_data(self, n_users=50, n_movies=30, sparsity=0.7):
        """
        Create synthetic movie ratings dataset.
        
        Parameters:
        -----------
        n_users : int
            Number of users
        n_movies : int
            Number of movies
        sparsity : float
            Sparsity level of the rating matrix (0-1)
        """
        print(f"Creating sample dataset: {n_users} users, {n_movies} movies...")
        
        np.random.seed(self.random_state)
        
        # Create sparse ratings matrix (1-5 stars)
        self.ratings_matrix = np.zeros((n_users, n_movies))
        
        # Fill with ratings with controlled sparsity
        for i in range(n_users):
            n_ratings = np.random.randint(5, 15)  # Each user rates 5-15 movies
            movie_indices = np.random.choice(n_movies, n_ratings, replace=False)
            for j in movie_indices:
                self.ratings_matrix[i, j] = np.random.randint(1, 6)  # Rating 1-5
        
        self.user_item_matrix = self.ratings_matrix.copy()
        
        # Movie names and user IDs
        self.movie_names = [f"Movie_{i+1}" for i in range(n_movies)]
        self.user_ids = [f"User_{i+1}" for i in range(n_users)]
        
        # Calculate sparsity
        actual_sparsity = np.sum(self.ratings_matrix == 0) / self.ratings_matrix.size
        
        print(f"Dataset created:")
        print(f"  Shape: {self.ratings_matrix.shape}")
        print(f"  Sparsity: {actual_sparsity:.2%}")
        print(f"  Average rating: {np.mean(self.ratings_matrix[self.ratings_matrix > 0]):.2f}")
        print(f"  Ratings range: 1-5\n")
        
        return self
    
    def explore_data(self):
        """Explore dataset characteristics."""
        print("Dataset Exploration:")
        
        # User statistics
        user_ratings_count = np.count_nonzero(self.ratings_matrix, axis=1)
        print(f"  Avg ratings per user: {user_ratings_count.mean():.1f}")
        print(f"  Min ratings per user: {user_ratings_count.min()}")
        print(f"  Max ratings per user: {user_ratings_count.max()}")
        
        # Movie statistics
        movie_ratings_count = np.count_nonzero(self.ratings_matrix, axis=0)
        print(f"  Avg ratings per movie: {movie_ratings_count.mean():.1f}")
        print(f"  Min ratings per movie: {movie_ratings_count.min()}")
        print(f"  Max ratings per movie: {movie_ratings_count.max()}")
        
        # Rating distribution
        ratings = self.ratings_matrix[self.ratings_matrix > 0]
        print(f"\n  Rating distribution:")
        for rating in range(1, 6):
            count = np.sum(ratings == rating)
            print(f"    {rating} stars: {count} ({count/len(ratings)*100:.1f}%)")
        
        print()
        return self
    
    def visualize_data(self):
        """Visualize the ratings matrix and statistics."""
        print("Creating visualization plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Ratings matrix heatmap (sample)
        sample_size = min(20, self.ratings_matrix.shape[0])
        sns.heatmap(self.ratings_matrix[:sample_size, :sample_size], 
                   annot=False, cmap='YlOrRd', ax=axes[0, 0], cbar_kws={'label': 'Rating'})
        axes[0, 0].set_title('Sample Ratings Matrix (20x20)')
        axes[0, 0].set_xlabel('Movies')
        axes[0, 0].set_ylabel('Users')
        
        # 2. Ratings per user
        user_ratings_count = np.count_nonzero(self.ratings_matrix, axis=1)
        axes[0, 1].hist(user_ratings_count, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
        axes[0, 1].set_xlabel('Number of Ratings')
        axes[0, 1].set_ylabel('Number of Users')
        axes[0, 1].set_title('Distribution of User Ratings')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Ratings per movie
        movie_ratings_count = np.count_nonzero(self.ratings_matrix, axis=0)
        axes[1, 0].hist(movie_ratings_count, bins=15, color='darkgreen', alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Number of Ratings')
        axes[1, 0].set_ylabel('Number of Movies')
        axes[1, 0].set_title('Distribution of Movie Ratings')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Rating value distribution
        ratings = self.ratings_matrix[self.ratings_matrix > 0]
        rating_counts = [np.sum(ratings == i) for i in range(1, 6)]
        axes[1, 1].bar([1, 2, 3, 4, 5], rating_counts, color='coral', edgecolor='black')
        axes[1, 1].set_xlabel('Rating Value')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Rating Value Distribution')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/02-movie-recommendation/01_data_exploration.png', dpi=300, bbox_inches='tight')
        print("Saved: 01_data_exploration.png\n")
        
        return self
    
    def user_based_collaborative_filtering(self, user_id_idx, n_recommendations=5):
        """
        Recommend movies using user-based collaborative filtering.
        
        Parameters:
        -----------
        user_id_idx : int
            Index of the target user
        n_recommendations : int
            Number of movies to recommend
        """
        print(f"Computing user-based collaborative filtering...")
        
        # Calculate user-user similarity using cosine similarity
        user_ratings = self.ratings_matrix[user_id_idx].reshape(1, -1)
        
        # Only compare with users who have rated at least one movie in common
        similarities = []
        for i in range(len(self.ratings_matrix)):
            if i == user_id_idx:
                similarities.append(0)
            else:
                # Find common rated movies
                common_movies = (self.ratings_matrix[user_id_idx] > 0) & (self.ratings_matrix[i] > 0)
                if np.sum(common_movies) > 0:
                    sim = cosine_similarity(
                        self.ratings_matrix[user_id_idx].reshape(1, -1),
                        self.ratings_matrix[i].reshape(1, -1)
                    )[0, 0]
                    similarities.append(sim)
                else:
                    similarities.append(0)
        
        similarities = np.array(similarities)
        
        # Get similar users (excluding target user)
        similar_user_indices = np.argsort(similarities)[::-1][:10]  # Top 10 similar users
        
        # Get recommendations from similar users
        user_watched = self.ratings_matrix[user_id_idx] > 0
        recommendations = np.zeros(self.ratings_matrix.shape[1])
        
        for sim_user_idx in similar_user_indices:
            if similarities[sim_user_idx] > 0:
                # Movies rated by similar user but not by target user
                for movie_idx in range(self.ratings_matrix.shape[1]):
                    if not user_watched[movie_idx] and self.ratings_matrix[sim_user_idx, movie_idx] > 0:
                        recommendations[movie_idx] += (
                            self.ratings_matrix[sim_user_idx, movie_idx] * similarities[sim_user_idx]
                        )
        
        # Get top n recommendations
        top_indices = np.argsort(recommendations)[::-1][:n_recommendations]
        
        print(f"User-based recommendations for {self.user_ids[user_id_idx]}:")
        for rank, idx in enumerate(top_indices, 1):
            print(f"  {rank}. {self.movie_names[idx]} (score: {recommendations[idx]:.2f})")
        
        print()
        return top_indices, recommendations
    
    def item_based_collaborative_filtering(self, user_id_idx, n_recommendations=5):
        """
        Recommend movies using item-based collaborative filtering.
        
        Parameters:
        -----------
        user_id_idx : int
            Index of the target user
        n_recommendations : int
            Number of movies to recommend
        """
        print(f"Computing item-based collaborative filtering...")
        
        # Calculate item-item similarity
        item_similarity = cosine_similarity(self.ratings_matrix.T)
        
        # Get movies rated by user
        user_movies = np.where(self.ratings_matrix[user_id_idx] > 0)[0]
        user_ratings = self.ratings_matrix[user_id_idx, user_movies]
        
        # Calculate weighted recommendations
        recommendations = np.zeros(self.ratings_matrix.shape[1])
        similarity_sum = np.zeros(self.ratings_matrix.shape[1])
        
        for rated_movie_idx, rating in zip(user_movies, user_ratings):
            # Find similar movies
            for movie_idx in range(self.ratings_matrix.shape[1]):
                if self.ratings_matrix[user_id_idx, movie_idx] == 0:  # Not yet rated
                    sim = item_similarity[rated_movie_idx, movie_idx]
                    recommendations[movie_idx] += rating * sim
                    similarity_sum[movie_idx] += abs(sim)
        
        # Normalize by similarity sum
        recommendations = np.divide(recommendations, similarity_sum + 1e-10)
        
        # Get top n recommendations
        top_indices = np.argsort(recommendations)[::-1][:n_recommendations]
        
        print(f"Item-based recommendations for {self.user_ids[user_id_idx]}:")
        for rank, idx in enumerate(top_indices, 1):
            print(f"  {rank}. {self.movie_names[idx]} (score: {recommendations[idx]:.2f})")
        
        print()
        return top_indices, recommendations
    
    def matrix_factorization_svd(self, n_factors=10):
        """
        Matrix factorization using Singular Value Decomposition (SVD).
        
        Parameters:
        -----------
        n_factors : int
            Number of latent factors
        """
        print(f"Performing SVD-based matrix factorization with {n_factors} factors...")
        
        # Handle missing values (zeros) by replacing with mean rating
        mean_rating = np.mean(self.ratings_matrix[self.ratings_matrix > 0])
        ratings_filled = self.ratings_matrix.copy()
        ratings_filled[ratings_filled == 0] = mean_rating
        
        # SVD decomposition
        U, sigma, Vt = svds(ratings_filled, k=n_factors)
        
        # Reconstruct predicted ratings
        sigma = np.diag(sigma)
        predicted_ratings = np.dot(np.dot(U, sigma), Vt)
        
        # Clip predictions to valid rating range
        predicted_ratings = np.clip(predicted_ratings, 1, 5)
        
        self.predictions['SVD'] = predicted_ratings
        
        # Calculate RMSE on known ratings
        known_ratings = self.ratings_matrix[self.ratings_matrix > 0]
        predicted_known = predicted_ratings[self.ratings_matrix > 0]
        rmse = np.sqrt(mean_squared_error(known_ratings, predicted_known))
        mae = mean_absolute_error(known_ratings, predicted_known)
        
        print(f"SVD Matrix Factorization completed:")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  Shape of U: {U.shape}")
        print(f"  Shape of Vt: {Vt.shape}\n")
        
        return predicted_ratings
    
    def get_recommendations_svd(self, user_id_idx, predicted_ratings, n_recommendations=5):
        """
        Get recommendations using SVD predictions.
        
        Parameters:
        -----------
        user_id_idx : int
            Index of the target user
        predicted_ratings : np.ndarray
            Predicted ratings from SVD
        n_recommendations : int
            Number of movies to recommend
        """
        user_watched = self.ratings_matrix[user_id_idx] > 0
        user_predictions = predicted_ratings[user_id_idx].copy()
        
        # Set watched movies to -inf to exclude them
        user_predictions[user_watched] = -np.inf
        
        # Get top recommendations
        top_indices = np.argsort(user_predictions)[::-1][:n_recommendations]
        
        print(f"SVD-based recommendations for {self.user_ids[user_id_idx]}:")
        for rank, idx in enumerate(top_indices, 1):
            print(f"  {rank}. {self.movie_names[idx]} (predicted rating: {user_predictions[idx]:.2f})")
        
        print()
        return top_indices
    
    def handle_cold_start(self, new_user_ratings, n_recommendations=5):
        """
        Handle cold-start problem for new users with few/no ratings.
        
        Parameters:
        -----------
        new_user_ratings : dict
            Dictionary of {movie_idx: rating} for new user
        n_recommendations : int
            Number of movies to recommend
        """
        print("Handling cold-start problem for new user...")
        
        if len(new_user_ratings) < 2:
            print("  Strategy: Recommend most popular movies")
            # Most popular movies (most rated)
            movie_popularity = np.count_nonzero(self.ratings_matrix, axis=0)
            top_indices = np.argsort(movie_popularity)[::-1][:n_recommendations]
        else:
            print(f"  Strategy: Find similar users based on {len(new_user_ratings)} ratings")
            # Find similar users
            # Create temporary user vector
            temp_vector = np.zeros(self.ratings_matrix.shape[1])
            for movie_idx, rating in new_user_ratings.items():
                temp_vector[movie_idx] = rating
            
            # Find similar users
            similarities = []
            for i in range(len(self.ratings_matrix)):
                if np.sum(self.ratings_matrix[i] > 0) > 0:
                    sim = cosine_similarity(temp_vector.reshape(1, -1), 
                                           self.ratings_matrix[i].reshape(1, -1))[0, 0]
                    similarities.append(sim)
                else:
                    similarities.append(0)
            
            similarities = np.array(similarities)
            similar_user_indices = np.argsort(similarities)[::-1][:5]
            
            # Get recommendations
            recommendations = np.zeros(self.ratings_matrix.shape[1])
            for movie_idx in new_user_ratings.keys():
                for sim_user_idx in similar_user_indices:
                    if similarities[sim_user_idx] > 0:
                        for j in range(self.ratings_matrix.shape[1]):
                            if j not in new_user_ratings and self.ratings_matrix[sim_user_idx, j] > 0:
                                recommendations[j] += self.ratings_matrix[sim_user_idx, j] * similarities[sim_user_idx]
            
            top_indices = np.argsort(recommendations)[::-1][:n_recommendations]
        
        print("Cold-start recommendations:")
        for rank, idx in enumerate(top_indices, 1):
            print(f"  {rank}. {self.movie_names[idx]}")
        
        print()
        return top_indices
    
    def visualize_recommendations(self, user_id_idx, user_based, item_based, svd_based):
        """Visualize recommendations from different methods."""
        print("Creating recommendation visualization...")
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        methods = ['User-Based', 'Item-Based', 'SVD-Based']
        recommendations_lists = [user_based, item_based, svd_based]
        
        for idx, (method, recs) in enumerate(zip(methods, recommendations_lists)):
            movie_labels = [self.movie_names[i] for i in recs]
            movie_indices = np.arange(len(recs))
            
            axes[idx].barh(movie_indices, [5] * len(recs), color=['gold', 'silver', '#CD7F32'][:len(recs)], alpha=0.7)
            axes[idx].set_yticks(movie_indices)
            axes[idx].set_yticklabels(movie_labels)
            axes[idx].set_xlabel('Recommendation Score')
            axes[idx].set_title(f'{method}\nRecommendations for {self.user_ids[user_id_idx]}')
            axes[idx].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig('/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals/02-movie-recommendation/02_recommendations_comparison.png', dpi=300, bbox_inches='tight')
        print("Saved: 02_recommendations_comparison.png\n")
        
        return self
    
    def generate_report(self):
        """Generate comprehensive report."""
        print("\n" + "="*80)
        print("MOVIE RECOMMENDATION SYSTEM - REPORT")
        print("="*80 + "\n")
        
        print(f"Dataset Statistics:")
        print(f"  Users: {self.ratings_matrix.shape[0]}")
        print(f"  Movies: {self.ratings_matrix.shape[1]}")
        print(f"  Total Ratings: {np.count_nonzero(self.ratings_matrix)}")
        print(f"  Sparsity: {np.sum(self.ratings_matrix == 0) / self.ratings_matrix.size:.2%}")
        
        print(f"\nCollaborative Filtering Methods Implemented:")
        print(f"  ✓ User-Based Filtering")
        print(f"  ✓ Item-Based Filtering")
        print(f"  ✓ Matrix Factorization (SVD)")
        print(f"  ✓ Cold-Start Problem Handling")
        
        print("\n" + "="*80)


def main():
    """Main execution function."""
    # Initialize system
    system = MovieRecommendationSystem()
    
    # Create and explore data
    (system
     .create_sample_data(n_users=50, n_movies=30, sparsity=0.75)
     .explore_data()
     .visualize_data())
    
    # Test different recommendation methods
    test_user_idx = 0
    
    # User-based CF
    user_recs, user_scores = system.user_based_collaborative_filtering(test_user_idx, n_recommendations=5)
    
    # Item-based CF
    item_recs, item_scores = system.item_based_collaborative_filtering(test_user_idx, n_recommendations=5)
    
    # Matrix factorization
    predicted = system.matrix_factorization_svd(n_factors=10)
    svd_recs = system.get_recommendations_svd(test_user_idx, predicted, n_recommendations=5)
    
    # Visualize recommendations
    system.visualize_recommendations(test_user_idx, user_recs, item_recs, svd_recs)
    
    # Test cold-start
    new_user_ratings = {0: 5, 5: 4, 10: 3}  # New user with 3 ratings
    cold_start_recs = system.handle_cold_start(new_user_ratings, n_recommendations=5)
    
    # Generate report
    system.generate_report()
    
    print("\n✓ Movie Recommendation System Completed Successfully!")
    print("Generated files:")
    print("  - 01_data_exploration.png")
    print("  - 02_recommendations_comparison.png")


if __name__ == "__main__":
    main()
