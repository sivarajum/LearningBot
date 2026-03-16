"""XGBoost churn prediction model: training, evaluation, and inference."""

from pathlib import Path
from typing import Dict, Any, Tuple, List

import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)
from xgboost import XGBClassifier

MODEL_DIR = Path(__file__).parent.parent / "data"


def train_model(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    test_size: float = 0.2,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Train an XGBoost classifier and return metrics + artifacts.

    Returns dict with keys:
        model, accuracy, precision, recall, f1,
        feature_importance, confusion_matrix, cv_scores
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=seed,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Cross-validation on full data
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")

    # Feature importance dict
    importances = dict(zip(feature_names, model.feature_importances_.tolist()))
    importances = dict(sorted(importances.items(), key=lambda x: x[-1], reverse=True))

    return {
        "model": model,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
        "feature_importance": importances,
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "cv_scores": cv_scores.tolist(),
        "cv_mean": round(cv_scores.mean(), 4),
    }


def save_model(model: XGBClassifier, artifacts: Dict[str, Any], path: Path = MODEL_DIR) -> Path:
    """Persist model and preprocessing artifacts."""
    path.mkdir(parents=True, exist_ok=True)
    bundle = {"model": model, **artifacts}
    out = path / "model_bundle.joblib"
    joblib.dump(bundle, out)
    return out


def load_model(path: Path = MODEL_DIR / "model_bundle.joblib") -> Dict[str, Any]:
    """Load persisted model bundle."""
    return joblib.load(path)


def predict_single(
    model: XGBClassifier,
    X: np.ndarray,
    feature_names: list[str],
) -> Dict[str, Any]:
    """Predict churn probability and return top contributing features."""
    proba = model.predict_proba(X)[0]
    churn_prob = round(float(proba[1]), 4)

    # Top 3 features by importance weighted by absolute feature value
    importances = model.feature_importances_
    contributions = np.abs(X[0]) * importances
    top_indices = contributions.argsort()[-3:][::-1]
    top_features: List[Tuple[str, float]] = [
        (feature_names[i], round(float(importances[i]), 4)) for i in top_indices
    ]

    return {
        "churn_probability": churn_prob,
        "prediction": "churn" if churn_prob >= 0.5 else "no_churn",
        "top_contributing_features": top_features,
    }
