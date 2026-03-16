"""FastAPI server exposing the agent orchestration pipeline."""

import time
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.orchestrator import run_pipeline

app = FastAPI(title="Agent Orchestration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    topic: str


class RunResponse(BaseModel):
    topic: str
    research: str
    draft: str
    review_feedback: str
    iteration: int
    status: str
    elapsed_seconds: float


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "agent-orchestration"}


@app.post("/run", response_model=RunResponse)
def run(request: RunRequest):
    """Run the full agent pipeline for a given topic.

    Accepts a topic string, runs Researcher -> Writer -> Reviewer loop,
    and returns all intermediate outputs.
    """
    start = time.time()
    try:
        result = run_pipeline(request.topic)
        elapsed = round(time.time() - start, 2)
        return RunResponse(
            topic=result.get("topic", request.topic),
            research=result.get("research", ""),
            draft=result.get("draft", ""),
            review_feedback=result.get("review_feedback", ""),
            iteration=result.get("iteration", 0),
            status=result.get("status", "complete"),
            elapsed_seconds=elapsed,
        )
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        return RunResponse(
            topic=request.topic,
            research="",
            draft="",
            review_feedback=f"Pipeline error: {e}\n{traceback.format_exc()}",
            iteration=0,
            status="error",
            elapsed_seconds=elapsed,
        )
