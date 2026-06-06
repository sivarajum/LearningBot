"""
profiler.py — Automatic data profiling for any pandas DataFrame.

The DataProfiler generates rich column-level and dataset-level statistics
without requiring the user to specify schema upfront. This is the "discovery"
layer of a DQ framework — run it before defining rules to understand your data.

Real-world use:
    - Onboarding a new data source: profile first, then define rules
    - Change detection: compare today's profile vs yesterday's
    - Documentation generation: auto-generate data dictionaries

Profile includes:
    - Null counts and rates
    - Distinct counts and uniqueness ratio
    - Min / max / mean / std for numeric columns
    - Sample values
    - Inferred data type category
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ColumnProfile:
    """
    Statistical profile for a single column.

    Attributes:
        column          : Column name
        dtype           : pandas dtype string (e.g. "object", "int64", "float64")
        inferred_type   : Human-friendly type: "numeric", "text", "datetime", "boolean", "mixed"
        total_count     : Total rows in the DataFrame
        null_count      : Number of null / NaN values
        null_rate       : null_count / total_count
        distinct_count  : Number of unique non-null values
        distinct_rate   : distinct_count / non_null_count
        min_value       : Minimum value (for numeric/datetime)
        max_value       : Maximum value (for numeric/datetime)
        mean_value      : Mean (for numeric only)
        std_dev         : Standard deviation (for numeric only)
        median_value    : Median (for numeric only)
        top_values      : Top 5 most frequent values with counts
        sample_values   : Up to 5 random sample values
    """
    column: str
    dtype: str
    inferred_type: str
    total_count: int
    null_count: int
    null_rate: float
    distinct_count: int
    distinct_rate: float
    min_value: Any = None
    max_value: Any = None
    mean_value: Optional[float] = None
    std_dev: Optional[float] = None
    median_value: Optional[float] = None
    top_values: List[Dict] = field(default_factory=list)
    sample_values: List[Any] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        # Ensure all values are JSON-serialisable
        for key in ["min_value", "max_value", "mean_value", "std_dev", "median_value"]:
            if d[key] is not None:
                try:
                    # Convert numpy types and pandas Timestamps
                    val = d[key]
                    if hasattr(val, "item"):
                        d[key] = val.item()
                    elif hasattr(val, "isoformat"):
                        d[key] = str(val)
                    else:
                        d[key] = val
                except (ValueError, TypeError, AttributeError):
                    d[key] = str(d[key])
        d["null_rate"] = round(d["null_rate"], 4)
        d["distinct_rate"] = round(d["distinct_rate"], 4)
        return d


@dataclass
class DatasetProfile:
    """
    Full profile for a DataFrame: metadata + per-column profiles.

    Attributes:
        dataset_name    : Logical name of the dataset (e.g. "customers")
        profiled_at     : ISO 8601 timestamp of when profiling ran
        row_count       : Total number of rows
        column_count    : Total number of columns
        columns         : List of ColumnProfile objects
        duplicate_rows  : Number of fully duplicate rows
        duplicate_rate  : duplicate_rows / row_count
    """
    dataset_name: str
    profiled_at: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    duplicate_rows: int
    duplicate_rate: float

    def to_dict(self) -> dict:
        return {
            "dataset_name": self.dataset_name,
            "profiled_at": self.profiled_at,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "duplicate_rows": self.duplicate_rows,
            "duplicate_rate": round(self.duplicate_rate, 4),
            "columns": [c.to_dict() for c in self.columns],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def summary(self) -> str:
        lines = [
            f"Dataset: {self.dataset_name}",
            f"Rows: {self.row_count:,} | Columns: {self.column_count}",
            f"Profiled at: {self.profiled_at}",
            f"Duplicate rows: {self.duplicate_rows} ({self.duplicate_rate * 100:.2f}%)",
            "",
            f"{'Column':<30} {'Type':<12} {'Nulls':>8} {'Null%':>7} {'Distinct':>10} {'Min':>15} {'Max':>15}",
            "-" * 100,
        ]
        for col in self.columns:
            lines.append(
                f"{col.column:<30} {col.inferred_type:<12} "
                f"{col.null_count:>8} {col.null_rate * 100:>6.1f}% "
                f"{col.distinct_count:>10} "
                f"{str(col.min_value)[:14]:>15} {str(col.max_value)[:14]:>15}"
            )
        return "\n".join(lines)


def _infer_type(series: pd.Series) -> str:
    """Infer a human-friendly type category from a pandas Series."""
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    # Try to parse as datetime
    non_null = series.dropna().astype(str)
    if len(non_null) > 0:
        sample = non_null.head(20)
        try:
            pd.to_datetime(sample, errors="raise")
            return "datetime"
        except (ValueError, TypeError):
            pass
    return "text"


class DataProfiler:
    """
    Auto-profile any pandas DataFrame and return rich statistics.

    Usage:
        profiler = DataProfiler()
        profile = profiler.profile(df, dataset_name="customers")
        print(profile.summary())
        report_dict = profile.to_dict()
    """

    def profile(self, df: pd.DataFrame, dataset_name: str) -> DatasetProfile:
        """
        Generate a full DatasetProfile for the given DataFrame.

        Args:
            df:            The DataFrame to profile.
            dataset_name:  Logical name for the dataset.

        Returns:
            DatasetProfile with column-level and dataset-level stats.
        """
        profiled_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        row_count = len(df)
        column_count = len(df.columns)

        # Whole-row duplicates
        duplicate_rows = int(df.duplicated().sum())
        duplicate_rate = duplicate_rows / row_count if row_count > 0 else 0.0

        column_profiles = []
        for col in df.columns:
            cp = self._profile_column(df[col], col, row_count)
            column_profiles.append(cp)

        return DatasetProfile(
            dataset_name=dataset_name,
            profiled_at=profiled_at,
            row_count=row_count,
            column_count=column_count,
            columns=column_profiles,
            duplicate_rows=duplicate_rows,
            duplicate_rate=duplicate_rate,
        )

    def _profile_column(self, series: pd.Series, col_name: str, total_count: int) -> ColumnProfile:
        """Profile a single pandas Series."""
        dtype_str = str(series.dtype)
        inferred_type = _infer_type(series)

        null_count = int(series.isna().sum())
        null_rate = null_count / total_count if total_count > 0 else 0.0
        non_null = series.dropna()
        non_null_count = len(non_null)
        distinct_count = int(non_null.nunique())
        distinct_rate = distinct_count / non_null_count if non_null_count > 0 else 0.0

        min_value = None
        max_value = None
        mean_value = None
        std_dev = None
        median_value = None

        if inferred_type == "numeric":
            numeric = pd.to_numeric(non_null, errors="coerce").dropna()
            if len(numeric) > 0:
                min_value = self._safe_val(numeric.min())
                max_value = self._safe_val(numeric.max())
                mean_value = float(round(numeric.mean(), 4))
                std_dev = float(round(numeric.std(), 4)) if len(numeric) > 1 else 0.0
                median_value = float(round(numeric.median(), 4))
        elif inferred_type == "datetime":
            try:
                parsed = pd.to_datetime(non_null, errors="coerce").dropna()
                if len(parsed) > 0:
                    min_value = str(parsed.min())
                    max_value = str(parsed.max())
            except (ValueError, TypeError):
                logger.warning("Could not parse datetime values for column '%s'", col_name)
        elif inferred_type == "text":
            if non_null_count > 0:
                strs = non_null.astype(str)
                lengths = strs.str.len()
                min_value = int(lengths.min())
                max_value = int(lengths.max())
                mean_value = float(round(lengths.mean(), 2))

        # Top-N most frequent values
        top_values = []
        if non_null_count > 0:
            vc = non_null.astype(str).value_counts().head(5)
            top_values = [{"value": k, "count": int(v)} for k, v in vc.items()]

        # Sample values (random 5, reproducible)
        sample_values = []
        if non_null_count > 0:
            n = min(5, non_null_count)
            try:
                sample_values = [str(v) for v in non_null.sample(n, random_state=42).tolist()]
            except (ValueError, TypeError):
                sample_values = [str(v) for v in non_null.head(n).tolist()]

        return ColumnProfile(
            column=col_name,
            dtype=dtype_str,
            inferred_type=inferred_type,
            total_count=total_count,
            null_count=null_count,
            null_rate=null_rate,
            distinct_count=distinct_count,
            distinct_rate=distinct_rate,
            min_value=min_value,
            max_value=max_value,
            mean_value=mean_value,
            std_dev=std_dev,
            median_value=median_value,
            top_values=top_values,
            sample_values=sample_values,
        )

    @staticmethod
    def _safe_val(v: Any) -> Any:
        """Convert numpy scalar to native Python type for JSON serialisation."""
        if hasattr(v, "item"):
            return v.item()
        return v
