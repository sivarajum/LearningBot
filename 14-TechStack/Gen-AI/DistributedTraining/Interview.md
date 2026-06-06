# Distributed Training: Interview Questions

## Beginner Level

### Q1: What is the difference between Data Parallelism and Model Parallelism?
**Answer:**

| Aspect | Data Parallelism | Model Parallelism |
|--------|-----------------|-------------------|
| **What's split** | Data batches | Model layers/weights |
| **Each GPU has** | Full model copy | Part of the model |
| **Communication** | Gradient sync (AllReduce) | Activations between layers |
| **When to use** | Model fits on 1 GPU | Model too large for 1 GPU |
| **Example** | DDP, FSDP | Pipeline, Tensor Parallelism |

```python
# Data Parallel: each GPU processes different data, same model
# GPU 0: batch[0:32], GPU 1: batch[32:64], GPU 2: batch[64:96]
model = DDP(model, device_ids=[rank])

# Pipeline Parallel: different layers on different GPUs
# GPU 0: layers[0:8], GPU 1: layers[8:16], GPU 2: layers[16:24]
```

---

### Q2: Why is DDP preferred over DataParallel?
**Answer:**

```python
# ❌ DataParallel (DP) — AVOID
model = nn.DataParallel(model)
# Problems:
# 1. GIL bottleneck — single Python process
# 2. GPU 0 bottleneck — gathers all outputs, computes loss
# 3. Redundant data transfer — scatter input, gather output every step
# 4. Memory imbalance — GPU 0 uses more memory

# ✅ DistributedDataParallel (DDP) — USE THIS
model = DDP(model, device_ids=[rank])
# Advantages:
# 1. Multi-process — one process per GPU, no GIL
# 2. AllReduce — efficient gradient sync, no single bottleneck
# 3. Overlap — communication overlaps with backward pass
# 4. Equal memory — all GPUs hold identical model replica
```

DDP is **20-50% faster** than DP on 4+ GPUs.

---

### Q3: What is gradient accumulation and when do you use it?
**Answer:**

Gradient accumulation simulates larger batch sizes without needing more GPU memory.

```python
accumulation_steps = 8  # Simulate 8× larger batch

for i, batch in enumerate(dataloader):
    loss = model(batch).loss / accumulation_steps  # Normalize
    loss.backward()  # Accumulate gradients (don't step yet)

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()       # Now update weights
        optimizer.zero_grad()  # Reset gradients

# Effective batch: micro_batch × accumulation × GPUs
# = 4 × 8 × 4 = 128
```

**Use when:** You need large batch sizes (e.g., contrastive learning needs 4096+) but GPU memory only fits batch_size=4.

---

### Q4: Explain mixed precision training (FP16/BF16).
**Answer:**

Mixed precision uses lower precision (16-bit) for most operations while keeping critical ops in FP32:

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()  # Prevents underflow in FP16

for batch in loader:
    optimizer.zero_grad()
    with autocast(dtype=torch.float16):  # Forward in FP16
        loss = model(batch).loss
    scaler.scale(loss).backward()        # Backward: gradients in FP32
    scaler.step(optimizer)
    scaler.update()
```

| Type | Bits | Range | Use |
|------|------|-------|-----|
| FP32 | 32 | ±3.4e38 | Master weights, loss scaling |
| FP16 | 16 | ±65504 | Forward/backward (needs scaler) |
| BF16 | 16 | ±3.4e38 | Forward/backward (A100+, no scaler needed) |

**BF16 is preferred** on modern GPUs (A100, H100) — same range as FP32, no loss scaling needed.

---

### Q5: What is NCCL and why is it important?
**Answer:**

**NCCL** (NVIDIA Collective Communications Library) is the communication backend for GPU-to-GPU data transfer.

```python
# Initialize with NCCL backend (for GPU training)
dist.init_process_group(backend="nccl")

# Alternative backends:
# "gloo" — CPU training, or GPU fallback
# "mpi" — traditional HPC
```

NCCL implements collective operations efficiently:
- **AllReduce** — Sum gradients across all GPUs (used by DDP)
- **AllGather** — Gather sharded parameters (used by FSDP/ZeRO-3)
- **ReduceScatter** — Reduce + scatter in single op (used by ZeRO-2)
- **Broadcast** — Send from one GPU to all (used for initialization)

NCCL uses NVLink (900 GB/s) within a node and InfiniBand (400 Gb/s) across nodes.

---

## Intermediate Level

### Q6: Explain DeepSpeed ZeRO stages 1, 2, and 3.
**Answer:**

ZeRO progressively shards training state to reduce per-GPU memory:

```
7B parameter model (FP32 training):
- Parameters: 28 GB
- Gradients: 28 GB  
- Optimizer (Adam): 56 GB (momentum + variance)
- Total: 112 GB per GPU in DDP

ZeRO Stage 1: Shard optimizer → 28 + 28 + 56/N per GPU
ZeRO Stage 2: + Shard gradients → 28 + 28/N + 56/N per GPU  
ZeRO Stage 3: + Shard parameters → 28/N + 28/N + 56/N per GPU
```

With 8 GPUs:
| Stage | Per GPU Memory | Reduction |
|-------|---------------|-----------|
| DDP (no ZeRO) | 112 GB | 0% |
| Stage 1 | 63 GB | 44% |
| Stage 2 | 31.5 GB | 72% |
| Stage 3 | 14 GB | 87% |

**Stage 3 tradeoff:** Parameters must be gathered before each forward/backward → more communication. Use `overlap_comm=true` to hide latency.

---

### Q7: How does FSDP compare to DeepSpeed ZeRO?
**Answer:**

| Aspect | FSDP | DeepSpeed ZeRO |
|--------|------|----------------|
| **Framework** | PyTorch native (torch.distributed) | Microsoft (separate library) |
| **Stages** | FULL_SHARD ≈ ZeRO-3, SHARD_GRAD_OP ≈ ZeRO-2 | ZeRO 0/1/2/3 + Offload |
| **CPU Offload** | Basic support | Mature (ZeRO-Offload, ZeRO-Infinity) |
| **NVMe Offload** | No | Yes (ZeRO-Infinity) |
| **HuggingFace** | Via Accelerate | Via `deepspeed` argument |
| **Activation checkpointing** | `checkpoint_wrapper` | Built-in `activation_checkpointing` |
| **Maturity** | Growing (PyTorch 2.0+) | Battle-tested (3+ years) |

```python
# FSDP
model = FSDP(model, sharding_strategy=ShardingStrategy.FULL_SHARD)

# DeepSpeed ZeRO-3 (via config)
training_args = TrainingArguments(deepspeed="ds_z3_config.json")
```

**My recommendation:** Use FSDP for new projects (native PyTorch, simpler). Use DeepSpeed if you need CPU/NVMe offload or ZeRO-Infinity.

---

### Q8: What is gradient checkpointing and when should you use it?
**Answer:**

Gradient checkpointing trades compute for memory: instead of storing all activations for backward pass, recompute them.

```python
from torch.utils.checkpoint import checkpoint

class TransformerBlock(nn.Module):
    def forward(self, x):
        # Without checkpointing: stores all intermediate activations
        # With checkpointing: stores only input, recomputes rest in backward
        return checkpoint(self._forward, x, use_reentrant=False)

    def _forward(self, x):
        x = self.attention(x)
        x = self.feedforward(x)
        return x

# In HuggingFace:
model.gradient_checkpointing_enable()

# In TrainingArguments:
args = TrainingArguments(gradient_checkpointing=True)
```

| | Without Checkpointing | With Checkpointing |
|-|----------------------|-------------------|
| Memory | O(N layers) | O(√N layers) |
| Compute | 1× forward + 1× backward | 1× forward + ~1.33× backward |
| Speedup | Faster per step | ~25% slower per step but can use larger batch |

**Use when:** OOM errors. The 25% slowdown is worth it if it lets you double batch size.

---

### Q9: How do you handle checkpointing in distributed training?
**Answer:**

Only save on rank 0 (or use distributed saving for FSDP/ZeRO-3):

```python
# DDP: Save on rank 0 only
if dist.get_rank() == 0:
    torch.save({
        "model": model.module.state_dict(),  # .module to unwrap DDP
        "optimizer": optimizer.state_dict(),
        "epoch": epoch,
        "step": step,
    }, f"checkpoint_epoch{epoch}.pt")
dist.barrier()  # Wait for save to finish

# FSDP: Use StateDictType for efficient saving
from torch.distributed.fsdp import StateDictType

with FSDP.state_dict_type(model, StateDictType.FULL_STATE_DICT):
    state_dict = model.state_dict()
    if rank == 0:
        torch.save(state_dict, "checkpoint.pt")

# DeepSpeed: Built-in saving
model_engine.save_checkpoint("checkpoints/", tag=f"step_{step}")
```

---

### Q10: How do you debug distributed training issues?
**Answer:**

```python
# 1. Start with 1 GPU to verify logic
CUDA_VISIBLE_DEVICES=0 python train.py

# 2. Use NCCL debug logging
NCCL_DEBUG=INFO torchrun --nproc_per_node=2 train.py

# 3. Print on specific rank
if dist.get_rank() == 0:
    print(f"Loss: {loss.item()}, LR: {optimizer.param_groups[0]['lr']}")

# 4. Check for hanging (timeout debug)
dist.init_process_group("nccl", timeout=timedelta(minutes=5))

# 5. Verify all ranks have same loss (gradient sync working)
loss_tensor = torch.tensor([loss.item()]).cuda()
dist.all_reduce(loss_tensor)
if dist.get_rank() == 0:
    print(f"Sum of losses across ranks: {loss_tensor.item()}")
    # Should be: single_loss × world_size

# 6. Memory profiling
torch.cuda.memory_summary(device=rank)
```

Common issues:
| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Hangs at init | Firewall blocking ports | Open port 29500, check MASTER_ADDR |
| All GPUs same data | Missing DistributedSampler | Add sampler, set_epoch() each epoch |
| Slow training | NCCL over ethernet | Use NVLink/InfiniBand |
| OOM on some GPUs | Uneven batch sizes | Ensure divisible batch size |

---

## Advanced Level

### Q11: Design a distributed training pipeline for a financial LLM.
**Answer:**

```python
"""
Architecture: Fine-tune Llama-2-13B on 5 years of NSE regulatory filings
Hardware: 4× A100-80GB (single node)
Strategy: FSDP + BF16 + gradient checkpointing + gradient accumulation
"""
import torch
from accelerate import Accelerator, FullyShardedDataParallelPlugin
from torch.distributed.fsdp import ShardingStrategy, MixedPrecision

fsdp_plugin = FullyShardedDataParallelPlugin(
    sharding_strategy=ShardingStrategy.FULL_SHARD,
    mixed_precision_policy=MixedPrecision(
        param_dtype=torch.bfloat16,
        reduce_dtype=torch.bfloat16,
    ),
)

accelerator = Accelerator(
    fsdp_plugin=fsdp_plugin,
    gradient_accumulation_steps=8,
)

# Load model
model = load_llama_13b()
model.gradient_checkpointing_enable()

# Prepare with accelerate
model, optimizer, train_loader, scheduler = accelerator.prepare(
    model, optimizer, train_loader, scheduler
)

# Training loop with fault tolerance
for epoch in range(num_epochs):
    for step, batch in enumerate(train_loader):
        with accelerator.accumulate(model):
            outputs = model(**batch)
            loss = outputs.loss
            accelerator.backward(loss)
            accelerator.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

        # Checkpoint every 500 steps
        if step % 500 == 0:
            accelerator.save_state(f"checkpoint/step_{step}")

        # Log metrics
        if accelerator.is_main_process:
            wandb.log({"loss": loss.item(), "lr": scheduler.get_last_lr()[0]})
```

---

### Q12: Compare 3D parallelism strategies for training 70B+ models.
**Answer:**

3D parallelism combines Data + Pipeline + Tensor parallelism:

```
64 GPUs = 8 nodes × 8 GPUs

Tensor Parallel (TP=4): 4 GPUs split each layer's weights
Pipeline Parallel (PP=4): 4 groups, each handles 1/4 of layers
Data Parallel (DP=4): 4 replicas process different data

TP within NVLink-connected GPUs (fastest interconnect)
PP across groups (medium communication)
DP across nodes (gradient sync, least frequent)
```

| Config | TP | PP | DP | Best For |
|--------|----|----|-----|----------|
| Pure DDP | 1 | 1 | 64 | Models <10B |
| TP + DP | 4 | 1 | 16 | Models 10-30B |
| 3D | 4 | 4 | 4 | Models 70B+ |
| 3D + ZeRO | 4 | 4 | 4+ZeRO-1 | Maximum efficiency |

**Rule:** Put TP within a node (NVLink), PP across close nodes, DP across all nodes.

---

### Q13: How do you handle fault tolerance in multi-day distributed training runs?
**Answer:**

```python
import torch.distributed.elastic as elastic
from torch.distributed.elastic.multiprocessing.errors import record

@record  # Captures and reports errors from all ranks
def main():
    # Elastic training: auto-restarts on failure
    # torchrun handles process management
    
    # 1. Async checkpointing (don't block training)
    import threading
    def async_checkpoint(state_dict, path):
        thread = threading.Thread(target=torch.save, args=(state_dict, path))
        thread.start()
    
    # 2. Heartbeat monitoring
    last_step_time = time.time()
    TIMEOUT = 300  # 5 minutes
    
    for step, batch in enumerate(loader):
        loss = model(batch).loss
        loss.backward()
        optimizer.step()
        
        # Detect stuck workers
        if time.time() - last_step_time > TIMEOUT:
            raise RuntimeError(f"Rank {rank} stuck for {TIMEOUT}s")
        last_step_time = time.time()
        
        # Periodic checkpoint
        if step % 1000 == 0:
            state = {
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "step": step,
                "rng_states": torch.cuda.get_rng_state_all(),
            }
            async_checkpoint(state, f"ckpt/step_{step}.pt")
    
    # 3. Resume from latest checkpoint
    def find_latest_checkpoint(ckpt_dir):
        ckpts = sorted(Path(ckpt_dir).glob("step_*.pt"))
        return ckpts[-1] if ckpts else None

# Launch with elastic:
# torchrun --nproc_per_node=4 --rdzv_backend=c10d \
#   --rdzv_endpoint=host:29500 --max_restarts=3 train.py
```

Key fault tolerance patterns:
1. **Elastic training** — `torchrun` auto-restarts failed workers
2. **Frequent checkpoints** — every N steps, async to avoid blocking
3. **RNG state saving** — reproducible resume
4. **Spot instance support** — preemption-aware checkpointing on cloud
