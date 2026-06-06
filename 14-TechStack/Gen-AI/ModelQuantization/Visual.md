# Model Quantization: Visual Guide & Architecture Diagrams

> **Comprehensive visual reference** for model quantization methods, pipelines, comparisons, and decision frameworks using Mermaid diagrams.

---

## Table of Contents

- [1. Quantization Methods Taxonomy](#1-quantization-methods-taxonomy)
- [2. GPTQ Pipeline Flow](#2-gptq-pipeline-flow)
- [3. AWQ Pipeline Flow](#3-awq-pipeline-flow)
- [4. Memory Comparison](#4-memory-comparison-by-model-size-and-precision)
- [5. Quality vs Speed Tradeoff](#5-quality-vs-speed-tradeoff)
- [6. Deployment Options](#6-deployment-options-architecture)
- [7. Decision Tree](#7-decision-tree-which-quantization-method-to-use)
- [8. Learning Path](#8-learning-path)

---

## 1. Quantization Methods Taxonomy

```mermaid
graph TB
    ROOT["🔢 Model Quantization Methods"]

    ROOT --> PTQ["📦 Post-Training Quantization<br/>(PTQ)"]
    ROOT --> QAT["🎓 Quantization-Aware Training<br/>(QAT)"]
    ROOT --> MP["⚡ Mixed Precision"]

    PTQ --> WEIGHT["Weight-Only Quantization"]
    PTQ --> WA["Weight + Activation<br/>Quantization"]

    WEIGHT --> GPTQ["🔵 GPTQ<br/>Hessian-based<br/>INT4/INT8<br/>GPU deployment"]
    WEIGHT --> AWQ["🟢 AWQ<br/>Activation-aware<br/>INT4<br/>GPU deployment"]
    WEIGHT --> GGUF["🟡 GGUF<br/>llama.cpp format<br/>Q2-Q8 variants<br/>CPU/hybrid"]
    WEIGHT --> BNB["🟣 bitsandbytes<br/>NF4/FP4/INT8<br/>QLoRA base"]

    WA --> SMOOTH["SmoothQuant<br/>W8A8<br/>Migrate difficulty<br/>to weights"]
    WA --> FP8Q["FP8 Quantization<br/>W8A8 (float)<br/>H100 native<br/>support"]

    QAT --> QLORA["🔴 QLoRA<br/>NF4 base + LoRA<br/>Most practical<br/>for fine-tuning"]
    QAT --> LLMQAT["LLM-QAT<br/>Data-free distillation<br/>Full QAT for LLMs"]
    QAT --> PEFTQAT["PEFT-QAT<br/>Quantize + train<br/>subset of params"]

    MP --> LLMINT8["LLM.int8()<br/>Outlier decomposition<br/>FP16 outliers + INT8 rest"]
    MP --> LAYER["Layer-wise Mixing<br/>Critical layers: FP16<br/>Others: INT4/INT8"]
    MP --> W4A16["W4A16<br/>Weights: INT4<br/>Activations: FP16"]

    style ROOT fill:#1a1a2e,stroke:#e94560,color:#fff
    style PTQ fill:#16213e,stroke:#0f3460,color:#fff
    style QAT fill:#16213e,stroke:#0f3460,color:#fff
    style MP fill:#16213e,stroke:#0f3460,color:#fff
    style GPTQ fill:#0f3460,stroke:#53a8b6,color:#fff
    style AWQ fill:#0f3460,stroke:#53a8b6,color:#fff
    style GGUF fill:#0f3460,stroke:#53a8b6,color:#fff
    style QLORA fill:#0f3460,stroke:#e94560,color:#fff
```

---

## 2. GPTQ Pipeline Flow

```mermaid
flowchart TD
    START["🚀 Full-Precision Model<br/>(FP32/FP16)"] --> CALIB["📊 Calibration Phase"]

    CALIB --> LOAD_DATA["Load Calibration Dataset<br/>(128-256 samples from C4/Pile)"]
    LOAD_DATA --> FWD["Forward Pass<br/>Collect activation statistics X"]

    FWD --> HESSIAN["🧮 Hessian Computation<br/>H = 2 · Xᵀ · X<br/>per linear layer"]

    HESSIAN --> CHOLESKY["Cholesky Decomposition<br/>H + λI = LLᵀ<br/>(dampening for stability)"]

    CHOLESKY --> LAYER_LOOP["⚙️ Layer-by-Layer Quantization"]

    LAYER_LOOP --> COL_LOOP["For each column block<br/>(group_size = 128)"]

    COL_LOOP --> QUANT_W["1. Quantize weight w_j<br/>ŵ_j = round(w_j / scale) × scale"]
    QUANT_W --> CALC_ERR["2. Compute error<br/>δ_j = w_j - ŵ_j"]
    CALC_ERR --> COMPENSATE["3. Compensate remaining<br/>w_{j+1:} -= δ_j · (H_{j,j+1:} / H_{j,j})"]
    COMPENSATE --> NEXT_COL{"More columns<br/>in block?"}

    NEXT_COL -->|Yes| COL_LOOP
    NEXT_COL -->|No| LAZY_UPDATE["4. Lazy Batch Update<br/>Apply accumulated error<br/>to remaining blocks"]

    LAZY_UPDATE --> NEXT_LAYER{"More layers?"}
    NEXT_LAYER -->|Yes| LAYER_LOOP
    NEXT_LAYER -->|No| SAVE["💾 Save Quantized Model"]

    SAVE --> OUTPUT["Quantized Model<br/>• INT4/INT8 weights<br/>• Scale + zero-point per group<br/>• 2-4x smaller"]

    OUTPUT --> VALIDATE["✅ Validate Quality<br/>• Perplexity check<br/>• Benchmark tasks<br/>• Compare to FP16 baseline"]

    style START fill:#2d3436,stroke:#00b894,color:#fff
    style HESSIAN fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style CHOLESKY fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style COMPENSATE fill:#e17055,stroke:#fab1a0,color:#fff
    style OUTPUT fill:#00b894,stroke:#55efc4,color:#fff
    style VALIDATE fill:#0984e3,stroke:#74b9ff,color:#fff
```

### GPTQ Key Parameters

```mermaid
graph LR
    PARAMS["GPTQ Parameters"] --> BITS["bits: 4 or 8<br/>Target precision"]
    PARAMS --> GS["group_size: 128<br/>Weights sharing<br/>same scale/zero-point"]
    PARAMS --> DA["desc_act: True/False<br/>Reorder by activation<br/>magnitude (slower, better)"]
    PARAMS --> DAMP["damp_percent: 0.01<br/>Hessian dampening<br/>for numerical stability"]
    PARAMS --> SYM["sym: True/False<br/>Symmetric vs<br/>asymmetric quant"]

    BITS --> |"4-bit"| SMALL["3.5GB per 7B params<br/>~3% PPL degradation"]
    BITS --> |"8-bit"| MEDIUM["7GB per 7B params<br/>~0.5% PPL degradation"]

    style PARAMS fill:#2d3436,stroke:#6c5ce7,color:#fff
```

---

## 3. AWQ Pipeline Flow

```mermaid
flowchart TD
    START["🚀 Full-Precision Model"] --> OBSERVE["📊 Observe Activations"]

    OBSERVE --> RUN_CALIB["Run calibration data<br/>(128 samples)"]
    RUN_CALIB --> MEASURE["Measure per-channel<br/>activation magnitudes<br/>|x_c| for each channel c"]

    MEASURE --> IDENTIFY["🎯 Identify Salient Channels"]

    IDENTIFY --> SALIENT["Salient Channels<br/>(large |x_c|)<br/>~1% of channels"]
    IDENTIFY --> NORMAL["Normal Channels<br/>(small |x_c|)<br/>~99% of channels"]

    SALIENT --> SCALE_UP["Scale UP weights<br/>w_c × s_c (s > 1)<br/>↓ Relative quant error"]
    NORMAL --> DIRECT["Direct quantization<br/>Standard INT4 rounding"]

    SCALE_UP --> GRID["Grid Search<br/>Find optimal s_c per channel<br/>to minimize output error"]

    GRID --> QUANT_ALL["Quantize ALL weights<br/>to INT4 uniformly"]
    DIRECT --> QUANT_ALL

    QUANT_ALL --> STORE_SCALES["Store scaling factors<br/>with quantized weights"]

    STORE_SCALES --> INFERENCE["⚡ Inference Time"]

    INFERENCE --> DEQ["Dequantize weights<br/>ŵ = INT4_val × scale"]
    DEQS["Scale down activations<br/>x_c / s_c"] --> MATMUL
    DEQ --> MATMUL["Matrix Multiply<br/>ŵ · (x/s) = output"]
    INFERENCE --> DEQS

    MATMUL --> OUTPUT["✅ Output<br/>Preserved quality for<br/>salient channels"]

    style START fill:#2d3436,stroke:#00b894,color:#fff
    style IDENTIFY fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style SALIENT fill:#e17055,stroke:#fab1a0,color:#fff
    style GRID fill:#fdcb6e,stroke:#f39c12,color:#333
    style OUTPUT fill:#00b894,stroke:#55efc4,color:#fff
```

### AWQ vs GPTQ Comparison

```mermaid
graph TB
    subgraph AWQ ["🟢 AWQ"]
        A1["Activation-aware scaling"]
        A2["~10 min quantization (7B)"]
        A3["Simple INT4 kernels"]
        A4["No Hessian computation"]
        A5["Slightly better PPL"]
        A6["GEMM kernel optimized"]
    end

    subgraph GPTQ ["🔵 GPTQ"]
        G1["Hessian-based compensation"]
        G2["~30 min quantization (7B)"]
        G3["Requires Cholesky decomp"]
        G4["Column-wise error correction"]
        G5["Excellent PPL"]
        G6["desc_act option for quality"]
    end

    subgraph SHARED ["✅ Both Support"]
        S1["4-bit and 8-bit"]
        S2["vLLM integration"]
        S3["HuggingFace Transformers"]
        S4["Group size 128"]
        S5["SafeTensors format"]
    end

    style AWQ fill:#00b894,stroke:#55efc4,color:#fff
    style GPTQ fill:#0984e3,stroke:#74b9ff,color:#fff
    style SHARED fill:#636e72,stroke:#b2bec3,color:#fff
```

---

## 4. Memory Comparison by Model Size and Precision

```mermaid
graph TD
    subgraph MEM7B ["📊 7B Parameter Model"]
        FP32_7["FP32: 28 GB"]
        FP16_7["FP16: 14 GB"]
        INT8_7["INT8: 7 GB"]
        INT4_7["INT4: 3.5 GB"]
    end

    subgraph MEM13B ["📊 13B Parameter Model"]
        FP32_13["FP32: 52 GB"]
        FP16_13["FP16: 26 GB"]
        INT8_13["INT8: 13 GB"]
        INT4_13["INT4: 6.5 GB"]
    end

    subgraph MEM70B ["📊 70B Parameter Model"]
        FP32_70["FP32: 280 GB"]
        FP16_70["FP16: 140 GB"]
        INT8_70["INT8: 70 GB"]
        INT4_70["INT4: 35 GB"]
    end

    subgraph GPU_FIT ["🖥️ GPU Memory Fit"]
        RTX3090["RTX 3090: 24 GB"]
        RTX4090["RTX 4090: 24 GB"]
        A10G["A10G: 24 GB"]
        A100_40["A100-40: 40 GB"]
        A100_80["A100-80: 80 GB"]
        H100["H100: 80 GB"]
    end

    INT4_7 -.->|"✅ Fits"| RTX3090
    INT4_13 -.->|"✅ Fits"| RTX3090
    FP16_7 -.->|"✅ Fits"| RTX3090
    INT4_70 -.->|"✅ Fits"| A100_40
    FP16_70 -.->|"❌ Needs 2x"| A100_80

    style MEM7B fill:#2d3436,stroke:#00b894,color:#fff
    style MEM13B fill:#2d3436,stroke:#0984e3,color:#fff
    style MEM70B fill:#2d3436,stroke:#e17055,color:#fff
    style GPU_FIT fill:#636e72,stroke:#b2bec3,color:#fff
```

### Memory Formula

```mermaid
graph LR
    FORMULA["Memory (GB) = Parameters × Bytes_per_param / 10⁹"]

    FORMULA --> FP32["FP32: 4 bytes<br/>7B × 4 = 28 GB"]
    FORMULA --> FP16["FP16: 2 bytes<br/>7B × 2 = 14 GB"]
    FORMULA --> INT8["INT8: 1 byte<br/>7B × 1 = 7 GB"]
    FORMULA --> INT4["INT4: 0.5 bytes<br/>7B × 0.5 = 3.5 GB"]

    FORMULA --> OVERHEAD["+ KV Cache overhead<br/>+ Activation memory<br/>+ Framework overhead<br/>≈ 10-20% extra"]

    style FORMULA fill:#6c5ce7,stroke:#a29bfe,color:#fff
```

---

## 5. Quality vs Speed Tradeoff

```mermaid
quadrantChart
    title Quality vs Inference Speed (7B LLaMA-2)
    x-axis Low Speed --> High Speed
    y-axis Low Quality --> High Quality
    quadrant-1 Ideal Zone
    quadrant-2 Quality-First
    quadrant-3 Avoid
    quadrant-4 Speed-First
    FP16 Baseline: [0.30, 0.95]
    INT8 SmoothQuant: [0.55, 0.92]
    GPTQ 4-bit: [0.70, 0.85]
    AWQ 4-bit: [0.75, 0.87]
    GGUF Q4_K_M CPU: [0.15, 0.83]
    GGUF Q5_K_S CPU: [0.12, 0.88]
    NF4 bitsandbytes: [0.45, 0.82]
    GGUF Q2_K CPU: [0.20, 0.55]
    FP8 H100: [0.65, 0.93]
```

### Detailed Quality Metrics

```mermaid
graph TB
    subgraph QUALITY ["📈 Quality Metrics (LLaMA-2-7B)"]
        direction TB
        Q_TABLE["
        Method         | PPL  | MMLU  | HumanEval
        ─────────────────────────────────────────
        FP16 baseline  | 5.47 | 46.1% | 14.0%
        FP8 (H100)     | 5.48 | 46.0% | 13.9%
        AWQ 4-bit      | 5.60 | 45.5% | 13.1%
        GPTQ 4-bit     | 5.63 | 45.2% | 12.8%
        GGUF Q4_K_M    | 5.68 | 44.8% | 12.2%
        NF4 (QLoRA)    | 5.70 | 44.5% | 12.0%
        RTN 4-bit      | 6.85 | 38.2% | 8.5%
        "]
    end

    subgraph SPEED ["⚡ Speed Metrics (tokens/sec)"]
        direction TB
        S_TABLE["
        Method         | A100  | RTX4090 | CPU (M2)
        ─────────────────────────────────────────────
        FP16           | 52    | 35      | 2
        FP8 (H100)     | 85    | N/A     | N/A
        AWQ + vLLM     | 105   | 72      | N/A
        GPTQ + vLLM    | 95    | 65      | N/A
        GGUF Q4_K_M    | N/A   | 55*     | 22
        GGUF Q5_K_S    | N/A   | 48*     | 18
        * = llama.cpp with GPU offload
        "]
    end

    style QUALITY fill:#2d3436,stroke:#00b894,color:#fff
    style SPEED fill:#2d3436,stroke:#0984e3,color:#fff
```

---

## 6. Deployment Options Architecture

```mermaid
flowchart TB
    MODEL["Quantized Model"] --> GPU_PATH["🖥️ GPU Deployment"]
    MODEL --> CPU_PATH["💻 CPU Deployment"]
    MODEL --> HYBRID["🔄 Hybrid (GPU+CPU)"]

    GPU_PATH --> VLLM["vLLM<br/>• PagedAttention<br/>• Continuous batching<br/>• AWQ/GPTQ/FP8<br/>• Best throughput"]
    GPU_PATH --> TGI["TGI (HuggingFace)<br/>• Docker-native<br/>• AWQ/GPTQ<br/>• Flash Attention<br/>• Good for HF models"]
    GPU_PATH --> TRTLLM["TensorRT-LLM<br/>• NVIDIA optimized<br/>• FP8/INT8/INT4<br/>• Triton Inference Server<br/>• Maximum GPU utilization"]
    GPU_PATH --> DEEPSPEED["DeepSpeed-Inference<br/>• ZeRO-Inference<br/>• Multi-GPU<br/>• INT8/FP16<br/>• Azure integration"]

    CPU_PATH --> LLAMACPP["llama.cpp<br/>• GGUF format<br/>• Q2-Q8 variants<br/>• ARM NEON, AVX2<br/>• Minimal dependencies"]
    CPU_PATH --> ONNX["ONNX Runtime<br/>• Cross-platform<br/>• INT8/INT4<br/>• Mobile/Edge<br/>• DirectML, CUDA, CPU"]
    CPU_PATH --> CTRANS["CTransformers<br/>• Python bindings<br/>• GGUF support<br/>• LangChain integration"]

    HYBRID --> OLLAMA["Ollama<br/>• llama.cpp based<br/>• Docker-friendly<br/>• Auto GPU offload<br/>• Easiest setup"]
    HYBRID --> EXLLAMAV2["ExLlamaV2<br/>• Custom GPTQ kernels<br/>• Mixed GPU+CPU<br/>• Interactive speeds"]

    VLLM --> PROD_GPU["Production Targets"]
    TGI --> PROD_GPU
    TRTLLM --> PROD_GPU

    LLAMACPP --> PROD_CPU["Edge / Local"]
    OLLAMA --> PROD_CPU

    PROD_GPU --> LB["Load Balancer<br/>(nginx/envoy)"]
    LB --> API["OpenAI-Compatible API<br/>/v1/chat/completions<br/>/v1/completions"]

    style MODEL fill:#2d3436,stroke:#6c5ce7,color:#fff
    style VLLM fill:#00b894,stroke:#55efc4,color:#fff
    style LLAMACPP fill:#fdcb6e,stroke:#f39c12,color:#333
    style OLLAMA fill:#0984e3,stroke:#74b9ff,color:#fff
```

### Deployment Decision Matrix

```mermaid
graph TB
    subgraph MATRIX ["📋 Engine × Format Compatibility"]
        direction TB
        TABLE["
        Engine        | AWQ | GPTQ | GGUF | FP8 | BnB | FP16
        ──────────────────────────────────────────────────────
        vLLM          | ✅  | ✅   | 🔬   | ✅  | ✅  | ✅
        TGI           | ✅  | ✅   | ❌   | ✅  | ❌  | ✅
        TensorRT-LLM  | ❌  | ✅   | ❌   | ✅  | ❌  | ✅
        llama.cpp     | ❌  | ❌   | ✅   | ❌  | ❌  | ✅
        DeepSpeed     | ❌  | ❌   | ❌   | ❌  | ❌  | ✅
        ONNX Runtime  | ❌  | ❌   | ❌   | ❌  | ❌  | ✅
        ExLlamaV2     | ❌  | ✅   | ❌   | ❌  | ❌  | ❌
        Ollama        | ❌  | ❌   | ✅   | ❌  | ❌  | ❌

        🔬 = Experimental   ✅ = Supported   ❌ = Not supported
        "]
    end

    style MATRIX fill:#2d3436,stroke:#b2bec3,color:#fff
```

---

## 7. Decision Tree: Which Quantization Method to Use

```mermaid
flowchart TD
    START["🤔 Need to quantize<br/>an LLM?"] --> Q1{"What's the<br/>deployment target?"}

    Q1 -->|"GPU Server<br/>(Cloud)"| GPU_Q{"Need to<br/>fine-tune?"}
    Q1 -->|"Consumer GPU<br/>(Local)"| CONSUMER_Q{"VRAM<br/>available?"}
    Q1 -->|"CPU Only"| CPU_Q{"Priority?"}
    Q1 -->|"Mobile / Edge"| EDGE["GGUF Q4_0<br/>via llama.cpp<br/>or ONNX INT4"]

    GPU_Q -->|"Yes"| QLORA_REC["✅ QLoRA<br/>NF4 + LoRA<br/>bitsandbytes"]
    GPU_Q -->|"No"| GPU_PRIORITY{"Priority?"}

    GPU_PRIORITY -->|"Max throughput"| AWQ_REC["✅ AWQ + vLLM<br/>Best tokens/sec"]
    GPU_PRIORITY -->|"Max quality"| GPTQ_DESC["✅ GPTQ (desc_act=True)<br/>+ vLLM"]
    GPU_PRIORITY -->|"Near-FP16 quality"| FP8_REC["✅ FP8 (H100/Ada)<br/>Native hardware"]
    GPU_PRIORITY -->|"Easy setup"| BNB_REC["✅ bitsandbytes INT8<br/>Just load_in_8bit=True"]

    CONSUMER_Q -->|"24 GB"| C24{"Model size?"}
    CONSUMER_Q -->|"16 GB"| C16["GGUF Q4_K_M<br/>with GPU offload<br/>(up to 13B)"]
    CONSUMER_Q -->|"8 GB"| C8["GGUF Q3_K_M<br/>or Q2_K<br/>(up to 7B)"]

    C24 -->|"≤ 13B"| AWQ_C["AWQ/GPTQ 4-bit<br/>Fits entirely in VRAM"]
    C24 -->|"70B"| GGUF_SPLIT["GGUF Q4_K_M<br/>Split: 40 layers GPU<br/>+ rest on CPU"]

    CPU_Q -->|"Speed"| GGUF_FAST["✅ GGUF Q4_K_M<br/>Best speed/quality"]
    CPU_Q -->|"Quality"| GGUF_QUAL["✅ GGUF Q5_K_S<br/>or Q6_K"]
    CPU_Q -->|"Min memory"| GGUF_SMALL["GGUF Q2_K<br/>⚠️ Significant<br/>quality loss"]

    style START fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style AWQ_REC fill:#00b894,stroke:#55efc4,color:#fff
    style GPTQ_DESC fill:#0984e3,stroke:#74b9ff,color:#fff
    style QLORA_REC fill:#e17055,stroke:#fab1a0,color:#fff
    style GGUF_FAST fill:#fdcb6e,stroke:#f39c12,color:#333
    style FP8_REC fill:#00b894,stroke:#55efc4,color:#fff
```

---

## 8. Learning Path

```mermaid
graph TB
    subgraph WEEK1 ["📅 Week 1: Foundations"]
        W1A["Understand data types<br/>FP32, FP16, BF16, INT8, INT4"]
        W1B["Load model with<br/>bitsandbytes 4-bit/8-bit"]
        W1C["Compare memory usage<br/>FP16 vs INT8 vs INT4"]
        W1A --> W1B --> W1C
    end

    subgraph WEEK2 ["📅 Week 2: GPTQ & AWQ"]
        W2A["Quantize a model<br/>with AutoGPTQ"]
        W2B["Quantize with AutoAWQ"]
        W2C["Compare quality:<br/>GPTQ vs AWQ vs FP16"]
        W2D["Understand calibration<br/>datasets"]
        W2A --> W2B --> W2C --> W2D
    end

    subgraph WEEK3 ["📅 Week 3: GGUF & Serving"]
        W3A["Convert model to GGUF"]
        W3B["Run with llama.cpp<br/>and Ollama"]
        W3C["Deploy with vLLM<br/>(OpenAI API server)"]
        W3D["Deploy with TGI<br/>(Docker)"]
        W3A --> W3B --> W3C --> W3D
    end

    subgraph WEEK4 ["📅 Week 4: Advanced"]
        W4A["QLoRA fine-tuning<br/>NF4 + LoRA adapters"]
        W4B["Mixed-precision inference<br/>LLM.int8() outlier decomp"]
        W4C["Production deployment<br/>Load balancing, monitoring"]
        W4D["Benchmark & compare<br/>All methods on your task"]
        W4A --> W4B --> W4C --> W4D
    end

    WEEK1 --> WEEK2 --> WEEK3 --> WEEK4

    WEEK4 --> EXPERT["🏆 Expert Level"]

    EXPERT --> E1["GPTQ internals<br/>Hessian, Cholesky"]
    EXPERT --> E2["Custom quant kernels<br/>CUDA, Triton"]
    EXPERT --> E3["FP6/FP8 formats<br/>Hardware co-design"]
    EXPERT --> E4["Multi-model serving<br/>A/B testing quant methods"]

    style WEEK1 fill:#2d3436,stroke:#00b894,color:#fff
    style WEEK2 fill:#2d3436,stroke:#0984e3,color:#fff
    style WEEK3 fill:#2d3436,stroke:#fdcb6e,color:#fff
    style WEEK4 fill:#2d3436,stroke:#e17055,color:#fff
    style EXPERT fill:#6c5ce7,stroke:#a29bfe,color:#fff
```

### QLoRA Training Pipeline

```mermaid
flowchart LR
    BASE["Base Model<br/>(LLaMA-2-7B)<br/>FP16: 14GB"] --> QUANT["Quantize to NF4<br/>bitsandbytes<br/>~3.8GB"]

    QUANT --> FREEZE["Freeze Base<br/>Weights"]

    FREEZE --> LORA["Add LoRA<br/>Adapters<br/>(~0.12% params)"]

    subgraph TRAINING ["Training Loop"]
        FWD["Forward<br/>(NF4 → BF16 → compute)"]
        LOSS["Compute Loss"]
        BWD["Backward<br/>(gradients through<br/>LoRA only)"]
        UPDATE["Update LoRA<br/>weights (BF16)"]
        FWD --> LOSS --> BWD --> UPDATE
        UPDATE -.->|next batch| FWD
    end

    LORA --> TRAINING

    TRAINING --> SAVE["Save LoRA<br/>Adapters<br/>(~300MB)"]

    SAVE --> MERGE["Merge into<br/>Base Model<br/>(FP16)"]

    MERGE --> DEPLOY_GPTQ["Re-quantize<br/>with GPTQ/AWQ<br/>for deployment"]

    style BASE fill:#636e72,stroke:#b2bec3,color:#fff
    style QUANT fill:#6c5ce7,stroke:#a29bfe,color:#fff
    style TRAINING fill:#2d3436,stroke:#00b894,color:#fff
    style SAVE fill:#00b894,stroke:#55efc4,color:#fff
    style DEPLOY_GPTQ fill:#0984e3,stroke:#74b9ff,color:#fff
```

### Data Type Precision Spectrum

```mermaid
graph LR
    subgraph SPECTRUM ["📏 Precision Spectrum (Bits per Parameter)"]
        direction LR
        FP32["FP32<br/>32 bits<br/>🟢 Training gold std"]
        BF16["BF16<br/>16 bits<br/>🟢 Training + Inference"]
        FP16["FP16<br/>16 bits<br/>🟢 Inference baseline"]
        FP8["FP8<br/>8 bits<br/>🟡 H100 native"]
        INT8["INT8<br/>8 bits<br/>🟡 SmoothQuant"]
        FP6["FP6<br/>6 bits<br/>🟠 Custom kernels"]
        Q5["Q5_K<br/>~5.5 bits<br/>🟠 GGUF variant"]
        NF4["NF4<br/>4 bits<br/>🔴 QLoRA"]
        INT4["INT4<br/>4 bits<br/>🔴 GPTQ/AWQ"]
        Q2["Q2_K<br/>~2.6 bits<br/>⛔ Emergency only"]

        FP32 --- BF16 --- FP16 --- FP8 --- INT8 --- FP6 --- Q5 --- NF4 --- INT4 --- Q2
    end

    style SPECTRUM fill:#1a1a2e,stroke:#e94560,color:#fff
    style FP32 fill:#00b894,stroke:#55efc4,color:#fff
    style BF16 fill:#00b894,stroke:#55efc4,color:#fff
    style FP16 fill:#00b894,stroke:#55efc4,color:#fff
    style FP8 fill:#fdcb6e,stroke:#f39c12,color:#333
    style INT8 fill:#fdcb6e,stroke:#f39c12,color:#333
    style NF4 fill:#e17055,stroke:#fab1a0,color:#fff
    style INT4 fill:#e17055,stroke:#fab1a0,color:#fff
    style Q2 fill:#d63031,stroke:#ff7675,color:#fff
```
