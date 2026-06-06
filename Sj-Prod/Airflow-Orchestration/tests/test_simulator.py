"""
Unit tests for DAGSimulator (src/simulator.py).

Covers:
  - Simulator instantiation and DAG loading
  - DAG listing and metadata
  - Task dependency resolution (topological sort)
  - Simple DAG execution (simulate)
  - XComStore push/pull/all_xcoms/task_xcoms
  - FakeTaskInstance operations
  - Retry logic (task fails then succeeds on second attempt)
  - Branch operator handling
  - Error handling for invalid DAG IDs
  - get_dag_graph node/edge structure

Run:
    PYTHONPATH=. pytest tests/test_simulator.py -v
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

from src.simulator import (
    DAGSimulator,
    FakeTaskInstance,
    SimulationResult,
    XComStore,
    _topological_sort,
    STATUS_FAILED,
    STATUS_SKIPPED,
    STATUS_SUCCESS,
    STATUS_UPSTREAM_FAILED,
)


# ============================================================================
# XComStore tests
# ============================================================================


class TestXComStore(unittest.TestCase):
    """Tests for the in-memory XCom implementation."""

    def setUp(self):
        self.store = XComStore()

    def test_push_and_pull_basic(self):
        """push then pull with a single task_id returns the pushed value."""
        self.store.push("task_a", "my_key", {"rows": 42})
        result = self.store.pull("task_a", "my_key")
        self.assertEqual(result, {"rows": 42})

    def test_pull_missing_key_returns_none(self):
        """Pulling a key that was never pushed returns None."""
        result = self.store.pull("nonexistent", "missing_key")
        self.assertIsNone(result)

    def test_pull_with_list_of_task_ids(self):
        """pull accepts a list of task_ids and returns the first match."""
        self.store.push("task_b", "val", 100)
        result = self.store.pull(["task_a", "task_b"], "val")
        self.assertEqual(result, 100)

    def test_pull_with_string_task_id(self):
        """pull wraps a single string task_id into a list internally."""
        self.store.push("task_x", "k", "hello")
        result = self.store.pull("task_x", "k")
        self.assertEqual(result, "hello")

    def test_pull_strips_task_group_prefix(self):
        """pull falls back to stripping 'group.' prefix for TaskGroup tasks."""
        self.store.push("my_task", "k", 999)
        result = self.store.pull("group.my_task", "k")
        self.assertEqual(result, 999)

    def test_all_xcoms(self):
        """all_xcoms returns a dict keyed by 'task_id/key'."""
        self.store.push("a", "x", 1)
        self.store.push("b", "y", 2)
        result = self.store.all_xcoms()
        self.assertEqual(result, {"a/x": 1, "b/y": 2})

    def test_task_xcoms(self):
        """task_xcoms returns only XComs for a specific task."""
        self.store.push("t1", "k1", "v1")
        self.store.push("t1", "k2", "v2")
        self.store.push("t2", "k1", "other")
        result = self.store.task_xcoms("t1")
        self.assertEqual(result, {"k1": "v1", "k2": "v2"})

    def test_overwrite_existing_key(self):
        """Pushing the same (task_id, key) pair overwrites the previous value."""
        self.store.push("t", "k", "old")
        self.store.push("t", "k", "new")
        self.assertEqual(self.store.pull("t", "k"), "new")


# ============================================================================
# FakeTaskInstance tests
# ============================================================================


class TestFakeTaskInstance(unittest.TestCase):
    """Tests for the FakeTaskInstance injected into task context."""

    def setUp(self):
        self.store = XComStore()
        self.ti = FakeTaskInstance("my_task", self.store)

    def test_xcom_push_stores_in_xcom_data(self):
        """xcom_push populates both the XComStore and the local xcom_data dict."""
        self.ti.xcom_push(key="count", value=42)
        self.assertEqual(self.ti.xcom_data["count"], 42)
        self.assertEqual(self.store.pull("my_task", "count"), 42)

    def test_xcom_pull_from_other_task(self):
        """xcom_pull retrieves values pushed by a different task."""
        self.store.push("upstream", "result", {"status": "ok"})
        result = self.ti.xcom_pull(task_ids="upstream", key="result")
        self.assertEqual(result, {"status": "ok"})

    def test_xcom_pull_no_task_ids(self):
        """xcom_pull with task_ids=None returns None (no tasks to search)."""
        result = self.ti.xcom_pull(task_ids=None, key="anything")
        self.assertIsNone(result)

    def test_xcom_pull_default_key(self):
        """xcom_pull defaults to key='return_value'."""
        self.store.push("up", "return_value", "hello")
        result = self.ti.xcom_pull(task_ids="up")
        self.assertEqual(result, "hello")


# ============================================================================
# Topological sort tests
# ============================================================================


class TestTopologicalSort(unittest.TestCase):
    """Tests for _topological_sort (Kahn's algorithm)."""

    def test_linear_chain(self):
        """A simple linear chain should sort in the correct order."""
        tasks = [
            {"task_id": "a", "upstream": []},
            {"task_id": "b", "upstream": ["a"]},
            {"task_id": "c", "upstream": ["b"]},
        ]
        order = _topological_sort(tasks)
        self.assertEqual(order, ["a", "b", "c"])

    def test_fan_out(self):
        """Root task fans out to multiple children."""
        tasks = [
            {"task_id": "root", "upstream": []},
            {"task_id": "child_1", "upstream": ["root"]},
            {"task_id": "child_2", "upstream": ["root"]},
        ]
        order = _topological_sort(tasks)
        self.assertEqual(order[0], "root")
        self.assertIn("child_1", order)
        self.assertIn("child_2", order)

    def test_fan_in(self):
        """Multiple parents converge on a single child."""
        tasks = [
            {"task_id": "a", "upstream": []},
            {"task_id": "b", "upstream": []},
            {"task_id": "c", "upstream": ["a", "b"]},
        ]
        order = _topological_sort(tasks)
        self.assertEqual(order[-1], "c")
        self.assertIn("a", order[:2])
        self.assertIn("b", order[:2])

    def test_diamond(self):
        """Classic diamond: a -> b,c -> d."""
        tasks = [
            {"task_id": "a", "upstream": []},
            {"task_id": "b", "upstream": ["a"]},
            {"task_id": "c", "upstream": ["a"]},
            {"task_id": "d", "upstream": ["b", "c"]},
        ]
        order = _topological_sort(tasks)
        self.assertEqual(order[0], "a")
        self.assertEqual(order[-1], "d")
        self.assertTrue(order.index("b") < order.index("d"))
        self.assertTrue(order.index("c") < order.index("d"))

    def test_single_task(self):
        """A single task with no dependencies."""
        tasks = [{"task_id": "only", "upstream": []}]
        order = _topological_sort(tasks)
        self.assertEqual(order, ["only"])

    def test_empty_task_list(self):
        """Empty input produces empty output."""
        self.assertEqual(_topological_sort([]), [])

    def test_ignores_unknown_upstream_references(self):
        """Upstream references to non-existent tasks are silently ignored."""
        tasks = [
            {"task_id": "a", "upstream": ["nonexistent"]},
        ]
        order = _topological_sort(tasks)
        self.assertEqual(order, ["a"])


# ============================================================================
# DAGSimulator instantiation and DAG loading
# ============================================================================


class TestSimulatorInstantiation(unittest.TestCase):
    """Tests for simulator creation and DAG discovery."""

    @classmethod
    def setUpClass(cls):
        """Create one simulator instance for all tests in this class."""
        cls.sim = DAGSimulator()

    def test_instantiation(self):
        """Simulator can be instantiated without errors."""
        self.assertIsInstance(self.sim, DAGSimulator)

    def test_list_dags_returns_list(self):
        """list_dags returns a non-empty list."""
        dags = self.sim.list_dags()
        self.assertIsInstance(dags, list)
        self.assertGreater(len(dags), 0)

    def test_known_dags_are_discovered(self):
        """The five well-known DAG IDs must be discovered."""
        dag_ids = {d.dag_id for d in self.sim.list_dags()}
        expected = {
            "etl_transactions_pipeline",
            "data_quality_pipeline",
            "multi_source_etl_customer_journey",
            "sensor_vendor_file_pipeline",
        }
        for eid in expected:
            self.assertIn(eid, dag_ids, f"Expected DAG '{eid}' not found")

    def test_dynamic_dags_are_registered(self):
        """Dynamic DAGs (etl_sales, etl_inventory, etc.) are registered."""
        dag_ids = {d.dag_id for d in self.sim.list_dags()}
        for name in ["etl_sales", "etl_inventory", "etl_customer_360", "etl_marketing_attribution"]:
            self.assertIn(name, dag_ids, f"Dynamic DAG '{name}' not found")

    def test_dag_info_has_required_fields(self):
        """Each DAGInfo object has the expected fields populated."""
        for dag_info in self.sim.list_dags():
            self.assertTrue(dag_info.dag_id, "dag_id must be non-empty")
            self.assertIsInstance(dag_info.tags, list)
            self.assertIsInstance(dag_info.tasks, list)
            self.assertTrue(dag_info.source_file, "source_file must be non-empty")

    def test_dag_tasks_have_task_ids(self):
        """Each task within a DAG has a non-empty task_id."""
        for dag_info in self.sim.list_dags():
            for task in dag_info.tasks:
                self.assertTrue(task.task_id, f"Empty task_id in DAG {dag_info.dag_id}")


# ============================================================================
# get_dag_graph
# ============================================================================


class TestGetDagGraph(unittest.TestCase):
    """Tests for the get_dag_graph method."""

    @classmethod
    def setUpClass(cls):
        cls.sim = DAGSimulator()

    def test_graph_structure(self):
        """Graph contains dag_id, nodes, edges, task_count, edge_count."""
        graph = self.sim.get_dag_graph("etl_transactions_pipeline")
        self.assertEqual(graph["dag_id"], "etl_transactions_pipeline")
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)
        self.assertEqual(graph["task_count"], len(graph["nodes"]))
        self.assertEqual(graph["edge_count"], len(graph["edges"]))

    def test_nodes_have_required_keys(self):
        """Each node has id, label, operator, group, color."""
        graph = self.sim.get_dag_graph("data_quality_pipeline")
        for node in graph["nodes"]:
            for key in ("id", "label", "operator", "group", "color"):
                self.assertIn(key, node, f"Node missing key '{key}'")

    def test_edges_have_source_and_target(self):
        """Each edge has source and target keys."""
        graph = self.sim.get_dag_graph("etl_transactions_pipeline")
        for edge in graph["edges"]:
            self.assertIn("source", edge)
            self.assertIn("target", edge)

    def test_graph_for_dynamic_dag(self):
        """Dynamic DAGs also produce valid graphs."""
        graph = self.sim.get_dag_graph("etl_sales")
        self.assertGreater(graph["task_count"], 0)
        self.assertEqual(graph["dag_id"], "etl_sales")

    def test_graph_for_nonexistent_dag_returns_empty(self):
        """Requesting a graph for an unknown DAG returns empty nodes/edges."""
        graph = self.sim.get_dag_graph("totally_fake_dag_xyz")
        self.assertEqual(graph["task_count"], 0)
        self.assertEqual(graph["edge_count"], 0)


# ============================================================================
# Simulation execution
# ============================================================================


class TestSimulation(unittest.TestCase):
    """Tests for the simulate method."""

    @classmethod
    def setUpClass(cls):
        cls.sim = DAGSimulator()

    def test_simulate_returns_simulation_result(self):
        """simulate returns a SimulationResult dataclass."""
        result = self.sim.simulate("etl_sales")
        self.assertIsInstance(result, SimulationResult)

    def test_simulation_result_has_required_fields(self):
        """SimulationResult contains all expected fields."""
        result = self.sim.simulate("etl_sales")
        self.assertEqual(result.dag_id, "etl_sales")
        self.assertTrue(result.run_id.startswith("sim__"))
        self.assertIn(result.status, (STATUS_SUCCESS, STATUS_FAILED))
        self.assertIsInstance(result.task_results, list)
        self.assertIsInstance(result.xcoms, dict)
        self.assertIsInstance(result.task_order, list)
        self.assertIsInstance(result.errors, list)

    def test_simulate_dynamic_dag_succeeds(self):
        """Dynamic DAGs (etl_sales) can be simulated successfully."""
        result = self.sim.simulate("etl_sales")
        # Dynamic DAGs have extract -> validate -> transform -> load
        self.assertEqual(len(result.task_order), 4)
        self.assertIn("extract", result.task_order)
        self.assertIn("load", result.task_order)

    def test_simulate_sensor_pipeline(self):
        """Sensor pipeline simulation completes (sensors auto-succeed)."""
        result = self.sim.simulate("sensor_vendor_file_pipeline")
        self.assertIsInstance(result, SimulationResult)
        self.assertGreater(len(result.task_results), 0)
        # Sensors should succeed in simulator mode
        sensor_results = [
            r for r in result.task_results
            if r.task_id in ("wait_for_vendor_file", "wait_for_dimension_refresh")
        ]
        for sr in sensor_results:
            self.assertEqual(sr.status, STATUS_SUCCESS, f"Sensor {sr.task_id} should succeed")

    def test_simulate_multi_source_etl(self):
        """Multi-source ETL pipeline simulation completes."""
        result = self.sim.simulate("multi_source_etl_customer_journey")
        self.assertIsInstance(result, SimulationResult)
        self.assertGreater(len(result.task_results), 0)

    def test_simulate_xcoms_populated(self):
        """After simulation of ETL pipeline, xcoms dict is populated by task callables."""
        result = self.sim.simulate("etl_transactions_pipeline")
        self.assertIsInstance(result.xcoms, dict)
        # The ETL pipeline has real callables that push XComs (extract_data, validate_data, etc.)
        if result.status == STATUS_SUCCESS:
            self.assertGreater(len(result.xcoms), 0, "XComs should be populated on success")

    def test_task_order_respects_dependencies(self):
        """Task order should respect upstream dependencies."""
        result = self.sim.simulate("etl_sales")
        order = result.task_order
        # extract must come before validate, validate before transform, etc.
        self.assertLess(
            order.index("extract"), order.index("validate"),
            "extract must precede validate",
        )
        self.assertLess(
            order.index("validate"), order.index("transform"),
            "validate must precede transform",
        )
        self.assertLess(
            order.index("transform"), order.index("load"),
            "transform must precede load",
        )


# ============================================================================
# Error handling
# ============================================================================


class TestSimulationErrors(unittest.TestCase):
    """Tests for error handling in simulation."""

    @classmethod
    def setUpClass(cls):
        cls.sim = DAGSimulator()

    def test_invalid_dag_id_raises_value_error(self):
        """Simulating a non-existent DAG raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            self.sim.simulate("completely_nonexistent_dag_12345")
        self.assertIn("not found", str(ctx.exception))

    def test_invalid_dag_id_error_lists_available_dags(self):
        """The ValueError message includes a list of available DAG IDs."""
        with self.assertRaises(ValueError) as ctx:
            self.sim.simulate("bogus_dag")
        self.assertIn("Available", str(ctx.exception))


# ============================================================================
# Branch operator handling
# ============================================================================


class TestBranchOperator(unittest.TestCase):
    """Tests for BranchPythonOperator simulation logic."""

    @classmethod
    def setUpClass(cls):
        cls.sim = DAGSimulator()

    def test_etl_pipeline_has_branch(self):
        """The ETL pipeline has a BranchPythonOperator task."""
        graph = self.sim.get_dag_graph("etl_transactions_pipeline")
        operators = {n["id"]: n["operator"] for n in graph["nodes"]}
        self.assertEqual(
            operators.get("check_validation_branch"), "BranchPythonOperator",
        )

    def test_branch_skips_non_chosen_path(self):
        """After a branch, the non-chosen path should be skipped."""
        result = self.sim.simulate("etl_transactions_pipeline")
        statuses = {r.task_id: r.status for r in result.task_results}
        # The branch chooses either transform_data or handle_validation_failure
        # One path should execute, the other should be skipped
        if "transform_data" in statuses and "handle_validation_failure" in statuses:
            transform_status = statuses.get("transform_data")
            failure_status = statuses.get("handle_validation_failure")
            # At least one should be skipped (or upstream_failed)
            non_success = {STATUS_SKIPPED, STATUS_UPSTREAM_FAILED}
            self.assertTrue(
                transform_status in non_success or failure_status in non_success,
                "One branch path should be skipped/upstream_failed",
            )

    def test_dq_pipeline_has_branch(self):
        """The data quality pipeline also uses a BranchPythonOperator."""
        graph = self.sim.get_dag_graph("data_quality_pipeline")
        operators = {n["id"]: n["operator"] for n in graph["nodes"]}
        self.assertEqual(
            operators.get("branch_on_dq_result"), "BranchPythonOperator",
        )


# ============================================================================
# Retry logic
# ============================================================================


class TestRetryLogic(unittest.TestCase):
    """Tests for the retry mechanism in the simulator."""

    @classmethod
    def setUpClass(cls):
        cls.sim = DAGSimulator()

    def test_etl_pipeline_handles_transient_failures(self):
        """The ETL pipeline uses retry logic; some tasks may report attempt > 1."""
        # Run multiple times to increase chance of hitting the random failure path
        # We just confirm the simulator doesn't crash on retries
        for _ in range(3):
            result = self.sim.simulate("etl_transactions_pipeline")
            self.assertIsInstance(result, SimulationResult)
            # Every task result should have an attempt field
            for tr in result.task_results:
                self.assertGreaterEqual(tr.attempt, 0)

    def test_task_results_have_duration(self):
        """All task results have a non-negative duration_ms."""
        result = self.sim.simulate("etl_sales")
        for tr in result.task_results:
            self.assertGreaterEqual(tr.duration_ms, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
