# Hugging Face Interview Questions and Answers

## Beginner Level Questions

### Q1: What is Hugging Face and what problem does it solve?

**Answer:**

Hugging Face is the leading open-source AI/ML platform that provides:
- **Transformers library**: 1M+ pretrained model checkpoints for NLP, vision, audio, multimodal tasks
- **PEFT library**: Parameter-Efficient Fine-Tuning (LoRA, QLoRA, Adapter Tuning)
- **Datasets library**: 100,000+ ready-to-use ML datasets
- **Hub**: Community platform to share/discover models and datasets
- **Accelerate**: Distributed training made simple

**Problem It Solves:**
Training LLMs from scratch costs $10M–$100M+. Hugging Face lets you:
- **Reuse** state-of-the-art models in 3 lines of code
- **Fine-tune** any model for your domain without full retraining (PEFT)
- **Deploy** via Inference API or on your own hardware

```python
from transformers import pipeline

# Production-ready NLP in 2 lines
classifier = pipeline("sentiment-analysis")
result = classifier("Hugging Face democratizes AI!")
# [{'label': 'POSITIVE', 'score': 0.9999}]
```

---

### Q2: What are the main libraries in the Hugging Face ecosystem?

**Answer:**

| Library | Purpose |
|---------|---------|
| `transformers` | Model architectures, tokenizers, Trainer API, Pipeline API |
| `datasets` | Load, process, and share ML datasets |
| `peft` | Parameter-Efficient Fine-Tuning (LoRA, QLoRA, Adapters) |
| `accelerate` | Distributed training, multi-GPU, DeepSpeed, FSDP |
| `trl` | RLHF, PPO, SFT training for LLMs |
| `evaluate` | Metrics (accuracy, BLEU, ROUGE, F1) |
| `diffusers` | Diffusion models (Stable Diffusion, DALL-E) |
| `tokenizers` | Fast Rust-based tokenizers |

---

### Q3: How do you use the Pipeline API?

**Answer:**

The `pipeline` API is the highest-level abstraction — you don't need to know model internals.

```python
from transformers import pipeline

# 30+ supported tasks out of the box:
tasks = [
    "text-generation",
    "text-classification",
    "question-answering",
    "summarization",
    "translation",
    "ner",                    # Named Entity Recognition
    "fill-mask",
    "image-classification",
    "object-detection",
    "automatic-speech-recognition",
    "text-to-speech",
]

# Generic usage pattern:
pipe = pipeline(task="text-generation", model="gpt2", device=0)
result = pipe("The key to artificial intelligence is", max_new_tokens=50)
print(result[0]["generated_text"])
```

---

### Q4: What is the difference between `AutoModel`, `AutoModelForXxx`, and `pipeline`?

**Answer:**

| Class | When to Use |
|-------|------------|
| `pipeline(task)` | Quickest — handles tokenization, inference, post-processing automatically |
| `AutoModelForXxx` | When you need the model head for a specific task (classification, generation) |
| `AutoModel` | Raw hidden states — use when building custom heads |

```python
# Level 1 — Pipeline (easiest)
from transformers import pipeline
pipe = pipeline("text-classification", model="bert-base-uncased")

# Level 2 — AutoModelForXxx (task-specific head)
from transformers import AutoModelForSequenceClassification, AutoTokenizer
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Level 3 — AutoModel (raw hidden states)
from transformers import AutoModel
model = AutoModel.from_pretrained("bert-base-uncased")
# outputs.last_hidden_state — shape: (batch, seq_len, hidden_size)
```

---

### Q5: How do you load and push models to the Hugging Face Hub?

**Answer:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load from Hub
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")

# Authenticate (one-time)
from huggingface_hub import login
login(token="hf_your_token")

# Push to Hub
model.push_to_hub("your-username/my-finetuned-llama")
tokenizer.push_to_hub("your-username/my-finetuned-llama")
```

---

## Intermediate Level Questions

### Q6: What is PEFT and why is it better than full fine-tuning?

**Answer:**

**PEFT (Parameter-Efficient Fine-Tuning)** fine-tunes a tiny fraction of model parameters (<1%) while achieving performance comparable to full fine-tuning.

**Why full fine-tuning is impractical for LLMs:**
- LLaMA 3.1 70B has 70 billion parameters
- Full fine-tuning requires storing optimizer states (8 bytes/param) → **560GB RAM**
- Even a single forward pass needs 140GB VRAM

**PEFT solution:**
- LoRA on LLaMA 3.1 70B → only 0.06% parameters trained → **fits on 1× A100**

| Approach | Trainable Params | GPU Required | Performance |
|----------|-----------------|--------------|-------------|
| Full fine-tuning | 100% | 8× A100 (640GB) | Baseline |
| LoRA (r=16) | ~0.1% | 1× A100 (80GB) | ≈95% of full FT |
| QLoRA (4-bit + LoRA) | ~0.1% | 1× 3090 (24GB) | ≈90% of full FT |

```python
from peft import get_peft_model, LoraConfig, TaskType

config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,             # Rank — controls adapter capacity
    lora_alpha=32,    # Scaling: effective LR = lora_alpha/r
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
)
model = get_peft_model(base_model, config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.06%
```

---

### Q7: Explain LoRA — how does it work mathematically?

**Answer:**

**LoRA (Low-Rank Adaptation)** decomposes weight updates into two small matrices:

Instead of updating the full weight matrix W ∈ ℝ^(d×d):
```
ΔW = BA   where B ∈ ℝ^(d×r), A ∈ ℝ^(r×d), r << d
```

- Original weights **W are frozen** — never updated
- Only **A** and **B** are trained (r = 16 vs d = 4096 → 256× fewer params)
- At inference: `W_effective = W + (lora_alpha/r) * B @ A`
- LoRA adapters can be merged back into base weights for **zero inference overhead**

```python
# Key hyperparameters:
# r (rank): 4, 8, 16, 32, 64 — higher = more capacity, more params
# lora_alpha: scaling factor, typically 2×r
# target_modules: which projection layers to adapt
#   - Attention: q_proj, k_proj, v_proj, o_proj
#   - MLP: gate_proj, up_proj, down_proj
```

---

### Q8: What is QLoRA and how does it differ from LoRA?

**Answer:**

**QLoRA = Quantization + LoRA**

1. **Quantize the base model to 4-bit NF4** (NormalFloat4 format) → 87% memory reduction
2. **Add LoRA adapters in full precision (BF16)**
3. Use **double quantization** (quantize the quantization constants too)
4. Use **paged optimizers** to offload optimizer states to CPU

```python
from transformers import BitsAndBytesConfig
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                          # Enable 4-bit
    bnb_4bit_quant_type="nf4",                  # NF4 quantization type
    bnb_4bit_use_double_quant=True,             # Double quantization
    bnb_4bit_compute_dtype=torch.bfloat16,      # Compute in BF16
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B",
    quantization_config=bnb_config,
    device_map="auto",
)

# Now apply LoRA on top of 4-bit model
from peft import prepare_model_for_kbit_training, get_peft_model

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)
# Result: 70B model fits in ~40GB VRAM (1× A100 80GB)
```

---

### Q9: How do you use the Trainer API for custom training?

**Answer:**

```python
from transformers import Trainer, TrainingArguments
import evaluate
import numpy as np

# 1. Define training arguments
args = TrainingArguments(
    output_dir="./checkpoints",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    fp16=True,                          # Mixed precision
    gradient_checkpointing=True,        # Memory optimization
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    report_to="none",                   # or "wandb", "tensorboard"
)

# 2. Define compute_metrics
f1_metric = evaluate.load("f1")
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return f1_metric.compute(predictions=predictions, references=labels, average="macro")

# 3. Initialize Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# 4. Train and evaluate
trainer.train()
results = trainer.evaluate()
print(f"F1: {results['eval_f1']:.4f}")
```

---

### Q10: How does the Datasets library handle large datasets?

**Answer:**

The `datasets` library uses **memory-mapping (Apache Arrow)** — datasets are read directly from disk without loading into RAM.

```python
from datasets import load_dataset

# Streaming — never loads full dataset into memory
dataset = load_dataset("wikipedia", "20220301.en", streaming=True)

# Process one batch at a time
for sample in dataset["train"].take(10):
    print(sample["title"])

# Filter large datasets efficiently
filtered = dataset.filter(lambda x: len(x["text"]) > 100)

# Map/tokenize in parallel
tokenized = dataset.map(
    tokenize_function,
    batched=True,
    num_proc=4,     # CPU parallel processing
    remove_columns=["text"],
)
```

---

## Advanced Level Questions

### Q11: How do you implement RLHF (Reinforcement Learning from Human Feedback)?

**Answer:**

RLHF has 3 stages:

**Stage 1: Supervised Fine-Tuning (SFT)**
```python
from trl import SFTTrainer

sft_trainer = SFTTrainer(
    model=base_model,
    train_dataset=curated_demonstrations,
    dataset_text_field="text",
    max_seq_length=2048,
    peft_config=lora_config,
)
sft_trainer.train()
```

**Stage 2: Reward Model Training**
```python
from trl import RewardTrainer, RewardConfig

reward_config = RewardConfig(output_dir="reward-model", per_device_train_batch_size=4)
reward_trainer = RewardTrainer(
    model=reward_model,
    args=reward_config,
    train_dataset=preference_dataset,  # chosen vs rejected pairs
    tokenizer=tokenizer,
)
reward_trainer.train()
```

**Stage 3: PPO Fine-Tuning**
```python
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead

ppo_config = PPOConfig(batch_size=128, mini_batch_size=16, learning_rate=1.41e-5)
ppo_trainer = PPOTrainer(config=ppo_config, model=sft_model, ref_model=ref_model,
                          tokenizer=tokenizer, dataset=dataset)

for batch in ppo_trainer.dataloader:
    response_tensors = ppo_trainer.generate(batch["input_ids"], max_new_tokens=200)
    rewards = [reward_model_score(q, r) for q, r in zip(batch["input_ids"], response_tensors)]
    stats = ppo_trainer.step(batch["input_ids"], response_tensors, rewards)
```

---

### Q12: How do you build a production inference pipeline for LLMs at scale?

**Answer:**

```python
# Option 1: Hugging Face Inference Endpoints (managed)
# Deploy via UI/API — auto-scales, handles batching

# Option 2: Text Generation Inference (TGI) — self-hosted
# docker run -p 8080:80 ghcr.io/huggingface/text-generation-inference \
#   --model-id meta-llama/Llama-3.1-8B-Instruct

# Option 3: vLLM (best open-source throughput)
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    tensor_parallel_size=2,      # Multi-GPU
    gpu_memory_utilization=0.9,
    max_model_len=8192,
)

sampling_params = SamplingParams(temperature=0.7, max_tokens=200)

# Continuous batching — handle 100s of requests simultaneously
outputs = llm.generate(prompts, sampling_params)

# Option 4: Load merged LoRA adapter for inference
from peft import PeftModel

model = AutoModelForCausalLM.from_pretrained(base_model_name)
model = PeftModel.from_pretrained(model, "path/to/adapter")
model = model.merge_and_unload()  # Merge for zero inference overhead
```

---

### Q13: How do you evaluate LLMs and fine-tuned models rigorously?

**Answer:**

```python
import evaluate
from lm_eval import evaluator

# Task-specific metrics
rouge = evaluate.load("rouge")      # Summarization
bleu = evaluate.load("sacrebleu")   # Translation
bertscore = evaluate.load("bertscore")  # Semantic similarity

# LM Evaluation Harness — standardized benchmarks
results = evaluator.simple_evaluate(
    model="hf",
    model_args="pretrained=mistralai/Mistral-7B-v0.1",
    tasks=["hellaswag", "mmlu", "truthfulqa_mc", "gsm8k"],
    num_fewshot=5,
    device="cuda",
)

# Perplexity — lower is better
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

def compute_perplexity(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
    return torch.exp(outputs.loss).item()
```

---

### Q14: What are the architectural differences between LoRA, Adapter Tuning, and Prefix Tuning?

**Answer:**

| Method | Where It Adds Params | How It Works | Best For |
|--------|---------------------|--------------|---------|
| **LoRA** | Inside attention (q, v projections) | Low-rank decomposition ΔW=BA | General, most popular |
| **Adapter Tuning** | Between transformer sub-layers | Bottleneck FFN layers inserted | Multi-task, modular |
| **Prefix Tuning** | Input sequence (prepended tokens) | Learns virtual token embeddings | NLG tasks, conditional gen |
| **Prompt Tuning** | Input embeddings only | Soft prompt vectors (no model change) | Very lightweight adaptation |
| **AdaLoRA** | Attention matrices (SVD-based) | Adaptive rank per weight matrix | When compute budget is tight |

```python
# Adapter Tuning
from peft import AdaptionPromptConfig

# Prefix Tuning
from peft import PrefixTuningConfig
config = PrefixTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,  # Length of prefix
)

# Prompt Tuning
from peft import PromptTuningConfig, PromptTuningInit
config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    prompt_tuning_init=PromptTuningInit.TEXT,
    num_virtual_tokens=8,
    prompt_tuning_init_text="Classify the sentiment of this text:",
)
```

---

### Q15: How do you handle distributed multi-node LLM training with Hugging Face?

**Answer:**

```python
# accelerate config — run once:
# accelerate config  →  sets up multi-GPU/multi-node YAML

# Launch distributed training
# accelerate launch --num_processes=8 --num_machines=2 train.py

from accelerate import Accelerator
from accelerate.utils import DeepSpeedPlugin

# DeepSpeed ZeRO Stage 3 — shards params, grads, optimizer across all GPUs
deepspeed_plugin = DeepSpeedPlugin(
    zero_stage=3,
    gradient_accumulation_steps=4,
    offload_optimizer_device="cpu",  # ZeRO-Offload
    offload_param_device="cpu",
)

accelerator = Accelerator(
    mixed_precision="bf16",
    deepspeed_plugin=deepspeed_plugin,
)

model, optimizer, train_dataloader, scheduler = accelerator.prepare(
    model, optimizer, train_dataloader, lr_scheduler
)

# FSDP alternative (PyTorch native)
# accelerate launch --fsdp_sharding_strategy FULL_SHARD train.py
```
