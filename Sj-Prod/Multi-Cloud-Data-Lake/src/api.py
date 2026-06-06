"""FastAPI server exposing the Multi-Cloud Data Lake."""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.cloud_simulator import generate_cloud_data, save_cloud_data, DATA_DIR
from src.lake_builder import build_lake, load_lake_table, LAKE_DIR
from src.settings import ALLOWED_CLOUDS, ALLOWED_LAKE_TABLES, CORS_ORIGINS

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Generate cloud data and build lake on startup if not present."""
    if not (LAKE_DIR / "customers.parquet").exists():
        logger.info("No lake found. Generating cloud data and building lake...")
        data = generate_cloud_data()
        save_cloud_data(data)
        build_lake()
    yield


app = FastAPI(
    title="Multi-Cloud Data Lake API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "data-lake"}


@app.post("/generate")
def generate_data() -> dict[str, Any]:
    """Regenerate all cloud data and rebuild the lake."""
    start = time.time()
    data = generate_cloud_data()
    saved = save_cloud_data(data)
    lake_paths = build_lake()
    elapsed = round(time.time() - start, 2)

    return {
        "cloud_files": saved,
        "lake_tables": lake_paths,
        "elapsed_seconds": elapsed,
    }


@app.get("/clouds")
def list_clouds() -> dict[str, dict[str, list[str]]]:
    """List data available per cloud."""
    clouds: dict[str, list[str]] = {}
    for cloud in ["aws", "azure", "gcp"]:
        cloud_dir = DATA_DIR / cloud
        if cloud_dir.exists():
            files = [f.name for f in cloud_dir.glob("*.parquet")]
            clouds[cloud] = files
    return {"clouds": clouds}


@app.get("/lake/tables")
def lake_tables() -> dict[str, list[str]]:
    """List tables in the data lake."""
    if not LAKE_DIR.exists():
        return {"tables": []}
    tables = [f.stem for f in LAKE_DIR.glob("*.parquet")]
    return {"tables": tables}


@app.get("/lake/{table_name}")
def query_lake(
    table_name: str,
    limit: int = Query(default=100, ge=1, le=10000),
    cloud: str | None = Query(default=None),
) -> dict[str, Any]:
    """Query a lake table. Optionally filter by source cloud."""
    # Validate table_name against allowed values to prevent path traversal
    if table_name not in ALLOWED_LAKE_TABLES:
        raise HTTPException(
            status_code=404,
            detail=f"Table '{table_name}' not found. Allowed tables: {sorted(ALLOWED_LAKE_TABLES)}",
        )

    # Validate cloud parameter against allowed values
    if cloud is not None and cloud not in ALLOWED_CLOUDS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid cloud '{cloud}'. Allowed values: {sorted(ALLOWED_CLOUDS)}",
        )

    try:
        df = load_lake_table(table_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    if cloud and "source_cloud" in df.columns:
        df = df[df["source_cloud"] == cloud]

    # Convert timestamps to strings for JSON serialization
    for col in df.select_dtypes(include=["datetime64[ns, UTC]", "datetime64[ns]"]).columns:
        df[col] = df[col].astype(str)

    records = df.head(limit).to_dict(orient="records")
    return {"table": table_name, "total_rows": len(df), "returned": len(records), "data": records}


@app.get("/analytics/summary")
def analytics_summary() -> dict[str, Any]:
    """Return cross-cloud analytics summary."""
    try:
        customers = load_lake_table("customers")
        transactions = load_lake_table("transactions")
        metrics = load_lake_table("customer_metrics")
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Lake not built yet. POST /generate first.")

    # Convert timestamps for aggregation
    customers["signup_date"] = customers["signup_date"].astype(str)
    transactions["transaction_date"] = transactions["transaction_date"].astype(str)

    summary: dict[str, Any] = {
        "total_customers": len(customers),
        "total_transactions": len(transactions),
        "customers_by_cloud": customers["source_cloud"].value_counts().to_dict(),
        "transactions_by_cloud": transactions["source_cloud"].value_counts().to_dict(),
        "revenue_by_cloud": transactions.groupby("source_cloud")["amount"].sum().round(2).to_dict(),
        "revenue_by_category": transactions.groupby("category")["amount"].sum().round(2).to_dict(),
        "customers_by_plan": customers["plan"].value_counts().to_dict(),
        "active_rate_by_cloud": customers.groupby("source_cloud")["is_active"].mean().round(4).to_dict(),
        "avg_spend_by_cloud": metrics.groupby("source_cloud")["total_spent"].mean().round(2).to_dict(),
    }
    return summary
