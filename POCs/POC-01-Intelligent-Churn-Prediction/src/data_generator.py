"""Synthetic customer data generator for churn prediction."""

import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
NUM_CUSTOMERS = 10_000
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "customers.csv"

CONTRACT_TYPES = ["month-to-month", "one_year", "two_year"]
PAYMENT_METHODS = ["electronic_check", "mailed_check", "bank_transfer", "credit_card"]
INTERNET_SERVICES = ["DSL", "Fiber", "No"]


def generate_customers(n: int = NUM_CUSTOMERS, seed: int = SEED) -> pd.DataFrame:
    """Generate synthetic customer data with realistic churn correlations."""
    rng = np.random.RandomState(seed)

    tenure = rng.randint(1, 73, size=n)
    monthly_charges = rng.uniform(20, 120, size=n).round(2)
    total_charges = (tenure * monthly_charges * rng.uniform(0.85, 1.05, size=n)).round(2)

    contract_type = rng.choice(CONTRACT_TYPES, size=n, p=[0.50, 0.30, 0.20])
    payment_method = rng.choice(PAYMENT_METHODS, size=n, p=[0.35, 0.25, 0.22, 0.18])
    internet_service = rng.choice(INTERNET_SERVICES, size=n, p=[0.35, 0.45, 0.20])

    num_support_tickets = rng.poisson(lam=2.5, size=n).clip(0, 10)

    # --- Realistic churn probability based on feature correlations ---
    churn_score = np.zeros(n, dtype=float)

    # Short tenure increases churn
    churn_score += np.where(tenure < 12, 1.5, np.where(tenure < 24, 0.5, -0.8))

    # Month-to-month contracts churn far more
    churn_score += np.where(contract_type == "month-to-month", 1.2,
                  np.where(contract_type == "one_year", -0.3, -1.0))

    # Higher monthly charges increase churn
    churn_score += (monthly_charges - 70) / 50

    # Electronic check correlates with churn
    churn_score += np.where(payment_method == "electronic_check", 0.6, -0.2)

    # Fiber internet has more churn (price sensitivity)
    churn_score += np.where(internet_service == "Fiber", 0.5,
                  np.where(internet_service == "No", -0.4, 0.0))

    # More support tickets = more churn
    churn_score += (num_support_tickets - 2.5) * 0.3

    # Add noise and convert to probability
    churn_score += rng.normal(0, 0.8, size=n)
    churn_prob = 1 / (1 + np.exp(-churn_score * 0.6))

    # Target ~26% overall churn rate
    threshold = np.percentile(churn_prob, 74)
    churn = (churn_prob >= threshold).astype(int)

    df = pd.DataFrame({
        "customer_id": [f"CUST-{i:05d}" for i in range(n)],
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "contract_type": contract_type,
        "payment_method": payment_method,
        "internet_service": internet_service,
        "num_support_tickets": num_support_tickets,
        "churn": churn,
    })
    return df


def save_data(df: pd.DataFrame, path: Path = OUTPUT_PATH) -> Path:
    """Save generated data to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    df = generate_customers()
    path = save_data(df)
    churn_rate = df["churn"].mean()
    print(f"Generated {len(df)} customers | Churn rate: {churn_rate:.1%} | Saved to {path}")
