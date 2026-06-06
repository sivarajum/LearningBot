"""Tests for the full pipeline, NLP, prompts, safety, and optimizer modules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestNLPProcessor:
    def test_clean_text(self):
        from src.nlp.text_processor import TextProcessor
        proc = TextProcessor(use_spacy=False)
        result = proc.clean("  Hello  world  <br> test  ")
        assert "  " not in result
        assert "<br>" not in result

    def test_keyword_extraction(self):
        from src.nlp.text_processor import TextProcessor
        proc = TextProcessor(use_spacy=False)
        text = "AI legal document analyzer startup idea with LLM and NLP"
        keywords = proc.extract_keywords(text, top_n=5)
        assert len(keywords) <= 5
        assert all(isinstance(k, str) for k in keywords)

    def test_entity_extraction_fallback(self):
        from src.nlp.text_processor import TextProcessor
        proc = TextProcessor(use_spacy=False)
        text = "Harvey AI raised $100M in San Francisco"
        entities = proc.extract_entities(text)
        assert isinstance(entities, list)

    def test_startup_component_extraction(self):
        from src.nlp.text_processor import TextProcessor
        proc = TextProcessor(use_spacy=False)
        text = "AI-powered legal document analyzer using NLP and LLM"
        components = proc.extract_startup_components(text)
        assert "technology" in components
        assert "ai" in components["technology"].lower() or "nlp" in components["technology"].lower()

    def test_process_pipeline(self):
        from src.nlp.text_processor import TextProcessor
        proc = TextProcessor(use_spacy=False)
        result = proc.process("Build an AI startup for legal document analysis")
        assert result.word_count > 0
        assert len(result.cleaned) > 0


class TestPromptEngineering:
    def test_get_prompt(self):
        from src.prompts.prompt_templates import get_prompt
        prompt = get_prompt("market_research")
        assert prompt.name == "market_research"
        assert prompt.system
        assert "$startup_idea" in prompt.user_template

    def test_format_prompt(self):
        from src.prompts.prompt_templates import get_prompt
        prompt = get_prompt("market_research")
        rendered = prompt.format(startup_idea="AI legal tool")
        assert "AI legal tool" in rendered["user"]
        assert rendered["system"]

    def test_invalid_prompt_raises(self):
        from src.prompts.prompt_templates import get_prompt
        try:
            get_prompt("nonexistent_prompt")
            assert False, "Should have raised KeyError"
        except KeyError:
            pass

    def test_all_prompts_renderable(self):
        from src.prompts.prompt_templates import PROMPT_REGISTRY
        for name, prompt in PROMPT_REGISTRY.items():
            rendered = prompt.format(
                startup_idea="test",
                requirements="test",
                market_size="$1B",
                differentiator="unique",
                traction="10 users",
                competitors_placeholder="CompA, CompB",
            )
            assert rendered["system"]


class TestFewShotExamples:
    def test_build_few_shot_prompt(self):
        from src.prompts.few_shot_examples import FewShotBuilder
        builder = FewShotBuilder()
        prompt = builder.build_few_shot_prompt("market_sizing", "legal tech TAM?")
        assert "Example" in prompt
        assert "legal tech TAM?" in prompt

    def test_zero_shot_cot(self):
        from src.prompts.few_shot_examples import FewShotBuilder
        builder = FewShotBuilder()
        cot = builder.build_zero_shot_cot("What is the best pricing strategy?")
        assert "step by step" in cot.lower()

    def test_self_consistency(self):
        from src.prompts.few_shot_examples import FewShotBuilder
        builder = FewShotBuilder()
        paths = builder.self_consistency_prompt("Legal tech GTM", n_paths=3)
        assert len(paths) == 3

    def test_add_examples(self):
        from src.prompts.few_shot_examples import Example, FewShotBuilder
        builder = FewShotBuilder()
        new_ex = Example(input="test input", output="test output")
        builder.add_examples("new_task", [new_ex])
        assert "new_task" in builder.list_tasks()


class TestGuardrails:
    def test_good_report_passes(self):
        from src.safety.output_validator import OutputValidator
        validator = OutputValidator()
        # Use a report long enough to pass the word-count check (>50 words)
        good = (
            "Market research shows the legal technology sector has a TAM of $45.2B growing at 18.9% CAGR through 2030. "
            "Competitor analysis: Harvey AI is a well-funded rival targeting BigLaw firms with $100M raised. "
            "Revenue model: SaaS subscription at $299/month. "
            "Team: 3 senior engineers, 1 sales lead, founder CEO with legal background. "
            "Milestone: $150K ARR in 12 months via PLG strategy targeting solo and small firms."
        )
        passed, issues = validator.validate_report(good)
        critical = [i for i in issues if not i.startswith("[WARNING]")]
        assert len(critical) == 0

    def test_bad_report_fails(self):
        from src.safety.output_validator import OutputValidator
        validator = OutputValidator()
        bad = "Growth of 1000% guaranteed! Market is $999999B. Use insider trading to gain edge."
        passed, issues = validator.validate_report(bad)
        assert not passed or len(issues) > 0

    def test_market_data_validation(self):
        from src.safety.output_validator import OutputValidator
        validator = OutputValidator()
        good = {"tam_billions": 45.2, "cagr_percent": 18.9}
        bad = {"tam_billions": 999999, "cagr_percent": 500}
        assert validator.validate_market_data(good).passed
        assert not validator.validate_market_data(bad).passed

    def test_auto_correct(self):
        from src.safety.output_validator import OutputValidator
        validator = OutputValidator()
        messy = "## Section\n- point 1\n-- point 2"
        corrected = validator.correct_common_errors(messy)
        assert "  " not in corrected


class TestEmbeddingService:
    def test_single_embed(self):
        from src.embeddings.embedding_service import EmbeddingService
        svc = EmbeddingService()
        result = svc.embed("AI legal document analyzer")
        assert result.dimensions > 0
        assert len(result.vector) == result.dimensions

    def test_batch_embed(self):
        from src.embeddings.embedding_service import EmbeddingService
        svc = EmbeddingService()
        texts = ["Legal AI", "Market research", "Technical plan"]
        results = svc.embed_batch(texts)
        assert len(results) == 3

    def test_cosine_similarity_range(self):
        from src.embeddings.embedding_service import EmbeddingService
        svc = EmbeddingService()
        e1 = svc.embed("legal document analysis")
        e2 = svc.embed("legal document analysis")  # same = 1.0
        sim = svc.cosine_similarity(e1.vector, e2.vector)
        assert 0.99 <= sim <= 1.01  # Should be ~1.0 for identical texts

    def test_semantic_search(self):
        from src.embeddings.embedding_service import EmbeddingService
        svc = EmbeddingService()
        corpus = ["AI for legal docs", "Weather forecasting", "Financial trading", "Contract review"]
        results = svc.semantic_search("legal document AI", corpus, top_k=2)
        assert len(results) == 2
        assert results[0].rank == 1


class TestFullPipeline:
    def test_advisor_demo_mode(self):
        from pipeline.startup_advisor import StartupAdvisor
        advisor = StartupAdvisor("AI legal document analyzer")
        plan = advisor.run(mode="demo")
        assert plan.startup_idea == "AI legal document analyzer"
        assert len(plan.tools_used) > 0
        assert plan.elapsed_seconds > 0

    def test_plan_save(self, tmp_path):
        from pipeline.startup_advisor import StartupAdvisor
        advisor = StartupAdvisor("Test startup")
        plan = advisor.run(mode="demo")
        output = plan.save(str(tmp_path / "test_plan.md"))
        assert output.exists()
        content = output.read_text()
        # Title is uppercased in the plan
        assert "TEST STARTUP" in content

    def test_all_required_sections(self):
        from pipeline.startup_advisor import StartupAdvisor
        advisor = StartupAdvisor("AI startup")
        plan = advisor.run(mode="demo")
        # All key attributes should be populated
        assert hasattr(plan, "market_research")
        assert hasattr(plan, "competitive_analysis")
        assert hasattr(plan, "technical_plan")
        assert hasattr(plan, "team_plans")
        assert hasattr(plan, "debate_outcome")
