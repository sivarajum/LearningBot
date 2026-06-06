# LLM Inference Engines — Complete Guide

## Table of Contents
1. [What Are LLM Inference Engines?](#what-are-llm-inference-engines)
2. [Why Inference Engines Matter](#why-inference-engines-matter)
3. [Core Techniques](#core-techniques)
4. [vLLM — The Throughput King](#vllm--the-throughput-king)
5. [TGI — HuggingFace's Production Server](#tgi--huggingfaces-production-server)
6. [DeepSpeed-Inference](#deepspeed-inference)
7. [FP6-LLM — 6-Bit Inference](#fp6-llm--6-bit-inference)
8. [TensorRT-LLM — NVIDIA Optimized](#tensorrt-llm--nvidia-optimized)
9. [SGLang — Structured Generation Language](#sglang--structured-generation-language)
10. [Beginner Guide](#beginner-guide)
11. [Intermediate Guide](#intermediate-guide)
12. [Advanced Guide](#advanced-guide)
13. [Engine Comparison & Benchmarks](#engine-comparison--benchmarks)
14. [Production Deployment Patterns](#production-deployment-patterns)
15. [Best Practices](#best-practices)
16. [Common Pitfalls](#common-pitfalls)
17. [Further Reading](#further-reading)

---

## What Are LLM Inference Engines?

LLM Inference Engines are specialized serving systems designed to run large language models efficiently in production. Unlike training frameworks (PyTorch, JAX), inference engines focus on:

- **Maximizing throughput** (tokens/second for many concurrent users)
- **Minimizing latency** (time-to-first-token, inter-token latency)
- **Efficient memory management** (fitting larger models on fewer GPUs)
- **Production readiness** (health checks, metrics, scaling, fault tolerance)

### The Problem They Solve

Naive PyTorch inference is catastrophically inefficient for LLMs:

| Metric | Naive PyTorch | vLLM | Improvement |
|--------|--------------|------|-------------|
| Throughput (req/s) | 1.2 | 28.8 | **24x** |
| GPU Memory Utilization | 30-50% | 90-95% | **2-3x** |
| Concurrent Users | 1-4 | 100+ | **25x+** |
| KV Cache Waste | 60-80% | <4% | **15-20x** |

The root cause: LLM inference is **memory-bound**, not compute-bound. The KV cache for attention grows linearly with sequence length and batch size. Without intelligent memory management, GPUs sit idle while memory is wasted on fragmentation.

---

## Why Inference Engines Matter

### Cost Impact

Running a 70B parameter model on 4×A100 GPUs costs ~$12/hour on cloud. At naive throughput (1.2 req/s), that's $10/request. With vLLM (28.8 req/s), it drops to $0.42/request — **a 24x cost reduction**.

### The Inference Tax

For most production LLM applications:
- **Training cost**: One-time, amortized over model lifetime
- **Inference cost**: Ongoing, scales with every user request
- **Ratio**: Inference costs are typically **10-100x** higher than training costs over a model's lifetime

### Key Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **TTFT** | Time-to-first-token — latency before streaming starts | <500ms |
| **ITL** | Inter-token latency — time between successive tokens | <30ms |
| **Throughput** | Total tokens generated per second (across all requests) | Maximize |
| **GPU Utilization** | % of GPU compute actually used | >80% |
| **KV Cache Hit Rate** | Prefix cache reuse across requests | >60% |

---

## Core Techniques

### 1. Continuous Batching

**The Problem:** Static batching waits for ALL requests in a batch to complete before processing the next batch. Short requests block on long ones.

**The Solution:** Continuous batching (also called "iteration-level scheduling") processes requests at the token level. When a request finishes, a new one immediately takes its slot.

```
Static Batching:
Request A: [████████████████████]  ←── All wait for longest
Request B: [████████░░░░░░░░░░░]  ←── Wasted GPU cycles
Request C: [██████░░░░░░░░░░░░░]  ←── Wasted GPU cycles
                                       ↑ Next batch starts here

Continuous Batching:
Request A: [████████████████████]
Request B: [████████]→[Request D]→[Request F████]
Request C: [██████]→[Request E████████]→[Req G]
                  ↑ Slots freed immediately
```

**Impact:** 2-5x throughput improvement over static batching alone.

### 2. PagedAttention (Virtual Memory for KV Cache)

**The Breakthrough:** Inspired by operating system virtual memory and paging. Instead of allocating contiguous memory blocks for each request's KV cache, PagedAttention divides the KV cache into fixed-size **pages** (blocks).

**How It Works:**

1. **Block Table:** Each request has a block table mapping logical KV blocks to physical memory
2. **Non-Contiguous Storage:** KV cache blocks can be scattered in GPU memory
3. **Copy-on-Write:** Shared prefixes (system prompts) share physical blocks until modified
4. **Dynamic Allocation:** Blocks allocated on-demand as the sequence grows

```
Traditional KV Cache (contiguous allocation):
GPU Memory: [Req1: 2048 tokens reserved████████░░░░░░]  ← 60% wasted
            [Req2: 2048 tokens reserved████░░░░░░░░░░]  ← 80% wasted

PagedAttention (paged allocation):
GPU Memory: [B1:R1][B2:R2][B3:R1][B4:R3][B5:R2][B6:R1][free][free]
            ↑ Blocks used on-demand, <4% waste
```

**Memory Savings:**
- Eliminates internal fragmentation (within allocated blocks)
- Eliminates external fragmentation (between blocks)
- Enables copy-on-write for shared prefixes → **beam search uses 55% less memory**
- Near-optimal memory utilization: **>96% efficiency** vs 20-40% with naive allocation

### 3. Tensor Parallelism

Splits individual layers across multiple GPUs. Each GPU holds a slice of every weight matrix and computes a portion of every operation.

```
Single GPU:                    2-way Tensor Parallel:
[Full Weight Matrix]     →     GPU0: [Left Half]   GPU1: [Right Half]
[Full Attention]         →     GPU0: [Half Heads]  GPU1: [Half Heads]
[Full FFN]               →     GPU0: [Half FFN]    GPU1: [Half FFN]
                               ↕ AllReduce after each layer ↕
```

**When to use:**
- Model doesn't fit on one GPU
- Need to reduce per-token latency (not just throughput)
- Have NVLink or high-bandwidth GPU interconnect

**Overhead:** ~5-15% communication overhead with NVLink, ~30-50% with PCIe

### 4. Speculative Decoding

Uses a small "draft" model to predict multiple tokens, then verifies them in parallel with the large "target" model.

```
Traditional (1 token at a time):
Target 70B: [token1] → [token2] → [token3] → [token4] → [token5]
Time:       |--50ms--| |--50ms--| |--50ms--| |--50ms--| |--50ms--|
Total: 250ms for 5 tokens

Speculative Decoding:
Draft 7B:   [t1,t2,t3,t4,t5] ← Generate 5 draft tokens (5ms)
Target 70B: [verify all 5 in one forward pass] ← 55ms
Accept:     [t1 ✓, t2 ✓, t3 ✓, t4 ✗] → 3 tokens accepted
Total: ~60ms for 3 tokens (vs 150ms traditional)
```

**Acceptance Rate:** Typically 60-80% with well-matched draft models. Net speedup: **2-3x** for generation-heavy workloads.

### 5. Flash Attention

Optimized attention kernel that avoids materializing the full N×N attention matrix in GPU HBM (High Bandwidth Memory).

```
Standard Attention:
Q,K,V → Compute S = QK^T (N×N matrix, stored in HBM) → softmax → SV
Memory: O(N²) — explodes for long sequences

Flash Attention:
Q,K,V → Tile computation in SRAM → Stream results → Never materialize full matrix
Memory: O(N) — constant overhead regardless of sequence length
```

**Impact:**
- 2-4x speedup on attention computation
- Enables longer context lengths (up to 1M+ tokens)
- Reduces memory from O(N²) to O(N)

### 6. Quantization (Reducing Precision)

| Precision | Bits/Param | Memory for 70B | Quality Loss | Speedup |
|-----------|-----------|----------------|-------------|---------|
| FP32 | 32 | 280 GB | Baseline | 1x |
| FP16/BF16 | 16 | 140 GB | Negligible | 2x |
| INT8 (W8A8) | 8 | 70 GB | <1% perplexity | 2-3x |
| INT4 (GPTQ/AWQ) | 4 | 35 GB | 1-3% perplexity | 3-4x |
| FP6 | 6 | 52.5 GB | <1% perplexity | 2.5x |
| INT3/INT2 | 2-3 | 17.5-26 GB | 5-15% perplexity | 4-6x |

---

## vLLM — The Throughput King

### Overview

vLLM (Virtual LLM) is the most popular open-source LLM inference engine, developed at UC Berkeley. It introduced **PagedAttention** and achieves **up to 24x higher throughput** than naive HuggingFace inference.

**Key Features:**
- PagedAttention for near-zero KV cache waste
- Continuous batching for maximum GPU utilization
- OpenAI-compatible API server (drop-in replacement)
- Tensor parallelism for multi-GPU serving
- Prefix caching (automatic prompt cache reuse)
- LoRA support (multiple adapters on one base model)
- Speculative decoding
- Quantization support (AWQ, GPTQ, SqueezeLLM, FP8)
- Distributed serving across multiple nodes

### Installation

```bash
# Basic installation
pip install vllm

# With CUDA 12.1
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121

# From source (for latest features)
git clone https://github.com/vllm-project/vllm.git
cd vllm
pip install -e .
```

### Basic Usage (Offline / Batch Inference)

```python
from vllm import LLM, SamplingParams

# Initialize the model
llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4,        # 4 GPUs
    dtype="auto",                   # Auto-detect best dtype
    max_model_len=8192,            # Max context length
    gpu_memory_utilization=0.90,   # Use 90% of GPU memory for KV cache
)

# Define sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
    stop=["</s>", "\n\nHuman:"],
    presence_penalty=0.1,
)

# Batch inference — all processed in parallel
prompts = [
    "Explain quantum computing in simple terms.",
    "Write a Python function to sort a list.",
    "What are the benefits of renewable energy?",
]

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}")
    print(f"Generated: {generated_text!r}\n")
```

### OpenAI-Compatible API Server

```bash
# Start the server (drop-in replacement for OpenAI API)
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 1 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.90 \
    --enable-prefix-caching \
    --max-num-seqs 256
```

```python
# Client code — identical to OpenAI SDK
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy",  # vLLM doesn't require a real key
)

# Chat completion
response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is PagedAttention?"},
    ],
    temperature=0.7,
    max_tokens=256,
    stream=True,  # Streaming supported
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Advanced Configuration

```python
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

# Multi-LoRA serving
llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    enable_lora=True,
    max_loras=4,               # Serve up to 4 LoRA adapters simultaneously
    max_lora_rank=64,          # Maximum LoRA rank
    gpu_memory_utilization=0.90,
)

# Serve different LoRA adapters per request
output_medical = llm.generate(
    ["Diagnose: patient with chest pain and shortness of breath"],
    SamplingParams(max_tokens=256),
    lora_request=LoRARequest("medical", 1, "/models/medical-lora"),
)

output_legal = llm.generate(
    ["Draft a non-disclosure agreement for a tech startup"],
    SamplingParams(max_tokens=256),
    lora_request=LoRARequest("legal", 2, "/models/legal-lora"),
)
```

### vLLM with Quantized Models

```python
from vllm import LLM, SamplingParams

# AWQ quantized model (4-bit)
llm = LLM(
    model="TheBloke/Llama-2-70B-Chat-AWQ",
    quantization="awq",
    tensor_parallel_size=2,  # 70B AWQ fits on 2×A100-40GB
    dtype="half",
)

# GPTQ quantized model
llm = LLM(
    model="TheBloke/Llama-2-70B-Chat-GPTQ",
    quantization="gptq",
    tensor_parallel_size=2,
)

# FP8 quantization (H100/Ada GPUs)
llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    quantization="fp8",
    tensor_parallel_size=4,
)
```

### Speculative Decoding in vLLM

```python
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    speculative_model="meta-llama/Llama-3.2-1B-Instruct",
    num_speculative_tokens=5,     # Draft 5 tokens at a time
    tensor_parallel_size=4,
    use_v2_block_manager=True,    # Required for spec decoding
)

# Same API — speculative decoding is transparent
output = llm.generate(
    ["Write a detailed essay about climate change."],
    SamplingParams(temperature=0.0, max_tokens=1024),
)
# 2-3x faster for long-form generation tasks
```

---

## TGI — HuggingFace's Production Server

### Overview

Text Generation Inference (TGI) is HuggingFace's production-grade inference server. It powers the HuggingFace Inference API and is optimized for enterprise deployment.

**Key Features:**
- Flash Attention 2 integration
- Continuous batching with dynamic scheduling
- Token streaming via Server-Sent Events (SSE)
- Quantization: GPTQ, AWQ, EETQ, bitsandbytes
- Tensor parallelism (multi-GPU, multi-node)
- Watermarking for AI-generated text detection
- Prometheus metrics endpoint
- Production-ready Docker images
- Grammar-constrained generation (JSON, regex)

### Docker Deployment (Recommended)

```bash
# Pull the official image
docker pull ghcr.io/huggingface/text-generation-inference:latest

# Run with a model
docker run --gpus all \
    --shm-size 1g \
    -p 8080:80 \
    -v /data/models:/data \
    -e HUGGING_FACE_HUB_TOKEN=$HF_TOKEN \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id meta-llama/Llama-3.1-8B-Instruct \
    --max-input-length 4096 \
    --max-total-tokens 8192 \
    --max-batch-prefill-tokens 16384 \
    --num-shard 1 \
    --quantize awq

# Multi-GPU (4-way tensor parallel)
docker run --gpus '"device=0,1,2,3"' \
    --shm-size 1g \
    -p 8080:80 \
    -v /data/models:/data \
    -e HUGGING_FACE_HUB_TOKEN=$HF_TOKEN \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id meta-llama/Llama-3.1-70B-Instruct \
    --num-shard 4
```

### Client Usage

```python
# Using huggingface_hub client
from huggingface_hub import InferenceClient

client = InferenceClient("http://localhost:8080")

# Simple generation
output = client.text_generation(
    "What are the main causes of inflation?",
    max_new_tokens=256,
    temperature=0.7,
    top_p=0.95,
    repetition_penalty=1.1,
)
print(output)

# Streaming
for token in client.text_generation(
    "Explain neural networks step by step:",
    max_new_tokens=512,
    stream=True,
):
    print(token, end="")

# Chat completion (OpenAI-compatible)
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python quicksort implementation."},
    ],
    max_tokens=512,
    temperature=0.3,
)
print(response.choices[0].message.content)
```

### Grammar-Constrained Generation

```python
from huggingface_hub import InferenceClient

client = InferenceClient("http://localhost:8080")

# Force JSON output with a specific schema
json_grammar = {
    "type": "json",
    "value": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "skills": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["name", "age", "skills"],
    },
}

output = client.text_generation(
    "Generate a profile for a senior Python developer:",
    grammar=json_grammar,
    max_new_tokens=200,
)
# Guaranteed valid JSON matching the schema
```

### TGI Configuration Reference

```bash
# Key performance flags
--max-batch-prefill-tokens 16384   # Max tokens in prefill batch
--max-input-length 4096            # Max input sequence length
--max-total-tokens 8192            # Max input + output combined
--max-concurrent-requests 128      # Max concurrent requests
--waiting-served-ratio 0.3         # Ratio of waiting vs serving
--max-batch-size 32                # Max requests per batch
--cuda-memory-fraction 0.9         # GPU memory fraction to use
--rope-scaling dynamic             # RoPE scaling for longer contexts
--disable-custom-kernels           # Fallback to standard kernels
```

---

## DeepSpeed-Inference

### Overview

DeepSpeed-Inference is Microsoft's inference optimization library, part of the DeepSpeed ecosystem. It focuses on extreme-scale model serving with features like:

- **ZeRO-Inference:** Memory-optimized inference with CPU offloading
- **Kernel Fusion:** Custom CUDA kernels for attention + residual + layer norm
- **Multi-GPU via Tensor Parallelism:** Automatic model partitioning
- **Heterogeneous Memory:** Seamlessly uses GPU + CPU + NVMe for massive models
- **MoE Support:** Efficient Mixture-of-Experts inference

### Installation

```bash
pip install deepspeed>=0.12.0

# Verify installation
ds_report
```

### Basic Usage

```python
import deepspeed
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model normally
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    torch_dtype=torch.float16,
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

# Apply DeepSpeed inference optimization
ds_model = deepspeed.init_inference(
    model,
    mp_size=1,                    # Tensor parallel degree
    dtype=torch.float16,          # Inference dtype
    replace_with_kernel_inject=True,  # Use optimized CUDA kernels
    max_tokens=4096,              # Max output tokens
)

# Generate
inputs = tokenizer("Explain gradient descent:", return_tensors="pt").to("cuda")
outputs = ds_model.generate(**inputs, max_new_tokens=256)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### DeepSpeed Config for Inference

```json
{
    "tensor_parallel": {
        "tp_size": 4
    },
    "dtype": "fp16",
    "replace_with_kernel_inject": true,
    "kernel_inject": true,
    "max_tokens": 4096,
    "enable_cuda_graph": true,
    "use_triton": false,
    "injection_policy": {
        "LlamaDecoderLayer": {
            "attn": ["self_attn.o_proj"],
            "mlp": ["mlp.down_proj"]
        }
    },
    "zero": {
        "stage": 3,
        "offload_param": {
            "device": "cpu",
            "pin_memory": true
        }
    }
}
```

### ZeRO-Inference (CPU/NVMe Offloading)

```python
import deepspeed
import torch
from transformers import AutoModelForCausalLM

# Load a model too large for GPU memory
# ZeRO-Inference offloads to CPU/NVMe dynamically
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-405B-Instruct",
    torch_dtype=torch.float16,
)

ds_config = {
    "zero": {
        "stage": 3,
        "offload_param": {
            "device": "cpu",        # Offload parameters to CPU
            "pin_memory": True,
            "nvme_path": "/nvme/offload",  # Optional NVMe offload
        },
        "offload_optimizer": {
            "device": "cpu",
        }
    },
    "dtype": "fp16",
    "tensor_parallel": {"tp_size": 8},
}

ds_model = deepspeed.init_inference(
    model,
    config=ds_config,
)
# Now the 405B model runs on 8 GPUs + CPU RAM
```

### Multi-GPU Tensor Parallel

```python
import deepspeed
import torch
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B-Instruct",
    torch_dtype=torch.float16,
)

# Automatic 4-way tensor parallelism
ds_model = deepspeed.init_inference(
    model,
    mp_size=4,                        # 4   GPUs
    dtype=torch.float16,
    replace_with_kernel_inject=True,  # Fused kernels
    enable_cuda_graph=True,           # CUDA graph capture for repeated shapes
)

# Launch with: deepspeed --num_gpus 4 inference_script.py
```

---

## FP6-LLM — 6-Bit Inference

### Overview

FP6-LLM is a specialized inference system using **6-bit floating-point quantization**, achieving a sweet spot between INT4 (too lossy) and INT8 (too large). Developed by Microsoft Research.

**Key insight:** FP6 preserves the floating-point format (sign + exponent + mantissa), unlike INT4/INT8 which lose the dynamic range. This provides near-FP16 quality with 2.67x memory reduction.

### Why 6 Bits?

| Precision | Quality (% of FP16) | Memory Savings | Hardware Support |
|-----------|---------------------|---------------|-----------------|
| FP16 | 100% (baseline) | 1x | Native |
| INT8 | 99.2% | 2x | Native (A100+) |
| **FP6** | **98.8%** | **2.67x** | Software kernel |
| INT4 (GPTQ) | 96-98% | 4x | Software kernel |
| INT4 (AWQ) | 97-99% | 4x | Software kernel |

### Usage

```python
from fp6_llm import FP6Linear
import torch
from transformers import AutoModelForCausalLM

# Quantize model to FP6
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B-Instruct",
    torch_dtype=torch.float16,
)

# Replace linear layers with FP6 variants
fp6_model = FP6Linear.quantize_model(model)

# Inference (2.67x less GPU memory, ~2x faster)
# 70B model fits on single A100-80GB in FP6
```

### Architecture Insight

```
FP6 Format: [S|EEE|MM]  (1 sign + 3 exponent + 2 mantissa)
FP16 Format: [S|EEEEE|MMMMMMMMMM]  (1 sign + 5 exponent + 10 mantissa)

Key: FP6 keeps the floating-point representation, preserving:
  ✓ Dynamic range (via exponent bits)
  ✓ Sign handling (positive/negative)
  ✗ Precision (reduced mantissa)

vs INT4: [SSSS] — fixed range, no exponent, loses dynamic range
```

---

## TensorRT-LLM — NVIDIA Optimized

### Overview

TensorRT-LLM is NVIDIA's proprietary inference optimization library. It compiles LLM architectures into highly optimized TensorRT engines with custom CUDA kernels for every major model family.

**Key Features:**
- FP8 quantization (native on H100/Ada Lovelace)
- In-flight batching (NVIDIA's continuous batching)
- Paged KV cache
- Multi-GPU/multi-node via Tensor + Pipeline Parallelism
- Custom attention kernels (XQA, MQA, GQA)
- Speculative decoding & Medusa heads
- KV cache reuse for prefix sharing
- Triton Inference Server integration

### Installation

```bash
# Docker (recommended)
docker pull nvcr.io/nvidia/tritonserver:24.02-trtllm-python-py3

# pip install (limited platform support)
pip install tensorrt-llm -U --pre \
    --extra-index-url https://pypi.nvidia.com
```

### Build & Run a Model

```bash
# Step 1: Convert HuggingFace model to TensorRT-LLM checkpoint
python convert_checkpoint.py \
    --model_dir /models/Llama-3.1-70B-Instruct \
    --output_dir /engines/llama-70b-ckpt \
    --dtype float16 \
    --tp_size 4 \
    --pp_size 1

# Step 2: Build the TensorRT engine
trtllm-build \
    --checkpoint_dir /engines/llama-70b-ckpt \
    --output_dir /engines/llama-70b-engine \
    --gemm_plugin float16 \
    --gpt_attention_plugin float16 \
    --max_batch_size 64 \
    --max_input_len 4096 \
    --max_seq_len 8192 \
    --paged_kv_cache enable \
    --remove_input_padding enable \
    --use_fp8_context_fmha enable  # H100 only
```

### Python Runtime

```python
import tensorrt_llm
from tensorrt_llm.runtime import ModelRunner

runner = ModelRunner.from_dir(
    engine_dir="/engines/llama-70b-engine",
    rank=0,  # GPU rank
)

outputs = runner.generate(
    batch_input_ids=[tokenizer.encode("Explain PagedAttention:")],
    max_new_tokens=256,
    end_id=tokenizer.eos_token_id,
    pad_id=tokenizer.pad_token_id,
    temperature=0.7,
    top_k=50,
    top_p=0.9,
    streaming=False,
)

output_text = tokenizer.decode(outputs[0][0])
print(output_text)
```

### FP8 Quantization (H100)

```bash
# Quantize to FP8 — near-FP16 quality, 2x memory savings
python quantize.py \
    --model_dir /models/Llama-3.1-70B-Instruct \
    --output_dir /engines/llama-70b-fp8 \
    --dtype float16 \
    --qformat fp8 \
    --kv_cache_dtype fp8 \
    --calib_dataset cnn_dailymail \
    --calib_size 512

# Build FP8 engine
trtllm-build \
    --checkpoint_dir /engines/llama-70b-fp8 \
    --output_dir /engines/llama-70b-fp8-engine \
    --max_batch_size 128 \
    --use_fp8_context_fmha enable
```

---

## SGLang — Structured Generation Language

### Overview

SGLang (Structured Generation Language) is a fast serving framework from the LMSYS team (creators of Chatbot Arena). It focuses on:

- **RadixAttention:** Advanced prefix caching using a radix tree data structure
- **Compressed Finite State Machine:** Efficient constrained decoding (JSON, regex)
- **Frontend Language:** Python-embedded DSL for complex LLM programs
- **Multi-modal support:** Vision-language models (LLaVA, etc.)

### Key Innovation: RadixAttention

```
Traditional Prefix Caching:
"You are a helpful assistant. " → Cache entry 1
"You are a helpful assistant. What is 2+2?" → Miss (different suffix)

RadixAttention (Radix Tree):
Root → "You are a helpful" → "assistant. " → "What is 2+2?"
                                            → "Explain quantum..."
                                            → "Write a poem..."
     → "Summarize the " → "following article:"
                        → "key points of:"

Benefit: Automatic longest-prefix matching, O(1) lookup, LRU eviction
```

### Installation & Server

```bash
pip install sglang[all]

# Start the server
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3.1-8B-Instruct \
    --port 30000 \
    --tp 1
```

### Frontend Language (SGLang Programs)

```python
import sglang as sgl

@sgl.function
def multi_turn_qa(s, question1, question2):
    s += sgl.system("You are a helpful assistant.")
    s += sgl.user(question1)
    s += sgl.assistant(sgl.gen("answer1", max_tokens=256))
    s += sgl.user(question2)
    s += sgl.assistant(sgl.gen("answer2", max_tokens=256))

# Run with automatic batching and prefix caching
state = multi_turn_qa.run(
    question1="What is machine learning?",
    question2="Give me a concrete example.",
)

print(state["answer1"])
print(state["answer2"])
```

### Constrained Generation

```python
import sglang as sgl

@sgl.function
def extract_info(s, text):
    s += sgl.user(f"Extract structured information from: {text}")
    s += sgl.assistant(
        sgl.gen(
            "result",
            max_tokens=200,
            regex=r'\{"name": "[^"]+", "age": \d+, "city": "[^"]+"\}',
        )
    )

# Output guaranteed to match the regex pattern
state = extract_info.run(text="John is 30 years old and lives in NYC.")
print(state["result"])
# {"name": "John", "age": 30, "city": "NYC"}
```

---

## Beginner Guide

### Getting Started with vLLM (Simplest Path)

**Step 1: Install**
```bash
pip install vllm openai
```

**Step 2: Start a Server**
```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 8000
```

**Step 3: Query It**
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="na")
response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### Which Engine Should I Use?

| Scenario | Recommended Engine | Why |
|----------|-------------------|-----|
| First time serving an LLM | **vLLM** | Easiest setup, OpenAI-compatible |
| HuggingFace ecosystem | **TGI** | Tight integration, Docker-ready |
| NVIDIA GPUs (H100/A100) | **TensorRT-LLM** | Maximum performance on NVIDIA |
| Complex LLM programs | **SGLang** | Frontend DSL, RadixAttention |
| Existing DeepSpeed training | **DeepSpeed-Inference** | Same ecosystem |
| Memory-constrained | **FP6-LLM** or vLLM+AWQ | Best quality/memory tradeoff |

### Key Concepts You Must Understand

1. **KV Cache**: The stored key-value pairs from attention computation. Grows with sequence length. This is the bottleneck.
2. **Prefill vs Decode**: Prefill processes the entire prompt in parallel (fast). Decode generates one token at a time (slow).
3. **Throughput vs Latency**: Throughput = total tokens/sec. Latency = time per request. Often in tension.
4. **Batch Size**: More requests batched together = higher throughput but higher latency per request.

---

## Intermediate Guide

### Multi-GPU Serving with vLLM

```python
from vllm import LLM, SamplingParams

# Tensor parallelism — split model across GPUs
llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    tensor_parallel_size=4,          # 4 GPUs
    pipeline_parallel_size=1,        # No pipeline parallelism
    max_model_len=8192,
    gpu_memory_utilization=0.92,
    enforce_eager=False,             # Enable CUDA graphs
    enable_prefix_caching=True,      # Cache shared prefixes
)
```

### Quantized Model Serving

```bash
# AWQ is generally the best quality/speed tradeoff
# 1. Quantize offline (one-time cost)
pip install autoawq
python -c "
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model = AutoAWQForCausalLM.from_pretrained('meta-llama/Llama-3.1-70B-Instruct')
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-70B-Instruct')
model.quantize(tokenizer, quant_config={'zero_point': True, 'q_group_size': 128, 'w_bit': 4})
model.save_quantized('/models/llama-70b-awq')
"

# 2. Serve with vLLM
python -m vllm.entrypoints.openai.api_server \
    --model /models/llama-70b-awq \
    --quantization awq \
    --tensor-parallel-size 2 \
    --max-model-len 8192
```

### TGI with Prometheus Monitoring

```yaml
# docker-compose.yml
version: "3.8"
services:
  tgi:
    image: ghcr.io/huggingface/text-generation-inference:latest
    ports:
      - "8080:80"
    volumes:
      - ./models:/data
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 4
              capabilities: [gpu]
    environment:
      - HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}
    command: >
      --model-id meta-llama/Llama-3.1-70B-Instruct
      --num-shard 4
      --max-input-length 4096
      --max-total-tokens 8192
      --max-batch-prefill-tokens 16384

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'tgi'
    scrape_interval: 5s
    static_configs:
      - targets: ['tgi:80']
    metrics_path: /metrics
```

### Key TGI Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|------------|----------------|
| `tgi_request_duration_seconds` | Request latency histogram | p99 > 5s |
| `tgi_request_count` | Total requests served | — |
| `tgi_queue_size` | Requests waiting in queue | > 50 |
| `tgi_batch_current_size` | Current batch size | — |
| `tgi_request_generated_tokens_total` | Total tokens generated | — |
| `tgi_request_input_length` | Input length histogram | — |

### Load Testing

```bash
# Using hey (HTTP benchmark tool)
hey -n 1000 -c 50 -m POST \
    -H "Content-Type: application/json" \
    -d '{"inputs":"What is deep learning?","parameters":{"max_new_tokens":100}}' \
    http://localhost:8080/generate
```

---

## Advanced Guide

### Multi-LoRA Serving at Scale

```python
# Serve 10+ LoRA adapters on one base model in vLLM
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    enable_lora=True,
    max_loras=16,            # Hot-swap up to 16 adapters
    max_lora_rank=64,
    max_cpu_loras=32,        # Cache 32 on CPU (swap to GPU on demand)
    gpu_memory_utilization=0.92,
)

# Register LoRA adapters dynamically
adapters = {
    "medical":   LoRARequest("medical", 1, "s3://models/medical-lora-r64"),
    "legal":     LoRARequest("legal", 2, "s3://models/legal-lora-r64"),
    "finance":   LoRARequest("finance", 3, "s3://models/finance-lora-r64"),
    "code":      LoRARequest("code", 4, "s3://models/code-lora-r64"),
    "creative":  LoRARequest("creative", 5, "s3://models/creative-lora-r64"),
}

# Route requests to appropriate adapters
def serve_request(prompt: str, domain: str) -> str:
    adapter = adapters.get(domain)
    output = llm.generate(
        [prompt],
        SamplingParams(temperature=0.7, max_tokens=512),
        lora_request=adapter,
    )
    return output[0].outputs[0].text
```

### Kubernetes Deployment with vLLM

```yaml
# vllm-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-llama-70b
  labels:
    app: vllm-inference
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vllm-inference
  template:
    metadata:
      labels:
        app: vllm-inference
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        ports:
        - containerPort: 8000
        env:
        - name: HUGGING_FACE_HUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-secret
              key: token
        args:
        - "--model"
        - "meta-llama/Llama-3.1-70B-Instruct"
        - "--tensor-parallel-size"
        - "4"
        - "--max-model-len"
        - "8192"
        - "--gpu-memory-utilization"
        - "0.92"
        - "--enable-prefix-caching"
        resources:
          limits:
            nvidia.com/gpu: 4
          requests:
            nvidia.com/gpu: 4
            memory: "64Gi"
            cpu: "16"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 120
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 180
          periodSeconds: 30
      nodeSelector:
        nvidia.com/gpu.product: "NVIDIA-A100-SXM4-80GB"
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
---
apiVersion: v1
kind: Service
metadata:
  name: vllm-service
spec:
  selector:
    app: vllm-inference
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-llama-70b
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Pods
    pods:
      metric:
        name: gpu_utilization
      target:
        type: AverageValue
        averageValue: "80"
  - type: Pods
    pods:
      metric:
        name: request_queue_size
      target:
        type: AverageValue
        averageValue: "20"
```

### Speculative Decoding — Deep Dive

```python
# Option 1: Separate draft model
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    speculative_model="meta-llama/Llama-3.2-1B-Instruct",
    num_speculative_tokens=5,
    speculative_max_model_len=2048,
    use_v2_block_manager=True,
)

# Option 2: Self-speculative (ngram-based draft)
llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    speculative_model="[ngram]",
    ngram_prompt_lookup_max=4,
    ngram_prompt_lookup_min=1,
    num_speculative_tokens=5,
    use_v2_block_manager=True,
)
# No draft model needed — uses ngram matching from the prompt itself
```

### Multi-Node Distributed Serving

```bash
# Node 0 (head)
ray start --head --port=6379

# Node 1 (worker)
ray start --address="node0:6379"

# Launch vLLM across both nodes
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-405B-Instruct \
    --tensor-parallel-size 8 \
    --pipeline-parallel-size 2 \
    --distributed-executor-backend ray
# Total: 16 GPUs across 2 nodes
```

---

## Engine Comparison & Benchmarks

### Throughput Comparison (Llama-3.1-70B, 4×A100-80GB)

| Engine | Throughput (tok/s) | TTFT (ms) | ITL (ms) | Quantization | Setup Difficulty |
|--------|--------------------|-----------|----------|-------------|-----------------|
| **vLLM** | 2,800 | 180 | 22 | AWQ/GPTQ/FP8 | ⭐ Easy |
| **TGI** | 2,400 | 200 | 25 | AWQ/GPTQ/EETQ | ⭐ Easy (Docker) |
| **TensorRT-LLM** | 3,500 | 120 | 18 | FP8/INT4/INT8 | ⭐⭐⭐ Hard |
| **SGLang** | 3,000 | 160 | 20 | AWQ/GPTQ | ⭐⭐ Medium |
| **DeepSpeed** | 2,200 | 250 | 28 | INT8/FP6 | ⭐⭐ Medium |
| **Naive PyTorch** | 120 | 3,000 | 85 | None | ⭐ Easy |

### Memory Efficiency (Llama-3.1-70B)

| Engine | FP16 Memory | Best Quantized | Min GPUs (80GB) |
|--------|------------|----------------|-----------------|
| vLLM | 140 GB | 35 GB (AWQ) | 2 (AWQ) / 4 (FP16) |
| TGI | 140 GB | 35 GB (AWQ) | 2 (AWQ) / 4 (FP16) |
| TensorRT-LLM | 140 GB | 35 GB (FP8) | 1 (FP8, H100) / 2 (FP16) |
| DeepSpeed | 140 GB + CPU | N/A (CPU offload) | 1 + 128GB RAM |

### Feature Matrix

| Feature | vLLM | TGI | TensorRT-LLM | SGLang | DeepSpeed |
|---------|------|-----|-------------|--------|-----------|
| PagedAttention | ✅ | ✅ | ✅ | ✅ | ❌ |
| Continuous Batching | ✅ | ✅ | ✅ | ✅ | ❌ |
| OpenAI API | ✅ | ✅ | ✅ (Triton) | ✅ | ❌ |
| Streaming | ✅ | ✅ | ✅ | ✅ | ❌ |
| Multi-LoRA | ✅ | ❌ | ✅ | ✅ | ❌ |
| Spec Decoding | ✅ | ✅ | ✅ | ✅ | ❌ |
| Prefix Caching | ✅ | ❌ | ✅ | ✅ (Radix) | ❌ |
| JSON Constrained | ✅ | ✅ | ❌ | ✅ | ❌ |
| CPU Offload | ❌ | ❌ | ❌ | ❌ | ✅ |
| Vision Models | ✅ | ✅ | ✅ | ✅ | ❌ |
| FP8 (H100) | ✅ | ❌ | ✅ | ✅ | ❌ |
| Production Ready | ✅✅ | ✅✅✅ | ✅✅✅ | ✅✅ | ✅ |

### When to Use What

| Scenario | Winner | Reason |
|----------|--------|--------|
| Maximum throughput, NVIDIA hardware | **TensorRT-LLM** | Custom NVIDIA kernels, FP8 |
| Fastest setup, OpenAI migration | **vLLM** | Drop-in API, 3-minute setup |
| Enterprise HuggingFace pipeline | **TGI** | Battle-tested, enterprise support |
| Complex multi-turn programs | **SGLang** | RadixAttention, frontend DSL |
| Massive models, limited GPUs | **DeepSpeed** | CPU/NVMe offloading |
| Structured JSON outputs | **SGLang** or **TGI** | Grammar constraints |
| Multi-LoRA serving | **vLLM** | Best LoRA management |

---

## Production Deployment Patterns

### Pattern 1: Single-Model High-Throughput

```
Client → Load Balancer → [vLLM Pod 1 (4×A100)]
                       → [vLLM Pod 2 (4×A100)]
                       → [vLLM Pod 3 (4×A100)]
```

### Pattern 2: Multi-Model Router

```
Client → API Gateway → Router (model selection)
                       → vLLM: Llama-70B (complex tasks)
                       → vLLM: Llama-8B (simple tasks)
                       → vLLM: CodeLlama-34B (code tasks)
```

### Pattern 3: LoRA-Based Multi-Tenant

```
Client → Auth → LoRA Router (tenant → adapter mapping)
             → vLLM (base model + 16 hot LoRA adapters)
             → CPU LoRA Cache (100+ cold adapters)
```

### Pattern 4: Speculative Decoding Pipeline

```
Client → vLLM Server
         ├── Draft Model (1B, GPU 0)
         └── Target Model (70B, GPU 1-3)
         → Verify → Accept/Reject → Stream tokens
```

---

## Best Practices

### 1. Memory Management
- Set `gpu_memory_utilization` to 0.90-0.95 (leave room for transient allocations)
- Enable prefix caching for chat applications (shared system prompts)
- Use AWQ quantization for best quality/memory tradeoff

### 2. Throughput Optimization
- Increase `max-num-seqs` (max concurrent requests) until GPU saturates
- Enable CUDA graphs (`enforce_eager=False`) for repeated input shapes
- Use continuous batching (default in vLLM, TGI, SGLang)
- Batch similar-length requests together when possible

### 3. Latency Optimization
- Enable speculative decoding for generation-heavy workloads
- Use tensor parallelism to reduce per-token latency
- Place GPUs on same NVLink fabric for TP communication
- Keep `max_model_len` as small as needed (less KV cache overhead)

### 4. Reliability
- Always set readiness/liveness probes in K8s
- Monitor GPU memory and request queue depth
- Implement circuit breakers for upstream services
- Use graceful shutdown (drain requests before pod termination)

### 5. Cost Optimization
- Use spot/preemptible instances for batch workloads
- Right-size GPU allocation (don't use 4×A100 for an 8B model)
- Quantize aggressively (AWQ/GPTQ) for cost-sensitive deployments
- Scale to zero during off-peak hours

---

## Common Pitfalls

### 1. OOM (Out of Memory)
**Symptom:** `CUDA out of memory` during inference
**Cause:** `max_model_len` too large, `gpu_memory_utilization` too high, or batch size too big
**Fix:** Reduce `max_model_len`, lower `gpu_memory_utilization` to 0.85, or use quantization

### 2. Slow TTFT (Time-to-First-Token)
**Symptom:** Users wait 2-5 seconds before tokens start streaming
**Cause:** Large input prompts hitting prefill bottleneck
**Fix:** Enable chunked prefill, reduce prompt length, or use prefix caching

### 3. Tokenizer Mismatch
**Symptom:** Garbage output, broken generation
**Cause:** Using wrong tokenizer or chat template
**Fix:** Always load tokenizer from the same model path; use `apply_chat_template()`

### 4. LoRA Loading Slowness
**Symptom:** First request to a new LoRA adapter takes 5-10 seconds
**Cause:** Loading from disk/S3 on first request
**Fix:** Pre-warm adapters at startup, increase `max_cpu_loras` for caching

### 5. Speculative Decoding Regression
**Symptom:** Speculative decoding is slower than normal decoding
**Cause:** Poor draft model (low acceptance rate), or short outputs (overhead > benefit)
**Fix:** Use a draft model from the same family, only enable for outputs > 100 tokens

### 6. Multi-GPU Communication Bottleneck
**Symptom:** 4-GPU TP is only 2x faster than 1 GPU (not 4x)
**Cause:** PCIe interconnect (not NVLink), high communication overhead
**Fix:** Use NVLink-connected GPUs, reduce TP degree, consider pipeline parallelism

---

## Further Reading

| Resource | URL |
|----------|-----|
| vLLM Paper | https://arxiv.org/abs/2309.06180 |
| PagedAttention Paper | https://arxiv.org/abs/2309.06180 |
| Flash Attention 2 | https://arxiv.org/abs/2307.08691 |
| TGI Documentation | https://huggingface.co/docs/text-generation-inference |
| TensorRT-LLM Docs | https://nvidia.github.io/TensorRT-LLM/ |
| SGLang Paper | https://arxiv.org/abs/2312.07104 |
| DeepSpeed-Inference | https://www.deepspeed.ai/inference/ |
| FP6-LLM Paper | https://arxiv.org/abs/2401.14112 |
| Speculative Decoding | https://arxiv.org/abs/2211.17192 |
| Continuous Batching (Orca) | https://www.usenix.org/conference/osdi22/presentation/yu |
| vLLM GitHub | https://github.com/vllm-project/vllm |
| SGLang GitHub | https://github.com/sgl-project/sglang |

---

*Last updated: March 2026*
