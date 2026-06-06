# What is PEFT & Fine-Tuning? — Complete Executive Guide

## Table of Contents
1. [Definition & Executive Summary](#1-definition--executive-summary)
2. [Core Architecture](#2-core-architecture)
3. [Key Features & Capabilities](#3-key-features--capabilities)
4. [Installation & Setup](#4-installation--setup)
5. [Beginner Examples](#5-beginner-examples)
6. [Intermediate Patterns](#6-intermediate-patterns)
7. [Advanced Architectures](#7-advanced-architectures)
8. [Best Practices](#8-best-practices)
9. [Common Pitfalls & How to Fix Them](#9-common-pitfalls--how-to-fix-them)
10. [Comparison Matrix](#10-comparison-matrix)
11. [Real-World Use Cases](#11-real-world-use-cases)
12. [Performance & Scalability](#12-performance--scalability)

---

## 1. Definition & Executive Summary

**PEFT (Parameter-Efficient Fine-Tuning)** is a family of techniques that adapt large pretrained models to downstream tasks by training only a small fraction (<1%) of model parameters, while achieving performance comparable to full fine-tuning. Built and maintained by Hugging Face, the `peft` library is the industry standard.

**The Business Problem:** Fine-tuning a 70B-parameter LLM requires 8× A100 GPUs (640GB VRAM) costing $50K+ per training run. PEFT brings this down to 1× A100 ($5K) or even 1× RTX 4090 ($500).

**Who Uses It:** OpenAI (instruction tuning), Meta (Llama fine-tuning guides), Google (Gemma adapters), Microsoft (Phi fine-tuning), Anthropic (RLHF alignment), every Fortune 500 AI team building domain-specific LLMs.

### The Fine-Tuning Landscape

| Method | What It Is | Trainable Params |
|--------|-----------|-----------------|
| **Full Fine-Tuning** | Update all model weights | 100% |
| **LoRA** | Low-rank weight decomposition | 0.01–0.1% |
| **QLoRA** | LoRA + 4-bit quantization | 0.01–0.1% |
| **Adapter Tuning** | Bottleneck FFN layers inserted | 1–5% |
| **Prefix Tuning** | Learned virtual prefix tokens | 0.1% |
| **Prompt Tuning** | Soft prompt vectors only | 0.001% |
| **Instruction Tuning** | SFT on instruction-response pairs | 100% or PEFT |
| **(IA)³** | Inhibit/amplify inner activations | 0.01% |

---

## 2. Core Architecture

### LoRA — Low-Rank Adaptation (Most Popular)

LoRA decomposes weight updates into two small matrices:

```
Original: h = W₀x          (W₀ ∈ ℝ^(d×d), frozen)
LoRA:     h = W₀x + (α/r)·BAx   (B ∈ ℝ^(d×r), A ∈ ℝ^(r×d), trained)
```

- **r (rank)**: Controls adapter capacity. r=16 is standard. Higher = more expressive, more params.
- **α (lora_alpha)**: Scaling factor. Effective learning rate = α/r. Typical: α = 2×r.
- **target_modules**: Which weight matrices to adapt (q_proj, v_proj for attention, gate_proj for MLP).

**Why it works:** Weight updates during fine-tuning have low intrinsic rank — you don't need to update the full d×d matrix.

```python
from peft import LoraConfig, get_peft_model, TaskType

config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
)

model = get_peft_model(base_model, config)
model.print_trainable_parameters()
# trainable: 41,943,040 || all: 8,030,261,248 || trainable%: 0.52%
```

### QLoRA — Quantized LoRA

QLoRA combines 3 innovations:
1. **NF4 Quantization**: 4-bit NormalFloat — optimal for normally distributed weights
2. **Double Quantization**: Quantize the quantization constants (saves 0.37 bits/param)
3. **Paged Optimizers**: Offload optimizer states to CPU via unified memory

```python
from transformers import BitsAndBytesConfig
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B",
    quantization_config=bnb_config,
    device_map="auto",
)
```

### Adapter Tuning

Inserts small bottleneck FFN layers between existing transformer sub-layers:

```
Input → LayerNorm → Self-Attention → [ADAPTER] → Residual
      → LayerNorm → FFN → [ADAPTER] → Residual

Adapter = Linear(d→r) → ReLU → Linear(r→d) + Residual
```

### Prefix Tuning

Prepends learnable virtual tokens to the key-value pairs in every attention layer:

```python
from peft import PrefixTuningConfig

config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    encoder_hidden_size=1024,
)
```

### Prompt Tuning

Only learns soft prompt embeddings prepended to the input — the simplest PEFT method:

```python
from peft import PromptTuningConfig, PromptTuningInit

config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    prompt_tuning_init=PromptTuningInit.TEXT,
    num_virtual_tokens=8,
    prompt_tuning_init_text="Classify if this text is positive or negative:",
    tokenizer_name_or_path="meta-llama/Llama-3.1-8B",
)
```

---

## 3. Key Features & Capabilities

| Feature | What It Does | When to Use |
|---------|-------------|-------------|
| LoRA | Low-rank weight decomposition | Default choice for most fine-tuning |
| QLoRA | LoRA on 4-bit quantized model | Limited GPU memory (<48GB) |
| DoRA | Weight-decomposed LoRA (direction + magnitude) | When LoRA underperforms full FT |
| AdaLoRA | Adaptive rank allocation per layer | Tight param budget optimization |
| (IA)³ | Learned rescaling vectors | Extremely lightweight adaptation |
| Prefix Tuning | Virtual prefix tokens per layer | NLG, conditional generation |
| Prompt Tuning | Soft prompt vectors at input only | Very lightweight, many tasks |
| P-Tuning v2 | Deep prompt tuning across layers | NLU tasks (classification, NER) |
| Adapter merging | Combine multiple adapters | Multi-skill models |
| Multi-adapter inference | Switch adapters at runtime | Multi-tenant serving |

### Native Integrations
Transformers, TRL (SFT/DPO/PPO), Accelerate, DeepSpeed, FSDP, bitsandbytes, Diffusers, Sentence-Transformers, vLLM (LoRA serving), SGLang, Axolotl, LitGPT, Unsloth, Weights & Biases, MLflow

---

## 4. Installation & Setup

```bash
# Core PEFT
pip install peft

# Full fine-tuning stack
pip install peft transformers datasets accelerate bitsandbytes trl evaluate

# For Flash Attention (Linux + NVIDIA)
pip install flash-attn --no-build-isolation

# For Unsloth (2x faster LoRA)
pip install unsloth
```

```python
# Verify installation
import peft
print(peft.__version__)  # 0.13.x+

import torch
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")
```

---

## 5. Beginner Examples

### Example 1: LoRA Fine-Tuning GPT-2 for Sentiment

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
model.config.pad_token_id = tokenizer.pad_token_id

# Add LoRA
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    r=8,
    lora_alpha=16,
    target_modules=["c_attn"],
    lora_dropout=0.1,
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Data
dataset = load_dataset("imdb", split="train[:1000]")
def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, max_length=256, padding="max_length")

tokenized = dataset.map(tokenize, batched=True)

# Train
trainer = Trainer(
    model=model,
    args=TrainingArguments(output_dir="lora-gpt2-imdb", num_train_epochs=3, per_device_train_batch_size=8, fp16=True),
    train_dataset=tokenized,
)
trainer.train()
```

### Example 2: QLoRA on Mistral-7B

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.3", quantization_config=bnb_config, device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
tokenizer.pad_token = tokenizer.eos_token

model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16, lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)

dataset = load_dataset("timdettmers/openassistant-guanaco", split="train[:5000]")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=SFTConfig(output_dir="qlora-mistral", num_train_epochs=1, per_device_train_batch_size=4,
                   gradient_accumulation_steps=4, fp16=True, max_seq_length=2048),
    tokenizer=tokenizer,
    dataset_text_field="text",
)
trainer.train()
model.save_pretrained("qlora-mistral-adapter")  # Saves ~50MB adapter, not 14GB model
```

---

## 6. Intermediate Patterns

### Pattern 1: Multi-Adapter Inference (Serve Many Customers from One Base)
```python
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")

# Load different adapters for different tasks
model = PeftModel.from_pretrained(base_model, "adapters/coding-adapter")
model.load_adapter("adapters/medical-adapter", adapter_name="medical")
model.load_adapter("adapters/legal-adapter", adapter_name="legal")

# Switch at runtime
model.set_adapter("medical")
output_medical = model.generate(inputs)

model.set_adapter("legal")
output_legal = model.generate(inputs)
```

### Pattern 2: Adapter Merging
```python
from peft import PeftModel

model = PeftModel.from_pretrained(base_model, "coding-adapter")
merged = model.merge_and_unload()  # Creates standard model — zero inference overhead
merged.save_pretrained("merged-coding-llama")
```

### Pattern 3: DPO (Direct Preference Optimization) with TRL
```python
from trl import DPOTrainer, DPOConfig
from peft import LoraConfig

dpo_config = DPOConfig(
    output_dir="dpo-output", num_train_epochs=3,
    per_device_train_batch_size=4, beta=0.1,  # KL penalty strength
)
lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])

trainer = DPOTrainer(
    model=sft_model,
    ref_model=None,  # Uses implicit reference with PEFT
    args=dpo_config,
    train_dataset=preference_data,  # columns: prompt, chosen, rejected
    tokenizer=tokenizer,
    peft_config=lora_config,
)
trainer.train()
```

---

## 7. Advanced Architectures

### 1. Multi-Task Adapter System
```
Base LLaMA-3.1-70B (shared, frozen)
├── LoRA Adapter: Customer Support (r=32)
├── LoRA Adapter: Code Generation (r=64)
├── LoRA Adapter: Medical QA (r=16)
├── LoRA Adapter: Legal Analysis (r=16)
└── LoRA Adapter: Financial Reports (r=32)

Router → selects adapter based on request → single GPU serves all tasks
```

### 2. QLoRA + RLHF Pipeline at Scale
```
Stage 1: QLoRA SFT on instruction data (1× A100, 8 hours)
Stage 2: Train reward model (QLoRA on same base, 1× A100, 4 hours)
Stage 3: PPO with LoRA policy (2× A100, 24 hours)
Total cost: ~$300 vs $50,000 for full fine-tuning
```

### 3. Adapter Composition (Merging Math)
```python
# Weighted merge of multiple adapters
from peft import set_peft_model_state_dict
import torch

adapter_weights = {"coding": 0.6, "reasoning": 0.3, "safety": 0.1}
merged_state = {}
for name, weight in adapter_weights.items():
    model.load_adapter(f"adapters/{name}", adapter_name=name)
    state = model.get_adapter_state_dict(name)
    for key, val in state.items():
        merged_state[key] = merged_state.get(key, 0) + weight * val
```

---

## 8. Best Practices

1. **Start with LoRA r=16, alpha=32** — increase r if underfitting, decrease if overfitting
2. **Target all linear layers** for best results: `target_modules="all-linear"`
3. **Use QLoRA for 7B+ models** on consumer GPUs
4. **Always call `prepare_model_for_kbit_training()`** before applying LoRA to quantized models
5. **Learning rate 1e-4 to 2e-4** for LoRA (10x higher than full FT)
6. **Save adapters, not full models** — 50MB vs 14GB
7. **Evaluate before and after merging** — verify no quality loss
8. **Use gradient checkpointing** to halve memory at 30% speed cost
9. **Benchmark your target_modules** — sometimes adding MLP layers helps
10. **Version your adapters on Hugging Face Hub** with model cards

---

## 9. Common Pitfalls & How to Fix Them

| Pitfall | Root Cause | Fix |
|---------|-----------|-----|
| OOM during QLoRA training | Missed `prepare_model_for_kbit_training()` | Always call it before `get_peft_model()` |
| Adapter doesn't save properly | Called `model.save_pretrained()` on wrong object | Use `model.save_pretrained()` on PEFT model |
| Quality drops after merge | Float precision loss during merge | Use `torch.float32` for merge: `model.merge_and_unload(safe_merge=True)` |
| Training loss doesn't decrease | Wrong learning rate | Use 1e-4 to 2e-4 for LoRA, not 2e-5 |
| Model outputs gibberish | Tokenizer pad_token not set | Set `tokenizer.pad_token = tokenizer.eos_token` |
| LoRA underperforms | Too few target modules | Use `target_modules="all-linear"` |
| Multi-GPU QLoRA fails | Wrong device_map | Use `device_map="auto"` with accelerate |
| Adapter incompatible after update | PEFT version mismatch | Pin versions in requirements.txt |

---

## 10. Comparison Matrix

| Feature | Full FT | LoRA | QLoRA | Adapter | Prefix | Prompt |
|---------|---------|------|-------|---------|--------|--------|
| **Trainable %** | 100% | 0.01-1% | 0.01-1% | 1-5% | 0.1% | 0.001% |
| **GPU (7B)** | 4×A100 | 1×A100 | 1×3090 | 1×A100 | 1×3090 | 1×3090 |
| **GPU (70B)** | 8×A100 | 2×A100 | 1×A100 | 4×A100 | 1×A100 | 1×A100 |
| **Quality** | 100% | ~97% | ~93% | ~95% | ~85% | ~78% |
| **Train Speed** | Baseline | 2x faster | 1.5x | 1.5x | 3x | 5x |
| **Inference Overhead** | None | None (after merge) | None | Small | Small | None |
| **Multi-task** | No | Yes (swap adapters) | Yes | Yes (modular) | Yes | Yes |
| **Best For** | Unlimited budget | Default choice | Consumer GPU | Multi-task | NLG | Quick exp |

---

## 11. Real-World Use Cases

1. **Bloomberg**: QLoRA fine-tuning of LLaMA for financial text analysis — 90% cheaper than full FT
2. **Hugging Face**: LoRA adapters on Hub — 100K+ community adapters shared
3. **Microsoft Phi**: LoRA fine-tuning guides for enterprise domain adaptation
4. **Medical AI**: QLoRA on Mistral-7B for clinical decision support — 1 GPU, 8 hours, 92% clinical accuracy
5. **Code Generation**: LoRA on CodeLlama for internal codebase — 50MB adapter captures company coding patterns

---

## 12. Performance & Scalability

| Model Size | Method | GPU | VRAM Used | Train Time (1 epoch, 50K samples) |
|-----------|--------|-----|-----------|-----------------------------------|
| 7B | Full FT | 4×A100 | 240GB | 4 hours |
| 7B | LoRA r=16 | 1×A100 | 20GB | 2 hours |
| 7B | QLoRA r=16 | 1×3090 | 12GB | 3 hours |
| 13B | LoRA r=16 | 1×A100 | 35GB | 4 hours |
| 13B | QLoRA r=16 | 1×3090 | 18GB | 6 hours |
| 70B | LoRA r=64 | 2×A100 | 160GB | 24 hours |
| 70B | QLoRA r=16 | 1×A100 | 40GB | 36 hours |
| 405B | QLoRA r=16 | 4×A100 | 280GB | 72 hours |
