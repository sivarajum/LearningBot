"""
api.py — FastAPI application exposing Medallion Architecture pipeline data.

Endpoints:
  GET  /health
  GET  /layers                    — all layer stats
  GET  /layers/{layer}            — single layer stats
  GET  /layers/{layer}/{model}    — 20-row preview
  POST /pipeline/run              — trigger full pipeline
  GET  /pipeline/status           — last run result
  GET  /lineage                   — data lineage graph
  GET  /concepts                  — architecture concepts reference
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .pipeline import MedallionPipeline
from .settings import CORS_ORIGINS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Medallion Architecture API",
    description=(
        "POC-08: dbt + DuckDB Medallion Architecture — Bronze / Silver / Gold layers. "
        "Exposes pipeline orchestration, layer data previews, and lineage."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pipeline singleton (lazy init)
# ---------------------------------------------------------------------------

_pipeline: Optional[MedallionPipeline] = None


def get_pipeline() -> MedallionPipeline:
    """Return the singleton MedallionPipeline, creating it if needed."""
    global _pipeline  # noqa: PLW0603
    if _pipeline is None:
        _pipeline = MedallionPipeline()
    return _pipeline


# ---------------------------------------------------------------------------
# In-memory pipeline state
# ---------------------------------------------------------------------------

_last_pipeline_result: Optional[Dict[str, Any]] = None
_pipeline_running: bool = False


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    dbt_installed: bool
    warehouse_exists: bool
    version: str = "1.0.0"


class LayerSummary(BaseModel):
    layer: str
    models: List[str]
    row_counts: Dict[str, int]
    total_rows: int
    pipeline_run: bool


class PipelineStatusResponse(BaseModel):
    running: bool
    last_result: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    """Quick liveness + readiness check."""
    pipeline = get_pipeline()
    return HealthResponse(
        status="ok",
        dbt_installed=pipeline.check_dbt_installed(),
        warehouse_exists=pipeline.duckdb_path.exists(),
    )


@app.get("/layers", tags=["Data"])
def list_layers() -> Dict[str, Dict[str, Any]]:
    """Return high-level stats for all three medallion layers."""
    pipeline = get_pipeline()
    all_stats = pipeline.get_all_layer_stats()
    result = {}
    for layer, stats in all_stats.items():
        result[layer] = {
            "layer": stats.layer,
            "models": stats.models,
            "row_counts": stats.row_counts,
            "total_rows": stats.total_rows,
            "pipeline_run": pipeline.duckdb_path.exists(),
        }
    return result


@app.get("/layers/{layer}", tags=["Data"])
def get_layer(layer: str) -> Dict[str, Any]:
    """Return detailed stats for a single layer (bronze | silver | gold)."""
    valid_layers = ["bronze", "silver", "gold"]
    if layer not in valid_layers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid layer '{layer}'. Must be one of: {valid_layers}",
        )
    pipeline = get_pipeline()
    stats = pipeline.get_layer_stats(layer, include_sample=False)
    return {
        "layer": stats.layer,
        "models": stats.models,
        "row_counts": stats.row_counts,
        "total_rows": stats.total_rows,
        "pipeline_run": pipeline.duckdb_path.exists(),
    }


@app.get("/layers/{layer}/{model}", tags=["Data"])
def get_model_preview(layer: str, model: str, limit: int = 20) -> Dict[str, Any]:
    """Return up to `limit` rows from a specific dbt model."""
    valid_layers = ["bronze", "silver", "gold"]
    if layer not in valid_layers:
        raise HTTPException(status_code=400, detail=f"Invalid layer '{layer}'")

    pipeline = get_pipeline()
    known_models = pipeline.LAYER_MODELS.get(layer, [])
    if model not in known_models:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model}' not found in layer '{layer}'. Available: {known_models}",
        )

    if not pipeline.duckdb_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Warehouse not found. Run POST /pipeline/run first.",
        )

    rows = pipeline.get_model_preview(layer, model, limit=min(limit, 100))
    return {
        "layer": layer,
        "model": model,
        "row_count": len(rows),
        "data": rows,
    }


@app.post("/pipeline/run", tags=["Pipeline"])
async def run_pipeline(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Trigger a full pipeline run (async background task).

    The pipeline generates fresh data, runs dbt bronze→silver→gold, and runs tests.
    Poll GET /pipeline/status to check progress.
    """
    global _pipeline_running, _last_pipeline_result  # noqa: PLW0603

    if _pipeline_running:
        return {"status": "already_running", "message": "Pipeline is already in progress."}

    def _run() -> None:
        global _pipeline_running, _last_pipeline_result  # noqa: PLW0603
        _pipeline_running = True
        try:
            pipeline = get_pipeline()
            result = pipeline.run_full_pipeline()
            _last_pipeline_result = result.to_dict()
        except Exception as exc:  # noqa: BLE001
            logger.error("Pipeline background task failed: %s", exc)
            _last_pipeline_result = {"success": False, "errors": [str(exc)]}
        finally:
            _pipeline_running = False

    background_tasks.add_task(_run)
    return {
        "status": "started",
        "message": "Pipeline started in background. Poll GET /pipeline/status.",
    }


@app.get("/pipeline/status", response_model=PipelineStatusResponse, tags=["Pipeline"])
def pipeline_status() -> PipelineStatusResponse:
    """Return the running state and last pipeline result."""
    return PipelineStatusResponse(
        running=_pipeline_running,
        last_result=_last_pipeline_result,
    )


@app.get("/lineage", tags=["Metadata"])
def get_lineage() -> Dict[str, Any]:
    """Return the data lineage graph: source files → bronze → silver → gold."""
    pipeline = get_pipeline()
    return pipeline.get_lineage()


@app.get("/concepts", tags=["Metadata"])
def get_concepts() -> List[Dict[str, str]]:
    """Return a quick-reference glossary of Medallion Architecture concepts."""
    return [
        {
            "term": "Medallion Architecture",
            "definition": (
                "A multi-layer data design pattern (Bronze/Silver/Gold) that progressively "
                "refines raw data into curated, business-ready assets."
            ),
        },
        {
            "term": "Bronze Layer",
            "definition": (
                "Raw ingest layer — data is loaded as-is from source systems with minimal "
                "transformation. Only type casts and metadata columns (_ingested_at, _source_file) "
                "are added. Serves as the system of record."
            ),
        },
        {
            "term": "Silver Layer",
            "definition": (
                "Cleansed and conformed layer — data is validated, deduplicated, enriched with "
                "derived columns, and standardised. Business logic starts here."
            ),
        },
        {
            "term": "Gold Layer",
            "definition": (
                "Business-ready layer — aggregated metrics, KPIs, and wide tables optimised for "
                "BI tools and analytical queries. Each model answers a specific business question."
            ),
        },
        {
            "term": "dbt (data build tool)",
            "definition": (
                "SQL-first transformation framework. Engineers write SELECT statements; dbt "
                "handles materialisation (table/view/incremental), dependency resolution, "
                "testing, and documentation."
            ),
        },
        {
            "term": "dbt Incremental Model",
            "definition": (
                "A dbt materialisation strategy that processes only new/changed rows on "
                "subsequent runs, dramatically reducing warehouse compute costs."
            ),
        },
        {
            "term": "DuckDB",
            "definition": (
                "An in-process analytical database (OLAP). No server required — runs inside "
                "the Python process or as a single file. Ideal for local development and testing "
                "of warehouse patterns before moving to Snowflake/BigQuery/Databricks."
            ),
        },
        {
            "term": "Data Contract",
            "definition": (
                "A formal agreement between data producers and consumers defining schema, "
                "quality SLAs, and semantics. dbt tests act as lightweight data contracts."
            ),
        },
        {
            "term": "dbt Test",
            "definition": (
                "Assertions on model data. Generic tests (not_null, unique, accepted_values, "
                "relationships) are declared in schema.yml. Singular tests are custom SQL files "
                "that must return zero rows to pass."
            ),
        },
        {
            "term": "Data Lineage",
            "definition": (
                "The provenance trail of data from source to consumption. dbt automatically "
                "generates a DAG (Directed Acyclic Graph) showing model dependencies."
            ),
        },
        {
            "term": "CLV (Customer Lifetime Value)",
            "definition": (
                "Total revenue attributed to a customer across all their delivered orders. "
                "A Gold-layer metric computed from Silver customers × Silver orders."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    from .settings import API_HOST, API_PORT

    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "src.api:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info",
    )
