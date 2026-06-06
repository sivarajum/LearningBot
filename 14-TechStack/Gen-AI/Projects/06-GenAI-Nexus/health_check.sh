#!/bin/bash
# ============================================================
# GenAI Nexus — Local Health Check
# Verifies all prerequisites for local end-to-end execution
# Usage: ./health_check.sh
# ============================================================

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0
warn_count=0

check_pass() { echo -e "  ${GREEN}✅ $1${NC}"; ((pass_count++)); }
check_fail() { echo -e "  ${RED}❌ $1${NC}"; ((fail_count++)); }
check_warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; ((warn_count++)); }

echo "================================================================="
echo "  GenAI Nexus — Local Health Check"
echo "================================================================="
echo ""

# ── 1. Python ──────────────────────────────────────────────
echo "📦 Python Environment"
if command -v python3 &>/dev/null; then
    py_version=$(python3 --version 2>&1)
    check_pass "Python: $py_version"
else
    check_fail "Python 3 not found"
fi

# ── 2. Ollama ──────────────────────────────────────────────
echo ""
echo "🦙 Ollama Server"
if command -v ollama &>/dev/null; then
    check_pass "Ollama installed: $(ollama --version 2>&1 | head -1)"
else
    check_fail "Ollama not installed (brew install ollama)"
fi

if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    check_pass "Ollama server running at localhost:11434"
else
    check_fail "Ollama server not running (ollama serve)"
fi

# ── 3. Ollama Models ──────────────────────────────────────
echo ""
echo "🧠 Ollama Models"
for model in "llama3.1:8b" "codellama:7b" "llama3.2:3b" "nomic-embed-text"; do
    if ollama list 2>/dev/null | grep -q "$model"; then
        check_pass "$model"
    else
        check_warn "$model not pulled (ollama pull $model)"
    fi
done

# ── 4. Python Packages ────────────────────────────────────
echo ""
echo "📚 Python Packages"
packages=(
    "openai:openai"
    "pydantic_settings:pydantic-settings"
    "chromadb:chromadb"
    "langchain:langchain"
    "langchain_ollama:langchain-ollama"
    "torch:torch"
    "transformers:transformers"
    "crewai:crewai"
    "streamlit:streamlit"
    "sentence_transformers:sentence-transformers"
    "keras:keras"
    "spacy:spacy"
)

for pkg_pair in "${packages[@]}"; do
    import_name="${pkg_pair%%:*}"
    display_name="${pkg_pair##*:}"
    if python3 -c "import $import_name" 2>/dev/null; then
        check_pass "$display_name"
    else
        check_warn "$display_name not installed (pip install $display_name)"
    fi
done

# ── 5. Disk Space ─────────────────────────────────────────
echo ""
echo "💾 Disk Usage"
if [ -d "$HOME/.ollama/models" ]; then
    ollama_size=$(du -sh "$HOME/.ollama/models" 2>/dev/null | cut -f1)
    echo "  Ollama models: $ollama_size"
else
    echo "  Ollama models: none found"
fi

if [ -d "$HOME/.cache/huggingface" ]; then
    hf_size=$(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1)
    echo "  HuggingFace cache: $hf_size"
else
    echo "  HuggingFace cache: none (will download on first use)"
fi

# ── 6. GPU Detection ──────────────────────────────────────
echo ""
echo "🎮 GPU Status"
if python3 -c "import torch; assert torch.backends.mps.is_available()" 2>/dev/null; then
    check_pass "Apple Metal (MPS) GPU available"
elif python3 -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
    gpu_name=$(python3 -c "import torch; print(torch.cuda.get_device_name(0))" 2>/dev/null)
    check_pass "NVIDIA CUDA GPU: $gpu_name"
else
    check_warn "No GPU detected — will use CPU (slower but works)"
fi

# ── 7. .env File ──────────────────────────────────────────
echo ""
echo "⚙️  Configuration"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    check_pass ".env file exists"
    if grep -q "USE_LOCAL_LLM=true" "$SCRIPT_DIR/.env" 2>/dev/null; then
        check_pass "USE_LOCAL_LLM=true is set"
    else
        check_warn "USE_LOCAL_LLM not set to true in .env"
    fi
else
    check_warn ".env not found — copy from .env.example"
fi

# ── Summary ───────────────────────────────────────────────
echo ""
echo "================================================================="
echo -e "  Results: ${GREEN}$pass_count passed${NC} | ${RED}$fail_count failed${NC} | ${YELLOW}$warn_count warnings${NC}"
echo "================================================================="

if [ $fail_count -gt 0 ]; then
    echo ""
    echo "Fix the failed checks above before running the pipeline."
    exit 1
else
    echo ""
    echo "✅ Ready to run: python main.py --idea 'your idea' --mode quick --local"
    exit 0
fi
