"""Tests for the agent pattern demo module."""

from src.agents.demos import (
    demo_react,
    demo_plan_and_execute,
    demo_reflection,
    demo_multi_agent_debate,
    run_demo,
    DEMO_REGISTRY,
)

SAMPLE_TASK = "Building an ML pipeline"
SAMPLE_TOPIC = "Adopting AI in enterprise"


# ---------- demo_react ----------

class TestDemoReact:
    def test_returns_list(self):
        result = demo_react(SAMPLE_TASK)
        assert isinstance(result, list)

    def test_has_multiple_steps(self):
        result = demo_react(SAMPLE_TASK)
        assert len(result) == 7

    def test_step_types_sequence(self):
        result = demo_react(SAMPLE_TASK)
        types = [step["type"] for step in result]
        assert types == ["thought", "action", "observation", "thought", "action", "observation", "answer"]

    def test_thought_steps_have_content(self):
        result = demo_react(SAMPLE_TASK)
        thought_steps = [s for s in result if s["type"] == "thought"]
        for step in thought_steps:
            assert "content" in step
            assert len(step["content"]) > 0

    def test_action_steps_have_tool_and_input(self):
        result = demo_react(SAMPLE_TASK)
        action_steps = [s for s in result if s["type"] == "action"]
        for step in action_steps:
            assert "tool" in step
            assert "input" in step
            assert step["tool"] in {"web_search", "calculator", "database_lookup"}

    def test_answer_step_references_task(self):
        result = demo_react(SAMPLE_TASK)
        answer = [s for s in result if s["type"] == "answer"][0]
        assert SAMPLE_TASK in answer["content"]

    def test_uses_two_different_tools(self):
        result = demo_react(SAMPLE_TASK)
        action_steps = [s for s in result if s["type"] == "action"]
        tools_used = {s["tool"] for s in action_steps}
        assert len(tools_used) == 2, "ReAct should use two different tools"


# ---------- demo_plan_and_execute ----------

class TestDemoPlanAndExecute:
    def test_returns_dict(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        assert "task" in result
        assert "plan" in result
        assert "executions" in result
        assert "final_answer" in result

    def test_plan_is_list_of_strings(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        assert isinstance(result["plan"], list)
        assert len(result["plan"]) == 4
        for step in result["plan"]:
            assert isinstance(step, str)

    def test_executions_match_plan(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        assert len(result["executions"]) == len(result["plan"])

    def test_execution_step_has_required_keys(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        for ex in result["executions"]:
            assert "step" in ex
            assert "plan" in ex
            assert "status" in ex
            assert "result" in ex
            assert "duration_ms" in ex

    def test_all_steps_completed(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        for ex in result["executions"]:
            assert ex["status"] == "completed"

    def test_task_echoed_back(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        assert result["task"] == SAMPLE_TASK

    def test_final_answer_is_nonempty(self):
        result = demo_plan_and_execute(SAMPLE_TASK)
        assert len(result["final_answer"]) > 0


# ---------- demo_reflection ----------

class TestDemoReflection:
    def test_returns_dict(self):
        result = demo_reflection(SAMPLE_TASK)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = demo_reflection(SAMPLE_TASK)
        assert "task" in result
        assert "iterations" in result
        assert "final_output" in result

    def test_has_two_iterations(self):
        result = demo_reflection(SAMPLE_TASK)
        assert len(result["iterations"]) == 2

    def test_each_iteration_has_draft_and_critique(self):
        result = demo_reflection(SAMPLE_TASK)
        for iteration in result["iterations"]:
            assert "draft" in iteration
            assert "critique" in iteration

    def test_critique_has_score(self):
        result = demo_reflection(SAMPLE_TASK)
        for iteration in result["iterations"]:
            assert "score" in iteration["critique"]
            assert isinstance(iteration["critique"]["score"], int)

    def test_critique_has_issues_and_strengths(self):
        result = demo_reflection(SAMPLE_TASK)
        for iteration in result["iterations"]:
            critique = iteration["critique"]
            assert "issues" in critique
            assert "strengths" in critique

    def test_final_iteration_is_approved(self):
        result = demo_reflection(SAMPLE_TASK)
        last_critique = result["iterations"][-1]["critique"]
        assert last_critique.get("approved") is True

    def test_final_output_is_nonempty(self):
        result = demo_reflection(SAMPLE_TASK)
        assert len(result["final_output"]) > 0

    def test_task_echoed_back(self):
        result = demo_reflection(SAMPLE_TASK)
        assert result["task"] == SAMPLE_TASK


# ---------- demo_multi_agent_debate ----------

class TestDemoMultiAgentDebate:
    def test_returns_dict(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        assert "topic" in result
        assert "agents" in result
        assert "synthesis" in result
        assert "recommendation" in result

    def test_has_three_agents(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        assert len(result["agents"]) == 3

    def test_agent_roles(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        expected_agents = {"optimist", "skeptic", "pragmatist"}
        assert set(result["agents"].keys()) == expected_agents

    def test_each_agent_has_role_and_argument(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        for key, agent in result["agents"].items():
            assert "role" in agent, f"Agent '{key}' missing role"
            assert "argument" in agent, f"Agent '{key}' missing argument"
            assert len(agent["argument"]) > 0

    def test_synthesis_references_topic(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        assert SAMPLE_TOPIC in result["synthesis"]

    def test_recommendation_is_nonempty(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        assert len(result["recommendation"]) > 0

    def test_topic_echoed_back(self):
        result = demo_multi_agent_debate(SAMPLE_TOPIC)
        assert result["topic"] == SAMPLE_TOPIC


# ---------- DEMO_REGISTRY ----------

class TestDemoRegistry:
    def test_has_four_entries(self):
        assert len(DEMO_REGISTRY) == 4

    def test_expected_keys(self):
        expected = {"react", "plan_and_execute", "reflection", "multi_agent_debate"}
        assert set(DEMO_REGISTRY.keys()) == expected

    def test_each_entry_has_fn_and_name(self):
        for key, entry in DEMO_REGISTRY.items():
            assert "fn" in entry, f"Registry entry '{key}' missing 'fn'"
            assert "name" in entry, f"Registry entry '{key}' missing 'name'"
            assert callable(entry["fn"]), f"Registry entry '{key}' fn is not callable"


# ---------- run_demo ----------

class TestRunDemo:
    def test_valid_pattern_react(self):
        result = run_demo("react", SAMPLE_TASK)
        assert "error" not in result
        assert result["pattern"] == "react"
        assert result["pattern_name"] == "ReAct (Reason + Act)"
        assert result["task"] == SAMPLE_TASK
        assert "result" in result
        assert "elapsed_seconds" in result

    def test_valid_pattern_plan_and_execute(self):
        result = run_demo("plan_and_execute", SAMPLE_TASK)
        assert "error" not in result
        assert result["pattern"] == "plan_and_execute"

    def test_valid_pattern_reflection(self):
        result = run_demo("reflection", SAMPLE_TASK)
        assert "error" not in result
        assert result["pattern"] == "reflection"

    def test_valid_pattern_multi_agent_debate(self):
        result = run_demo("multi_agent_debate", SAMPLE_TASK)
        assert "error" not in result
        assert result["pattern"] == "multi_agent_debate"

    def test_invalid_pattern_returns_error(self):
        result = run_demo("nonexistent_pattern", SAMPLE_TASK)
        assert "error" in result
        assert "nonexistent_pattern" in result["error"]

    def test_elapsed_seconds_is_nonnegative(self):
        result = run_demo("react", SAMPLE_TASK)
        assert result["elapsed_seconds"] >= 0

    def test_result_contains_actual_demo_output(self):
        result = run_demo("react", SAMPLE_TASK)
        assert isinstance(result["result"], list)  # react returns a list of steps

        result2 = run_demo("plan_and_execute", SAMPLE_TASK)
        assert isinstance(result2["result"], dict)  # plan_and_execute returns a dict
