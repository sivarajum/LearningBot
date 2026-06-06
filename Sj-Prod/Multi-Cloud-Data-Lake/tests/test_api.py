"""Tests for the FastAPI endpoints."""

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.cloud_simulator import generate_cloud_data, save_cloud_data
from src.lake_builder import build_lake


@pytest.fixture()
def client(tmp_data_dir):
    """Create a TestClient with test data pre-populated."""
    # Generate and save small data, then build the lake
    data = generate_cloud_data(customers_per_cloud=10, transactions_per_cloud=50)
    save_cloud_data(data)
    build_lake()

    from src.api import app

    with TestClient(app, raise_server_exceptions=True) as tc:
        yield tc


@pytest.fixture()
def empty_client(tmp_data_dir):
    """Create a TestClient with empty data dirs and no lifespan auto-generation."""
    from src.api import app

    # Replace the lifespan so the app does NOT auto-generate data on startup.
    @asynccontextmanager
    async def _noop_lifespan(application: FastAPI):
        yield

    original_router_lifespan = app.router.lifespan_context
    app.router.lifespan_context = _noop_lifespan
    try:
        with TestClient(app, raise_server_exceptions=True) as tc:
            yield tc
    finally:
        app.router.lifespan_context = original_router_lifespan


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    """Tests for GET /health."""

    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_body(self, client):
        body = client.get("/health").json()
        assert body["status"] == "healthy"
        assert body["service"] == "data-lake"


# ---------------------------------------------------------------------------
# Cloud sources
# ---------------------------------------------------------------------------

class TestClouds:
    """Tests for GET /clouds."""

    def test_clouds_returns_200(self, client):
        resp = client.get("/clouds")
        assert resp.status_code == 200

    def test_clouds_lists_all_providers(self, client):
        body = client.get("/clouds").json()
        clouds = body["clouds"]
        assert set(clouds.keys()) == {"aws", "azure", "gcp"}

    def test_clouds_each_has_files(self, client):
        body = client.get("/clouds").json()
        for cloud, files in body["clouds"].items():
            assert "customers.parquet" in files
            assert "transactions.parquet" in files


# ---------------------------------------------------------------------------
# Lake tables listing
# ---------------------------------------------------------------------------

class TestLakeTables:
    """Tests for GET /lake/tables."""

    def test_lake_tables_returns_200(self, client):
        resp = client.get("/lake/tables")
        assert resp.status_code == 200

    def test_lake_tables_lists_tables(self, client):
        body = client.get("/lake/tables").json()
        tables = body["tables"]
        assert "customers" in tables
        assert "transactions" in tables
        assert "customer_metrics" in tables

    def test_lake_tables_empty_when_no_lake(self, empty_client):
        body = empty_client.get("/lake/tables").json()
        assert body["tables"] == []


# ---------------------------------------------------------------------------
# Query lake table
# ---------------------------------------------------------------------------

class TestQueryLake:
    """Tests for GET /lake/{table_name}."""

    def test_query_customers(self, client):
        resp = client.get("/lake/customers?limit=5")
        assert resp.status_code == 200
        body = resp.json()
        assert body["table"] == "customers"
        assert body["returned"] == 5
        assert body["total_rows"] == 30  # 10 per cloud
        assert len(body["data"]) == 5

    def test_query_transactions(self, client):
        resp = client.get("/lake/transactions?limit=10")
        assert resp.status_code == 200
        body = resp.json()
        assert body["table"] == "transactions"
        assert body["returned"] == 10
        assert body["total_rows"] == 150  # 50 per cloud

    def test_query_with_cloud_filter(self, client):
        resp = client.get("/lake/customers?cloud=aws&limit=100")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_rows"] == 10  # only AWS customers
        for record in body["data"]:
            assert record["source_cloud"] == "aws"

    def test_query_nonexistent_table_returns_404(self, client):
        resp = client.get("/lake/nonexistent")
        assert resp.status_code == 404

    def test_query_default_limit(self, client):
        resp = client.get("/lake/transactions")
        body = resp.json()
        assert body["returned"] <= 100  # default limit

    def test_query_customer_metrics(self, client):
        resp = client.get("/lake/customer_metrics?limit=5")
        assert resp.status_code == 200
        body = resp.json()
        assert body["table"] == "customer_metrics"
        assert len(body["data"]) == 5


# ---------------------------------------------------------------------------
# Analytics summary
# ---------------------------------------------------------------------------

class TestAnalyticsSummary:
    """Tests for GET /analytics/summary."""

    def test_summary_returns_200(self, client):
        resp = client.get("/analytics/summary")
        assert resp.status_code == 200

    def test_summary_fields(self, client):
        body = client.get("/analytics/summary").json()
        assert "total_customers" in body
        assert "total_transactions" in body
        assert "customers_by_cloud" in body
        assert "transactions_by_cloud" in body
        assert "revenue_by_cloud" in body
        assert "revenue_by_category" in body
        assert "customers_by_plan" in body
        assert "active_rate_by_cloud" in body
        assert "avg_spend_by_cloud" in body

    def test_summary_customer_count(self, client):
        body = client.get("/analytics/summary").json()
        assert body["total_customers"] == 30

    def test_summary_transaction_count(self, client):
        body = client.get("/analytics/summary").json()
        assert body["total_transactions"] == 150

    def test_summary_customers_by_cloud(self, client):
        body = client.get("/analytics/summary").json()
        cbc = body["customers_by_cloud"]
        assert cbc["aws"] == 10
        assert cbc["azure"] == 10
        assert cbc["gcp"] == 10

    def test_summary_returns_400_when_no_lake(self, empty_client):
        resp = empty_client.get("/analytics/summary")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Generate endpoint
# ---------------------------------------------------------------------------

class TestGenerate:
    """Tests for POST /generate."""

    def test_generate_returns_200(self, client):
        resp = client.post("/generate")
        assert resp.status_code == 200

    def test_generate_response_body(self, client):
        body = client.post("/generate").json()
        assert "cloud_files" in body
        assert "lake_tables" in body
        assert "elapsed_seconds" in body
        assert set(body["cloud_files"].keys()) == {"aws", "azure", "gcp"}
