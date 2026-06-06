"""Tests for the FastAPI endpoints."""

import pytest

from src.api import DemoRequest, VALID_DEMO_PATTERNS


# ---------- Health ----------

class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_response_body(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-agents-learning-platform"


# ---------- GET /frameworks ----------

class TestListFrameworks:
    def test_returns_200(self, client):
        resp = client.get("/frameworks")
        assert resp.status_code == 200

    def test_returns_all_frameworks(self, client):
        data = client.get("/frameworks").json()
        assert data["total"] == 8
        assert len(data["frameworks"]) == 8

    def test_filter_by_category_orchestration(self, client):
        data = client.get("/frameworks?category=orchestration").json()
        assert data["total"] == 2
        for fw in data["frameworks"].values():
            assert fw["category"] == "orchestration"

    def test_filter_by_category_multi_agent(self, client):
        data = client.get("/frameworks?category=multi-agent").json()
        assert data["total"] == 2
        for fw in data["frameworks"].values():
            assert fw["category"] == "multi-agent"

    def test_filter_by_category_platform(self, client):
        data = client.get("/frameworks?category=platform").json()
        assert data["total"] == 2

    def test_filter_by_nonexistent_category(self, client):
        data = client.get("/frameworks?category=nonexistent").json()
        assert data["total"] == 0
        assert data["frameworks"] == {}

    def test_no_filter_returns_all(self, client):
        data = client.get("/frameworks").json()
        expected_keys = {
            "langchain", "langgraph", "autogen", "crewai",
            "openai_assistants", "claude_agent_sdk", "llamaindex", "dspy",
        }
        assert set(data["frameworks"].keys()) == expected_keys


# ---------- GET /frameworks/{name} ----------

class TestGetFrameworkDetail:
    def test_langchain_returns_200(self, client):
        resp = client.get("/frameworks/langchain")
        assert resp.status_code == 200

    def test_langchain_has_correct_name(self, client):
        data = client.get("/frameworks/langchain").json()
        assert data["name"] == "LangChain"
        assert data["category"] == "orchestration"

    def test_dspy_returns_200(self, client):
        resp = client.get("/frameworks/dspy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "DSPy (Stanford)"

    def test_nonexistent_returns_404(self, client):
        resp = client.get("/frameworks/nonexistent")
        assert resp.status_code == 404

    def test_404_has_detail_message(self, client):
        data = client.get("/frameworks/nonexistent").json()
        assert "detail" in data
        assert "nonexistent" in data["detail"]


# ---------- GET /patterns ----------

class TestListPatterns:
    def test_returns_200(self, client):
        resp = client.get("/patterns")
        assert resp.status_code == 200

    def test_returns_six_patterns(self, client):
        data = client.get("/patterns").json()
        assert data["total"] == 6
        assert len(data["patterns"]) == 6

    def test_patterns_have_expected_keys(self, client):
        data = client.get("/patterns").json()
        expected = {"react", "plan_and_execute", "reflection", "multi_agent_debate", "tool_use", "rag"}
        assert set(data["patterns"].keys()) == expected


# ---------- GET /patterns/{name} ----------

class TestGetPatternDetail:
    def test_react_returns_200(self, client):
        resp = client.get("/patterns/react")
        assert resp.status_code == 200

    def test_react_has_correct_name(self, client):
        data = client.get("/patterns/react").json()
        assert data["name"] == "ReAct (Reason + Act)"

    def test_rag_returns_200(self, client):
        resp = client.get("/patterns/rag")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Retrieval-Augmented Generation"

    def test_nonexistent_returns_404(self, client):
        resp = client.get("/patterns/nonexistent")
        assert resp.status_code == 404

    def test_404_has_detail_message(self, client):
        data = client.get("/patterns/nonexistent").json()
        assert "detail" in data
        assert "nonexistent" in data["detail"]


# ---------- GET /comparisons ----------

class TestGetComparisons:
    def test_returns_200(self, client):
        resp = client.get("/comparisons")
        assert resp.status_code == 200

    def test_returns_comparisons_list(self, client):
        data = client.get("/comparisons").json()
        assert "comparisons" in data
        assert isinstance(data["comparisons"], list)
        assert len(data["comparisons"]) == 6

    def test_each_comparison_has_dimension(self, client):
        data = client.get("/comparisons").json()
        for comp in data["comparisons"]:
            assert "dimension" in comp


# ---------- GET /demos ----------

class TestListDemos:
    def test_returns_200(self, client):
        resp = client.get("/demos")
        assert resp.status_code == 200

    def test_returns_four_demos(self, client):
        data = client.get("/demos").json()
        assert data["total"] == 4

    def test_demos_have_expected_keys(self, client):
        data = client.get("/demos").json()
        expected = {"react", "plan_and_execute", "reflection", "multi_agent_debate"}
        assert set(data["demos"].keys()) == expected

    def test_demo_values_are_names(self, client):
        data = client.get("/demos").json()
        assert data["demos"]["react"] == "ReAct (Reason + Act)"
        assert data["demos"]["reflection"] == "Reflection / Self-Critique"


# ---------- POST /demos/run ----------

class TestRunDemoEndpoint:
    def test_valid_pattern_returns_200(self, client):
        resp = client.post("/demos/run", json={"pattern": "react", "task": "Test task"})
        assert resp.status_code == 200

    def test_valid_pattern_response_structure(self, client):
        data = client.post("/demos/run", json={"pattern": "react", "task": "Test task"}).json()
        assert data["pattern"] == "react"
        assert data["pattern_name"] == "ReAct (Reason + Act)"
        assert data["task"] == "Test task"
        assert "result" in data
        assert "elapsed_seconds" in data

    def test_plan_and_execute_returns_200(self, client):
        resp = client.post("/demos/run", json={"pattern": "plan_and_execute", "task": "Test"})
        assert resp.status_code == 200

    def test_reflection_returns_200(self, client):
        resp = client.post("/demos/run", json={"pattern": "reflection", "task": "Test"})
        assert resp.status_code == 200

    def test_multi_agent_debate_returns_200(self, client):
        resp = client.post("/demos/run", json={"pattern": "multi_agent_debate", "task": "Test"})
        assert resp.status_code == 200

    def test_invalid_pattern_returns_400(self, client):
        resp = client.post("/demos/run", json={"pattern": "nonexistent", "task": "Test"})
        assert resp.status_code == 400

    def test_invalid_pattern_error_message(self, client):
        data = client.post("/demos/run", json={"pattern": "nonexistent", "task": "Test"}).json()
        assert "detail" in data
        assert "nonexistent" in data["detail"]

    def test_default_task(self, client):
        data = client.post("/demos/run", json={"pattern": "react"}).json()
        assert data["task"] == "Building a production ML pipeline"

    def test_missing_pattern_returns_422(self, client):
        resp = client.post("/demos/run", json={"task": "Test"})
        assert resp.status_code == 422

    def test_empty_task_returns_422(self, client):
        resp = client.post("/demos/run", json={"pattern": "react", "task": ""})
        assert resp.status_code == 422

    def test_task_too_long_returns_422(self, client):
        resp = client.post("/demos/run", json={"pattern": "react", "task": "x" * 1001})
        assert resp.status_code == 422

    def test_task_at_max_length_returns_200(self, client):
        resp = client.post("/demos/run", json={"pattern": "react", "task": "x" * 1000})
        assert resp.status_code == 200


# ---------- DemoRequest model ----------

class TestDemoRequestModel:
    def test_valid_request(self):
        req = DemoRequest(pattern="react", task="Test task")
        assert req.pattern == "react"
        assert req.task == "Test task"

    def test_default_task(self):
        req = DemoRequest(pattern="react")
        assert req.task == "Building a production ML pipeline"

    def test_task_min_length_enforced(self):
        with pytest.raises(Exception):
            DemoRequest(pattern="react", task="")

    def test_task_max_length_enforced(self):
        with pytest.raises(Exception):
            DemoRequest(pattern="react", task="x" * 1001)

    def test_task_at_max_length(self):
        req = DemoRequest(pattern="react", task="x" * 1000)
        assert len(req.task) == 1000


# ---------- CORS origins ----------

class TestCORSOrigins:
    def test_valid_demo_patterns_frozenset(self):
        assert isinstance(VALID_DEMO_PATTERNS, frozenset)
        assert len(VALID_DEMO_PATTERNS) == 4

    def test_valid_demo_patterns_match_registry(self):
        from src.agents.demos import DEMO_REGISTRY
        assert VALID_DEMO_PATTERNS == frozenset(DEMO_REGISTRY.keys())
