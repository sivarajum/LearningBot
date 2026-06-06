# POC-08 dbt Medallion Architecture — Test Results

## What Tests Exist

dbt has two kinds of tests. Both are enumerated in full below.

---

## Schema Tests (defined in schema.yml files)

Schema tests are declared inline in `models/*/schema.yml`. dbt compiles each one to a SQL query and runs it. A test passes when the query returns zero rows.

### Bronze Layer (`models/bronze/schema.yml`)

**bronze_customers**

| Test | Column | Type |
|------|--------|------|
| `not_null_bronze_customers_customer_id` | `customer_id` | not_null |
| `not_null_bronze_customers_email` | `email` | not_null |
| `not_null_bronze_customers_tier` | `tier` | not_null |
| `not_null_bronze_customers__ingested_at` | `_ingested_at` | not_null |

**bronze_orders**

| Test | Column | Type |
|------|--------|------|
| `not_null_bronze_orders_order_id` | `order_id` | not_null |
| `unique_bronze_orders_order_id` | `order_id` | unique |
| `not_null_bronze_orders_customer_id` | `customer_id` | not_null |
| `not_null_bronze_orders_amount` | `amount` | not_null |
| `not_null_bronze_orders_status` | `status` | not_null |

**bronze_products**

| Test | Column | Type |
|------|--------|------|
| `not_null_bronze_products_product_id` | `product_id` | not_null |
| `unique_bronze_products_product_id` | `product_id` | unique |
| `not_null_bronze_products_price` | `price` | not_null |
| `not_null_bronze_products_cost` | `cost` | not_null |

**Bronze schema tests subtotal: 13**

---

### Silver Layer (`models/silver/schema.yml`)

**silver_customers**

| Test | Column | Type |
|------|--------|------|
| `not_null_silver_customers_customer_id` | `customer_id` | not_null |
| `unique_silver_customers_customer_id` | `customer_id` | unique |
| `not_null_silver_customers_email` | `email` | not_null |
| `not_null_silver_customers_tier` | `tier` | not_null |
| `accepted_values_silver_customers_tier__BRONZE__SILVER__GOLD` | `tier` | accepted_values: BRONZE, SILVER, GOLD |
| `not_null_silver_customers_customer_age_days` | `customer_age_days` | not_null |

**silver_orders**

| Test | Column | Type |
|------|--------|------|
| `not_null_silver_orders_order_id` | `order_id` | not_null |
| `unique_silver_orders_order_id` | `order_id` | unique |
| `not_null_silver_orders_customer_id` | `customer_id` | not_null |
| `not_null_silver_orders_status` | `status` | not_null |
| `accepted_values_silver_orders_704e1ab...` | `status` | accepted_values: PENDING, SHIPPED, DELIVERED, CANCELLED |
| `not_null_silver_orders_amount` | `amount` | not_null |

**silver_products**

| Test | Column | Type |
|------|--------|------|
| `not_null_silver_products_product_id` | `product_id` | not_null |
| `unique_silver_products_product_id` | `product_id` | unique |
| `not_null_silver_products_category` | `category` | not_null |

**Silver schema tests subtotal: 15**

---

### Gold Layer (`models/gold/schema.yml`)

**gold_customer_lifetime_value**

| Test | Column | Type |
|------|--------|------|
| `not_null_gold_customer_lifetime_value_customer_id` | `customer_id` | not_null |
| `unique_gold_customer_lifetime_value_customer_id` | `customer_id` | unique |
| `not_null_gold_customer_lifetime_value_lifetime_value` | `lifetime_value` | not_null |
| `not_null_gold_customer_lifetime_value_clv_segment` | `clv_segment` | not_null |
| `accepted_values_gold_customer__de846f54...` | `clv_segment` | accepted_values: high_value, mid_value, low_value |

**gold_product_performance**

| Test | Column | Type |
|------|--------|------|
| `not_null_gold_product_performance_product_id` | `product_id` | not_null |
| `unique_gold_product_performance_product_id` | `product_id` | unique |
| `not_null_gold_product_performance_total_revenue` | `total_revenue` | not_null |

**gold_daily_revenue**

| Test | Column | Type |
|------|--------|------|
| `not_null_gold_daily_revenue_order_date` | `order_date` | not_null |
| `unique_gold_daily_revenue_order_date` | `order_date` | unique |
| `not_null_gold_daily_revenue_daily_revenue` | `daily_revenue` | not_null |

**Gold schema tests subtotal: 11**

---

## Singular Tests (`tests/` directory)

Singular tests are hand-written SQL files in `medallion_dbt/tests/`. A test passes when the query returns zero rows.

| File | Model Tested | Assertion |
|------|-------------|-----------|
| `tests/bronze_customers_not_null.sql` | `bronze_customers` | No row has NULL `customer_id` OR NULL `email` |
| `tests/silver_orders_valid_status.sql` | `silver_orders` | No row has `status` outside ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED') |

**Singular tests subtotal: 2**

---

## Total Test Count

| Category | Count |
|----------|-------|
| Bronze schema tests | 13 |
| Silver schema tests | 15 |
| Gold schema tests | 11 |
| Singular tests | 2 |
| **Total** | **41** |

---

## What the 3,022 Number Was

If you looked in `medallion_dbt/target/` and saw thousands of `.sql` files, those are **NOT tests**. They are compiled query artifacts.

dbt's build process generates two directories inside `target/`:

- `target/compiled/` — SQL files that represent the compiled version of every model and test, with Jinja macros resolved and `{{ ref() }}` calls replaced with actual table names. These are read-only artifacts showing what dbt *would* run.
- `target/run/` — SQL files that wrap each compiled query in a `CREATE TABLE` or `SELECT` statement used for actual execution.

For every model (9 models) and every test (41 tests), dbt writes a compiled file AND a run file — in two directories. The target directory also accumulates files from previous runs and includes macro files, adapter SQL, and Python package SQL from the `.venv` directory.

The actual test count for this project is **41**: 39 schema tests + 2 singular tests.

---

## How to Run Tests

```bash
cd /Users/sivarajumalladi/Documents/GitHub/LearningBot/POCs/POC-08-Medallion-Architecture-dbt/medallion_dbt
dbt test
```

To run tests for a specific model only:

```bash
dbt test --select bronze_customers
dbt test --select silver_orders
dbt test --select gold_customer_lifetime_value
```

To run only schema tests (skips singular tests):

```bash
dbt test --select test_type:generic
```

To run only singular tests:

```bash
dbt test --select test_type:singular
```

---

## Sample Expected Output

> **Note:** The output below is illustrative. Actual timing and dbt version will vary based on your environment.

When all 41 tests pass against the generated dataset, `dbt test` produces output in this format:

```
Running with dbt=1.8.x
Found 9 models, 41 tests, 1 source, 0 exposures, 0 metrics

Concurrency: 1 threads (target='dev')

1 of 41 START test accepted_values_gold_customer__de846f54... .......... [RUN]
1 of 41 PASS  accepted_values_gold_customer__de846f54... ............... [PASS in 0.05s]
2 of 41 START test accepted_values_silver_customers_tier__BRONZE__SILVER__GOLD ... [RUN]
2 of 41 PASS  accepted_values_silver_customers_tier__BRONZE__SILVER__GOLD ... [PASS in 0.04s]
...
40 of 41 START test unique_silver_products_product_id .................. [RUN]
40 of 41 PASS  unique_silver_products_product_id ....................... [PASS in 0.03s]
41 of 41 START test silver_orders_valid_status ......................... [RUN]
41 of 41 PASS  silver_orders_valid_status .............................. [PASS in 0.04s]

Finished running 39 generic tests, 2 singular tests in 0.XX seconds.

PASS=41 WARN=0 ERROR=0 SKIP=0 TOTAL=41
```

A test failure looks like:

```
1 of 41 START test not_null_bronze_customers_customer_id ............... [RUN]
1 of 41 FAIL 3 not_null_bronze_customers_customer_id ................... [FAIL 3 in 0.05s]
```

The number after `FAIL` is the row count returned by the test query — i.e., the number of records that violated the constraint.
