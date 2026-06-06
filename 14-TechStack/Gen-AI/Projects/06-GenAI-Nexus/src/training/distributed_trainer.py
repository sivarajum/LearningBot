"""
Gen-AI Tool: Distributed Training
====================================
Demonstrates: PyTorch DDP (DistributedDataParallel), multi-GPU setup,
gradient synchronization, ZeRO optimization (DeepSpeed), and
distributed training launcher configuration.

Role in GenAI Nexus: Large-scale training setup for when the startup
advisor model needs to train on the full startup knowledge corpus at scale.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class DistributedConfig:
    """Configuration for distributed training."""

    # Cluster setup
    num_nodes: int = 1          # Number of machines
    num_gpus_per_node: int = 4  # GPUs per machine
    backend: str = "nccl"       # "nccl" (NVIDIA) | "gloo" (CPU)

    # Training
    model_name: str = "meta-llama/Llama-3.2-1B"
    batch_size_per_gpu: int = 4
    gradient_accumulation_steps: int = 8  # Effective batch = 4×4×8=128
    max_steps: int = 1000
    learning_rate: float = 1e-4
    warmup_steps: int = 100

    # ZeRO (DeepSpeed memory optimization)
    zero_stage: int = 3          # 0=disabled, 1=optimizer, 2=+gradients, 3=+parameters

    # Checkpointing
    save_steps: int = 100
    output_dir: str = "./data/distributed_checkpoints"

    @property
    def world_size(self) -> int:
        return self.num_nodes * self.num_gpus_per_node

    @property
    def effective_batch_size(self) -> int:
        return self.batch_size_per_gpu * self.world_size * self.gradient_accumulation_steps


@dataclass
class TrainingNode:
    """Represents one node (machine) in the training cluster."""

    rank: int           # Global rank (0 = master)
    local_rank: int     # Rank within this node
    world_size: int     # Total processes
    node_rank: int      # Which machine this is


def get_deepspeed_config(zero_stage: int, batch_size: int) -> dict:
    """
    Generate DeepSpeed ZeRO config dictionary.

    ZeRO stages:
    - Stage 1: Optimizer states partitioned across GPUs (~4x memory reduction)
    - Stage 2: + Gradient partitioning (~8x memory reduction)
    - Stage 3: + Model parameter partitioning (train 175B on 8xA100!)
    """
    base_config = {
        "train_batch_size": batch_size,
        "gradient_accumulation_steps": 8,
        "optimizer": {
            "type": "AdamW",
            "params": {"lr": 1e-4, "betas": [0.9, 0.999], "eps": 1e-8, "weight_decay": 0.01},
        },
        "scheduler": {
            "type": "WarmupDecayLR",
            "params": {"warmup_min_lr": 0, "warmup_max_lr": 1e-4, "warmup_num_steps": 100},
        },
        "fp16": {"enabled": True, "loss_scale": 0, "initial_scale_power": 16},
        "gradient_clipping": 1.0,
        "wall_clock_breakdown": False,
    }

    if zero_stage == 1:
        base_config["zero_optimization"] = {
            "stage": 1,
            "allgather_partitions": True,
            "reduce_scatter": True,
        }
    elif zero_stage == 2:
        base_config["zero_optimization"] = {
            "stage": 2,
            "allgather_partitions": True,
            "reduce_scatter": True,
            "overlap_comm": True,
        }
    elif zero_stage == 3:
        base_config["zero_optimization"] = {
            "stage": 3,
            "offload_optimizer": {"device": "cpu", "pin_memory": True},
            "offload_param": {"device": "cpu", "pin_memory": True},
            "overlap_comm": True,
            "contiguous_gradients": True,
            "reduce_bucket_size": 5e8,
            "stage3_prefetch_bucket_size": 5e8,
        }

    return base_config


class DistributedTrainer:
    """
    Distributed training orchestrator.

    Demonstrates:
    - DDP setup (torch.distributed)
    - DeepSpeed ZeRO optimization
    - Gradient accumulation for large effective batches
    - Checkpoint saving and resumption
    - Training loop with distributed data sampling
    - FSDP (Fully Sharded Data Parallel) as alternative
    """

    def __init__(self, config: DistributedConfig | None = None):
        self.config = config or DistributedConfig()
        self._torch_available = False

        try:
            import torch
            self._torch_available = True
        except ImportError:
            pass

    def describe_setup(self) -> str:
        """Print the distributed training setup."""
        return f"""
DISTRIBUTED TRAINING SETUP
============================
Model: {self.config.model_name}
Cluster: {self.config.num_nodes} node(s) × {self.config.num_gpus_per_node} GPUs = {self.config.world_size} total
Backend: {self.config.backend}
ZeRO Stage: {self.config.zero_stage}

Batching:
  Per-GPU batch size: {self.config.batch_size_per_gpu}
  Gradient accumulation steps: {self.config.gradient_accumulation_steps}
  Effective batch size: {self.config.effective_batch_size} samples

Memory Estimates (ZeRO Stage {self.config.zero_stage}):
  Stage 0 (no ZeRO): ~24GB/GPU for 7B model
  Stage 1: ~12GB/GPU (optimizer states sharded)
  Stage 2: ~6GB/GPU (+ gradients sharded)
  Stage 3: ~3GB/GPU (+ parameters sharded, enables larger models)

Launch Command:
  # Single node
  torchrun --nproc_per_node={self.config.num_gpus_per_node} train.py

  # Multi-node
  torchrun --nnodes={self.config.num_nodes} \\
    --nproc_per_node={self.config.num_gpus_per_node} \\
    --node_rank=NODE_RANK \\
    --master_addr=MASTER_IP \\
    --master_port=29500 \\
    train.py
"""

    def setup_process_group(self, rank: int, world_size: int):
        """Initialize distributed process group (DDP)."""
        if not self._torch_available:
            print(f"[Demo] Would init process group: rank={rank}, world_size={world_size}")
            return

        import torch.distributed as dist

        os.environ.setdefault("MASTER_ADDR", "localhost")
        os.environ.setdefault("MASTER_PORT", "29500")

        dist.init_process_group(
            backend=self.config.backend,
            rank=rank,
            world_size=world_size,
        )
        print(f"Process group initialized: rank {rank}/{world_size}")

    def wrap_model_ddp(self, model):
        """Wrap model with DistributedDataParallel."""
        if not self._torch_available:
            print("[Demo] Would wrap model with DDP")
            return model

        import torch
        import torch.distributed as dist
        from torch.nn.parallel import DistributedDataParallel as DDP

        local_rank = int(os.environ.get("LOCAL_RANK", 0))
        device = torch.device(f"cuda:{local_rank}" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        model = DDP(model, device_ids=[local_rank] if torch.cuda.is_available() else None)
        return model

    def training_loop_demo(self) -> dict:
        """
        Demonstrate the distributed training loop pattern.
        Shows the structure without requiring actual GPUs.
        """
        print(f"\nDistributed Training Loop (Demo)")
        print(f"World size: {self.config.world_size}")
        print(f"Effective batch: {self.config.effective_batch_size}")

        # Simulate training steps
        results = {"steps": [], "final_loss": 0.0}

        for step in range(min(5, self.config.max_steps)):
            # In real DDP:
            # 1. Each GPU gets different data shard (DistributedSampler)
            # 2. Forward pass on each GPU independently
            # 3. Loss backward → gradients accumulated
            # 4. At sync point: all_reduce averages gradients across GPUs
            # 5. Optimizer step updates model (identical state on all GPUs)

            simulated_loss = 2.5 - step * 0.2
            results["steps"].append({"step": step, "loss": round(simulated_loss, 3)})
            print(f"  Step {step+1}: loss={simulated_loss:.3f} [all GPUs synchronized]")

        results["final_loss"] = results["steps"][-1]["loss"]
        return results

    def get_fsdp_config(self) -> dict:
        """
        FSDP (Fully Sharded Data Parallel) configuration.
        PyTorch native alternative to DeepSpeed ZeRO.
        """
        return {
            "sharding_strategy": "FULL_SHARD",    # ZeRO-3 equivalent
            "cpu_offload": True,                  # Offload to CPU when not in use
            "auto_wrap_policy": "transformer_auto_wrap",
            "backward_prefetch": "BACKWARD_PRE",  # Prefetch params during backward
            "forward_prefetch": True,
            "mixed_precision": "fp16",
            "activation_checkpointing": True,     # Trade compute for memory
        }

    def estimate_training_cost(self) -> dict:
        """Estimate cloud training cost."""
        # AWS p4d.24xlarge = 8×A100 80GB, $32.77/hour
        hours_per_1000_steps = 0.5  # rough estimate for 1B model
        total_hours = (self.config.max_steps / 1000) * hours_per_1000_steps
        instances = max(1, self.config.num_nodes)
        cost_per_hour = 32.77 * instances  # p4d.24xlarge

        return {
            "estimated_hours": round(total_hours, 1),
            "instances": instances,
            "cost_per_hour_usd": cost_per_hour,
            "total_cost_usd": round(total_hours * cost_per_hour, 2),
            "note": "Estimate for AWS p4d.24xlarge (8xA100 80GB) instances",
        }


def demo():
    print("=" * 60)
    print("DEMO: Distributed Training Setup")
    print("=" * 60)

    config = DistributedConfig(
        num_nodes=2,
        num_gpus_per_node=4,
        zero_stage=3,
        max_steps=500,
    )
    trainer = DistributedTrainer(config)

    print("\n[1] Distributed Setup Description")
    print(trainer.describe_setup())

    print("\n[2] DeepSpeed ZeRO Stage 3 Config")
    import json
    ds_config = get_deepspeed_config(zero_stage=3, batch_size=128)
    print(json.dumps(ds_config, indent=2)[:500] + "...")

    print("\n[3] FSDP Configuration")
    fsdp_config = trainer.get_fsdp_config()
    for k, v in fsdp_config.items():
        print(f"  {k}: {v}")

    print("\n[4] Training Loop Demo")
    results = trainer.training_loop_demo()
    print(f"Final loss: {results['final_loss']:.3f}")

    print("\n[5] Cost Estimation")
    cost = trainer.estimate_training_cost()
    print(f"Estimated training time: {cost['estimated_hours']} hours")
    print(f"Instances: {cost['instances']} × p4d.24xlarge")
    print(f"Total cost: ${cost['total_cost_usd']:,.2f}")
    print(f"Note: {cost['note']}")


if __name__ == "__main__":
    demo()
