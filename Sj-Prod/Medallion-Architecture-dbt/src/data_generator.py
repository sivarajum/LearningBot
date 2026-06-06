"""
data_generator.py — Generate realistic synthetic CSV data for the Medallion Architecture POC.

Produces:
  - data/raw/customers.csv   (500 rows)
  - data/raw/orders.csv      (2000 rows)
  - data/raw/products.csv    (50 rows)
"""

from __future__ import annotations

import csv
import logging
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List

from faker import Faker

logger = logging.getLogger(__name__)

fake = Faker()
Faker.seed(42)
random.seed(42)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CUSTOMER_TIERS = ["bronze", "silver", "gold"]
TIER_WEIGHTS = [0.60, 0.30, 0.10]  # most customers are bronze

ORDER_STATUSES = ["pending", "shipped", "delivered", "cancelled"]
ORDER_STATUS_WEIGHTS = [0.10, 0.15, 0.65, 0.10]  # most orders delivered

PRODUCT_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Books",
    "Sports & Outdoors",
    "Beauty & Personal Care",
    "Toys & Games",
    "Food & Grocery",
]

COUNTRY_POOL = [
    "United States", "Canada", "United Kingdom", "Germany", "France",
    "Australia", "India", "Brazil", "Japan", "Netherlands",
]

# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def generate_products(n: int = 50) -> List[Dict[str, Any]]:
    """Return a list of product dicts."""
    products = []
    for i in range(1, n + 1):
        category = random.choice(PRODUCT_CATEGORIES)
        cost = round(random.uniform(2.0, 120.0), 2)
        # Price is cost × margin (1.2–2.5×)
        margin = round(random.uniform(1.2, 2.5), 2)
        price = round(cost * margin, 2)
        products.append(
            {
                "product_id": f"PROD-{i:04d}",
                "name": fake.catch_phrase(),
                "category": category,
                "price": price,
                "cost": cost,
            }
        )
    return products


def generate_customers(n: int = 500) -> List[Dict[str, Any]]:
    """Return a list of customer dicts."""
    customers = []
    start_date = date(2018, 1, 1)
    end_date = date(2024, 12, 31)
    delta_days = (end_date - start_date).days

    for i in range(1, n + 1):
        signup_date = start_date + timedelta(days=random.randint(0, delta_days))
        tier = random.choices(CUSTOMER_TIERS, weights=TIER_WEIGHTS, k=1)[0]
        # Intentionally inject ~2% bad emails to demonstrate Silver filtering
        email = fake.email() if random.random() > 0.02 else fake.first_name()
        customers.append(
            {
                "customer_id": f"CUST-{i:05d}",
                "name": fake.name(),
                "email": email,
                "country": random.choice(COUNTRY_POOL),
                "signup_date": signup_date.isoformat(),
                "tier": tier,
            }
        )
    return customers


def generate_orders(
    customers: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    n: int = 2000,
) -> List[Dict[str, Any]]:
    """Return a list of order dicts referencing existing customers and products."""
    orders = []
    start_date = date(2019, 1, 1)
    end_date = date(2025, 3, 31)
    delta_days = (end_date - start_date).days

    customer_ids = [c["customer_id"] for c in customers]
    product_map = {p["product_id"]: p for p in products}
    product_ids = list(product_map.keys())

    for i in range(1, n + 1):
        product_id = random.choice(product_ids)
        base_price = product_map[product_id]["price"]
        # Small random discount or markup (±10 %)
        amount = round(base_price * random.uniform(0.90, 1.10), 2)
        order_date = start_date + timedelta(days=random.randint(0, delta_days))
        status = random.choices(ORDER_STATUSES, weights=ORDER_STATUS_WEIGHTS, k=1)[0]

        orders.append(
            {
                "order_id": f"ORD-{i:06d}",
                "customer_id": random.choice(customer_ids),
                "product_id": product_id,
                "order_date": order_date.isoformat(),
                "amount": amount,
                "status": status,
            }
        )
    return orders


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------


def write_csv(records: List[Dict[str, Any]], path: Path) -> None:
    """Write a list of dicts to a CSV file."""
    if not records:
        raise ValueError("No records to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    logger.info("Wrote %d rows to %s", len(records), path)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def generate_all(output_dir: str | Path | None = None) -> Dict[str, Path]:
    """
    Generate all synthetic CSV files and return a dict of {name: Path}.

    Parameters
    ----------
    output_dir : str | Path | None
        Directory in which to write raw/ sub-directory.
        Defaults to <repo_root>/data/raw.
    """
    if output_dir is None:
        # Resolve relative to this file's location
        output_dir = Path(__file__).parent.parent / "data" / "raw"
    raw_dir = Path(output_dir)

    logger.info("Generating synthetic data → %s", raw_dir)

    products = generate_products(50)
    customers = generate_customers(500)
    orders = generate_orders(customers, products, 2000)

    paths: Dict[str, Path] = {}

    paths["products"] = raw_dir / "products.csv"
    write_csv(products, paths["products"])

    paths["customers"] = raw_dir / "customers.csv"
    write_csv(customers, paths["customers"])

    paths["orders"] = raw_dir / "orders.csv"
    write_csv(orders, paths["orders"])

    logger.info(
        "Data generation complete: %d products, %d customers, %d orders",
        len(products),
        len(customers),
        len(orders),
    )
    return paths


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    paths = generate_all()
    for name, path in paths.items():
        logger.info("  %s: %s", name, path)
