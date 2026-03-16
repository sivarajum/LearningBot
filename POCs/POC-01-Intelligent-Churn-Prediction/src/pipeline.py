"""End-to-end pipeline: generate data -> engineer features -> train model -> save."""

import time
from datetime import datetime, timezone

from src.data_generator import generate_customers, save_data
from src.feature_engineering import build_features
from src.model import train_model, save_model


def run_pipeline() -> dict:
    """Execute the full training pipeline and return summary metrics."""
    print("=" * 60)
    print("  Churn Prediction Pipeline")
    print("=" * 60)

    # Step 1: Generate data
    t0 = time.time()
    print("\n[1/4] Generating synthetic customer data...")
    df = generate_customers()
    data_path = save_data(df)
    churn_rate = df["churn"].mean()
    print(f"  -> {len(df)} customers | churn rate: {churn_rate:.1%} | saved to {data_path}")
    print(f"  -> Done in {time.time() - t0:.1f}s")

    # Step 2: Feature engineering
    t1 = time.time()
    print("\n[2/4] Engineering features...")
    X, y, feature_names, artifacts = build_features(df, fit=True)
    print(f"  -> {X.shape[1]} features: {feature_names}")
    print(f"  -> Done in {time.time() - t1:.1f}s")

    # Step 3: Train model
    t2 = time.time()
    print("\n[3/4] Training XGBoost model...")
    results = train_model(X, y, feature_names)
    print(f"  -> Accuracy:  {results['accuracy']:.2%}")
    print(f"  -> Precision: {results['precision']:.2%}")
    print(f"  -> Recall:    {results['recall']:.2%}")
    print(f"  -> F1 Score:  {results['f1']:.2%}")
    print(f"  -> CV Mean:   {results['cv_mean']:.2%}")
    print(f"  -> Done in {time.time() - t2:.1f}s")

    # Step 4: Save artifacts
    t3 = time.time()
    print("\n[4/4] Saving model and artifacts...")
    metrics = {
        "accuracy": results["accuracy"],
        "precision": results["precision"],
        "recall": results["recall"],
        "f1": results["f1"],
        "cv_mean": results["cv_mean"],
        "confusion_matrix": results["confusion_matrix"],
        "training_date": datetime.now(timezone.utc).isoformat(),
    }
    save_artifacts = {
        **artifacts,
        "feature_importance": results["feature_importance"],
        "metrics": metrics,
    }
    model_path = save_model(results["model"], save_artifacts)
    print(f"  -> Model bundle saved to {model_path}")
    print(f"  -> Done in {time.time() - t3:.1f}s")

    total = time.time() - t0
    print("\n" + "=" * 60)
    print(f"  Pipeline completed in {total:.1f}s")
    print("=" * 60)

    return metrics


if __name__ == "__main__":
    run_pipeline()
