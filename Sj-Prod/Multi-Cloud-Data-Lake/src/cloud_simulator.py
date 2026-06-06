"""Simulated multi-cloud storage: generates data as if from AWS S3, Azure ADLS, and GCP GCS."""

import logging
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.settings import DATA_DIR

logger = logging.getLogger(__name__)

REGIONS_BY_CLOUD: dict[str, list[str]] = {
    "aws": ["us-east-1", "us-west-2", "eu-west-1"],
    "azure": ["eastus", "westeurope", "southeastasia"],
    "gcp": ["us-central1", "europe-west1", "asia-east1"],
}

PRODUCT_CATEGORIES: list[str] = ["electronics", "clothing", "groceries", "books", "home"]


def _generate_customers(cloud: str, n: int, seed: int) -> pd.DataFrame:
    """Generate customer data as if from a specific cloud provider."""
    rng = np.random.RandomState(seed)
    regions = REGIONS_BY_CLOUD[cloud]

    start_date = datetime(2022, 1, 1, tzinfo=timezone.utc)
    signup_dates = [
        start_date + timedelta(days=int(rng.randint(0, 730)))
        for _ in range(n)
    ]

    return pd.DataFrame({
        "customer_id": [f"{cloud[:2].upper()}-{i:05d}" for i in range(n)],
        "source_cloud": cloud,
        "name": [f"Customer_{cloud}_{i}" for i in range(n)],
        "region": rng.choice(regions, size=n).tolist(),
        "signup_date": signup_dates,
        "plan": rng.choice(["free", "basic", "premium", "enterprise"], size=n,
                           p=[0.40, 0.30, 0.20, 0.10]).tolist(),
        "monthly_spend": rng.uniform(0, 500, size=n).round(2),
        "is_active": rng.choice([True, False], size=n, p=[0.75, 0.25]).tolist(),
    })


def _generate_transactions(cloud: str, customers: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    """Generate transaction data for customers from a specific cloud."""
    rng = np.random.RandomState(seed)
    customer_ids = customers["customer_id"].tolist()

    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    tx_dates = [
        start_date + timedelta(days=int(rng.randint(0, 365)),
                               hours=int(rng.randint(0, 23)),
                               minutes=int(rng.randint(0, 59)))
        for _ in range(n)
    ]

    return pd.DataFrame({
        "transaction_id": [f"TX-{cloud[:2].upper()}-{i:06d}" for i in range(n)],
        "customer_id": rng.choice(customer_ids, size=n).tolist(),
        "source_cloud": cloud,
        "amount": rng.uniform(5, 1000, size=n).round(2),
        "category": rng.choice(PRODUCT_CATEGORIES, size=n).tolist(),
        "transaction_date": tx_dates,
        "payment_method": rng.choice(
            ["credit_card", "debit_card", "bank_transfer", "digital_wallet"],
            size=n, p=[0.40, 0.25, 0.20, 0.15]
        ).tolist(),
    })


def generate_cloud_data(
    customers_per_cloud: int = 1000,
    transactions_per_cloud: int = 5000,
) -> dict[str, dict[str, pd.DataFrame]]:
    """Generate data for all three cloud providers.

    Returns:
        Dict mapping cloud name to dict of DataFrames (customers, transactions).
    """
    data: dict[str, dict[str, pd.DataFrame]] = {}
    seeds = {"aws": 42, "azure": 123, "gcp": 456}

    for cloud, seed in seeds.items():
        customers = _generate_customers(cloud, customers_per_cloud, seed)
        transactions = _generate_transactions(cloud, customers, transactions_per_cloud, seed + 1)
        data[cloud] = {"customers": customers, "transactions": transactions}

    return data


def save_cloud_data(data: dict[str, dict[str, pd.DataFrame]]) -> dict[str, list[str]]:
    """Save generated data to cloud-specific directories as Parquet files.

    Returns:
        Dict mapping cloud name to list of saved file paths.
    """
    saved: dict[str, list[str]] = {}
    for cloud, tables in data.items():
        cloud_dir = DATA_DIR / cloud
        cloud_dir.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []
        for table_name, df in tables.items():
            path = cloud_dir / f"{table_name}.parquet"
            df.to_parquet(path, index=False)
            paths.append(str(path))
        saved[cloud] = paths
    return saved


def load_cloud_data(cloud: str, table: str) -> pd.DataFrame:
    """Load a specific table from a specific cloud's storage."""
    path = DATA_DIR / cloud / f"{table}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"No data found: {path}")
    return pd.read_parquet(path)
