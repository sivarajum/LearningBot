# 🏗️ Project 7: Distributed LLM Training Platform on GCP

> **Gen-ChitChat Initiative** — Alice (MIT) vs. Bob (Stanford) Architectural Design Session

***

## 📋 Project Description

Build infrastructure to train 7B–70B parameter models from scratch or continued pre-training on domain corpora. Requires sharding models across dozens of GPUs with efficient data pipelines. Deployed on **GCP** with Vertex AI Training, FSDP/DeepSpeed, and managed MLOps.

***

## 🏛️ System Architecture

```mermaid
flowchart TD
    DATA["📦 Raw Training Data\n500B Tokens\nCloud Storage Bucket"] --> PRE["Data Preprocessing\nTokenization\nHuggingFace Tokenizers\nCloud Dataflow"]
    PRE --> GCS["Cloud Storage\n+ Cloud Filestore\nHigh-Throughput NFS"]
    GCS --> DIST["Distributed Training Cluster\nVertex AI Training\na3-highgpu-8g × 8 nodes\n8×H100 per node = 64 GPUs"]
    DIST --> DS["DeepSpeed ZeRO-3\nOptimizer State Sharding\nGradient Checkpointing\nActivation Offloading"]
    DIST --> FSDP["PyTorch FSDP\nFully Sharded Data Parallel\nHybrid Sharding\nBackward Prefetch"]
    DS & FSDP --> MODEL["Keras / PyTorch Model\nTransformer Architecture\nMixed Precision BF16\nFlash Attention 2"]
    MODEL --> CKPT["Checkpoint Manager\nCloud Storage + Vertex AI Experiments\nAsync Checkpointing"]
    CKPT --> EVAL2["Evaluation\nPerplexity + Benchmarks\nHellaSwag / MMLU / HumanEval"]
    EVAL2 --> HUB["🤗 HuggingFace Hub\nModel Registry + Model Card\n+ Vertex AI Model Registry"]

    style DIST fill:#FF6B35,color:#fff
    style DS fill:#4A90D9,color:#fff
    style FSDP fill:#7B68EE,color:#fff
```

### 📐 DeepSpeed ZeRO Stages — Visualized

```mermaid
flowchart TD
    subgraph "ZeRO Stage 0: No Sharding (Data Parallel)"
        GPU0_S0["GPU 0\nFull Model + Optim + Grad\n💾 560 GB ❌"]
    end

    subgraph "ZeRO Stage 1: Shard Optimizer States"
        GPU0_S1["GPU 0\nFull Model + Grad\n+ 1/N Optimizer\n💾 220 GB"]
    end

    subgraph "ZeRO Stage 2: + Shard Gradients"
        GPU0_S2["GPU 0\nFull Model\n+ 1/N Optim + 1/N Grad\n💾 140 GB"]
    end

    subgraph "ZeRO Stage 3: + Shard Parameters"
        GPU0_S3["GPU 0\n1/N Model + 1/N Optim + 1/N Grad\n💾 8.75 GB ✅"]
    end

    GPU0_S0 --> GPU0_S1 --> GPU0_S2 --> GPU0_S3

    style GPU0_S0 fill:#E74C3C,color:#fff
    style GPU0_S3 fill:#27AE60,color:#fff
```

### 📐 FSDP Communication Pattern

```mermaid
sequenceDiagram
    participant GPU0 as GPU 0
    participant GPU1 as GPU 1
    participant GPU2 as GPU 2
    participant GPU3 as GPU 3

    Note over GPU0,GPU3: Forward Pass (Layer 1)
    GPU0->>GPU0: AllGather: Reconstruct full Layer 1 params
    GPU1->>GPU0: Send Layer 1 shard
    GPU2->>GPU0: Send Layer 1 shard
    GPU3->>GPU0: Send Layer 1 shard
    GPU0->>GPU0: Compute forward for Layer 1
    GPU0->>GPU0: Free reconstructed params (memory saved!)

    Note over GPU0,GPU3: Forward Pass (Layer 2)
    GPU0->>GPU0: AllGather: Reconstruct full Layer 2 params
    Note right of GPU0: Backward Prefetch:\nPre-fetch Layer 1 params\nfor backward pass

    Note over GPU0,GPU3: Backward Pass
    GPU0->>GPU0: Compute gradients
    GPU0->>GPU0: ReduceScatter: Each GPU gets 1/N gradient shard
    GPU0->>GPU0: Update local parameter shard with local optimizer
```

### 📐 Data Pipeline for Training

```mermaid
flowchart LR
    RAW["📄 Raw Text Corpus\n500B tokens\nCommon Crawl, Wikipedia,\nDomain-specific docs"] --> DEDUP["Deduplication\nMinHash + LSH\nCloud Dataflow"]
    DEDUP --> FILTER["Quality Filter\nPerplexity-based\nLanguage detection\nToxicity removal"]
    FILTER --> TOK["Tokenization\nBPE Tokenizer\n50K vocab\nHuggingFace Tokenizers"]
    TOK --> PACK["Sequence Packing\nPack short sequences\ninto max_length chunks\nNo PAD waste"]
    PACK --> SHARD["Shard into\n1024 Shards\n~500M tokens each\nArrow format"]
    SHARD --> GCS2["Cloud Storage\n+ Cloud Filestore\nMounted as NFS\n100+ GB/s throughput"]

    style DEDUP fill:#E74C3C,color:#fff
    style PACK fill:#27AE60,color:#fff
```

### 📐 MLOps Pipeline

```mermaid
flowchart TD
    subgraph "Vertex AI Pipelines"
        TRIGGER["Pipeline Trigger\nScheduled / Manual"]
        DATA_V["Data Validation\nSchema + Distribution Check"]
        TRAIN["Distributed Training\nDeepSpeed / FSDP\n8-node cluster"]
        EVAL3["Model Evaluation\nHellaSwag, MMLU, HumanEval\nPerplexity on holdout"]
        COMPARE["Model Comparison\nNew vs. Baseline\nStatistical significance"]
        REGISTER["Model Registry\nVertex AI Model Registry\nVersion + Lineage"]
        DEPLOY2["Deploy\nVertex AI Endpoint\nvLLM serving container"]
    end

    TRIGGER --> DATA_V --> TRAIN --> EVAL3 --> COMPARE
    COMPARE -->|"New > Baseline"| REGISTER --> DEPLOY2
    COMPARE -->|"New ≤ Baseline"| ALERT["Alert Team\n'Training did not improve'"]
```

***

## 🎙️ Tech Talk — Alice vs. Bob

### Round 1: DeepSpeed ZeRO-3 vs. PyTorch FSDP

**Alice (MIT):** "For **distributed training** at 70B scale, I'm using **DeepSpeed ZeRO Stage 3**. The math:
- FP16 model: 140 GB
- Optimizer states (Adam): 280 GB
- Gradients: 140 GB
- **Total: 560 GB**
- With 64 GPUs at ZeRO-3: **8.75 GB per GPU** ✅"

**Bob (Stanford):** "DeepSpeed has communication overhead — `AllGather` on every forward, `ReduceScatter` on every backward. **PyTorch FSDP** does the same sharding but natively integrated into PyTorch 2.0+. No external library. And FSDP's `backward_prefetch=BACKWARD_PRE` hides communication behind compute."

**Alice:** "DeepSpeed has **ZeRO-Infinity** — offload to CPU DRAM and NVMe SSDs. For 175B+ that doesn't fit in aggregate GPU memory, essential."

**Bob:** "ZeRO-Infinity is for extreme scale. For 7B–30B — 90% of enterprise training — FSDP is cleaner. And `hybrid_shard` shards intra-node (fast NVLink) but replicates inter-node (slower InfiniBand). Halves inter-node communication."

### Round 2: Hardware & GCP Infrastructure

**Alice:** "On GCP, **a3-highgpu-8g** — 8× H100 80GB, NVLink 4.0 (900 GB/s), inter-node GPUDirect-RDMA (3,200 Gbps). 8-node cluster = 64 GPUs, 5.12 TB aggregate."

**Bob:** "**Cloud Filestore** (managed NFS) for data loading — 100+ GB/s throughput. Regular Cloud Storage starves GPUs. GPU utilization must be >90% — anything less means data pipeline bottleneck."

**Alice:** "**Sequence packing** is the highest-ROI optimization. Instead of padding to 4096 tokens, pack 8 short sequences into one chunk. 8x more tokens per batch, free. Use proper attention masking so packed sequences don't attend to each other."

### Round 3: GPU Failure Management

**Bob:** "At 64 GPUs over 72 hours, ~15% probability of at least ONE GPU failure:
- **Hard failure**: GPU hangs, NCCL timeout
- **Soft failure**: ECC memory errors → NaN gradients → silent model corruption
- **Network failure**: InfiniBand drops 30 seconds, AllReduce hangs

Strategy: health checks every 1,000 steps, NaN detection after every backward pass, gradient clipping `max_grad_norm=1.0`, async checkpointing every 1,000 steps."

**Alice:** "Smart checkpointing: FSDP's `SHARDED_STATE_DICT` saves each GPU's shard independently (8 × 5GB vs one monolithic 280GB). Background thread saves while training continues. Keep last 3 + every 10th checkpoint. Validate before discarding predecessors."

### Round 4: Mixed Precision & Keras Monitoring

**Bob:** "**BF16** on H100, not FP16. BF16 has same range as FP32 (8 bits exponent) — no overflow, no loss scaling needed. One config line:
```python
mixed_precision=MixedPrecision(param_dtype=torch.bfloat16)
```
Saves 10-20 hours of NaN debugging vs FP16."

**Alice:** "**Keras callbacks** for monitoring: `CSVLogger` for per-step metrics, `TensorBoard` sent to Vertex AI, `ReduceLROnPlateau`, `EarlyStopping`. 5 lines of code vs. 50 lines of custom PyTorch logging. And `model.summary()` verifies FSDP is sharding correctly."

**Bob:** "Evaluation uses **HellaSwag** (commonsense), **MMLU** (multitask knowledge), **HumanEval** (code). Run via **Vertex AI Pipelines** after each training run. Auto-promote if statistically better (p < 0.05 on ≥2 benchmarks)."

***

## 📊 DeepSpeed ZeRO-3 vs. PyTorch FSDP

| Feature | **DeepSpeed ZeRO-3** | **PyTorch FSDP** |
|---|---|---|
| **Parameter Sharding** | ✅ Full | ✅ Full |
| **NVMe Offload** | ✅ ZeRO-Infinity | ❌ Not supported |
| **Hybrid Sharding** | ❌ Manual config | ✅ `hybrid_shard` strategy |
| **Integration** | External library | Native PyTorch 2.0+ |
| **Backward Prefetch** | ✅ Config-driven | ✅ Native `BACKWARD_PRE` |
| **Keras Compatibility** | Custom training loop | ✅ Native |
| **Best For** | 70B+, extreme scale | 7B–30B, clean codebase |

## 📊 GCP GPU Instance Types

| Instance | GPU | Memory | Interconnect | Cost/hr | Max Model |
|---|---|---|---|---|---|
| **a3-highgpu-8g** | 8× H100 80GB | 640 GB | NVLink 900 GB/s | ~$54/hr | ~70B |
| **a2-highgpu-8g** | 8× A100 80GB | 640 GB | NVLink 600 GB/s | ~$37/hr | ~30B |
| **g2-standard-96** | 8× L4 24GB | 192 GB | PCIe Gen4 | ~$14/hr | ~7B |

## 📊 Data Pipeline Optimizations

| Optimization | **Impact** | **Cost** |
|---|---|---|
| Cloud Filestore mount | GPU utilization: 60% → 95% | ~$500/month |
| Sequence Packing | 8x more tokens per batch | Free (code change) |
| Pre-tokenization | Data loading 10x faster | One-time (Cloud Dataflow) |
| 1024 shards | Parallel data loading | Free (data resharding) |

***

## 🏗️ GCP Architecture

```mermaid
flowchart TD
    subgraph "GCP Project"
        subgraph "Data Pipeline"
            GCS_R["Cloud Storage\nRaw Corpus"]
            DF3["Cloud Dataflow\nProcessing"]
            FILEST2["Cloud Filestore\nNFS Mount"]
        end

        subgraph "Training Cluster"
            VAI_T2["Vertex AI Training"]
            N_1["Node 1: 8×H100"]
            N_2["Node 2: 8×H100"]
            N_8["Node 8: 8×H100"]
            IB2["InfiniBand\n3200 Gbps"]
        end

        subgraph "MLOps"
            TB5["TensorBoard"]
            EXP4["Experiments"]
            PIPE2["Vertex AI Pipeline"]
            MR5["Model Registry"]
        end
    end

    GCS_R --> DF3 --> FILEST2
    FILEST2 --> N_1 & N_2 & N_8
    N_1 & N_2 & N_8 <--> IB2
    VAI_T2 --> TB5 & EXP4
    PIPE2 --> MR5
```

***

## 🔑 Key Takeaways

1. **FSDP for 7-30B, DeepSpeed for 70B+** — right tool for right scale
2. **hybrid_shard** halves inter-node communication — crucial for multi-node training
3. **Sequence packing is a free 8x speedup** — pack short sequences, don't pad them
4. **Cloud Filestore prevents GPU starvation** — data pipeline must NEVER be the bottleneck
5. **BF16 on H100** — no overflow, no loss scaling, saves 10-20 hours of debugging
6. **Keras callbacks in 5 lines** replace 50 lines of custom monitoring code

***

*← Back to [TODO.MD](./TODO.MD)*
