"""Feature engineering pipeline for churn prediction."""

import logging
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to the raw customer dataframe."""
    df = df.copy()

    # Average monthly spend (smoothed for short tenures)
    df["avg_monthly_spend"] = df["total_charges"] / df["tenure"].clip(lower=1)

    # Tenure buckets: new / mid / loyal / veteran
    bins = [0, 6, 24, 48, 73]
    labels = [0, 1, 2, 3]
    df["tenure_bucket"] = pd.cut(df["tenure"], bins=bins, labels=labels, include_lowest=True)
    df["tenure_bucket"] = df["tenure_bucket"].astype(int)

    # Support ticket rate (tickets per year of tenure)
    df["support_ticket_rate"] = (
        df["num_support_tickets"] / (df["tenure"].clip(lower=1) / 12)
    ).round(4)

    # Charge-to-tenure ratio (spending intensity)
    df["charge_tenure_ratio"] = (df["monthly_charges"] * df["tenure"]).round(2)

    return df


def encode_categoricals(
    df: pd.DataFrame,
    encoders: Dict[str, LabelEncoder] | None = None,
    fit: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    """Label-encode categorical columns. Reuse fitted encoders at inference."""
    categorical_cols = ["contract_type", "payment_method", "internet_service"]
    df = df.copy()

    if encoders is None:
        encoders = {}

    for col in categorical_cols:
        if fit:
            enc = LabelEncoder()
            df[col] = enc.fit_transform(df[col])
            encoders[col] = enc
        else:
            df[col] = encoders[col].transform(df[col])

    return df, encoders


def build_features(
    df: pd.DataFrame,
    scaler: StandardScaler | None = None,
    encoders: Dict[str, LabelEncoder] | None = None,
    fit: bool = True,
) -> Tuple[np.ndarray, np.ndarray | None, list[str], Dict[str, Any]]:
    """
    Full feature pipeline: derive features, encode, scale.

    Returns:
        X: feature matrix
        y: target array (None during inference)
        feature_names: list of column names
        artifacts: dict with fitted scaler and encoders for persistence
    """
    df = create_derived_features(df)
    df, encoders = encode_categoricals(df, encoders=encoders, fit=fit)

    feature_cols = [
        "tenure", "monthly_charges", "total_charges",
        "contract_type", "payment_method", "internet_service",
        "num_support_tickets", "avg_monthly_spend",
        "tenure_bucket", "support_ticket_rate", "charge_tenure_ratio",
    ]

    # Handle missing values
    df[feature_cols] = df[feature_cols].fillna(0)

    X = df[feature_cols].values.astype(float)

    if fit:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
    else:
        X = scaler.transform(X)  # type: ignore[union-attr]

    y = df["churn"].values if "churn" in df.columns else None

    artifacts = {"scaler": scaler, "encoders": encoders, "feature_names": feature_cols}
    return X, y, feature_cols, artifacts
