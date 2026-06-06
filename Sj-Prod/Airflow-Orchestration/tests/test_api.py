"""
Unit tests for the FastAPI service (src/api.py).

Uses FastAPI's TestClient (backed by httpx) so no running server is needed.

Run:
    PYTHONPATH=. pytest tests/test_api.py -v
"""

import os
import sys
import unittest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from fastapi.testclient import TestClient

from src.api import app


# ============================================================================
# Shared test client
# ============================================================================

client = TestClient(app)


# ============================================================================
# Health endpoint
# ============================================================================


class TestHealthEndpoint(unittest.TestCase):
    """Tests for GET /health."""

    def test_health_returns_200(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_health_status_is_healthy(self):
        data = client.get("/health").json()
        self.assertEqual(data["status"], "healthy")

    def test_health_has_required_fields(self):
        data = client.get("/health").json()
        for key in ("status", "timestamp", "version", "airflow_mode"):
            self.assertIn(key, data, f"Missing key '{key}' in /health response")

    def test_health_version(self):
        data = client.get("/health").json()
        self.assertEqual(data["version"], "1.0.0")

    def test_health_airflow_mode_simulator(self):
        """Without Airflow installed, should report simulator mode."""
        data = client.get("/health").json()
        self.assertIn("simulator", data["airflow_mode"].lower())


# ============================================================================
# DAGs list endpoint
# ============================================================================


class TestDagsListEndpoint(unittest.TestCase):
    """Tests for GET /dags."""

    def test_dags_returns_200(self):
        response = client.get("/dags")
        self.assertEqual(response.status_code, 200)

    def test_dags_returns_list(self):
        data = client.get("/dags").json()
        self.assertIsInstance(data, list)

    def test_dags_list_is_not_empty(self):
        data = client.get("/dags").json()
        self.assertGreater(len(data), 0, "DAG list should not be empty")

    def test_dag_list_item_has_required_fields(self):
        data = client.get("/dags").json()
        required_keys = {"dag_id", "description", "schedule", "tags", "task_count", "owner", "source_file"}
        for dag in data:
            for key in required_keys:
                self.assertIn(key, dag, f"DAG item missing key '{key}'")

    def test_known_dag_appears_in_list(self):
        data = client.get("/dags").json()
        dag_ids = [d["dag_id"] for d in data]
        self.assertIn("etl_transactions_pipeline", dag_ids)

    def test_dynamic_dags_appear_in_list(self):
        data = client.get("/dags").json()
        dag_ids = [d["dag_id"] for d in data]
        self.assertIn("etl_sales", dag_ids)


# ============================================================================
# DAG detail endpoint
# ============================================================================


class TestDagDetailEndpoint(unittest.TestCase):
    """Tests for GET /dags/{dag_id}."""

    def test_dag_detail_returns_200(self):
        response = client.get("/dags/etl_transactions_pipeline")
        self.assertEqual(response.status_code, 200)

    def test_dag_detail_has_tasks(self):
        data = client.get("/dags/etl_transactions_pipeline").json()
        self.assertIn("tasks", data)
        self.assertGreater(len(data["tasks"]), 0)

    def test_dag_detail_has_required_fields(self):
        data = client.get("/dags/etl_transactions_pipeline").json()
        for key in ("dag_id", "description", "schedule", "tags", "owner", "tasks", "task_count"):
            self.assertIn(key, data, f"Missing key '{key}' in DAG detail response")

    def test_task_info_has_required_fields(self):
        data = client.get("/dags/etl_transactions_pipeline").json()
        for task in data["tasks"]:
            for key in ("task_id", "operator_type"):
                self.assertIn(key, task, f"Task missing key '{key}'")

    def test_nonexistent_dag_returns_404(self):
        response = client.get("/dags/totally_fake_dag_999")
        self.assertEqual(response.status_code, 404)


# ============================================================================
# DAG graph endpoint
# ============================================================================


class TestDagGraphEndpoint(unittest.TestCase):
    """Tests for GET /dags/{dag_id}/graph."""

    def test_graph_returns_200(self):
        response = client.get("/dags/etl_transactions_pipeline/graph")
        self.assertEqual(response.status_code, 200)

    def test_graph_has_nodes_and_edges(self):
        data = client.get("/dags/etl_transactions_pipeline/graph").json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertGreater(len(data["nodes"]), 0)

    def test_graph_node_has_required_fields(self):
        data = client.get("/dags/etl_transactions_pipeline/graph").json()
        for node in data["nodes"]:
            for key in ("id", "label", "operator", "group", "color"):
                self.assertIn(key, node, f"Node missing key '{key}'")

    def test_graph_nonexistent_dag_returns_404(self):
        response = client.get("/dags/nonexistent_dag_xyz/graph")
        self.assertEqual(response.status_code, 404)

    def test_graph_task_count_matches_nodes(self):
        data = client.get("/dags/data_quality_pipeline/graph").json()
        self.assertEqual(data["task_count"], len(data["nodes"]))

    def test_graph_edge_count_matches_edges(self):
        data = client.get("/dags/data_quality_pipeline/graph").json()
        self.assertEqual(data["edge_count"], len(data["edges"]))


# ============================================================================
# DAG run (simulation) endpoint
# ============================================================================


class TestDagRunEndpoint(unittest.TestCase):
    """Tests for POST /dags/{dag_id}/run."""

    def test_run_returns_200(self):
        response = client.post("/dags/etl_sales/run")
        self.assertEqual(response.status_code, 200)

    def test_run_response_has_required_fields(self):
        data = client.post("/dags/etl_sales/run").json()
        for key in ("dag_id", "run_id", "status", "start_time", "end_time",
                     "duration_ms", "task_results", "xcoms", "task_order",
                     "errors", "summary"):
            self.assertIn(key, data, f"Missing key '{key}' in run response")

    def test_run_summary_has_counts(self):
        data = client.post("/dags/etl_sales/run").json()
        summary = data["summary"]
        for key in ("total_tasks", "succeeded", "failed", "skipped", "xcom_count"):
            self.assertIn(key, summary, f"Summary missing key '{key}'")

    def test_run_nonexistent_dag_returns_404(self):
        response = client.post("/dags/fake_dag_9999/run")
        self.assertEqual(response.status_code, 404)

    def test_run_task_results_have_status_color(self):
        data = client.post("/dags/etl_sales/run").json()
        for tr in data["task_results"]:
            self.assertIn("status_color", tr, "Task result must include status_color")
            self.assertTrue(tr["status_color"].startswith("#"), "status_color must be a hex color")

    def test_run_with_task_inputs(self):
        """Passing task_inputs in the request body does not crash."""
        response = client.post(
            "/dags/etl_sales/run",
            json={"task_inputs": {"extract": {"custom": True}}},
        )
        self.assertEqual(response.status_code, 200)


# ============================================================================
# XComs endpoint
# ============================================================================


class TestXcomsEndpoint(unittest.TestCase):
    """Tests for GET /xcoms."""

    def test_xcoms_returns_200(self):
        response = client.get("/xcoms")
        self.assertEqual(response.status_code, 200)

    def test_xcoms_with_dag_filter_no_run(self):
        """Querying xcoms for a DAG that has not been simulated returns a message."""
        response = client.get("/xcoms", params={"dag_id": "nonexistent_dag_xyz"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)

    def test_xcoms_after_run(self):
        """After running a DAG, xcoms should be available."""
        # First, trigger a run
        client.post("/dags/etl_sales/run")
        # Then query xcoms
        response = client.get("/xcoms", params={"dag_id": "etl_sales"})
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("xcoms", data)


# ============================================================================
# Concepts endpoint
# ============================================================================


class TestConceptsEndpoint(unittest.TestCase):
    """Tests for GET /concepts."""

    def test_concepts_returns_200(self):
        response = client.get("/concepts")
        self.assertEqual(response.status_code, 200)

    def test_concepts_has_expected_keys(self):
        data = client.get("/concepts").json()
        expected_keys = {"dag", "operators", "tasks", "xcoms", "sensors", "executors"}
        for key in expected_keys:
            self.assertIn(key, data, f"Concepts missing key '{key}'")


# ============================================================================
# Reload endpoint
# ============================================================================


class TestReloadEndpoint(unittest.TestCase):
    """Tests for POST /reload."""

    def test_reload_returns_200(self):
        response = client.post("/reload")
        self.assertEqual(response.status_code, 200)

    def test_reload_response_has_dag_count(self):
        data = client.post("/reload").json()
        self.assertTrue(data.get("reloaded"))
        self.assertGreater(data.get("dag_count", 0), 0)
        self.assertIsInstance(data.get("dag_ids"), list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
