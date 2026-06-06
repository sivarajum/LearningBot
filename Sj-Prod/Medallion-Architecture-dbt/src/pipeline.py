"""
pipeline.py — Orchestrate: data generation → dbt bronze/silver/gold → dbt tests.

Key design decisions:
  - dbt is invoked via subprocess so it runs in its own venv-aware process.
  - DuckDB is queried directly via the duckdb Python driver for stats / previews.
  - All public methods return plain dataclass/dict results — no framework coupling.
  - Graceful degradation: if dbt is not installed, helpful error message is shown.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dataclasses for structured results
# ---------------------------------------------------------------------------


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def success(self) -> bool:
        return self.returncode == 0


@dataclass
class LayerStats:
    layer: str
    models: List[str] = field(default_factory=list)
    row_counts: Dict[str, int] = field(default_factory=dict)
    total_rows: int = 0
    sample_data: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


@dataclass
class PipelineResult:
    started_at: str
    finished_at: str
    duration_seconds: float
    success: bool
    steps: List[CommandResult] = field(default_factory=list)
    layer_stats: Dict[str, LayerStats] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 2),
            "success": self.success,
            "errors": self.errors,
            "steps": [
                {
                    "command": s.command,
                    "returncode": s.returncode,
                    "success": s.success,
                    "duration_seconds": round(s.duration_seconds, 2),
                    "stdout_tail": s.stdout[-500:] if s.stdout else "",
                    "stderr_tail": s.stderr[-500:] if s.stderr else "",
                }
                for s in self.steps
            ],
            "layer_stats": {
                layer: {
                    "layer": ls.layer,
                    "models": ls.models,
                    "row_counts": ls.row_counts,
                    "total_rows": ls.total_rows,
                }
                for layer, ls in self.layer_stats.items()
            },
        }


# ---------------------------------------------------------------------------
# MedallionPipeline
# ---------------------------------------------------------------------------


class MedallionPipeline:
    """
    Orchestrates the full Medallion Architecture pipeline.

    Parameters
    ----------
    project_root : Path | None
        Root of the POC directory (default: parent of this file).
    """

    # Model names per layer — used for DuckDB queries
    LAYER_MODELS: Dict[str, List[str]] = {
        "bronze": ["bronze_customers", "bronze_orders", "bronze_products"],
        "silver": ["silver_customers", "silver_orders", "silver_products"],
        "gold": [
            "gold_customer_lifetime_value",
            "gold_product_performance",
            "gold_daily_revenue",
        ],
    }

    # dbt-duckdb prefixes schemas with the DuckDB database name (default "main").
    # The effective schema for layer "bronze" becomes "main_bronze".
    # This method resolves the actual schema name by checking what exists.
    def _resolve_schema(self, conn, layer: str) -> str:
        """Return the actual DuckDB schema name for a given layer string."""
        # Try the prefixed form first (dbt-duckdb default), then bare layer name.
        candidates = [f"main_{layer}", layer]
        for candidate in candidates:
            try:
                result = conn.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = ?",
                    [candidate],
                ).fetchone()
                if result and result[0] > 0:
                    return candidate
            except Exception as exc:  # noqa: BLE001
                logger.debug("Schema resolution failed for candidate %r: %s", candidate, exc)
                continue
        # Fallback: return the prefixed form (will return -1 counts gracefully)
        return f"main_{layer}"

    def __init__(self, project_root: Optional[Path] = None) -> None:
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = Path(project_root).resolve()
        self.dbt_project_dir = self.project_root / "medallion_dbt"
        self.data_dir = self.project_root / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.duckdb_path = self.data_dir / "warehouse.duckdb"
        self._last_result: Optional[PipelineResult] = None

    # ------------------------------------------------------------------
    # dbt binary resolution
    # ------------------------------------------------------------------

    def _dbt_bin(self) -> str:
        """
        Return the path to the dbt executable.

        Priority:
          1. Same directory as the running Python interpreter (venv/bin/dbt)
          2. PATH lookup via shutil.which
        """
        venv_dbt = Path(sys.executable).parent / "dbt"
        if venv_dbt.exists():
            return str(venv_dbt)
        found = shutil.which("dbt")
        if found:
            return found
        return "dbt"  # last resort — will fail with FileNotFoundError

    # ------------------------------------------------------------------
    # dbt check
    # ------------------------------------------------------------------

    def check_dbt_installed(self) -> bool:
        """Return True if dbt-duckdb is importable / callable."""
        try:
            result = subprocess.run(
                [self._dbt_bin(), "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    # ------------------------------------------------------------------
    # subprocess helper
    # ------------------------------------------------------------------

    def run_dbt_command(self, command: str) -> CommandResult:
        """
        Run a dbt CLI command inside the medallion_dbt project directory.

        Parameters
        ----------
        command : str
            e.g. "run --select bronze" or "test"
        """
        env = os.environ.copy()
        env["RAW_DATA_PATH"] = str(self.raw_data_dir)
        env["DUCKDB_PATH"] = str(self.duckdb_path)
        # Ensure profiles.yml is picked up from the project dir
        env["DBT_PROFILES_DIR"] = str(self.dbt_project_dir)

        dbt = self._dbt_bin()
        full_cmd = (
            f'"{dbt}" {command}'
            f" --project-dir {self.dbt_project_dir}"
            f" --profiles-dir {self.dbt_project_dir}"
        )
        logger.info("Running: %s", full_cmd)

        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=full_cmd,
                returncode=124,
                stdout="",
                stderr="dbt command timed out after 300 seconds",
                duration_seconds=300.0,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("dbt command failed with unexpected error: %s", exc, exc_info=True)
            return CommandResult(
                command=full_cmd,
                returncode=1,
                stdout="",
                stderr=str(exc),
                duration_seconds=time.perf_counter() - t0,
            )

        duration = time.perf_counter() - t0
        return CommandResult(
            command=full_cmd,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_seconds=duration,
        )

    # ------------------------------------------------------------------
    # DuckDB query helpers
    # ------------------------------------------------------------------

    def _get_duckdb_connection(self):  # type: ignore[return]
        """Return a read-only DuckDB connection (creates file if needed)."""
        try:
            import duckdb  # noqa: PLC0415

            return duckdb.connect(str(self.duckdb_path), read_only=False)
        except ImportError as exc:
            raise RuntimeError(
                "duckdb Python package not installed. Run: pip install duckdb"
            ) from exc

    def _table_exists(self, conn, schema: str, table: str) -> bool:
        """Check whether a table/view exists in DuckDB."""
        try:
            result = conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = ? AND table_name = ?",
                [schema, table],
            ).fetchone()
            return (result[0] if result else 0) > 0
        except Exception as exc:  # noqa: BLE001
            logger.warning("Error checking table existence %s.%s: %s", schema, table, exc)
            return False

    def get_layer_stats(self, layer: str, include_sample: bool = False) -> LayerStats:
        """
        Return row counts (and optionally sample rows) for all models in a layer.

        Parameters
        ----------
        layer : str
            One of "bronze", "silver", "gold".
        include_sample : bool
            If True, include up to 20 rows per model in stats.sample_data.
        """
        models = self.LAYER_MODELS.get(layer, [])
        stats = LayerStats(layer=layer, models=models)

        if not self.duckdb_path.exists():
            logger.warning("Warehouse not found at %s — pipeline not yet run.", self.duckdb_path)
            return stats

        try:
            conn = self._get_duckdb_connection()
            # Resolve the actual schema name (may be "main_bronze" etc.)
            schema = self._resolve_schema(conn, layer)
            for model in models:
                if self._table_exists(conn, schema, model):
                    row = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{model}"').fetchone()
                    count = row[0] if row else 0
                    stats.row_counts[model] = count
                    stats.total_rows += count

                    if include_sample:
                        rows = conn.execute(
                            f'SELECT * FROM "{schema}"."{model}" LIMIT 20'
                        ).fetchdf()
                        stats.sample_data[model] = rows.to_dict(orient="records")
                else:
                    stats.row_counts[model] = -1  # -1 = not yet materialized
            conn.close()
        except Exception as exc:  # noqa: BLE001
            logger.error("Error querying DuckDB layer %s: %s", layer, exc)

        return stats

    def get_model_preview(self, layer: str, model: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Return up to `limit` rows from a specific model."""
        if not self.duckdb_path.exists():
            return []
        try:
            conn = self._get_duckdb_connection()
            schema = self._resolve_schema(conn, layer)
            if self._table_exists(conn, schema, model):
                df = conn.execute(f'SELECT * FROM "{schema}"."{model}" LIMIT {limit}').fetchdf()
                conn.close()
                # Convert timestamps/dates to strings for JSON serialisation.
                # Use object dtype check to catch all datetime-like columns
                # (pandas 2.x uses datetime64[us] which select_dtypes won't match
                # with a literal frequency string).
                for col in df.columns:
                    if hasattr(df[col], "dt") or str(df[col].dtype).startswith("datetime"):
                        df[col] = df[col].astype(str)
                    elif str(df[col].dtype) in ("date32[day][pyarrow]", "object"):
                        pass  # already string-compatible
                return df.to_dict(orient="records")
            conn.close()
        except Exception as exc:  # noqa: BLE001
            logger.error("Error previewing %s.%s: %s", layer, model, exc)
        return []

    def get_all_layer_stats(self) -> Dict[str, LayerStats]:
        """Return stats for all three layers."""
        return {
            layer: self.get_layer_stats(layer)
            for layer in ["bronze", "silver", "gold"]
        }

    # ------------------------------------------------------------------
    # Full pipeline
    # ------------------------------------------------------------------

    def run_full_pipeline(self) -> PipelineResult:
        """
        Execute the complete pipeline:
          1. Generate synthetic CSV data
          2. dbt deps (install dbt packages if any)
          3. dbt run --select bronze
          4. dbt run --select silver
          5. dbt run --select gold
          6. dbt test
        """
        started_at = datetime.utcnow().isoformat()
        t_start = time.perf_counter()
        steps: List[CommandResult] = []
        errors: List[str] = []

        # ---- pre-flight: dbt installed? --------------------------------
        if not self.check_dbt_installed():
            msg = (
                "dbt-duckdb is not installed or not on PATH. "
                "Run: pip install dbt-duckdb>=1.7.0"
            )
            logger.error(msg)
            return PipelineResult(
                started_at=started_at,
                finished_at=datetime.utcnow().isoformat(),
                duration_seconds=time.perf_counter() - t_start,
                success=False,
                errors=[msg],
            )

        # ---- step 1: generate data ------------------------------------
        logger.info("Step 1/6 — Generating synthetic CSV data")
        try:
            from .data_generator import generate_all  # noqa: PLC0415

            self.raw_data_dir.mkdir(parents=True, exist_ok=True)
            generate_all(self.raw_data_dir)
        except Exception as exc:  # noqa: BLE001
            err = f"Data generation failed: {exc}"
            logger.error(err)
            errors.append(err)
            return PipelineResult(
                started_at=started_at,
                finished_at=datetime.utcnow().isoformat(),
                duration_seconds=time.perf_counter() - t_start,
                success=False,
                steps=steps,
                errors=errors,
            )

        # ---- step 2: dbt deps (optional) ------------------------------
        logger.info("Step 2/6 — dbt deps")
        deps_result = self.run_dbt_command("deps")
        steps.append(deps_result)
        if not deps_result.success:
            logger.warning("dbt deps returned non-zero, continuing anyway...")

        # ---- step 3: bronze -------------------------------------------
        logger.info("Step 3/6 — dbt run bronze layer")
        bronze_result = self.run_dbt_command("run --select bronze")
        steps.append(bronze_result)
        if not bronze_result.success:
            errors.append(f"Bronze layer failed: {bronze_result.stderr[-300:]}")

        # ---- step 4: silver -------------------------------------------
        logger.info("Step 4/6 — dbt run silver layer")
        silver_result = self.run_dbt_command("run --select silver")
        steps.append(silver_result)
        if not silver_result.success:
            errors.append(f"Silver layer failed: {silver_result.stderr[-300:]}")

        # ---- step 5: gold ---------------------------------------------
        logger.info("Step 5/6 — dbt run gold layer")
        gold_result = self.run_dbt_command("run --select gold")
        steps.append(gold_result)
        if not gold_result.success:
            errors.append(f"Gold layer failed: {gold_result.stderr[-300:]}")

        # ---- step 6: tests --------------------------------------------
        logger.info("Step 6/6 — dbt test")
        test_result = self.run_dbt_command("test")
        steps.append(test_result)
        if not test_result.success:
            logger.warning("Some dbt tests failed (non-fatal for pipeline)")

        # ---- collect stats --------------------------------------------
        layer_stats = self.get_all_layer_stats()

        finished_at = datetime.utcnow().isoformat()
        duration = time.perf_counter() - t_start

        overall_success = all(s.success for s in steps if "run" in s.command) and not errors

        result = PipelineResult(
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration,
            success=overall_success,
            steps=steps,
            layer_stats=layer_stats,
            errors=errors,
        )
        self._last_result = result
        logger.info(
            "Pipeline %s in %.1fs",
            "SUCCEEDED" if overall_success else "FAILED",
            duration,
        )
        return result

    def get_last_result(self) -> Optional[PipelineResult]:
        """Return the result of the most recent pipeline run (in-process only)."""
        return self._last_result

    # ------------------------------------------------------------------
    # Lineage helper
    # ------------------------------------------------------------------

    def get_lineage(self) -> Dict[str, Any]:
        """
        Return a graph-like dict describing source → bronze → silver → gold lineage.
        """
        return {
            "nodes": [
                {"id": "customers.csv", "layer": "source", "type": "csv"},
                {"id": "orders.csv", "layer": "source", "type": "csv"},
                {"id": "products.csv", "layer": "source", "type": "csv"},
                {"id": "bronze_customers", "layer": "bronze", "type": "table"},
                {"id": "bronze_orders", "layer": "bronze", "type": "table"},
                {"id": "bronze_products", "layer": "bronze", "type": "table"},
                {"id": "silver_customers", "layer": "silver", "type": "table"},
                {"id": "silver_orders", "layer": "silver", "type": "table"},
                {"id": "silver_products", "layer": "silver", "type": "table"},
                {"id": "gold_customer_lifetime_value", "layer": "gold", "type": "table"},
                {"id": "gold_product_performance", "layer": "gold", "type": "table"},
                {"id": "gold_daily_revenue", "layer": "gold", "type": "table"},
            ],
            "edges": [
                # source → bronze
                {"from": "customers.csv", "to": "bronze_customers"},
                {"from": "orders.csv", "to": "bronze_orders"},
                {"from": "products.csv", "to": "bronze_products"},
                # bronze → silver
                {"from": "bronze_customers", "to": "silver_customers"},
                {"from": "bronze_orders", "to": "silver_orders"},
                {"from": "bronze_products", "to": "silver_products"},
                # silver → gold
                {"from": "silver_customers", "to": "gold_customer_lifetime_value"},
                {"from": "silver_orders", "to": "gold_customer_lifetime_value"},
                {"from": "silver_orders", "to": "gold_product_performance"},
                {"from": "silver_products", "to": "gold_product_performance"},
                {"from": "silver_orders", "to": "gold_daily_revenue"},
            ],
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )
    pipeline = MedallionPipeline()
    result = pipeline.run_full_pipeline()
    logger.info("Pipeline result:\n%s", json.dumps(result.to_dict(), indent=2))
