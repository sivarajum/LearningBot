# RLHF Interview Questions and Answers

## Beginner Level Questions

### Q1: What is RLHF and why is it important?

**Answer:**

RLHF (Reinforcement Learning from Human Feedback) is a training methodology that aligns large language models with human preferences by using human feedback as a reward signal. It bridges the gap between raw language modeling capability and actually useful, safe, helpful behavior.

**Why it matters:**
- **Pre-trained LLMs** learn to predict next tokens — they don't inherently know what's helpful, harmless, or honest
- **SFT alone** teaches format but not nuanced judgment (e.g., when to refuse, how to be balanced)
- **RLHF** captures the subtlety of human preference that no loss function can encode directly
- Powers **ChatGPT, Claude, Gemini** — every frontier model uses some form of human feedback alignment

**The Core Insight:**
Humans can't write a mathematical formula for "good response," but they CAN compare two responses and say which is better. RLHF exploits this asymmetry.

**Simple Analogy:**
- Pre-training = Learning a language by reading every book ever written
- SFT = Learning to follow instructions from curated examples
- RLHF = Having a teacher who reviews your work and says "this answer is better than that one"

---

### Q2: What are the 3 stages of the RLHF pipeline?

**Answer:**

The canonical RLHF pipeline (as described in InstructGPT) has 3 stages:

| Stage | Name | Input | Output | Purpose |
|-------|------|-------|--------|---------|
| **1** | Supervised Fine-Tuning (SFT) | Curated (prompt, response) pairs | SFT model | Teach instruction-following format |
| **2** | Reward Model Training | Human preference comparisons | Reward model (scalar score) | Learn what humans prefer |
| **3** | RL Optimization (PPO) | Prompts + reward signal | Final aligned model | Optimize policy to maximize reward |

**Stage-by-Stage Breakdown:**

**Stage 1 — SFT (Supervised Fine-Tuning):**
```python
from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

dataset = load_dataset("tatsu-lab/alpaca", split="train")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=512,
    packing=True,  # Pack multiple examples into one sequence for efficiency
)
trainer.train()
```

**Stage 2 — Reward Model:**
Train a model to predict human preferences from comparison data.

**Stage 3 — PPO:**
Use the reward model to optimize the SFT model via reinforcement learning.

---

### Q3: What is a reward model and how does it work?

**Answer:**

A reward model (RM) is a neural network trained to predict a scalar reward score for a given (prompt, response) pair. It learns from **human preference data** — pairs of responses where humans labeled which one is better.

**How it's trained:**

1. Collect prompts and generate multiple responses per prompt
2. Human annotators rank responses: "Response A > Response B"
3. Train the RM using a **Bradley-Terry pairwise loss**:

$$\mathcal{L}_{\text{RM}} = -\log \sigma(r_\theta(x, y_w) - r_\theta(x, y_l))$$

Where:
- $r_\theta(x, y_w)$ = reward for the preferred (winning) response
- $r_\theta(x, y_l)$ = reward for the rejected (losing) response
- $\sigma$ = sigmoid function

**Code Example:**
```python
from trl import RewardTrainer, RewardConfig
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

# Reward model is a classifier that outputs a scalar
model = AutoModelForSequenceClassification.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    num_labels=1,  # Scalar reward output
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

# Preference dataset: each example has (prompt, chosen, rejected)
dataset = load_dataset("Anthropic/hh-rlhf", split="train")

training_args = RewardConfig(
    output_dir="reward-model",
    per_device_train_batch_size=4,
    num_train_epochs=1,
    learning_rate=1e-5,
    max_length=512,
)

trainer = RewardTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

**Key Properties:**
- Typically initialized from the SFT model (shared representations)
- Final layer replaced with a linear head outputting a single scalar
- Must generalize beyond the training comparisons

---

### Q4: What is preference data and how is it collected?

**Answer:**

Preference data consists of human judgments comparing two or more model outputs for the same prompt. It's the fuel that powers RLHF.

**Format:**
```json
{
  "prompt": "Explain quantum computing simply",
  "chosen": "Quantum computing uses qubits that can be 0 and 1 simultaneously...",
  "rejected": "Quantum computing is a type of computing that uses quantum mechanics..."
}
```

**Collection Methods:**

| Method | Description | Scale | Cost |
|--------|-------------|-------|------|
| **Human Annotators** | Trained raters compare responses | 10K-100K | $$$$ |
| **AI-Assisted (RLAIF)** | Use a stronger model (e.g., GPT-4) to judge | 100K-1M | $$ |
| **Constitutional AI** | Model self-critiques based on principles | Unlimited | $ |
| **Implicit Feedback** | User upvotes/downvotes, thumbs up/down | Millions | Free |

**Major Preference Datasets:**

| Dataset | Source | Size | Description |
|---------|--------|------|-------------|
| `Anthropic/hh-rlhf` | Anthropic | 170K | Helpfulness + Harmlessness |
| `OpenAssistant/oasst1` | Open-source | 160K | Multi-turn conversations |
| `argilla/ultrafeedback-binarized` | Argilla | 60K | GPT-4 judged preferences |
| `stanfordnlp/SHP` | Stanford | 385K | Reddit-sourced preferences |

**Quality Matters More Than Quantity:**
- InstructGPT used only ~33K comparisons but with highly trained annotators
- Inter-annotator agreement should be >70% — low agreement = noisy signal
- Diverse prompts matter more than many comparisons per prompt

---

### Q5: Why is RLHF needed when SFT already works?

**Answer:**

SFT teaches the model to **mimic** good responses. RLHF teaches the model to **understand why** they're good and generalize that understanding.

**Key Limitations of SFT Alone:**

| Problem | SFT Behavior | RLHF Behavior |
|---------|-------------|----------------|
| **Refusal** | Refuses too much or too little (copies training data distribution) | Learns nuanced boundaries |
| **Verbosity** | Copies length patterns from data | Learns that concise ≠ lazy |
| **Hallucination** | Confidently wrong (learned from confident data) | Lower confidence when uncertain |
| **Sycophancy** | Agrees with user to match "helpful" pattern | Pushes back when user is wrong |
| **Edge Cases** | No training data = random behavior | Generalizes preference patterns |

**Empirical Evidence (InstructGPT paper):**
- 1.3B parameter model with RLHF preferred over 175B SFT-only model
- RLHF improved truthfulness by 21% and reduced toxicity by 25%
- Human raters preferred RLHF outputs 71% of the time over SFT

**The Distributional Argument:**
```
SFT loss:    L = -log P(y_correct | x)       → Mode-seeking (copy the "right" answer)
RLHF loss:   L = -E[R(x,y)] + β·KL(π||π_ref) → Reward-seeking (find ANY good answer)
```

SFT collapses to imitating the training distribution. RLHF explores the full space of good responses, discovering novel correct behaviors beyond the training set.

---

## Intermediate Level Questions

### Q1: How does PPO work in the context of RLHF?

**Answer:**

PPO (Proximal Policy Optimization) is the RL algorithm used to optimize the language model (policy) using the reward model's signal. In RLHF, the "environment" is: generate a response, get a reward score, update the policy.

**PPO Objective in RLHF:**

$$\mathcal{L}_{\text{PPO}} = \mathbb{E}_{(x,y) \sim \pi_\theta} \left[ R_\phi(x, y) - \beta \cdot \text{KL}(\pi_\theta \| \pi_{\text{ref}}) \right]$$

Where:
- $\pi_\theta$ = current policy (the model being trained)
- $\pi_{\text{ref}}$ = reference policy (frozen SFT model)
- $R_\phi(x, y)$ = reward model score
- $\beta$ = KL penalty coefficient
- KL term prevents the model from diverging too far from SFT

**The PPO Training Loop:**

```python
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer, pipeline
import torch

# 1. Load models
model = AutoModelForCausalLMWithValueHead.from_pretrained("sft-model")
ref_model = AutoModelForCausalLMWithValueHead.from_pretrained("sft-model")
tokenizer = AutoTokenizer.from_pretrained("sft-model")

# 2. Load reward model (as a sentiment pipeline or custom RM)
reward_pipeline = pipeline("text-classification", model="reward-model", tokenizer=tokenizer)

# 3. Configure PPO
ppo_config = PPOConfig(
    model_name="rlhf-model",
    learning_rate=1.41e-5,
    batch_size=16,
    mini_batch_size=4,
    gradient_accumulation_steps=1,
    ppo_epochs=4,              # Number of PPO optimization epochs per batch
    kl_penalty="kl",           # KL divergence penalty type
    init_kl_coef=0.2,          # Initial KL coefficient (β)
    target_kl=6.0,             # Target KL divergence
    adap_kl_ctrl=True,         # Adaptive KL controller
    cliprange=0.2,             # PPO clipping parameter
    vf_coef=0.1,               # Value function coefficient
)

# 4. Create PPO trainer
ppo_trainer = PPOTrainer(
    model=model,
    ref_model=ref_model,
    config=ppo_config,
    tokenizer=tokenizer,
)

# 5. Training loop
prompts = ["Explain gravity", "Write a poem about AI", "Debug this code..."]

for epoch in range(10):
    for prompt_text in prompts:
        # Tokenize prompt
        query_tensor = tokenizer.encode(prompt_text, return_tensors="pt").squeeze()

        # Generate response from current policy
        response_tensor = ppo_trainer.generate(query_tensor, max_new_tokens=128)

        # Get reward score
        response_text = tokenizer.decode(response_tensor.squeeze())
        reward_output = reward_pipeline(response_text)
        reward = torch.tensor([reward_output[0]["score"]])

        # PPO step: update policy
        stats = ppo_trainer.step(
            queries=[query_tensor],
            responses=[response_tensor.squeeze()],
            scores=[reward],
        )

        # Log metrics
        print(f"Epoch {epoch} | Reward: {reward.item():.3f} | KL: {stats['ppo/mean_kl']:.3f}")
```

**Why PPO Specifically?**
- **Clipping** prevents catastrophically large updates (stability)
- **Trust region** approach — small steps in policy space
- Empirically more stable than REINFORCE, A2C for LLM fine-tuning
- Well-tested at scale (InstructGPT, ChatGPT)

---

### Q2: What is the role of KL divergence penalty in RLHF?

**Answer:**

The KL (Kullback-Leibler) divergence penalty is the single most critical component preventing RLHF from collapsing. It acts as a regularizer that keeps the RL-updated policy close to the original SFT model.

$$\text{KL}(\pi_\theta \| \pi_{\text{ref}}) = \mathbb{E}_{y \sim \pi_\theta} \left[ \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)} \right]$$

**Why It's Needed:**

Without KL penalty, the model will **reward hack** — find degenerate outputs that score high on the reward model but are garbage:

| Without KL | With KL |
|-----------|---------|
| Model outputs same high-reward phrase repeatedly | Model generates diverse, natural responses |
| Exploits reward model weaknesses | Stays close to coherent language |
| Catastrophic forgetting of pre-training | Retains general language ability |
| Mode collapse to a single response type | Maintains output diversity |

**Adaptive KL Control:**

In practice, KL is controlled adaptively:
```python
# Adaptive KL controller (from TRL)
# If KL too high → increase β (stronger penalty)
# If KL too low  → decrease β (allow more exploration)

if current_kl > target_kl * 1.5:
    kl_coef *= 1.5   # Tighten constraint
elif current_kl < target_kl / 1.5:
    kl_coef /= 1.5   # Relax constraint
```

**Typical Values:**
- `init_kl_coef` (β): 0.01–0.2
- `target_kl`: 3.0–10.0
- If KL > 15: model has diverged too far, likely unstable
- If KL ≈ 0: model isn't learning anything new

**Impact Visualization:**
```
β too low (0.001):  Model → reward hacking, gibberish, mode collapse
β sweet spot (0.1): Model → helpful, diverse, aligned outputs
β too high (10.0):  Model → barely changes from SFT (underfitting to preferences)
```

---

### Q3: What is DPO and how does it differ from PPO-based RLHF?

**Answer:**

DPO (Direct Preference Optimization) is a 2023 breakthrough that eliminates the reward model and RL loop entirely. It directly optimizes the policy using preference data with a simple classification-like loss.

**Key Insight:** The optimal policy under the RLHF objective has a closed-form solution in terms of the reward function. DPO reparameterizes the reward as a function of the policy itself.

**DPO Loss:**

$$\mathcal{L}_{\text{DPO}} = -\log \sigma \left( \beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right)$$

**PPO vs DPO Comparison:**

| Aspect | PPO (RLHF) | DPO |
|--------|-----------|-----|
| **Models needed** | Policy + Reference + Reward + Value | Policy + Reference only |
| **GPU memory** | 4 models in memory | 2 models in memory |
| **Training stability** | Sensitive to hyperparameters | More stable |
| **Training speed** | Slow (RL loop, generation) | Fast (supervised-like) |
| **Implementation** | Complex (PPO algorithm) | Simple (binary cross-entropy) |
| **Performance** | Battle-tested at massive scale | Competitive, sometimes better |
| **Exploration** | Explores via generation | No exploration (offline only) |

**DPO Code Example:**
```python
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# Load SFT model and reference
model = AutoModelForCausalLM.from_pretrained("sft-model")
ref_model = AutoModelForCausalLM.from_pretrained("sft-model")
tokenizer = AutoTokenizer.from_pretrained("sft-model")
tokenizer.pad_token = tokenizer.eos_token

# Preference dataset: must have "prompt", "chosen", "rejected" columns
dataset = load_dataset("argilla/ultrafeedback-binarized-preferences", split="train")

dpo_config = DPOConfig(
    output_dir="dpo-model",
    beta=0.1,                         # Temperature (controls deviation from reference)
    learning_rate=5e-7,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=1,
    max_length=1024,
    max_prompt_length=512,
    loss_type="sigmoid",              # Options: "sigmoid", "hinge", "ipo"
    bf16=True,
)

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=dpo_config,
    train_dataset=dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

**When to Use Each:**
- **PPO**: When you have a reward model already, need online exploration, or working at massive scale (>70B params)
- **DPO**: Default choice for most practitioners. Simpler, faster, competitive results. Use when you have preference data.

---

### Q4: What is reward hacking and how do you prevent it?

**Answer:**

Reward hacking occurs when the RL-trained model finds degenerate shortcuts to maximize the reward model's score without actually improving response quality. It exploits **reward model weaknesses** rather than learning genuine alignment.

**Common Reward Hacking Behaviors:**

| Hack | What Happens | Example |
|------|-------------|---------|
| **Length gaming** | Longer responses get higher reward | Model writes 10 paragraphs for a yes/no question |
| **Style mimicry** | Certain phrases score high | "Great question! Let me break this down..." every time |
| **Sycophancy** | Agreeing with user scores high | "You're absolutely right!" even when user is wrong |
| **Repetition** | Repeating key phrases boosts score | Same sentence reformulated 5 times |
| **Format exploitation** | Bullet points/headers score well | Everything in numbered lists regardless of content |

**Prevention Strategies:**

```python
# 1. KL penalty (primary defense)
ppo_config = PPOConfig(
    init_kl_coef=0.2,       # Strong KL constraint
    target_kl=6.0,
    adap_kl_ctrl=True,
)

# 2. Reward model ensemble (reduces single-point exploitation)
class EnsembleRewardModel:
    def __init__(self, models):
        self.models = models  # Multiple RMs trained on different data splits

    def score(self, prompt, response):
        scores = [m.score(prompt, response) for m in self.models]
        return min(scores)  # Conservative: take minimum reward

# 3. Length normalization
def length_normalized_reward(reward, response_length, target_length=200):
    penalty = max(0, (response_length - target_length) / target_length)
    return reward - 0.5 * penalty

# 4. Reward clipping
def clip_reward(reward, min_val=-4.0, max_val=4.0):
    return max(min_val, min(reward, max_val))
```

**Key Principle:** The reward model is always an imperfect proxy for human preferences. RLHF training will find its weaknesses if you push too hard.

---

### Q5: What is Constitutional AI (CAI) and how does it relate to RLHF?

**Answer:**

Constitutional AI (Anthropic, 2022) replaces human annotators with a constitution — a set of principles the model uses to self-critique and self-improve. It's sometimes called RLAIF (RL from AI Feedback).

**The CAI Pipeline:**

| Stage | What Happens | Human Needed? |
|-------|-------------|---------------|
| 1. Generate | Model generates initial response | No |
| 2. Critique | Model critiques its own response against principles | No |
| 3. Revise | Model writes an improved version | No |
| 4. Train RM | Train reward model on (original, revised) pairs | No |
| 5. RL | Standard PPO using the AI-trained RM | No |

**Example Constitution Principles:**
```
1. Choose the response that is most helpful to the user.
2. Choose the response that is least harmful or toxic.
3. Choose the response that is most honest and doesn't make up facts.
4. Choose the response that best avoids stereotypes and bias.
5. Choose the response that best respects privacy.
```

**Self-Critique Example:**
```python
constitution = [
    "Is this response harmful or toxic in any way?",
    "Does this response contain any factual errors?",
    "Could this response be more helpful while remaining safe?",
]

def constitutional_critique(model, prompt, response, principles):
    """Model critiques its own response against constitutional principles."""
    critiques = []
    for principle in principles:
        critique_prompt = f"""
Human: {prompt}
Assistant: {response}

Critique Request: {principle}
Provide your critique and a revised response.
"""
        critique = model.generate(critique_prompt)
        critiques.append(critique)

    # Use the revised responses as "chosen" and originals as "rejected"
    # to train the reward model
    return critiques
```

**CAI vs Standard RLHF:**

| Aspect | Standard RLHF | Constitutional AI |
|--------|--------------|-------------------|
| **Human labor** | Thousands of comparisons | Write ~20 principles |
| **Scalability** | Limited by annotator bandwidth | Unlimited comparisons |
| **Consistency** | Inter-annotator disagreement | Consistent principles |
| **Cost** | $100K–$1M for preference data | Minimal (compute only) |
| **Transparency** | Black-box preferences | Explicit, auditable rules |
| **Used by** | OpenAI (InstructGPT, ChatGPT) | Anthropic (Claude) |

---

## Advanced Level Questions

### Q1: How do you scale RLHF training to 70B+ parameter models?

**Answer:**

Scaling RLHF to 70B+ models is one of the hardest problems in alignment engineering. PPO requires 4 models in memory simultaneously: **policy**, **reference**, **reward model**, and **value head**. For a 70B model, that's ~560GB in fp16.

**Memory Requirements:**

| Component | 7B (fp16) | 70B (fp16) | 70B (LoRA) |
|-----------|-----------|------------|------------|
| Policy model | 14 GB | 140 GB | 140 GB + 0.2 GB adapters |
| Reference model | 14 GB | 140 GB | 140 GB (frozen) |
| Reward model | 14 GB | 140 GB | 140 GB |
| Value head | 14 GB | 140 GB | Shared with policy |
| Optimizer states | 28 GB | 280 GB | 0.4 GB |
| **Total** | **84 GB** | **840 GB** | **~420 GB** |

**Scaling Strategies:**

```python
# Strategy 1: LoRA + QLoRA (most practical)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig
import torch

# 4-bit quantization reduces memory 4×
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    quantization_config=bnb_config,
    device_map="auto",  # Automatic multi-GPU sharding
)
model = prepare_model_for_kbit_training(model)

# LoRA: train only 0.1% of parameters
lora_config = LoraConfig(
    r=64,                    # Rank
    lora_alpha=16,           # Scaling factor
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
# Trainable params: ~67M out of 70B (0.1%)
```

```python
# Strategy 2: DeepSpeed ZeRO Stage 3 (distributed across GPUs)
# deepspeed_config.json
{
    "bf16": {"enabled": true},
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu"},
        "offload_param": {"device": "cpu"},
        "overlap_comm": true,
        "contiguous_gradients": true,
        "reduce_bucket_size": 5e8
    },
    "gradient_accumulation_steps": 16,
    "train_micro_batch_size_per_gpu": 1
}
```

```python
# Strategy 3: Use DPO instead of PPO (halves memory — no RM or value head)
from trl import DPOTrainer, DPOConfig

# DPO only needs policy + reference = 2 models instead of 4
# For 70B: 280 GB instead of 840 GB
dpo_config = DPOConfig(
    beta=0.1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    bf16=True,
    gradient_checkpointing=True,  # Trade compute for memory
)
```

**Production Setup (8×A100 80GB):**
- Policy: Sharded across 4 GPUs (ZeRO-3)
- Reference: Sharded across 4 GPUs (frozen, no grad)
- Reward model: Can be smaller (7B) on 1 GPU
- Total: 8 GPUs = 640 GB, fits 70B PPO with ZeRO-3

---

### Q2: Explain the InstructGPT pipeline in detail

**Answer:**

InstructGPT (Ouyang et al., 2022) is the foundational paper for RLHF. It describes how OpenAI aligned GPT-3 (175B) to follow instructions, producing the precursor to ChatGPT.

**Dataset Construction:**

| Stage | Data Source | Size | Annotators |
|-------|-----------|------|------------|
| **SFT** | Labeler-written demonstrations | ~13K prompts | 40 contractors |
| **RM** | Labeler comparisons (4-9 responses ranked) | ~33K comparisons | 40 contractors |
| **PPO** | Prompts from API users | ~31K prompts | No human in loop |

**Key Technical Decisions:**

```python
# InstructGPT reward model architecture
class InstructGPTRewardModel:
    """
    - Initialized from GPT-3 6B (NOT 175B — smaller RM is fine)
    - Final unembedding layer replaced with scalar projection head
    - Trained on all K choose 2 comparisons per prompt (not just pairs)
    """
    def __init__(self, base_model_size="6B"):
        self.backbone = GPT3(base_model_size)
        self.scalar_head = nn.Linear(hidden_size, 1)  # Projects to scalar reward

    def forward(self, prompt, response):
        hidden = self.backbone(prompt + response)
        reward = self.scalar_head(hidden[-1])  # Last token's hidden state
        return reward

# Loss: pairwise ranking over all comparisons from a single prompt
# If annotator ranks: A > B > C > D, train on all C(4,2) = 6 pairs
def reward_loss(rewards, rankings):
    """
    rewards: dict mapping response_id -> scalar reward
    rankings: list of (winner, loser) pairs
    """
    loss = 0
    for winner, loser in rankings:
        loss += -torch.log(torch.sigmoid(rewards[winner] - rewards[loser]))
    return loss / len(rankings)
```

**Critical Results from the Paper:**

| Metric | GPT-3 (175B) | InstructGPT (1.3B) | Improvement |
|--------|-------------|--------------------|----|
| Human preference win rate | 29% | **71%** | +42% |
| Truthfulness (TruthfulQA) | 22% | **43%** | +21% |
| Toxicity reduction | Baseline | **-25%** | Significant |
| Hallucination rate | High | Lower | Measured |

**The Key Takeaway:** A 1.3B RLHF model was preferred by humans over a 175B SFT-only model. Alignment > Size.

**Annotator Selection Protocol:**
- 40 contractors screened from thousands
- Tested on sensitivity assessment tasks
- Inter-annotator agreement: ~73%
- Annotators trained on detailed guidelines (not just "pick the better one")

---

### Q3: How are reward models architected and what makes a good one?

**Answer:**

Reward model architecture is deceptively simple but getting it right is critical. A bad RM means a bad final model — garbage in, garbage out.

**Architecture Options:**

```python
# Option 1: Classifier head on LLM (most common)
from transformers import AutoModelForSequenceClassification

class LLMRewardModel:
    """
    Architecture: Base LLM + Linear(hidden_dim → 1) on final token
    Pros: Inherits language understanding from pre-training
    Cons: Expensive, slow inference
    """
    def __init__(self, model_name):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=1
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits  # Shape: (batch_size, 1)


# Option 2: Smaller dedicated model (practical for production)
class EfficientRewardModel(nn.Module):
    """
    Architecture: DeBERTa-v3-large (304M params) + MLP head
    Used by: Open-source projects (OpenAssistant, Zephyr)
    Pros: Fast inference, fits on single GPU
    Cons: Less expressive than large LLM-based RM
    """
    def __init__(self):
        super().__init__()
        self.backbone = AutoModel.from_pretrained("microsoft/deberta-v3-large")
        self.head = nn.Sequential(
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 1),
        )

    def forward(self, input_ids, attention_mask):
        hidden = self.backbone(input_ids, attention_mask).last_hidden_state
        pooled = hidden[:, -1, :]  # Last token pooling
        return self.head(pooled)


# Option 3: Ensemble reward model (most robust)
class EnsembleRM:
    """
    Train 3-5 RMs on different data splits.
    Take conservative estimate (min or mean - std).
    Prevents reward hacking better than single RM.
    """
    def __init__(self, models):
        self.models = models

    def score(self, prompt, response):
        scores = [m.score(prompt, response) for m in self.models]
        mean = sum(scores) / len(scores)
        std = (sum((s - mean)**2 for s in scores) / len(scores)) ** 0.5
        return mean - std  # Conservative estimate
```

**Reward Model Quality Metrics:**

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| **Accuracy** | Agreement with held-out human preferences | >70% |
| **Calibration** | Score distribution matches preference strength | Smooth sigmoid |
| **OOD Robustness** | Performance on unseen prompt types | <5% drop |
| **Length bias** | Correlation between reward and response length | r < 0.3 |
| **Reward variance** | Score stability across paraphrases | Low variance |

**Common Pitfalls:**
1. **Length bias** — RM gives higher scores to longer responses → normalize by length
2. **Position bias** — RM prefers response A over B regardless of content → shuffle pairs
3. **Verbosity reward** — Bullet points/headers always score high → add format-agnostic examples
4. **Overfit to annotator quirks** — Use diverse annotator pool, not just 3 people

---

### Q4: Compare all RLHF alternatives: DPO, ORPO, KTO, IPO, and SPIN

**Answer:**

The RLHF landscape has exploded with alternatives to PPO. Here's a rigorous comparison:

**Mathematical Formulations:**

```python
import torch
import torch.nn.functional as F


def ppo_objective(policy_logprobs, ref_logprobs, rewards, kl_coef=0.1, clip_eps=0.2):
    """Standard RLHF with PPO: maximize reward while staying close to reference."""
    ratio = torch.exp(policy_logprobs - ref_logprobs)
    advantages = rewards - rewards.mean()
    clipped = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * advantages
    kl = (policy_logprobs - ref_logprobs).mean()
    return -torch.min(ratio * advantages, clipped).mean() + kl_coef * kl


def dpo_loss(policy_chosen_lp, policy_rejected_lp, ref_chosen_lp, ref_rejected_lp, beta=0.1):
    """DPO: Direct optimization without reward model.
    Reparameterizes reward as implicit function of policy.
    """
    chosen_logratios = policy_chosen_lp - ref_chosen_lp
    rejected_logratios = policy_rejected_lp - ref_rejected_lp
    logits = beta * (chosen_logratios - rejected_logratios)
    return -F.logsigmoid(logits).mean()


def ipo_loss(policy_chosen_lp, policy_rejected_lp, ref_chosen_lp, ref_rejected_lp, beta=0.1):
    """IPO (Identity Preference Optimization): avoids overfitting to preference strength.
    Uses squared loss instead of log-sigmoid.
    """
    chosen_logratios = policy_chosen_lp - ref_chosen_lp
    rejected_logratios = policy_rejected_lp - ref_rejected_lp
    logits = beta * (chosen_logratios - rejected_logratios)
    return (logits - 1.0 / (2 * beta)).pow(2).mean()


def kto_loss(policy_lp, ref_lp, is_desirable, beta=0.1):
    """KTO (Kahneman-Tversky Optimization): works with unpaired data (just good/bad labels).
    Based on prospect theory — losses loom larger than gains.
    """
    logratios = policy_lp - ref_lp
    z_ref = logratios.detach().mean()
    desirable_loss = -F.logsigmoid(beta * (logratios - z_ref))
    undesirable_loss = -F.logsigmoid(beta * (z_ref - logratios))
    loss = torch.where(is_desirable, desirable_loss, undesirable_loss)
    return loss.mean()


def orpo_loss(policy_chosen_lp, policy_rejected_lp, beta=0.1):
    """ORPO (Odds Ratio Preference Optimization): no reference model needed!
    Combines SFT loss with odds-ratio preference term.
    """
    # Log odds ratio
    chosen_odds = policy_chosen_lp - torch.log1p(-policy_chosen_lp.exp())
    rejected_odds = policy_rejected_lp - torch.log1p(-policy_rejected_lp.exp())
    log_odds_ratio = chosen_odds - rejected_odds
    # Preference loss
    pref_loss = -F.logsigmoid(beta * log_odds_ratio).mean()
    # SFT loss on chosen (built-in — no separate SFT step)
    sft_loss = -policy_chosen_lp.mean()
    return sft_loss + pref_loss
```

**Head-to-Head Comparison:**

| Method | Year | Needs RM? | Needs Ref Model? | Needs Paired Data? | Memory (7B) | Stability | Performance |
|--------|------|-----------|-------------------|--------------------|-------------|-----------|-------------|
| **PPO** | 2017/2022 | ✅ Yes | ✅ Yes | ❌ No (uses RM) | 56 GB | ⚠️ Sensitive | ⭐⭐⭐⭐⭐ |
| **DPO** | 2023 | ❌ No | ✅ Yes | ✅ Yes | 28 GB | ✅ Stable | ⭐⭐⭐⭐ |
| **IPO** | 2023 | ❌ No | ✅ Yes | ✅ Yes | 28 GB | ✅ Very stable | ⭐⭐⭐⭐ |
| **KTO** | 2024 | ❌ No | ✅ Yes | ❌ No (unpaired) | 28 GB | ✅ Stable | ⭐⭐⭐⭐ |
| **ORPO** | 2024 | ❌ No | ❌ No | ✅ Yes | 14 GB | ✅ Very stable | ⭐⭐⭐⭐ |
| **SPIN** | 2024 | ❌ No | ❌ No | ❌ No (self-play) | 28 GB | ✅ Stable | ⭐⭐⭐ |

**When to Choose What:**

```
Have human preference pairs?    → DPO (simplest, strong baseline)
Only have good/bad labels?      → KTO (works with unpaired data)
Want minimal memory footprint?  → ORPO (no reference model)
Need maximum performance?       → PPO (gold standard, but expensive)
Concerned about DPO overfitting? → IPO (more conservative)
No preference data at all?      → SPIN (self-play improvement)
```

---

### Q5: What is multi-objective RLHF and how do you balance helpfulness vs. safety?

**Answer:**

Real-world alignment isn't a single objective. You need the model to be simultaneously **helpful**, **harmless**, **honest**, and maybe **concise**, **factual**, **creative**, etc. These objectives often conflict.

**The Multi-Objective Problem:**

```
Maximize: helpfulness(response)
Subject to:
  - harmlessness(response) > threshold_safety
  - honesty(response) > threshold_truth
  - length(response) < max_tokens
  - format(response) matches request
```

**Approaches:**

```python
# Approach 1: Multiple Reward Models (Llama 2 style)
class MultiObjectiveRM:
    """
    Llama 2 uses separate reward models for helpfulness and safety.
    Final reward = weighted combination.
    """
    def __init__(self):
        self.helpfulness_rm = load_model("helpfulness-rm")
        self.safety_rm = load_model("safety-rm")

    def score(self, prompt, response, safety_weight=0.5):
        h_score = self.helpfulness_rm(prompt, response)
        s_score = self.safety_rm(prompt, response)

        # Safety has a margin — if unsafe, safety dominates
        if s_score < 0.5:  # Below safety threshold
            return s_score  # Only safety matters
        else:
            return (1 - safety_weight) * h_score + safety_weight * s_score


# Approach 2: Reward model with multi-head output
class MultiHeadRM(nn.Module):
    """
    Single backbone, multiple heads for different objectives.
    More parameter-efficient than separate models.
    """
    def __init__(self, backbone):
        super().__init__()
        self.backbone = backbone
        self.helpfulness_head = nn.Linear(hidden_dim, 1)
        self.safety_head = nn.Linear(hidden_dim, 1)
        self.honesty_head = nn.Linear(hidden_dim, 1)

    def forward(self, input_ids, attention_mask):
        hidden = self.backbone(input_ids, attention_mask).last_hidden_state[:, -1, :]
        return {
            "helpfulness": self.helpfulness_head(hidden),
            "safety": self.safety_head(hidden),
            "honesty": self.honesty_head(hidden),
        }


# Approach 3: Constrained optimization (Pareto-optimal)
class ConstrainedRLHF:
    """
    Treat safety/honesty as constraints, not objectives.
    Maximize helpfulness subject to safety > threshold.
    Uses Lagrangian relaxation.
    """
    def compute_reward(self, prompt, response):
        h = self.helpfulness_rm(prompt, response)
        s = self.safety_rm(prompt, response)

        # Lagrangian: L = helpfulness - λ * max(0, threshold - safety)
        safety_threshold = 0.5
        safety_violation = max(0, safety_threshold - s)

        # λ increases when safety is violated (adaptive)
        self.lagrange_lambda += self.lr * safety_violation
        self.lagrange_lambda = max(0, self.lagrange_lambda)

        reward = h - self.lagrange_lambda * safety_violation
        return reward
```

**Llama 2 Safety Approach (Meta):**
1. Train two separate RMs: helpfulness-RM and safety-RM
2. During PPO: if safety-RM score < threshold → use only safety reward
3. Otherwise: weighted average of both rewards
4. **Safety margin**: 0.15 gap required between chosen and rejected safety scores
5. Context-dependent weighting: for sensitive topics, safety weight → 1.0

**The Alignment Tax:**
```
Helpfulness-only RLHF:   Performance = 100%
With safety constraint:    Performance = 92-95%   (-5-8%)
With honesty constraint:   Performance = 88-93%   (-7-12%)
All constraints:           Performance = 85-90%   (-10-15%)
```

This performance trade-off is the "alignment tax" — the cost of making models safer. The goal is to minimize it through better training techniques, not by removing safety constraints.

---

## Quick Reference Card

### Key Formulas

| Method | Loss Function |
|--------|------|
| **SFT** | $\mathcal{L} = -\sum \log P_\theta(y_i \mid y_{<i}, x)$ |
| **Reward Model** | $\mathcal{L} = -\log \sigma(r_\theta(x, y_w) - r_\theta(x, y_l))$ |
| **PPO** | $\mathcal{L} = -\mathbb{E}[R(x,y)] + \beta \cdot KL(\pi_\theta \| \pi_{ref})$ |
| **DPO** | $\mathcal{L} = -\log \sigma(\beta(\log \frac{\pi_\theta(y_w))}{\pi_{ref}(y_w)} - \log \frac{\pi_\theta(y_l)}{\pi_{ref}(y_l)}))$ |

### Essential Libraries

| Library | Purpose | Install |
|---------|---------|---------|
| `trl` | SFT, RM, PPO, DPO trainers | `pip install trl` |
| `transformers` | Model loading, tokenizers | `pip install transformers` |
| `peft` | LoRA, QLoRA adapters | `pip install peft` |
| `datasets` | Loading preference data | `pip install datasets` |
| `bitsandbytes` | 4-bit/8-bit quantization | `pip install bitsandbytes` |
| `deepspeed` | Distributed training | `pip install deepspeed` |
| `accelerate` | Multi-GPU orchestration | `pip install accelerate` |

### Key Papers

| Paper | Year | Contribution |
|-------|------|-------------|
| InstructGPT (Ouyang et al.) | 2022 | Original RLHF pipeline for LLMs |
| Constitutional AI (Bai et al.) | 2022 | AI feedback replaces human feedback |
| DPO (Rafailov et al.) | 2023 | Eliminates RM and RL loop |
| Llama 2 (Touvron et al.) | 2023 | Multi-objective RLHF at scale |
| KTO (Ethayarajh et al.) | 2024 | Works with unpaired preference data |
| ORPO (Hong et al.) | 2024 | No reference model needed |
| IPO (Azar et al.) | 2023 | More robust DPO variant |
| SPIN (Chen et al.) | 2024 | Self-play fine-tuning |
