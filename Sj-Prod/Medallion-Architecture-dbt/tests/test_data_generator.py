"""Tests for src.data_generator — synthetic CSV data generation."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
from src.data_generator import (
    generate_all,
    generate_customers,
    generate_orders,
    generate_products,
    write_csv,
)

# ---------------------------------------------------------------------------
# generate_products
# ---------------------------------------------------------------------------


class TestGenerateProducts:
    """Tests for generate_products()."""

    def test_default_count(self):
        products = generate_products()
        assert len(products) == 50

    def test_custom_count(self):
        products = generate_products(10)
        assert len(products) == 10

    def test_expected_columns(self):
        products = generate_products(5)
        expected_cols = {"product_id", "name", "category", "price", "cost"}
        for p in products:
            assert set(p.keys()) == expected_cols

    def test_product_id_format(self):
        products = generate_products(5)
        for p in products:
            assert p["product_id"].startswith("PROD-")

    def test_price_exceeds_cost(self):
        products = generate_products(50)
        for p in products:
            assert p["price"] > p["cost"], f"price ({p['price']}) should exceed cost ({p['cost']})"

    def test_price_and_cost_are_float(self):
        products = generate_products(5)
        for p in products:
            assert isinstance(p["price"], float)
            assert isinstance(p["cost"], float)

    def test_category_valid(self):
        from src.data_generator import PRODUCT_CATEGORIES

        products = generate_products(50)
        for p in products:
            assert p["category"] in PRODUCT_CATEGORIES


# ---------------------------------------------------------------------------
# generate_customers
# ---------------------------------------------------------------------------


class TestGenerateCustomers:
    """Tests for generate_customers()."""

    def test_default_count(self):
        customers = generate_customers()
        assert len(customers) == 500

    def test_custom_count(self):
        customers = generate_customers(25)
        assert len(customers) == 25

    def test_expected_columns(self):
        customers = generate_customers(5)
        expected_cols = {"customer_id", "name", "email", "country", "signup_date", "tier"}
        for c in customers:
            assert set(c.keys()) == expected_cols

    def test_customer_id_format(self):
        customers = generate_customers(5)
        for c in customers:
            assert c["customer_id"].startswith("CUST-")

    def test_tier_values(self):
        from src.data_generator import CUSTOMER_TIERS

        customers = generate_customers(100)
        for c in customers:
            assert c["tier"] in CUSTOMER_TIERS

    def test_country_values(self):
        from src.data_generator import COUNTRY_POOL

        customers = generate_customers(100)
        for c in customers:
            assert c["country"] in COUNTRY_POOL

    def test_signup_date_is_iso_string(self):
        customers = generate_customers(5)
        for c in customers:
            # ISO format: YYYY-MM-DD
            parts = c["signup_date"].split("-")
            assert len(parts) == 3
            assert len(parts[0]) == 4  # year


# ---------------------------------------------------------------------------
# generate_orders
# ---------------------------------------------------------------------------


class TestGenerateOrders:
    """Tests for generate_orders()."""

    def test_default_count(self):
        customers = generate_customers(10)
        products = generate_products(5)
        orders = generate_orders(customers, products)
        assert len(orders) == 2000

    def test_custom_count(self):
        customers = generate_customers(10)
        products = generate_products(5)
        orders = generate_orders(customers, products, n=50)
        assert len(orders) == 50

    def test_expected_columns(self):
        customers = generate_customers(5)
        products = generate_products(3)
        orders = generate_orders(customers, products, n=10)
        expected_cols = {"order_id", "customer_id", "product_id", "order_date", "amount", "status"}
        for o in orders:
            assert set(o.keys()) == expected_cols

    def test_order_id_format(self):
        customers = generate_customers(5)
        products = generate_products(3)
        orders = generate_orders(customers, products, n=10)
        for o in orders:
            assert o["order_id"].startswith("ORD-")

    def test_references_valid_customers(self):
        customers = generate_customers(10)
        products = generate_products(5)
        orders = generate_orders(customers, products, n=50)
        valid_ids = {c["customer_id"] for c in customers}
        for o in orders:
            assert o["customer_id"] in valid_ids

    def test_references_valid_products(self):
        customers = generate_customers(10)
        products = generate_products(5)
        orders = generate_orders(customers, products, n=50)
        valid_ids = {p["product_id"] for p in products}
        for o in orders:
            assert o["product_id"] in valid_ids

    def test_status_values(self):
        from src.data_generator import ORDER_STATUSES

        customers = generate_customers(10)
        products = generate_products(5)
        orders = generate_orders(customers, products, n=100)
        for o in orders:
            assert o["status"] in ORDER_STATUSES

    def test_amount_is_positive(self):
        customers = generate_customers(10)
        products = generate_products(5)
        orders = generate_orders(customers, products, n=50)
        for o in orders:
            assert o["amount"] > 0


# ---------------------------------------------------------------------------
# write_csv
# ---------------------------------------------------------------------------


class TestWriteCSV:
    """Tests for write_csv()."""

    def test_creates_file(self, tmp_path):
        records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        path = tmp_path / "test.csv"
        write_csv(records, path)
        assert path.exists()

    def test_correct_row_count(self, tmp_path):
        records = [{"x": i} for i in range(10)]
        path = tmp_path / "out.csv"
        write_csv(records, path)
        with open(path) as f:
            reader = csv.reader(f)
            rows = list(reader)
        # 1 header + 10 data rows
        assert len(rows) == 11

    def test_correct_headers(self, tmp_path):
        records = [{"name": "Alice", "age": 30}]
        path = tmp_path / "headers.csv"
        write_csv(records, path)
        with open(path) as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == ["name", "age"]

    def test_empty_records_raises(self, tmp_path):
        path = tmp_path / "empty.csv"
        with pytest.raises(ValueError, match="No records"):
            write_csv([], path)

    def test_creates_parent_dirs(self, tmp_path):
        path = tmp_path / "nested" / "deep" / "file.csv"
        records = [{"k": "v"}]
        write_csv(records, path)
        assert path.exists()


# ---------------------------------------------------------------------------
# generate_all (integration of all generators)
# ---------------------------------------------------------------------------


class TestGenerateAll:
    """Tests for generate_all() — the main entry point."""

    def test_creates_three_csv_files(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        assert "customers" in paths
        assert "orders" in paths
        assert "products" in paths
        for name, path in paths.items():
            assert path.exists(), f"{name} file not created at {path}"

    def test_customer_row_count(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        with open(paths["customers"]) as f:
            reader = csv.reader(f)
            rows = list(reader)
        # 1 header + 500 data rows
        assert len(rows) == 501

    def test_order_row_count(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        with open(paths["orders"]) as f:
            reader = csv.reader(f)
            rows = list(reader)
        # 1 header + 2000 data rows
        assert len(rows) == 2001

    def test_product_row_count(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        with open(paths["products"]) as f:
            reader = csv.reader(f)
            rows = list(reader)
        # 1 header + 50 data rows
        assert len(rows) == 51

    def test_customer_csv_columns(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        with open(paths["customers"]) as f:
            reader = csv.DictReader(f)
            row = next(reader)
        expected = {"customer_id", "name", "email", "country", "signup_date", "tier"}
        assert set(row.keys()) == expected

    def test_order_csv_columns(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        with open(paths["orders"]) as f:
            reader = csv.DictReader(f)
            row = next(reader)
        expected = {"order_id", "customer_id", "product_id", "order_date", "amount", "status"}
        assert set(row.keys()) == expected

    def test_product_csv_columns(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        with open(paths["products"]) as f:
            reader = csv.DictReader(f)
            row = next(reader)
        expected = {"product_id", "name", "category", "price", "cost"}
        assert set(row.keys()) == expected

    def test_returns_path_objects(self, tmp_output_dir):
        paths = generate_all(tmp_output_dir)
        for name, path in paths.items():
            assert isinstance(path, Path), f"{name} should be a Path, got {type(path)}"
