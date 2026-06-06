# POC-09: Enterprise Data Quality Framework
## A Complete Guide for Data Architects and Principal Data Engineers

**Target audience:** Lead Data Engineers (10+ years) preparing for Data Architect / Principal DE interviews.
**Technology stack:** Pure Python + pandas. No Great Expectations, no Spark, no external DQ dependencies.
**Why custom?** Building from scratch demonstrates mastery of DQ mechanics — far more impressive in interviews than configuring a third-party tool.

---

## Table of Contents

1. [Why Data Quality Matters](#1-why-data-quality-matters)
2. [The 6 DQ Dimensions](#2-the-6-dq-dimensions)
3. [Framework Architecture](#3-framework-architecture)
4. [The Rules Engine](#4-the-rules-engine)
5. [Module Code Walkthrough](#5-module-code-walkthrough)
6. [Sample Datasets and Their Issues](#6-sample-datasets-and-their-issues)
7. [DQ Scoring Methodology](#7-dq-scoring-methodology)
8. [Running Validation: Step by Step](#8-running-validation-step-by-step)
9. [API Endpoints with curl Examples](#9-api-endpoints-with-curl-examples)
10. [Dashboard Walkthrough](#10-dashboard-walkthrough)
11. [Extending the Framework](#11-extending-the-framework)
12. [Mapping to Real Work](#12-mapping-to-real-work)
13. [Troubleshooting](#13-troubleshooting)
14. [Glossary](#14-glossary)

---

## 1. Why Data Quality Matters

### The Cost of Bad Data

The Gartner Institute estimated in 2017 that poor data quality costs organisations an average of **$12.9 million per year**. For large enterprises like FedEx or PayPal, the figure is orders of magnitude higher.

More importantly, bad data has non-linear consequences:

**Direct costs:**
- Failed ETL jobs requiring manual re-runs (engineering time)
- Incorrect invoices requiring reprocessing (finance time + customer trust)
- Misrouted shipments (operational cost + customer SLA violation)

**Indirect costs:**
- ML models trained on bad data produce subtly wrong predictions — the worst kind of failure because you don't know it's happening
- Regulatory fines from incorrect compliance reporting (GDPR, SOX, PCI-DSS)
- Business decisions made on wrong dashboards — compounded over months

### Real Examples from Financial Services

**PayPal (payment processing context):**
- A 5% null rate on `merchant_id` meant 1 in 20 transactions could not be settled to the correct merchant. The settlement batch failed silently every Friday, requiring 3 hours of manual reconciliation.
- Duplicate `transaction_id` values from a misconfigured retry mechanism caused double-posting in the ledger — a P0 incident that took 6 hours to detect.
- Stale fraud model inputs (6-hour-old transaction data) meant a new fraud attack pattern went undetected for one full batch cycle, resulting in $500K in losses.

**FedEx (logistics / supply chain context):**
- Invalid `delivery_zip_code` (nulls, 4-digit ZIPs instead of 5-digit) caused routing failures affecting 0.3% of packages daily — at FedEx scale, that's tens of thousands of mis-routed packages per day.
- Orphaned `shipment_id` records (no corresponding pickup record) blocked the monthly revenue reconciliation process for 3 working days, delaying financial close.
- Package status timestamps with `delivery_date < pickup_date` (impossible timeline) corrupted SLA reporting, making on-time delivery look better than it was.

### The Rule of Ten

The cost of fixing a data quality issue increases roughly **10x at each stage** of the data pipeline:
- Fix at source system: **$1**
- Fix at ingestion/ETL: **$10**
- Fix in the data warehouse: **$100**
- Fix in a downstream BI report: **$1,000**
- Fix after a business decision is made: **$10,000+**

This is why DQ frameworks focus on catching issues early — at ingestion time — before bad data propagates downstream.

---

## 2. The 6 DQ Dimensions

The industry recognises 6 core data quality dimensions. This framework implements 5 (accuracy is discussed below).

### 2.1 Completeness
**Definition:** The degree to which all required data values are present.

**Metric:** `(non-null count) / (total count)` = completeness ratio

**When to use which rule:**
- `NotNullRule`: Mandatory fields that must never be null (primary keys, required IDs)
- `CompletenessRatioRule`: Fields that are usually populated but allow some nulls (phone numbers, middle names)

**Threshold guidance:**
- Primary keys: 100% completeness required
- Foreign keys: 100% (use with ReferentialIntegrityRule)
- Contact fields (phone, secondary email): 85%+ acceptable
- Optional enrichment fields: 50%+ depending on business need

### 2.2 Validity
**Definition:** The degree to which data conforms to defined formats, types, ranges, and business rules.

**This is the broadest dimension** — covers format validation, type checking, range constraints, and categorical values.

**Rule types:**
- `RegexRule`: Email format, phone format, zip code, tracking number patterns
- `ValueRangeRule`: Age 0–120, amount > 0, rating 1–5, percentage 0–100
- `AllowedValuesRule`: Status codes, currency codes, country codes, category labels
- `TypeRule`: Columns that should be integers, floats, or parseable dates

**Interview insight:** Validity rules are where the richest business logic lives. A sophisticated DQ framework lets business analysts define validity rules in configuration (JSON/YAML) without writing code — this is what you built here.

### 2.3 Uniqueness
**Definition:** The degree to which data values are free from unintended duplication.

**Note:** "Unintended" is key — some duplication is expected (same customer can have multiple transactions).

**Rule types:**
- `UniqueRule`: Columns that must be globally unique (primary keys, transaction IDs, tracking numbers)
- `UniquenessRatioRule`: Columns that should be "mostly" unique but allow some overlap (email addresses — one person may have multiple accounts)

**Deduplication strategy:**
1. Detect with UniqueRule
2. Profile with DataProfiler (see distinct_rate)
3. Remediate: choose canonical record (most recent, most complete, merge)
4. Implement prevention: add unique constraint at source

### 2.4 Consistency
**Definition:** The degree to which data values are logically coherent within and across datasets.

**Two types:**
1. **Referential integrity:** Values in column A must exist in another table's column B
   - `transaction.customer_id` must exist in `customers.customer_id`
   - `order.product_id` must exist in `products.product_id`

2. **Cross-column consistency:** Logical relationship between two columns in the same row
   - `end_date >= start_date`
   - `delivery_date >= pickup_date`
   - `total_amount == unit_price * quantity` (derived field consistency)

**Enterprise pattern — consistency across systems:**
Beyond what this framework implements, real enterprise consistency checks compare the same entity across multiple source systems. For example: does the customer address in the CRM match the address in the billing system? This requires joining data from multiple sources before running rules.

### 2.5 Freshness
**Definition:** The degree to which data is sufficiently recent for its intended use.

**Why it's weighted lowest (10%):** Freshness is highly context-dependent. A customer master table updated monthly is fine; a real-time fraud model needing sub-second data would fail a 24-hour freshness check.

**Rule:** `DataFreshnessRule` checks the maximum date in a timestamp column against a configurable age threshold.

**Typical SLAs by use case:**
- Real-time fraud detection: < 1 minute
- Near-real-time dashboards: < 1 hour
- Operational reporting: < 24 hours
- Strategic analytics: < 7 days
- Regulatory reporting: per regulatory schedule (monthly/quarterly)

### 2.6 Accuracy (not implemented — intentional design choice)
**Definition:** The degree to which data correctly describes the real-world entity it represents.

**Why not implemented:** Accuracy is the hardest dimension to measure automatically because it requires comparing data against an authoritative external source (the real world). For example: "Is this customer's address correct?" requires a geocoding API or address validation service.

**In practice:** Accuracy is often approximated by Validity (format/range checks) and Consistency (cross-system comparison). True accuracy measurement requires domain-specific authoritative reference data.

---

## 3. Framework Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Enterprise DQ Framework — Layers           │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Configuration (config/dq_rules.json)          │
│           Rule definitions per dataset, severities       │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Data Generator (src/data_generator.py)        │
│           Synthetic data with known DQ issues            │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Rules Engine (src/rules/)                      │
│           BaseRule (ABC) → 11 concrete rule classes     │
│           RuleResult (dataclass)                        │
├─────────────────────────────────────────────────────────┤
│  Layer 4: DataProfiler (src/profiler.py)                │
│           Auto-stats: null rates, cardinality, ranges   │
├─────────────────────────────────────────────────────────┤
│  Layer 5: DQValidator (src/validator.py)                │
│           Orchestrates rules → ValidationResult         │
├─────────────────────────────────────────────────────────┤
│  Layer 6: DQScorer (src/scorer.py)                      │
│           ValidationResult → DQScoreCard (0-100, A-F)  │
├─────────────────────────────────────────────────────────┤
│  Layer 7: DQReporter (src/reporter.py)                  │
│           Full JSON report + alerts + recommendations   │
├─────────────────────────────────────────────────────────┤
│  Layer 8: FastAPI (src/api.py)                         │
│           REST interface: /validate, /score, /profile  │
├─────────────────────────────────────────────────────────┤
│  Layer 9: Streamlit UI (src/ui.py)                     │
│           Gauges, heatmaps, rule tables, concept guide  │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

**1. Single Responsibility:** Each layer does exactly one thing. The validator doesn't score; the scorer doesn't report; the reporter doesn't profile.

**2. Configuration-driven rules:** Business analysts can add rules in JSON without touching Python code. This is a key selling point in enterprise environments where data owners want to maintain their own DQ rules.

**3. Graceful degradation:** Rule-level exceptions are caught and reported as failing rules, not framework crashes. A pipeline with 30 rules can report on 29 of them even if one throws.

**4. Extensible base class:** `BaseRule` provides helper methods (`_check_column_exists`, `_build_result`) so new rule implementations are minimal — just the business logic.

**5. Dataclass-first:** All result objects (`RuleResult`, `ValidationResult`, `DQScoreCard`) are Python dataclasses, not raw dicts. This provides IDE auto-completion, type safety, and clean `.to_dict()` serialisation.

---

## 4. The Rules Engine

### BaseRule Contract

Every rule in this framework follows a strict contract:

```python
class BaseRule(ABC):
    dimension: str   # Set at class level

    def __init__(self, name: str, column: str, severity: str):
        # name     = unique identifier for this rule instance
        # column   = which column to check
        # severity = "error" | "warning" | "info"

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> RuleResult:
        # Input:  any pandas DataFrame
        # Output: RuleResult with score, counts, details
```

### RuleResult Fields

```
rule_name      String identifier
column         Column checked
dimension      DQ dimension (completeness / validity / etc.)
severity       error | warning | info
passed         True if zero violations (score == 1.0)
score          0.0 – 1.0  (pass_rate for most rules)
failing_count  Number of rows that violated the rule
total_count    Total rows evaluated
pass_rate      (total - failing) / total
details        Human-readable explanation
failing_values Sample of up to 10 failing values (for debugging)
```

### Severity Semantics

| Severity | Meaning | Effect on overall_passed |
|----------|---------|--------------------------|
| error    | Rule failure = data is unfit for use | Failing error rules set overall_passed = False |
| warning  | Issue to investigate, doesn't block pipeline | Does not affect overall_passed |
| info     | Informational only, for monitoring | Does not affect overall_passed |

This mirrors production DQ frameworks: error rules can gate a pipeline; warning rules generate alerts; info rules populate dashboards.

### Rule Catalogue

| Rule Class | Dimension | Key Parameter(s) |
|-----------|-----------|-----------------|
| `NotNullRule` | completeness | — |
| `CompletenessRatioRule` | completeness | `threshold` (default 5%) |
| `RegexRule` | validity | `pattern` (regex string) |
| `ValueRangeRule` | validity | `min_val`, `max_val` |
| `AllowedValuesRule` | validity | `allowed_values` (set) |
| `TypeRule` | validity | `expected_type` (int/float/str/bool/date) |
| `UniqueRule` | uniqueness | — |
| `UniquenessRatioRule` | uniqueness | `threshold` (default 95%) |
| `ReferentialIntegrityRule` | consistency | `reference_values` (set) |
| `CrossColumnRule` | consistency | `column_b`, `operator` (>=, <=, ==, etc.) |
| `DataFreshnessRule` | freshness | `max_age_hours` (default 48) |

---

## 5. Module Code Walkthrough

### 5.1 src/rules/base_rule.py

The abstract foundation. Key design decisions:

**`_check_column_exists()`** — Called at the start of every rule's `validate()`. Returns a pre-built failing `RuleResult` if the column is missing. This prevents KeyError crashes and gives a clean error message.

**`_build_result()`** — Convenience helper that takes a boolean mask of failing rows and builds a `RuleResult`. This eliminates copy-paste arithmetic across all rule implementations:
```python
failing_count = int(failing_mask.sum())
pass_rate = (total - failing_count) / total
score = pass_rate
```

### 5.2 src/rules/completeness.py

**`NotNullRule`** — Treats both `NaN` and empty strings (`""`, `"  "`) as null. This is important because many CSV sources use empty strings instead of proper nulls.

**`CompletenessRatioRule`** — The `score` calculation is nuanced: if null_rate <= threshold, score = 1.0 (you met the bar, no penalty). If over threshold, score degrades proportionally between the threshold and 100% null.

### 5.3 src/rules/validity.py

**`RegexRule`** — Compiles the regex once at init time (performance). Skips nulls — use `NotNullRule` separately if nulls should also count as violations.

**`ValueRangeRule`** — Uses `pd.to_numeric(errors="coerce")` to handle mixed-type columns gracefully. Non-numeric values that can't be coerced also count as failures.

**`AllowedValuesRule`** — Converts all values to strings for comparison. This handles cases where the DataFrame has integer `1` and the allowed set has string `"1"`.

**`TypeRule`** — Supports 5 types: `int`, `float`, `str`, `bool`, `date`. The `date` type uses `pd.to_datetime()` for broad format support.

### 5.4 src/rules/uniqueness.py

**`UniqueRule`** — Uses `Series.duplicated(keep="first")` to mark all duplicate occurrences except the first. `failing_count` = the number of "extra" duplicate rows.

**`UniquenessRatioRule`** — The score formula: `min(1.0, uniqueness_ratio / threshold)`. If uniqueness is 90% and threshold is 95%, score = 0.9/0.95 = 0.947. This gives proportional credit rather than a binary pass/fail.

### 5.5 src/rules/consistency.py

**`ReferentialIntegrityRule`** — Normalises both the column values and the reference set to strings before comparison. This handles type mismatches (int IDs vs string IDs) cleanly.

**`CrossColumnRule`** — Tries numeric comparison first, then datetime, then raw. This handles most real-world cases: comparing two date columns, two numeric amounts, or two string codes.

### 5.6 src/profiler.py

The `DataProfiler` auto-detects column types using `_infer_type()`:
1. Check pandas dtype first (bool, numeric, datetime64)
2. If dtype is `object`, sample 20 values and try `pd.to_datetime()` — catches date-as-string columns
3. Default to "text"

For numeric columns: computes min, max, mean, std, median.
For datetime columns: computes min and max date.
For text columns: min/max are string lengths; mean is average string length.

`top_values` uses `value_counts().head(5)` — invaluable for understanding categorical distributions.

### 5.7 src/validator.py

The validator's `_summarise_by_dimension()` computes per-dimension stats as a dict:
```python
{
    "completeness": {
        "total_rules": 3, "passed": 2, "failed": 1, "avg_score": 0.96
    }, ...
}
```

The `overall_passed` flag is set to False if any **error-severity** rule fails. Warning and info rules never block the pipeline.

### 5.8 src/scorer.py

The weighted scoring formula:
```
overall_score = sum(dimension_score * weight for each dimension) * 100
```

If a dimension has zero rules configured (e.g., no freshness rules), it contributes a neutral score of 1.0 weighted at its weight. This avoids penalising datasets for unconfigured dimensions.

### 5.9 src/reporter.py

The `_generate_recommendations()` function uses rule metadata to generate domain-specific remediation advice. It knows that a `completeness` failure on a rate < 50% is critical and suggests investigating the upstream ETL, while a `validity` failure on a `regex` rule suggests adding input validation at the source.

---

## 6. Sample Datasets and Their Issues

### Dataset 1: customers (500 rows)

**Represents:** CRM / user master table (similar to PayPal's customer onboarding data)

| Column | Type | Intentional Issues |
|--------|------|--------------------|
| customer_id | string | ~1% null, ~3% duplicates |
| email | string | ~5% null, ~4% invalid format (missing @) |
| age | integer | ~2% negative (< 0), ~1% > 120 |
| status | string | ~2% invalid values (ACTIVE, SUSPENDED) |
| first_name | string | ~3% null |
| phone | string | ~8% null |
| signup_date | date | ~1% future dates |

**DQ rules configured:** 10 rules across completeness, validity, uniqueness, freshness

**Expected score:** ~72-78 (Grade B/C) — several issues but mostly valid data

### Dataset 2: transactions (2000 rows)

**Represents:** Payment transaction fact table (similar to PayPal's payment records)

| Column | Type | Intentional Issues |
|--------|------|--------------------|
| transaction_id | string | ~1% duplicates |
| customer_id | string | ~6% orphaned (not in customers table) |
| amount | float | ~4% null, ~3% negative |
| transaction_date | datetime | ~5% future dates |
| transaction_type | string | ~2% null |

**DQ rules configured:** 9 rules + 1 referential integrity rule at runtime

**Expected score:** ~65-72 (Grade C) — referential integrity violations and negative amounts drag the score down

### Dataset 3: products (100 rows)

**Represents:** Product catalog / dimension table

| Column | Type | Intentional Issues |
|--------|------|--------------------|
| product_code | string | ~4% duplicates |
| product_name | string | ~3% null |
| category | string | ~5% invalid (not in allowed list) |
| price | float | ~2% negative |
| stock_quantity | integer | ~6% null |

**DQ rules configured:** 7 rules

**Expected score:** ~74-80 (Grade B/C) — smaller dataset with moderate issues

---

## 7. DQ Scoring Methodology

### Dimension Weights

The weights reflect how data quality issues typically impact downstream systems:

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| Completeness | 30% | Missing data is the most common issue and blocks the most processes |
| Validity | 25% | Format/range violations cause ETL failures and incorrect analytics |
| Uniqueness | 20% | Duplicates corrupt aggregations and are expensive to clean |
| Consistency | 15% | Cross-dataset issues are harder to detect and fix |
| Freshness | 10% | Recency is context-dependent; many batch use cases are tolerant |

**Adjusting weights:** These weights are a starting point. In a real deployment, adjust based on your domain:
- For real-time fraud: increase Freshness to 25%, reduce Completeness to 20%
- For regulatory reporting: increase Validity to 35%, increase Consistency to 20%
- For ML feature stores: increase Completeness to 35%, increase Freshness to 20%

### Score Calculation

```
For each rule:
    rule_score = (passing rows) / (total rows)  [0.0 – 1.0]

For each dimension:
    dimension_score = mean(rule_scores in that dimension)  [0.0 – 1.0]

Overall score:
    = sum(dimension_score_i * weight_i for all dimensions) * 100  [0 – 100]
```

### Grade Thresholds

| Grade | Score | Business Interpretation |
|-------|-------|------------------------|
| A | 90–100 | Production-ready. Data meets all quality standards. |
| B | 75–89 | Good quality. Minor issues to investigate; suitable for most use cases. |
| C | 60–74 | Fair quality. Significant issues requiring remediation before critical use. |
| D | 45–59 | Poor quality. Serious problems. Investigate root cause before using data. |
| F | < 45 | Failing. Data should not be used for business decisions. |

### Interpreting Scores by Dimension

When a specific dimension score is low, it points to a specific type of problem:
- **Low completeness score:** Source system has null issues; ETL drops values; schema mismatch
- **Low validity score:** Input validation missing at source; data migration without format normalisation
- **Low uniqueness score:** Retry logic creating duplicates; CDC processing issues; merge errors
- **Low consistency score:** Load order wrong (child before parent); cross-system sync issues
- **Low freshness score:** Pipeline schedule missed; upstream SLA breach; job failure

---

## 8. Running Validation: Step by Step

### Prerequisites

```bash
cd /path/to/POC-09-Data-Quality-Framework
pip install -r requirements.txt
```

### Step 1: Generate Data + Validate (all in one)

```bash
python main.py validate
```

This runs the full pipeline:
1. Generates `data/customers.csv`, `data/transactions.csv`, `data/products.csv` (if not present)
2. Profiles each dataset
3. Loads rules from `config/dq_rules.json`
4. Runs DQValidator on each dataset
5. Computes DQScoreCard per dataset
6. Generates JSON reports in `reports/`
7. Prints scorecards to stdout

### Step 2: Review the Output

The console output shows:
```
Dataset Profile:
  Column stats (null counts, distinct counts, min/max)

Validation Summary:
  Rules run, passed, failed
  Detailed failure list with failing_count / total

DQ Scorecard:
  Overall score: 74.3 / 100   Grade: C
  Completeness:  91.2  [A]
  Validity:      68.4  [C]
  Uniqueness:    82.1  [B]
  Consistency:   71.3  [C]
  Freshness:     100.0 [A]

Cross-Dataset Summary:
  customers    : 76.1  B
  transactions : 68.4  C
  products     : 74.9  C
```

### Step 3: Review JSON Reports

Reports are saved to `reports/dq_report_{dataset}_{timestamp}.json`:

```json
{
  "metadata": {
    "generated_at": "2026-05-18T10:30:00Z",
    "framework_version": "1.0.0",
    "dataset_name": "customers"
  },
  "scorecard": { "overall_score": 76.1, "overall_grade": "B", ... },
  "profile": { "row_count": 500, "columns": [...] },
  "validation": { "total_rules": 11, "rule_results": [...] },
  "alerts": [ { "severity": "error", "rule_name": "age_valid_range", ... } ],
  "recommendations": [ "Column 'age' has 12 out-of-range values..." ]
}
```

---

## 9. API Endpoints with curl Examples

### Start the API

```bash
python main.py api
# or
uvicorn src.api:app --reload --port 8000
```

Open interactive docs: http://localhost:8000/docs

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "framework": "Enterprise Data Quality Framework",
  "version": "1.0.0",
  "datasets_loaded": ["customers", "transactions", "products"]
}
```

### List Datasets

```bash
curl http://localhost:8000/datasets
```

### Get Dataset Profile

```bash
curl http://localhost:8000/datasets/customers/profile | python -m json.tool
```

Returns column-level stats: null rates, distinct counts, min/max, sample values.

### Run DQ Validation (Full Report)

```bash
curl -X POST http://localhost:8000/datasets/customers/validate | python -m json.tool
```

Returns the complete report: scorecard + profile + validation results + alerts + recommendations.

### Get Scorecard Only

```bash
curl http://localhost:8000/datasets/customers/score
```

Response:
```json
{
  "dataset_name": "customers",
  "overall_score": 76.1,
  "overall_grade": "B",
  "grade_description": "Good — minor issues, monitor closely",
  "dimensions": {
    "completeness": { "score": 91.2, "grade": "A", "passed_rules": 4, "rule_count": 4 },
    "validity": { "score": 68.4, "grade": "C", ... },
    ...
  }
}
```

### List Rules for a Dataset

```bash
curl http://localhost:8000/datasets/transactions/rules
```

### Cross-Dataset Summary

```bash
curl http://localhost:8000/summary
```

### DQ Concepts

```bash
curl http://localhost:8000/concepts | python -m json.tool
```

---

## 10. Dashboard Walkthrough

### Start the Dashboard

```bash
streamlit run src/ui.py
```

Open: http://localhost:8501

### Tab 1: DQ Dashboard

**Overview of all three datasets:**
- Top metrics row: datasets monitored, average DQ score, total rules, critical issues
- Per-dataset gauge charts (0–100 with colour-coded zones)
- Letter grade badges (A–F with colour coding)
- Dimension heatmap: score by dimension × dataset (colour-coded 0–100)
- Issue summary table: critical (error-severity) failures

**How to read the heatmap:**
- Green cells: dimension score ≥ 75 — healthy
- Yellow cells: 60–74 — needs attention
- Red/orange cells: < 60 — critical problems

### Tab 2: Dataset Explorer

**Select a dataset to explore:**
- Top metrics: row count, column count, duplicate rows, duplicate rate
- Column profile table: type, null count, null %, distinct count, distinct %, min, max, mean
- Null rate bar chart: visual representation of completeness per column
- Raw data sample (first 20 rows)

**How to use this tab:**
1. Look for columns with high null % — those are your completeness issues
2. Compare distinct % to expected — a "status" column with 100% distinct means it's probably free-text, not a proper categorical
3. Check min/max for range violations (negative ages, future dates)

### Tab 3: Validation Results

**Detailed rule-by-rule breakdown:**
- Scorecard with gauge chart, letter grade, rule pass/fail counts
- Dimension scores with progress bars and rule counts
- Filterable rule results table (filter by severity and pass/fail status)
- Colour-coded rows: green = PASS, red = FAIL
- Alert list: all failing rules formatted as error/warning/info alerts
- Recommendations: auto-generated remediation suggestions

**How to investigate a failing rule:**
1. Filter to FAIL status
2. Note the `Failures` count and `Pass Rate` columns
3. Click on the rule name to see `details` (the full explanation)
4. Look at the `failing_values` in the full report (via API) for sample bad data

### Tab 4: DQ Concepts

**Educational reference:**
- Expandable sections for each DQ dimension with definition, examples, rules, and real-world impact
- Scoring methodology: how weights work, grade thresholds
- Architecture diagram: all framework layers
- How to add a custom rule: code walkthrough

---

## 11. Extending the Framework

### Adding a New Rule

**Step 1:** Create the rule class in the appropriate file.

```python
# src/rules/validity.py — add a phone format rule

class PhoneFormatRule(BaseRule):
    """Validates international phone number format."""
    dimension = "validity"

    def __init__(self, name: str, column: str, severity: str = "warning"):
        super().__init__(name=name, column=column, severity=severity)
        import re
        # E.164 format: +1234567890 (7-15 digits)
        self._pattern = re.compile(r'^\+?[1-9]\d{6,14}$')

    def validate(self, df: pd.DataFrame) -> RuleResult:
        missing = self._check_column_exists(df)
        if missing:
            return missing

        non_null = df[self.column].dropna()
        # Strip spaces, dashes, parens for comparison
        cleaned = non_null.astype(str).str.replace(r'[\s\-\(\)]', '', regex=True)
        failing_in_nonnull = ~cleaned.str.match(self._pattern)

        # Map back to full DataFrame index
        failing_full = pd.Series(False, index=df.index)
        failing_full[non_null[failing_in_nonnull].index] = True

        return self._build_result(
            df, failing_mask=failing_full,
            details=f"Column '{self.column}': {failing_in_nonnull.sum()} invalid phone numbers."
        )
```

**Step 2:** Export from `src/rules/__init__.py`.

```python
from .validity import RegexRule, ValueRangeRule, AllowedValuesRule, TypeRule, PhoneFormatRule
```

**Step 3:** Add to `config/dq_rules.json`.

```json
{
  "rule": "PhoneFormatRule",
  "name": "customer_phone_format",
  "column": "phone",
  "severity": "warning"
}
```

**Step 4:** Add to the rule factory in `src/api.py`.

```python
elif rule_type == "PhoneFormatRule":
    rules.append(cls(name=name, column=column, severity=severity))
```

### Adding a New Dataset

**Step 1:** Add the dataset to `DataGenerator` or load it in `load_or_generate()`.

**Step 2:** Add rules for it in `config/dq_rules.json`.

**Step 3:** If it has referential integrity with another dataset, add it to `_add_referential_rules()` in `api.py`.

### Connecting to a Real Database

Replace the CSV loading in `data_generator.py` with a database query:

```python
import sqlalchemy

def load_from_database(connection_string: str, table_name: str) -> pd.DataFrame:
    engine = sqlalchemy.create_engine(connection_string)
    return pd.read_sql_table(table_name, engine)
```

The rest of the framework (profiler, validator, scorer, reporter) works with any pandas DataFrame regardless of source.

### Integrating with Great Expectations

This custom framework and Great Expectations are not mutually exclusive. You can:
1. Use this framework's profiler output to auto-generate GX Expectations
2. Run GX validations alongside custom rules in the same DQValidator
3. Use this framework's scorer on top of GX validation results

```python
# Wrapping a GE checkpoint result in a custom RuleResult
def ge_checkpoint_to_rule_result(ge_result, rule_name, column) -> RuleResult:
    stats = ge_result.statistics
    return RuleResult(
        rule_name=rule_name,
        column=column,
        dimension="validity",
        severity="error",
        passed=ge_result.success,
        score=stats["success_percent"] / 100,
        failing_count=int(stats.get("unsuccessful_expectations", 0)),
        total_count=int(stats.get("evaluated_expectations", 0)),
        pass_rate=stats["success_percent"] / 100,
        details=f"Great Expectations result: {ge_result.success}",
    )
```

### Scheduling DQ Checks (Production Pattern)

In production, DQ checks run on a schedule using an orchestration tool:

**Apache Airflow:**
```python
from airflow.decorators import task, dag
from datetime import datetime

@dag(schedule_interval="0 6 * * *", start_date=datetime(2026, 1, 1))
def daily_dq_check():
    @task
    def run_customers_dq():
        import sys
        sys.path.insert(0, "/opt/airflow/dags/dq_framework")
        from main import run_validate
        results = run_validate(verbose=False)
        if results["customers"]["overall_grade"] in ["D", "F"]:
            raise ValueError(f"Customers DQ grade {results['customers']['overall_grade']} — blocking pipeline")
        return results

    run_customers_dq()
```

---

## 12. Mapping to Real Work

### FedEx Migration DQ Scenario

**Context:** FedEx migrating package tracking data from legacy COBOL system to new cloud platform. 50 million records, 200+ columns.

**How this framework would apply:**

1. **Pre-migration profiling:** Run `DataProfiler` on source system extract to baseline all column stats (null rates, distinct counts, value distributions).

2. **Rule definition:** Work with logistics SMEs to define rules:
   - `NotNullRule` on `tracking_number`, `pickup_date`, `origin_zip`, `destination_zip`
   - `RegexRule` on `tracking_number` for format `[0-9]{12}`
   - `ValueRangeRule` on `weight_lbs` for 0.1 – 150
   - `AllowedValuesRule` on `service_type` for `{"GROUND", "EXPRESS", "OVERNIGHT"}`
   - `CrossColumnRule` on `delivery_date >= pickup_date`
   - `ReferentialIntegrityRule` on `destination_facility_id` against facility master

3. **Mid-migration validation:** Run DQValidator after each batch. Gate promotion to production on DQ score ≥ 85 (Grade B).

4. **Post-migration comparison:** Compare pre-migration vs post-migration profiles. Any column where null_rate increased by more than 1% is a migration issue.

5. **Ongoing monitoring:** Run freshness checks daily. Alert if `max(pickup_date)` is more than 2 hours old.

### PayPal Data Accuracy Checks

**Context:** PayPal running monthly accuracy checks on payment data fed to risk models.

**How this framework would apply:**

1. **Transaction completeness:** `NotNullRule` on `merchant_id`, `amount`, `customer_id`, `transaction_date`. Any null on these is a P1.

2. **Amount validity:** `ValueRangeRule` on `amount` for 0.01 – 100,000. Amounts outside this range flagged for manual review.

3. **Idempotency check:** `UniqueRule` on `transaction_id`. Any duplicate = potential double-posting. Triggers automatic ledger audit.

4. **Referential integrity:** All `customer_id` values must exist in the customer master. Orphaned transactions can't be attributed to accounts.

5. **Freshness for fraud model:** `DataFreshnessRule` on `transaction_date` with `max_age_hours=1`. If the most recent transaction in the batch is more than 1 hour old, the fraud model run is blocked.

6. **Cross-system consistency:** Compare transaction amounts between the payment processing system and the settlement system. Any discrepancy > $0.01 triggers reconciliation.

**Governance integration:** DQ score below 90 automatically creates a JIRA ticket assigned to the data engineering team. Score below 80 pages the on-call engineer.

---

## 13. Troubleshooting

### "No module named 'src'"

Ensure you're running from the project root:
```bash
cd /path/to/POC-09-Data-Quality-Framework
python main.py validate
```

Or set PYTHONPATH:
```bash
export PYTHONPATH=/path/to/POC-09-Data-Quality-Framework
python main.py validate
```

### "FileNotFoundError: config/dq_rules.json"

Run from the project root directory. The config path is resolved relative to `main.py`'s location.

### "No rules configured for dataset"

Check `config/dq_rules.json` — the key must exactly match the dataset name (case-sensitive).

### "Rule execution error: ..."

A rule threw an exception during validation. The error is captured in the `details` field of the corresponding `RuleResult`. Common causes:
- Column doesn't exist (use `_check_column_exists` — it's already in every rule)
- Data type mismatch (add `errors="coerce"` to `pd.to_numeric()`)
- Empty DataFrame (add empty-check before `.value_counts()`)

### Streamlit cache issues

If data doesn't refresh after regeneration:
```bash
# In the sidebar: click "Clear Cache & Reload"
# Or stop Streamlit (Ctrl+C) and restart
```

### FastAPI startup slow

Data generation happens at import time in `api.py`. The first startup generates all three datasets (usually < 2 seconds). Subsequent startups load from CSV.

### Port already in use

```bash
# For API (port 8000)
lsof -ti:8000 | xargs kill -9
# For Streamlit (port 8501)
lsof -ti:8501 | xargs kill -9
```

---

## 14. Glossary

**Accuracy** — The degree to which data correctly represents the real-world entity. Not implemented in this framework; requires external authoritative reference.

**Alert** — A notification generated when a DQ rule fails. Severity: error, warning, or info.

**BaseRule** — The abstract base class that all DQ rules in this framework inherit from. Defines the `validate(df) -> RuleResult` contract.

**Cardinality** — The number of distinct values in a column. High cardinality = many unique values (e.g., IDs). Low cardinality = few unique values (e.g., status codes).

**Completeness** — DQ dimension measuring the presence of required data values.

**Consistency** — DQ dimension measuring logical coherence within and across datasets.

**Data Catalog** — A metadata repository that describes data assets, their schemas, and their lineage. DQ scores can be published to a data catalog (e.g., Alation, Collibra, DataHub).

**Data Lineage** — The provenance of a data asset: where it came from, how it was transformed, where it goes. Essential for root-cause analysis of DQ issues.

**DataProfiler** — The framework component that auto-generates statistical summaries of any DataFrame without requiring schema knowledge.

**DatasetProfile** — The output of DataProfiler: a collection of ColumnProfile objects plus dataset-level stats.

**DQ Dimension** — A category of data quality measurement. This framework implements: completeness, validity, uniqueness, consistency, freshness.

**DQReporter** — The framework component that assembles profile + validation + scorecard into a single JSON report with alerts and recommendations.

**DQScoreCard** — The output of DQScorer: overall DQ score (0-100), letter grade, and per-dimension breakdown.

**DQScorer** — The framework component that translates raw rule results into weighted scores and letter grades.

**DQValidator** — The framework component that orchestrates rule execution against a DataFrame and returns a ValidationResult.

**Failing count** — The number of rows in a dataset that violate a specific DQ rule.

**Freshness** — DQ dimension measuring data recency relative to its intended use.

**Grade** — Letter grade (A-F) assigned based on the overall DQ score: A ≥ 90, B ≥ 75, C ≥ 60, D ≥ 45, F < 45.

**Idempotency** — The property of an operation where running it multiple times produces the same result. In DQ: duplicate transaction IDs can indicate non-idempotent write operations.

**Null rate** — The fraction of rows in a column that have null (or empty) values. `null_count / total_count`.

**Orphaned record** — A record in a child table (e.g., transactions) that references a non-existent parent record (e.g., customer). Detected by ReferentialIntegrityRule.

**Pass rate** — The fraction of rows that pass a specific DQ rule. `(total - failing_count) / total`.

**Profiling** — The process of computing statistical summaries of a dataset to understand its structure, content, and quality characteristics.

**Referential integrity** — The consistency constraint that values in a foreign key column must exist in the referenced primary key column.

**Rule** — A specific, measurable assertion about data quality. Implemented as a class inheriting from BaseRule.

**RuleResult** — The dataclass output of a single rule's validation: pass/fail, score, counts, and explanation.

**Severity** — The business impact level of a rule violation: `error` (blocks pipeline), `warning` (alerts only), `info` (monitoring only).

**Uniqueness** — DQ dimension measuring freedom from unintended duplication.

**Validity** — DQ dimension measuring conformance to defined formats, types, ranges, and allowed values.

**ValidationResult** — The output of DQValidator: collection of all RuleResult objects with summary statistics.

**Weighted score** — The overall DQ score calculated as a weighted average of dimension scores. Weights reflect business priority.

---

## 15. Interview Questions

### Situation: A data analyst reports that last month's revenue figure in the BI dashboard is negative $200K. You own the data pipeline. Walk me through your investigation.

Negative revenue is a data quality issue masquerading as a business anomaly. My investigation steps:

**1. Isolate the layer:** Query each layer of the pipeline — source extract, Bronze raw, Silver cleansed, Gold aggregation — to find where the negative number first appears. If it's in the source, it's an upstream problem. If it only appears in Gold, it's a transformation bug.

**2. Check for duplicate transactions with inverted signs:** A common cause is a CDC (Change Data Capture) feed that emits a delete as a negative-value row. If `UniqueRule` on `transaction_id` was failing silently, duplicate rows with sign-flipped amounts sum to negative. This is why `UniquenessRule` on financial tables must be a P1 alert, not a warning.

**3. Check cross-column consistency:** `CrossColumnRule` would catch `refund_amount > transaction_amount` or `transaction_date > settlement_date`. Either could indicate mis-joins producing Cartesian products or fan-out multiplication.

**4. Check the join logic:** If a LEFT JOIN was recently changed to a FULL OUTER JOIN, or an aggregation's `GROUP BY` dropped a dimension, one month's data could be summed at the wrong grain.

**5. Trace to a specific batch:** Use `DataFreshnessRule` audit timestamps to identify which ingestion batch introduced the anomaly.

**Prevention going forward:** Add a `ValueRangeRule` on `monthly_revenue` in the Gold model with `min_value=0` (or a business-approved floor). Add a `CrossColumnRule` asserting `this_month_revenue BETWEEN last_month_revenue * 0.5 AND last_month_revenue * 2` as a sanity-check alert. Any violation halts promotion to the reporting layer.

---

### Situation: A new VP of Data asks you to "improve our data quality" in 90 days. You have no budget for new tools. How do you structure the programme?

**Days 1–30 — Baseline and prioritise:**
- Run the `DataProfiler` on all production datasets. You cannot improve what you cannot measure. Document null rates, cardinality, and freshness for every table that feeds a BI dashboard or ML model.
- Interview data consumers: which datasets cause the most rework? Prioritise those. Business pain > theoretical completeness.
- Classify each dataset by DQ grade using the scoring framework. Anything below Grade C is an immediate remediation candidate.

**Days 31–60 — Fix the top 3 datasets:**
- For each priority dataset, define rules in consultation with the data owner (not just engineers). Rules without business sign-off get ignored or miscalibrated.
- Implement `error`-severity rules that block pipeline promotion and `warning`-severity rules that alert but don't block. Too many blocking rules = alert fatigue.
- Instrument the DQ scores into the existing monitoring stack (Grafana, DataDog, or even a Slack bot). Visibility creates accountability.

**Days 61–90 — Governance and sustainability:**
- Add DQ gate tasks to Airflow DAGs: a dataset that falls below Grade B blocks downstream jobs.
- Write a one-page Data Quality SLA for each priority dataset: owner, refresh SLA, minimum DQ score, escalation path for failures.
- Present the before/after DQ scores to the VP. Quantify the downstream impact: fewer analyst tickets, fewer manual reconciliations, fewer pipeline restarts.

---

### Situation: Your ML model's accuracy has degraded from 94% to 78% over 6 weeks. No code changed. How do you use your DQ framework to investigate?

ML degradation without code changes means the data changed. My investigation:

**1. Run freshness checks:** Is the training data being refreshed on schedule? `DataFreshnessRule` on the feature tables might reveal that a source system started delivering data 2 hours late, shifting the training window.

**2. Check null rates on key features:** If the top predictive feature (`credit_score`, `days_since_last_order`) developed a 15% null rate due to an upstream schema change, the model is now training on imputed values or dropping rows.

**3. Check value distributions with the profiler:** Compare the current `ColumnProfile` (mean, std, percentiles) against a baseline from 6 weeks ago. A feature whose mean shifted by >2 standard deviations is statistically significant distribution drift — the model was trained on one distribution and is predicting on another.

**4. Check uniqueness on join keys:** If a new source table introduced duplicate `customer_id` values, the feature engineering join produces fan-out — each customer row is multiplied, inflating counts and skewing aggregations.

**5. Check referential integrity:** If the training set joins `customers` to `transactions` but `transactions` now contains orphaned `customer_id` values (customers deleted from the master but still in transactions), the training set has changed shape.

**Root cause pattern:** Most ML degradation traces to either a null rate increase in top features or a distribution shift in a numeric feature. Both are caught by `DataProfiler` + `ValueRangeRule` with threshold alerting. The fix: add a pre-training DQ gate that compares the current feature distribution against a rolling 30-day baseline and halts training if any top-10 feature's mean shifts by >1.5σ.

---

**Q: If you had to rank the 5 DQ dimensions by importance for a payments processing system, how would you rank them and why?**

A: For payments, my ranking:

1. **Uniqueness** — Duplicate `transaction_id` is a double-charge or double-payout. It's the highest-severity possible failure: direct financial loss and regulatory violation. Every payment system treats uniqueness violations as P0.

2. **Completeness** — Null `merchant_id`, `amount`, or `customer_id` means the transaction cannot be settled. It blocks the payment, creates manual reconciliation work, and violates SLAs.

3. **Validity** — `amount` outside 0.01–100,000, invalid card formats, transaction dates in the future. These indicate either data corruption or fraud signals — both require immediate action.

4. **Consistency** — `settlement_amount != transaction_amount` (within rounding), `refund_date < transaction_date`, `status = SETTLED` with no settlement batch. Cross-system consistency failures compound over time and are expensive to detect retroactively.

5. **Freshness** — For real-time fraud models, stale transaction data (> 30 minutes old) means the model is scoring on incomplete context, increasing false negatives. For batch settlement, freshness determines whether the nightly batch has complete data.

Accuracy (correctness against an external authority) is arguably more important than freshness for some use cases, but it's not measurable without an external reference system — hence I treat it as a separate concern outside the five dimensions.

---

**Q: How do you decide whether a DQ rule violation should be `error` (pipeline-blocking) vs `warning` (alert-only)?**

A: The decision framework has three inputs:

**Business impact:** Does a violation in this column directly cause a downstream financial, operational, or regulatory failure? Null `transaction_amount` → error. Null `middle_name` → info.

**Detectability:** Can the consumer detect and compensate for the violation? If a BI analyst will see an obvious anomaly and flag it, a warning is sufficient. If the violation is invisible (e.g., subtly wrong ML feature values), it must be an error.

**False positive rate:** A rule that fires 10% of the time correctly is a good `warning`. A rule that fires 0.01% of the time must be an `error` — it's rare enough that every firing is significant. But a rule that fires 30% of the time as an error will cause alert fatigue and get disabled. Start conservative (warning), observe for 2 weeks, escalate to error if the false positive rate is < 5%.

**The threshold risk:** Setting a threshold too tight (e.g., `null_rate < 0.1%` when the true rate is 0.3%) causes constant errors and erodes trust. Setting it too loose (`null_rate < 50%`) makes the rule useless. Calibrate from historical data: set threshold at `historical_mean + 3 * historical_std` for error, `historical_mean + 1.5 * historical_std` for warning.

---

### System Design: How would you build a DQ monitoring system for 500+ tables with automatic rule suggestion?

**Architecture:**

```
Source Tables (500+)
        │
   Scheduled Profiler (Airflow, nightly)
        │
   Profile Store (time-series DB: Postgres or InfluxDB)
        │
   ┌─────────────────────────────────────────┐
   │         Rule Suggestion Engine          │
   │  - High null rate → suggest NotNullRule │
   │  - Low cardinality → suggest AllowedValues │
   │  - Numeric range → suggest ValueRange   │
   │  - PK column → suggest UniqueRule       │
   └─────────────────────────────────────────┘
        │
   Rule Catalogue (config-driven, per table)
        │
   DQ Validator (runs after each pipeline load)
        │
   DQ Score Store (per table, per run, time-series)
        │
   Alerting Layer (Slack/PagerDuty on grade drop)
        │
   DQ Dashboard (Grafana or Streamlit)
```

**Auto-profiling:** The `DataProfiler` runs on a sample (10K rows for tables > 1M rows) to keep runtime manageable. Profile results are stored with timestamps — this builds the baseline for drift detection.

**Rule suggestion:** A rule suggestion engine analyses the profile and generates candidate rules: if `null_rate < 1%` historically, suggest `NotNullRule(severity='error')`; if `cardinality < 20`, suggest `AllowedValuesRule`; if a column is a known PK via naming convention (`*_id`), suggest `UniqueRule`. Suggested rules require human approval before becoming active — engineers review a weekly "suggested rules" digest.

**Prioritisation:** Not all 500 tables get the same attention. Tag tables by tier (Tier 1 = feeds BI/ML, Tier 2 = operational, Tier 3 = archive). Tier 1 gets error-severity rules and PagerDuty alerts. Tier 3 gets warning-only with weekly digest.

**Scaling the validator:** At 500 tables, running full validation synchronously is too slow. Use a DAG with `max_active_tasks=20` running table-level validation tasks in parallel. Each task writes its result to the DQ Score Store. The dashboard reads from the store, not from live validation.

---

### System Design: How do you implement data contracts between a data producer (DE team) and data consumer (Analytics team)?

**What a data contract is:** A formal, version-controlled agreement specifying: schema (column names, types, nullable), quality SLAs (minimum DQ score, max null rate per critical column), freshness SLA (data available by HH:MM), and semantics (what `status = 'ACTIVE'` means).

**Implementation in this framework:**

**Step 1 — Define contracts as config:**
```json
{
  "table": "silver_customers",
  "version": "2.1",
  "owner": "data-engineering",
  "consumers": ["analytics", "risk-model"],
  "sla": {
    "available_by": "06:00 UTC",
    "min_dq_score": 85
  },
  "columns": {
    "customer_id": {"not_null": true, "unique": true},
    "email": {"not_null": true, "regex": "^[^@]+@[^@]+$"},
    "status": {"allowed_values": ["ACTIVE", "CHURNED", "SUSPENDED"]}
  }
}
```

**Step 2 — Generate rules from contracts:** The contract file drives `NotNullRule`, `UniqueRule`, `RegexRule`, and `AllowedValuesRule` automatically — no manual rule configuration needed for contracted columns.

**Step 3 — Gate pipeline on contract compliance:** After each Silver run, validate against the contract. If `min_dq_score` is not met, the Silver table is not promoted (the Gold downstream reads stale but valid data). Alert the producer team.

**Step 4 — Contract versioning and breaking-change notification:** Contracts live in git. A PR that removes a column or changes an `allowed_values` set is a breaking change — it requires all listed consumers to sign off. CI checks that existing consumer queries would still be valid after the change. This is data governance at the code layer, not the governance tool layer.

---

## Running Tests

### Prerequisites

Install test dependencies (separate from production requirements):

```bash
pip install -r requirements-test.txt
```

### Running the full test suite

From the POC-09 root directory:

```bash
pytest tests/ -v
```

### Running with coverage report

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Running a specific test file

```bash
pytest tests/test_completeness.py -v
pytest tests/test_validity.py -v
pytest tests/test_uniqueness.py -v
pytest tests/test_validator.py -v
pytest tests/test_scorer.py -v
```

### Test file inventory

| File | Rules Covered | Key Assertions |
|------|--------------|----------------|
| `tests/test_completeness.py` | `NotNullRule`, `CompletenessRatioRule` | clean column passes, NaN fails, empty strings treated as null, threshold boundary, invalid threshold raises |
| `tests/test_validity.py` | `RegexRule`, `ValueRangeRule`, `AllowedValuesRule` | valid/invalid email, null skipping, range boundaries, non-numeric graceful handling, allowed set membership |
| `tests/test_uniqueness.py` | `UniqueRule`, `UniquenessRatioRule` | distinct passes, duplicate fails, null exclusion, score proportionality |
| `tests/test_validator.py` | `DQValidator` | exception isolation (BrokenRule), overall_passed logic, warning vs error severity, all rules execute after exception |
| `tests/test_scorer.py` | `DQScorer` | grade thresholds A/B/C/D/F, dimension weights sum to 1.0, weighted contribution arithmetic, no-rules dimension defaults to 100 |

### Expected output (all tests passing)

```
tests/test_completeness.py::TestNotNullRule::test_passes_on_clean_column PASSED
tests/test_completeness.py::TestNotNullRule::test_fails_on_nan_column PASSED
...
tests/test_scorer.py::TestWeightedScoreArithmetic::test_to_json_is_valid_string PASSED

===== 55 passed in X.XXs =====
```

### Design notes

- All tests assert against **real pandas DataFrames**. No rule logic is mocked.
- `BrokenRule` in `test_validator.py` is a purpose-built rule that always raises `RuntimeError`, used to verify the exception isolation guarantee of `DQValidator`.
- Tests do not require a running server, database, or file system — they are fully in-memory and run in under 5 seconds.
