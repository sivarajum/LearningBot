"""End-to-end pipeline: generate data -> engineer features -> train model -> save."""

import logging
import time
from datetime import datetime, timezone

from src.data_generator import generate_customers, save_data
from src.feature_engineering import build_features
from src.model import train_model, save_model

logger = logging.getLogger(__name__)


def run_pipeline() -> dict:
    """Execute the full training pipeline and return summary metrics."""
    logger.info("=" * 60)
    logger.info("  Churn Prediction Pipeline")
    logger.info("=" * 60)

    # Step 1: Generate data
    t0 = time.time()
    logger.info("[1/4] Generating synthetic customer data...")
    df = generate_customers()
    data_path = save_data(df)
    churn_rate = df["churn"].mean()
    logger.info("  -> %d customers | churn rate: %.1f%% | saved to %s", len(df), churn_rate * 100, data_path)
    logger.info("  -> Done in %.1fs", time.time() - t0)

    # Step 2: Feature engineering
    t1 = time.time()
    logger.info("[2/4] Engineering features...")
    X, y, feature_names, artifacts = build_features(df, fit=True)
    logger.info("  -> %d features: %s", X.shape[1], feature_names)
    logger.info("  -> Done in %.1fs", time.time() - t1)

    # Step 3: Train model
    t2 = time.time()
    logger.info("[3/4] Training XGBoost model...")
    results = train_model(X, y, feature_names)
    logger.info("  -> Accuracy:  %.2f%%", results["accuracy"] * 100)
    logger.info("  -> Precision: %.2f%%", results["precision"] * 100)
    logger.info("  -> Recall:    %.2f%%", results["recall"] * 100)
    logger.info("  -> F1 Score:  %.2f%%", results["f1"] * 100)
    logger.info("  -> CV Mean:   %.2f%%", results["cv_mean"] * 100)
    logger.info("  -> Done in %.1fs", time.time() - t2)

    # Step 4: Save artifacts
    t3 = time.time()
    logger.info("[4/4] Saving model and artifacts...")
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
    logger.info("  -> Model bundle saved to %s", model_path)
    logger.info("  -> Done in %.1fs", time.time() - t3)

    total = time.time() - t0
    logger.info("=" * 60)
    logger.info("  Pipeline completed in %.1fs", total)
    logger.info("=" * 60)

    return metrics


if __name__ == "__main__":
    from src.logging_config import setup_logging

    setup_logging()
    run_pipeline()
