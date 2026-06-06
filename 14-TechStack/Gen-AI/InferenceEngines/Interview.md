# Inference Engines Interview Questions and Answers

## Beginner Level Questions

### Q1: What is an LLM inference engine and why do we need one?

**Answer:**

An inference engine is optimized software that serves LLM predictions at scale. Raw PyTorch/HuggingFace inference is too slow and memory-hungry for production.

| Aspect | Raw HuggingFace | Inference Engine (vLLM) |
|--------|----------------|------------------------|
| Throughput | 1-5 req/s | 50-200 req/s |
| Latency (first token) | 2-5s | 0.1-0.5s |
| Memory usage | 100% model size | 60-80% (KV cache opt) |
| Concurrent users | 1 | 100+ |

**Key engines:**
- **vLLM** — PagedAttention, continuous batching, highest throughput
- **TGI** (Text Generation Inference) — HuggingFace's production server
- **DeepSpeed-Inference** — Microsoft's distributed inference
- **TensorRT-LLM** — NVIDIA's GPU-optimized engine
- **SGLang** — Stanford's structured generation engine
- **llama.cpp** — CPU/Apple Silicon inference (GGUF format)

---

### Q2: What is continuous batching and why is it important?

**Answer:**

Traditional **static batching** waits for all requests to finish before returning ANY response. Continuous (dynamic) batching processes requests as they arrive and removes completed ones immediately.

```
Static Batching:
  Request A (10 tokens) ████████░░░░░░░░ waits for B
  Request B (50 tokens) ████████████████ done
  → A waited 40 extra tokens of time

Continuous Batching:
  Request A (10 tokens) ████████ → done immediately
  Request B (50 tokens) ████████████████ → done
  Request C (arrives during B) ░░░██████ → slots in
```

vLLM and TGI both use continuous batching — it provides **2-5x throughput improvement** over static batching.

---

### Q3: What is vLLM and what makes it fast?

**Answer:**

vLLM is an open-source inference engine from UC Berkeley. Its key innovation is **PagedAttention** — managing KV cache like virtual memory pages.

```python
# Install and run
pip install vllm

from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3.1-8B-Instruct")
params = SamplingParams(temperature=0.7, max_tokens=200)

outputs = llm.generate(["Explain quantum computing"], params)
print(outputs[0].outputs[0].text)
```

**Why vLLM is fast:**
1. **PagedAttention** — KV cache stored in non-contiguous blocks, ~95% memory utilization vs ~50% in naive approach
2. **Continuous batching** — new requests added mid-batch
3. **Tensor parallelism** — split model across GPUs
4. **Prefix caching** — reuse KV cache for shared prompt prefixes
5. **Speculative decoding** — draft model generates candidates, main model verifies

---

### Q4: What is the KV Cache and why does it matter?

**Answer:**

During autoregressive generation, each token depends on all previous tokens. Without caching, you'd recompute attention for ALL previous tokens at every step.

**KV Cache** stores the Key and Value tensors from previous tokens:
- Step 1: Compute K,V for token 1 → cache it
- Step 2: Compute K,V for token 2, reuse cached K,V for token 1
- Step N: Only compute K,V for new token, reuse cache for 1..N-1

**Memory impact:** For LLaMA 3.1 70B with 2048 token context:
- KV Cache = `2 × layers × heads × head_dim × seq_len × dtype_size`
- = 2 × 80 × 8 × 128 × 2048 × 2 bytes ≈ **6.7GB per request**

This is why PagedAttention (vLLM) matters — it avoids memory fragmentation of KV caches.

---

### Q5: What is DeepSpeed-Inference?

**Answer:**

Microsoft's DeepSpeed-Inference optimizes LLM serving with:

1. **Tensor parallelism** — split model layers across GPUs
2. **Kernel fusion** — combine multiple operations into one GPU kernel
3. **Quantization** — INT8/INT4 inference with minimal accuracy loss
4. **ZeRO-Inference** — offload parameters to CPU/NVMe for huge models

```python
import deepspeed
import torch
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-70B")

# DeepSpeed inference optimization
ds_model = deepspeed.init_inference(
    model,
    tensor_parallel={"tp_size": 4},  # 4 GPUs
    dtype=torch.float16,
    replace_with_kernel_inject=True,  # Fused kernels
)
```

---

## Intermediate Level Questions

### Q6: Compare vLLM vs TGI vs TensorRT-LLM for production deployment.

**Answer:**

| Feature | vLLM | TGI | TensorRT-LLM |
|---------|------|-----|---------------|
| **Developer** | UC Berkeley | HuggingFace | NVIDIA |
| **Key Innovation** | PagedAttention | Continuous Batching | GPU kernel optimization |
| **Throughput** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Latency** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ease of use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Model support** | Broad | Broad | NVIDIA GPUs only |
| **Quantization** | AWQ, GPTQ, FP8 | GPTQ, AWQ | FP8, INT8, INT4 |
| **Multi-GPU** | Tensor parallel | Tensor parallel | Tensor + Pipeline parallel |
| **OpenAI-compatible API** | ✅ Built-in | ✅ | ✅ via Triton |
| **Best for** | General production | HF ecosystem | Maximum perf on NVIDIA |

```bash
# vLLM server (OpenAI-compatible)
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --tensor-parallel-size 2

# TGI Docker
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-generation-inference \
  --model-id meta-llama/Llama-3.1-8B-Instruct

# TensorRT-LLM
trtllm-build --model_dir ./llama-3.1-8B --output_dir ./engine
```

---

### Q7: What is speculative decoding and how does it speed up inference?

**Answer:**

Normal autoregressive decoding generates **1 token per forward pass**. Speculative decoding uses a small **draft model** to generate K candidate tokens, then the large **target model** verifies them in a single pass.

```
Normal:  [token1] → [token2] → [token3] → [token4]  = 4 forward passes

Speculative:
  Draft model: [token1, token2, token3, token4] → 1 fast pass
  Target model: verify all 4 in 1 pass → accept 3, reject token4
  = 2 passes instead of 4  →  ~2x speedup
```

```python
# vLLM speculative decoding
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    speculative_model="meta-llama/Llama-3.1-8B-Instruct",
    num_speculative_tokens=5,
)
```

**Acceptance rate** depends on how well the draft model matches the target. Typically 60-80% of draft tokens are accepted → 1.5-2.5x speedup with zero quality loss.

---

### Q8: How does PagedAttention work in vLLM?

**Answer:**

Traditional KV cache allocation is **contiguous** — reserves max_seq_len of memory per request, wasting 60-80% on average.

PagedAttention borrows the **virtual memory/paging** concept from OS:

1. KV cache divided into fixed-size **blocks** (e.g., 16 tokens each)
2. Blocks allocated **on demand** as tokens are generated
3. Blocks can be **non-contiguous** in GPU memory
4. A **block table** maps logical positions to physical blocks
5. Completed requests free blocks for reuse

```
Traditional (wastes memory):
Request 1: [████████░░░░░░░░]  (8/16 tokens used, 50% waste)
Request 2: [████░░░░░░░░░░░░]  (4/16 tokens used, 75% waste)

PagedAttention (efficient):
Block pool: [B1][B2][B3][B4][B5][B6]...
Request 1: B1→B2 (8 tokens, 2 blocks, 0% waste)
Request 2: B3 (4 tokens, 1 block, minimal waste)
```

Result: **2-4x more concurrent requests** in the same GPU memory.

---

### Q9: How do you serve quantized models with inference engines?

**Answer:**

```python
# vLLM with AWQ quantized model
from vllm import LLM, SamplingParams

llm = LLM(
    model="TheBloke/Llama-3.1-70B-AWQ",
    quantization="awq",
    tensor_parallel_size=2,
    gpu_memory_utilization=0.9,
)

# vLLM with GPTQ
llm = LLM(
    model="TheBloke/Llama-3.1-70B-GPTQ",
    quantization="gptq",
)

# TensorRT-LLM with FP8
trtllm-build \
  --model_dir ./llama-3.1-70B \
  --output_dir ./engine_fp8 \
  --use_fp8 \
  --strongly_typed
```

| Quantization | Bits | Memory Savings | Quality Loss | Speed |
|-------------|------|---------------|-------------|-------|
| FP16 | 16 | Baseline | None | Baseline |
| FP8 | 8 | 50% | <1% | +20% faster |
| INT8 | 8 | 50% | 1-2% | +15% faster |
| AWQ (4-bit) | 4 | 75% | 2-3% | +10% faster |
| GPTQ (4-bit) | 4 | 75% | 2-4% | +5% faster |
| GGUF (2-6 bit) | 2-6 | 65-87% | 3-10% | CPU-friendly |

---

### Q10: What is SGLang and how is it different from vLLM?

**Answer:**

SGLang (Structured Generation Language) from Stanford focuses on **structured and constrained generation** — JSON schemas, regex patterns, and complex multi-call programs.

Key differentiators:
- **RadixAttention** — tree-based KV cache sharing for branching generations
- **Constrained decoding** — enforce JSON/regex output structure at decode time
- **Frontend language** — Python DSL for multi-turn LLM programs

```python
import sglang as sgl

@sgl.function
def multi_turn_qa(s, question):
    s += sgl.system("You are a helpful assistant.")
    s += sgl.user(question)
    s += sgl.assistant(sgl.gen("answer", max_tokens=256))
    s += sgl.user("Summarize your answer in one sentence.")
    s += sgl.assistant(sgl.gen("summary", max_tokens=64))

state = multi_turn_qa.run(question="Explain quantum computing")
print(state["summary"])
```

---

## Advanced Level Questions

### Q11: How do you design a multi-GPU inference architecture for 100+ concurrent users?

**Answer:**

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ vLLM     │ │ vLLM     │ │ vLLM     │
        │ Replica 1│ │ Replica 2│ │ Replica 3│
        │ (2×A100) │ │ (2×A100) │ │ (2×A100) │
        └──────────┘ └──────────┘ └──────────┘
```

Key decisions:
1. **Tensor parallelism within replica** — split model across 2-4 GPUs
2. **Data parallelism across replicas** — multiple independent instances behind load balancer
3. **Prefix caching** — share system prompt KV cache across requests
4. **Request routing** — route similar prompts to same replica for cache hits

```python
# Production vLLM deployment
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 4 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.92 \
    --enable-prefix-caching \
    --max-num-seqs 256 \
    --block-size 32
```

---

### Q12: How does FP8 inference work in TensorRT-LLM and what are the tradeoffs?

**Answer:**

FP8 (8-bit floating point) uses the E4M3 format on NVIDIA Hopper GPUs (H100):
- **E4M3**: 4-bit exponent, 3-bit mantissa — dynamic range of FP16 with INT8 throughput
- Per-tensor or per-channel scaling factors maintain accuracy

```
FP16: [1 sign][5 exponent][10 mantissa] = 16 bits
FP8:  [1 sign][4 exponent][3 mantissa]  = 8 bits
INT8: [1 sign][7 integer]               = 8 bits

FP8 advantages over INT8:
- No calibration dataset needed (unlike INT8 PTQ)
- Better handling of outlier activations
- Native hardware support on H100/H200
```

Performance on H100: FP8 provides ~1.8x throughput vs FP16 with <1% accuracy degradation.

---

### Q13: Explain prefix caching and how it reduces latency for RAG applications.

**Answer:**

In RAG, many requests share the same **system prompt + retrieved context**. Without prefix caching, each request recomputes KV cache for the shared prefix.

```
Request 1: [System Prompt (2K tokens)] + [Retrieved Docs (4K)] + [User Q (50)]
Request 2: [System Prompt (2K tokens)] + [Retrieved Docs (4K)] + [User Q (80)]
                    ↑ 6K tokens IDENTICAL ↑

Without prefix caching: 6K tokens recomputed per request
With prefix caching:    6K tokens computed ONCE, reused via hash lookup
```

vLLM automatic prefix caching:
```python
llm = LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    enable_prefix_caching=True,
)
# First request computes full KV cache
# Subsequent requests with same prefix → instant reuse
# Speedup: 3-10x for long shared prefixes
```

---

### Q14: How do you benchmark and compare inference engines?

**Answer:**

```python
# Key metrics to measure:
# 1. TTFT — Time To First Token (latency)
# 2. TPOT — Time Per Output Token (throughput per token)
# 3. Throughput — tokens/second across all concurrent requests
# 4. Memory — peak GPU VRAM usage

# Benchmarking with vLLM's built-in benchmark
python -m vllm.entrypoints.openai.api_server --model MODEL &

python benchmark_serving.py \
    --model MODEL \
    --num-prompts 1000 \
    --request-rate 10 \  # 10 requests/second
    --max-tokens 200

# Compare engines on same hardware:
# H100 80GB, LLaMA 3.1 70B, 1000 requests, avg 200 output tokens
# Engine       | Throughput  | TTFT   | TPOT
# vLLM         | 4500 tok/s  | 120ms  | 22ms
# TGI          | 3800 tok/s  | 150ms  | 26ms
# TensorRT-LLM | 5200 tok/s  | 90ms   | 19ms
# SGLang       | 4800 tok/s  | 110ms  | 21ms
```
