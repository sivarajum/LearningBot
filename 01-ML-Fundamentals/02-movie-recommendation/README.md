# Movie Recommendation System - Collaborative Filtering

## Overview
This project implements a movie recommendation system using collaborative filtering techniques. It demonstrates three different approaches: user-based filtering, item-based filtering, and matrix factorization.

## Problem Statement
**Cold-Start Problem**: How to recommend movies when:
- New users have no/few ratings
- New movies have no/few ratings
- The user-item matrix is very sparse (>95% missing)

## Collaborative Filtering Approaches

### 1. User-Based Collaborative Filtering
**Idea**: "If users A and B rated movies similarly, recommend A's favorite movies to B"

**Steps**:
1. Find users with similar rating patterns
2. Identify movies highly rated by similar users
3. Recommend movies the target user hasn't seen

**Formula**:
```
Recommendation_score = Σ(similarity(user_i, target_user) × rating(user_i, movie_j))
```

**Advantages**:
- Intuitive and interpretable
- Can capture diverse user preferences
- Works well with enough user data

**Disadvantages**:
- Scales poorly with many users (O(n²) similarity computation)
- Sparsity: Users rate few movies
- Cold-start problem for new users

### 2. Item-Based Collaborative Filtering
**Idea**: "Recommend movies similar to ones the user liked"

**Steps**:
1. Calculate movie-movie similarity (how similarly rated)
2. For movies user rated highly, find similar unwatched movies
3. Recommend based on similarity and user ratings

**Formula**:
```
Recommendation_score = Σ(rating(user, movie_i) × similarity(movie_i, movie_j))
```

**Advantages**:
- More stable over time (movies don't change as fast as users)
- Better for sparsity than user-based
- Efficient for large user bases

**Disadvantages**:
- Requires sufficient movie ratings
- May create filter bubbles
- Struggles with new items

### 3. Matrix Factorization (SVD)
**Idea**: "Decompose user-item matrix into latent factors representing hidden features"

**Formula**:
```
R(user, movie) ≈ U × Σ × V^T

where:
- R: original rating matrix
- U: user latent factors
- V: movie latent factors
- Σ: singular values (importance weights)
```

**Process**:
1. Decompose user-item matrix using SVD
2. Multiply factors to get predicted ratings
3. Recommend movies with highest predicted ratings

**Advantages**:
- Handles sparsity well
- Discovers latent patterns
- Better generalization
- Computationally efficient

**Disadvantages**:
- Less interpretable ("what do factors mean?")
- Requires tuning number of factors
- Still faces cold-start problem

## Project Structure
```
02-movie-recommendation/
├── recommendation_system.py        # Main implementation
├── movie_recommendation.ipynb      # Interactive notebook
├── README.md                       # This file
└── [output plots]
    ├── 01_data_exploration.png
    └── 02_recommendations_comparison.png
```

## Dataset

### Characteristics
- **Users**: 50
- **Movies**: 30
- **Sparsity**: ~75% (most users haven't rated most movies)
- **Ratings**: 1-5 stars
- **Total Ratings**: ~375

### Statistics
- Average ratings per user: ~7.5
- Average ratings per movie: ~12.5
- Most users rate between 5-15 movies

## Implementation Details

### Similarity Metrics

#### Cosine Similarity
```python
similarity = (A · B) / (||A|| × ||B||)
# Measures angle between vectors
# Range: -1 to 1 (higher = more similar)
```

#### Euclidean Distance
```python
distance = sqrt(Σ(a_i - b_i)²)
# Measures straight-line distance
# Lower = more similar
```

## Key Algorithms

### 1. User-Based CF Implementation
```python
def user_based_filtering(user_idx, n_recommendations=5):
    # 1. Calculate user-user similarities
    similarities = cosine_similarity(ratings_matrix[user_idx],
                                     all_user_ratings)

    # 2. Get movies rated by similar users
    similar_users = argsort(similarities)[::-1][:10]

    # 3. Aggregate ratings from similar users
    recommendations = {}
    for movie in all_movies:
        if user_not_watched(movie):
            score = sum(similarity[user] * rating[user][movie]
                       for user in similar_users)
            recommendations[movie] = score

    # 4. Return top recommendations
    return top_k(recommendations, k=5)
```

### 2. Item-Based CF Implementation
```python
def item_based_filtering(user_idx, n_recommendations=5):
    # 1. Calculate item-item similarities
    item_similarities = cosine_similarity(ratings_matrix.T,
                                         ratings_matrix.T)

    # 2. Get movies user rated
    user_movies = movies_rated_by(user_idx)

    # 3. Find similar unwatched movies
    recommendations = {}
    for movie_watched in user_movies:
        for movie_candidate in all_movies:
            if not user_watched(movie_candidate):
                similarity = item_similarities[movie_watched][movie_candidate]
                rating = ratings[user_idx][movie_watched]
                recommendations[movie_candidate] += rating * similarity

    # 4. Return top recommendations
    return top_k(recommendations, k=5)
```

### 3. SVD Implementation
```python
def matrix_factorization(n_factors=10):
    # 1. Fill missing values with mean
    R_filled = ratings_matrix.copy()
    R_filled[R_filled == 0] = mean_rating

    # 2. SVD decomposition
    U, sigma, Vt = svds(R_filled, k=n_factors)

    # 3. Reconstruct predictions
    predicted_ratings = U @ np.diag(sigma) @ Vt

    # 4. Clip to valid range [1, 5]
    predicted_ratings = np.clip(predicted_ratings, 1, 5)

    return predicted_ratings
```

## Cold-Start Problem Solutions

### For New Users (Few Ratings)
```python
def handle_new_user(new_user_ratings, n_recommendations=5):
    if len(new_user_ratings) < 2:
        # Show most popular movies
        return get_popular_movies()
    else:
        # Find similar users and recommend
        similar_users = find_similar_users(new_user_ratings)
        return aggregate_recommendations(similar_users)
```

### For New Movies (No Ratings)
```python
def recommend_new_movie(movie_features):
    # Use content-based filtering
    # Find similar movies and check if users liked them
    similar_movies = find_similar_movies(movie_features)
    popularity = estimate_popularity(similar_movies)
    return popularity
```

## Evaluation Metrics

### Root Mean Square Error (RMSE)
```
RMSE = sqrt(Σ(predicted - actual)² / n)

Lower is better. Interpretation:
- RMSE < 0.5: Excellent predictions
- RMSE 0.5-1.0: Good predictions
- RMSE > 1.5: Poor predictions
```

### Mean Absolute Error (MAE)
```
MAE = Σ|predicted - actual| / n

Average prediction error in rating points:
- MAE < 0.5: Excellent
- MAE < 1.0: Good
```

## Quick Start

### Run Python Script
```bash
python recommendation_system.py
```

### Run Jupyter Notebook
```bash
jupyter notebook movie_recommendation.ipynb
```

## Feature Highlights

✓ Synthetic realistic movie ratings data
✓ Three different recommendation approaches
✓ Comparison of different methods
✓ Cold-start problem handling
✓ Multiple similarity metrics
✓ Performance visualization
✓ Easy to adapt for real datasets

## Real-World Application

### Using Real MovieLens Dataset
```python
import pandas as pd

# Load MovieLens 100K dataset
ratings = pd.read_csv('ml-100k/u.data', sep='\t',
                      names=['user_id', 'movie_id', 'rating', 'timestamp'])

# Create user-item matrix
user_item_matrix = ratings.pivot_table(
    values='rating',
    index='user_id',
    columns='movie_id'
)

# Apply same algorithms
recommendations = matrix_factorization(user_item_matrix, n_factors=20)
```

## Comparing the Approaches

| Aspect | User-Based | Item-Based | SVD |
|--------|-----------|-----------|-----|
| **Scalability** | O(users²) | O(items²) | O(users × items × k) |
| **Sparsity Handling** | Moderate | Good | Excellent |
| **Interpretability** | High | High | Low |
| **Latency** | High | Medium | Low |
| **Cold-Start** | Poor | Poor | Poor |
| **Filter Bubble** | Yes | Yes | No |
| **Data Needed** | Much | Some | Some |
| **Best For** | Small user base | Large user base | Large, sparse data |

## Performance Tips

### Optimization
```python
# 1. Use sparse matrices for large datasets
from scipy.sparse import csr_matrix
R_sparse = csr_matrix(ratings_matrix)

# 2. Parallel computation
from sklearn.preprocessing import normalize
similarities = cosine_similarity(R_sparse, n_jobs=-1)

# 3. Reduce number of factors
# Use 20-50 factors instead of 100+
```

### Speed Comparison
- User-Based: ~5 seconds for 1000 users/500 movies
- Item-Based: ~1 second (items usually << users)
- SVD: ~0.1 seconds for prediction

## Hybrid Approaches

Combine multiple methods for better results:

```python
def hybrid_recommendation(user_idx, weights=None):
    """Combine user-based, item-based, and SVD"""

    if weights is None:
        weights = {'user_based': 0.3, 'item_based': 0.4, 'svd': 0.3}

    # Get recommendations from each method
    user_based = user_based_filtering(user_idx)
    item_based = item_based_filtering(user_idx)
    svd_based = get_svd_recommendations(user_idx)

    # Weighted combination
    final = (weights['user_based'] * user_based +
             weights['item_based'] * item_based +
             weights['svd'] * svd_based)

    return final
```

## A/B Testing

Evaluate recommendation quality:

```python
def evaluate_recommendations(model, test_ratings):
    """A/B test with offline metrics"""

    # Precision@k: Of top-k recommendations, how many did user like?
    # Recall@k: Of user's liked items, how many were in top-k?
    # NDCG: Normalized Discounted Cumulative Gain (ranking quality)

    precision = calculate_precision_at_k(model, test_ratings, k=5)
    recall = calculate_recall_at_k(model, test_ratings, k=5)
    ndcg = calculate_ndcg(model, test_ratings, k=5)

    return {'precision': precision, 'recall': recall, 'ndcg': ndcg}
```

## Common Issues and Solutions

### Issue: Recommendations are all the same
**Cause**: Not enough user diversity
**Solution**: Add diversity objective or use hybrid approach

### Issue: New users get poor recommendations
**Cause**: Cold-start problem
**Solution**: Use content-based features or explicit rating collection

### Issue: Slow recommendations
**Cause**: Too many factors or large dataset
**Solution**: Reduce factors, use sparse matrices, pre-compute similarities

### Issue: Outdated recommendations
**Cause**: Not re-training frequently
**Solution**: Incremental learning or scheduled re-training

## Files Generated

- **01_data_exploration.png**: Dataset statistics and visualizations
- **02_recommendations_comparison.png**: Comparison of three recommendation methods

## Learning Outcomes

After completing this project, you should understand:

✓ What collaborative filtering is
✓ User-based vs item-based approaches
✓ Matrix factorization and SVD
✓ Why sparsity is a problem
✓ Cold-start problem and solutions
✓ Evaluation metrics (RMSE, MAE)
✓ Similarity metrics (cosine, Euclidean)
✓ How recommendation systems work in practice
✓ Trade-offs between approaches

## Next Steps

1. **Real Dataset**: Use MovieLens or Netflix data
2. **Deep Learning**: Implement Neural Collaborative Filtering
3. **Content-Based**: Add movie features (genre, director, cast)
4. **Context-Aware**: Include time, location, user context
5. **Explainability**: Why was this movie recommended?

## References

- Netflix Prize Blog: https://blog.netflix.com/tag/netflix-prize/
- MovieLens Dataset: https://grouplens.org/datasets/movielens/
- "Recommender Systems Handbook" - Ricci, Rokach, Shapira
- Matrix Factorization: https://arxiv.org/abs/1206.3268

---

**Difficulty**: Intermediate | **Time**: 3-4 hours | **Prerequisites**: Linear algebra basics, Python
