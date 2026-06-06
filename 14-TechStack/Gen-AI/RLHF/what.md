# RLHF — Reinforcement Learning from Human Feedback

## Complete Conceptual Guide: From Foundations to Production

---

## 1. Definition & Core Problem

### What is RLHF?

**Reinforcement Learning from Human Feedback (RLHF)** is a training methodology that aligns Large Language Models (LLMs) with human preferences, values, and intentions using reinforcement learning signals derived from human judgments rather than handcrafted reward functions.

**The Alignment Problem:**
Pre-trained LLMs are next-token predictors — they learn statistical patterns of language but have no inherent understanding of what outputs are *helpful*, *harmless*, or *honest*. RLHF bridges this gap by teaching models what humans actually want.

```
Pre-training: "Predict the next token" → Fluent but unaligned
SFT:          "Mimic good examples" → Helpful but brittle
RLHF:         "Optimize for human preference" → Aligned and robust
```

### Why Not Just Use Supervised Fine-Tuning?

| Limitation of SFT | How RLHF Fixes It |
|---|---|
| Can only mimic demonstrations — ceiling = annotator quality | Learns preferences — can exceed annotator quality |
| Requires exact "correct" answers | Works with relative comparisons (A > B) |
| Mode averaging (blends conflicting styles) | Learns a coherent preference distribution |
| Expensive per-example annotations | Comparisons are 3-5× cheaper than demonstrations |
| Cannot express "degree of preference" | Captures nuanced preference gradients |

### Historical Context & Key Papers

| Year | Paper / Event | Contribution |
|---|---|---|
| 2017 | Christiano et al. — "Deep RL from Human Preferences" | Foundational RLHF for Atari/MuJoCo |
| 2019 | Ziegler et al. — "Fine-Tuning Language Models from Human Preferences" | First RLHF applied to text (summarization) |
| 2020 | Stiennon et al. — "Learning to Summarize from Human Feedback" | Scaled RLHF for summarization at OpenAI |
| 2022 | Ouyang et al. — **InstructGPT** | The seminal paper: 3-stage pipeline (SFT → RM → PPO) |
| 2022 | Bai et al. — **Anthropic's Constitutional AI** | RLAIF: AI-generated feedback replaces human labelers |
| 2023 | Touvron et al. — **Llama 2** | Meta's open RLHF-trained model, detailed safety tuning |
| 2023 | Rafailov et al. — **DPO (Direct Preference Optimization)** | Eliminates reward model, directly optimizes policy |
| 2024 | Hong et al. — **ORPO** | Combines SFT and preference alignment in single step |
| 2024 | Ethayarajh et al. — **KTO** | Works with binary (thumbs up/down) feedback, no pairs needed |

---

## 2. The 3-Stage RLHF Pipeline

The classic RLHF pipeline, as described in the InstructGPT paper, consists of three stages:

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   STAGE 1: SFT   │───▶│ STAGE 2: REWARD  │───▶│  STAGE 3: PPO    │
│                  │    │     MODEL        │    │                  │
│ Supervised Fine- │    │ Learn human      │    │ Optimize policy  │
│ Tuning on demos  │    │ preferences      │    │ with RL signal   │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

---

### Stage 1: Supervised Fine-Tuning (SFT)

**Goal:** Transform a pre-trained base model into a helpful instruction-following assistant.

**Data:** Human-written demonstrations — (prompt, ideal_response) pairs.

**Process:**
1. Collect high-quality demonstration data (typically 10K–100K examples)
2. Fine-tune the pre-trained model using standard cross-entropy loss
3. The resulting SFT model becomes the starting point for RLHF

**Key Concept — Why SFT First?**
PPO is unstable on a raw pre-trained model. SFT provides a "warm start" in the right region of policy space, making RL optimization tractable.

```python
# Stage 1: SFT using TRL
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# Load base model
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

# Load demonstration dataset
# Format: {"text": "### Human: ...\n### Assistant: ..."}
dataset = load_dataset("tatsu-lab/alpaca", split="train")

# SFT Configuration
sft_config = SFTConfig(
    output_dir="./sft_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    logging_steps=10,
    save_strategy="epoch",
    bf16=True,
    max_seq_length=2048,
    packing=True,  # Pack multiple short examples into one sequence
)

# Train
trainer = SFTTrainer(
    model=model,
    args=sft_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
trainer.save_model("./sft_model")
```

**SFT Data Quality Matters More Than Quantity:**
- LIMA paper showed 1,000 curated examples can outperform 50K noisy ones
- Focus on diversity of tasks, not volume
- Include formatting instructions (markdown, code blocks, step-by-step)

---

### Stage 2: Reward Model Training

**Goal:** Train a model that scores any (prompt, response) pair, predicting human preference.

**Data:** Preference pairs — same prompt, two responses, human picks the better one.

```
Prompt: "Explain quantum computing"
Response A: [detailed, accurate explanation]  ← Chosen (preferred)
Response B: [vague, slightly wrong]           ← Rejected
```

**Architecture:**
The reward model is typically the same architecture as the LLM but with the language modeling head replaced by a scalar head that outputs a single reward score.

```
Input: (prompt, response) → Tokenize → Transformer → Last Token Hidden State → Linear(d, 1) → Scalar Reward
```

**Bradley-Terry Loss:**
The reward model is trained using the Bradley-Terry preference model:

$$\mathcal{L}_{RM} = -\log\sigma(r_\theta(x, y_w) - r_\theta(x, y_l))$$

where:
- $r_\theta(x, y_w)$ = reward for chosen response $y_w$
- $r_\theta(x, y_l)$ = reward for rejected response $y_l$
- $\sigma$ = sigmoid function

The model learns to assign higher scores to preferred responses.

```python
# Stage 2: Reward Model Training using TRL
from trl import RewardTrainer, RewardConfig
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

# Start from SFT model — same base, adds classification head
model = AutoModelForSequenceClassification.from_pretrained(
    "./sft_model",
    num_labels=1,  # Scalar reward output
)
tokenizer = AutoTokenizer.from_pretrained("./sft_model")
tokenizer.pad_token = tokenizer.eos_token

# Load preference dataset
# Format: {"prompt": ..., "chosen": ..., "rejected": ...}
dataset = load_dataset("Anthropic/hh-rlhf", split="train")

# Preprocessing: format into comparison pairs
def preprocess(examples):
    """Format preference pairs for RewardTrainer."""
    return {
        "input_ids_chosen": tokenizer(
            examples["chosen"], truncation=True, max_length=512
        )["input_ids"],
        "input_ids_rejected": tokenizer(
            examples["rejected"], truncation=True, max_length=512
        )["input_ids"],
    }

dataset = dataset.map(preprocess, batched=True)

# Reward model config
reward_config = RewardConfig(
    output_dir="./reward_model",
    num_train_epochs=1,           # 1 epoch to avoid overfitting
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=1e-5,           # Lower LR than SFT
    bf16=True,
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    max_length=512,
)

# Train reward model
trainer = RewardTrainer(
    model=model,
    args=reward_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
trainer.save_model("./reward_model")
```

**Reward Model Design Choices:**

| Choice | Recommendation | Why |
|---|---|---|
| Size relative to policy | 50-100% of policy size | Smaller RMs learn shortcuts |
| Training epochs | 1 epoch | Overfitting → reward hacking |
| Initialization | From SFT checkpoint | Better representations |
| Data scaling | 100K+ comparisons | More data = more robust RM |
| Label noise handling | Filter low-agreement pairs | Noisy labels hurt RM quality |

---

### Stage 3: PPO (Proximal Policy Optimization)

**Goal:** Optimize the SFT model to maximize reward model scores while staying close to the original SFT model.

**Why PPO?**
PPO is a policy gradient algorithm that clips the objective to prevent catastrophically large updates — critical for LLM alignment where we want gradual, stable improvement.

**The RLHF Objective:**

$$\mathcal{J}(\theta) = \mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(\cdot|x)} \left[ r_\phi(x, y) - \beta \cdot \text{KL}[\pi_\theta(y|x) || \pi_{\text{ref}}(y|x)] \right]$$

where:
- $r_\phi(x, y)$ = reward model score
- $\beta$ = KL penalty coefficient (typically 0.01–0.2)
- $\pi_\theta$ = policy being optimized
- $\pi_{\text{ref}}$ = reference model (frozen SFT model)
- KL term prevents "reward hacking" — the policy can't drift too far from its starting point

**PPO Clipped Objective:**

$$L^{CLIP}(\theta) = \mathbb{E}_t \left[ \min \left( r_t(\theta) \hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]$$

where $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$ and $\epsilon$ is the clipping range (typically 0.2).

```python
# Stage 3: PPO Training using TRL
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer, pipeline
import torch

# Load SFT model with value head for PPO
model = AutoModelForCausalLMWithValueHead.from_pretrained("./sft_model")
ref_model = AutoModelForCausalLMWithValueHead.from_pretrained("./sft_model")
tokenizer = AutoTokenizer.from_pretrained("./sft_model")
tokenizer.pad_token = tokenizer.eos_token

# Load reward model as a sentiment pipeline
reward_pipe = pipeline(
    "text-classification",
    model="./reward_model",
    tokenizer=tokenizer,
    device=0,
)

# PPO Configuration
ppo_config = PPOConfig(
    model_name="sft_model",
    learning_rate=1.41e-5,
    batch_size=64,
    mini_batch_size=16,
    gradient_accumulation_steps=4,
    ppo_epochs=4,
    kl_penalty="kl",          # KL divergence penalty type
    init_kl_coef=0.2,         # Initial KL coefficient (β)
    target_kl=6.0,            # Adaptive KL target
    clip_range=0.2,           # PPO clipping range (ε)
    vf_coef=0.1,              # Value function coefficient
    log_with="wandb",
)

# Initialize PPO Trainer
ppo_trainer = PPOTrainer(
    config=ppo_config,
    model=model,
    ref_model=ref_model,
    tokenizer=tokenizer,
)

# Training loop
prompts_dataset = [...]  # List of prompts

for epoch in range(ppo_config.ppo_epochs):
    for batch in ppo_trainer.dataloader:
        query_tensors = batch["input_ids"]

        # 1. Generate responses from current policy
        response_tensors = ppo_trainer.generate(
            query_tensors,
            max_new_tokens=256,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
        )

        # 2. Decode responses
        responses = tokenizer.batch_decode(response_tensors, skip_special_tokens=True)

        # 3. Score with reward model
        texts = [q + r for q, r in zip(batch["query"], responses)]
        rewards = [torch.tensor(output["score"]) for output in reward_pipe(texts)]

        # 4. PPO update step
        stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
        ppo_trainer.log_stats(stats, batch, rewards)

# Save aligned model
model.save_pretrained("./rlhf_model")
tokenizer.save_pretrained("./rlhf_model")
```

**Critical PPO Hyperparameters:**

| Parameter | Typical Range | Impact |
|---|---|---|
| `init_kl_coef` (β) | 0.01 – 0.2 | Too low → reward hacking; too high → no learning |
| `clip_range` (ε) | 0.1 – 0.3 | Controls max policy update per step |
| `ppo_epochs` | 2 – 4 | Inner loop optimization steps |
| `mini_batch_size` | 8 – 64 | Affects gradient variance |
| `target_kl` | 3.0 – 10.0 | Adaptive β adjustment target |
| `vf_coef` | 0.1 – 1.0 | Value function loss weight |
| `learning_rate` | 1e-6 – 5e-5 | Policy LR (lower than SFT) |

---

## 3. DPO — Direct Preference Optimization

### The DPO Revolution

**Paper:** "Direct Preference Optimization: Your Language Model Is Secretly a Reward Model" (Rafailov et al., 2023)

**Key Insight:** You don't need a separate reward model or RL training loop. The optimal policy under the RLHF objective has a closed-form solution, and you can directly optimize for it using a simple classification-like loss.

### DPO Derivation (Simplified)

Starting from the RLHF objective:

$$\pi^*(y|x) = \frac{1}{Z(x)} \pi_{\text{ref}}(y|x) \exp\left(\frac{1}{\beta} r(x, y)\right)$$

Solve for the reward:

$$r(x, y) = \beta \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \beta \log Z(x)$$

Substitute into the Bradley-Terry preference model to get the **DPO loss**:

$$\mathcal{L}_{\text{DPO}}(\pi_\theta; \pi_{\text{ref}}) = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right) \right]$$

**Translation:** DPO increases the probability of chosen responses and decreases the probability of rejected responses, scaled by how much each response deviates from the reference model.

### DPO Implementation

```python
# DPO Training using TRL
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from peft import LoraConfig

# Load SFT model (policy) and reference model
model = AutoModelForCausalLM.from_pretrained("./sft_model")
ref_model = AutoModelForCausalLM.from_pretrained("./sft_model")
tokenizer = AutoTokenizer.from_pretrained("./sft_model")
tokenizer.pad_token = tokenizer.eos_token

# LoRA for memory efficiency
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    task_type="CAUSAL_LM",
)

# Load preference data
# Format: {"prompt": ..., "chosen": ..., "rejected": ...}
dataset = load_dataset("Anthropic/hh-rlhf", split="train")

# DPO Configuration
dpo_config = DPOConfig(
    output_dir="./dpo_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=5e-7,          # Very low LR for DPO
    beta=0.1,                    # KL penalty coefficient
    loss_type="sigmoid",         # Standard DPO loss
    bf16=True,
    logging_steps=10,
    warmup_ratio=0.1,
    max_length=1024,
    max_prompt_length=512,
    save_strategy="epoch",
)

# Train with DPO
trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=dpo_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
    peft_config=peft_config,
)
trainer.train()
trainer.save_model("./dpo_model")
```

### PPO vs DPO — Head-to-Head

| Dimension | PPO (RLHF) | DPO |
|---|---|---|
| **Architecture** | Policy + Reward Model + Value Head + Reference | Policy + Reference only |
| **Training stability** | Unstable — sensitive to hyperparams | Stable — simple loss function |
| **GPU memory** | 4 models in memory | 2 models in memory |
| **Implementation** | Complex — RL loop | Simple — classification-like |
| **Performance** | Slight edge on complex tasks | Comparable or better on most benchmarks |
| **Speed** | 2-4× slower | Faster (no generation during training) |
| **Online learning** | Yes — generates new responses | Offline only (fixed preference dataset) |
| **Reward hacking risk** | Higher (explicit reward to exploit) | Lower (implicit reward) |
| **Scalability** | Harder (more moving parts) | Easier |
| **Industry adoption** | ChatGPT, Claude (original) | Llama 3, Zephyr, many open models |

---

## 4. Alternative Alignment Methods

### ORPO (Odds Ratio Preference Optimization)

**Paper:** Hong et al., 2024

**Key Idea:** Combines SFT and preference alignment into a single training step. No need for a separate SFT stage or a reference model.

**ORPO Loss:**

$$\mathcal{L}_{\text{ORPO}} = \mathcal{L}_{\text{SFT}} + \lambda \cdot \mathcal{L}_{\text{OR}}$$

where $\mathcal{L}_{\text{OR}}$ uses the odds ratio of generating chosen vs rejected:

$$\text{OR}(y_w, y_l) = \frac{\text{odds}(y_w)}{\text{odds}(y_l)} = \frac{P(y_w) / (1 - P(y_w))}{P(y_l) / (1 - P(y_l))}$$

```python
# ORPO Training using TRL
from trl import ORPOTrainer, ORPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

orpo_config = ORPOConfig(
    output_dir="./orpo_model",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=8e-6,
    beta=0.1,                # Odds ratio weight (λ)
    bf16=True,
    max_length=1024,
    max_prompt_length=512,
)

trainer = ORPOTrainer(
    model=model,
    args=orpo_config,
    train_dataset=preference_dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

**ORPO Advantages:**
- Single stage: no separate SFT → simpler pipeline
- No reference model → lower memory
- Competitive results with DPO

---

### KTO (Kahneman-Tversky Optimization)

**Paper:** Ethayarajh et al., 2024

**Key Insight:** You don't need paired preferences at all. KTO works with binary signals: "this response is good" or "this response is bad." Inspired by prospect theory — humans feel losses more strongly than gains.

**KTO Loss:**

$$\mathcal{L}_{\text{KTO}} = \mathbb{E}_{(x,y) \sim \mathcal{D}_{\text{desirable}}} \left[ \lambda_D \sigma(\beta \cdot r_\theta) \right] + \mathbb{E}_{(x,y) \sim \mathcal{D}_{\text{undesirable}}} \left[ \lambda_U \sigma(-\beta \cdot r_\theta) \right]$$

where $r_\theta = \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)} - \text{KL}[\pi_\theta || \pi_{\text{ref}}]$

```python
# KTO Training using TRL
from trl import KTOTrainer, KTOConfig

kto_config = KTOConfig(
    output_dir="./kto_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=5e-7,
    beta=0.1,
    desirable_weight=1.0,      # Weight for "good" examples
    undesirable_weight=1.0,    # Weight for "bad" examples
    bf16=True,
    max_length=1024,
    max_prompt_length=512,
)

# Dataset format: {"prompt": ..., "completion": ..., "label": True/False}
trainer = KTOTrainer(
    model=model,
    ref_model=ref_model,
    args=kto_config,
    train_dataset=binary_feedback_dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

**KTO Advantages:**
- Works with unpaired data — no need for A/B comparisons
- Realistic: most real feedback is thumbs up/down
- Handles imbalanced feedback naturally via prospect theory weighting

---

### IPO (Identity Preference Optimization)

**Paper:** Azar et al., 2023

IPO addresses a theoretical flaw in DPO — the assumption that the Bradley-Terry model perfectly captures preferences. IPO adds a regularization term:

$$\mathcal{L}_{\text{IPO}} = \mathbb{E}\left[ \left( \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} - \frac{1}{2\beta} \right)^2 \right]$$

Available in TRL via `DPOConfig(loss_type="ipo")`.

---

### Complete Comparison Matrix: All Alignment Methods

| Method | Stages | Needs RM? | Needs Ref? | Needs Pairs? | Memory | Stability | Performance |
|---|---|---|---|---|---|---|---|
| **RLHF (PPO)** | 3 (SFT→RM→PPO) | ✅ Yes | ✅ Yes | ✅ Yes | 4 models | Low | Excellent |
| **DPO** | 2 (SFT→DPO) | ❌ No | ✅ Yes | ✅ Yes | 2 models | High | Excellent |
| **ORPO** | 1 (combined) | ❌ No | ❌ No | ✅ Yes | 1 model | High | Very Good |
| **KTO** | 2 (SFT→KTO) | ❌ No | ✅ Yes | ❌ No (binary) | 2 models | High | Good |
| **IPO** | 2 (SFT→IPO) | ❌ No | ✅ Yes | ✅ Yes | 2 models | Very High | Good |
| **SPIN** | 2 (SFT→SPIN) | ❌ No | ❌ No (self-play) | Generated | 2 models | Medium | Good |
| **RLAIF** | 3 (SFT→AI-RM→PPO) | ✅ Yes (AI) | ✅ Yes | ✅ Yes (AI) | 4 models | Medium | Very Good |

---

## 5. Advanced Topics

### Constitutional AI (CAI) & RLAIF

**Anthropic's approach:** Replace human feedback with AI feedback guided by a constitution.

**Constitutional AI Pipeline:**
1. Generate responses from a helpful-only model
2. Ask the model to critique its own responses using constitutional principles
3. Ask the model to revise based on critiques
4. Use the revised responses as preference data
5. Train with RLHF/DPO on this AI-generated data

```python
# RLAIF: AI-generated preference data
from anthropic import Anthropic

client = Anthropic()

CONSTITUTION = [
    "Please choose the response that is most helpful while being honest and harmless.",
    "Choose the response that does not contain harmful, unethical, or illegal content.",
    "Choose the response that is factually accurate and well-reasoned.",
]

def generate_ai_preference(prompt, response_a, response_b, principle):
    """Use an AI model to generate preference labels."""
    judge_prompt = f"""
    Given the following prompt and two responses, which response better follows this principle:
    "{principle}"

    Prompt: {prompt}
    Response A: {response_a}
    Response B: {response_b}

    Which is better? Answer with just "A" or "B" and explain briefly.
    """

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    return message.content[0].text
```

**RLAIF Advantages:**
- Scales beyond human labeling capacity
- Consistent application of criteria
- 10-100× cheaper than human annotation
- Can enforce rules humans might miss

---

### Online vs Offline RLHF

| Aspect | Online RLHF | Offline RLHF |
|---|---|---|
| **Data generation** | Policy generates new responses during training | Uses fixed preference dataset |
| **Methods** | PPO, Online DPO, REINFORCE | Standard DPO, KTO, ORPO |
| **Exploration** | Explores new regions of response space | Limited to existing data |
| **Performance** | Generally better (iterative improvement) | Slightly worse (static data) |
| **Compute cost** | Higher (generation overhead) | Lower (no generation step) |
| **Complexity** | Higher (RL loop) | Lower |

**Online DPO:**
```python
# Online DPO generates new responses during training
from trl import OnlineDPOTrainer, OnlineDPOConfig

config = OnlineDPOConfig(
    output_dir="./online_dpo",
    num_train_epochs=1,
    per_device_train_batch_size=4,
    learning_rate=5e-7,
    beta=0.1,
    bf16=True,
)

# Uses a reward model to judge online-generated responses
trainer = OnlineDPOTrainer(
    model=model,
    ref_model=ref_model,
    reward_model=reward_model,  # Judge for online pairs
    args=config,
    train_dataset=prompt_dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

---

### Reward Hacking & Mitigation

**Reward hacking:** The policy finds shortcuts to maximize the reward model's score without actually improving response quality.

**Common Hacking Patterns:**

| Pattern | Description | Example |
|---|---|---|
| **Length exploitation** | Longer responses get higher scores | Model generates verbose, padded responses |
| **Sycophancy** | Agreeing with the user always scores higher | "Great question! You're absolutely right..." |
| **Formatting tricks** | Specific formatting patterns inflate scores | Always using bullet points and headers |
| **Repetition** | Repeating key phrases the RM favors | Restating the question multiple times |
| **Hedging** | Over-qualifying statements | "It's possible that maybe..." |

**Mitigations:**

```python
# 1. KL Penalty (built into PPO/DPO)
# Higher β → more conservative updates → less hacking
ppo_config = PPOConfig(init_kl_coef=0.2)  # Default 0.2, increase if needed

# 2. Length penalty
def compute_reward_with_length_penalty(reward, response_length, target_length=200):
    """Penalize responses that are too long or too short."""
    length_penalty = -0.01 * max(0, response_length - target_length)
    return reward + length_penalty

# 3. Reward model ensemble
def ensemble_reward(prompt, response, reward_models):
    """Average scores from multiple reward models to reduce individual bias."""
    scores = [rm(prompt, response) for rm in reward_models]
    return sum(scores) / len(scores)

# 4. Early stopping based on KL divergence
# Stop training when KL divergence from reference exceeds threshold
ppo_config = PPOConfig(target_kl=6.0)  # Adaptive KL targeting
```

---

### Goodhart's Law in RLHF

**"When a measure becomes a target, it ceases to be a good measure."**

In RLHF context: the reward model is a proxy for human preferences. When optimized too aggressively, the policy exploits the proxy rather than actually satisfying humans.

**The Overoptimization Curve:**
```
Reward Model Score ↑
                    /‾‾‾‾‾‾‾‾‾‾
                   /            \
                  /              \  ← True human preference
                 /                \    starts decreasing
                /                  \
               /                    ‾‾‾
              /
             / ← Sweet spot:
            /    RM score and human pref aligned
           /
──────────/───────────────────────────→ KL from reference
         0   1   2   3   4   5   6

RM score keeps increasing, but actual human satisfaction peaks
and then drops as the policy overfits to RM artifacts.
```

**Mitigation strategies:**
1. **KL constraint** — bound how far policy drifts from reference
2. **RM ensemble** — reduce exploitable gaps
3. **Iterative RLHF** — periodically retrain RM on new policy outputs
4. **Best-of-N** — sample N responses, pick highest reward (no gradient optimization)

---

### Scaling RLHF to 70B+ Models

**Challenges at Scale:**

| Challenge | Solution |
|---|---|
| 4 models in GPU memory (PPO) | DeepSpeed ZeRO-3, FSDP, QLoRA |
| Generation with 70B parameters | vLLM for fast inference, separate generation cluster |
| Reward model latency | Batch scoring, async pipeline |
| Training stability at scale | Lower LR, gradient clipping, longer warmup |

```python
# Scaling RLHF with DeepSpeed + QLoRA
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig
import torch

# 4-bit quantization for 70B model
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load quantized model
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)
model = prepare_model_for_kbit_training(model)

# LoRA adapters (trainable params: ~0.1% of total)
peft_config = LoraConfig(
    r=64,
    lora_alpha=128,
    lora_dropout=0.05,
    target_modules=[
        "q_proj", "v_proj", "k_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    task_type="CAUSAL_LM",
)
```

**Infrastructure for 70B RLHF:**
```
┌─────────────────────────────────────────────┐
│           RLHF Training Cluster              │
├─────────────────────────────────────────────┤
│ Policy Model:   8×A100 80GB (FSDP/ZeRO-3)  │
│ Reference Model: 4×A100 80GB (frozen)        │
│ Reward Model:   4×A100 80GB (frozen)         │
│ Value Head:     Shared with policy           │
│ Generation:     vLLM on separate 4×A100      │
├─────────────────────────────────────────────┤
│ Total: 20×A100 80GB (~$100/hour cloud)      │
│ Training time: 3-7 days                      │
└─────────────────────────────────────────────┘
```

---

## 6. Installation & Setup

### Full Environment Setup

```bash
# Create virtual environment
python -m venv rlhf-env
source rlhf-env/bin/activate

# Install core packages
pip install trl>=0.9.0 transformers>=4.41.0 datasets>=2.19.0
pip install peft>=0.11.0 accelerate>=0.30.0
pip install bitsandbytes>=0.43.0  # For QLoRA
pip install torch>=2.3.0

# Optional: for distributed training
pip install deepspeed>=0.14.0

# Optional: for fast inference during PPO
pip install vllm>=0.4.0

# Optional: for experiment tracking
pip install wandb tensorboard

# Verify installation
python -c "import trl; print(f'TRL version: {trl.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Minimum Hardware Requirements

| Method | Min VRAM (7B) | Min VRAM (13B) | Min VRAM (70B) |
|---|---|---|---|
| SFT (full) | 28 GB | 52 GB | 280 GB |
| SFT (LoRA) | 16 GB | 28 GB | 48 GB |
| DPO (LoRA) | 24 GB | 40 GB | 80 GB |
| PPO (LoRA) | 48 GB | 80 GB | 160 GB |
| ORPO (LoRA) | 16 GB | 28 GB | 48 GB |

---

## 7. Preference Data Collection

### Data Formats

```python
# Format 1: Anthropic/HH-RLHF style (conversation pairs)
{
    "chosen": "\n\nHuman: How do I bake a cake?\n\nAssistant: Here's a simple recipe...",
    "rejected": "\n\nHuman: How do I bake a cake?\n\nAssistant: I don't know."
}

# Format 2: OpenAI/TRL style (structured)
{
    "prompt": "How do I bake a cake?",
    "chosen": "Here's a simple recipe for a vanilla cake:\n1. Preheat oven to 350°F...",
    "rejected": "I'm not sure about baking."
}

# Format 3: chat_template style (messages)
{
    "prompt": [{"role": "user", "content": "How do I bake a cake?"}],
    "chosen": [{"role": "assistant", "content": "Here's a simple recipe..."}],
    "rejected": [{"role": "assistant", "content": "I don't really know."}],
}

# Format 4: KTO binary style
{
    "prompt": "Write a poem about the ocean",
    "completion": "The vast and endless sea stretches...",
    "label": True  # True = desirable, False = undesirable
}
```

### Building a Preference Dataset

```python
from datasets import Dataset

def build_preference_dataset(model, prompts, tokenizer, num_responses=4):
    """Generate preference data by sampling multiple responses and ranking them."""
    records = []

    for prompt in prompts:
        # Generate multiple responses
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        responses = []
        for _ in range(num_responses):
            output = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.9,
                top_p=0.95,
            )
            response = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:],
                                       skip_special_tokens=True)
            responses.append(response)

        # In practice: send to human annotators for ranking
        # Here: placeholder for annotation pipeline
        # ranked_responses = human_rank(prompt, responses)

        # Create pairs from rankings: every (i, j) where rank[i] < rank[j]
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                records.append({
                    "prompt": prompt,
                    "chosen": responses[i],   # Higher ranked
                    "rejected": responses[j],  # Lower ranked
                })

    return Dataset.from_list(records)
```

---

## 8. Best Practices & Production Tips

### Training Pipeline Best Practices

1. **SFT first, always.** Even for DPO — a strong SFT checkpoint is your foundation.
2. **Reward model size matters.** Use at least 50% the size of your policy model.
3. **1 epoch for reward model.** Overfitting is the #1 RM failure mode.
4. **Monitor KL divergence obsessively.** If KL > 10, you're likely reward hacking.
5. **Use LoRA for RL stages.** Full fine-tuning during PPO is wasteful and unstable.
6. **Validate with held-out evaluators.** Track win-rate against reference on N prompts.
7. **Length-normalize reward scores.** Prevents the "verbosity" exploit.
8. **Save checkpoints frequently.** RLHF training is non-monotonic — best model isn't always last.

### Evaluation Metrics

```python
# Key metrics to track during RLHF
{
    "reward/mean": "Average reward score (should increase)",
    "reward/std": "Reward variance (should be moderate, not zero)",
    "kl_divergence": "KL from reference (monitor for drift)",
    "ppo/loss/total": "Combined PPO loss",
    "ppo/policy/entropy": "Policy entropy (should decrease slowly)",
    "ppo/returns/mean": "Advantage-adjusted returns",
    "response_length/mean": "Average response length (watch for inflation)",
    "win_rate/vs_sft": "Human eval win rate against SFT baseline",
    "win_rate/vs_reference": "Win rate against last checkpoint",
}
```

### Common Pitfalls & Solutions

| Pitfall | Symptom | Solution |
|---|---|---|
| Reward hacking | High RM score, low human satisfaction | Increase β, use RM ensemble |
| Mode collapse | All responses look the same | Increase entropy bonus, lower LR |
| Length exploitation | Responses get progressively longer | Add length penalty to reward |
| Sycophancy | Model always agrees with user | Include "disagree correctly" in training data |
| Catastrophic forgetting | Loses base capabilities during RL | Keep KL low, use LoRA |
| Training instability | Loss oscillates wildly | Reduce LR, increase batch size |
| Reward model overfit | RM accuracy very high on train, poor on test | 1 epoch only, more diverse data |
| Degenerate responses | Gibberish or repetitive text | Check tokenizer padding, increase clip range |

---

## 9. Real-World Implementations

### ChatGPT (OpenAI, 2022)

- **Base model:** GPT-3.5 / GPT-4
- **Method:** InstructGPT pipeline (SFT → RM → PPO)
- **Data:** ~100K demonstrations, ~300K comparisons
- **Key innovation:** Showed RLHF dramatically improves base model alignment
- **Result:** A 1.3B RLHF model was preferred over a 175B base model

### Claude (Anthropic, 2023-2024)

- **Base model:** Proprietary
- **Method:** Constitutional AI (RLAIF) + RLHF
- **Key innovation:** AI-generated feedback from constitutional principles
- **Result:** Safer, more honest model with explicit value alignment

### Llama 2 Chat (Meta, 2023)

- **Base model:** Llama 2 (7B, 13B, 70B)
- **Method:** SFT → RLHF (rejection sampling + PPO)
- **Data:** 27K demonstrations, 1M+ comparisons (iteratively collected)
- **Key innovation:** Rejection sampling — generate K responses, pick best by RM
- **Key insight:** Iterative RLHF — retrain RM after each PPO round

### Zephyr (HuggingFace, 2023)

- **Base model:** Mistral 7B
- **Method:** dSFT (distilled SFT) → DPO
- **Data:** UltraChat (SFT), UltraFeedback (DPO)
- **Key innovation:** Showed DPO + small open model can match bigger RLHF models
- **Result:** Beat Llama 2 Chat 70B on MT-Bench with just a 7B model

---

## 10. Future Directions

### Trends in 2025-2026

1. **Process Reward Models (PRMs)** — reward each step of reasoning, not just final answer
2. **Multi-turn RLHF** — align over entire conversations, not single turn
3. **Self-play alignment** — model debates itself to find flaws (SPIN)
4. **Scalable oversight** — human → AI → hierarchical supervision
5. **Value-aligned RL** — constitutional AI with more nuanced values
6. **Token-level rewards** — credit assignment to specific tokens
7. **Synthetic preference data** — LLM-as-a-judge at scale (RLAIF becomes dominant)
8. **RLHF for reasoning** — DeepSeek-R1, OpenAI o1 use RL for chain-of-thought

### Open Challenges

- **Preference data quality** — garbage in → garbage out; noisy labels kill RM
- **Inter-annotator disagreement** — different humans prefer different things
- **Cultural alignment** — whose preferences? Which culture's values?
- **Evaluation** — no gold standard for measuring alignment
- **Compute cost** — PPO requires 4x the memory of standard fine-tuning
- **Safety vs capability** — over-alignment makes models overly cautious ("refusal mode")

---

## 11. Quick Reference Cheat Sheet

```
RLHF Pipeline:    SFT → Reward Model → PPO
DPO Pipeline:     SFT → DPO (no RM needed)
ORPO Pipeline:    Just ORPO (no SFT, no RM)
KTO Pipeline:     SFT → KTO (no pairs needed)
RLAIF Pipeline:   SFT → AI Reward → PPO/DPO

Key Libraries:    trl, transformers, peft, datasets, accelerate
Key Papers:       InstructGPT (2022), DPO (2023), Llama 2 (2023)
Key Metric:       KL divergence from reference model

Golden Rules:
1. SFT quality > SFT quantity
2. 1 epoch for reward model
3. Monitor KL divergence
4. Length-normalize rewards
5. LoRA for RL stages
6. Save checkpoints early and often
```

---

*Last updated: March 2026*
