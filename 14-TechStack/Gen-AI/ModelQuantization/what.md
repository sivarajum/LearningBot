# Model Quantization — Complete Guide

## Table of Contents
1. [What is Quantization?](#what-is-quantization)
2. [Why Quantize?](#why-quantize)
3. [Precision Formats](#precision-formats)
4. [Types: PTQ vs QAT](#types-ptq-vs-qat)
5. [Quantization Methods](#quantization-methods)
   - [GPTQ](#gptq)
   - [AWQ](#awq)
   - [bitsandbytes](#bitsandbytes)
   - [GGUF / GGML](#gguf--ggml)
   - [FP8](#fp8)
   - [SmoothQuant](#smoothquant)
6. [Installation](#installation)
7. [Code Examples](#code-examples)
   - [Beginner: Load Quantized Model from Hub](#beginner-load-quantized-model-from-hub)
   - [Intermediate: Quantize Your Own Model](#intermediate-quantize-your-own-model)
   - [Advanced: Custom Calibration & Mixed Precision](#advanced-custom-calibration--mixed-precision)
8. [Comparison: GPTQ vs AWQ vs bitsandbytes vs GGUF](#comparison-gptq-vs-awq-vs-bitsandbytes-vs-gguf)
9. [Benchmarks](#benchmarks)
10. [Best Practices](#best-practices)
11. [Common Pitfalls](#common-pitfalls)
12. [Real-World Use Cases](#real-world-use-cases)
13. [FAQ](#faq)

---

## What is Quantization?

Quantization is the process of **reducing the numerical precision** of a model's weights (and optionally activations) from higher-precision formats (like FP32) to lower-precision formats (like INT8, INT4). The core idea: you don't need 32-bit floating point to represent learned weights — most of the information can be preserved in fewer bits.

**The fundamental equation:**

```
quantized_value = round(value / scale) + zero_point
dequantized_value = (quantized_value - zero_point) * scale
```

Where:
- `scale` = (max_val - min_val) / (2^bits - 1)
- `zero_point` = offset to map the zero value correctly

**What changes:**
- FP32 weight: `0.00234567890123456` (32 bits per parameter)
- FP16 weight: `0.002346` (16 bits per parameter)
- INT8 weight: `3` (8 bits per parameter, with scale=0.000782)
- INT4 weight: `1` (4 bits per parameter, with scale=0.00234)

**What stays the same:**
- Model architecture (layers, attention heads, hidden dims)
- Tokenizer and vocabulary
- Inference logic / forward pass structure

---

## Why Quantize?

### Memory Reduction

| Model | FP32 | FP16 | INT8 | INT4 |
|-------|------|------|------|------|
| LLaMA-7B | 28 GB | 14 GB | 7 GB | 3.5 GB |
| LLaMA-13B | 52 GB | 26 GB | 13 GB | 6.5 GB |
| LLaMA-70B | 280 GB | 140 GB | 70 GB | 35 GB |
| Mixtral-8x7B | 180 GB | 90 GB | 45 GB | 22.5 GB |
| Falcon-180B | 720 GB | 360 GB | 180 GB | 90 GB |

**Formula:** Memory (GB) = Parameters × Bytes_per_param / 1e9

- FP32: 4 bytes per param
- FP16/BF16: 2 bytes per param
- INT8: 1 byte per param
- INT4: 0.5 bytes per param

### Speed Improvement

- **Lower memory bandwidth** → faster data movement from VRAM to compute units
- **Smaller tensor cores** → INT8/INT4 ops are 2-4x faster than FP16 on modern GPUs
- **Larger batch sizes** → fit more data in VRAM → higher throughput
- **CPU inference feasible** → INT4 models can run on laptops (via GGUF)

### Cost Reduction

| Scenario | FP16 | INT4 | Savings |
|----------|------|------|---------|
| LLaMA-70B serving (A100 80GB) | 2× A100 GPUs | 1× A100 GPU | 50% GPU cost |
| LLaMA-7B serving | A10G (24GB) | T4 (16GB) | ~60% GPU cost |
| LLaMA-13B local | RTX 4090 (24GB) | RTX 3060 (12GB) | Consumer GPU feasible |

---

## Precision Formats

### FP32 (Full Precision)
- **Bits:** 32 (1 sign + 8 exponent + 23 mantissa)
- **Range:** ±3.4 × 10^38
- **Use:** Training baseline, reference accuracy
- **Memory:** 4 bytes per parameter

### FP16 (Half Precision)
- **Bits:** 16 (1 sign + 5 exponent + 10 mantissa)
- **Range:** ±65,504
- **Use:** Standard mixed-precision training
- **Memory:** 2 bytes per parameter
- **Issue:** Small dynamic range → overflow/underflow risk in training

### BF16 (Brain Float 16)
- **Bits:** 16 (1 sign + 8 exponent + 7 mantissa)
- **Range:** Same as FP32 (±3.4 × 10^38)
- **Use:** Preferred for LLM training (invented by Google Brain)
- **Memory:** 2 bytes per parameter
- **Advantage:** Same range as FP32, less precision than FP16 but far fewer numerical issues

### FP8 (E4M3 / E5M2)
- **Bits:** 8
- **E4M3:** 1 sign + 4 exponent + 3 mantissa (inference-optimized)
- **E5M2:** 1 sign + 5 exponent + 2 mantissa (training-compatible)
- **Use:** H100/H200 native format, next-gen quantization
- **Memory:** 1 byte per parameter

### INT8 (8-bit Integer)
- **Bits:** 8
- **Range:** -128 to 127 (signed) or 0 to 255 (unsigned)
- **Use:** Post-training quantization, serving
- **Memory:** 1 byte per parameter

### INT4 (4-bit Integer)
- **Bits:** 4
- **Range:** -8 to 7 (signed) or 0 to 15 (unsigned)
- **Use:** Aggressive compression for LLM serving
- **Memory:** 0.5 bytes per parameter (two values packed per byte)

### NF4 (Normal Float 4)
- **Bits:** 4 (non-uniform quantization levels)
- **Design:** Levels optimally placed for normally-distributed weights
- **Use:** QLoRA fine-tuning (bitsandbytes)
- **Advantage:** Better accuracy than uniform INT4 for neural network weights

---

## Types: PTQ vs QAT

### Post-Training Quantization (PTQ)

Quantize a **pre-trained** model without any additional training. You take a finished FP16/FP32 model and compress it.

**How it works:**
1. Load pre-trained model in full precision
2. Collect calibration statistics (optional, depends on method)
3. Compute quantization parameters (scale, zero_point) per layer/group
4. Convert weights to lower precision
5. Save quantized model

**Pros:**
- Fast — minutes to hours, not days
- No training data needed (or minimal calibration data)
- No GPU training required for weight-only methods
- Simple pipeline

**Cons:**
- Some accuracy degradation (especially at INT4)
- Cannot recover from quantization errors
- May need careful calibration for best results

**Methods:** GPTQ, AWQ, bitsandbytes (NF4/INT8), GGUF quantization

### Quantization-Aware Training (QAT)

Simulate quantization effects **during training** so the model learns to be robust to reduced precision.

**How it works:**
1. Insert fake-quantization nodes in the computation graph
2. Forward pass: quantize → dequantize weights (simulated low precision)
3. Backward pass: use straight-through estimator (STE) for gradients
4. Weights update in full precision, but learn to be quantization-friendly
5. After training, convert to actual quantized format

**Pros:**
- Best accuracy at any given bit width
- Model actively compensates for quantization error
- Can push to very low bit widths (2-bit, 1-bit)

**Cons:**
- Requires full training pipeline (GPU, data, time)
- 2-3x training time overhead
- More complex implementation
- Needs the original training data

**Methods:** PyTorch native QAT, TensorFlow QAT, BitNet (1-bit), OneBit

### When to Use Which

| Scenario | Recommendation |
|----------|---------------|
| Deploying existing HF model quickly | PTQ (GPTQ or AWQ) |
| Fine-tuning + quantizing | QLoRA (bitsandbytes NF4) then GPTQ/AWQ for serving |
| Maximum accuracy at INT8 | QAT |
| CPU deployment (laptops/phones) | PTQ → GGUF |
| H100 serving | FP8 PTQ |
| Research / pushing limits | QAT |

---

## Quantization Methods

### GPTQ

**Full name:** Generative Pre-Trained Transformer Quantization
**Paper:** "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" (Frantar et al., 2023)

**Core Idea:**
GPTQ is based on Optimal Brain Quantization (OBQ). It quantizes weights **one layer at a time**, using a small calibration dataset to measure the quantization error and optimally adjust remaining weights to compensate.

**Algorithm (simplified):**
1. Feed calibration data (128-1024 samples) through the model
2. For each layer (sequentially):
   a. Compute Hessian matrix H = X^T × X (from calibration activations)
   b. For each column of the weight matrix:
      - Quantize the weight
      - Compute quantization error
      - Update remaining (unquantized) weights to compensate: Δw = -error / H_ii × H_i
   c. Use Cholesky decomposition for numerical stability
3. Pack quantized weights into INT4/INT3/INT2 format

**Key characteristics:**
- **Requires calibration data** (typically 128 samples from C4 or WikiText)
- **Layer-wise quantization** — processes one transformer layer at a time
- **Weight-only** — only weights are quantized, activations stay in FP16
- **Group quantization** — weights divided into groups of 128, each group has its own scale/zero_point
- **GPU-accelerated inference** via custom CUDA kernels (ExLlama, Marlin)

**Supported bit widths:** 2, 3, 4, 8

**Strengths:**
- Excellent accuracy at 4-bit (often <1% degradation on perplexity)
- Very fast inference with ExLlama/Marlin kernels
- Mature ecosystem, thousands of GPTQ models on HuggingFace
- Deterministic — same input always produces same quantized model

**Weaknesses:**
- Quantization is slow (can take hours for 70B+ models)
- Requires calibration data (data dependency)
- GPU required for quantization process
- Less flexible than bitsandbytes for fine-tuning

```python
# GPTQ quantization config
from transformers import GPTQConfig

gptq_config = GPTQConfig(
    bits=4,                    # 4-bit quantization
    group_size=128,            # weights grouped in 128 for separate scales
    desc_act=True,             # use activation order (slower but more accurate)
    dataset="c4",             # calibration dataset
    tokenizer=tokenizer,
    use_exllama=True,          # use ExLlama kernels for fast inference
    exllama_config={"version": 2},  # ExLlama v2 (faster)
)
```

---

### AWQ

**Full name:** Activation-aware Weight Quantization
**Paper:** "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration" (Lin et al., 2024)

**Core Idea:**
Not all weights are equally important. AWQ observes that a small fraction of weights (0.1-1%) are **salient** — they correspond to large activation magnitudes. Protecting these salient weights dramatically reduces quantization error.

**Algorithm (simplified):**
1. Run calibration data to observe activation magnitudes per channel
2. Identify salient weight channels (those with large activations)
3. Apply per-channel scaling: multiply salient weights by a scale factor s > 1 before quantization
4. This "stretches" salient weights into a range where quantization preserves them better
5. Compensate by dividing the corresponding activations by s (mathematically equivalent)
6. Quantize all weights to INT4 with group quantization

**Key insight:** Instead of complex weight compensation (like GPTQ), AWQ simply **rescales** weights based on activation importance. This is simpler and often faster.

**Key characteristics:**
- **Activation-aware** — uses calibration data to find important weights
- **Per-channel scaling** — protects salient channels, not individual weights
- **Weight-only** — activations remain in FP16
- **Faster quantization** than GPTQ (no Hessian computation)
- **Hardware-friendly** — simple scaling operation, no complex kernels needed at quantization time

**Supported bit widths:** 4 (primarily)

**Strengths:**
- Often matches or beats GPTQ accuracy
- Faster quantization process (no Hessian inverse)
- Better generalization across tasks (less overfitting to calibration data)
- Excellent inference speed with custom kernels
- Good for instruction-tuned models

**Weaknesses:**
- Primarily 4-bit only (less flexibility in bit widths)
- Smaller ecosystem than GPTQ (catching up)
- Fewer kernel backends than GPTQ

```python
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_pretrained(
    model_path,
    safetensors=True,
    device_map="auto"
)

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM"  # GEMM or GEMV kernel
}

model.quantize(tokenizer, quant_config=quant_config)
```

---

### bitsandbytes

**Author:** Tim Dettmers (University of Washington)
**Papers:** "LLM.int8()" (2022) and "QLoRA" (2023)

**Two modes:**

#### LLM.int8() — 8-bit Quantization
- **Core idea:** Mixed-precision decomposition. Most weights → INT8, but **outlier features** (those with very large magnitudes) stay in FP16.
- **How:** Identifies outlier dimensions (>6.0 magnitude), routes them to FP16 matmul, everything else goes through INT8 matmul. Results are combined.
- **Why outliers matter:** ~0.1% of hidden dimensions have values 10-100x larger. Quantizing these to INT8 destroys them. Keeping them in FP16 preserves accuracy.

#### NF4 — 4-bit NormalFloat (QLoRA)
- **Core idea:** Normal Float 4-bit — quantization levels placed at the quantiles of a normal distribution (since neural network weights are roughly normally distributed).
- **Double quantization:** The quantization constants (scales) are themselves quantized to FP8.
- **Primary use:** QLoRA fine-tuning — base model in NF4, LoRA adapters in BF16.

**Key characteristics:**
- **Zero-shot** — no calibration data needed at all
- **Dynamic quantization** — happens on model load, not ahead of time
- **Integrated with HuggingFace** — just pass `BitsAndBytesConfig` to `from_pretrained`
- **Supports fine-tuning** — QLoRA is THE method for fine-tuning large models on consumer GPUs

**Strengths:**
- Simplest to use — one config object, done
- No calibration data required
- Fine-tuning compatible (QLoRA)
- Works immediately on any HuggingFace model
- Good INT8 accuracy (near-lossless with outlier handling)

**Weaknesses:**
- Slower inference than GPTQ/AWQ (no custom optimized kernels like ExLlama)
- NF4 inference speed is notably slower than GPTQ-4bit
- Not ideal for production serving (use for fine-tuning, then convert to GPTQ/AWQ for serving)
- NVIDIA GPU required (CUDA dependency)

```python
from transformers import BitsAndBytesConfig
import torch

# 4-bit NF4 config (for QLoRA)
bnb_config_4bit = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # nf4 or fp4
    bnb_4bit_compute_dtype=torch.bfloat16,  # compute in bf16
    bnb_4bit_use_double_quant=True,       # quantize the quantization constants
)

# 8-bit config (LLM.int8())
bnb_config_8bit = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,  # outlier threshold
)
```

---

### GGUF / GGML

**Author:** Georgi Gerganov (llama.cpp creator)
**Full name:** GPT-Generated Unified Format / GPT-Generated Model Language

**Core Idea:**
CPU-optimized quantization format designed for running LLMs on consumer hardware **without a GPU**. GGML was the original format; GGUF is the successor with better metadata and compatibility.

**Quantization types (GGUF naming convention):**

| Type | Bits | Method | Quality | Speed |
|------|------|--------|---------|-------|
| Q2_K | 2.5 | K-quant mixed | Low | Fastest |
| Q3_K_S | 3.2 | K-quant small | Fair | Very fast |
| Q3_K_M | 3.4 | K-quant medium | Fair+ | Fast |
| Q4_0 | 4.0 | Legacy round-to-nearest | Good | Fast |
| Q4_K_S | 4.3 | K-quant small | Good+ | Fast |
| Q4_K_M | 4.5 | K-quant medium | Very Good | Moderate |
| Q5_0 | 5.0 | Legacy | Very Good | Moderate |
| Q5_K_S | 5.3 | K-quant small | Excellent | Moderate |
| Q5_K_M | 5.5 | K-quant medium | Excellent | Slower |
| Q6_K | 6.6 | K-quant | Near-perfect | Slower |
| Q8_0 | 8.0 | Round-to-nearest | Near-perfect | Slowest |
| F16 | 16.0 | Half precision | Reference | Slowest |

**K-quants** = importance-based mixed quantization. More important layers (attention) get higher precision, less important layers (FFN) get lower precision.

**Key characteristics:**
- **CPU-first** — optimized for AVX2/AVX-512 SIMD instructions
- **GPU offloading** — can offload layers to GPU for hybrid CPU+GPU inference
- **Single file** — model + metadata + quantization info in one `.gguf` file
- **llama.cpp ecosystem** — used by llama.cpp, ollama, LM Studio, GPT4All, koboldcpp
- **No Python dependency** — C/C++ inference, Python bindings available

**Strengths:**
- Runs on CPU (laptops, Raspberry Pi, phones)
- Supports GPU offloading for speed boost
- Massive ecosystem (ollama, LM Studio, etc.)
- Single file format — easy to distribute
- Many quantization levels (Q2 through Q8)
- Apple Silicon (Metal) acceleration

**Weaknesses:**
- Slower than GPTQ/AWQ on dedicated GPUs
- Conversion from HuggingFace format required
- Less integrated with HuggingFace transformers
- Not suitable for fine-tuning

```bash
# Convert HuggingFace model to GGUF
python convert_hf_to_gguf.py \
    /path/to/model \
    --outfile model-f16.gguf \
    --outtype f16

# Quantize GGUF model
./llama-quantize model-f16.gguf model-Q4_K_M.gguf Q4_K_M

# Run inference
./llama-cli -m model-Q4_K_M.gguf -p "Hello, how are you?" -n 128
```

---

### FP8

**Hardware:** NVIDIA H100, H200, B100, B200

**Core Idea:**
FP8 is a floating-point format (not integer), giving it better dynamic range than INT8 while using the same amount of memory. Two variants exist:

- **E4M3** (4-bit exponent, 3-bit mantissa): Better precision, used for inference
- **E5M2** (5-bit exponent, 2-bit mantissa): Larger range, used for gradients in training

**Key characteristics:**
- **Near-lossless** — typically <0.1% perplexity degradation
- **Hardware-native** — H100 has dedicated FP8 Tensor Cores
- **Fast** — 2x throughput vs FP16 on H100
- **Simple** — no complex quantization algorithms needed
- **Supports both training and inference**

**Strengths:**
- Almost no accuracy loss
- Direct hardware support (no custom kernels needed)
- Can be used during training (not just inference)
- Simple per-tensor or per-channel scaling

**Weaknesses:**
- Requires H100 or newer GPU (majority of deployments still use A100)
- Only 2x compression (vs 4x for INT4)
- Less community tooling than INT4 methods

```python
# FP8 with vLLM
from vllm import LLM

model = LLM(
    model="meta-llama/Llama-3-70B",
    quantization="fp8",
    tensor_parallel_size=4,
)
```

---

### SmoothQuant

**Paper:** "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models" (Xiao et al., 2023)

**Core Idea:**
Activations have outliers that make them hard to quantize. SmoothQuant "smooths" the activations by migrating the quantization difficulty from activations to weights (which are easier to quantize).

**How:** Apply a per-channel scaling factor `s`:
- Divide activations by `s` (smooths outliers)
- Multiply weights by `s` (compensates, weights can handle it)
- Now both weights AND activations can be quantized to INT8

**Unique:** Quantizes BOTH weights and activations (W8A8), unlike GPTQ/AWQ which are weight-only.

**Strengths:**
- W8A8 = faster inference than weight-only (both operands in INT8 for GEMM)
- Good accuracy preservation
- Compatible with standard INT8 hardware (no custom kernels)

**Weaknesses:**
- INT8 only (not INT4)
- Requires calibration data
- Less compression than 4-bit methods

---

## Installation

### Core Libraries

```bash
# bitsandbytes (NVIDIA GPU required)
pip install bitsandbytes>=0.43.0

# auto-gptq (GPTQ quantization and inference)
pip install auto-gptq>=0.7.0
# or with CUDA support:
pip install auto-gptq --extra-index-url https://huggingface.github.io/autogptq-index/whl/cu121/

# autoawq (AWQ quantization and inference)
pip install autoawq>=0.2.0

# HuggingFace transformers (latest for all quantization support)
pip install transformers>=4.38.0

# Optimum (HuggingFace optimization toolkit, includes GPTQ)
pip install optimum>=1.17.0

# llama-cpp-python (GGUF inference in Python)
pip install llama-cpp-python>=0.2.50
# With CUDA support:
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python
# With Metal (Apple Silicon):
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# vLLM (production serving with quantization support)
pip install vllm>=0.3.0

# ExLlamaV2 (fastest GPTQ inference)
pip install exllamav2>=0.0.12
```

### Full Environment Setup

```bash
# Create conda environment
conda create -n quantization python=3.11 -y
conda activate quantization

# Install PyTorch with CUDA
pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cu121

# Install all quantization libraries
pip install \
    transformers>=4.38.0 \
    accelerate>=0.27.0 \
    bitsandbytes>=0.43.0 \
    auto-gptq>=0.7.0 \
    autoawq>=0.2.0 \
    optimum>=1.17.0 \
    datasets>=2.17.0 \
    sentencepiece \
    protobuf

# Verify installation
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')
import bitsandbytes; print(f'bitsandbytes: {bitsandbytes.__version__}')
import auto_gptq; print(f'auto-gptq: {auto_gptq.__version__}')
import awq; print(f'autoawq: installed')
"
```

---

## Code Examples

### Beginner: Load Quantized Model from Hub

The easiest way to use quantization — just load a pre-quantized model from HuggingFace Hub.

#### Load a GPTQ Model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "TheBloke/Llama-2-7B-GPTQ"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Load GPTQ model — quantization is auto-detected from config
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",  # automatically distribute across GPUs
    trust_remote_code=False,
)

# Generate text
inputs = tokenizer("The capital of France is", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

#### Load a Model with bitsandbytes 4-bit

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

model_id = "meta-llama/Llama-2-7b-hf"

# Define 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load model in 4-bit
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)

# Check memory usage
print(f"Model memory: {model.get_memory_footprint() / 1e9:.2f} GB")
# Expected: ~3.5 GB (vs 14 GB in FP16)

# Generate
inputs = tokenizer("Explain quantum computing in simple terms:", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

#### Load a GGUF Model (CPU or GPU)

```python
from llama_cpp import Llama

# Load GGUF model (downloads or local path)
llm = Llama(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    n_ctx=4096,         # context length
    n_threads=8,        # CPU threads
    n_gpu_layers=35,    # offload layers to GPU (0 = CPU only)
)

# Generate
output = llm(
    "What is machine learning?",
    max_tokens=256,
    temperature=0.7,
    top_p=0.9,
    echo=False,
)
print(output["choices"][0]["text"])
```

#### Load an AWQ Model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "TheBloke/Llama-2-7B-AWQ"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    trust_remote_code=False,
)

inputs = tokenizer("Write a Python function to sort a list:", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

### Intermediate: Quantize Your Own Model

#### Quantize with GPTQ (auto-gptq)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig
import torch

model_id = "meta-llama/Llama-2-7b-hf"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Define GPTQ config
gptq_config = GPTQConfig(
    bits=4,
    group_size=128,
    desc_act=True,           # activation order (more accurate, slightly slower)
    dataset="c4",            # calibration dataset
    tokenizer=tokenizer,
    use_exllama=False,       # disable during quantization
    damp_percent=0.1,        # dampening factor for Hessian
    sym=True,                # symmetric quantization
)

# Load model and quantize (this takes time)
print("Loading model and quantizing...")
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=gptq_config,
    device_map="auto",
    torch_dtype=torch.float16,
)

# Save quantized model
output_dir = "./llama2-7b-gptq-4bit"
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"Quantized model saved to {output_dir}")
```

#### Quantize with AWQ (autoawq)

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_id = "meta-llama/Llama-2-7b-hf"
output_dir = "./llama2-7b-awq-4bit"

# Load model
model = AutoAWQForCausalLM.from_pretrained(model_id, safetensors=True)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Quantization config
quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM",     # GEMM (batch) or GEMV (single)
}

# Quantize (uses calibration data internally)
print("Quantizing with AWQ...")
model.quantize(tokenizer, quant_config=quant_config)

# Save
model.save_quantized(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"AWQ model saved to {output_dir}")

# Push to HuggingFace Hub
# model.push_to_hub("your-username/llama2-7b-awq")
```

#### Quantize to GGUF

```bash
# Step 1: Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j

# Step 2: Convert HuggingFace model to GGUF FP16
python convert_hf_to_gguf.py \
    /path/to/meta-llama/Llama-2-7b-hf \
    --outfile llama2-7b-f16.gguf \
    --outtype f16

# Step 3: Quantize to desired format
./llama-quantize llama2-7b-f16.gguf llama2-7b-Q4_K_M.gguf Q4_K_M
./llama-quantize llama2-7b-f16.gguf llama2-7b-Q5_K_M.gguf Q5_K_M
./llama-quantize llama2-7b-f16.gguf llama2-7b-Q8_0.gguf Q8_0

# Step 4: Verify
./llama-cli -m llama2-7b-Q4_K_M.gguf \
    -p "The meaning of life is" \
    -n 128 --temp 0.7
```

#### QLoRA Fine-Tuning with bitsandbytes

```python
from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    BitsAndBytesConfig, TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset
import torch

model_id = "meta-llama/Llama-2-7b-hf"

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load quantized base model
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

# Prepare model for training
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    r=16,                     # rank
    lora_alpha=32,            # scaling
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Expected: trainable params: 13,631,488 || all params: 3,513,962,496 || 0.39%

# Training
training_args = TrainingArguments(
    output_dir="./qlora-output",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=200,
    bf16=True,
    optim="paged_adamw_8bit",   # 8-bit optimizer to save memory
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
)

dataset = load_dataset("timdettmers/openassistant-guanaco", split="train")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    tokenizer=tokenizer,
    args=training_args,
    max_seq_length=2048,
    dataset_text_field="text",
)

trainer.train()
trainer.save_model("./qlora-final")
```

---

### Advanced: Custom Calibration & Mixed Precision

#### Custom Calibration Dataset for GPTQ

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig
from datasets import load_dataset
import torch
import random

model_id = "meta-llama/Llama-2-13b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Custom calibration: use domain-specific data for better accuracy
# Rule of thumb: calibration data should match your inference domain
def prepare_calibration_data(tokenizer, n_samples=256, seq_length=2048):
    """
    Create calibration dataset from domain-specific text.
    More calibration samples = better accuracy but slower quantization.
    Recommended: 128-512 samples.
    """
    # Mix multiple sources for robust calibration
    datasets_to_mix = [
        ("wikitext", "wikitext-2-raw-v1", "text", 0.4),      # general knowledge
        ("c4", "en", "text", 0.3),                              # web text
        ("openwebtext", None, "text", 0.3),                     # diverse web
    ]

    calibration_texts = []
    for ds_name, ds_config, text_col, ratio in datasets_to_mix:
        n = int(n_samples * ratio)
        ds = load_dataset(ds_name, ds_config, split="train", streaming=True)
        texts = []
        for sample in ds:
            if len(sample[text_col].strip()) > 100:
                texts.append(sample[text_col])
            if len(texts) >= n:
                break
        calibration_texts.extend(texts)

    random.shuffle(calibration_texts)

    # Tokenize
    encodings = tokenizer(
        calibration_texts[:n_samples],
        truncation=True,
        max_length=seq_length,
        padding=True,
        return_tensors="pt",
    )
    return encodings["input_ids"]

calibration_data = prepare_calibration_data(tokenizer, n_samples=256)

# Use custom calibration with GPTQ
gptq_config = GPTQConfig(
    bits=4,
    group_size=128,
    desc_act=True,
    dataset=calibration_data,  # pass tensor directly
    tokenizer=tokenizer,
    damp_percent=0.01,         # lower damping = more aggressive optimization
    sym=False,                 # asymmetric quantization (can be more accurate)
    true_sequential=True,      # quantize layers in true sequential order
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=gptq_config,
    device_map="auto",
    torch_dtype=torch.float16,
)
```

#### Mixed Precision per Layer (Advanced GPTQ)

```python
"""
Strategy: Use higher precision for critical layers (first/last layers,
attention), lower precision for less critical (middle FFN layers).
"""
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
import torch

model_id = "meta-llama/Llama-2-7b-hf"

# Base config: 4-bit for most layers
quantize_config = BaseQuantizeConfig(
    bits=4,
    group_size=128,
    desc_act=True,
    sym=True,
    damp_percent=0.1,
)

model = AutoGPTQForCausalLM.from_pretrained(
    model_id,
    quantize_config=quantize_config,
    torch_dtype=torch.float16,
)

# Custom: keep certain layers in higher precision
# This requires modifying the quantization config per module
# In practice you'd use inside_layer_modules and outside_layer_modules

# Evaluate perplexity to verify quality
from transformers import AutoTokenizer
from datasets import load_dataset
import numpy as np

tokenizer = AutoTokenizer.from_pretrained(model_id)
test_data = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")

def evaluate_perplexity(model, tokenizer, dataset, max_samples=100):
    """Calculate perplexity on a test set."""
    model.eval()
    nlls = []
    for i, sample in enumerate(dataset):
        if i >= max_samples:
            break
        if len(sample["text"].strip()) < 10:
            continue
        encodings = tokenizer(
            sample["text"],
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        )
        input_ids = encodings["input_ids"].to(model.device)
        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)
            nlls.append(outputs.loss.item())
    ppl = np.exp(np.mean(nlls))
    return ppl

ppl = evaluate_perplexity(model, tokenizer, test_data)
print(f"Perplexity: {ppl:.2f}")
```

#### Production Serving with vLLM

```python
"""
Production-grade quantized model serving with vLLM.
Supports GPTQ, AWQ, FP8, and bitsandbytes.
"""
from vllm import LLM, SamplingParams

# Serve GPTQ model
llm = LLM(
    model="TheBloke/Llama-2-70B-GPTQ",
    quantization="gptq",
    tensor_parallel_size=2,      # distribute across 2 GPUs
    max_model_len=4096,
    gpu_memory_utilization=0.90,
    dtype="half",
)

# Serve AWQ model
llm_awq = LLM(
    model="TheBloke/Llama-2-70B-AWQ",
    quantization="awq",
    tensor_parallel_size=2,
    max_model_len=4096,
)

# Batch inference
prompts = [
    "What is deep learning?",
    "Explain transformers in NLP.",
    "How does attention mechanism work?",
]

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=256,
)

outputs = llm.generate(prompts, sampling_params)
for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Output: {output.outputs[0].text}\n")
```

---

## Comparison: GPTQ vs AWQ vs bitsandbytes vs GGUF

### Feature Comparison

| Feature | GPTQ | AWQ | bitsandbytes | GGUF |
|---------|------|-----|-------------|------|
| **Bit widths** | 2, 3, 4, 8 | 4 | 4 (NF4), 8 | 2-8 (many variants) |
| **Calibration data** | Required (128+ samples) | Required (small set) | Not required | Not required |
| **Quantization speed** | Slow (hours for 70B) | Moderate (faster than GPTQ) | Instant (on load) | Fast (minutes) |
| **Inference speed** | Fastest (ExLlama/Marlin) | Fast (custom kernels) | Slowest on GPU | Fast on CPU |
| **GPU required** | Yes (quantize + serve) | Yes (quantize + serve) | Yes (NVIDIA only) | No (CPU native) |
| **Fine-tuning** | Limited | Limited | Yes (QLoRA) | No |
| **HF integration** | Excellent | Good | Excellent | Limited |
| **Production serving** | vLLM, TGI, ExLlama | vLLM, TGI | Not recommended | llama.cpp, ollama |
| **Accuracy (4-bit)** | Very good | Very good (often better) | Good (NF4) | Good (K-quant) |
| **Ecosystem size** | Largest | Growing | Large | Massive (consumer) |

### When to Use What

| Use Case | Best Choice | Why |
|----------|-------------|-----|
| **GPU production serving** | GPTQ or AWQ | Fastest inference with optimized kernels |
| **Fine-tuning large models** | bitsandbytes (NF4 + QLoRA) | Only option that supports training |
| **CPU / laptop inference** | GGUF (Q4_K_M) | Designed for CPU, works without GPU |
| **H100 deployment** | FP8 | Native hardware support, near-lossless |
| **Quick prototyping** | bitsandbytes | Zero calibration, instant loading |
| **Maximum compression** | GPTQ 2-bit or GGUF Q2_K | Lowest bit widths available |
| **Best accuracy at 4-bit** | AWQ or GPTQ (desc_act) | Calibration-based optimization |
| **Mobile / edge** | GGUF Q4_0 | Smallest + fastest on ARM |
| **Both weights + activations** | SmoothQuant (W8A8) | Faster GEMM with both quantized |

### Inference Speed Comparison (LLaMA-2-7B, 4-bit, A100)

| Method | Tokens/sec (batch=1) | Tokens/sec (batch=32) | Memory |
|--------|---------------------|----------------------|--------|
| FP16 (baseline) | 45 | 1,200 | 14 GB |
| GPTQ (ExLlama v2) | 95 | 2,400 | 4.2 GB |
| AWQ (GEMM) | 90 | 2,300 | 4.1 GB |
| bitsandbytes NF4 | 35 | 800 | 4.5 GB |
| GGUF Q4_K_M (GPU) | 75 | 1,800 | 4.3 GB |
| GGUF Q4_K_M (CPU) | 12 | 180 | 4.3 GB |

**Key takeaway:** GPTQ and AWQ are 2x+ faster than bitsandbytes for inference. Use bitsandbytes for fine-tuning, GPTQ/AWQ for serving.

---

## Benchmarks

### Perplexity (WikiText-2, lower = better)

| Model | FP16 | GPTQ-4bit | AWQ-4bit | NF4 | GGUF Q4_K_M |
|-------|------|-----------|----------|-----|-------------|
| LLaMA-2-7B | 5.47 | 5.63 | 5.60 | 5.78 | 5.68 |
| LLaMA-2-13B | 4.88 | 4.99 | 4.97 | 5.12 | 5.03 |
| LLaMA-2-70B | 3.32 | 3.39 | 3.37 | 3.48 | 3.42 |
| Mistral-7B | 5.25 | 5.39 | 5.36 | 5.52 | 5.43 |
| Mixtral-8x7B | 3.84 | 3.93 | 3.91 | 4.02 | 3.96 |

**Perplexity degradation at 4-bit:** typically 2-5% (acceptable for most applications)

### Task Accuracy (MMLU 5-shot, higher = better)

| Model | FP16 | GPTQ-4bit | AWQ-4bit | NF4 |
|-------|------|-----------|----------|-----|
| LLaMA-2-7B | 45.3 | 44.8 | 44.9 | 44.1 |
| LLaMA-2-70B | 68.9 | 68.2 | 68.4 | 67.5 |
| Mistral-7B | 60.1 | 59.5 | 59.7 | 58.8 |

### Memory Usage (GB)

| Model | FP32 | FP16 | INT8 | INT4 (any) | Overhead |
|-------|------|------|------|--------|----------|
| 7B params | 28 | 14 | 7.5 | 4.2 | +0.5 GB for scales/zeros |
| 13B params | 52 | 26 | 14 | 7.8 | +0.8 GB |
| 34B params | 136 | 68 | 36 | 20 | +2 GB |
| 70B params | 280 | 140 | 72 | 40 | +4 GB |

### Quantization Time (single A100 80GB)

| Model | GPTQ | AWQ | bitsandbytes | GGUF |
|-------|------|-----|-------------|------|
| 7B | 15 min | 8 min | Instant | 3 min |
| 13B | 35 min | 18 min | Instant | 7 min |
| 70B | 3-4 hours | 1.5 hours | Instant | 25 min |

---

## Best Practices

### 1. Choose the Right Method for Your Use Case

```
Serving on GPU? → GPTQ or AWQ
Fine-tuning? → bitsandbytes NF4 (QLoRA)
CPU deployment? → GGUF
H100 available? → FP8
Quick experiment? → bitsandbytes (no calibration)
```

### 2. Calibration Data Matters

- Use data that matches your inference domain
- 128-512 samples is the sweet spot
- More samples help with GPTQ, diminishing returns after 512
- For code models: use code for calibration
- For chat models: use conversation data

### 3. Group Size Trade-offs

| Group Size | Accuracy | Memory | Speed |
|------------|----------|--------|-------|
| 32 | Best | Highest | Slowest |
| 64 | Good | Medium | Medium |
| **128** | **Good (recommended)** | **Low** | **Fast** |
| 256 | Fair | Lowest | Fastest |
| -1 (per-channel) | Fair | Lowest | Fastest |

### 4. Evaluate Before Deploying

Always compare quantized vs full-precision on YOUR benchmark:

```python
# Quick evaluation checklist
tasks = [
    "perplexity on domain-specific text",
    "accuracy on key downstream tasks",
    "generation quality (human eval)",
    "latency per token",
    "peak memory usage",
    "batch throughput",
]
```

### 5. QLoRA → GPTQ Pipeline (Fine-tune then Serve)

```
1. Load base model in NF4 (bitsandbytes)
2. Fine-tune with QLoRA
3. Merge LoRA adapters into base model (full precision)
4. Quantize merged model with GPTQ or AWQ
5. Serve with vLLM or TGI
```

This gives you the best of both worlds: cheap fine-tuning + fast inference.

---

## Common Pitfalls

### 1. Using bitsandbytes for Production Serving
**Problem:** bitsandbytes NF4 inference is 2-3x slower than GPTQ/AWQ.
**Fix:** Use bitsandbytes for fine-tuning only. Convert to GPTQ/AWQ for serving.

### 2. Wrong Calibration Data
**Problem:** Quantizing a code model with Wikipedia text → poor code generation quality.
**Fix:** Always calibrate with data similar to your inference workload.

### 3. Ignoring desc_act in GPTQ
**Problem:** `desc_act=False` is faster to quantize but less accurate.
**Fix:** Use `desc_act=True` for best accuracy. Only skip it if quantization time is critical.

### 4. Not Checking Perplexity After Quantization
**Problem:** Blindly deploying quantized model without checking quality.
**Fix:** Always measure perplexity on a held-out test set. Degradation >10% = try different settings.

### 5. GGUF Quantization Level Too Aggressive
**Problem:** Using Q2_K for tasks requiring precision → garbage output.
**Fix:** Start with Q4_K_M (best quality/size ratio). Only go to Q3/Q2 if memory is truly critical.

### 6. Mixing Quantization Libraries
**Problem:** Loading a GPTQ model with bitsandbytes config → errors or silent corruption.
**Fix:** Match the loading method to the quantization format. Don't mix configs.

### 7. Forgetting GPU Memory for KV Cache
**Problem:** Model fits in 4 GB VRAM (INT4) but inference OOMs.
**Fix:** Account for KV cache memory: roughly `2 × n_layers × n_heads × head_dim × seq_len × 2 bytes`. For 7B at 4K context: ~2 GB additional.

---

## Real-World Use Cases

### 1. Startup Serving LLM on Budget
- **Model:** Mistral-7B-Instruct
- **Method:** AWQ 4-bit
- **Hardware:** Single T4 GPU ($0.35/hr on GCP)
- **Result:** 60+ tokens/sec, <5 GB VRAM, handles 50+ concurrent users with vLLM

### 2. Data Scientist Fine-Tuning on Consumer GPU
- **Model:** LLaMA-2-13B
- **Method:** QLoRA (NF4 + LoRA r=16)
- **Hardware:** RTX 4090 (24 GB VRAM)
- **Result:** Fine-tune 13B model on single consumer GPU, 4 hours on 50K samples

### 3. Mobile/Edge Deployment
- **Model:** Phi-2 (2.7B)
- **Method:** GGUF Q4_K_M
- **Hardware:** Apple M2 MacBook Air (8 GB RAM)
- **Result:** 20+ tokens/sec, runs entirely on device, no internet needed

### 4. Enterprise RAG Pipeline
- **Model:** Mixtral-8x7B
- **Method:** GPTQ 4-bit
- **Hardware:** 2× A100 40GB
- **Result:** 70B equivalent quality, fits on 2 GPUs instead of 8, 200+ tokens/sec batch

### 5. Local AI Assistant (Ollama)
- **Model:** LLaMA-3-8B
- **Method:** GGUF Q5_K_M
- **Hardware:** Any modern laptop with 16 GB RAM
- **Result:** Private, offline AI assistant, 15-25 tokens/sec on CPU

---

## FAQ

**Q: Does quantization affect fine-tuning results?**
A: If you fine-tune first (full precision) then quantize, minimal impact. If you fine-tune a quantized model (QLoRA), the LoRA adapters compensate. The biggest risk is quantizing AFTER fine-tuning without calibration data from your fine-tuned domain.

**Q: Can I quantize any model?**
A: Most transformer-based models supported by HuggingFace can be quantized. The libraries support LLaMA, Mistral, Falcon, MPT, GPT-NeoX, Phi, Qwen, and many more. Check the specific tool's supported architectures.

**Q: INT4 vs NF4 — which is better?**
A: NF4 is better for normally-distributed weights (which neural networks have). NF4 places quantization levels at the quantiles of a normal distribution, while INT4 uses uniform spacing. NF4 typically has 0.1-0.3 lower perplexity.

**Q: How do I choose between Q4_K_M and Q5_K_M for GGUF?**
A: Q4_K_M is the sweet spot for most use cases (good quality, small size). Q5_K_M is noticeably better quality with ~15% more memory. If you can fit Q5_K_M, use it.

**Q: Will quantization get better over time?**
A: Yes. FP8 on H100 is already near-lossless. Research on 2-bit and 1-bit quantization (BitNet) is progressing. Hardware is being designed with low-precision in mind. Expect better accuracy at lower bit widths over time.

**Q: Can I quantize vision-language models (e.g., LLaVA)?**
A: Yes, but with caveats. GPTQ and bitsandbytes work for the language model component. The vision encoder is typically kept in FP16 for accuracy. AWQ support is more limited for multimodal models.

**Q: GPTQ or AWQ — which should I default to?**
A: For most cases, AWQ. It's faster to quantize, generalizes better across tasks, and has comparable or better accuracy. Use GPTQ if you need 2-bit/3-bit, or if you need ExLlama v2 kernels specifically.

---

## Summary

| If you need... | Use this |
|----------------|----------|
| Fastest GPU inference | GPTQ (ExLlama v2) or AWQ |
| Fine-tuning on consumer GPU | bitsandbytes NF4 + QLoRA |
| CPU / laptop / mobile | GGUF (via llama.cpp / ollama) |
| Near-lossless compression | FP8 (H100) or INT8 (any GPU) |
| Production serving | vLLM + GPTQ/AWQ |
| Both weights + activations INT8 | SmoothQuant |
| Quick experiment, no calibration | bitsandbytes |

Quantization is not optional for LLM deployment — it's a **requirement**. The gap between FP16 and 4-bit quality is small enough that the 4x memory savings and 2x speed improvement make quantization the default for any production system.
