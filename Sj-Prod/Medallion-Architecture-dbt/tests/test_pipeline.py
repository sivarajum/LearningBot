"""Tests for src.pipeline — MedallionPipeline class and data structures."""

from __future__ import annotations

from pathlib import Path

import pytest
from src.pipeline import CommandResult, LayerStats, MedallionPipeline, PipelineResult

# ---------------------------------------------------------------------------
# CommandResult
# ---------------------------------------------------------------------------


class TestCommandResult:
    """Tests for the CommandResult dataclass."""

    def test_success_on_zero_returncode(self):
        cr = CommandResult(command="dbt run", returncode=0, stdout="ok", stderr="", duration_seconds=1.0)
        assert cr.success is True

    def test_failure_on_nonzero_returncode(self):
        cr = CommandResult(command="dbt run", returncode=1, stdout="", stderr="error", duration_seconds=0.5)
        assert cr.success is False

    def test_stores_all_fields(self):
        cr = CommandResult(
            command="dbt test",
            returncode=0,
            stdout="all passed",
            stderr="",
            duration_seconds=3.14,
        )
        assert cr.command == "dbt test"
        assert cr.returncode == 0
        assert cr.stdout == "all passed"
        assert cr.stderr == ""
        assert cr.duration_seconds == pytest.approx(3.14)


# ---------------------------------------------------------------------------
# LayerStats
# ---------------------------------------------------------------------------


class TestLayerStats:
    """Tests for the LayerStats dataclass."""

    def test_defaults(self):
        ls = LayerStats(layer="bronze")
        assert ls.layer == "bronze"
        assert ls.models == []
        assert ls.row_counts == {}
        assert ls.total_rows == 0
        assert ls.sample_data == {}

    def test_with_data(self):
        ls = LayerStats(
            layer="gold",
            models=["gold_clv", "gold_revenue"],
            row_counts={"gold_clv": 100, "gold_revenue": 365},
            total_rows=465,
        )
        assert ls.layer == "gold"
        assert len(ls.models) == 2
        assert ls.total_rows == 465


# ---------------------------------------------------------------------------
# PipelineResult
# ---------------------------------------------------------------------------


class TestPipelineResult:
    """Tests for the PipelineResult dataclass."""

    def test_to_dict_basic(self):
        pr = PipelineResult(
            started_at="2025-01-01T00:00:00",
            finished_at="2025-01-01T00:01:00",
            duration_seconds=60.0,
            success=True,
        )
        d = pr.to_dict()
        assert d["success"] is True
        assert d["duration_seconds"] == 60.0
        assert d["started_at"] == "2025-01-01T00:00:00"
        assert d["steps"] == []
        assert d["layer_stats"] == {}
        assert d["errors"] == []

    def test_to_dict_with_steps(self):
        step = CommandResult(
            command="dbt run --select bronze",
            returncode=0,
            stdout="done",
            stderr="",
            duration_seconds=2.5,
        )
        pr = PipelineResult(
            started_at="2025-01-01T00:00:00",
            finished_at="2025-01-01T00:01:00",
            duration_seconds=60.0,
            success=True,
            steps=[step],
        )
        d = pr.to_dict()
        assert len(d["steps"]) == 1
        assert d["steps"][0]["command"] == "dbt run --select bronze"
        assert d["steps"][0]["success"] is True

    def test_to_dict_with_layer_stats(self):
        ls = LayerStats(
            layer="bronze",
            models=["bronze_customers"],
            row_counts={"bronze_customers": 500},
            total_rows=500,
        )
        pr = PipelineResult(
            started_at="2025-01-01T00:00:00",
            finished_at="2025-01-01T00:01:00",
            duration_seconds=10.0,
            success=True,
            layer_stats={"bronze": ls},
        )
        d = pr.to_dict()
        assert "bronze" in d["layer_stats"]
        assert d["layer_stats"]["bronze"]["total_rows"] == 500

    def test_to_dict_errors(self):
        pr = PipelineResult(
            started_at="2025-01-01T00:00:00",
            finished_at="2025-01-01T00:01:00",
            duration_seconds=5.0,
            success=False,
            errors=["Bronze layer failed", "Silver layer failed"],
        )
        d = pr.to_dict()
        assert d["success"] is False
        assert len(d["errors"]) == 2


# ---------------------------------------------------------------------------
# MedallionPipeline instantiation and configuration
# ---------------------------------------------------------------------------


class TestMedallionPipelineInit:
    """Tests for MedallionPipeline construction and properties."""

    def test_default_init(self):
        pipeline = MedallionPipeline()
        # Default project root is parent of pipeline.py's parent
        assert pipeline.project_root.is_absolute()
        assert pipeline.dbt_project_dir.name == "medallion_dbt"
        assert pipeline.data_dir.name == "data"
        assert pipeline.raw_data_dir.name == "raw"
        assert pipeline.duckdb_path.name == "warehouse.duckdb"

    def test_custom_root(self, tmp_path):
        pipeline = MedallionPipeline(tmp_path)
        assert pipeline.project_root == tmp_path
        assert pipeline.dbt_project_dir == tmp_path / "medallion_dbt"
        assert pipeline.data_dir == tmp_path / "data"
        assert pipeline.raw_data_dir == tmp_path / "data" / "raw"
        assert pipeline.duckdb_path == tmp_path / "data" / "warehouse.duckdb"

    def test_last_result_initially_none(self):
        pipeline = MedallionPipeline()
        assert pipeline.get_last_result() is None


class TestMedallionPipelineLayerModels:
    """Tests for the LAYER_MODELS class attribute."""

    def test_has_three_layers(self):
        assert set(MedallionPipeline.LAYER_MODELS.keys()) == {"bronze", "silver", "gold"}

    def test_bronze_models(self):
        expected = ["bronze_customers", "bronze_orders", "bronze_products"]
        assert MedallionPipeline.LAYER_MODELS["bronze"] == expected

    def test_silver_models(self):
        expected = ["silver_customers", "silver_orders", "silver_products"]
        assert MedallionPipeline.LAYER_MODELS["silver"] == expected

    def test_gold_models(self):
        expected = [
            "gold_customer_lifetime_value",
            "gold_product_performance",
            "gold_daily_revenue",
        ]
        assert MedallionPipeline.LAYER_MODELS["gold"] == expected


class TestMedallionPipelineLineage:
    """Tests for get_lineage()."""

    def test_lineage_has_nodes_and_edges(self):
        pipeline = MedallionPipeline()
        lineage = pipeline.get_lineage()
        assert "nodes" in lineage
        assert "edges" in lineage

    def test_lineage_node_count(self):
        pipeline = MedallionPipeline()
        lineage = pipeline.get_lineage()
        # 3 source + 3 bronze + 3 silver + 3 gold = 12 nodes
        assert len(lineage["nodes"]) == 12

    def test_lineage_edge_count(self):
        pipeline = MedallionPipeline()
        lineage = pipeline.get_lineage()
        # 3 source->bronze + 3 bronze->silver + 5 silver->gold = 11 edges
        assert len(lineage["edges"]) == 11

    def test_lineage_node_layers(self):
        pipeline = MedallionPipeline()
        lineage = pipeline.get_lineage()
        layers = {n["layer"] for n in lineage["nodes"]}
        assert layers == {"source", "bronze", "silver", "gold"}

    def test_lineage_source_nodes(self):
        pipeline = MedallionPipeline()
        lineage = pipeline.get_lineage()
        source_ids = {n["id"] for n in lineage["nodes"] if n["layer"] == "source"}
        assert source_ids == {"customers.csv", "orders.csv", "products.csv"}

    def test_lineage_edges_reference_valid_nodes(self):
        pipeline = MedallionPipeline()
        lineage = pipeline.get_lineage()
        node_ids = {n["id"] for n in lineage["nodes"]}
        for edge in lineage["edges"]:
            assert edge["from"] in node_ids, f"Edge 'from' references unknown node: {edge['from']}"
            assert edge["to"] in node_ids, f"Edge 'to' references unknown node: {edge['to']}"


class TestMedallionPipelineLayerStats:
    """Tests for get_layer_stats() when no warehouse exists."""

    def test_stats_without_warehouse(self, tmp_path):
        """When no DuckDB file exists, stats should return empty counts."""
        pipeline = MedallionPipeline(tmp_path)
        stats = pipeline.get_layer_stats("bronze")
        assert stats.layer == "bronze"
        assert stats.total_rows == 0
        assert stats.row_counts == {}

    def test_get_all_layer_stats_keys(self, tmp_path):
        pipeline = MedallionPipeline(tmp_path)
        all_stats = pipeline.get_all_layer_stats()
        assert set(all_stats.keys()) == {"bronze", "silver", "gold"}

    def test_model_preview_without_warehouse(self, tmp_path):
        """When no DuckDB file exists, preview should return empty list."""
        pipeline = MedallionPipeline(tmp_path)
        rows = pipeline.get_model_preview("bronze", "bronze_customers")
        assert rows == []
