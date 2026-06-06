# PEFT & Fine-Tuning Interview Questions and Answers

## Beginner Level Questions

### Q1: What is PEFT and why is it needed?

**Why this question is asked:** Tests if you understand the fundamental cost/scale problem of LLM fine-tuning.

**Answer:**
PEFT (Parameter-Efficient Fine-Tuning) is a family of techniques that adapt large pretrained models by training only a tiny fraction (<1%) of parameters. Full fine-tuning a 70B model requires 640GB VRAM (8× A100s) and costs $50K+ per run. PEFT reduces this to 1 GPU and $500 while achieving 93-97% of full fine-tuning quality.

The key insight: weight updates during fine-tuning have low intrinsic rank — you don't need d×d parameters, just d×r where r << d.

**Code Example:**
```python
from peft import get_peft_model, LoraConfig
config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])
model = get_peft_model(base_model, config)
model.print_trainable_parameters()
# trainable: 0.06% of total parameters
```

**Follow-up questions:**
- What is the mathematical basis for LoRA working?
- When would PEFT NOT be appropriate?

**Red flags:** Saying "PEFT is just LoRA" (it's a family of methods). Not knowing the memory/cost savings.

**Senior differentiator:** Discussing the Aghajanyan et al. 2020 paper showing intrinsic dimensionality of fine-tuning, and when full FT is actually needed (pre-training on new domains).

---

### Q2: Explain LoRA — how does it work mathematically?

**Why this question is asked:** Tests depth of understanding beyond "it uses fewer parameters."

**Answer:**
LoRA freezes the pretrained weight matrix W₀ ∈ ℝ^(d×d) and adds a low-rank decomposition:

```
h = W₀x + (α/r) · BAx

Where: B ∈ ℝ^(d×r), A ∈ ℝ^(r×d), r << d
```

- A is initialized with Gaussian, B with zeros → ΔW starts at zero (training starts from pretrained)
- Only A and B are trained: 2×d×r parameters vs d×d for full update
- For d=4096, r=16: 131K params vs 16.7M (128× reduction)
- At inference, merge: W = W₀ + (α/r)·BA → zero overhead

**Follow-up questions:**
- Why initialize B with zeros?
- How does lora_alpha interact with learning rate?
- What is AdaLoRA and how does it improve on LoRA?

**Red flags:** Not knowing the shapes of A and B. Confusing LoRA with adapter tuning.

**Senior differentiator:** Knowing that α/r acts as a scaling factor that lets you tune α independently of learning rate, and that DoRA (Weight-Decomposed LoRA) separates direction and magnitude for better convergence.

---

### Q3: What is QLoRA and how does it differ from LoRA?

**Answer:**
QLoRA = 4-bit Quantization + LoRA, with three innovations:

1. **NF4 (NormalFloat4)**: Custom 4-bit data type optimal for normally-distributed weights
2. **Double Quantization**: Quantizes the quantization constants (saves 0.37 bits/param additional)
3. **Paged Optimizers**: Uses CUDA unified memory to page optimizer states to CPU when GPU runs out

Result: 70B model fits in 40GB VRAM (1× A100) vs 640GB for full FT.

```python
from transformers import BitsAndBytesConfig
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)
```

**Senior differentiator:** Understanding that QLoRA computes in BF16 but stores in NF4 — the compute dtype matters for training stability. Also knowing that `prepare_model_for_kbit_training()` enables gradient checkpointing and sets input embeddings to require grad.

---

### Q4: What are target_modules and how do you choose them?

**Answer:**
target_modules specifies which weight matrices in the model get LoRA adapters. Common choices:

- **Attention only**: `["q_proj", "v_proj"]` — minimum, works okay
- **All attention**: `["q_proj", "k_proj", "v_proj", "o_proj"]` — better
- **All linear**: `target_modules="all-linear"` — best quality, most params
- **Custom**: inspect model architecture with `model.named_modules()`

Research shows: more target modules = better quality, linearly more params.

**Red flags:** Only knowing attention targets. Not knowing how to find module names.

---

### Q5: What is the difference between LoRA, Adapter Tuning, and Prefix Tuning?

**Answer:**

| Method | Where Params Go | How It Works |
|--------|----------------|-------------|
| LoRA | Inside attention (weight matrices) | Low-rank decomposition ΔW = BA |
| Adapter | Between sub-layers (inserted) | Bottleneck FFN: Linear(d→r)→ReLU→Linear(r→d) |
| Prefix | Prepended to KV in every layer | Learnable virtual token embeddings |

LoRA has zero inference overhead after merging. Adapters add small latency. Prefix tuning adds sequence length.

---

## Intermediate Level Questions

### Q6: How do you implement a full QLoRA training pipeline?

**Answer:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

# 1. Quantize base model
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    quantization_config=bnb_config, device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
tokenizer.pad_token = tokenizer.eos_token

# 2. Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# 3. Apply LoRA
lora_config = LoraConfig(
    r=16, lora_alpha=32, target_modules="all-linear",
    lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)

# 4. Train with SFTTrainer
dataset = load_dataset("HuggingFaceH4/ultrachat_200k", split="train_sft[:10000]")
trainer = SFTTrainer(
    model=model, train_dataset=dataset, tokenizer=tokenizer,
    args=SFTConfig(
        output_dir="qlora-llama", num_train_epochs=1,
        per_device_train_batch_size=4, gradient_accumulation_steps=4,
        learning_rate=2e-4, bf16=True, max_seq_length=2048,
        gradient_checkpointing=True,
    ),
)
trainer.train()
model.save_pretrained("qlora-llama-adapter")
```

---

### Q7: How do you serve multiple LoRA adapters efficiently?

**Answer:**
Modern inference engines (vLLM, SGLang) support multi-LoRA serving from a single base model:

```python
# vLLM multi-LoRA serving
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM(model="meta-llama/Llama-3.1-8B", enable_lora=True, max_loras=10)

# Different customers get different adapters
medical_req = LoRARequest("medical", 1, "adapters/medical")
legal_req = LoRARequest("legal", 2, "adapters/legal")

output = llm.generate("Diagnose: chest pain", SamplingParams(), lora_request=medical_req)
```

**Senior differentiator:** Knowing that vLLM keeps LoRA weights in GPU memory and applies them per-request with minimal overhead — the base model KV cache is shared across all adapters.

---

### Q8: When does LoRA fail and what are the alternatives?

**Answer:**
LoRA struggles when:
1. **Domain shift is massive** (English model → code → clinical notes) — need full FT or larger r
2. **Task requires precise calibration** (reward models for RLHF) — use DoRA or full FT
3. **Very small models** (<1B) — adapter overhead is proportionally larger

Alternatives:
- **DoRA**: Decomposes into direction + magnitude, better convergence
- **Full fine-tuning with DeepSpeed ZeRO-3**: When budget allows
- **Continued pre-training + LoRA**: For massive domain shift

---

## Advanced Level Questions

### Q9: Design a multi-tenant fine-tuning platform for 50 enterprise customers

**Answer:**
Architecture:
1. **Base model layer**: Single LLaMA-3.1-70B deployed with vLLM, tensor parallelism across 2× A100
2. **Adapter store**: S3/GCS bucket with versioned LoRA adapters per customer (50MB each)
3. **Training pipeline**: Kubernetes jobs with QLoRA training, auto-triggered when customer uploads new data
4. **Router**: API gateway routes requests to correct adapter based on API key
5. **Quality gate**: Automated eval on held-out set before promoting adapter to production

Cost: $2K/month base infra + $50/customer/training run vs $50K/customer for full FT.

---

### Q10: How do you combine PEFT with RLHF for alignment?

**Answer:**
```
Stage 1: QLoRA SFT (adapt base model to follow instructions)
  - LoRA on all-linear, r=64, train on instruction data
  - Output: SFT adapter (100MB)

Stage 2: Reward Model (QLoRA on same base)
  - LoRA r=32, train on preference pairs (chosen vs rejected)
  - Output: RM adapter (50MB)

Stage 3: PPO with LoRA
  - Policy: base + SFT adapter + new LoRA layer for PPO
  - Reference: base + SFT adapter (frozen)
  - KL penalty prevents divergence from reference
  - Output: Final aligned adapter
```

Total training: 3× A100-hours vs 100× for full RLHF. This is exactly how QLoRA + DPO is used at scale.

---

### Q11: System Design — Build a LoRA fine-tuning-as-a-service platform

**Answer:**
```
User → Upload training data (JSON/JSONL)
     → API validates format + triggers training job

Training Orchestrator (K8s):
  → Provisions GPU node (spot A100)
  → Downloads base model from cache
  → Runs QLoRA training (SFTTrainer)
  → Evaluates on held-out split
  → Uploads adapter to artifact store (GCS/S3)
  → Notifies user

Serving Layer (vLLM cluster):
  → Loads base model once (shared)
  → Hot-loads LoRA adapters per request
  → Auto-scales based on QPS

Monitoring:
  → Training loss curves (W&B)
  → Inference latency P50/P99
  → Adapter quality scores over time
```

---

### Q12: How do you evaluate fine-tuned model quality vs base model?
**Answer:**

```python
from lm_eval import evaluator

# 1. Automated evaluation (benchmark tasks)
results_base = evaluator.simple_evaluate(model="meta-llama/Llama-3-8B", tasks=["mmlu", "hellaswag"])
results_ft = evaluator.simple_evaluate(model="./fine-tuned-adapter", tasks=["mmlu", "hellaswag"])

# 2. Domain-specific evaluation (financial accuracy)
test_cases = [
    {"input": "Classify: RELIANCE PE at 28, EPS growing 15% YoY", "expected": "BUY"},
    {"input": "Classify: TATAMOTORS debt/equity 1.8, FCF negative", "expected": "SELL"},
]
correct = sum(1 for tc in test_cases if model.generate(tc["input"]).strip() == tc["expected"])
accuracy = correct / len(test_cases)

# 3. A/B evaluation (LLM-as-judge)
judge_prompt = """Compare these two responses to the same query:
Response A (base): {base_response}
Response B (fine-tuned): {ft_response}
Which is better for financial analysis? Output: A or B with reasoning."""
```

**Key metrics:**
| Metric | What It Measures | Target |
|--------|-----------------|--------|
| Perplexity | How surprised the model is by text | Lower = better |
| ROUGE-L | Overlap with reference answers | > 0.7 for summaries |
| Domain accuracy | Correct financial classifications | > 80% |
| Hallucination rate | Made-up financial data | < 5% |
| Latency overhead | LoRA adapter adds ~2-5% inference time | < 10ms added |

### Q13: What are the key differences between LoRA, QLoRA, DoRA, and AdaLoRA?
**Answer:**

| Method | Key Innovation | Memory | Quality | Best For |
|--------|---------------|--------|---------|----------|
| **LoRA** | Low-rank decomposition (A×B) | 10-20% base | Good | Standard fine-tuning |
| **QLoRA** | 4-bit quantized base + LoRA | 5-10% base | Near-LoRA | Memory-constrained GPUs |
| **DoRA** | Decomposes weight into magnitude + direction | ~LoRA | Better than LoRA | When quality matters most |
| **AdaLoRA** | Adaptive rank per layer (SVD-based) | Variable | Best | Limited compute budget |
| **IA³** | Learned vectors (not matrices) | 0.01% base | Lower | Extreme efficiency |
| **Prefix Tuning** | Learnable prefix tokens | Tiny | Task-specific | Classification tasks |

```python
# AdaLoRA — automatically allocates rank budget
from peft import AdaLoraConfig
config = AdaLoraConfig(
    init_r=12,         # Initial rank
    target_r=4,        # Target average rank after pruning
    beta1=0.85, beta2=0.85,  # Importance scores EMA
    tinit=200, tfinal=1000,  # Warmup and final pruning steps
    deltaT=10,         # Pruning frequency
)
# Result: critical layers get rank=12, unimportant layers pruned to rank=2
```

### Q14: How do you fine-tune for multi-turn conversation (chat models)?
**Answer:**

```python
# Chat template format (Llama 3 style)
training_data = [
    {
        "messages": [
            {"role": "system", "content": "You are a SEBI-compliant trading advisor."},
            {"role": "user", "content": "Should I buy RELIANCE at current levels?"},
            {"role": "assistant", "content": "Based on RSI=45 and support at 2,380..."},
            {"role": "user", "content": "What about the sector rotation risk?"},
            {"role": "assistant", "content": "Energy sector is 22% of NIFTY, below the 25% SEBI limit..."},
        ]
    }
]

# SFTTrainer handles chat template automatically
from trl import SFTTrainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=lora_config,
    formatting_func=lambda x: tokenizer.apply_chat_template(x["messages"], tokenize=False),
    max_seq_length=4096,  # Longer for multi-turn
)
```

**Key considerations:**
- Loss masking: Only compute loss on assistant turns (not system/user)
- Context window: Multi-turn needs 2-4x more tokens than single-turn
- Data quality: 1,000 high-quality multi-turn conversations > 10,000 single-turn

### Q15: How do you deploy and serve multiple LoRA adapters efficiently in production?
**Answer:**

```python
# vLLM — serve 100+ LoRA adapters on one base model
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM(model="meta-llama/Llama-3-8B", enable_lora=True, max_loras=50)

# Request-level adapter selection
params = SamplingParams(temperature=0.1, max_tokens=256)

# Each user gets their fine-tuned adapter
result1 = llm.generate("Analyze NIFTY...", params, lora_request=LoRARequest("trading-v1", 1, "adapters/trading/"))
result2 = llm.generate("Summarize earnings...", params, lora_request=LoRARequest("finance-v1", 2, "adapters/finance/"))
```

**Production architecture:**
```
Request → Router (selects adapter based on task type)
  → Base model loaded once in GPU VRAM (~16GB for 8B model)
  → LoRA adapter hot-loaded per request (~50MB, <100ms swap)
  → Response generated with merged weights
  → Adapter evicted from GPU cache via LRU policy

Scaling:
- Horizontal: Multiple vLLM replicas behind load balancer
- Adapter store: GCS bucket with versioned adapters
- A/B testing: Route 10% traffic to new adapter version
- Rollback: Instant — just switch adapter path
```
