# Intelligent Churn Prediction - Complete End-to-End Guide

This guide walks you through every piece of the churn prediction system, from raw data to a live dashboard. Each section explains **what** the code does, **why** it does it, and **how** to run it yourself.

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [Project Structure](#2-project-structure)
3. [Prerequisites - Setting Up Your Environment](#3-prerequisites---setting-up-your-environment)
4. [Step 1: Data Generation (src/data_generator.py)](#4-step-1-data-generation)
5. [Step 2: Feature Engineering (src/feature_engineering.py)](#5-step-2-feature-engineering)
6. [Step 3: Model Training (src/model.py)](#6-step-3-model-training)
7. [Step 4: The Pipeline - Tying It All Together (src/pipeline.py)](#7-step-4-the-pipeline)
8. [Step 5: REST API (src/api.py)](#8-step-5-rest-api)
9. [Step 6: Streamlit Dashboard (src/ui.py)](#9-step-6-streamlit-dashboard)
10. [Running the Full System](#10-running-the-full-system)
11. [Running with Docker](#11-running-with-docker)
12. [Testing the API Manually](#12-testing-the-api-manually)
13. [How Data Flows Through the System](#13-how-data-flows-through-the-system)
14. [Key Concepts Explained](#14-key-concepts-explained)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. What Is This Project?

**Customer churn** means a customer stops using your service. This project builds a machine learning system that:

1. Generates realistic fake customer data (10,000 customers)
2. Engineers meaningful features from that raw data
3. Trains an XGBoost model to predict which customers will churn
4. Serves predictions through a REST API
5. Displays everything on a visual dashboard

```
Raw Customer Data
       |
       v
Feature Engineering (create new useful columns)
       |
       v
Model Training (XGBoost learns patterns)
       |
       v
Save Model to Disk (model_bundle.joblib)
       |
       v
FastAPI loads the model and serves predictions
       |
       v
Streamlit dashboard calls the API and shows charts
```

---

## 2. Project Structure

```
POC-01-Intelligent-Churn-Prediction/
|
|-- main.py                  # Entry point - run everything from here
|-- requirements.txt         # Python packages needed
|-- Dockerfile               # Container build instructions
|-- docker-compose.yml       # Multi-container orchestration
|
|-- src/
|   |-- __init__.py          # Makes src/ a Python package
|   |-- data_generator.py    # Step 1: Create fake customer data
|   |-- feature_engineering.py  # Step 2: Transform raw data into features
|   |-- model.py             # Step 3: Train, save, load, and predict
|   |-- pipeline.py          # Step 4: Run steps 1-3 in sequence
|   |-- api.py               # Step 5: FastAPI REST endpoints
|   |-- ui.py                # Step 6: Streamlit visual dashboard
|
|-- data/
|   |-- customers.csv        # Generated customer dataset (created by pipeline)
|   |-- model_bundle.joblib  # Trained model + preprocessing artifacts (created by pipeline)
```

---

## 3. Prerequisites - Setting Up Your Environment

### Step 3.1: Make sure you have Python 3.10+

```bash
python --version
# Should print Python 3.10.x or higher
```

### Step 3.2: Navigate to the project directory

```bash
cd POCs/POC-01-Intelligent-Churn-Prediction
```

### Step 3.3: (Recommended) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows
```

### Step 3.4: Install dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package | What It Does |
|---------|-------------|
| `scikit-learn` | Machine learning utilities (train/test split, scaling, encoding, metrics) |
| `xgboost` | The gradient boosting model we train |
| `pandas` | Tabular data manipulation (DataFrames) |
| `numpy` | Numerical arrays and math |
| `fastapi` | Web framework for the REST API |
| `uvicorn` | ASGI server that runs FastAPI |
| `streamlit` | Web framework for the dashboard UI |
| `joblib` | Saves/loads Python objects to disk (our model) |
| `plotly` | Interactive charts in the dashboard |
| `python-multipart` | Handles file uploads in FastAPI |
| `requests` | HTTP client (UI calls the API with this) |

---

## 4. Step 1: Data Generation

**File:** `src/data_generator.py`

### What it does

Creates 10,000 fake but realistic customer records. Each customer has attributes that correlate with churn in ways that mirror real-world telecom data.

### The customer record

Each row in the generated CSV looks like this:

| Column | Example | Description |
|--------|---------|-------------|
| `customer_id` | CUST-00042 | Unique identifier |
| `tenure` | 15 | Months as a customer (1-72) |
| `monthly_charges` | 65.20 | Monthly bill amount ($20-$120) |
| `total_charges` | 4012.16 | Cumulative spend (tenure x monthly, with some noise) |
| `contract_type` | month-to-month | Contract term (month-to-month, one_year, two_year) |
| `payment_method` | electronic_check | How they pay (electronic_check, mailed_check, bank_transfer, credit_card) |
| `internet_service` | Fiber | Internet plan (DSL, Fiber, No) |
| `num_support_tickets` | 3 | Support tickets filed (0-10) |
| `churn` | 1 | Did they leave? (0=stayed, 1=churned) |

### How churn is simulated

The generator builds a **churn score** for each customer by adding up risk factors:

```
churn_score = 0

+ Short tenure (< 12 months)?       --> +1.5 points (high risk)
+ Month-to-month contract?          --> +1.2 points (high risk)
+ High monthly charges?             --> up to +1.0 point
+ Pays by electronic check?         --> +0.6 points
+ Has Fiber internet?               --> +0.5 points
+ Many support tickets?             --> +0.3 per ticket above average

+ Random noise                      --> makes it realistic, not deterministic
```

The score is converted to a probability using the **sigmoid function** (`1 / (1 + e^(-score))`), and the top 26% become churners. This produces a realistic ~26% churn rate.

### Run it standalone

```bash
python -m src.data_generator
```

**Output:**
```
Generated 10000 customers | Churn rate: 26.0% | Saved to data/customers.csv
```

### What gets created

`data/customers.csv` - a CSV file with 10,000 rows and 9 columns.

---

## 5. Step 2: Feature Engineering

**File:** `src/feature_engineering.py`

### What it does

Takes the raw customer DataFrame and transforms it into a numeric matrix that a machine learning model can understand. This involves three sub-steps:

1. **Create derived features** - new columns calculated from existing ones
2. **Encode categoricals** - convert text labels to numbers
3. **Scale everything** - normalize so no single feature dominates

### Sub-step 2a: Derived features (`create_derived_features`)

Four new columns are created from the raw data:

| New Feature | Formula | Why It Matters |
|-------------|---------|---------------|
| `avg_monthly_spend` | `total_charges / max(tenure, 1)` | Smooths out total_charges for customers with different tenures. A new customer with $500 total is different from a 5-year customer with $500 total. |
| `tenure_bucket` | Bins: 0-6=0, 7-24=1, 25-48=2, 49-73=3 | Groups tenure into "new / mid / loyal / veteran" categories. The model can learn that "new" customers behave very differently from "veteran" ones. |
| `support_ticket_rate` | `tickets / (tenure / 12)` | Tickets per year. A customer with 5 tickets in 1 month is very different from 5 tickets in 5 years. |
| `charge_tenure_ratio` | `monthly_charges * tenure` | Total spending intensity. Captures interaction between how much they pay and how long they've stayed. |

### Sub-step 2b: Encode categoricals (`encode_categoricals`)

ML models need numbers, not strings. `LabelEncoder` converts each text category to an integer:

```
contract_type:     month-to-month=0, one_year=1, two_year=2
payment_method:    bank_transfer=0, credit_card=1, electronic_check=2, mailed_check=3
internet_service:  DSL=0, Fiber=1, No=2
```

The fitted encoders are saved so we can apply the **exact same mapping** at prediction time.

### Sub-step 2c: Scale features (`StandardScaler`)

StandardScaler makes each feature have mean=0 and standard deviation=1:

```
scaled_value = (value - mean) / std_deviation
```

**Why?** Without scaling, `total_charges` (values like 5000) would dominate `num_support_tickets` (values like 3). Scaling puts them on equal footing.

### The final feature vector

After all transformations, each customer is represented by **11 numbers**:

```
["tenure", "monthly_charges", "total_charges",
 "contract_type", "payment_method", "internet_service",
 "num_support_tickets", "avg_monthly_spend",
 "tenure_bucket", "support_ticket_rate", "charge_tenure_ratio"]
```

### Training vs Inference

The `build_features` function has a `fit` parameter:

- **`fit=True`** (training): Learns the scaler means/stds and encoder mappings from the data
- **`fit=False`** (inference): Reuses previously learned scaler and encoders to transform new data identically

This is critical - if you scale training data one way and prediction data another way, the model gets garbage input.

---

## 6. Step 3: Model Training

**File:** `src/model.py`

### What it does

Trains an XGBoost classifier to predict churn (0 or 1) from the 11-feature vector, evaluates it, and provides functions to save/load/predict.

### The model: XGBoost (`XGBClassifier`)

XGBoost (eXtreme Gradient Boosting) builds an **ensemble of decision trees**. Each tree fixes the mistakes of the previous ones:

```
Tree 1: Makes rough predictions, gets some wrong
Tree 2: Focuses on what Tree 1 got wrong, improves
Tree 3: Focuses on what Trees 1+2 still get wrong
... (200 trees total)
Final: Combine all 200 trees for the answer
```

**Hyperparameters used:**

| Parameter | Value | What It Means |
|-----------|-------|--------------|
| `n_estimators` | 200 | Build 200 decision trees |
| `max_depth` | 5 | Each tree can be at most 5 levels deep (prevents overfitting) |
| `learning_rate` | 0.1 | Each tree only contributes 10% correction (slower but more stable) |
| `subsample` | 0.8 | Each tree sees 80% of the data (adds randomness, prevents overfitting) |
| `colsample_bytree` | 0.8 | Each tree sees 80% of the features |
| `eval_metric` | logloss | Optimizes for log-loss (good for probability estimation) |

### Train/test split

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y
)
```

- 80% of data for training, 20% held out for testing
- `stratify=y` ensures both sets have the same churn ratio (~26%)

### Evaluation metrics

After training, the model is evaluated on the 20% test set:

| Metric | What It Measures | Our Score |
|--------|-----------------|-----------|
| **Accuracy** | % of all predictions that are correct | ~86% |
| **Precision** | Of customers we predicted as churners, how many actually churned? | ~75% |
| **Recall** | Of all actual churners, how many did we catch? | ~71% |
| **F1 Score** | Harmonic mean of precision and recall (balanced measure) | ~73% |
| **CV Mean** | Average accuracy across 5 cross-validation folds | ~87% |

**Confusion matrix** shows the breakdown:

```
                    Predicted
                 No Churn | Churn
Actual No Churn [  TN     |  FP  ]
Actual Churn    [  FN     |  TP  ]
```

- TN (True Negative): Correctly predicted "stays"
- TP (True Positive): Correctly predicted "churns"
- FP (False Positive): Predicted "churn" but they stayed (false alarm)
- FN (False Negative): Predicted "stays" but they churned (missed!)

### Feature importance

XGBoost tells us which features matter most for predictions. The model returns a dict like:

```python
{"tenure_bucket": 0.42, "contract_type": 0.23, "tenure": 0.07, ...}
```

This means `tenure_bucket` alone drives 42% of the model's decisions.

### Saving the model (`save_model`)

Everything needed for future predictions is bundled into one file:

```python
bundle = {
    "model": trained_xgboost_model,
    "scaler": fitted_standard_scaler,
    "encoders": {"contract_type": encoder, "payment_method": encoder, ...},
    "feature_names": ["tenure", "monthly_charges", ...],
    "feature_importance": {"tenure_bucket": 0.42, ...},
    "metrics": {"accuracy": 0.86, ...}
}
joblib.dump(bundle, "data/model_bundle.joblib")
```

`joblib` serializes Python objects to disk. One file contains everything.

### Single prediction (`predict_single`)

For a single customer:

1. Run the feature vector through `model.predict_proba()` to get churn probability (0.0 to 1.0)
2. If probability >= 0.5, predict "churn"; otherwise "no_churn"
3. Find the top 3 features that contributed most to this specific prediction (importance weighted by feature value)

---

## 7. Step 4: The Pipeline

**File:** `src/pipeline.py`

### What it does

Runs Steps 1-3 in sequence with timing and progress output. This is the **training pipeline** - you run it once to produce a trained model.

### The four stages

```
[1/4] Generate synthetic customer data
      -> Calls data_generator.generate_customers()
      -> Saves to data/customers.csv
      -> Output: DataFrame with 10,000 rows

[2/4] Engineer features
      -> Calls feature_engineering.build_features(df, fit=True)
      -> Output: X (10000 x 11 matrix), y (10000 labels),
                 feature_names, artifacts (scaler + encoders)

[3/4] Train XGBoost model
      -> Calls model.train_model(X, y, feature_names)
      -> Output: trained model + all metrics

[4/4] Save everything
      -> Bundles model + scaler + encoders + metrics
      -> Calls model.save_model()
      -> Output: data/model_bundle.joblib
```

### Run it

```bash
python -m src.pipeline
```

**Expected output:**
```
============================================================
  Churn Prediction Pipeline
============================================================

[1/4] Generating synthetic customer data...
  -> 10000 customers | churn rate: 26.0% | saved to data/customers.csv
  -> Done in 0.0s

[2/4] Engineering features...
  -> 11 features: ['tenure', 'monthly_charges', ...]
  -> Done in 0.0s

[3/4] Training XGBoost model...
  -> Accuracy:  86.10%
  -> Precision: 74.59%
  -> Recall:    70.58%
  -> F1 Score:  72.53%
  -> CV Mean:   86.63%
  -> Done in 1.5s

[4/4] Saving model and artifacts...
  -> Model bundle saved to data/model_bundle.joblib
  -> Done in 0.0s

============================================================
  Pipeline completed in 1.6s
============================================================
```

### What gets created

After the pipeline runs, the `data/` folder contains:

```
data/
|-- customers.csv          # 10,000-row dataset (~800 KB)
|-- model_bundle.joblib    # Trained model bundle (~1.5 MB)
```

---

## 8. Step 5: REST API

**File:** `src/api.py`

### What it does

Wraps the trained model in a web API using FastAPI. Other applications (including our dashboard) call these HTTP endpoints to get predictions.

### Startup (lifespan)

When the API server starts, it:

1. Checks if `data/model_bundle.joblib` exists
2. If missing, automatically runs the full training pipeline
3. Loads the model bundle into memory (`MODEL_BUNDLE` dict)
4. The model stays in memory for fast predictions

### Endpoints

#### `GET /health`

Health check. Returns whether the model is loaded.

```json
{"status": "healthy", "model_loaded": true}
```

#### `GET /model-info`

Returns training metrics and feature importance.

```json
{
  "training_date": "2024-01-15T10:30:00+00:00",
  "metrics": {
    "accuracy": 0.861,
    "precision": 0.7459,
    "recall": 0.7058,
    "f1": 0.7253,
    "cv_mean": 0.8663,
    "confusion_matrix": [[1345, 135], [143, 377]]
  },
  "feature_importance": {
    "tenure_bucket": 0.4163,
    "contract_type": 0.226,
    ...
  }
}
```

#### `POST /predict`

Predict churn for a single customer. Send a JSON body:

```json
{
  "tenure": 12,
  "monthly_charges": 65.0,
  "contract_type": "month-to-month",
  "payment_method": "electronic_check",
  "internet_service": "Fiber",
  "num_support_tickets": 3
}
```

Response:

```json
{
  "churn_probability": 0.9768,
  "prediction": "churn",
  "top_contributing_features": [
    ["tenure_bucket", 0.4163],
    ["contract_type", 0.226],
    ["tenure", 0.066]
  ]
}
```

**What happens internally:**

1. `_prepare_input()` creates a DataFrame from the JSON
2. If `total_charges` is missing, it's calculated as `tenure * monthly_charges`
3. `build_features()` runs with `fit=False` using the saved scaler and encoders
4. `predict_single()` gets the probability and top features
5. Result is returned as JSON

#### `POST /batch-predict`

Upload a CSV file to predict churn for many customers at once.

```bash
curl -X POST http://localhost:8000/batch-predict \
  -F "file=@data/customers.csv"
```

Response:

```json
{
  "predictions": [
    {
      "churn_probability": 0.12,
      "prediction": "no_churn",
      "top_contributing_features": [...],
      "customer_id": "CUST-00000"
    },
    ...
  ],
  "total": 10000
}
```

### Run the API

```bash
python main.py api
```

The API starts at `http://localhost:8000`. FastAPI auto-generates interactive docs at `http://localhost:8000/docs` where you can try every endpoint in your browser.

---

## 9. Step 6: Streamlit Dashboard

**File:** `src/ui.py`

### What it does

A visual web dashboard that calls the API and displays:

1. **Model performance metrics** (accuracy, precision, recall, F1) as big number cards
2. **Feature importance chart** (horizontal bar chart showing which features matter most)
3. **Confusion matrix heatmap** (actual vs predicted labels)
4. **Interactive prediction form** (fill in customer attributes, click predict, see the result)

### How it connects to the API

```python
API_URL = os.getenv("API_URL", "http://localhost:8000")
```

- When running locally: calls `http://localhost:8000`
- When running in Docker: the env var overrides to `http://api:8000` (Docker service name)

### The dashboard layout

```
+------------------------------------------------------+
|  Customer Churn Prediction Dashboard                  |
+------------------------------------------------------+
|  Accuracy: 86.10%  |  Precision: 74.59%  |           |
|  Recall: 70.58%    |  F1 Score: 72.53%   |           |
+------------------------------------------------------+
|  Feature Importance (bar chart)                       |
|  [============================] tenure_bucket  0.42   |
|  [================]             contract_type  0.23   |
|  [=====]                        tenure         0.07   |
|  ...                                                  |
+------------------------------------------------------+
|  Confusion Matrix (heatmap)                           |
|             Predicted No | Predicted Yes              |
|  Actual No  [  1345     |    135      ]               |
|  Actual Yes [   143     |    377      ]               |
+------------------------------------------------------+
|  Predict Customer Churn                               |
|  Tenure: [====12====]   Contract: [month-to-month v]  |
|  Monthly: [===65.0===]  Payment:  [electronic_check]  |
|  Tickets: [====2=====]  Internet: [Fiber           v]  |
|  [Predict Churn Risk]                                 |
|                                                       |
|  >> Churn Risk: 97.7% (red)                           |
|  >> Top features: tenure_bucket, contract_type, ...   |
+------------------------------------------------------+
```

### Run the dashboard

First make sure the API is running (in another terminal or use `main.py all`):

```bash
# Terminal 1: Start the API
python main.py api

# Terminal 2: Start the dashboard
python main.py ui
```

The dashboard opens at `http://localhost:8501`.

---

## 10. Running the Full System

### Option A: Quick start (one command)

```bash
cd POCs/POC-01-Intelligent-Churn-Prediction
pip install -r requirements.txt
python main.py all
```

This:
1. Trains the model if it doesn't exist
2. Starts the API server on port 8000
3. Starts the Streamlit dashboard on port 8501

Open `http://localhost:8501` in your browser.

### Option B: Step by step

```bash
# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Run the training pipeline
python main.py pipeline

# Step 3: Start the API (leave this running)
python main.py api

# Step 4: In a NEW terminal, start the dashboard
python main.py ui
```

### Option C: Individual modules

```bash
# Generate data only
python -m src.data_generator

# Run the full training pipeline only
python -m src.pipeline

# Start just the API
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

# Start just the Streamlit UI
streamlit run src/ui.py --server.port 8501
```

### main.py commands reference

| Command | What It Does |
|---------|-------------|
| `python main.py pipeline` | Run the training pipeline (generate data + train + save) |
| `python main.py api` | Start the FastAPI server on port 8000 |
| `python main.py ui` | Start the Streamlit dashboard on port 8501 |
| `python main.py all` | Start both API and dashboard together |

---

## 11. Running with Docker

If you have Docker and Docker Compose installed, you can run the entire system in containers without installing Python dependencies on your machine.

### Build and start

```bash
cd POCs/POC-01-Intelligent-Churn-Prediction
docker-compose up --build
```

### What happens during build

1. Docker pulls `python:3.11-slim` base image
2. Installs all packages from `requirements.txt`
3. Copies `src/` and `data/` into the container
4. Runs `python -m src.pipeline` to train the model inside the image
5. Two containers start:
   - **api** (port 8000): FastAPI server
   - **ui** (port 8501): Streamlit dashboard (waits for API health check first)

### Access the services

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |

### Stop everything

```bash
docker-compose down
```

---

## 12. Testing the API Manually

### Using the interactive docs

Open `http://localhost:8000/docs` in your browser. FastAPI generates a Swagger UI where you can click "Try it out" on any endpoint.

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/model-info

# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "tenure": 3,
    "monthly_charges": 95.0,
    "contract_type": "month-to-month",
    "payment_method": "electronic_check",
    "internet_service": "Fiber",
    "num_support_tickets": 5
  }'

# Batch prediction (upload the generated CSV)
curl -X POST http://localhost:8000/batch-predict \
  -F "file=@data/customers.csv"
```

### Using Python

```python
import requests

# Single prediction
response = requests.post("http://localhost:8000/predict", json={
    "tenure": 3,
    "monthly_charges": 95.0,
    "contract_type": "month-to-month",
    "payment_method": "electronic_check",
    "internet_service": "Fiber",
    "num_support_tickets": 5,
})
print(response.json())
# {'churn_probability': 0.99, 'prediction': 'churn', 'top_contributing_features': [...]}
```

---

## 13. How Data Flows Through the System

### Training flow (runs once)

```
generate_customers()              # numpy random -> pandas DataFrame
        |
        v
    customers.csv                 # 10,000 rows x 9 columns saved to disk
        |
        v
create_derived_features()         # Add 4 calculated columns -> 13 columns
        |
        v
encode_categoricals(fit=True)     # Convert 3 text columns to integers
        |                           Save the encoder mappings
        v
StandardScaler(fit=True)          # Scale all 11 feature columns to mean=0, std=1
        |                           Save the scaler means & stds
        v
    X (10000 x 11 matrix)        # Ready for model
    y (10000 labels)              # 0=stayed, 1=churned
        |
        v
train_test_split(80/20)           # 8000 train, 2000 test
        |
        v
XGBClassifier.fit(X_train)       # Train 200 decision trees
        |
        v
evaluate on X_test                # Calculate accuracy, precision, recall, F1
        |
        v
joblib.dump(bundle)               # Save model + scaler + encoders + metrics
        |                           All in one file: model_bundle.joblib
        v
    DONE - model is ready
```

### Prediction flow (every API request)

```
Customer JSON from user
  {"tenure": 12, "monthly_charges": 65, ...}
        |
        v
Create pandas DataFrame (1 row)
        |
        v
create_derived_features()         # Same 4 derived columns
        |
        v
encode_categoricals(fit=False)    # Reuse SAVED encoders (same mapping)
        |
        v
StandardScaler.transform()       # Reuse SAVED scaler (same mean/std)
        |
        v
    X (1 x 11 matrix)            # Same shape as training data
        |
        v
model.predict_proba(X)           # XGBoost returns [P(stay), P(churn)]
        |
        v
    Response JSON
    {"churn_probability": 0.977, "prediction": "churn", ...}
```

### Dashboard flow (user interaction)

```
User opens http://localhost:8501
        |
        v
Streamlit calls GET /model-info  -----> API returns metrics + feature importance
        |
        v
Dashboard renders:
  - Metric cards (accuracy, precision, recall, F1)
  - Feature importance bar chart
  - Confusion matrix heatmap
        |
        v
User fills prediction form and clicks "Predict"
        |
        v
Streamlit calls POST /predict    -----> API runs the prediction flow above
        |
        v
Dashboard shows:
  - Churn probability (color-coded: green < 30% < orange < 50% < red)
  - Top contributing features
```

---

## 14. Key Concepts Explained

### What is a "model bundle"?

A single file (`model_bundle.joblib`) that contains everything needed to make predictions:

```
model_bundle.joblib
  |-- model            # The trained XGBoost classifier (200 decision trees)
  |-- scaler           # StandardScaler with learned mean/std for each feature
  |-- encoders         # LabelEncoders for contract_type, payment_method, internet_service
  |-- feature_names    # List of 11 column names in the correct order
  |-- feature_importance  # Which features matter most
  |-- metrics          # Training performance numbers
```

Without the scaler and encoders, you can't transform new customer data correctly.

### Why `fit=True` vs `fit=False`?

- **Training time (`fit=True`)**: The scaler and encoders LEARN from the data
  - Scaler learns: "tenure has mean=36.5 and std=20.8"
  - Encoder learns: "month-to-month=0, one_year=1, two_year=2"
- **Prediction time (`fit=False`)**: They REUSE what they learned
  - Same mean/std applied to new data
  - Same category-to-number mapping

If you re-fit at prediction time, a single customer's data would give different scaling (mean of 1 value = that value, std = 0), producing garbage.

### What is cross-validation?

Instead of one train/test split, cross-validation does 5 splits:

```
Fold 1: [TEST] [train] [train] [train] [train]  -> accuracy
Fold 2: [train] [TEST] [train] [train] [train]  -> accuracy
Fold 3: [train] [train] [TEST] [train] [train]  -> accuracy
Fold 4: [train] [train] [train] [TEST] [train]  -> accuracy
Fold 5: [train] [train] [train] [train] [TEST]  -> accuracy

CV Mean = average of all 5 accuracies
```

This gives a more reliable estimate than a single split. If CV mean is close to test accuracy, the model is stable.

### What is FastAPI lifespan?

FastAPI's `lifespan` is code that runs **once** when the server starts (not on every request):

```python
@asynccontextmanager
async def lifespan(app):
    # STARTUP: runs once when server starts
    load_model_into_memory()
    yield
    # SHUTDOWN: runs once when server stops (cleanup)
```

This is much faster than loading the model on every request.

### What is StandardScaler doing mathematically?

For each feature column:

```
scaled = (value - mean) / standard_deviation
```

Example for `tenure`:
- Training data has tenure mean = 36.5, std = 20.8
- A customer with tenure = 12:
  - scaled_tenure = (12 - 36.5) / 20.8 = -1.18
- A customer with tenure = 60:
  - scaled_tenure = (60 - 36.5) / 20.8 = +1.13

After scaling, all features are centered around 0 with similar ranges.

---

## 15. Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

You must run commands from the project root directory:

```bash
cd POCs/POC-01-Intelligent-Churn-Prediction
python -m src.pipeline    # correct
```

Not from inside `src/`:

```bash
cd src
python pipeline.py        # WRONG - will fail
```

### "Cannot reach the API" in the dashboard

The API must be running before you start the dashboard:

```bash
# Terminal 1
python main.py api        # Start this first

# Terminal 2
python main.py ui         # Then start this
```

Or use `python main.py all` to start both.

### "FileNotFoundError: model_bundle.joblib"

The model hasn't been trained yet. Run the pipeline first:

```bash
python main.py pipeline
```

Or just start the API - it will auto-train if the model is missing.

### Port already in use

If port 8000 or 8501 is busy:

```bash
# Find what's using the port
lsof -i :8000

# Kill it (replace PID with the actual number)
kill <PID>
```

Or use a different port:

```bash
uvicorn src.api:app --port 8001
streamlit run src/ui.py --server.port 8502
```

If using a different API port, tell the UI:

```bash
API_URL=http://localhost:8001 streamlit run src/ui.py

---

## 16. Interview Questions

*Situation-based and technical questions commonly asked in Data Scientist, ML Engineer, and Senior Data Engineer interviews. Sourced from LinkedIn posts, Glassdoor interview reports, and community discussions on r/datascience and r/MachineLearning.*

---

### Situational / Behavioral Questions

**Q: "Walk me through how you'd connect a churn prediction model's output to actual business action. A senior PM is asking this."**

A: A churn probability score alone is useless without an intervention playbook. First, segment the output into three risk tiers: low (< 30%), medium (30–60%), high (> 60%). Each tier triggers a different retention action — high-risk gets a personal call from the CSM or a targeted discount; medium-risk gets an automated email nurture sequence; low-risk gets nothing (over-retaining happy customers destroys margin). Next, use the `top_contributing_features` from the model to personalize the message. If `contract_type` drove the prediction, the offer should address contract flexibility. If `num_support_tickets` was the driver, the intervention should be a proactive support outreach. The model becomes valuable only when paired with this playbook. I'd also track the model's impact: compare churn rate of flagged-but-intervened customers vs. a holdout control group to measure actual ROI.

**Q: "Your churn model has been live for 6 months and the business says predictions are no longer accurate. How do you diagnose this?"**

A: Two-track diagnosis. Track 1 — **data drift**: has the distribution of input features changed? Run a PSI (Population Stability Index) check: compare the training data distribution to recent data for each feature. A new pricing tier changes `monthly_charges`, a product launch changes `internet_service` mix, an acquisition changes `contract_type` distribution. The scaler fit on old data produces out-of-distribution scaled values for new inputs. Track 2 — **concept drift**: has the relationship between features and churn changed? Score the last 30 days and compare precision/recall against actual churn outcomes (use the `customers.csv` churn labels as ground truth). If metrics dropped significantly, the model needs retraining on recent data. Fix: retrain quarterly on a time-weighted sample that emphasizes the last 60 days, and schedule automated PSI checks as an Airflow task that alerts when any feature's PSI exceeds 0.2.

**Q: "Midway through a sprint, your stakeholder changed the success metric from accuracy to 'revenue saved from churn prevention.' How do you redesign the model evaluation?"**

A: Revenue impact reframes the problem correctly — accuracy is the wrong metric anyway for an imbalanced classification problem. I'd move to a **cost-sensitive evaluation matrix**: assign each prediction outcome a business cost. A false negative (missed churner who leaves) costs the full customer LTV. A false positive (flagged as churner but they stay) costs the retention offer value (e.g., one month free = $65). The optimal classification threshold minimizes total expected cost across both error types, not the default 0.5. I'd also change the ranking metric: sort customers by `churn_probability × estimated_LTV` rather than raw probability. A 95% churn probability on a $5/month customer matters less than a 65% probability on a $200/month enterprise customer. The model's lift curve (revenue recovered at each decile) becomes the primary evaluation artifact for stakeholders.

---

### Technical Deep-Dive Questions

**Q: "Why XGBoost for this problem? When would you switch to a different algorithm?"**

A: XGBoost wins here for three reasons: (1) **Mixed feature types** — it handles numeric features (`tenure`, `monthly_charges`) and label-encoded categoricals (`contract_type`) natively without separate preprocessing paths. (2) **Feature interactions** — high monthly charges combined with month-to-month contracts is a stronger churn signal than either alone. Gradient boosting captures these multiplicative interactions implicitly. (3) **Calibrated probabilities** — with `eval_metric='logloss'`, XGBoost produces well-calibrated probability outputs suitable for risk tier segmentation. When I'd switch: **Logistic regression** if the model must be fully interpretable (regulatory requirement — every feature's coefficient has a direct business meaning). **LightGBM** if training time becomes critical at scale (10M+ rows — LightGBM is 3–10x faster than XGBoost for large datasets). **Survival analysis (Cox PH model)** if the business question changes from "will they churn?" to "when will they churn?" — survival models give time-to-event predictions.

**Q: "The model has 86% accuracy but the business is unhappy. Explain why, and how would you fix it?"**

A: The 86% accuracy includes a massive baseline effect — a model that predicts "nobody churns" achieves 74% accuracy since the churn rate is 26%. The model is barely better than doing nothing. The real problem: with default threshold 0.5, the model is optimizing for overall accuracy rather than catching churners. I'd surface the confusion matrix to stakeholders: "We caught 377 churners but missed 143 (38% of actual churners). Each missed churner costs approximately $X in LTV." Three fixes: (1) **Lower the classification threshold** from 0.5 to 0.3 — catches more churners at the cost of more false alarms. Tune the threshold to the cost ratio. (2) **Class weight adjustment** — set `scale_pos_weight` in XGBoost to `(1 - churn_rate) / churn_rate ≈ 2.85` to make the model pay more attention to churners. (3) **Change the primary metric** to F1 score or recall@precision>0.7 to align model training with business requirements from the start.

**Q: "Explain `fit=True` vs `fit=False` in your feature engineering. What happens if you apply fit=True at prediction time?"**

A: During training (`fit=True`), the StandardScaler learns the mean and standard deviation of each feature from the training data. The LabelEncoders learn the mapping `{"month-to-month": 0, "one_year": 1, "two_year": 2}`. These learned parameters are saved in the model bundle. During inference (`fit=False`), the same learned parameters are reapplied to new customer data — the same mean, same standard deviation, same category mappings. If you accidentally called `fit=True` at prediction time on a single customer, the scaler would compute `mean = the customer's own value` and `std = 0` (or near 0), producing a scaled value of exactly 0 for every feature — all signal erased. The model would receive a zero vector and output garbage probabilities. This is a subtle bug that's hard to detect without careful testing; the API still returns a prediction, just an incorrect one. The `fit` parameter discipline is what makes the model bundle self-consistent.

---

### System Design Questions

**Q: "Design a churn prevention system end-to-end: raw customer data to automated retention emails."**

A: Five layers: (1) **Feature pipeline** — daily Airflow DAG extracts CRM data, computes derived features (avg_monthly_spend, support_ticket_rate), and writes to a feature store (BigQuery materialized view or Feast). Features are time-stamped to prevent training-serving skew. (2) **Batch scoring** — weekly Spark job scores all active customers using the serialized model bundle. Output: `churn_predictions` table with `customer_id`, `churn_probability`, `churn_tier`, `top_features`, `prediction_date`. (3) **Segmentation + personalization** — SQL query segments by risk tier and LTV. For each high-risk customer, a separate service maps `top_features` to offer templates: `contract_type → "Switch to annual plan, save 20%"`, `num_support_tickets → "Proactive check-in call from your CSM"`. (4) **Campaign delivery** — integration with Salesforce Marketing Cloud or Braze via API. High-risk gets a personal outreach within 24 hours; medium-risk enters a 7-day email sequence. (5) **Outcome tracking** — 90-day follow-up: did intervened churners actually stay? Join intervention records to actual churn events in a `churn_outcomes` table. This closes the feedback loop for model retraining and ROI measurement.

**Q: "How would you monitor this model in production for drift and degradation?"**

A: Three monitoring layers running as daily Airflow tasks: (1) **Input feature drift** — compare the current day's feature distribution against the training set using PSI (Population Stability Index). PSI > 0.25 on any feature triggers an alert and initiates a retraining investigation. Libraries: Evidently AI or Nannyml handle this in 10 lines of code. (2) **Prediction drift** — track the daily predicted churn rate. If the model suddenly predicts 40% churn when historical average is 26%, either the model is unstable or a real business event occurred. Alert on > 5% week-over-week change in predicted churn rate. (3) **Outcome-based monitoring** — the hardest but most important. Because churn has a 30–90 day lag (customers take time to officially cancel), build a `churn_actuals` pipeline: join 90-day-old predictions to actual cancellation events. Compute true recall, precision, and F1 on this "ground truth" cohort monthly. If recall drops below 65%, the model needs retraining. If it drops below 50%, flag for immediate investigation and consider falling back to a rule-based segmentation while retraining.
```

### Docker build fails

Make sure Docker is running, then:

```bash
docker-compose down        # Clean up
docker-compose up --build  # Rebuild from scratch
```

### Prediction returns unexpected results

The model uses a fixed random seed (42), so retraining always produces the same model. If you get different results, check that:

1. The `data/model_bundle.joblib` was generated by this project's pipeline
2. You're passing valid values for categorical fields (exact strings like `"month-to-month"`, not `"Month-to-Month"`)
