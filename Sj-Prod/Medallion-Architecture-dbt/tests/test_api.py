"""Tests for src.api -- FastAPI endpoints for the Medallion Architecture.

Uses a real MedallionPipeline instance backed by a temporary directory with
generated CSV data and a live DuckDB warehouse.  Only dbt subprocess calls
are mocked (they require dbt installed).
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.data_generator import generate_all
from src.pipeline import MedallionPipeline

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_duckdb(db_path: Path, raw_dir: Path) -> None:
    """
    Read the generated CSVs and load them into DuckDB schemas/tables that
    mirror what dbt would create (main_bronze, main_silver, main_gold).
    This lets us exercise the real pipeline.get_layer_stats /
    get_model_preview code paths without running dbt.
    """
    conn = duckdb.connect(str(db_path))

    # -- bronze ---------------------------------------------------------------
    conn.execute("CREATE SCHEMA IF NOT EXISTS main_bronze")
    conn.execute(
        f"""
        CREATE TABLE main_bronze.bronze_customers AS
        SELECT *, current_timestamp AS _ingested_at, 'customers.csv' AS _source_file
        FROM read_csv_auto('{raw_dir / "customers.csv"}')
        """
    )
    conn.execute(
        f"""
        CREATE TABLE main_bronze.bronze_orders AS
        SELECT *, current_timestamp AS _ingested_at, 'orders.csv' AS _source_file
        FROM read_csv_auto('{raw_dir / "orders.csv"}')
        """
    )
    conn.execute(
        f"""
        CREATE TABLE main_bronze.bronze_products AS
        SELECT *, current_timestamp AS _ingested_at, 'products.csv' AS _source_file
        FROM read_csv_auto('{raw_dir / "products.csv"}')
        """
    )

    # -- silver ---------------------------------------------------------------
    conn.execute("CREATE SCHEMA IF NOT EXISTS main_silver")
    conn.execute(
        "CREATE TABLE main_silver.silver_customers AS SELECT * FROM main_bronze.bronze_customers"
    )
    conn.execute(
        "CREATE TABLE main_silver.silver_orders AS SELECT * FROM main_bronze.bronze_orders"
    )
    conn.execute(
        "CREATE TABLE main_silver.silver_products AS SELECT * FROM main_bronze.bronze_products"
    )

    # -- gold -----------------------------------------------------------------
    conn.execute("CREATE SCHEMA IF NOT EXISTS main_gold")
    conn.execute(
        """
        CREATE TABLE main_gold.gold_customer_lifetime_value AS
        SELECT customer_id, SUM(CAST(amount AS DOUBLE)) AS lifetime_value
        FROM main_silver.silver_orders
        GROUP BY customer_id
        """
    )
    conn.execute(
        """
        CREATE TABLE main_gold.gold_product_performance AS
        SELECT product_id, COUNT(*) AS order_count, SUM(CAST(amount AS DOUBLE)) AS total_revenue
        FROM main_silver.silver_orders
        GROUP BY product_id
        """
    )
    conn.execute(
        """
        CREATE TABLE main_gold.gold_daily_revenue AS
        SELECT order_date, SUM(CAST(amount AS DOUBLE)) AS revenue
        FROM main_silver.silver_orders
        GROUP BY order_date
        """
    )

    conn.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def pipeline_dir(tmp_path: Path) -> Path:
    """Create a real project layout in tmp_path with generated data and DuckDB."""
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)

    # Generate real CSV data (small)
    generate_all(raw_dir)

    # Seed DuckDB with tables matching what dbt would produce
    db_path = tmp_path / "data" / "warehouse.duckdb"
    _seed_duckdb(db_path, raw_dir)

    # Create the medallion_dbt dir so paths resolve
    (tmp_path / "medallion_dbt").mkdir(exist_ok=True)

    return tmp_path


@pytest.fixture()
def client(pipeline_dir: Path) -> TestClient:
    """Return a FastAPI TestClient backed by a real MedallionPipeline."""
    import src.api as api_module

    real_pipeline = MedallionPipeline(pipeline_dir)

    api_module._pipeline = real_pipeline
    api_module._last_pipeline_result = None
    api_module._pipeline_running = False

    yield TestClient(app)

    # Cleanup singleton
    api_module._pipeline = None


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_response_fields(self, client: TestClient) -> None:
        resp = client.get("/health")
        data = resp.json()
        assert data["status"] == "ok"
        assert "dbt_installed" in data
        assert "warehouse_exists" in data
        assert "version" in data

    def test_health_warehouse_exists(self, client: TestClient) -> None:
        resp = client.get("/health")
        data = resp.json()
        assert data["warehouse_exists"] is True

    def test_health_version(self, client: TestClient) -> None:
        resp = client.get("/health")
        data = resp.json()
        assert data["version"] == "1.0.0"


# ---------------------------------------------------------------------------
# GET /layers
# ---------------------------------------------------------------------------


class TestLayersEndpoint:
    """Tests for the /layers endpoint."""

    def test_layers_returns_200(self, client: TestClient) -> None:
        resp = client.get("/layers")
        assert resp.status_code == 200

    def test_layers_has_three_layers(self, client: TestClient) -> None:
        resp = client.get("/layers")
        data = resp.json()
        assert set(data.keys()) == {"bronze", "silver", "gold"}

    def test_layers_bronze_structure(self, client: TestClient) -> None:
        resp = client.get("/layers")
        data = resp.json()
        bronze = data["bronze"]
        assert bronze["layer"] == "bronze"
        assert "models" in bronze
        assert "row_counts" in bronze
        assert "total_rows" in bronze
        assert "pipeline_run" in bronze

    def test_layers_row_counts_are_positive(self, client: TestClient) -> None:
        """With seeded data, all row counts should be > 0."""
        resp = client.get("/layers")
        data = resp.json()
        for layer_name in ["bronze", "silver", "gold"]:
            layer_data = data[layer_name]
            assert layer_data["total_rows"] > 0, f"{layer_name} should have rows"


# ---------------------------------------------------------------------------
# GET /layers/{layer}
# ---------------------------------------------------------------------------


class TestLayerDetailEndpoint:
    """Tests for the /layers/{layer} endpoint."""

    def test_valid_layer_returns_200(self, client: TestClient) -> None:
        resp = client.get("/layers/bronze")
        assert resp.status_code == 200

    def test_invalid_layer_returns_400(self, client: TestClient) -> None:
        resp = client.get("/layers/platinum")
        assert resp.status_code == 400

    def test_layer_detail_structure(self, client: TestClient) -> None:
        resp = client.get("/layers/bronze")
        data = resp.json()
        assert data["layer"] == "bronze"
        assert "models" in data
        assert "row_counts" in data
        assert "total_rows" in data

    def test_each_layer_returns_real_counts(self, client: TestClient) -> None:
        for layer in ["bronze", "silver", "gold"]:
            resp = client.get(f"/layers/{layer}")
            data = resp.json()
            assert data["total_rows"] > 0, f"{layer} layer should have rows"


# ---------------------------------------------------------------------------
# GET /layers/{layer}/{model}
# ---------------------------------------------------------------------------


class TestModelPreviewEndpoint:
    """Tests for the /layers/{layer}/{model} endpoint."""

    def test_valid_model_returns_200(self, client: TestClient) -> None:
        resp = client.get("/layers/bronze/bronze_customers")
        assert resp.status_code == 200

    def test_preview_returns_data(self, client: TestClient) -> None:
        resp = client.get("/layers/bronze/bronze_customers")
        data = resp.json()
        assert data["layer"] == "bronze"
        assert data["model"] == "bronze_customers"
        assert "data" in data
        assert len(data["data"]) > 0

    def test_preview_respects_limit(self, client: TestClient) -> None:
        resp = client.get("/layers/bronze/bronze_customers?limit=5")
        data = resp.json()
        assert data["row_count"] <= 5

    def test_preview_gold_model(self, client: TestClient) -> None:
        resp = client.get("/layers/gold/gold_daily_revenue")
        data = resp.json()
        assert data["layer"] == "gold"
        assert len(data["data"]) > 0

    def test_invalid_layer_returns_400(self, client: TestClient) -> None:
        resp = client.get("/layers/platinum/some_model")
        assert resp.status_code == 400

    def test_invalid_model_returns_404(self, client: TestClient) -> None:
        resp = client.get("/layers/bronze/nonexistent_model")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /pipeline/status
# ---------------------------------------------------------------------------


class TestPipelineStatusEndpoint:
    """Tests for the /pipeline/status endpoint."""

    def test_status_returns_200(self, client: TestClient) -> None:
        resp = client.get("/pipeline/status")
        assert resp.status_code == 200

    def test_status_fields(self, client: TestClient) -> None:
        resp = client.get("/pipeline/status")
        data = resp.json()
        assert "running" in data
        assert data["running"] is False
        assert "last_result" in data


# ---------------------------------------------------------------------------
# POST /pipeline/run  (dbt subprocess mocked)
# ---------------------------------------------------------------------------


class TestPipelineRunEndpoint:
    """Tests for the /pipeline/run endpoint."""

    def test_run_returns_200(self, client: TestClient) -> None:
        resp = client.post("/pipeline/run")
        assert resp.status_code == 200

    def test_run_returns_started_status(self, client: TestClient) -> None:
        resp = client.post("/pipeline/run")
        data = resp.json()
        assert data["status"] == "started"
        assert "message" in data


# ---------------------------------------------------------------------------
# GET /lineage  (exercises real pipeline.get_lineage())
# ---------------------------------------------------------------------------


class TestLineageEndpoint:
    """Tests for the /lineage endpoint."""

    def test_lineage_returns_200(self, client: TestClient) -> None:
        resp = client.get("/lineage")
        assert resp.status_code == 200

    def test_lineage_has_nodes_and_edges(self, client: TestClient) -> None:
        resp = client.get("/lineage")
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 12
        assert len(data["edges"]) == 11

    def test_lineage_node_layers(self, client: TestClient) -> None:
        resp = client.get("/lineage")
        data = resp.json()
        layers = {n["layer"] for n in data["nodes"]}
        assert layers == {"source", "bronze", "silver", "gold"}


# ---------------------------------------------------------------------------
# GET /concepts
# ---------------------------------------------------------------------------


class TestConceptsEndpoint:
    """Tests for the /concepts endpoint."""

    def test_concepts_returns_200(self, client: TestClient) -> None:
        resp = client.get("/concepts")
        assert resp.status_code == 200

    def test_concepts_is_list(self, client: TestClient) -> None:
        resp = client.get("/concepts")
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_concept_structure(self, client: TestClient) -> None:
        resp = client.get("/concepts")
        data = resp.json()
        first = data[0]
        assert "term" in first
        assert "definition" in first

    def test_concepts_includes_medallion(self, client: TestClient) -> None:
        resp = client.get("/concepts")
        data = resp.json()
        terms = [c["term"] for c in data]
        assert "Medallion Architecture" in terms
