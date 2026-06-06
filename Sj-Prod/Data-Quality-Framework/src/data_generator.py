"""
data_generator.py — Generate realistic sample datasets with intentional DQ issues.

Why intentional DQ issues?
    A DQ framework demonstration needs real problems to detect. Real datasets
    have missing values, invalid formats, orphaned references, and stale data.
    These generators reproduce the most common patterns seen in enterprise data.

    The generated issues mirror real scenarios from financial services:
        - customers  : PayPal user onboarding data — nulls, bad emails, age outliers
        - transactions: Payment records — negative amounts, future dates, orphaned IDs
        - products   : Product catalog — duplicate codes, bad categories, null names

Datasets:
    1. customers    (500 rows)  — CRM / user master table
    2. transactions (2000 rows) — Payment / event fact table
    3. products     (100 rows)  — Reference / dimension table

Usage:
    from src.data_generator import DataGenerator
    gen = DataGenerator(output_dir="./data")
    dfs = gen.generate_all()  # Returns dict of DataFrames, saves CSVs
"""

import logging
import os
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Generates three sample datasets with known, intentional DQ issues.

    The seed is fixed for reproducibility — same issues every run.
    """

    def __init__(self, output_dir: str = "./data", seed: int = 42):
        self.output_dir = output_dir
        self.seed = seed
        random.seed(seed)
        os.makedirs(output_dir, exist_ok=True)

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        """Generate all three datasets, save as CSV, return as dict of DataFrames."""
        dfs = {}
        dfs["customers"] = self.generate_customers()
        dfs["transactions"] = self.generate_transactions(
            customer_ids=list(dfs["customers"]["customer_id"].dropna())
        )
        dfs["products"] = self.generate_products()

        for name, df in dfs.items():
            path = os.path.join(self.output_dir, f"{name}.csv")
            df.to_csv(path, index=False)
            logger.info("Saved %s: %d rows -> %s", name, len(df), path)

        return dfs

    # ─────────────────────────────────────────────────────────
    # Dataset 1: Customers (500 rows)
    # ─────────────────────────────────────────────────────────

    def generate_customers(self, n: int = 500) -> pd.DataFrame:
        """
        Generate customer master data with intentional DQ issues:

        Issues injected:
            - ~5% null emails
            - ~3% duplicate customer_ids
            - ~4% invalid email formats (missing @, typos)
            - ~2% ages < 0 (data entry error)
            - ~1% ages > 120 (unrealistic)
            - ~3% null first names
            - ~2% invalid status values (not in allowed set)
            - ~1% null customer_id (critical completeness issue)
        """
        rng = random.Random(self.seed)

        first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
            "Linda", "William", "Barbara", "David", "Susan", "Richard", "Jessica",
            "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Lisa", "Priya",
            "Arjun", "Wei", "Mei", "Carlos", "Sofia", "Ahmed", "Fatima",
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        ]
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "company.com"]
        statuses = ["active", "inactive", "pending"]

        rows = []
        base_ids = [f"CUST{str(i).zfill(6)}" for i in range(1, n + 1)]

        # Inject ~3% duplicate IDs (replace some IDs with earlier ones)
        dup_count = int(n * 0.03)
        dup_source_ids = base_ids[:50]
        for i in range(n - dup_count, n - dup_count + dup_count):
            base_ids[i] = rng.choice(dup_source_ids)

        for i in range(n):
            cid = base_ids[i]

            # ~1% null customer_id
            if rng.random() < 0.01:
                cid = None

            first = rng.choice(first_names)
            last = rng.choice(last_names)

            # ~3% null first names
            if rng.random() < 0.03:
                first = None

            # Build email
            domain = rng.choice(domains)
            clean_first = (first or "user").lower()
            clean_last = last.lower()
            email = f"{clean_first}.{clean_last}{rng.randint(1, 999)}@{domain}"

            # ~5% null emails
            if rng.random() < 0.05:
                email = None
            # ~4% invalid email format
            elif rng.random() < 0.04:
                bad_formats = [
                    f"{clean_first}{clean_last}{rng.randint(1,99)}",       # missing @
                    f"{clean_first}@",                                       # no domain
                    f"@{domain}",                                            # no local part
                    f"{clean_first}..{clean_last}@{domain}",                # double dot
                ]
                email = rng.choice(bad_formats)

            # Age with issues
            age = rng.randint(18, 75)
            if rng.random() < 0.02:
                age = rng.randint(-10, -1)   # invalid: negative age
            elif rng.random() < 0.01:
                age = rng.randint(121, 200)  # invalid: impossibly old

            # Status
            status = rng.choice(statuses)
            if rng.random() < 0.02:
                status = rng.choice(["ACTIVE", "Inactive", "SUSPENDED", "unknown"])

            # Signup date — mostly in the past 3 years, some in the future
            days_ago = rng.randint(1, 1095)
            signup_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            if rng.random() < 0.01:
                # Future signup date (invalid)
                signup_date = (datetime.now(timezone.utc) + timedelta(days=rng.randint(1, 30))).strftime("%Y-%m-%d")

            phone = f"+1-{rng.randint(200,999)}-{rng.randint(100,999)}-{rng.randint(1000,9999)}"
            if rng.random() < 0.08:
                phone = None  # 8% null phones — more acceptable

            country = rng.choice(["US", "CA", "GB", "DE", "FR", "AU", "SG", "IN"])

            rows.append({
                "customer_id": cid,
                "first_name": first,
                "last_name": last,
                "email": email,
                "age": age,
                "status": status,
                "signup_date": signup_date,
                "phone": phone,
                "country": country,
            })

        return pd.DataFrame(rows)

    # ─────────────────────────────────────────────────────────
    # Dataset 2: Transactions (2000 rows)
    # ─────────────────────────────────────────────────────────

    def generate_transactions(
        self, n: int = 2000, customer_ids: list = None
    ) -> pd.DataFrame:
        """
        Generate payment transaction records with intentional DQ issues:

        Issues injected:
            - ~4% null amounts
            - ~3% negative amounts (invalid for a payment)
            - ~5% transaction dates in the future (invalid)
            - ~6% customer_ids NOT in the customers table (referential integrity violation)
            - ~2% null transaction_type
            - ~1% duplicate transaction_ids
        """
        rng = random.Random(self.seed + 1)

        if not customer_ids:
            customer_ids = [f"CUST{str(i).zfill(6)}" for i in range(1, 501)]

        txn_types = ["purchase", "refund", "transfer", "withdrawal", "deposit"]
        currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
        channels = ["web", "mobile", "api", "pos"]
        statuses = ["completed", "pending", "failed", "reversed"]

        rows = []
        base_txn_ids = [f"TXN{str(i).zfill(8)}" for i in range(1, n + 1)]

        # Inject ~1% duplicate transaction IDs
        dup_count = int(n * 0.01)
        for i in range(n - dup_count, n):
            base_txn_ids[i] = base_txn_ids[rng.randint(0, n - dup_count - 1)]

        # Build a pool of "ghost" customer IDs not in the customers table
        ghost_ids = [f"GHOST{str(i).zfill(6)}" for i in range(1, 200)]

        for i in range(n):
            txn_id = base_txn_ids[i]

            # Customer reference
            if rng.random() < 0.06:
                cid = rng.choice(ghost_ids)  # referential integrity violation
            else:
                cid = rng.choice(customer_ids)

            # Amount
            amount = round(rng.uniform(1.0, 5000.0), 2)
            if rng.random() < 0.04:
                amount = None  # null amount
            elif rng.random() < 0.03:
                amount = round(-rng.uniform(0.01, 999.0), 2)  # negative (invalid)

            # Transaction date
            days_ago = rng.randint(1, 365)
            txn_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            if rng.random() < 0.05:
                # Future date (invalid)
                future_days = rng.randint(1, 90)
                txn_date = (datetime.now(timezone.utc) + timedelta(days=future_days)).strftime("%Y-%m-%d %H:%M:%S")

            txn_type = rng.choice(txn_types)
            if rng.random() < 0.02:
                txn_type = None

            currency = rng.choice(currencies)
            channel = rng.choice(channels)
            status = rng.choice(statuses)
            merchant_id = f"MERCH{rng.randint(1000, 9999)}"

            rows.append({
                "transaction_id": txn_id,
                "customer_id": cid,
                "amount": amount,
                "currency": currency,
                "transaction_date": txn_date,
                "transaction_type": txn_type,
                "channel": channel,
                "status": status,
                "merchant_id": merchant_id,
            })

        return pd.DataFrame(rows)

    # ─────────────────────────────────────────────────────────
    # Dataset 3: Products (100 rows)
    # ─────────────────────────────────────────────────────────

    def generate_products(self, n: int = 100) -> pd.DataFrame:
        """
        Generate product catalog data with intentional DQ issues:

        Issues injected:
            - ~4% duplicate product_codes
            - ~5% categories not in the allowed list
            - ~3% null product names
            - ~2% negative prices
            - ~6% null stock_quantity
        """
        rng = random.Random(self.seed + 2)

        allowed_categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Food"]
        bad_categories = ["ELEC", "clothes", "novel", "household", "gym", "groceries", "misc"]

        adjectives = ["Premium", "Standard", "Basic", "Advanced", "Pro", "Lite", "Ultra", "Classic"]
        nouns = ["Widget", "Gadget", "Device", "Tool", "Kit", "Module", "Pack", "Set"]

        rows = []
        base_codes = [f"PROD{str(i).zfill(4)}" for i in range(1, n + 1)]

        # Inject ~4% duplicate product codes
        dup_count = int(n * 0.04)
        for i in range(n - dup_count, n):
            base_codes[i] = base_codes[rng.randint(0, n - dup_count - 1)]

        for i in range(n):
            code = base_codes[i]

            name = f"{rng.choice(adjectives)} {rng.choice(nouns)} {rng.randint(100, 999)}"
            if rng.random() < 0.03:
                name = None  # null product name

            category = rng.choice(allowed_categories)
            if rng.random() < 0.05:
                category = rng.choice(bad_categories)  # invalid category

            price = round(rng.uniform(0.99, 999.99), 2)
            if rng.random() < 0.02:
                price = round(-rng.uniform(0.01, 99.0), 2)  # negative price

            stock = rng.randint(0, 1000)
            if rng.random() < 0.06:
                stock = None  # null stock

            sku = "".join(rng.choices(string.ascii_uppercase + string.digits, k=10))
            in_stock = price is not None and (stock or 0) > 0

            rows.append({
                "product_code": code,
                "product_name": name,
                "category": category,
                "price": price,
                "stock_quantity": stock,
                "sku": sku,
                "in_stock": in_stock,
            })

        return pd.DataFrame(rows)


def load_or_generate(data_dir: str = "./data") -> Dict[str, pd.DataFrame]:
    """
    Load CSVs from data_dir if they exist; otherwise generate and save them.

    This is the standard entry point used by api.py and ui.py.
    """
    required = ["customers.csv", "transactions.csv", "products.csv"]
    all_exist = all(os.path.exists(os.path.join(data_dir, f)) for f in required)

    if all_exist:
        dfs = {}
        for fname in required:
            name = fname.replace(".csv", "")
            dfs[name] = pd.read_csv(os.path.join(data_dir, fname))
        logger.info("Loaded existing datasets from %s", data_dir)
        return dfs
    else:
        logger.info("Generating datasets in %s...", data_dir)
        gen = DataGenerator(output_dir=data_dir)
        return gen.generate_all()
