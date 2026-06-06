# Distributed Training: Visual Guide

## 1. Distributed Training Strategy Overview

```mermaid
graph TB
    subgraph DT["🚀 Distributed Training Strategies"]
        direction TB
        DP["📊 Data Parallelism<br/>Split batches across GPUs"]
        MP["🧩 Model Parallelism<br/>Split model across GPUs"]
        HP["⚡ Hybrid Parallelism<br/>Combine both"]
    end

    DP --> DDP["DDP<br/>Full model per GPU"]
    DP --> FSDP["FSDP<br/>Sharded model per GPU"]
    DP --> ZERO["DeepSpeed ZeRO<br/>Progressive sharding"]

    MP --> PP["Pipeline Parallel<br/>Split by layers"]
    MP --> TP["Tensor Parallel<br/>Split by weights"]

    HP --> THREE["3D Parallelism<br/>TP + PP + DP"]
    HP --> MEG["Megatron-LM<br/>NVIDIA reference"]

    style DT fill:#1a1a2e,color:#fff,stroke:#e94560
    style DP fill:#0f3460,color:#fff,stroke:#16213e
    style MP fill:#533483,color:#fff,stroke:#16213e
    style HP fill:#e94560,color:#fff,stroke:#16213e
    style DDP fill:#3498db,color:#fff
    style FSDP fill:#2ecc71,color:#fff
    style ZERO fill:#e67e22,color:#fff
    style PP fill:#9b59b6,color:#fff
    style TP fill:#e74c3c,color:#fff
    style THREE fill:#f39c12,color:#fff
    style MEG fill:#1abc9c,color:#fff
```

## 2. DDP Communication Flow (AllReduce)

```mermaid
sequenceDiagram
    participant G0 as 🖥️ GPU 0
    participant G1 as 🖥️ GPU 1
    participant G2 as 🖥️ GPU 2
    participant G3 as 🖥️ GPU 3

    Note over G0,G3: 📥 Each GPU processes different data batch

    G0->>G0: Forward + Backward (grad₀)
    G1->>G1: Forward + Backward (grad₁)
    G2->>G2: Forward + Backward (grad₂)
    G3->>G3: Forward + Backward (grad₃)

    Note over G0,G3: 🔄 AllReduce: Ring-based gradient sync

    G0->>G1: Send partial grad
    G1->>G2: Send partial grad
    G2->>G3: Send partial grad
    G3->>G0: Send partial grad

    Note over G0,G3: ✅ All GPUs now have averaged gradients

    G0->>G0: optimizer.step() (identical update)
    G1->>G1: optimizer.step() (identical update)
    G2->>G2: optimizer.step() (identical update)
    G3->>G3: optimizer.step() (identical update)

    Note over G0,G3: 🎯 All GPUs have identical model weights
```

## 3. DeepSpeed ZeRO Stages Memory Breakdown

```mermaid
graph LR
    subgraph S0["Stage 0: DDP<br/>112 GB/GPU"]
        P0["📦 Params 28GB"]
        G0["📐 Grads 28GB"]
        O0["⚙️ Optimizer 56GB"]
    end

    subgraph S1["Stage 1: Shard Optimizer<br/>63 GB/GPU"]
        P1["📦 Params 28GB"]
        G1["📐 Grads 28GB"]
        O1["⚙️ Optim 7GB<br/>÷8 GPUs"]
    end

    subgraph S2["Stage 2: + Shard Grads<br/>31.5 GB/GPU"]
        P2["📦 Params 28GB"]
        G2["📐 Grads 3.5GB<br/>÷8 GPUs"]
        O2["⚙️ Optim 7GB<br/>÷8 GPUs"]
    end

    subgraph S3["Stage 3: + Shard Params<br/>14 GB/GPU"]
        P3["📦 Params 3.5GB<br/>÷8 GPUs"]
        G3["📐 Grads 3.5GB<br/>÷8 GPUs"]
        O3["⚙️ Optim 7GB<br/>÷8 GPUs"]
    end

    S0 -->|"44% savings"| S1
    S1 -->|"72% savings"| S2
    S2 -->|"87% savings"| S3

    style S0 fill:#e74c3c,color:#fff
    style S1 fill:#e67e22,color:#fff
    style S2 fill:#f1c40f,color:#000
    style S3 fill:#2ecc71,color:#fff
    style P0 fill:#c0392b,color:#fff
    style P1 fill:#d35400,color:#fff
    style P2 fill:#f39c12,color:#000
    style P3 fill:#27ae60,color:#fff
    style G0 fill:#c0392b,color:#fff
    style G1 fill:#d35400,color:#fff
    style G2 fill:#f39c12,color:#000
    style G3 fill:#27ae60,color:#fff
    style O0 fill:#c0392b,color:#fff
    style O1 fill:#d35400,color:#fff
    style O2 fill:#f39c12,color:#000
    style O3 fill:#27ae60,color:#fff
```

## 4. Pipeline Parallelism: Micro-Batch Scheduling

```mermaid
gantt
    title Pipeline Parallelism — GPipe vs 1F1B Schedule
    dateFormat X
    axisFormat %s

    section GPU 0 (Layers 0-7)
    F0-mb1 :active, f01, 0, 1
    F0-mb2 :active, f02, 1, 2
    F0-mb3 :active, f03, 2, 3
    F0-mb4 :active, f04, 3, 4
    Bubble  :crit, b0, 4, 8
    B0-mb4 :done, b04, 8, 9
    B0-mb3 :done, b03, 9, 10
    B0-mb2 :done, b02, 10, 11
    B0-mb1 :done, b01, 11, 12

    section GPU 1 (Layers 8-15)
    Bubble  :crit, w1, 0, 1
    F1-mb1 :active, f11, 1, 2
    F1-mb2 :active, f12, 2, 3
    F1-mb3 :active, f13, 3, 4
    F1-mb4 :active, f14, 4, 5
    Bubble  :crit, b1, 5, 7
    B1-mb4 :done, b14, 7, 8
    B1-mb3 :done, b13, 8, 9
    B1-mb2 :done, b12, 9, 10
    B1-mb1 :done, b11, 10, 11

    section GPU 2 (Layers 16-23)
    Bubble  :crit, w2, 0, 2
    F2-mb1 :active, f21, 2, 3
    F2-mb2 :active, f22, 3, 4
    F2-mb3 :active, f23, 4, 5
    F2-mb4 :active, f24, 5, 6
    B2-mb4 :done, b24, 6, 7
    B2-mb3 :done, b23, 7, 8
    B2-mb2 :done, b22, 8, 9
    B2-mb1 :done, b21, 9, 10

    section GPU 3 (Layers 24-31)
    Bubble  :crit, w3, 0, 3
    F3-mb1 :active, f31, 3, 4
    F3-mb2 :active, f32, 4, 5
    F3-mb3 :active, f33, 5, 6
    F3-mb4 :active, f34, 6, 7
    B3-mb4 :done, b34, 5, 6
    B3-mb3 :done, b33, 6, 7
    B3-mb2 :done, b32, 7, 8
    B3-mb1 :done, b31, 8, 9
```

## 5. FSDP vs DDP vs DeepSpeed Decision Guide

```mermaid
flowchart TD
    START["🤔 How to distribute training?"] --> Q1{"Model fits<br/>on 1 GPU?"}

    Q1 -->|"✅ Yes"| Q2{"Need faster<br/>training?"}
    Q1 -->|"❌ No"| Q3{"Single node<br/>or multi-node?"}

    Q2 -->|"Yes"| DDP["✅ Use DDP<br/>Simplest, fastest"]
    Q2 -->|"No, just 1 GPU"| GA["✅ Gradient Accumulation<br/>+ Mixed Precision"]

    Q3 -->|"Single node"| Q4{"Model size?"}
    Q3 -->|"Multi-node"| Q5{"Need CPU/NVMe<br/>offload?"}

    Q4 -->|"< 30B"| FSDP["✅ Use FSDP<br/>PyTorch native"]
    Q4 -->|"> 30B"| DS3["✅ DeepSpeed ZeRO-3<br/>Maximum sharding"]

    Q5 -->|"Yes"| DSO["✅ ZeRO-Offload<br/>or ZeRO-Infinity"]
    Q5 -->|"No"| Q6{"Prefer native<br/>PyTorch?"}

    Q6 -->|"Yes"| FSDP2["✅ FSDP FULL_SHARD"]
    Q6 -->|"No, want features"| DS2["✅ DeepSpeed ZeRO-2/3"]

    style START fill:#1a1a2e,color:#fff,stroke:#e94560
    style DDP fill:#2ecc71,color:#fff,stroke:#27ae60
    style GA fill:#3498db,color:#fff,stroke:#2980b9
    style FSDP fill:#27ae60,color:#fff,stroke:#1e8449
    style DS3 fill:#e67e22,color:#fff,stroke:#d35400
    style DSO fill:#e74c3c,color:#fff,stroke:#c0392b
    style FSDP2 fill:#2ecc71,color:#fff,stroke:#27ae60
    style DS2 fill:#f39c12,color:#fff,stroke:#e67e22
    style Q1 fill:#8e44ad,color:#fff
    style Q2 fill:#8e44ad,color:#fff
    style Q3 fill:#8e44ad,color:#fff
    style Q4 fill:#8e44ad,color:#fff
    style Q5 fill:#8e44ad,color:#fff
    style Q6 fill:#8e44ad,color:#fff
```

## 6. 3D Parallelism Layout (64 GPUs)

```mermaid
graph TB
    subgraph Cluster["🌐 64 GPU Cluster: TP=4 × PP=4 × DP=4"]
        subgraph N0["Node 0 — DP Rank 0"]
            subgraph TP0["TP Group (Layers 0-7)"]
                G00["GPU 0<br/>¼ weights"]
                G01["GPU 1<br/>¼ weights"]
                G02["GPU 2<br/>¼ weights"]
                G03["GPU 3<br/>¼ weights"]
            end
            subgraph TP1["TP Group (Layers 8-15)"]
                G04["GPU 4"]
                G05["GPU 5"]
                G06["GPU 6"]
                G07["GPU 7"]
            end
        end

        subgraph N1["Node 1 — DP Rank 0"]
            subgraph TP2["TP Group (Layers 16-23)"]
                G10["GPU 8"]
                G11["GPU 9"]
                G12["GPU 10"]
                G13["GPU 11"]
            end
            subgraph TP3["TP Group (Layers 24-31)"]
                G14["GPU 12"]
                G15["GPU 13"]
                G16["GPU 14"]
                G17["GPU 15"]
            end
        end
    end

    TP0 -->|"Pipeline"| TP1
    TP1 -->|"Pipeline"| TP2
    TP2 -->|"Pipeline"| TP3

    style Cluster fill:#1a1a2e,color:#fff,stroke:#e94560
    style N0 fill:#0f3460,color:#fff
    style N1 fill:#0f3460,color:#fff
    style TP0 fill:#e94560,color:#fff
    style TP1 fill:#f39c12,color:#fff
    style TP2 fill:#2ecc71,color:#fff
    style TP3 fill:#3498db,color:#fff
    style G00 fill:#c0392b,color:#fff
    style G01 fill:#c0392b,color:#fff
    style G02 fill:#c0392b,color:#fff
    style G03 fill:#c0392b,color:#fff
    style G04 fill:#d35400,color:#fff
    style G05 fill:#d35400,color:#fff
    style G06 fill:#d35400,color:#fff
    style G07 fill:#d35400,color:#fff
    style G10 fill:#27ae60,color:#fff
    style G11 fill:#27ae60,color:#fff
    style G12 fill:#27ae60,color:#fff
    style G13 fill:#27ae60,color:#fff
    style G14 fill:#2980b9,color:#fff
    style G15 fill:#2980b9,color:#fff
    style G16 fill:#2980b9,color:#fff
    style G17 fill:#2980b9,color:#fff
```

## 7. Mixed Precision & Memory Optimization

```mermaid
graph TD
    subgraph MEM["💾 GPU Memory Optimization Stack"]
        L1["Layer 1: Mixed Precision<br/>FP32 → BF16 = 50% memory"]
        L2["Layer 2: Gradient Accumulation<br/>Simulate 8× batch = same memory"]
        L3["Layer 3: Gradient Checkpointing<br/>Recompute activations = √N memory"]
        L4["Layer 4: FSDP / ZeRO Sharding<br/>Split across N GPUs = 1/N memory"]
        L5["Layer 5: CPU Offload<br/>Move optimizer to RAM"]
        L6["Layer 6: NVMe Offload<br/>Move params to SSD"]
    end

    L1 -->|"Still OOM?"| L2
    L2 -->|"Still OOM?"| L3
    L3 -->|"Still OOM?"| L4
    L4 -->|"Still OOM?"| L5
    L5 -->|"Still OOM?"| L6

    L1 -.->|"50% saved"| S1["Can train 2× model"]
    L3 -.->|"60% saved"| S2["Can train 3× depth"]
    L4 -.->|"87% saved"| S3["Can train 8× model"]
    L6 -.->|"99% saved"| S4["Train 70B on 1 GPU"]

    style MEM fill:#1a1a2e,color:#fff,stroke:#e94560
    style L1 fill:#2ecc71,color:#fff
    style L2 fill:#27ae60,color:#fff
    style L3 fill:#f39c12,color:#fff
    style L4 fill:#e67e22,color:#fff
    style L5 fill:#e74c3c,color:#fff
    style L6 fill:#c0392b,color:#fff
    style S1 fill:#3498db,color:#fff
    style S2 fill:#3498db,color:#fff
    style S3 fill:#3498db,color:#fff
    style S4 fill:#3498db,color:#fff
```

## 8. Framework Comparison

```mermaid
graph TB
    subgraph Frameworks["🔧 Distributed Training Frameworks"]
        direction LR
        subgraph Native["PyTorch Native"]
            DDP2["DDP"]
            FSDP3["FSDP"]
        end
        subgraph Microsoft["Microsoft"]
            DS["DeepSpeed"]
            ORT["ONNX Runtime"]
        end
        subgraph NVIDIA["NVIDIA"]
            MEG2["Megatron-LM"]
            NEMO["NeMo"]
        end
        subgraph HL["High-Level"]
            ACC["🤗 Accelerate"]
            LIT["⚡ Lightning"]
            COLOSS["Colossal-AI"]
        end
    end

    ACC -->|wraps| DDP2
    ACC -->|wraps| FSDP3
    ACC -->|wraps| DS
    LIT -->|wraps| DDP2
    LIT -->|wraps| DS

    style Frameworks fill:#1a1a2e,color:#fff,stroke:#e94560
    style Native fill:#3498db,color:#fff
    style Microsoft fill:#e67e22,color:#fff
    style NVIDIA fill:#2ecc71,color:#fff
    style HL fill:#9b59b6,color:#fff
    style DDP2 fill:#2980b9,color:#fff
    style FSDP3 fill:#2980b9,color:#fff
    style DS fill:#d35400,color:#fff
    style ORT fill:#d35400,color:#fff
    style MEG2 fill:#27ae60,color:#fff
    style NEMO fill:#27ae60,color:#fff
    style ACC fill:#8e44ad,color:#fff
    style LIT fill:#8e44ad,color:#fff
    style COLOSS fill:#8e44ad,color:#fff
```

## 9. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Foundations"]
        A1["Single GPU Training<br/>Mixed Precision + AMP"]
        A2["Gradient Accumulation<br/>Simulate larger batches"]
        A3["Gradient Checkpointing<br/>Trade compute for memory"]
    end

    subgraph W2["📘 Week 2: Multi-GPU"]
        B1["DDP Setup<br/>torchrun, DistributedSampler"]
        B2["HuggingFace Accelerate<br/>Simple multi-GPU wrapper"]
        B3["Profiling<br/>torch.profiler, nvidia-smi"]
    end

    subgraph W3["📙 Week 3: Large Models"]
        C1["FSDP<br/>Parameter sharding"]
        C2["DeepSpeed ZeRO<br/>Stages 1-2-3"]
        C3["CPU/NVMe Offload<br/>ZeRO-Infinity"]
    end

    subgraph W4["📕 Week 4: Expert Level"]
        D1["3D Parallelism<br/>TP + PP + DP"]
        D2["Megatron-LM<br/>NVIDIA reference impl"]
        D3["Fault Tolerance<br/>Elastic training, checkpoints"]
    end

    W1 --> W2 --> W3 --> W4

    style W1 fill:#2ecc71,color:#fff
    style W2 fill:#3498db,color:#fff
    style W3 fill:#e67e22,color:#fff
    style W4 fill:#e74c3c,color:#fff
    style A1 fill:#27ae60,color:#fff
    style A2 fill:#27ae60,color:#fff
    style A3 fill:#27ae60,color:#fff
    style B1 fill:#2980b9,color:#fff
    style B2 fill:#2980b9,color:#fff
    style B3 fill:#2980b9,color:#fff
    style C1 fill:#d35400,color:#fff
    style C2 fill:#d35400,color:#fff
    style C3 fill:#d35400,color:#fff
    style D1 fill:#c0392b,color:#fff
    style D2 fill:#c0392b,color:#fff
    style D3 fill:#c0392b,color:#fff
```
