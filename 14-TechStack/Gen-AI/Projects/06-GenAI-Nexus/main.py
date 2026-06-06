"""
GenAI Nexus — CLI Entry Point
==============================
Run the full AI Startup Advisor pipeline from the command line.

Usage:
    python main.py --idea "AI legal document analyzer" --mode demo
    python main.py --idea "AI medical diagnosis" --mode quick --output plan.md
    python main.py --idea "..." --mode full --output my_plan.md

Modes:
    demo   — No API keys needed. Fast. Uses mock responses. (default)
    quick  — Needs API keys. Skips training modules. ~2-5 min.
    full   — All 26 tools including training. GPU recommended. ~30+ min.
"""

import argparse
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="GenAI Nexus — AI Startup Advisor (26 Gen-AI Tools)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --idea "AI legal document analyzer" --mode demo
  python main.py --idea "AI medical imaging" --mode quick --output plan.md
  python main.py --demo-individual openai  # Run individual module demo

Individual module demos:
  openai, claude, gemini, langchain, langgraph, rag, advrag, llama,
  embeddings, chroma, agents, crew, autogen, guardrails, prompts,
  fewshot, nlp, hf, keras, transfer, peft, rlhf, quant, vllm, dist, aws
        """,
    )

    parser.add_argument(
        "--idea",
        type=str,
        default="AI-powered legal document analyzer",
        help="Startup idea to analyze (default: AI legal doc analyzer)",
    )
    parser.add_argument(
        "--mode",
        choices=["demo", "quick", "full"],
        default="demo",
        help="Analysis mode: demo (no API keys) | quick | full (default: demo)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./data/startup_plan.md",
        help="Output file path for the startup plan (default: ./data/startup_plan.md)",
    )
    parser.add_argument(
        "--demo-individual",
        type=str,
        metavar="MODULE",
        help="Run demo for a single module (e.g., --demo-individual openai)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Force local LLM mode (Ollama). No cloud API keys needed.",
    )

    return parser.parse_args()


INDIVIDUAL_DEMOS = {
    "openai": "src.llm.openai_client",
    "claude": "src.llm.claude_client",
    "gemini": "src.llm.gemini_client",
    "ollama": "src.llm.ollama_client",
    "langchain": "src.chains.analysis_chains",
    "langgraph": "src.graph.startup_workflow",
    "rag": "src.rag.basic_rag",
    "advrag": "src.rag.advanced_rag",
    "llama": "src.rag.llama_indexer",
    "embeddings": "src.embeddings.embedding_service",
    "chroma": "src.vectorstore.chroma_store",
    "agents": "src.agents.agentic_core",
    "crew": "src.agents.crew_team",
    "autogen": "src.agents.autogen_debate",
    "guardrails": "src.safety.output_validator",
    "prompts": "src.prompts.prompt_templates",
    "fewshot": "src.prompts.few_shot_examples",
    "nlp": "src.nlp.text_processor",
    "hf": "src.huggingface.hf_models",
    "keras": "src.models.sentiment_model",
    "transfer": "src.models.transfer_adapter",
    "peft": "src.training.peft_trainer",
    "rlhf": "src.training.rlhf_feedback",
    "quant": "src.optimization.quantizer",
    "vllm": "src.optimization.inference_server",
    "dist": "src.training.distributed_trainer",
    "aws": "src.cloud.aws_client",
}


def run_individual_demo(module_name: str):
    """Run the demo() function of a specific module."""
    if module_name not in INDIVIDUAL_DEMOS:
        print(f"Unknown module: {module_name}")
        print(f"Available: {', '.join(sorted(INDIVIDUAL_DEMOS.keys()))}")
        sys.exit(1)

    module_path = INDIVIDUAL_DEMOS[module_name]
    print(f"\nRunning demo for: {module_path}\n")

    import importlib

    module = importlib.import_module(module_path)
    module.demo()


def main():
    args = parse_args()

    # Ensure data directory exists
    Path("./data").mkdir(exist_ok=True)

    if args.demo_individual:
        run_individual_demo(args.demo_individual)
        return

    # Apply --local flag: override environment for local LLM
    if args.local:
        import os

        os.environ["USE_LOCAL_LLM"] = "true"
        os.environ["DEMO_MODE"] = "false"
        os.environ["EMBEDDING_MODEL"] = "huggingface"
        # Reload settings with new env vars
        from config.settings import Settings

        import config.settings

        config.settings.settings = Settings()

    # Full pipeline
    print(f"""
╔══════════════════════════════════════════════════════════╗
║          GenAI Nexus — AI Startup Advisor                ║
║          26 Gen-AI Tools • One Complete Analysis         ║
╚══════════════════════════════════════════════════════════╝
""")

    from pipeline.startup_advisor import StartupAdvisor

    advisor = StartupAdvisor(args.idea)
    plan = advisor.run(mode=args.mode)

    # Save output
    output_path = plan.save(args.output)
    print(f"\n📄 Startup plan saved to: {output_path}")
    print(f"\nTools used ({len(plan.tools_used)}):")
    for tool in plan.tools_used:
        print(f"  ✓ {tool}")


if __name__ == "__main__":
    main()
