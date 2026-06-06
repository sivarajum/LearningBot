"""
GenAI Nexus — Streamlit Web App
================================
Interactive UI for the AI Startup Advisor.
Each tab demonstrates a different Gen-AI tool category.

Run: streamlit run app.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit not installed. Run: pip install streamlit")
    sys.exit(1)

st.set_page_config(
    page_title="GenAI Nexus — AI Startup Advisor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.title("GenAI Nexus")
    st.caption("26 Gen-AI Tools • One Platform")

    st.divider()

    startup_idea = st.text_area(
        "Your Startup Idea",
        value="AI-powered legal document analyzer for law firms",
        height=100,
        help="Describe your startup idea in 1-3 sentences",
    )

    mode = st.selectbox(
        "Analysis Mode",
        ["demo", "quick", "full"],
        help="demo: no API keys needed | quick: needs keys | full: all tools",
    )

    run_btn = st.button("Analyze Startup", type="primary", use_container_width=True)

    st.divider()
    st.caption("**26 Gen-AI Tools:**")
    tools = [
        "OpenAI GPT", "Claude API", "Gemini API",
        "LangChain", "LangGraph", "RAG", "Advanced RAG",
        "LlamaIndex", "Embeddings", "ChromaDB",
        "AgenticAI", "CrewAI", "AutoGen", "Guardrails",
        "Prompt Engineering", "Few-Shot", "NLP",
        "HuggingFace", "Keras", "Transfer Learning",
        "PEFT/LoRA", "RLHF", "Model Quantization",
        "vLLM", "Distributed Training", "AWS AI/ML",
    ]
    for t in tools:
        st.caption(f"• {t}")


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

st.title("GenAI Nexus — AI Startup Advisor")
st.caption("A single Gen-AI platform demonstrating all 26 tool categories")

if run_btn:
    with st.spinner(f"Analyzing: {startup_idea}"):
        try:
            from pipeline.startup_advisor import StartupAdvisor
            advisor = StartupAdvisor(startup_idea)
            plan = advisor.run(mode=mode)
            st.session_state["plan"] = plan
            st.success(f"Analysis complete in {plan.elapsed_seconds:.1f}s")
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.session_state["plan"] = None

# Default plan for display
plan = st.session_state.get("plan")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tabs = st.tabs([
    "Overview", "Market Research", "Competitive",
    "Technical", "Team Plan", "Debate",
    "Pitch Content", "Code Skeleton",
    "Sentiment", "Module Demos",
])

with tabs[0]:  # Overview
    st.header("Analysis Overview")
    if plan:
        col1, col2, col3 = st.columns(3)
        col1.metric("Tools Used", len(plan.tools_used))
        col2.metric("Generation Time", f"{plan.elapsed_seconds:.1f}s")
        col3.metric("Validation", plan.validation_status)

        st.subheader("Tool Coverage")
        cols = st.columns(4)
        for i, tool in enumerate(plan.tools_used):
            cols[i % 4].success(f"✓ {tool}")
    else:
        st.info("Enter a startup idea in the sidebar and click 'Analyze Startup'")
        st.markdown("""
### How it works:
1. **NLP** preprocesses your startup idea
2. **Advanced RAG** retrieves market knowledge
3. **LangChain** chains: Market → Competitive → Technical analysis
4. **CrewAI** (CEO + CTO + CMO + CFO) each contribute their plan
5. **AutoGen** stress-tests via optimist/skeptic debate
6. **Guardrails** validates all outputs
7. **LangGraph** orchestrates the entire workflow
8. **HuggingFace** analyzes market sentiment
9. **Multiple LLMs** (OpenAI/Claude/Gemini) handle different tasks
        """)

with tabs[1]:  # Market Research
    st.header("Market Research")
    st.caption("Tools: RAG + Advanced RAG + LlamaIndex + OpenAI")
    if plan and plan.market_research:
        st.markdown(plan.market_research)
    else:
        st.info("Run analysis to see market research")
        with st.expander("Preview (Demo Data)"):
            from src.vectorstore.chroma_store import SAMPLE_KNOWLEDGE
            for doc in SAMPLE_KNOWLEDGE[:2]:
                st.markdown(f"**{doc.metadata.get('type', 'data')}:** {doc.content}")

with tabs[2]:  # Competitive
    st.header("Competitive Analysis")
    st.caption("Tools: Claude (long-context) + ChromaDB + LangChain")
    if plan and plan.competitive_analysis:
        st.markdown(plan.competitive_analysis)
    else:
        st.info("Run analysis to see competitive landscape")

with tabs[3]:  # Technical
    st.header("Technical Architecture")
    st.caption("Tools: Claude + PromptEngineering + FewShot")
    if plan and plan.technical_plan:
        st.markdown(plan.technical_plan)
    else:
        st.info("Run analysis to see technical plan")

with tabs[4]:  # Team Plan
    st.header("Executive Team Plan")
    st.caption("Tools: CrewAI (CEO + CTO + CMO + CFO agents)")
    if plan and plan.team_plans:
        for role, content in plan.team_plans.items():
            with st.expander(f"{role.upper()} Plan"):
                st.markdown(content)
    else:
        st.info("Run analysis to see team plans")
        from src.agents.crew_team import DEMO_CEO_OUTPUT
        with st.expander("Preview — CEO Demo Output"):
            st.markdown(DEMO_CEO_OUTPUT)

with tabs[5]:  # Debate
    st.header("Startup Plan Stress Test")
    st.caption("Tools: AutoGen (Optimist vs Skeptic debate)")
    if plan and plan.debate_outcome:
        st.markdown(plan.debate_outcome)
    else:
        st.info("Run analysis to see debate results")
        from src.agents.autogen_debate import DEMO_DEBATE
        with st.expander("Preview — AutoGen Debate Demo"):
            st.markdown(DEMO_DEBATE)

with tabs[6]:  # Pitch Content
    st.header("Pitch Deck Content")
    st.caption("Tools: Gemini + PromptEngineering")
    if plan and plan.pitch_content:
        st.markdown(plan.pitch_content)
    else:
        st.info("Run analysis to generate pitch content")

with tabs[7]:  # Code Skeleton
    st.header("MVP Code Skeleton")
    st.caption("Tools: Claude + AgenticAI")
    if plan and plan.code_skeleton:
        st.code(plan.code_skeleton, language="python")
    else:
        st.info("Run analysis to generate code skeleton")

with tabs[8]:  # Sentiment
    st.header("Market Sentiment Analysis")
    st.caption("Tools: HuggingFace Transformers + Keras Custom Model")
    if plan and plan.sentiment_score:
        score = plan.sentiment_score
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", score.get("overall", "N/A"))
        col2.metric("Positive %", f"{float(score.get('positive_pct', 0)):.0%}")
        col3.metric("Interpretation", score.get("interpretation", "N/A"))
    else:
        st.info("Run analysis to see sentiment data")
        # Live demo
        st.subheader("Try Sentiment Analysis")
        test_text = st.text_input("Enter a headline:", "AI legal startup raises $50M Series B")
        if st.button("Analyze Sentiment"):
            from src.huggingface.hf_models import HuggingFaceModels
            hf = HuggingFaceModels()
            results = hf.analyze_sentiment([test_text])
            if results:
                r = results[0]
                color = "green" if r.label == "POSITIVE" else "red"
                st.markdown(f"**{r.label}** (confidence: {r.score:.1%})")

with tabs[9]:  # Module Demos
    st.header("Individual Module Demos")
    st.caption("Test each Gen-AI tool individually")

    module_map = {
        "NLP Text Processor": "nlp",
        "Embedding Service": "embeddings",
        "ChromaDB Vector Store": "chroma",
        "Basic RAG": "rag",
        "Prompt Templates": "prompts",
        "Few-Shot Examples": "fewshot",
        "HuggingFace Models": "hf",
        "Keras Sentiment": "keras",
        "Transfer Learning": "transfer",
        "PEFT Trainer": "peft",
        "RLHF Pipeline": "rlhf",
        "Model Quantizer": "quant",
        "Distributed Trainer": "dist",
    }

    selected_module = st.selectbox("Select Module", list(module_map.keys()))
    test_input = st.text_input("Test Input", startup_idea)

    if st.button("Run Module Demo"):
        module_key = module_map[selected_module]
        st.code(f"python main.py --demo-individual {module_key}", language="bash")
        st.info(f"Running {selected_module} demo with: '{test_input[:60]}'")

        # Show relevant demo output
        if module_key == "nlp":
            from src.nlp.text_processor import TextProcessor
            proc = TextProcessor()
            result = proc.process(test_input)
            st.json({
                "word_count": result.word_count,
                "keywords": result.keywords[:5],
                "entities": result.entities[:3],
            })
        elif module_key == "embeddings":
            from src.embeddings.embedding_service import EmbeddingService
            svc = EmbeddingService()
            emb = svc.embed(test_input)
            st.json({
                "model": emb.model,
                "dimensions": emb.dimensions,
                "vector_preview": emb.vector[:5],
            })
        elif module_key == "quant":
            from src.optimization.quantizer import ModelQuantizer
            q = ModelQuantizer()
            profiles = q.benchmark()
            data = [(p.name, p.size_gb, p.throughput_tokens_per_sec, p.accuracy_pct) for p in profiles]
            st.table(
                {"Model": [d[0] for d in data],
                 "Size (GB)": [d[1] for d in data],
                 "Tok/s": [d[2] for d in data],
                 "Accuracy %": [d[3] for d in data]}
            )
        else:
            st.success(f"{selected_module} demo: run `python main.py --demo-individual {module_key}` in terminal")
