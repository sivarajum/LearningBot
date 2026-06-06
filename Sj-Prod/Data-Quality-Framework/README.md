# Data Quality Framework

Rule-based data quality validation engine with 5 DQ dimensions, weighted scoring, profiling, and reporting. FastAPI API + Streamlit dashboard.

## What It Does

- **Data Profiling**: Automated statistical profiling of datasets (null rates, cardinality, distributions)
- **Rule-Based Validation**: 5 data quality dimensions — Completeness, Validity, Uniqueness, Consistency, Freshness
- **Weighted Scoring**: Configurable dimension weights for composite DQ scores
- **Reporting**: JSON reports with per-column and per-dimension breakdowns
- **REST API**: 8 FastAPI endpoints for profiling, validation, scoring
- **Dashboard**: Streamlit UI for interactive data quality exploration

## Architecture

```
src/data_generator.py     # Synthetic data (customers, transactions, products)
src/profiler.py           # Statistical data profiling
src/rules/                # DQ rule implementations
  completeness.py         # Null/missing checks
  validity.py             # Format/range validation
  uniqueness.py           # Duplicate detection
  consistency.py          # Cross-field consistency
  freshness.py            # Data recency checks
src/validator.py          # Rule orchestration engine
src/scorer.py             # Weighted DQ scoring
src/reporter.py           # JSON report generation
src/api.py                # FastAPI REST API
src/ui.py                 # Streamlit dashboard
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py pipeline    # Run full DQ pipeline
python main.py api         # API on :8001
python main.py ui          # Dashboard on :8501
python main.py all         # Both API + UI
```

## Testing

```bash
pytest                     # 155 tests
```

## Docker

```bash
docker compose up --build
```

See [RUNNING.md](RUNNING.md) for full build, test, and deployment instructions.
