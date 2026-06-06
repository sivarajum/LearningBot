"""FastAPI server for the AI Agents Learning Platform."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agents.demos import run_demo, DEMO_REGISTRY
from src.knowledge_base import (
    get_all_frameworks,
    get_all_patterns,
    get_comparisons,
    get_framework,
    get_pattern,
)
from src.settings import CORS_ORIGINS

logger = logging.getLogger(__name__)

VALID_DEMO_PATTERNS = frozenset(DEMO_REGISTRY.keys())

app = FastAPI(
    title="AI Agents Learning Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DemoRequest(BaseModel):
    pattern: str = Field(
        ...,
        description="Agent pattern to demo",
        json_schema_extra={"enum": sorted(VALID_DEMO_PATTERNS)},
    )
    task: str = Field(
        default="Building a production ML pipeline",
        min_length=1,
        max_length=1000,
        description="Task description for the agent demo",
    )


@app.get("/health")
def health() -> dict[str, str]:
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "ai-agents-learning-platform"}


@app.get("/frameworks")
def list_frameworks(category: str = Query(default=None)) -> dict[str, Any]:
    """List all AI agent frameworks. Optionally filter by category."""
    frameworks = get_all_frameworks()
    if category:
        frameworks = {k: v for k, v in frameworks.items() if v["category"] == category}
    logger.info("Listed frameworks (category=%s, count=%d)", category, len(frameworks))
    return {"frameworks": frameworks, "total": len(frameworks)}


@app.get("/frameworks/{name}")
def get_framework_detail(name: str) -> dict[str, Any]:
    """Get detailed info about a specific framework."""
    fw = get_framework(name)
    if not fw:
        logger.warning("Framework not found: %s", name)
        raise HTTPException(status_code=404, detail=f"Framework '{name}' not found")
    logger.info("Returned framework detail: %s", name)
    return fw


@app.get("/patterns")
def list_patterns() -> dict[str, Any]:
    """List all agent design patterns."""
    patterns = get_all_patterns()
    logger.info("Listed %d patterns", len(patterns))
    return {"patterns": patterns, "total": len(patterns)}


@app.get("/patterns/{name}")
def get_pattern_detail(name: str) -> dict[str, Any]:
    """Get detailed info about a specific agent pattern."""
    p = get_pattern(name)
    if not p:
        logger.warning("Pattern not found: %s", name)
        raise HTTPException(status_code=404, detail=f"Pattern '{name}' not found")
    logger.info("Returned pattern detail: %s", name)
    return p


@app.get("/comparisons")
def get_comparison_data() -> dict[str, list[dict[str, Any]]]:
    """Get framework comparison matrix data."""
    logger.info("Returned comparison data")
    return {"comparisons": get_comparisons()}


@app.get("/demos")
def list_demos() -> dict[str, Any]:
    """List available interactive demos."""
    logger.info("Listed %d demos", len(DEMO_REGISTRY))
    return {
        "demos": {k: v["name"] for k, v in DEMO_REGISTRY.items()},
        "total": len(DEMO_REGISTRY),
    }


@app.post("/demos/run")
def run_agent_demo(req: DemoRequest) -> dict[str, Any]:
    """Run an interactive agent pattern demo."""
    if req.pattern not in VALID_DEMO_PATTERNS:
        logger.warning("Invalid demo pattern requested: %s", req.pattern)
        raise HTTPException(
            status_code=400,
            detail=f"Unknown pattern: {req.pattern}. Available: {sorted(VALID_DEMO_PATTERNS)}",
        )
    logger.info("Running demo: pattern=%s, task=%s", req.pattern, req.task[:80])
    result = run_demo(req.pattern, req.task)
    if "error" in result:
        logger.error("Demo error: %s", result["error"])
        raise HTTPException(status_code=400, detail=result["error"])
    logger.info("Demo completed: pattern=%s, elapsed=%.4fs", req.pattern, result["elapsed_seconds"])
    return result
