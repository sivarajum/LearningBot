# BigQuery ML Interview Questions and Answers

## Beginner Level Questions

### 1. What is BigQuery ML and why is it useful?

**Answer:**
BigQuery ML is a machine learning service integrated into Google BigQuery that allows users to create and execute ML models using SQL queries. It's useful because:

- **Democratizes ML**: Enables data analysts and SQL users to build ML models without programming expertise
- **No Data Movement**: Train models directly on BigQuery data without exporting
- **Serverless**: No infrastructure management required
- **Cost-Effective**: Pay only for BigQuery compute resources used
- **Fast Iteration**: Rapid prototyping and model development

BigQuery ML brings machine learning capabilities to SQL users, making ML accessible to a broader audience.

### 2. What are the main components of BigQuery ML?

**Answer:**
The main components include:

- **Models**: ML models stored as BigQuery objects
- **Training Data**: BigQuery tables used for model training
- **ML Functions**: SQL functions like ML.PREDICT(), ML.EVALUATE()
- **Model Types**: Linear regression, logistic regression, DNN, etc.
- **Evaluation Metrics**: Built-in metrics for model assessment
- **Feature Engineering**: SQL-based feature creation and transformation

These components work together to provide end-to-end ML capabilities within BigQuery.

### 3. How do you create a simple linear regression model in BigQuery ML?

**Answer:**
You create models using the CREATE MODEL statement:

**Basic Syntax:**
```sql
CREATE OR REPLACE MODEL `project.dataset.model_name`
OPTIONS(
  model_type='linear_reg',
  input_label_cols=['target_column']
) AS
SELECT
  feature1,
  feature2,
  target_column
FROM `project.dataset.training_table`;
```

**Example:**
```sql
CREATE OR REPLACE MODEL `ecommerce.sales_prediction`
OPTIONS(
  model_type='linear_reg',
  input_label_cols=['sales_amount']
) AS
SELECT
  marketing_spend,
  season,
  sales_amount
FROM `ecommerce.historical_sales`;
```

This creates a linear regression model to predict sales based on marketing spend and season.

## Intermediate Level Questions

### 4. What model types are supported in BigQuery ML?

**Answer:**
BigQuery ML supports various model types:

**Supervised Learning:**
- **Linear Regression** (`linear_reg`): Predict continuous values
- **Logistic Regression** (`logistic_reg`): Binary/multi-class classification
- **DNN Regressor** (`dnn_regressor`): Deep neural networks for regression
- **DNN Classifier** (`dnn_classifier`): Deep neural networks for classification
- **Boosted Trees** (`boosted_tree_regressor/classifier`): Ensemble methods

**Unsupervised Learning:**
- **K-Means** (`kmeans`): Clustering analysis
- **Autoencoder** (`autoencoder`): Dimensionality reduction

**Specialized Models:**
- **Matrix Factorization** (`matrix_factorization`): Recommendation systems
- **ARIMA/ARIMA_PLUS** (`arima_plus`): Time series forecasting

Each model type has specific use cases and configuration options.

### 5. How do you evaluate model performance in BigQuery ML?

**Answer:**
Model evaluation uses the ML.EVALUATE() function:

**Basic Evaluation:**
```sql
SELECT
  *
FROM ML.EVALUATE(MODEL `project.dataset.model_name`,
  (
    SELECT
      feature1,
      feature2,
      actual_label
    FROM `project.dataset.test_data`
  )
);
```

**Regression Metrics:**
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- R² (coefficient of determination)

**Classification Metrics:**
- Accuracy
- Precision
- Recall
- F1-Score
- Area Under ROC Curve (AUC)

**Custom Evaluation:**
```sql
-- Confusion matrix for classification
SELECT
  expected_label,
  predicted_label,
  COUNT(*) as count
FROM ML.PREDICT(MODEL `project.dataset.classifier`,
  (
    SELECT
      features,
      actual_label as expected_label
    FROM `project.dataset.test_set`
  )
)
GROUP BY expected_label, predicted_label;
```

### 6. How do you make predictions with BigQuery ML?

**Answer:**
Predictions use the ML.PREDICT() function:

**Batch Prediction:**
```sql
SELECT
  customer_id,
  predicted_label,
  predicted_probability
FROM ML.PREDICT(MODEL `project.dataset.churn_model`,
  (
    SELECT
      customer_id,
      tenure,
      monthly_charges,
      total_charges
    FROM `project.dataset.customer_data`
  )
);
```

**Real-time Prediction:**
- Export model to AI Platform
- Deploy as REST API endpoint
- Make HTTP requests for predictions

**Prediction with Confidence:**
```sql
-- For regression models
SELECT
  *,
  predicted_value - 1.96 * std_dev as lower_bound,
  predicted_value + 1.96 * std_dev as upper_bound
FROM ML.PREDICT(MODEL `project.dataset.regression_model`,
  (SELECT features FROM `project.dataset.new_data`)
);
```

### 7. What is feature engineering in BigQuery ML?

**Answer:**
Feature engineering creates meaningful input features from raw data:

**Numeric Transformations:**
```sql
SELECT
  -- Original features
  age,
  income,

  -- Engineered features
  LOG(income) as log_income,
  age * age as age_squared,
  CASE WHEN age > 65 THEN 1 ELSE 0 END as is_senior
FROM `dataset.customer_data`;
```

**Categorical Encoding:**
```sql
SELECT
  -- One-hot encoding
  CASE WHEN region = 'North' THEN 1 ELSE 0 END as region_north,
  CASE WHEN region = 'South' THEN 1 ELSE 0 END as region_south,
  CASE WHEN region = 'East' THEN 1 ELSE 0 END as region_east,
  CASE WHEN region = 'West' THEN 1 ELSE 0 END as region_west,

  -- Label encoding
  CASE
    WHEN education = 'High School' THEN 1
    WHEN education = 'Bachelor' THEN 2
    WHEN education = 'Master' THEN 3
    WHEN education = 'PhD' THEN 4
  END as education_level
FROM `dataset.customer_data`;
```

**Temporal Features:**
```sql
SELECT
  -- Time-based features
  EXTRACT(DAYOFWEEK FROM purchase_date) as day_of_week,
  EXTRACT(HOUR FROM purchase_date) as hour_of_day,
  EXTRACT(MONTH FROM purchase_date) as month,
  DATE_DIFF(CURRENT_DATE(), purchase_date, DAY) as days_since_purchase
FROM `dataset.purchase_data`;
```

### 8. How do you handle time series forecasting in BigQuery ML?

**Answer:**
Time series forecasting uses ARIMA models:

**Basic Time Series Model:**
```sql
CREATE OR REPLACE MODEL `project.dataset.sales_forecast`
OPTIONS(
  model_type='arima_plus',
  time_series_timestamp_col='date',
  time_series_data_col='sales',
  auto_arima=TRUE,
  data_frequency='DAILY'
) AS
SELECT
  date,
  sales
FROM `project.dataset.historical_sales`
ORDER BY date;
```

**Forecasting:**
```sql
SELECT
  forecast_timestamp,
  forecast_value,
  prediction_interval_lower_bound,
  prediction_interval_upper_bound,
  confidence_level
FROM ML.FORECAST(MODEL `project.dataset.sales_forecast`,
  STRUCT(30 AS horizon, 0.8 AS confidence_level)
);
```

**Advanced Options:**
- **Seasonality**: Handle daily, weekly, monthly patterns
- **Holidays**: Account for holiday effects
- **Multiple Series**: Forecast multiple related time series
- **Anomaly Detection**: Identify unusual patterns

### 9. What are the performance considerations for BigQuery ML?

**Answer:**
Performance depends on several factors:

**Data Size:**
- Models can handle billions of rows
- Training time scales with data size
- Consider sampling for very large datasets

**Model Complexity:**
- Simple models (linear regression) train faster
- Complex models (DNN) require more resources
- Use appropriate model types for your use case

**Query Optimization:**
```sql
-- Use partitioning for faster queries
CREATE TABLE `dataset.training_data_partitioned`
PARTITION BY DATE(timestamp)
CLUSTER BY feature_column
AS SELECT * FROM `dataset.raw_data`;

-- Use appropriate data types
SELECT
  CAST(age AS INT64) as age,
  CAST(income AS FLOAT64) as income
FROM `dataset.customer_data`;
```

**Cost Optimization:**
- Use flat-rate pricing for heavy usage
- Optimize queries to reduce slot usage
- Use appropriate model complexity

### 10. How do you implement recommendation systems with BigQuery ML?

**Answer:**
Recommendation systems use matrix factorization:

**Collaborative Filtering:**
```sql
CREATE OR REPLACE MODEL `project.dataset.movie_recommendations`
OPTIONS(
  model_type='matrix_factorization',
  input_label_cols=['rating'],
  user_col='user_id',
  item_col='movie_id',
  l2_reg=0.1
) AS
SELECT
  user_id,
  movie_id,
  rating
FROM `project.dataset.movie_ratings`;
```

**Generating Recommendations:**
```sql
-- Recommend movies for a user
SELECT
  *
FROM ML.RECOMMEND(MODEL `project.dataset.movie_recommendations`,
  (
    SELECT 123 as user_id  -- Specific user
    UNION ALL
    SELECT user_id FROM `project.dataset.all_users`  -- All users
  )
)
ORDER BY predicted_rating DESC
LIMIT 10;
```

**Evaluation:**
```sql
-- Calculate recommendation metrics
SELECT
  AVG(precision_at_5) as avg_precision,
  AVG(recall_at_5) as avg_recall
FROM (
  SELECT
    user_id,
    ML.RECOMMEND(MODEL `project.dataset.movie_recommendations`,
      (SELECT user_id)
    ) as recommendations
  FROM `project.dataset.test_users`
);
```

## Advanced Level Questions

### 11. How do you implement A/B testing with BigQuery ML?

**Answer:**
A/B testing compares model performance in production:

**Model Comparison:**
```sql
-- Compare two model versions
WITH model_a_predictions AS (
  SELECT
    customer_id,
    predicted_churn_prob as prob_a,
    actual_churn
  FROM ML.PREDICT(MODEL `project.dataset.churn_model_v1`,
    (SELECT * FROM `project.dataset.test_data`)
  )
),
model_b_predictions AS (
  SELECT
    customer_id,
    predicted_churn_prob as prob_b,
    actual_churn
  FROM ML.PREDICT(MODEL `project.dataset.churn_model_v2`,
    (SELECT * FROM `project.dataset.test_data`)
  )
)
SELECT
  AVG(CASE WHEN prob_a > 0.5 THEN 1 ELSE 0 END) as accuracy_a,
  AVG(CASE WHEN prob_b > 0.5 THEN 1 ELSE 0 END) as accuracy_b
FROM model_a_predictions a
JOIN model_b_predictions b ON a.customer_id = b.customer_id;
```

**Traffic Splitting:**
- Use AI Platform for online A/B testing
- Route percentage of traffic to different models
- Monitor business metrics and model performance
- Gradually roll out winning model

**Statistical Significance:**
```sql
-- Calculate statistical significance
SELECT
  model_version,
  AVG(conversion_rate) as mean_conversion,
  STDDEV(conversion_rate) as std_conversion,
  COUNT(*) as sample_size
FROM `project.dataset.ab_test_results`
GROUP BY model_version;
```

### 12. How do you handle model drift and retraining?

**Answer:**
Model drift requires continuous monitoring and retraining:

**Drift Detection:**
```sql
-- Monitor prediction distribution changes
CREATE OR REPLACE TABLE `project.dataset.prediction_monitoring`
AS
SELECT
  DATE(timestamp) as date,
  AVG(predicted_value) as avg_prediction,
  STDDEV(predicted_value) as std_prediction,
  COUNT(*) as prediction_count
FROM (
  SELECT
    timestamp,
    predicted_value
  FROM ML.PREDICT(MODEL `project.dataset.production_model`,
    (SELECT * FROM `project.dataset.daily_predictions`)
  )
)
GROUP BY DATE(timestamp);
```

**Automated Retraining:**
```sql
-- Retrain model with new data
CREATE OR REPLACE MODEL `project.dataset.churn_model_new`
OPTIONS(
  model_type='logistic_reg',
  input_label_cols=['churned']
) AS
SELECT
  features,
  churned
FROM `project.dataset.training_data`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY);
```

**Model Comparison and Deployment:**
```sql
-- Compare old vs new model performance
SELECT
  'old_model' as model_version,
  *
FROM ML.EVALUATE(MODEL `project.dataset.churn_model_old`,
  (SELECT * FROM `project.dataset.validation_data`)
)
UNION ALL
SELECT
  'new_model' as model_version,
  *
FROM ML.EVALUATE(MODEL `project.dataset.churn_model_new`,
  (SELECT * FROM `project.dataset.validation_data`)
);
```

### 13. What are the security considerations for BigQuery ML?

**Answer:**
Security encompasses data, models, and access:

**Data Security:**
- Column-level access controls
- Data masking for sensitive information
- Encryption at rest and in transit
- VPC Service Controls for data exfiltration prevention

**Model Security:**
```sql
-- Grant model access
GRANT `roles/bigquery.dataViewer`
ON MODEL `project.dataset.sensitive_model`
TO "user:analyst@example.com";
```

**Access Control:**
- IAM roles for BigQuery ML operations
- Service accounts for automated processes
- Audit logging for model access and predictions
- Row-level security for training data

**Compliance:**
- Support for HIPAA, PCI-DSS, and other regulations
- Data residency controls
- Model explainability for regulatory requirements
- Automated compliance reporting

### 14. How do you optimize costs in BigQuery ML?

**Answer:**
Cost optimization strategies:

**Query Optimization:**
```sql
-- Use sampling for large datasets
CREATE OR REPLACE MODEL `project.dataset.efficient_model`
OPTIONS(model_type='linear_reg', input_label_cols=['target'])
AS
SELECT
  features,
  target
FROM `project.dataset.large_table`
WHERE RAND() < 0.1;  -- 10% sample
```

**Model Optimization:**
- Choose simpler models when possible
- Use feature selection to reduce input dimensions
- Implement early stopping for iterative algorithms
- Use appropriate model types for your data size

**Storage Optimization:**
- Use partitioned tables for time-series data
- Implement data lifecycle policies
- Use appropriate data types to minimize storage

**Pricing Strategy:**
- **On-demand**: Pay per query for occasional use
- **Flat-rate**: Fixed monthly cost for heavy usage
- **Annual contracts**: Additional discounts for committed usage

### 15. How do you implement model explainability in BigQuery ML?

**Answer:**
Model explainability uses SHAP (SHapley Additive exPlanations):

**Feature Importance:**
```sql
SELECT
  *
FROM ML.EXPLAIN_PREDICT(MODEL `project.dataset.model_name`,
  (
    SELECT
      feature1,
      feature2,
      feature3
    FROM `project.dataset.inference_data`
  ),
  STRUCT(5 as top_k_features)
);
```

**Global Feature Importance:**
```sql
SELECT
  feature,
  SUM(attribution) as total_attribution
FROM (
  SELECT
    feature,
    attribution
  FROM ML.GLOBAL_EXPLAIN(MODEL `project.dataset.model_name`)
  WHERE feature IN ('feature1', 'feature2', 'feature3')
)
GROUP BY feature
ORDER BY total_attribution DESC;
```

**Visualization:**
- Use Looker for feature importance dashboards
- Create waterfall charts for individual predictions
- Implement partial dependence plots
- Generate feature contribution reports

**Regulatory Compliance:**
- Explainable AI for financial services
- Bias detection and mitigation
- Model validation for critical applications
- Audit trails for model decisions

### 16. What are the limitations of BigQuery ML?

**Answer:**
Understanding limitations helps set proper expectations:

**Model Limitations:**
- Limited to supported model types
- Maximum training time limits
- Memory constraints for very large models
- No custom loss functions (except for some models)

**Data Limitations:**
- Maximum 1000 features for most models
- Time series limited to single metric per model
- No streaming model updates
- Batch-oriented rather than real-time

**Performance Limitations:**
- Training time scales with data size
- Complex models require significant compute
- No GPU acceleration for training
- Limited hyperparameter optimization

**Operational Limitations:**
- No model versioning in BigQuery (use separate models)
- Limited model monitoring capabilities
- No automatic model retraining
- Manual model lifecycle management

### 17. How do you integrate BigQuery ML with other Google Cloud services?

**Answer:**
BigQuery ML integrates with the broader Google Cloud ecosystem:

**Vertex AI Integration:**
```sql
-- Export model to Vertex AI
EXPORT MODEL `project.dataset.bqml_model`
OPTIONS(
  uri='gs://bucket/models/*',
  job_id='export_bqml_model'
);

-- Then deploy in Vertex AI
gcloud ai models upload \
  --region=us-central1 \
  --display-name=bqml-model \
  --container-image-uri=gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-5:latest \
  --artifact-uri=gs://bucket/models/
```

**Looker Integration:**
- Create ML-based dashboards
- Use ML functions in LookML
- Implement predictive analytics
- Build interactive ML applications

**Dataflow Integration:**
```python
# Use BigQuery ML models in Dataflow
from google.cloud import bigquery_ml

def predict_churn(element):
    client = bigquery_ml.BigQueryMLHook()
    result = client.predict(
        model_name='project.dataset.churn_model',
        data=[element]
    )
    return result

# In pipeline
predictions = data | beam.Map(predict_churn)
```

**Cloud Functions Integration:**
```python
# Trigger ML predictions from Cloud Functions
def predict_sales(request):
    from google.cloud import bigquery

    client = bigquery.Client()
    query = """
    SELECT *
    FROM ML.PREDICT(MODEL `project.dataset.sales_model`,
      (SELECT features FROM `project.dataset.input_data`)
    )
    """

    results = client.query(query).result()
    return {"predictions": [dict(row) for row in results]}
```

### 18. How do you implement MLOps with BigQuery ML?

**Answer:**
MLOps practices for BigQuery ML:

**Version Control:**
```sql
-- Model versioning through naming
CREATE OR REPLACE MODEL `project.dataset.churn_model_v1_2_3`
OPTIONS(model_type='logistic_reg')
AS SELECT * FROM `project.dataset.training_v1_2_3`;

-- Model registry
INSERT INTO `project.dataset.model_registry`
VALUES (
  'churn_model',
  'v1.2.3',
  '2023-10-01',
  'Improved feature engineering',
  'gs://models/churn_v1_2_3/'
);
```

**CI/CD Pipeline:**
```yaml
# Cloud Build pipeline for ML
steps:
  - name: 'gcr.io/cloud-builders/bq'
    args: ['query', '--use_legacy_sql=false', 'CREATE OR REPLACE MODEL...']

  - name: 'gcr.io/cloud-builders/bq'
    args: ['query', '--use_legacy_sql=false', 'SELECT * FROM ML.EVALUATE...']

  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['ai', 'models', 'upload', '--region=us-central1', ...]
```

**Monitoring and Alerting:**
```sql
-- Model performance monitoring
CREATE OR REPLACE TABLE `project.dataset.model_performance`
AS
SELECT
  DATE(timestamp) as date,
  AVG(ABS(actual - predicted)) as mae,
  COUNT(*) as prediction_count
FROM (
  SELECT
    timestamp,
    actual_value as actual,
    predicted_value as predicted
  FROM `project.dataset.prediction_log`
)
GROUP BY DATE(timestamp);
```

**Automated Retraining:**
- Schedule regular model retraining
- Monitor model performance degradation
- Implement automated model deployment
- Rollback capabilities for failed deployments

### 19. What are the differences between BigQuery ML and other ML platforms?

**Answer:**
Comparison with other ML approaches:

**vs Traditional ML Frameworks:**
- **Accessibility**: SQL-based vs programming required
- **Data Movement**: No data export vs data transfer needed
- **Scalability**: BigQuery scale vs framework limitations
- **Integration**: Native BigQuery integration vs separate systems

**vs AutoML:**
- **Control**: Full control over features and parameters
- **Cost**: Pay for BigQuery usage vs AutoML pricing
- **Flexibility**: Custom feature engineering vs automated
- **Speed**: Faster iteration for SQL users

**vs Custom ML Models:**
- **Development Time**: Hours vs days/weeks
- **Maintenance**: Managed service vs custom infrastructure
- **Scalability**: Automatic scaling vs manual optimization
- **Cost**: Usage-based vs infrastructure costs

**vs Vertex AI Custom Training:**
- **Ease of Use**: SQL interface vs Python/code
- **Data Preparation**: SQL transformations vs data pipelines
- **Iteration Speed**: Rapid prototyping vs development cycles
- **Target Users**: Analysts vs data scientists

### 20. How do you troubleshoot BigQuery ML issues?

**Answer:**
Systematic troubleshooting approach:

**Training Issues:**
```sql
-- Check training job status
SELECT
  job_id,
  creation_time,
  end_time,
  state,
  error_message
FROM `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE job_type = 'CREATE MODEL'
ORDER BY creation_time DESC
LIMIT 10;
```

**Model Information:**
```sql
-- Get detailed model information
SELECT
  *
FROM ML.MODEL_INFO(MODEL `project.dataset.problematic_model`);
```

**Common Issues:**
- **Data Type Mismatches**: Ensure consistent data types
- **Null Values**: Handle missing data appropriately
- **Feature Scaling**: Normalize features for better performance
- **Class Imbalance**: Address unbalanced classification problems

**Performance Issues:**
```sql
-- Monitor query performance
SELECT
  job_id,
  query,
  total_bytes_processed,
  total_slot_ms,
  cache_hit
FROM `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE statement_type = 'CREATE MODEL'
ORDER BY total_slot_ms DESC;
```

**Prediction Issues:**
- Verify input data format matches training data
- Check for data drift between training and prediction
- Validate model is not corrupted or outdated
- Monitor prediction latency and error rates

## Scenario-Based Questions

### 21. How would you build a customer churn prediction model?

**Answer:**
End-to-end churn prediction implementation:

**Data Preparation:**
```sql
-- Feature engineering for churn prediction
CREATE OR REPLACE TABLE `project.dataset.churn_features`
AS
SELECT
  customer_id,
  -- Demographic features
  age,
  gender,
  tenure_months,

  -- Usage features
  monthly_charges,
  total_charges,
  num_support_tickets,

  -- Behavioral features
  days_since_last_login,
  avg_session_duration,
  num_products_used,

  -- Derived features
  total_charges / NULLIF(tenure_months, 0) as avg_monthly_spend,
  CASE WHEN num_support_tickets > 5 THEN 1 ELSE 0 END as high_support_user,

  -- Target
  CASE WHEN churn_date IS NOT NULL THEN 1 ELSE 0 END as churned
FROM `project.dataset.customer_raw_data`;
```

**Model Training:**
```sql
CREATE OR REPLACE MODEL `project.dataset.churn_model`
OPTIONS(
  model_type='logistic_reg',
  input_label_cols=['churned'],
  l2_reg=0.1,
  class_weights=[0.7, 0.3]  -- Handle class imbalance
) AS
SELECT
  * EXCEPT(customer_id)
FROM `project.dataset.churn_features`
WHERE customer_id IN (
  SELECT customer_id
  FROM `project.dataset.churn_features`
  ORDER BY RAND()
  LIMIT 80000  -- 80% for training
);
```

**Model Evaluation:**
```sql
-- Evaluate on test set
SELECT
  *
FROM ML.EVALUATE(MODEL `project.dataset.churn_model`,
  (
    SELECT * EXCEPT(customer_id)
    FROM `project.dataset.churn_features`
    WHERE customer_id NOT IN (
      SELECT customer_id
      FROM `project.dataset.churn_features`
      ORDER BY RAND()
      LIMIT 80000
    )
  )
);
```

**Production Deployment:**
```sql
-- Batch predictions for all customers
CREATE OR REPLACE TABLE `project.dataset.churn_predictions`
AS
SELECT
  customer_id,
  predicted_churned,
  predicted_churned_probs[OFFSET(1)] as churn_probability
FROM ML.PREDICT(MODEL `project.dataset.churn_model`,
  (
    SELECT * EXCEPT(churned)
    FROM `project.dataset.churn_features`
  )
);
```

### 22. How would you implement a recommendation system for an e-commerce site?

**Answer:**
Building a product recommendation system:

**Data Preparation:**
```sql
-- Prepare user-item interaction data
CREATE OR REPLACE TABLE `project.dataset.user_item_interactions`
AS
SELECT
  user_id,
  product_id,
  SUM(quantity) as total_quantity,
  AVG(rating) as avg_rating,
  COUNT(*) as interaction_count,
  MAX(purchase_date) as last_purchase_date
FROM `project.dataset.purchase_history`
GROUP BY user_id, product_id;
```

**Matrix Factorization Model:**
```sql
CREATE OR REPLACE MODEL `project.dataset.product_recommendations`
OPTIONS(
  model_type='matrix_factorization',
  input_label_cols=['avg_rating'],
  user_col='user_id',
  item_col='product_id',
  l2_reg=0.2,
  num_factors=50
) AS
SELECT
  user_id,
  product_id,
  avg_rating
FROM `project.dataset.user_item_interactions`
WHERE interaction_count >= 2;  -- Filter sparse interactions
```

**Generating Recommendations:**
```sql
-- Get top 10 recommendations for each user
CREATE OR REPLACE TABLE `project.dataset.user_recommendations`
AS
SELECT
  user_id,
  product_id,
  predicted_rating
FROM ML.RECOMMEND(MODEL `project.dataset.product_recommendations`)
WHERE user_id IN (SELECT DISTINCT user_id FROM `project.dataset.active_users`)
ORDER BY user_id, predicted_rating DESC;
```

**Evaluation:**
```sql
-- Calculate precision@K
WITH user_test_ratings AS (
  SELECT
    user_id,
    product_id,
    avg_rating
  FROM `project.dataset.user_item_interactions`
  WHERE purchase_date >= '2023-01-01'  -- Test period
),
user_recommendations AS (
  SELECT
    user_id,
    ARRAY_AGG(product_id ORDER BY predicted_rating DESC LIMIT 10) as recommended_products
  FROM `project.dataset.user_recommendations`
  GROUP BY user_id
)
SELECT
  AVG(precision_at_10) as avg_precision_at_10
FROM (
  SELECT
    r.user_id,
    (SELECT COUNT(*)
     FROM UNNEST(r.recommended_products) as rec_product
     JOIN user_test_ratings t ON rec_product = t.product_id AND r.user_id = t.user_id
    ) / 10.0 as precision_at_10
  FROM user_recommendations r
);
```

### 23. How would you handle a production ML model that starts performing poorly?

**Answer:**
Model performance degradation response:

**Initial Assessment:**
```sql
-- Check recent prediction performance
SELECT
  DATE(timestamp) as date,
  AVG(ABS(actual_value - predicted_value)) as mae,
  COUNT(*) as prediction_count
FROM `project.dataset.prediction_log`
WHERE timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

**Data Drift Analysis:**
```sql
-- Compare training vs recent data distributions
WITH training_stats AS (
  SELECT
    AVG(feature1) as avg_feature1_train,
    STDDEV(feature1) as std_feature1_train,
    AVG(feature2) as avg_feature2_train,
    STDDEV(feature2) as std_feature2_train
  FROM `project.dataset.training_data`
),
recent_stats AS (
  SELECT
    AVG(feature1) as avg_feature1_recent,
    STDDEV(feature1) as std_feature1_recent,
    AVG(feature2) as avg_feature2_recent,
    STDDEV(feature2) as std_feature2_recent
  FROM `project.dataset.recent_predictions`
)
SELECT
  ABS(avg_feature1_train - avg_feature1_recent) / NULLIF(std_feature1_train, 0) as drift_feature1,
  ABS(avg_feature2_train - avg_feature2_recent) / NULLIF(std_feature2_train, 0) as drift_feature2
FROM training_stats, recent_stats;
```

**Model Retraining:**
```sql
-- Retrain with recent data
CREATE OR REPLACE MODEL `project.dataset.model_v2`
OPTIONS(
  model_type='linear_reg',
  input_label_cols=['target']
) AS
SELECT
  features,
  target
FROM `project.dataset.combined_data`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 180 DAY);
```

**A/B Testing:**
- Deploy new model to subset of traffic
- Monitor performance metrics
- Compare business outcomes
- Gradually roll out winning model

**Root Cause Analysis:**
- Check for changes in data collection
- Review feature engineering logic
- Analyze external factor changes
- Document findings and preventive measures

## Summary

BigQuery ML interview questions typically cover:
- Basic model creation and SQL syntax
- Model types and appropriate use cases
- Feature engineering and data preparation
- Model evaluation and performance metrics
- Prediction and inference patterns
- Advanced topics like time series and recommendations
- Production deployment and monitoring
- Cost optimization and scaling considerations
- Integration with other Google Cloud services

Focus on understanding how BigQuery ML democratizes machine learning through SQL, its integration with BigQuery's analytics capabilities, and best practices for operationalizing ML models in production environments.
