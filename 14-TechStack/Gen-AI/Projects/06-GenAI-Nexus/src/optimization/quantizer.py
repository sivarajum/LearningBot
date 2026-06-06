"""
Gen-AI Tool: Model Quantization
==================================
Demonstrates: INT8 quantization with bitsandbytes, GGUF format,
quantization impact analysis, accuracy vs size tradeoffs, and
serving quantized models.

Role in GenAI Nexus: Compress the fine-tuned startup advisor model
for fast inference — reduce size 4x, speed up 2-3x, minimal accuracy loss.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuantizationConfig:
    """Quantization settings."""

    method: str = "int8"          # "int8" | "int4" | "gguf" | "awq"
    model_name: str = "meta-llama/Llama-3.2-1B"
    output_path: str = "./data/quantized_model"
    calibration_samples: int = 128  # Samples for INT8 calibration


@dataclass
class ModelProfile:
    """Before/after quantization profile."""

    name: str
    size_gb: float
    dtype: str
    latency_ms: float           # Per-token latency
    throughput_tokens_per_sec: float
    accuracy_pct: float          # Relative to float32 baseline


@dataclass
class QuantizationResult:
    original: ModelProfile
    quantized: ModelProfile
    size_reduction: float       # e.g., 4.0 = 4x smaller
    speed_improvement: float    # e.g., 2.5 = 2.5x faster
    accuracy_drop: float        # e.g., 0.02 = 2% accuracy drop


# Benchmark data for popular models (demonstrative)
QUANTIZATION_BENCHMARKS = {
    "llama-3.2-1b": {
        "float32": ModelProfile("LLaMA-3.2-1B (fp32)", 4.0, "float32", 45.0, 22.2, 100.0),
        "float16": ModelProfile("LLaMA-3.2-1B (fp16)", 2.0, "float16", 28.0, 35.7, 99.5),
        "int8": ModelProfile("LLaMA-3.2-1B (int8)", 1.0, "int8", 18.0, 55.6, 98.8),
        "int4": ModelProfile("LLaMA-3.2-1B (int4)", 0.5, "int4", 12.0, 83.3, 97.1),
        "gguf_q4_k_m": ModelProfile("LLaMA-3.2-1B (GGUF Q4_K_M)", 0.6, "gguf", 10.0, 100.0, 97.4),
    },
    "gpt2": {
        "float32": ModelProfile("GPT-2 (fp32)", 0.6, "float32", 12.0, 83.3, 100.0),
        "int8": ModelProfile("GPT-2 (int8)", 0.15, "int8", 7.0, 142.9, 99.2),
    },
}


class ModelQuantizer:
    """
    Quantize LLMs for production deployment.

    Demonstrates:
    - bitsandbytes INT8 quantization (LLM.int8())
    - bitsandbytes INT4 (QLoRA-style, nf4)
    - GGUF format (llama.cpp compatible, CPU inference)
    - AWQ (Activation-aware Weight Quantization)
    - Quantization accuracy benchmarking
    - Memory estimation
    """

    def __init__(self, config: QuantizationConfig | None = None):
        self.config = config or QuantizationConfig()
        self._bitsandbytes_available = False
        self._model = None
        self._tokenizer = None

        try:
            import bitsandbytes  # noqa: F401
            self._bitsandbytes_available = True
        except ImportError:
            pass

    def quantize_int8(self, model_name: str | None = None) -> QuantizationResult:
        """
        Apply LLM.int8() quantization using bitsandbytes.
        Mixed-precision: only linear layers are quantized to INT8.
        Activations remain in fp16 for accuracy.
        """
        name = model_name or self.config.model_name

        if not self._bitsandbytes_available:
            print(f"[Demo] Would quantize {name} to INT8")
            return self._get_demo_result("int8")

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

            bnb_config = BitsAndBytesConfig(load_in_8bit=True)
            self._model = AutoModelForCausalLM.from_pretrained(
                name, quantization_config=bnb_config, device_map="auto"
            )
            self._tokenizer = AutoTokenizer.from_pretrained(name)
            print(f"INT8 quantization applied to {name}")
            return self._get_demo_result("int8")
        except Exception as e:
            print(f"[Warning] INT8 quantization failed: {e}")
            return self._get_demo_result("int8")

    def quantize_int4(self, model_name: str | None = None) -> QuantizationResult:
        """
        Apply QLoRA-style 4-bit quantization (NF4 data type).
        4x smaller than fp32, ~2% accuracy drop on most benchmarks.
        """
        name = model_name or self.config.model_name

        if not self._bitsandbytes_available:
            print(f"[Demo] Would quantize {name} to INT4 (NF4)")
            return self._get_demo_result("int4")

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",          # NormalFloat4 — best for LLMs
                bnb_4bit_compute_dtype=torch.float16, # Compute in fp16
                bnb_4bit_use_double_quant=True,       # Nested quantization (saves 0.4 bits/param)
            )
            self._model = AutoModelForCausalLM.from_pretrained(
                name, quantization_config=bnb_config, device_map="auto"
            )
            return self._get_demo_result("int4")
        except Exception as e:
            print(f"[Warning] INT4 quantization failed: {e}")
            return self._get_demo_result("int4")

    def export_gguf(self, model_path: str, output_path: str | None = None) -> str:
        """
        Export model to GGUF format for llama.cpp inference.
        GGUF runs efficiently on CPU — no GPU required.
        """
        out = output_path or f"{self.config.output_path}/model.Q4_K_M.gguf"
        print(f"[Demo] GGUF export steps:")
        print(f"  1. Convert {model_path} → GGUF format")
        print(f"  2. Apply Q4_K_M quantization (4-bit mixed precision)")
        print(f"  3. Save to {out}")
        print(f"  4. Test with: llama-cli -m {out} -p 'What is your advice?'")
        print()
        print("  Real command:")
        print(f"  python llama.cpp/convert_hf_to_gguf.py {model_path} --outfile model.gguf")
        print(f"  llama.cpp/quantize model.gguf {out} Q4_K_M")
        return out

    def benchmark(self, model_key: str = "llama-3.2-1b") -> list[ModelProfile]:
        """Compare quantization levels for a given model."""
        profiles = QUANTIZATION_BENCHMARKS.get(model_key, {})
        return list(profiles.values())

    def recommend_quantization(
        self, constraints: dict[str, Any]
    ) -> dict[str, str]:
        """
        Recommend best quantization based on deployment constraints.

        constraints: {
            "max_gpu_gb": 4,       # GPU memory budget
            "latency_target_ms": 20,
            "min_accuracy_pct": 97,
            "deployment": "gpu" | "cpu"
        }
        """
        max_gpu = constraints.get("max_gpu_gb", 8)
        deployment = constraints.get("deployment", "gpu")
        min_acc = constraints.get("min_accuracy_pct", 97)

        recommendations = []

        if deployment == "cpu":
            recommendations.append(("GGUF Q4_K_M", "Best CPU inference, llama.cpp compatible"))
        elif max_gpu <= 1:
            recommendations.append(("INT4 (NF4)", "4x size reduction, fits in 1GB VRAM"))
        elif max_gpu <= 2:
            recommendations.append(("INT8", "2x size reduction, ~1.2% accuracy drop"))
        else:
            recommendations.append(("FP16", "2x size reduction, <0.5% accuracy drop"))

        return {
            "recommended": recommendations[0][0],
            "reason": recommendations[0][1],
            "alternatives": [r[0] for r in recommendations[1:]],
            "constraints": constraints,
        }

    def estimate_memory(self, model_params_billions: float, dtype: str = "int8") -> dict:
        """Estimate GPU memory needed for a quantized model."""
        bits_per_param = {
            "float32": 32, "float16": 16, "bfloat16": 16,
            "int8": 8, "int4": 4, "int3": 3,
        }
        bits = bits_per_param.get(dtype, 16)
        model_gb = model_params_billions * 1e9 * bits / 8 / 1e9
        overhead_gb = model_gb * 0.2  # KV cache + activations

        return {
            "model_gb": round(model_gb, 2),
            "overhead_gb": round(overhead_gb, 2),
            "total_gb": round(model_gb + overhead_gb, 2),
            "dtype": dtype,
            "params_B": model_params_billions,
        }

    def _get_demo_result(self, method: str) -> QuantizationResult:
        """Return demo quantization result."""
        benchmarks = QUANTIZATION_BENCHMARKS.get("llama-3.2-1b", {})
        original = benchmarks.get("float32", ModelProfile("Original", 4.0, "fp32", 45, 22, 100))
        quantized = benchmarks.get(method, ModelProfile("Quantized", 1.0, method, 18, 55, 98))

        return QuantizationResult(
            original=original,
            quantized=quantized,
            size_reduction=round(original.size_gb / max(quantized.size_gb, 0.001), 1),
            speed_improvement=round(
                quantized.throughput_tokens_per_sec / max(original.throughput_tokens_per_sec, 0.001), 1
            ),
            accuracy_drop=round(original.accuracy_pct - quantized.accuracy_pct, 2),
        )


def demo():
    print("=" * 60)
    print("DEMO: Model Quantization")
    print("=" * 60)
    quantizer = ModelQuantizer()

    print("\n[1] INT8 Quantization")
    result = quantizer.quantize_int8()
    print(f"  {result.original.name} → {result.quantized.name}")
    print(f"  Size: {result.original.size_gb}GB → {result.quantized.size_gb}GB ({result.size_reduction}x smaller)")
    print(f"  Speed: {result.original.throughput_tokens_per_sec} → {result.quantized.throughput_tokens_per_sec} tok/s")
    print(f"  Accuracy drop: {result.accuracy_drop}%")

    print("\n[2] INT4 (QLoRA-style)")
    result4 = quantizer.quantize_int4()
    print(f"  Size reduction: {result4.size_reduction}x | Speed improvement: {result4.speed_improvement}x")
    print(f"  Accuracy drop: {result4.accuracy_drop}%")

    print("\n[3] GGUF Export (CPU Inference)")
    path = quantizer.export_gguf("./data/peft_model")
    print(f"  Output: {path}")

    print("\n[4] Benchmark All Quantization Levels")
    profiles = quantizer.benchmark("llama-3.2-1b")
    print(f"  {'Model':<35} {'Size':>6} {'Latency':>10} {'Tok/s':>8} {'Acc%':>6}")
    print("  " + "-" * 70)
    for p in profiles:
        print(f"  {p.name:<35} {p.size_gb:>5.1f}G {p.latency_ms:>8.0f}ms {p.throughput_tokens_per_sec:>7.1f} {p.accuracy_pct:>5.1f}%")

    print("\n[5] Memory Estimation")
    for dtype in ["float32", "float16", "int8", "int4"]:
        mem = quantizer.estimate_memory(1.0, dtype)  # 1B param model
        print(f"  {dtype:10} → {mem['total_gb']:.2f}GB total (model={mem['model_gb']:.2f}GB)")

    print("\n[6] Quantization Recommendation")
    rec = quantizer.recommend_quantization({
        "max_gpu_gb": 2,
        "deployment": "gpu",
        "min_accuracy_pct": 97,
    })
    print(f"  Recommended: {rec['recommended']}")
    print(f"  Reason: {rec['reason']}")


if __name__ == "__main__":
    demo()
