"""Data lake builder: ingests from all clouds, transforms, and creates a unified lake."""

import logging
from pathlib import Path

import pandas as pd

from src.cloud_simulator import load_cloud_data
from src.settings import DATA_DIR, LAKE_DIR

logger = logging.getLogger(__name__)

CLOUDS: list[str] = ["aws", "azure", "gcp"]


def ingest_all_customers() -> pd.DataFrame:
    """Load and merge customer data from all clouds into a unified view."""
    frames: list[pd.DataFrame] = []
    for cloud in CLOUDS:
        try:
            df = load_cloud_data(cloud, "customers")
            frames.append(df)
        except FileNotFoundError:
            logger.warning("No customer data found for cloud=%s, skipping", cloud)
            continue

    if not frames:
        raise RuntimeError("No customer data found. Run data generation first.")

    unified = pd.concat(frames, ignore_index=True)
    return unified


def ingest_all_transactions() -> pd.DataFrame:
    """Load and merge transaction data from all clouds."""
    frames: list[pd.DataFrame] = []
    for cloud in CLOUDS:
        try:
            df = load_cloud_data(cloud, "transactions")
            frames.append(df)
        except FileNotFoundError:
            logger.warning("No transaction data found for cloud=%s, skipping", cloud)
            continue

    if not frames:
        raise RuntimeError("No transaction data found. Run data generation first.")

    unified = pd.concat(frames, ignore_index=True)
    return unified


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Apply transformations to the unified customer dataset."""
    df = df.copy()
    df["signup_date"] = pd.to_datetime(df["signup_date"])
    df["tenure_days"] = (pd.Timestamp.now(tz="UTC") - df["signup_date"]).dt.days
    df["spend_tier"] = pd.cut(
        df["monthly_spend"],
        bins=[0, 50, 150, 300, float("inf")],
        labels=["low", "medium", "high", "premium"],
    )
    return df


def transform_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Apply transformations to the unified transaction dataset."""
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["month"] = df["transaction_date"].dt.tz_localize(None).dt.to_period("M").astype(str)
    df["amount_bucket"] = pd.cut(
        df["amount"],
        bins=[0, 25, 100, 500, float("inf")],
        labels=["small", "medium", "large", "whale"],
    )
    return df


def compute_customer_metrics(customers: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
    """Compute per-customer aggregated metrics across all clouds."""
    tx_agg = transactions.groupby("customer_id").agg(
        total_transactions=("transaction_id", "count"),
        total_spent=("amount", "sum"),
        avg_transaction=("amount", "mean"),
        max_transaction=("amount", "max"),
        unique_categories=("category", "nunique"),
    ).round(2)

    merged = customers.merge(tx_agg, on="customer_id", how="left")
    merged["total_transactions"] = merged["total_transactions"].fillna(0).astype(int)
    merged["total_spent"] = merged["total_spent"].fillna(0)
    merged["avg_transaction"] = merged["avg_transaction"].fillna(0)
    return merged


def build_lake() -> dict[str, str]:
    """Run the full lake-building pipeline: ingest, transform, save.

    Returns:
        Dict with paths to saved lake tables.
    """
    LAKE_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("[1/5] Ingesting customers from all clouds...")
    customers = ingest_all_customers()
    logger.info("  -> %d customers from %d clouds", len(customers), customers["source_cloud"].nunique())

    logger.info("[2/5] Ingesting transactions from all clouds...")
    transactions = ingest_all_transactions()
    logger.info("  -> %d transactions", len(transactions))

    logger.info("[3/5] Transforming customer data...")
    customers = transform_customers(customers)

    logger.info("[4/5] Transforming transaction data...")
    transactions = transform_transactions(transactions)

    logger.info("[5/5] Computing customer metrics and saving lake...")
    metrics = compute_customer_metrics(customers, transactions)

    # Save to lake
    paths: dict[str, str] = {}
    for name, df in [("customers", customers), ("transactions", transactions), ("customer_metrics", metrics)]:
        path = LAKE_DIR / f"{name}.parquet"
        df.to_parquet(path, index=False)
        paths[name] = str(path)
        logger.info("  -> Saved %s: %d rows -> %s", name, len(df), path)

    return paths


def load_lake_table(name: str) -> pd.DataFrame:
    """Load a table from the data lake."""
    path = LAKE_DIR / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Lake table not found: {path}. Run build_lake() first.")
    return pd.read_parquet(path)
