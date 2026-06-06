# Distributed Training: Complete Guide

## 1. What is Distributed Training?

Distributed training splits model training across multiple GPUs or machines to reduce wall-clock time and enable training models that don't fit on a single device.

| Strategy | What It Splits | When to Use |
|----------|---------------|-------------|
| **Data Parallelism (DP)** | Data batches across GPUs | Model fits on 1 GPU, want faster training |
| **Distributed Data Parallel (DDP)** | Data + gradient sync | Standard multi-GPU (2-8 GPUs) |
| **Fully Sharded Data Parallel (FSDP)** | Model params + gradients + optimizer | Model barely fits on 1 GPU |
| **Pipeline Parallelism** | Model layers across GPUs | Very deep models (100+ layers) |
| **Tensor Parallelism** | Individual layer weights across GPUs | Huge layers (e.g., 12288×49152 matrix) |
| **DeepSpeed ZeRO** | Progressive sharding (3 stages) | LLM training at any scale |
| **Expert Parallelism** | MoE experts across GPUs | Mixture-of-Experts models |

**Why it matters for trading:** Training XGBoost on 1M+ rows across 374 NSE symbols, or fine-tuning FinBERT on regulatory filings — distributed training cuts hours to minutes.

---

## 2. Data Parallelism (DP vs DDP)

### Naive DataParallel (DP) — Don't Use This
```python
import torch
import torch.nn as nn

model = MyModel()
# DP: Simple but SLOW (GIL bottleneck, GPU 0 as bottleneck)
model = nn.DataParallel(model)  # ❌ Avoid in production
output = model(input_data)
```

### Distributed Data Parallel (DDP) — Standard Approach
```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler

def train_ddp(rank, world_size):
    # Initialize process group
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

    # Model on this GPU
    model = MyModel().to(rank)
    model = DDP(model, device_ids=[rank])

    # Each GPU gets different data slice
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    loader = DataLoader(dataset, batch_size=32, sampler=sampler)

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    for epoch in range(10):
        sampler.set_epoch(epoch)  # Shuffle differently each epoch
        for batch in loader:
            batch = batch.to(rank)
            loss = model(batch).loss
            loss.backward()       # Gradients synced automatically via AllReduce
            optimizer.step()
            optimizer.zero_grad()

    dist.destroy_process_group()

# Launch: 4 GPUs
import torch.multiprocessing as mp
mp.spawn(train_ddp, args=(4,), nprocs=4)
```

### DDP with `torchrun` (Recommended)
```bash
# Single node, 4 GPUs
torchrun --nproc_per_node=4 train.py

# Multi-node (2 machines, 4 GPUs each = 8 GPUs total)
# Machine 0:
torchrun --nproc_per_node=4 --nnodes=2 --node_rank=0 \
    --master_addr=192.168.1.1 --master_port=29500 train.py

# Machine 1:
torchrun --nproc_per_node=4 --nnodes=2 --node_rank=1 \
    --master_addr=192.168.1.1 --master_port=29500 train.py
```

---

## 3. Fully Sharded Data Parallel (FSDP)

FSDP shards model parameters, gradients, AND optimizer states across GPUs — each GPU holds only **1/N** of the model.

```python
import torch
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy, MixedPrecision
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from transformers import AutoModelForCausalLM

def train_fsdp(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)

    model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")

    # Auto-wrap transformer layers
    wrap_policy = transformer_auto_wrap_policy(
        transformer_layer_cls={LlamaDecoderLayer}
    )

    # Mixed precision for memory efficiency
    mp_policy = MixedPrecision(
        param_dtype=torch.bfloat16,
        reduce_dtype=torch.bfloat16,
        buffer_dtype=torch.bfloat16,
    )

    model = FSDP(
        model,
        sharding_strategy=ShardingStrategy.FULL_SHARD,  # Shard everything
        mixed_precision=mp_policy,
        auto_wrap_policy=wrap_policy,
        device_id=rank,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    for batch in dataloader:
        loss = model(**batch).loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
```

### FSDP Sharding Strategies

| Strategy | What's Sharded | Memory Savings | Communication |
|----------|---------------|----------------|---------------|
| `FULL_SHARD` | Params + grads + optimizer | Maximum (1/N) | Highest |
| `SHARD_GRAD_OP` | Grads + optimizer only | Good (similar to ZeRO-2) | Medium |
| `NO_SHARD` | Nothing (like DDP) | None | Lowest |
| `HYBRID_SHARD` | Full within node, DDP across | Balanced | Moderate |

---

## 4. DeepSpeed ZeRO

DeepSpeed's ZeRO (Zero Redundancy Optimizer) progressively shards more state as you go from Stage 0 → 3.

### ZeRO Stages

| Stage | What's Partitioned | Memory per GPU (7B model) | Use Case |
|-------|-------------------|--------------------------|----------|
| **Stage 0** | Nothing (DDP) | 120 GB | Baseline |
| **Stage 1** | Optimizer states | 51 GB | 2-4 GPUs |
| **Stage 2** | + Gradients | 37 GB | 4-8 GPUs |
| **Stage 3** | + Parameters | 1.9 GB* | 8+ GPUs, huge models |
| **Stage 3 + Offload** | + CPU/NVMe offload | < 1 GB GPU | Single GPU, large model |

*Stage 3 gathers parameters on-demand for each forward/backward pass.

### DeepSpeed Configuration
```json
{
    "bf16": {"enabled": true},
    "zero_optimization": {
        "stage": 2,
        "allgather_partitions": true,
        "allgather_bucket_size": 2e8,
        "overlap_comm": true,
        "reduce_scatter": true,
        "reduce_bucket_size": 2e8,
        "contiguous_gradients": true
    },
    "gradient_accumulation_steps": 4,
    "gradient_clipping": 1.0,
    "train_batch_size": 128,
    "train_micro_batch_size_per_gpu": 8,
    "wall_clock_breakdown": false
}
```

### DeepSpeed with HuggingFace
```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./output",
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    bf16=True,
    deepspeed="ds_config.json",      # Point to config
    gradient_checkpointing=True,      # Save memory
    dataloader_num_workers=4,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)
trainer.train()
```

```bash
# Launch with DeepSpeed
deepspeed --num_gpus=4 train.py --deepspeed ds_config.json

# Multi-node
deepspeed --hostfile hostfile.txt --num_gpus=4 train.py
```

### ZeRO-Offload (Train 13B on Single GPU!)
```json
{
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        },
        "offload_param": {
            "device": "cpu",
            "pin_memory": true
        },
        "sub_group_size": 1e9,
        "stage3_max_live_parameters": 1e9
    }
}
```

---

## 5. Pipeline Parallelism

Split model **layers** across GPUs sequentially. GPU 0 runs layers 0-7, GPU 1 runs layers 8-15, etc.

```python
# GPipe-style: split into micro-batches to reduce bubble time
from deepspeed.pipe import PipelineModule, LayerSpec

class PipelineLLM(PipelineModule):
    def __init__(self, num_stages=4):
        layers = [
            LayerSpec(EmbeddingLayer, vocab_size=32000, hidden_size=4096),
            *[LayerSpec(TransformerBlock, hidden_size=4096) for _ in range(32)],
            LayerSpec(OutputHead, hidden_size=4096, vocab_size=32000),
        ]
        super().__init__(layers=layers, num_stages=num_stages)
```

**Pipeline Bubble Problem:** GPU 0 finishes forward pass and waits for GPU 3 to do backward — idle time.

| Technique | Bubble Reduction |
|-----------|-----------------|
| **Micro-batching (GPipe)** | Split batch into micro-batches, pipeline them |
| **1F1B (PipeDream)** | Interleave forward and backward passes |
| **Interleaved Pipeline** | Assign non-contiguous layers to reduce bubble |

---

## 6. Tensor Parallelism

Split individual **weight matrices** across GPUs. For a 4096×16384 weight: GPU 0 holds 4096×4096, GPU 1 holds next 4096×4096, etc.

```python
# Megatron-LM style tensor parallelism
# Column-parallel: split output dimension
class ColumnParallelLinear:
    """Each GPU computes partial output, then AllGather."""
    def __init__(self, in_features, out_features, world_size):
        self.weight = torch.randn(in_features, out_features // world_size)

    def forward(self, x):
        partial = x @ self.weight  # Each GPU: partial result
        return all_gather(partial)  # Combine across GPUs

# Row-parallel: split input dimension
class RowParallelLinear:
    """Each GPU has partial input, AllReduce to combine."""
    def __init__(self, in_features, out_features, world_size):
        self.weight = torch.randn(in_features // world_size, out_features)

    def forward(self, x_partial):
        partial = x_partial @ self.weight
        return all_reduce(partial)  # Sum across GPUs
```

---

## 7. Gradient Accumulation & Mixed Precision

### Gradient Accumulation (Simulate Larger Batches)
```python
accumulation_steps = 4
optimizer.zero_grad()

for i, batch in enumerate(dataloader):
    loss = model(batch).loss
    loss = loss / accumulation_steps   # Normalize
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()

# Effective batch size = micro_batch × accumulation × num_gpus
# = 8 × 4 × 4 = 128
```

### Mixed Precision Training (AMP)
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    optimizer.zero_grad()

    with autocast(dtype=torch.bfloat16):   # Forward in BF16
        loss = model(batch).loss

    scaler.scale(loss).backward()           # Backward in FP32
    scaler.step(optimizer)
    scaler.update()
```

| Precision | Memory | Speed | Stability |
|-----------|--------|-------|-----------|
| FP32 | Baseline | 1x | Best |
| FP16 + Loss Scaling | 50% less | 2x | Good (needs scaler) |
| BF16 | 50% less | 2x | Better (no scaler needed) |
| FP8 (H100) | 75% less | 3x | Experimental |

---

## 8. HuggingFace Accelerate (Simplest Multi-GPU)

```python
from accelerate import Accelerator

accelerator = Accelerator(
    mixed_precision="bf16",
    gradient_accumulation_steps=4,
)

model, optimizer, dataloader = accelerator.prepare(model, optimizer, dataloader)

for batch in dataloader:
    with accelerator.accumulate(model):
        loss = model(**batch).loss
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()
```

```bash
# Configure once
accelerate config
# Launch
accelerate launch --num_processes=4 train.py
```

### Accelerate Config File
```yaml
compute_environment: LOCAL_MACHINE
distributed_type: MULTI_GPU
num_machines: 1
num_processes: 4
mixed_precision: bf16
deepspeed_config:
  zero_stage: 2
  gradient_accumulation_steps: 4
  offload_optimizer_device: none
```

---

## 9. Multi-Node Training on Cloud

### GCP (Vertex AI)
```python
from google.cloud import aiplatform

aiplatform.init(project="ai-trading-prod", location="asia-south1")

job = aiplatform.CustomJob.from_local_script(
    display_name="finbert-distributed",
    script_path="train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1:latest",
    requirements=["transformers", "accelerate", "deepspeed"],
    machine_type="n1-standard-8",
    accelerator_type="NVIDIA_TESLA_V100",
    accelerator_count=4,
    replica_count=2,  # 2 nodes × 4 GPUs = 8 GPUs
)
job.run()
```

### AWS (SageMaker)
```python
from sagemaker.pytorch import PyTorch

estimator = PyTorch(
    entry_point="train.py",
    role=role,
    instance_count=2,
    instance_type="ml.p3.8xlarge",  # 4 V100s per node
    framework_version="2.1",
    distribution={"torch_distributed": {"enabled": True}},
    hyperparameters={"epochs": 10, "batch_size": 32},
)
estimator.fit({"train": s3_train_path})
```

---

## 10. Best Practices

1. **Start with DDP** — simplest, works for most models up to ~10B params on 8 GPUs
2. **Use gradient accumulation first** — increase effective batch size before adding GPUs
3. **Profile before distributing** — `torch.profiler` to find actual bottlenecks
4. **Communication backend** — NCCL for GPUs, Gloo for CPU
5. **Pin memory** — `DataLoader(pin_memory=True)` for faster GPU transfer
6. **Overlap compute + communication** — DeepSpeed does this by default
7. **Checkpoint regularly** — distributed training crashes are expensive
8. **Monitor GPU utilization** — target >80%; if lower, bottleneck is elsewhere

---

## 11. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| OOM on single GPU | Gradient accumulation → FSDP → ZeRO-3 Offload |
| Slow multi-node training | Check network bandwidth; use NCCL, not Gloo |
| Different results with more GPUs | Set seeds, use `DistributedSampler`, normalize loss by gradient accumulation steps |
| DataLoader hangs | Set `num_workers=0` to debug, then increase |
| GPU memory fragmentation | `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128` |
| Model.save() hangs | Save only on rank 0: `if dist.get_rank() == 0: model.save()` |

---

## 12. Choosing the Right Strategy

| Model Size | GPUs Available | Recommended Strategy |
|-----------|---------------|---------------------|
| < 1B params | 1-2 GPUs | DDP + gradient accumulation |
| 1-7B params | 4-8 GPUs | DDP + FSDP (FULL_SHARD) |
| 7-13B params | 8+ GPUs | DeepSpeed ZeRO-2 or FSDP |
| 13-70B params | 16-64 GPUs | ZeRO-3 + tensor parallelism |
| 70B+ params | 64+ GPUs | Megatron-LM (3D parallelism) |
| Any size, 1 GPU | 1 GPU | ZeRO-3 Offload + gradient checkpointing |
