# Model Quantization Interview Questions and Answers

> **Complete interview preparation guide** covering beginner to advanced model quantization concepts with real code examples, production patterns, and deep technical analysis.

---

## Table of Contents

- [Beginner Level (5 Questions)](#beginner-level)
- [Intermediate Level (5 Questions)](#intermediate-level)
- [Advanced Level (5 Questions)](#advanced-level)
- [Code Examples Reference](#code-examples-reference)
- [Quick Revision Cheat Sheet](#quick-revision-cheat-sheet)

---

## Beginner Level

### Q1: What is model quantization, and why is it important for LLM deployment?

**Answer:**

Model quantization is the process of reducing the numerical precision of a model's weights (and optionally activations) from higher-precision formats (like FP32) to lower-precision formats (like FP16, INT8, or INT4). The goal is to reduce memory footprint, increase inference speed, and enable deployment on resource-constrained hardware — all while minimizing accuracy loss.

**Why it matters for LLMs:**

| Model Size | FP32 Memory | FP16 Memory | INT8 Memory | INT4 Memory |
|-----------|-------------|-------------|-------------|-------------|
| 7B params | 28 GB | 14 GB | 7 GB | 3.5 GB |
| 13B params | 52 GB | 26 GB | 13 GB | 6.5 GB |
| 70B params | 280 GB | 140 GB | 70 GB | 35 GB |

**Key benefits:**
- **Memory reduction**: 2-8x smaller model footprint
- **Speed increase**: 2-4x faster inference on compatible hardware
- **Cost savings**: Run larger models on cheaper GPUs (e.g., LLaMA-70B on a single A100 with INT4)
- **Edge deployment**: Run 7B models on consumer GPUs (RTX 3090, RTX 4090) or even CPUs

**Real-world example:**
```python
# Without quantization: LLaMA-2-70B needs 140GB VRAM (2x A100-80GB)
# With INT4 quantization: fits on a single A100-80GB (35GB)

from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# Load a 7B model in 4-bit — uses ~3.5GB instead of 14GB
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=quantization_config,
    device_map="auto",
)
# Model now consumes ~4GB VRAM instead of 14GB
```

---

### Q2: What are the differences between FP32, FP16, BF16, INT8, and INT4 data types?

**Answer:**

Each data type trades precision for memory efficiency:

| Data Type | Bits | Range | Precision | Memory (7B) | Use Case |
|-----------|------|-------|-----------|-------------|----------|
| **FP32** | 32 | ±3.4×10³⁸ | ~7 decimal digits | 28 GB | Training (gold standard) |
| **FP16** | 16 | ±65,504 | ~3.3 decimal digits | 14 GB | Mixed-precision training/inference |
| **BF16** | 16 | ±3.4×10³⁸ | ~2.4 decimal digits | 14 GB | Training on A100+, same range as FP32 |
| **INT8** | 8 | -128 to 127 | Integer only | 7 GB | Post-training quantization |
| **INT4** | 4 | -8 to 7 | Integer only | 3.5 GB | Aggressive quantization (GPTQ, AWQ) |
| **NF4** | 4 | Normalized float | Optimized for normal dist | 3.5 GB | QLoRA (bitsandbytes) |

**Key distinctions:**

1. **FP16 vs BF16**: BF16 has the same exponent range as FP32 (8 bits) but less mantissa precision (7 bits vs 10). This means BF16 rarely overflows/underflows during training, making it more stable than FP16 for training. FP16 has better precision but narrower range.

2. **INT8 vs INT4**: INT8 quantization typically preserves 99%+ of model quality. INT4 is more aggressive — quality depends heavily on the quantization method (GPTQ/AWQ preserve quality better than naive round-to-nearest).

3. **NF4 (Normal Float 4-bit)**: A special 4-bit format designed by Tim Dettmers for QLoRA. It's information-theoretically optimal for normally distributed weights, which neural network weights approximately are.

```python
import torch

# Demonstrating precision differences
value = 3.141592653589793

fp32 = torch.tensor(value, dtype=torch.float32)   # 3.1415927
fp16 = torch.tensor(value, dtype=torch.float16)   # 3.1406
bf16 = torch.tensor(value, dtype=torch.bfloat16)  # 3.1406

print(f"FP32: {fp32:.10f}")  # 3.1415927410
print(f"FP16: {fp16:.10f}")  # 3.1406250000
print(f"BF16: {bf16:.10f}")  # 3.1406250000

# BF16 advantage: handles large values without overflow
large_value = 100000.0
fp16_large = torch.tensor(large_value, dtype=torch.float16)  # inf (overflow!)
bf16_large = torch.tensor(large_value, dtype=torch.bfloat16) # 99840.0 (works)
```

---

### Q3: What is the difference between Post-Training Quantization (PTQ) and Quantization-Aware Training (QAT)?

**Answer:**

| Aspect | Post-Training Quantization (PTQ) | Quantization-Aware Training (QAT) |
|--------|----------------------------------|-----------------------------------|
| **When** | After training is complete | During training (or fine-tuning) |
| **Training required** | No (just calibration data) | Yes (full or partial training loop) |
| **Time** | Minutes to hours | Hours to days |
| **Quality** | Good for INT8, variable for INT4 | Best quality at any precision |
| **Cost** | Low (no GPU training needed) | High (requires full training setup) |
| **Examples** | GPTQ, AWQ, SmoothQuant, GGUF | QLoRA, LLM-QAT, PEFT-QAT |

**Post-Training Quantization (PTQ):**
- Takes a fully trained model and reduces precision after the fact
- Uses a small calibration dataset (128-1024 samples) to determine optimal quantization parameters
- GPTQ: Uses Hessian information to minimize quantization error layer-by-layer
- AWQ: Identifies "salient" weights (those with large activations) and protects them

```python
# PTQ Example: GPTQ quantization
from transformers import AutoModelForCausalLM, AutoTokenizer
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

# Step 1: Load the full-precision model
model_id = "meta-llama/Llama-2-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Step 2: Configure quantization
quantize_config = BaseQuantizeConfig(
    bits=4,                   # INT4 quantization
    group_size=128,           # Quantize in groups of 128 weights
    desc_act=False,           # Don't reorder by activation magnitude
    damp_percent=0.01,        # Dampening for Hessian stability
)

# Step 3: Load model for quantization
model = AutoGPTQForCausalLM.from_pretrained(model_id, quantize_config)

# Step 4: Prepare calibration data
calibration_data = [
    tokenizer(text, return_tensors="pt")
    for text in calibration_texts[:128]  # 128 samples typical
]

# Step 5: Run quantization (takes ~30 min for 7B on A100)
model.quantize(calibration_data)

# Step 6: Save quantized model
model.save_quantized("./llama-2-7b-gptq-4bit")
```

**Quantization-Aware Training (QAT):**
- Simulates quantization effects during training so the model learns to be robust to reduced precision
- Inserts "fake quantization" operations that round weights during forward pass but keep full precision for gradient computation
- Typically used as fine-tuning, not full pre-training

```python
# QAT Example: QLoRA (most popular QAT approach for LLMs)
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# Load base model in 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# Add LoRA adapters (trainable params on top of frozen quantized base)
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Output: trainable params: 4,194,304 || all params: 3,504,607,232 || trainable%: 0.12%
```

---

### Q4: What is GPTQ and how does it work at a high level?

**Answer:**

**GPTQ (Generative Pre-trained Transformer Quantization)** is a one-shot, post-training quantization method designed specifically for large language models. It was introduced in the paper "GPTQ: Accurate Post-Training Quantization for Generative Pre-Trained Transformers" (Frantar et al., 2023).

**How it works (high level):**

1. **Layer-by-layer**: Processes one transformer layer at a time, keeping the rest in full precision
2. **Hessian-based**: Uses second-order information (Hessian matrix) to determine which weights are most important
3. **Optimal Brain Quantizer**: Based on the OBQ framework — quantizes weights in order of increasing Hessian diagonal, compensating remaining weights for each quantized weight
4. **Lazy batching**: Processes weights in blocks of 128 (group_size) for efficiency

**GPTQ pipeline:**
1. Run calibration data through the model to collect activation statistics
2. For each layer:
   - Compute the Hessian matrix `H = 2 * X^T * X` (where X is the layer's input activations)
   - For each column of weights (in Hessian-determined order):
     - Quantize the weight to the nearest INT4/INT8 value
     - Compute the quantization error
     - Distribute the error to remaining unquantized weights using Hessian information
3. Save quantized weights + quantization parameters (scales, zero-points)

**Key parameters:**
- `bits`: Target precision (typically 4 or 8)
- `group_size`: Number of weights that share quantization parameters (128 is standard)
- `desc_act`: Whether to reorder weights by activation magnitude (better quality, slower)
- `damp_percent`: Dampening factor for numerical stability (0.01 default)

```python
# Using a pre-quantized GPTQ model
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-GPTQ",
    device_map="auto",
    trust_remote_code=False,
    revision="main",
)
tokenizer = AutoTokenizer.from_pretrained("TheBloke/Llama-2-7B-GPTQ")

prompt = "Explain quantum computing in simple terms:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=256)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

### Q5: When should you quantize a model, and when should you NOT?

**Answer:**

**When to quantize:**

| Scenario | Recommended Approach |
|----------|---------------------|
| Deploying LLMs on consumer GPUs (RTX 3090/4090) | INT4 (GPTQ/AWQ) or GGUF |
| Reducing cloud inference costs | INT8 (SmoothQuant) or INT4 (AWQ) |
| Serving models on CPU | GGUF (llama.cpp) with Q4_K_M or Q5_K_S |
| Fine-tuning large models on limited VRAM | QLoRA (NF4 + LoRA adapters) |
| Batch inference with high throughput needs | INT4/INT8 with vLLM or TGI |
| Edge/mobile deployment | INT4 with ONNX Runtime or TFLite |

**When NOT to quantize:**

| Scenario | Reason |
|----------|--------|
| Training from scratch | Quantization degrades gradient precision |
| Tasks requiring maximum precision (math, coding) | INT4 can noticeably hurt reasoning quality |
| Small models (< 1B params) | Small models are more sensitive to quantization error |
| When you have abundant GPU memory | FP16/BF16 gives best quality with no effort |
| Evaluation/benchmarking | Always benchmark in full precision first |
| Embedding models | Quantization can significantly degrade embedding quality |

**Decision framework:**
```
Model size > available VRAM?
├── YES → Quantize (GPTQ/AWQ for GPU, GGUF for CPU)
├── NO, but want faster inference → Try INT8 (minimal quality loss)
└── NO, quality is paramount → Stay at FP16/BF16

Need to fine-tune?
├── YES, limited VRAM → QLoRA (4-bit base + LoRA)
├── YES, enough VRAM → Full fine-tune or LoRA at FP16
└── NO → PTQ (GPTQ or AWQ)
```

**Quality impact by method (LLaMA-2-7B, perplexity on WikiText-2):**

| Method | Bits | Perplexity | Delta from FP16 |
|--------|------|-----------|-----------------|
| FP16 (baseline) | 16 | 5.47 | — |
| GPTQ | 4 | 5.63 | +0.16 (+2.9%) |
| AWQ | 4 | 5.60 | +0.13 (+2.4%) |
| GGUF Q4_K_M | 4 | 5.68 | +0.21 (+3.8%) |
| Round-to-nearest | 4 | 6.85 | +1.38 (+25.2%) |
| bitsandbytes NF4 | 4 | 5.70 | +0.23 (+4.2%) |

---

## Intermediate Level

### Q6: How does the AWQ (Activation-Aware Weight Quantization) algorithm work, and why is it often preferred over GPTQ?

**Answer:**

**AWQ** is a post-training quantization method introduced by MIT (Lin et al., 2023). Its key insight is: **not all weights are equally important — weights connected to channels with large activations are critical and should be quantized more carefully.**

**Core algorithm:**

1. **Observe activations**: Run calibration data and measure the magnitude of activations per channel
2. **Identify salient channels**: Channels with large activation magnitudes are "salient" — quantizing their corresponding weights carelessly causes large output errors
3. **Per-channel scaling**: Instead of mixed-precision (which hurts hardware efficiency), AWQ scales salient weight channels UP before quantization, then scales DOWN during inference. This reduces relative quantization error for important weights.
4. **Grid search**: Optimal scaling factors are found via grid search to minimize quantization error

**Mathematical intuition:**
```
Quantization error for weight w: |Q(w) - w| ≈ Δ (quantization step size)
Output error: ||Q(w·x) - w·x|| ∝ Δ · ||x||

For salient channels (large ||x||), the output error is amplified.
AWQ multiplies w by s (scale > 1) before quantization:
  Q(s·w) / s → relative error = Δ/(s·w) (smaller for larger s)
But activations are divided by s, reducing ||x/s||.
Net effect: better preservation of important channels.
```

**Why AWQ is often preferred over GPTQ:**

| Aspect | AWQ | GPTQ |
|--------|-----|------|
| Speed of quantization | Faster (no Hessian computation) | Slower (Hessian per layer) |
| Calibration data needed | ~128 samples | ~128 samples |
| Inference quality (4-bit) | Slightly better perplexity | Very good |
| Quantization time (7B) | ~10 min | ~30 min |
| Hardware compatibility | Excellent (simple INT4 kernels) | Good |
| vLLM integration | First-class support | Supported |
| Reordering needed | No | Optional (desc_act) |

```python
# AWQ Quantization with AutoAWQ
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = "meta-llama/Llama-2-7b-hf"
quant_path = "llama-2-7b-awq"

# Load model
model = AutoAWQForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# Configure AWQ
quant_config = {
    "zero_point": True,      # Asymmetric quantization
    "q_group_size": 128,     # Group size
    "w_bit": 4,              # 4-bit weights
    "version": "GEMM",       # Use GEMM kernels (fastest on NVIDIA)
}

# Quantize (searches for optimal per-channel scales)
model.quantize(tokenizer, quant_config=quant_config)

# Save
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)

# Load and use quantized model
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    quant_path,
    device_map="auto",
)
```

---

### Q7: Explain GPTQ internals — how does the Hessian-based approach minimize quantization error?

**Answer:**

GPTQ extends the **Optimal Brain Quantizer (OBQ)** framework to be practical for billion-parameter models. Here's the detailed internal workings:

**Step 1: Problem formulation**
For each linear layer with weight matrix `W` and input activations `X`, quantization aims to minimize:

$$\min_{\hat{W}} ||WX - \hat{W}X||_2^2$$

where $\hat{W}$ is the quantized weight matrix.

**Step 2: Hessian matrix**
The Hessian of the above objective with respect to W is:

$$H = 2X X^T$$

This captures how sensitive the layer output is to changes in each weight. Diagonal elements `H_{ii}` tell us how much the quantization error of weight `w_i` affects the output.

**Step 3: Column-wise quantization with error compensation**
GPTQ processes weights column by column (or in blocks):

```
For each column j (or block of columns):
    1. Quantize w_j to nearest INT4/INT8 value: ŵ_j = quant(w_j)
    2. Compute quantization error: δ_j = w_j - ŵ_j
    3. Compensate remaining columns:
       w_{j+1:} = w_{j+1:} - δ_j · (H_{j,j+1:} / H_{j,j})
```

The compensation step (3) is the key innovation — it adjusts not-yet-quantized weights to account for the error introduced by quantizing `w_j`. The Hessian provides the optimal adjustment direction.

**Step 4: Lazy batch updates (for efficiency)**
Instead of updating ALL remaining weights after each quantization:
- Process weights in blocks of `group_size` (128)
- Accumulate compensations within the block
- Apply accumulated updates to remaining blocks
- This reduces memory access from O(d²) per weight to O(d × group_size)

**Step 5: Cholesky-based inverse**
Computing `H⁻¹` directly is expensive. GPTQ uses the Cholesky decomposition:
- `H = LL^T` (Cholesky factorization)
- Row updates via forward/back substitution
- Dampening: `H += λI` for numerical stability (default λ = 0.01 × mean(diag(H)))

```python
# Simplified GPTQ core algorithm (pseudocode)
import torch

def gptq_quantize_layer(W, X, bits=4, group_size=128, damp=0.01):
    """
    W: weight matrix [out_features, in_features]
    X: calibration activations [n_samples, in_features]
    """
    n_cols = W.shape[1]

    # Step 1: Compute Hessian
    H = 2 * X.T @ X  # [in_features, in_features]

    # Dampening for stability
    diag_mean = torch.mean(torch.diag(H))
    H += damp * diag_mean * torch.eye(n_cols)

    # Step 2: Cholesky inverse
    H_inv = torch.linalg.cholesky(H)
    H_inv = torch.cholesky_inverse(H_inv)

    # Step 3: Column-wise quantization
    Q = torch.zeros_like(W)  # Quantized weights

    for block_start in range(0, n_cols, group_size):
        block_end = min(block_start + group_size, n_cols)

        # Work on this block
        W_block = W[:, block_start:block_end].clone()

        for j in range(block_start, block_end):
            # Quantize single weight column
            w_j = W[:, j]
            q_j = quantize_to_int(w_j, bits)  # Round to nearest
            Q[:, j] = q_j

            # Error
            err_j = (w_j - q_j) / H_inv[j, j]

            # Compensate remaining columns in block
            W[:, j+1:block_end] -= err_j.unsqueeze(1) * H_inv[j, j+1:block_end].unsqueeze(0)

        # Apply accumulated error to remaining columns outside block
        # (lazy batch update)
        W[:, block_end:] -= (W[:, block_start:block_end] - Q[:, block_start:block_end]) @ H_inv[block_start:block_end, block_end:]

    return Q

def quantize_to_int(w, bits):
    """Symmetric round-to-nearest quantization."""
    max_val = w.abs().max()
    scale = max_val / (2 ** (bits - 1) - 1)
    return torch.round(w / scale) * scale
```

---

### Q8: What is the NF4 (Normal Float 4-bit) data type used in QLoRA, and why is it better than standard INT4?

**Answer:**

**NF4 (4-bit NormalFloat)** is a data type designed by Tim Dettmers specifically for quantizing neural network weights. It's the default quantization format in QLoRA and bitsandbytes.

**Key insight:** Neural network weights follow approximately normal distributions. Standard INT4 uniformly spaces quantization levels across the range, wasting precision on rarely-occurring extreme values. NF4 spaces levels according to the normal distribution's quantiles.

**How NF4 works:**

1. **Normalize weights**: Each block of weights is normalized to have zero mean and unit variance
2. **Map to quantiles**: The 16 NF4 levels (4 bits = 2⁴ = 16 values) are placed at the quantiles of the standard normal distribution
3. **Assign levels**: Each weight is mapped to its nearest NF4 level

**NF4 quantization levels:**
```
NF4 values (16 levels, normalized to [-1, 1]):
[-1.0, -0.6962, -0.5251, -0.3949, -0.2844, -0.1848, -0.0911, 0.0,
  0.0796,  0.1609,  0.2461,  0.3379,  0.4407,  0.5626,  0.7230, 1.0]
```

Notice: levels are denser near 0 (where most weights cluster) and sparser at extremes (where few weights exist). This is information-theoretically optimal for normally distributed data.

**Comparison with standard INT4:**
```
INT4 levels (uniform spacing):
[-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]
→ Equal spacing wastes precision: many levels in tail regions with few weights

NF4 levels (normal-distribution-aware):
→ More levels near center (where most weights are)
→ Fewer levels in tails (where few weights are)
→ Result: lower mean quantization error
```

**Double quantization (nested quantization):**
QLoRA uses "double quantization" on top of NF4:
- First: Quantize weights to NF4 with FP32 scales (one scale per block of 64 weights)
- Second: Quantize the FP32 scales themselves to FP8
- Savings: reduces scale overhead from 0.5 bits/param → 0.127 bits/param

```python
# QLoRA with NF4 + double quantization
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",          # NF4 data type (vs "fp4" alternative)
    bnb_4bit_compute_dtype=torch.bfloat16,  # Compute in BF16 (dequantize on-the-fly)
    bnb_4bit_use_double_quant=True,      # Quantize the quantization constants too
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-13b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# Memory usage comparison (13B model):
# FP32:  ~52 GB
# FP16:  ~26 GB
# NF4:   ~7.3 GB (with double quant)
# INT4:  ~7.8 GB (without double quant)

# NF4 saves ~0.5 GB over INT4 for 13B model, and quality is measurably better
```

**Perplexity comparison (LLaMA-7B, WikiText-2):**

| Method | Bits | Perplexity | Memory |
|--------|------|-----------|--------|
| FP16 | 16 | 5.47 | 14 GB |
| NF4 (QLoRA) | 4 | 5.70 | 3.8 GB |
| FP4 (bitsandbytes) | 4 | 5.81 | 3.8 GB |
| INT4 (round-to-nearest) | 4 | 6.85 | 3.5 GB |

NF4 achieves the best quality among 4-bit formats because it's optimized for the actual weight distribution.

---

### Q9: How does mixed-precision inference work, and when would you use it instead of full quantization?

**Answer:**

**Mixed-precision inference** runs different parts of the model at different precisions. Instead of quantizing the entire model uniformly to INT4, sensitive layers stay at higher precision (FP16/BF16) while others are quantized.

**Why mixed precision:**
- Some layers are more sensitive to quantization than others
- First and last layers (embedding, LM head) are typically most sensitive
- Attention layers often need higher precision than FFN layers
- Mixed precision balances quality and efficiency

**Common mixed-precision patterns:**

| Pattern | Description | Example |
|---------|-------------|---------|
| **W4A16** | Weights in INT4, activations in FP16 | GPTQ, AWQ |
| **W8A8** | Both weights and activations in INT8 | SmoothQuant |
| **W4A16 + FP16 outliers** | INT4 weights, but FP16 for outlier channels | LLM.int8() |
| **Layer-wise mixing** | Critical layers in FP16, rest in INT4 | Custom configs |

**LLM.int8() (bitsandbytes) — The OG mixed-precision approach:**

The key insight from Tim Dettmers: LLM activations have "outlier features" — a few channels with magnitudes 10-100x larger than the rest. Quantizing these channels to INT8 causes massive errors.

Solution: Separate outlier channels and process them in FP16:
```
For each layer:
  1. Identify outlier features (|activation| > threshold, e.g., 6.0)
  2. Split into: regular channels (INT8) + outlier channels (FP16)
  3. Matrix multiply separately:
     output = INT8_matmul(W_regular, X_regular) + FP16_matmul(W_outlier, X_outlier)
  4. Combine results
```

```python
# Mixed-precision INT8 with outlier decomposition
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# INT8 with automatic outlier detection
config_8bit = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,        # Outlier threshold
    llm_int8_has_fp16_weight=False, # Keep weights in INT8
)

model_8bit = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=config_8bit,
    device_map="auto",
)
# ~7.5 GB VRAM (INT8 weights + FP16 outlier channels)

# SmoothQuant approach (W8A8 - quantizes both weights AND activations)
# Used by: TensorRT-LLM, vLLM (via FP8)
# Key idea: migrate quantization difficulty from activations to weights
#   W * X = (W * s) * (X / s)  where s is per-channel smoothing factor
#   Activations X/s become easier to quantize
#   Weights W*s become slightly harder, but weights are easier to quantize anyway
```

**When to use mixed-precision vs full quantization:**

| Scenario | Approach |
|----------|----------|
| Maximum quality needed | Mixed precision (LLM.int8() or W4A16 + FP16 heads) |
| Maximum speed needed | Full INT4 (GPTQ/AWQ with all layers quantized) |
| Serving 70B+ models | W4A16 (AWQ/GPTQ) — quality is still very good |
| Fine-tuning | QLoRA NF4 + FP16 LoRA adapters (inherently mixed precision) |
| Embedding models | FP16 or INT8 at most (embeddings degrade fast at INT4) |

---

### Q10: What is a calibration dataset, and how do you choose one for quantization?

**Answer:**

A **calibration dataset** is a small set of representative inputs used during post-training quantization (GPTQ, AWQ, SmoothQuant) to determine optimal quantization parameters (scales, zero-points, and compensation factors).

**Why calibration matters:**
- Quantization methods need to observe real activation patterns to make smart decisions
- GPTQ uses calibration to compute the Hessian (`H = 2X^TX`)
- AWQ uses it to identify salient channels (high-activation-magnitude channels)
- Bad calibration → poor quantization parameters → model quality drops

**Best practices for calibration datasets:**

| Rule | Explanation |
|------|-------------|
| **128-256 samples** | More doesn't help much; GPTQ diminishing returns after 128 |
| **Representative of deployment** | If model will serve coding tasks, use code samples |
| **Diverse** | Mix of different topics, lengths, and styles |
| **Not the eval set** | Don't calibrate on your benchmark data (overfitting risk) |
| **Reasonable length** | 512-2048 tokens per sample (match deployment context) |

**Common calibration datasets:**

| Dataset | Best For | Why |
|---------|----------|-----|
| C4 (en, train) | General purpose | Default for most GPTQ/AWQ quantizations |
| WikiText-2 (train) | General text | Clean, well-structured text |
| The Pile (subset) | Multi-domain models | Diverse: code, books, web, papers |
| Custom domain data | Specialized models | Best quality for specific domains |

```python
# Preparing calibration data for GPTQ
from datasets import load_dataset
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# Option 1: C4 dataset (most common default)
dataset = load_dataset("allenai/c4", "en", split="train", streaming=True)
calibration_data = []
for i, example in enumerate(dataset):
    if i >= 128:
        break
    tokenized = tokenizer(
        example["text"],
        return_tensors="pt",
        max_length=2048,
        truncation=True,
    )
    calibration_data.append(tokenized)

# Option 2: Custom domain-specific calibration
# For a coding model, use code samples:
code_samples = [
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "import pandas as pd\ndf = pd.read_csv('data.csv')\ndf.groupby('category').mean()",
    # ... 126 more diverse code samples
]
calibration_data = [
    tokenizer(code, return_tensors="pt", max_length=2048, truncation=True)
    for code in code_samples
]

# Option 3: Using GPTQ's built-in calibration loader
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from auto_gptq.utils import get_calib_dataset

# Built-in helper for common datasets
calibration_data = get_calib_dataset(
    "c4",                    # Dataset name
    tokenizer=tokenizer,
    n_samples=128,           # Number of samples
    block_size=2048,         # Sequence length
)
```

**Calibration experiment — impact of dataset choice (LLaMA-2-7B, GPTQ 4-bit):**

| Calibration Source | WikiText-2 PPL | HumanEval Pass@1 | MMLU 5-shot |
|-------------------|----------------|-------------------|-------------|
| C4 (default) | 5.63 | 12.8% | 45.2% |
| WikiText-2 train | 5.58 | 12.1% | 44.8% |
| The Pile | 5.65 | 13.0% | 45.5% |
| Code-only | 5.91 | 14.2% | 43.1% |
| Random noise | 7.23 | 8.5% | 38.2% |

Takeaway: C4 or The Pile work well as general-purpose calibration. Domain-specific calibration helps for that domain but can hurt general quality. Random/bad calibration is clearly harmful.

---

## Advanced Level

### Q11: Walk through the complete GPTQ-for-LLaMA workflow from raw model to production deployment.

**Answer:**

Here's the end-to-end workflow for quantizing a LLaMA model with GPTQ and deploying it with vLLM:

**Phase 1: Quantization**

```python
#!/usr/bin/env python3
"""Full GPTQ quantization pipeline for LLaMA models."""

from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer
from datasets import load_dataset
import torch
import time
import os

# ============================================================
# Step 1: Configuration
# ============================================================
MODEL_ID = "meta-llama/Llama-2-70b-hf"
OUTPUT_DIR = "./models/llama-2-70b-gptq-4bit"
BITS = 4
GROUP_SIZE = 128
N_CALIBRATION_SAMPLES = 128
MAX_SEQ_LEN = 2048

# ============================================================
# Step 2: Load tokenizer and prepare calibration data
# ============================================================
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token

# Load C4 calibration data
print("Loading calibration data...")
dataset = load_dataset("allenai/c4", "en", split="train", streaming=True)
calibration_texts = []
for i, example in enumerate(dataset):
    if i >= N_CALIBRATION_SAMPLES:
        break
    if len(example["text"]) > 100:  # Filter very short texts
        calibration_texts.append(example["text"])

calibration_data = [
    tokenizer(text, return_tensors="pt", max_length=MAX_SEQ_LEN, truncation=True)
    for text in calibration_texts
]
print(f"Prepared {len(calibration_data)} calibration samples")

# ============================================================
# Step 3: Configure GPTQ quantization
# ============================================================
quantize_config = BaseQuantizeConfig(
    bits=BITS,
    group_size=GROUP_SIZE,
    desc_act=False,         # True = better quality, 2x slower quant, some inference overhead
    damp_percent=0.01,      # Hessian dampening
    sym=True,               # Symmetric quantization (simpler kernels)
    true_sequential=True,   # Process layers in order (better quality)
    model_seqlen=MAX_SEQ_LEN,
)

# ============================================================
# Step 4: Load model and quantize
# ============================================================
print(f"Loading {MODEL_ID} for quantization...")
model = AutoGPTQForCausalLM.from_pretrained(
    MODEL_ID,
    quantize_config=quantize_config,
    torch_dtype=torch.float16,
    # For 70B, you need significant RAM (~140GB) during quantization
    max_memory={0: "40GiB", 1: "40GiB", "cpu": "100GiB"},
)

print("Starting quantization...")
start_time = time.time()
model.quantize(
    calibration_data,
    batch_size=1,           # Increase if you have more VRAM
)
quant_time = time.time() - start_time
print(f"Quantization completed in {quant_time/60:.1f} minutes")

# ============================================================
# Step 5: Save quantized model
# ============================================================
print(f"Saving to {OUTPUT_DIR}...")
model.save_quantized(OUTPUT_DIR, use_safetensors=True)
tokenizer.save_pretrained(OUTPUT_DIR)

# Verify file sizes
total_size = 0
for f in os.listdir(OUTPUT_DIR):
    size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
    total_size += size
    if size > 1e6:
        print(f"  {f}: {size/1e9:.2f} GB")
print(f"Total quantized model size: {total_size/1e9:.2f} GB")
# Expected: ~35GB for 70B model (down from ~140GB)
```

**Phase 2: Validation**

```python
# Validate quantized model quality
from transformers import AutoModelForCausalLM, AutoTokenizer
from lm_eval import evaluator, tasks

# Load quantized model
model = AutoModelForCausalLM.from_pretrained(
    OUTPUT_DIR,
    device_map="auto",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(OUTPUT_DIR)

# Quick perplexity check
from datasets import load_dataset
import torch

eval_data = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
eval_text = "\n\n".join(eval_data["text"])
encodings = tokenizer(eval_text, return_tensors="pt", truncation=True, max_length=4096)

with torch.no_grad():
    outputs = model(encodings.input_ids.to(model.device), labels=encodings.input_ids.to(model.device))
    perplexity = torch.exp(outputs.loss)
    print(f"WikiText-2 Perplexity: {perplexity.item():.2f}")

# Full benchmark with lm-evaluation-harness
results = evaluator.simple_evaluate(
    model="hf",
    model_args=f"pretrained={OUTPUT_DIR}",
    tasks=["hellaswag", "winogrande", "arc_easy", "mmlu"],
    num_fewshot=5,
    batch_size="auto",
)
for task, metrics in results["results"].items():
    print(f"  {task}: {metrics}")
```

**Phase 3: Production deployment with vLLM**

```python
# Serve with vLLM for production inference
# Terminal command:
"""
python -m vllm.entrypoints.openai.api_server \
    --model ./models/llama-2-70b-gptq-4bit \
    --quantization gptq \
    --tensor-parallel-size 2 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.90 \
    --port 8000 \
    --host 0.0.0.0
"""

# Client usage (OpenAI-compatible API)
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed",
)

response = client.chat.completions.create(
    model="./models/llama-2-70b-gptq-4bit",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    max_tokens=512,
    temperature=0.7,
)
print(response.choices[0].message.content)

# Batch inference for throughput testing
import asyncio
import aiohttp
import time

async def benchmark_throughput(n_requests=100, concurrency=10):
    """Benchmark vLLM throughput with quantized model."""
    url = "http://localhost:8000/v1/completions"

    prompts = [f"Write a short paragraph about topic {i}:" for i in range(n_requests)]

    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def make_request(prompt):
        async with semaphore:
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={
                    "model": "./models/llama-2-70b-gptq-4bit",
                    "prompt": prompt,
                    "max_tokens": 128,
                    "temperature": 0.7,
                }) as resp:
                    result = await resp.json()
                    latency = time.time() - start
                    tokens = result["usage"]["completion_tokens"]
                    results.append({"latency": latency, "tokens": tokens})

    overall_start = time.time()
    await asyncio.gather(*[make_request(p) for p in prompts])
    overall_time = time.time() - overall_start

    total_tokens = sum(r["tokens"] for r in results)
    avg_latency = sum(r["latency"] for r in results) / len(results)

    print(f"Total requests: {n_requests}")
    print(f"Total time: {overall_time:.2f}s")
    print(f"Throughput: {total_tokens/overall_time:.1f} tokens/sec")
    print(f"Avg latency: {avg_latency:.2f}s")
    print(f"Requests/sec: {n_requests/overall_time:.1f}")

asyncio.run(benchmark_throughput())
```

---

### Q12: Compare AWQ vs GPTQ vs GGUF with benchmark data. When would you choose each?

**Answer:**

**Comprehensive benchmark comparison (LLaMA-2-7B):**

| Metric | AWQ (4-bit) | GPTQ (4-bit) | GGUF Q4_K_M | GGUF Q5_K_S | FP16 (baseline) |
|--------|------------|--------------|-------------|-------------|-----------------|
| **WikiText-2 PPL** | 5.60 | 5.63 | 5.68 | 5.54 | 5.47 |
| **MMLU (5-shot)** | 45.5% | 45.2% | 44.8% | 45.6% | 46.1% |
| **HumanEval Pass@1** | 13.1% | 12.8% | 12.2% | 13.0% | 14.0% |
| **Model size** | 3.9 GB | 3.9 GB | 4.1 GB | 4.9 GB | 13.5 GB |
| **GPU VRAM (idle)** | 4.2 GB | 4.3 GB | N/A (CPU) | N/A (CPU) | 14.0 GB |
| **GPU tokens/sec** | 105 | 95 | N/A | N/A | 52 |
| **CPU tokens/sec** | N/A | N/A | 22 | 18 | 2 |
| **Quantization time** | ~10 min | ~30 min | ~5 min | ~5 min | N/A |
| **GPU required for quant** | Yes | Yes | No (CPU ok) | No (CPU ok) | N/A |

**Benchmark for larger models (LLaMA-2-70B):**

| Metric | AWQ (4-bit) | GPTQ (4-bit) | GGUF Q4_K_M |
|--------|------------|--------------|-------------|
| **Model size** | 35 GB | 35 GB | 40 GB |
| **VRAM needed** | 38 GB | 40 GB | 0 (CPU) / 24+ (GPU offload) |
| **GPU tokens/sec (A100)** | 48 | 42 | N/A |
| **CPU tokens/sec (M2 Ultra)** | N/A | N/A | 12 |
| **vLLM compatible** | ✅ First-class | ✅ Supported | ❌ (llama.cpp only) |
| **TGI compatible** | ✅ | ✅ | ❌ |

**Decision matrix — which format to choose:**

```
What's your deployment target?
│
├── GPU Server (A100, H100, L40S)
│   ├── Need maximum throughput → AWQ + vLLM
│   ├── Need maximum quality → GPTQ (desc_act=True) + vLLM
│   └── Need fine-tuning → bitsandbytes NF4 (QLoRA)
│
├── Consumer GPU (RTX 3090, 4090, Apple M-series)
│   ├── 24GB VRAM → AWQ or GPTQ for models up to 13B
│   ├── 16GB VRAM → GGUF Q4_K_M with GPU offload
│   └── 8GB VRAM → GGUF Q3_K_M or Q2_K
│
├── CPU Only (Intel, AMD)
│   ├── Maximum speed → GGUF Q4_K_M (best speed/quality)
│   ├── Maximum quality → GGUF Q5_K_S or Q6_K
│   └── Minimum memory → GGUF Q2_K (significant quality loss)
│
└── Mobile / Edge
    └── GGUF Q4_0 via llama.cpp (smallest, fastest)
```

**GGUF quantization variants explained:**

```python
# llama.cpp GGUF conversion and quantization
"""
# Step 1: Convert from HuggingFace format to GGUF
python convert_hf_to_gguf.py meta-llama/Llama-2-7b-hf --outtype f16

# Step 2: Quantize to desired format
./llama-quantize models/llama-2-7b-f16.gguf models/llama-2-7b-Q4_K_M.gguf Q4_K_M
"""

# GGUF quantization types (from highest to lowest quality):
GGUF_TYPES = {
    "Q8_0":   {"bits": 8.5, "quality": "~FP16",     "size_7b": "7.2 GB"},
    "Q6_K":   {"bits": 6.6, "quality": "Excellent",  "size_7b": "5.5 GB"},
    "Q5_K_S": {"bits": 5.5, "quality": "Very good",  "size_7b": "4.8 GB"},
    "Q5_K_M": {"bits": 5.7, "quality": "Very good+", "size_7b": "4.9 GB"},
    "Q4_K_M": {"bits": 4.8, "quality": "Good",       "size_7b": "4.1 GB"},  # Best balance
    "Q4_K_S": {"bits": 4.6, "quality": "Good-",      "size_7b": "3.9 GB"},
    "Q3_K_M": {"bits": 3.9, "quality": "Acceptable", "size_7b": "3.3 GB"},
    "Q3_K_S": {"bits": 3.5, "quality": "Fair",       "size_7b": "3.0 GB"},
    "Q2_K":   {"bits": 2.6, "quality": "Poor",       "size_7b": "2.3 GB"},  # Not recommended
}

# K-quant (K_M, K_S) variants: K = "k-quant" method (importance-weighted)
# M = medium (mix of INT4 and INT5/INT6 for important layers)
# S = small (more aggressive, slightly lower quality)
# Attention layers get higher precision, FFN layers get lower precision
```

**Practical deployment comparison:**

```python
# AWQ with vLLM (GPU — maximum throughput)
"""
pip install vllm autoawq
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-7B-AWQ \
    --quantization awq \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9
"""

# GPTQ with vLLM (GPU — maximum quality 4-bit)
"""
pip install vllm auto-gptq
python -m vllm.entrypoints.openai.api_server \
    --model TheBloke/Llama-2-7B-GPTQ \
    --quantization gptq \
    --max-model-len 4096
"""

# GGUF with llama.cpp (CPU/hybrid — most flexible)
"""
# CPU-only inference
./llama-server -m models/llama-2-7b-Q4_K_M.gguf \
    -c 4096 -t 8 --port 8080

# GPU-offloaded (put N layers on GPU, rest on CPU)
./llama-server -m models/llama-2-7b-Q4_K_M.gguf \
    -c 4096 -ngl 33 --port 8080
"""
```

---

### Q13: How would you implement quantization-aware training (QAT) for a large language model?

**Answer:**

QAT for LLMs is fundamentally different from traditional QAT (used in vision models). Due to the enormous cost of full training, LLM-QAT typically means one of:

1. **QLoRA** (most practical): Freeze quantized base model, train LoRA adapters at full precision
2. **LLM-QAT** (Meta, 2023): Full QAT with data-free distillation
3. **PEFT-QAT**: Quantize + train subset of parameters

**Approach 1: QLoRA (most practical, widely used)**

```python
"""
QLoRA: Quantized Low-Rank Adaptation
- Base model frozen at NF4 (4-bit)
- LoRA adapters trained at BF16 (16-bit)
- Gradients flow through frozen quantized layers via straight-through estimator
"""
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset

# ===============================
# Step 1: Load model in 4-bit
# ===============================
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer.pad_token = tokenizer.eos_token

# ===============================
# Step 2: Prepare for QLoRA
# ===============================
model = prepare_model_for_kbit_training(model)
# This does:
# - Enables gradient checkpointing
# - Casts layernorm to FP32 for stability
# - Enables input gradients

# ===============================
# Step 3: Configure LoRA adapters
# ===============================
lora_config = LoraConfig(
    r=64,                        # Rank (higher = more capacity, more params)
    lora_alpha=128,              # Scaling factor (alpha/r = scaling)
    target_modules=[             # Which modules get LoRA adapters
        "q_proj", "k_proj", "v_proj", "o_proj",  # Attention
        "gate_proj", "up_proj", "down_proj",       # FFN (MLP)
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 167,772,160 || all params: 3,668,873,216 || trainable%: 4.57%

# ===============================
# Step 4: Training configuration
# ===============================
training_args = TrainingArguments(
    output_dir="./llama-2-7b-qlora",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    bf16=True,
    logging_steps=10,
    save_strategy="steps",
    save_steps=100,
    optim="paged_adamw_8bit",  # 8-bit Adam (saves VRAM)
    gradient_checkpointing=True,
    max_grad_norm=0.3,
    group_by_length=True,
)

# ===============================
# Step 5: Train with SFTTrainer
# ===============================
dataset = load_dataset("tatsu-lab/alpaca", split="train")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=2048,
    dataset_text_field="text",
    packing=True,  # Pack multiple short samples into one sequence
)

trainer.train()

# ===============================
# Step 6: Save and merge for deployment
# ===============================
# Option A: Save LoRA adapters separately (small, ~300MB)
trainer.save_model("./llama-2-7b-qlora/adapter")

# Option B: Merge adapters into base model for deployment
from peft import AutoPeftModelForCausalLM

merged_model = AutoPeftModelForCausalLM.from_pretrained(
    "./llama-2-7b-qlora/adapter",
    device_map="auto",
    torch_dtype=torch.float16,
)
merged_model = merged_model.merge_and_unload()
merged_model.save_pretrained("./llama-2-7b-qlora-merged")

# Then quantize the merged model with GPTQ or AWQ for deployment
```

**Approach 2: LLM-QAT (Full quantization-aware training)**

```python
"""
LLM-QAT (Meta, 2023): True quantization-aware training for LLMs
Paper: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models"

Key innovation: Uses the model itself to generate training data (data-free distillation)
- No labeled data needed
- Teacher = original FP16 model
- Student = same model with fake-quantization operators inserted
"""

# Conceptual implementation (simplified)
import torch
import torch.nn as nn

class FakeQuantize(torch.autograd.Function):
    """Simulates quantization during training with straight-through estimator."""

    @staticmethod
    def forward(ctx, x, scale, zero_point, quant_min, quant_max):
        # Quantize
        x_int = torch.round(x / scale + zero_point)
        x_int = torch.clamp(x_int, quant_min, quant_max)
        # Dequantize
        x_quant = (x_int - zero_point) * scale
        return x_quant

    @staticmethod
    def backward(ctx, grad_output):
        # Straight-through estimator: pass gradients unchanged
        return grad_output, None, None, None, None


class QATLinear(nn.Module):
    """Linear layer with fake quantization for QAT."""

    def __init__(self, linear_layer, bits=4):
        super().__init__()
        self.linear = linear_layer
        self.bits = bits
        self.quant_min = -(2 ** (bits - 1))
        self.quant_max = 2 ** (bits - 1) - 1

        # Learnable quantization parameters
        self.weight_scale = nn.Parameter(torch.ones(1))
        self.weight_zero_point = nn.Parameter(torch.zeros(1))

    def forward(self, x):
        # Fake-quantize weights during forward pass
        w_quant = FakeQuantize.apply(
            self.linear.weight,
            self.weight_scale,
            self.weight_zero_point,
            self.quant_min,
            self.quant_max,
        )
        return nn.functional.linear(x, w_quant, self.linear.bias)


# Training loop for LLM-QAT
def train_llm_qat(teacher_model, student_model, tokenizer, n_steps=1000):
    """
    Data-free QAT: teacher generates data, student learns to match.
    """
    optimizer = torch.optim.AdamW(student_model.parameters(), lr=1e-5)
    kl_loss = nn.KLDivLoss(reduction="batchmean", log_target=True)

    for step in range(n_steps):
        # Generate data using teacher (data-free)
        prompt_ids = torch.randint(0, tokenizer.vocab_size, (4, 32))  # Random prompts

        with torch.no_grad():
            teacher_outputs = teacher_model(prompt_ids)
            teacher_logits = teacher_outputs.logits

        # Student forward with fake quantization
        student_outputs = student_model(prompt_ids)
        student_logits = student_outputs.logits

        # KL divergence loss (match teacher's output distribution)
        loss = kl_loss(
            torch.log_softmax(student_logits / 2.0, dim=-1),  # temperature=2
            torch.log_softmax(teacher_logits / 2.0, dim=-1),
        )

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if step % 100 == 0:
            print(f"Step {step}, Loss: {loss.item():.4f}")
```

---

### Q14: What are FP6 and FP4 formats, and how do they compare to integer quantization (INT4/INT8)?

**Answer:**

**FP6 and FP4** are floating-point formats with very few bits, offering an alternative to integer quantization. Unlike INT4/INT8 which have uniform spacing between values, floating-point formats have non-uniform spacing (denser near zero, sparser at extremes).

**Format breakdown:**

| Format | Sign | Exponent | Mantissa | Values | Dynamic Range |
|--------|------|----------|----------|--------|---------------|
| FP32 | 1 | 8 | 23 | ~4.3B | ±3.4×10³⁸ |
| FP16 | 1 | 5 | 10 | 65,536 | ±65,504 |
| BF16 | 1 | 8 | 7 | 65,536 | ±3.4×10³⁸ |
| FP8 E4M3 | 1 | 4 | 3 | 256 | ±448 |
| FP8 E5M2 | 1 | 5 | 2 | 256 | ±57,344 |
| **FP6 E3M2** | 1 | 3 | 2 | 64 | ±28 |
| **FP6 E2M3** | 1 | 2 | 3 | 64 | ±7.5 |
| **FP4 E2M1** | 1 | 2 | 1 | 16 | ±6 |
| INT8 | (1) | - | 7/8 | 256 | -128 to 127 |
| INT4 | (1) | - | 3/4 | 16 | -8 to 7 |

**FP6 — The "Goldilocks" format:**

FP6 was popularized by "FP6-LLM: Efficiently Serving Quantized Large Language Models on GPUs" (Xia et al., 2024). It offers a compelling middle ground:

| Metric | INT4 | FP6 | INT8 | FP16 |
|--------|------|-----|------|------|
| Memory savings | 4x | 2.67x | 2x | 1x |
| Quality (7B PPL) | 5.63 | 5.52 | 5.48 | 5.47 |
| Power-of-2 aligned | ✅ | ❌ | ✅ | ✅ |
| GPU kernel support | Good | Custom | Excellent | Native |
| Inference speed | ~2x | ~1.5-1.8x | ~1.5x | 1x |

FP6 is NOT power-of-2 aligned (6 bits doesn't divide evenly into bytes), which makes it harder to implement efficient GPU kernels. The FP6-LLM paper solved this with a custom "TC-FPx" kernel.

**FP4 — Alternative to INT4/NF4:**

```
FP4 E2M1 quantization levels:
{-6, -4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3, 4, 6}

INT4 quantization levels:
{-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7}

NF4 quantization levels (normalized):
{-1.0, -0.70, -0.53, -0.39, -0.28, -0.18, -0.09, 0.0,
  0.08,  0.16,  0.25,  0.34,  0.44,  0.56,  0.72, 1.0}
```

Key differences:
- INT4: Uniformly spaced, good for general-purpose
- FP4: Non-uniform (log-scale), better for values clustered near zero
- NF4: Non-uniform (normal quantile), theoretically optimal for Gaussian weights

**Comparison table — When to use which format:**

| Use Case | Best Format | Why |
|----------|-------------|-----|
| Maximum quality at ~4 bits | GPTQ/AWQ INT4 | Hessian/activation-aware optimal rounding |
| QLoRA fine-tuning | NF4 | Optimal for normally-distributed weights |
| Near-FP16 quality with savings | FP8 | Currently best balance on H100 |
| Maximum throughput on H100 | FP8 E4M3 | Native hardware support |
| Middle ground (quality vs size) | FP6 | Better quality than INT4, smaller than INT8 |
| CPU deployment | GGUF (k-quant INT4/5) | llama.cpp optimized kernels |

```python
# FP8 inference with vLLM (H100/Ada Lovelace GPUs)
"""
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-70b-hf \
    --quantization fp8 \
    --dtype float16 \
    --tensor-parallel-size 4
"""

# bitsandbytes FP4 mode
from transformers import BitsAndBytesConfig
import torch

config_fp4 = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="fp4",          # FP4 instead of NF4
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
# Generally NF4 > FP4 for neural network weights
# But FP4 has simpler dequantization logic
```

---

### Q15: How do you deploy quantized models in production with vLLM, including handling multiple quantization formats and monitoring quality?

**Answer:**

**Production deployment architecture:**

```python
#!/usr/bin/env python3
"""
Production-grade quantized model serving with vLLM.
Handles: AWQ, GPTQ, FP8, bitsandbytes formats.
Includes: health checks, quality monitoring, A/B testing.
"""

# ============================================================
# 1. vLLM Server Configuration (Docker Compose)
# ============================================================
DOCKER_COMPOSE = """
version: '3.8'
services:
  vllm-awq:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "8000:8000"
    volumes:
      - ./models:/models
    command: >
      --model /models/llama-2-70b-awq
      --quantization awq
      --tensor-parallel-size 2
      --max-model-len 4096
      --gpu-memory-utilization 0.90
      --max-num-seqs 256
      --enable-prefix-caching
      --disable-log-requests
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  vllm-gptq:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "8001:8000"
    volumes:
      - ./models:/models
    command: >
      --model /models/llama-2-70b-gptq
      --quantization gptq
      --tensor-parallel-size 2
      --max-model-len 4096
      --gpu-memory-utilization 0.90

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - vllm-awq
      - vllm-gptq
"""

# ============================================================
# 2. Quality Monitoring System
# ============================================================
import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InferenceMetrics:
    """Track inference quality and performance metrics."""
    model_name: str
    quantization: str
    total_requests: int = 0
    total_tokens: int = 0
    total_latency: float = 0.0
    errors: int = 0
    ttft_samples: list = field(default_factory=list)  # Time to first token
    tps_samples: list = field(default_factory=list)    # Tokens per second

    @property
    def avg_latency(self) -> float:
        return self.total_latency / max(self.total_requests, 1)

    @property
    def throughput(self) -> float:
        return self.total_tokens / max(self.total_latency, 0.001)

    @property
    def p50_ttft(self) -> float:
        if not self.ttft_samples:
            return 0
        sorted_ttft = sorted(self.ttft_samples)
        return sorted_ttft[len(sorted_ttft) // 2]

    @property
    def p99_ttft(self) -> float:
        if not self.ttft_samples:
            return 0
        sorted_ttft = sorted(self.ttft_samples)
        idx = int(len(sorted_ttft) * 0.99)
        return sorted_ttft[min(idx, len(sorted_ttft) - 1)]


class QuantizedModelMonitor:
    """Monitor quantized model quality in production."""

    def __init__(self):
        self.metrics: dict[str, InferenceMetrics] = {}
        self.quality_baselines: dict[str, dict] = {}

    def register_model(
        self,
        model_name: str,
        quantization: str,
        baseline_perplexity: Optional[float] = None,
    ):
        key = f"{model_name}_{quantization}"
        self.metrics[key] = InferenceMetrics(model_name, quantization)
        if baseline_perplexity:
            self.quality_baselines[key] = {"perplexity": baseline_perplexity}

    def record_request(
        self,
        model_name: str,
        quantization: str,
        latency: float,
        output_tokens: int,
        ttft: float,
        error: bool = False,
    ):
        key = f"{model_name}_{quantization}"
        m = self.metrics[key]
        m.total_requests += 1
        m.total_latency += latency
        m.total_tokens += output_tokens
        m.ttft_samples.append(ttft)
        m.tps_samples.append(output_tokens / max(latency, 0.001))
        if error:
            m.errors += 1

    def get_dashboard(self) -> dict:
        """Generate monitoring dashboard data."""
        dashboard = {}
        for key, m in self.metrics.items():
            dashboard[key] = {
                "model": m.model_name,
                "quantization": m.quantization,
                "total_requests": m.total_requests,
                "throughput_tps": round(m.throughput, 1),
                "avg_latency_ms": round(m.avg_latency * 1000, 1),
                "p50_ttft_ms": round(m.p50_ttft * 1000, 1),
                "p99_ttft_ms": round(m.p99_ttft * 1000, 1),
                "error_rate": round(m.errors / max(m.total_requests, 1) * 100, 2),
            }
        return dashboard


# ============================================================
# 3. A/B Testing Between Quantization Methods
# ============================================================
import random
import openai


class QuantizationABTest:
    """A/B test between different quantization methods."""

    def __init__(self, endpoints: dict[str, str], weights: Optional[dict[str, float]] = None):
        """
        endpoints: {"awq": "http://localhost:8000", "gptq": "http://localhost:8001"}
        weights: {"awq": 0.7, "gptq": 0.3}  (traffic split)
        """
        self.endpoints = endpoints
        self.weights = weights or {k: 1.0 / len(endpoints) for k in endpoints}
        self.monitor = QuantizedModelMonitor()

        for name, url in endpoints.items():
            self.monitor.register_model(name, name)

    def _select_variant(self) -> str:
        """Weighted random selection of quantization variant."""
        variants = list(self.weights.keys())
        weights = list(self.weights.values())
        return random.choices(variants, weights=weights, k=1)[0]

    async def generate(self, prompt: str, max_tokens: int = 256) -> dict:
        """Route request to a quantization variant and track metrics."""
        variant = self._select_variant()
        endpoint = self.endpoints[variant]

        client = openai.AsyncOpenAI(base_url=f"{endpoint}/v1", api_key="unused")

        start = time.time()
        ttft = None
        output_tokens = 0
        full_response = ""

        try:
            stream = await client.chat.completions.create(
                model="model",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if ttft is None:
                    ttft = time.time() - start
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    output_tokens += 1

            latency = time.time() - start
            self.monitor.record_request(
                variant, variant, latency, output_tokens, ttft or latency
            )

            return {
                "variant": variant,
                "response": full_response,
                "latency": latency,
                "ttft": ttft,
                "tokens": output_tokens,
            }

        except Exception as e:
            self.monitor.record_request(variant, variant, time.time() - start, 0, 0, error=True)
            raise


# ============================================================
# 4. Quantization Format Auto-Detection and Loading
# ============================================================
def detect_quantization_format(model_path: str) -> dict:
    """Detect the quantization format of a saved model."""
    import json
    import os

    config_path = os.path.join(model_path, "config.json")
    quant_config_path = os.path.join(model_path, "quantize_config.json")

    result = {"format": "unknown", "bits": None, "group_size": None}

    # Check for GPTQ
    if os.path.exists(quant_config_path):
        with open(quant_config_path) as f:
            qconfig = json.load(f)
        result["format"] = "gptq"
        result["bits"] = qconfig.get("bits", 4)
        result["group_size"] = qconfig.get("group_size", 128)
        return result

    # Check config.json for quantization info
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)

        quant_config = config.get("quantization_config", {})

        if quant_config.get("quant_method") == "awq":
            result["format"] = "awq"
            result["bits"] = quant_config.get("bits", 4)
            result["group_size"] = quant_config.get("group_size", 128)
        elif quant_config.get("quant_method") == "gptq":
            result["format"] = "gptq"
            result["bits"] = quant_config.get("bits", 4)
            result["group_size"] = quant_config.get("group_size", 128)
        elif "bitsandbytes" in str(quant_config):
            result["format"] = "bitsandbytes"
            result["bits"] = 4 if quant_config.get("load_in_4bit") else 8

    # Check for GGUF files
    gguf_files = [f for f in os.listdir(model_path) if f.endswith(".gguf")]
    if gguf_files:
        result["format"] = "gguf"
        # Parse quantization type from filename (e.g., "model-Q4_K_M.gguf")
        for f in gguf_files:
            for qt in ["Q2_K", "Q3_K_S", "Q3_K_M", "Q4_K_S", "Q4_K_M",
                       "Q5_K_S", "Q5_K_M", "Q6_K", "Q8_0"]:
                if qt in f:
                    result["quant_type"] = qt
                    result["bits"] = int(qt[1])
                    break

    return result


def get_vllm_launch_command(model_path: str, tp_size: int = 1) -> str:
    """Generate the correct vLLM launch command based on detected format."""
    fmt = detect_quantization_format(model_path)

    base_cmd = (
        f"python -m vllm.entrypoints.openai.api_server "
        f"--model {model_path} "
        f"--tensor-parallel-size {tp_size} "
        f"--max-model-len 4096 "
        f"--gpu-memory-utilization 0.90"
    )

    if fmt["format"] == "awq":
        return f"{base_cmd} --quantization awq"
    elif fmt["format"] == "gptq":
        return f"{base_cmd} --quantization gptq"
    elif fmt["format"] == "bitsandbytes":
        return f"{base_cmd} --quantization bitsandbytes --load-format bitsandbytes"
    elif fmt["format"] == "gguf":
        # vLLM has experimental GGUF support
        return f"{base_cmd} --quantization gguf"
    else:
        return f"{base_cmd}  # FP16 (no quantization detected)"
```

---

## Code Examples Reference

### Quick Reference: Load Any Quantized Model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# ============================================================
# bitsandbytes 4-bit (NF4/QLoRA)
# ============================================================
bnb_4bit = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
model_4bit = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_4bit,
    device_map="auto",
)

# ============================================================
# bitsandbytes 8-bit (LLM.int8())
# ============================================================
bnb_8bit = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
)
model_8bit = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_8bit,
    device_map="auto",
)

# ============================================================
# Pre-quantized GPTQ model (e.g., from TheBloke)
# ============================================================
model_gptq = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-GPTQ",
    device_map="auto",
    trust_remote_code=False,
)

# ============================================================
# Pre-quantized AWQ model
# ============================================================
model_awq = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-AWQ",
    device_map="auto",
)

# ============================================================
# GGUF with llama-cpp-python
# ============================================================
from llama_cpp import Llama

model_gguf = Llama(
    model_path="./models/llama-2-7b-Q4_K_M.gguf",
    n_gpu_layers=33,   # Offload all layers to GPU (-1 for all)
    n_ctx=4096,         # Context window
    n_threads=8,        # CPU threads for non-offloaded layers
)

output = model_gguf(
    "Explain quantum computing:",
    max_tokens=256,
    temperature=0.7,
    top_p=0.9,
)
print(output["choices"][0]["text"])
```

---

## Quick Revision Cheat Sheet

```
QUANTIZATION IN 60 SECONDS:
├── Formats: FP32 (32b) > FP16/BF16 (16b) > FP8 (8b) > INT8 (8b) > INT4/NF4 (4b)
├── Methods:
│   ├── PTQ (post-training): GPTQ, AWQ, GGUF — no training needed
│   └── QAT (during training): QLoRA, LLM-QAT — trains with fake quantization
├── GPTQ: Hessian-based, layer-by-layer, best quality INT4
├── AWQ: Activation-aware scaling, fastest quantization, slightly better than GPTQ
├── GGUF: llama.cpp format, works on CPU, many quant variants (Q2-Q8)
├── NF4: Normal-distribution-optimal 4-bit, used in QLoRA
├── Deployment:
│   ├── GPU: AWQ/GPTQ + vLLM (maximum throughput)
│   ├── CPU: GGUF Q4_K_M + llama.cpp (best CPU speed)
│   └── Fine-tuning: QLoRA (NF4 + LoRA adapters)
└── Rules of thumb:
    ├── INT8: <1% quality loss for any model
    ├── INT4 (GPTQ/AWQ): 2-5% quality loss, 4x memory savings
    ├── Never quantize models < 1B parameters
    └── Always benchmark on YOUR task, not just perplexity
```
