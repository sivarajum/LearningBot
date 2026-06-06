"""Tests for the knowledge base module."""

from src.knowledge_base import (
    get_all_frameworks,
    get_framework,
    get_all_patterns,
    get_pattern,
    get_comparisons,
    FRAMEWORKS,
    AGENT_PATTERNS,
)

REQUIRED_FRAMEWORK_KEYS = {
    "name", "category", "description", "key_features",
    "best_for", "complexity", "language", "github_stars", "license",
}


# ---------- Frameworks ----------

class TestGetAllFrameworks:
    def test_returns_dict(self):
        result = get_all_frameworks()
        assert isinstance(result, dict)

    def test_returns_eight_frameworks(self):
        result = get_all_frameworks()
        assert len(result) == 8

    def test_expected_framework_keys(self):
        result = get_all_frameworks()
        expected_keys = {
            "langchain", "langgraph", "autogen", "crewai",
            "openai_assistants", "claude_agent_sdk", "llamaindex", "dspy",
        }
        assert set(result.keys()) == expected_keys


class TestFrameworkSchema:
    """Every framework must have the required keys."""

    def test_each_framework_has_required_keys(self):
        for name, fw in get_all_frameworks().items():
            missing = REQUIRED_FRAMEWORK_KEYS - set(fw.keys())
            assert not missing, f"Framework '{name}' is missing keys: {missing}"

    def test_key_features_is_nonempty_list(self):
        for name, fw in get_all_frameworks().items():
            assert isinstance(fw["key_features"], list), f"{name}: key_features should be a list"
            assert len(fw["key_features"]) > 0, f"{name}: key_features should not be empty"

    def test_category_is_string(self):
        for name, fw in get_all_frameworks().items():
            assert isinstance(fw["category"], str)


class TestGetFramework:
    def test_langchain_returns_correct_data(self):
        fw = get_framework("langchain")
        assert fw is not None
        assert fw["name"] == "LangChain"
        assert fw["category"] == "orchestration"

    def test_langgraph_returns_correct_data(self):
        fw = get_framework("langgraph")
        assert fw is not None
        assert fw["name"] == "LangGraph"

    def test_autogen_returns_correct_data(self):
        fw = get_framework("autogen")
        assert fw is not None
        assert fw["name"] == "AutoGen (Microsoft)"
        assert fw["category"] == "multi-agent"

    def test_nonexistent_returns_none(self):
        assert get_framework("nonexistent") is None

    def test_empty_string_returns_none(self):
        assert get_framework("") is None

    def test_returns_same_reference_as_dict(self):
        fw = get_framework("langchain")
        assert fw is FRAMEWORKS["langchain"]


# ---------- Patterns ----------

class TestGetAllPatterns:
    def test_returns_dict(self):
        result = get_all_patterns()
        assert isinstance(result, dict)

    def test_returns_six_patterns(self):
        result = get_all_patterns()
        assert len(result) == 6

    def test_expected_pattern_keys(self):
        result = get_all_patterns()
        expected = {"react", "plan_and_execute", "reflection", "multi_agent_debate", "tool_use", "rag"}
        assert set(result.keys()) == expected


class TestPatternSchema:
    REQUIRED_PATTERN_KEYS = {"name", "description", "flow", "strengths", "weaknesses", "example_use"}

    def test_each_pattern_has_required_keys(self):
        for name, pat in get_all_patterns().items():
            missing = self.REQUIRED_PATTERN_KEYS - set(pat.keys())
            assert not missing, f"Pattern '{name}' is missing keys: {missing}"

    def test_strengths_and_weaknesses_are_lists(self):
        for name, pat in get_all_patterns().items():
            assert isinstance(pat["strengths"], list), f"{name}: strengths should be list"
            assert isinstance(pat["weaknesses"], list), f"{name}: weaknesses should be list"


class TestGetPattern:
    def test_valid_pattern_react(self):
        pat = get_pattern("react")
        assert pat is not None
        assert pat["name"] == "ReAct (Reason + Act)"

    def test_valid_pattern_rag(self):
        pat = get_pattern("rag")
        assert pat is not None
        assert pat["name"] == "Retrieval-Augmented Generation"

    def test_invalid_pattern_returns_none(self):
        assert get_pattern("nonexistent") is None

    def test_empty_string_returns_none(self):
        assert get_pattern("") is None


# ---------- Comparisons ----------

class TestGetComparisons:
    def test_returns_list(self):
        result = get_comparisons()
        assert isinstance(result, list)

    def test_returns_six_comparisons(self):
        result = get_comparisons()
        assert len(result) == 6

    def test_each_comparison_has_dimension(self):
        for comp in get_comparisons():
            assert "dimension" in comp

    def test_each_comparison_has_framework_scores(self):
        expected_frameworks = {"langchain", "langgraph", "crewai", "autogen", "openai_assistants", "llamaindex"}
        for comp in get_comparisons():
            present = set(comp.keys()) - {"dimension"}
            assert expected_frameworks == present, f"Comparison '{comp['dimension']}' missing frameworks"

    def test_scores_are_valid_range(self):
        for comp in get_comparisons():
            for key, value in comp.items():
                if key != "dimension":
                    assert isinstance(value, int), f"{comp['dimension']}.{key} should be int"
                    assert 1 <= value <= 5, f"{comp['dimension']}.{key}={value} out of range 1-5"

    def test_known_dimensions(self):
        dimensions = [c["dimension"] for c in get_comparisons()]
        assert "Ease of Setup" in dimensions
        assert "Multi-Agent Support" in dimensions
        assert "Production Readiness" in dimensions
