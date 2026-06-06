"""
Unit tests for DAG definitions (dags/*.py).

Verifies that each DAG file:
  - Can be imported without errors
  - Contains a valid DAG_ID
  - Defines task callables that are importable
  - Has consistent structure

Run:
    PYTHONPATH=. pytest tests/test_dags.py -v
"""

import importlib
import importlib.util
import os
import sys
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_DAGS_DIR = Path(_ROOT) / "dags"

# All known DAG files (by convention dag_NN_*.py)
DAG_FILES = sorted(_DAGS_DIR.glob("dag_*.py"))


def _import_dag_module(dag_file: Path):
    """Import a DAG file as a module and return it."""
    module_name = f"test_import_{dag_file.stem}"
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, dag_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# ============================================================================
# Test: all DAG files can be imported
# ============================================================================


class TestDagImports(unittest.TestCase):
    """Each DAG file under dags/ can be imported without raising exceptions."""

    def test_dag_files_exist(self):
        """At least one DAG file exists in dags/."""
        self.assertGreater(len(DAG_FILES), 0, "No dag_*.py files found in dags/")

    def test_import_dag_01_etl_pipeline(self):
        """dag_01_etl_pipeline.py imports without error."""
        module = _import_dag_module(_DAGS_DIR / "dag_01_etl_pipeline.py")
        self.assertIsNotNone(module)

    def test_import_dag_02_dynamic_dag(self):
        """dag_02_dynamic_dag.py imports without error."""
        module = _import_dag_module(_DAGS_DIR / "dag_02_dynamic_dag.py")
        self.assertIsNotNone(module)

    def test_import_dag_03_sensor_pipeline(self):
        """dag_03_sensor_pipeline.py imports without error."""
        module = _import_dag_module(_DAGS_DIR / "dag_03_sensor_pipeline.py")
        self.assertIsNotNone(module)

    def test_import_dag_04_data_quality(self):
        """dag_04_data_quality.py imports without error."""
        module = _import_dag_module(_DAGS_DIR / "dag_04_data_quality.py")
        self.assertIsNotNone(module)

    def test_import_dag_05_multi_source_etl(self):
        """dag_05_multi_source_etl.py imports without error."""
        module = _import_dag_module(_DAGS_DIR / "dag_05_multi_source_etl.py")
        self.assertIsNotNone(module)


# ============================================================================
# Test: DAG_ID is defined and non-empty
# ============================================================================


class TestDagIds(unittest.TestCase):
    """Each DAG module exports a DAG_ID constant."""

    def test_dag_01_has_dag_id(self):
        module = _import_dag_module(_DAGS_DIR / "dag_01_etl_pipeline.py")
        self.assertTrue(hasattr(module, "DAG_ID"))
        self.assertEqual(module.DAG_ID, "etl_transactions_pipeline")

    def test_dag_03_has_dag_id(self):
        module = _import_dag_module(_DAGS_DIR / "dag_03_sensor_pipeline.py")
        self.assertTrue(hasattr(module, "DAG_ID"))
        self.assertEqual(module.DAG_ID, "sensor_vendor_file_pipeline")

    def test_dag_04_has_dag_id(self):
        module = _import_dag_module(_DAGS_DIR / "dag_04_data_quality.py")
        self.assertTrue(hasattr(module, "DAG_ID"))
        self.assertEqual(module.DAG_ID, "data_quality_pipeline")

    def test_dag_05_has_dag_id(self):
        module = _import_dag_module(_DAGS_DIR / "dag_05_multi_source_etl.py")
        self.assertTrue(hasattr(module, "DAG_ID"))
        self.assertEqual(module.DAG_ID, "multi_source_etl_customer_journey")


# ============================================================================
# Test: DAG 01 — ETL Pipeline structure
# ============================================================================


class TestDag01Structure(unittest.TestCase):
    """Verify DAG 01 exports the expected task callables."""

    @classmethod
    def setUpClass(cls):
        cls.module = _import_dag_module(_DAGS_DIR / "dag_01_etl_pipeline.py")

    def test_has_extract_data(self):
        self.assertTrue(callable(getattr(self.module, "extract_data", None)))

    def test_has_validate_data(self):
        self.assertTrue(callable(getattr(self.module, "validate_data", None)))

    def test_has_check_validation_branch(self):
        self.assertTrue(callable(getattr(self.module, "check_validation_branch", None)))

    def test_has_transform_data(self):
        self.assertTrue(callable(getattr(self.module, "transform_data", None)))

    def test_has_load_data(self):
        self.assertTrue(callable(getattr(self.module, "load_data", None)))

    def test_has_notify_success(self):
        self.assertTrue(callable(getattr(self.module, "notify_success", None)))

    def test_has_default_args(self):
        self.assertTrue(hasattr(self.module, "DEFAULT_ARGS"))
        self.assertIsInstance(self.module.DEFAULT_ARGS, dict)
        self.assertIn("retries", self.module.DEFAULT_ARGS)

    def test_has_dag_object(self):
        """Module-level 'dag' object should exist."""
        self.assertTrue(hasattr(self.module, "dag"))


# ============================================================================
# Test: DAG 02 — Dynamic DAG factory
# ============================================================================


class TestDag02DynamicFactory(unittest.TestCase):
    """Verify DAG 02 generates DAGs from pipeline_config.json."""

    @classmethod
    def setUpClass(cls):
        cls.module = _import_dag_module(_DAGS_DIR / "dag_02_dynamic_dag.py")

    def test_has_config(self):
        """Module should load pipeline config."""
        self.assertTrue(hasattr(self.module, "CONFIG"))
        self.assertIsInstance(self.module.CONFIG, dict)

    def test_config_has_pipelines(self):
        """Config should contain a 'pipelines' list."""
        self.assertIn("pipelines", self.module.CONFIG)
        self.assertIsInstance(self.module.CONFIG["pipelines"], list)

    def test_get_generated_dag_ids(self):
        """get_generated_dag_ids returns a list of generated dag_id strings."""
        self.assertTrue(callable(getattr(self.module, "get_generated_dag_ids", None)))
        dag_ids = self.module.get_generated_dag_ids()
        self.assertIsInstance(dag_ids, list)
        self.assertGreater(len(dag_ids), 0)

    def test_generated_dag_ids_start_with_etl(self):
        """All dynamic DAG IDs should follow the etl_{name} pattern."""
        for dag_id in self.module.get_generated_dag_ids():
            self.assertTrue(dag_id.startswith("etl_"), f"'{dag_id}' does not start with 'etl_'")

    def test_create_pipeline_dag_callable(self):
        """create_pipeline_dag is a callable factory function."""
        self.assertTrue(callable(getattr(self.module, "create_pipeline_dag", None)))

    def test_factory_creates_dag_from_config(self):
        """create_pipeline_dag returns a DAG-like object with a dag_id attribute."""
        sample_config = {
            "name": "test_pipeline",
            "sources": [{"type": "postgres", "connection_id": "test_conn"}],
            "destination": {"type": "bigquery", "table": "test_table"},
        }
        global_cfg = self.module.CONFIG.get("global_settings", {})
        dag = self.module.create_pipeline_dag(sample_config, global_cfg)
        self.assertEqual(dag.dag_id, "etl_test_pipeline")


# ============================================================================
# Test: DAG 03 — Sensor Pipeline structure
# ============================================================================


class TestDag03Structure(unittest.TestCase):
    """Verify DAG 03 exports the expected task callables."""

    @classmethod
    def setUpClass(cls):
        cls.module = _import_dag_module(_DAGS_DIR / "dag_03_sensor_pipeline.py")

    def test_has_check_file_metadata(self):
        self.assertTrue(callable(getattr(self.module, "check_file_metadata", None)))

    def test_has_process_vendor_file(self):
        self.assertTrue(callable(getattr(self.module, "process_vendor_file", None)))

    def test_has_join_with_dimension(self):
        self.assertTrue(callable(getattr(self.module, "join_with_dimension", None)))

    def test_has_load_vendor_to_warehouse(self):
        self.assertTrue(callable(getattr(self.module, "load_vendor_to_warehouse", None)))


# ============================================================================
# Test: DAG 04 — Data Quality Pipeline structure
# ============================================================================


class TestDag04Structure(unittest.TestCase):
    """Verify DAG 04 exports the expected DQ check callables."""

    @classmethod
    def setUpClass(cls):
        cls.module = _import_dag_module(_DAGS_DIR / "dag_04_data_quality.py")

    def test_has_check_null_rates(self):
        self.assertTrue(callable(getattr(self.module, "check_null_rates", None)))

    def test_has_check_row_count(self):
        self.assertTrue(callable(getattr(self.module, "check_row_count", None)))

    def test_has_check_duplicates(self):
        self.assertTrue(callable(getattr(self.module, "check_duplicates", None)))

    def test_has_check_referential_integrity(self):
        self.assertTrue(callable(getattr(self.module, "check_referential_integrity", None)))

    def test_has_check_data_freshness(self):
        self.assertTrue(callable(getattr(self.module, "check_data_freshness", None)))

    def test_has_aggregate_dq_results(self):
        self.assertTrue(callable(getattr(self.module, "aggregate_dq_results", None)))

    def test_has_branch_on_dq_result(self):
        self.assertTrue(callable(getattr(self.module, "branch_on_dq_result", None)))

    def test_has_thresholds(self):
        self.assertTrue(hasattr(self.module, "THRESHOLDS"))
        self.assertIsInstance(self.module.THRESHOLDS, dict)
        self.assertIn("max_null_rate", self.module.THRESHOLDS)


# ============================================================================
# Test: DAG 05 — Multi-Source ETL structure
# ============================================================================


class TestDag05Structure(unittest.TestCase):
    """Verify DAG 05 exports the expected task callables."""

    @classmethod
    def setUpClass(cls):
        cls.module = _import_dag_module(_DAGS_DIR / "dag_05_multi_source_etl.py")

    def test_has_ingest_crm_data(self):
        self.assertTrue(callable(getattr(self.module, "ingest_crm_data", None)))

    def test_has_ingest_erp_data(self):
        self.assertTrue(callable(getattr(self.module, "ingest_erp_data", None)))

    def test_has_ingest_analytics_data(self):
        self.assertTrue(callable(getattr(self.module, "ingest_analytics_data", None)))

    def test_has_validate_ingest_completeness(self):
        self.assertTrue(callable(getattr(self.module, "validate_ingest_completeness", None)))

    def test_has_resolve_customer_entities(self):
        self.assertTrue(callable(getattr(self.module, "resolve_customer_entities", None)))

    def test_has_build_customer_journey(self):
        self.assertTrue(callable(getattr(self.module, "build_customer_journey", None)))

    def test_has_publish_to_bi(self):
        self.assertTrue(callable(getattr(self.module, "publish_to_bi", None)))

    def test_has_update_data_catalogue(self):
        self.assertTrue(callable(getattr(self.module, "update_data_catalogue", None)))


# ============================================================================
# Test: All DAG files have Airflow graceful fallback
# ============================================================================


class TestAirflowFallback(unittest.TestCase):
    """All DAG files define AIRFLOW_AVAILABLE and work without Airflow installed."""

    def test_all_dag_files_importable_without_airflow(self):
        """Every dag_*.py file can be imported without apache-airflow installed."""
        for dag_file in DAG_FILES:
            with self.subTest(dag_file=dag_file.name):
                try:
                    module = _import_dag_module(dag_file)
                    self.assertIsNotNone(module, f"Failed to import {dag_file.name}")
                except Exception as exc:
                    self.fail(f"Importing {dag_file.name} raised: {exc}")

    def test_all_dag_files_have_airflow_available_flag(self):
        """Each DAG file defines an AIRFLOW_AVAILABLE boolean."""
        for dag_file in DAG_FILES:
            with self.subTest(dag_file=dag_file.name):
                module = _import_dag_module(dag_file)
                self.assertTrue(
                    hasattr(module, "AIRFLOW_AVAILABLE"),
                    f"{dag_file.name} missing AIRFLOW_AVAILABLE flag",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
