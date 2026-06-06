"""
freshness.py — Rules that check data recency.

DQ Dimension: Freshness
    Freshness answers: "Is the data recent enough for its intended use?"
    Stale data = business decisions based on outdated information.

    Real-world context:
        - PayPal: risk models need transaction data < 1 hour old; stale = missed fraud
        - FedEx: package tracking must reflect status within 15 minutes
        - Analytics: dashboards relying on yesterday's data when today's is expected

Rules:
    DataFreshnessRule — max date in a timestamp column must be within max_age_hours
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd

from .base_rule import BaseRule, RuleResult

logger = logging.getLogger(__name__)


class DataFreshnessRule(BaseRule):
    """
    Asserts that the most recent value in a date/timestamp column is recent enough.

    Checks: max(column) >= (now - max_age_hours)
    Score: 1.0 if within age limit; decays proportionally as data gets older.

    Args:
        max_age_hours: Maximum acceptable age of newest record, in hours. Default 48.
        reference_time: Override the "now" timestamp (useful for testing). Default = datetime.now(UTC).

    Example:
        DataFreshnessRule(
            name="transactions_fresh", column="transaction_date",
            max_age_hours=24, severity="warning"
        )
        # Passes if there's at least one transaction within the last 24 hours
    """

    dimension = "freshness"

    def __init__(
        self,
        name: str,
        column: str,
        max_age_hours: float = 48.0,
        severity: str = "warning",
        reference_time: Optional[datetime] = None,
    ):
        super().__init__(name=name, column=column, severity=severity)
        if max_age_hours <= 0:
            raise ValueError(f"max_age_hours must be > 0, got {max_age_hours}")
        self.max_age_hours = max_age_hours
        self.reference_time = reference_time  # None = use datetime.now(UTC) at validation time

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        total = len(df)
        series = df[self.column].dropna()

        if len(series) == 0:
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=False, score=0.0,
                failing_count=total, total_count=total, pass_rate=0.0,
                details=f"Column '{self.column}' has no non-null values — cannot assess freshness.",
            )

        # Parse dates
        try:
            parsed = pd.to_datetime(series, errors="coerce", utc=False)
        except (ValueError, TypeError) as exc:
            logger.error("Failed to parse dates in column '%s': %s", self.column, exc)
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=False, score=0.0,
                failing_count=total, total_count=total, pass_rate=0.0,
                details=f"Column '{self.column}' could not be parsed as datetime.",
            )

        unparseable = int(parsed.isna().sum())
        valid_dates = parsed.dropna()

        if len(valid_dates) == 0:
            return RuleResult(
                rule_name=self.name, column=self.column, dimension=self.dimension,
                severity=self.severity, passed=False, score=0.0,
                failing_count=total, total_count=total, pass_rate=0.0,
                details=f"Column '{self.column}' has no parseable date values.",
            )

        max_date = valid_dates.max()

        # Resolve reference time
        now = self.reference_time if self.reference_time else datetime.now(timezone.utc).replace(tzinfo=None)
        # Make both timezone-naive for comparison
        if hasattr(max_date, "tzinfo") and max_date.tzinfo is not None:
            max_date = max_date.replace(tzinfo=None)

        cutoff = now - timedelta(hours=self.max_age_hours)
        age_hours = (now - max_date).total_seconds() / 3600

        passed = max_date >= cutoff

        # Score: 1.0 if exactly at freshness boundary, decays linearly
        # 1.0 at age=0, 0.5 at age=max_age_hours, 0 at age=2*max_age_hours
        if age_hours <= 0:
            score = 1.0
        elif age_hours <= self.max_age_hours:
            score = 1.0 - (age_hours / (2 * self.max_age_hours))
        else:
            score = max(0.0, 1.0 - (age_hours / (2 * self.max_age_hours)))

        details = (
            f"Column '{self.column}' freshness: most recent value is "
            f"'{max_date.strftime('%Y-%m-%d %H:%M:%S')}' "
            f"(age: {age_hours:.1f}h, limit: {self.max_age_hours}h). "
            f"{'PASSED' if passed else 'FAILED — data is stale'}."
        )

        # For freshness, the "failing count" is the count of stale rows (older than cutoff)
        stale_mask = valid_dates < cutoff
        failing_count = int(stale_mask.sum()) + unparseable

        return RuleResult(
            rule_name=self.name, column=self.column, dimension=self.dimension,
            severity=self.severity, passed=passed, score=score,
            failing_count=failing_count, total_count=total,
            pass_rate=(total - failing_count) / total if total > 0 else 1.0,
            details=details,
            failing_values=[str(max_date)],
        )
