"""
Gen-AI Tool: Inference Engines (vLLM)
=========================================
Demonstrates: vLLM async inference server, PagedAttention,
continuous batching, OpenAI-compatible API server, and
throughput optimization for high-concurrency LLM serving.

Role in GenAI Nexus: Serve the quantized startup advisor model with
high throughput for concurrent users — async, batched, fast.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator


@dataclass
class InferenceConfig:
    """vLLM server configuration."""

    model: str = "./data/quantized_model"
    host: str = "0.0.0.0"
    port: int = 8000
    tensor_parallel_size: int = 1   # GPUs for tensor parallelism
    max_model_len: int = 4096       # Max context length
    gpu_memory_utilization: float = 0.90  # Use 90% of GPU VRAM
    max_num_seqs: int = 32          # Max concurrent requests
    dtype: str = "float16"          # "float16" | "bfloat16" | "float32"
    quantization: str | None = "awq"  # "awq" | "gptq" | None


@dataclass
class InferenceRequest:
    """Single inference request."""

    prompt: str
    max_tokens: int = 512
    temperature: float = 0.3
    top_p: float = 0.95
    stream: bool = False
    request_id: str = ""

    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())[:8]


@dataclass
class InferenceResponse:
    """Inference result with metrics."""

    request_id: str
    generated_text: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    throughput_tokens_per_sec: float


@dataclass
class ServerMetrics:
    """Running server performance metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    avg_latency_ms: float = 0.0
    avg_throughput: float = 0.0
    queue_depth: int = 0
    gpu_utilization_pct: float = 0.0


class VLLMInferenceEngine:
    """
    vLLM-based high-performance LLM inference engine.

    Key vLLM innovations:
    - PagedAttention: Manages KV cache like OS virtual memory → 24x more throughput
    - Continuous Batching: New requests join the batch mid-computation
    - Tensor Parallelism: Splits model across multiple GPUs
    - OpenAI-compatible API: Drop-in replacement for OpenAI client

    Demonstrates:
    - vLLM engine setup
    - Sync and async inference
    - Streaming generation
    - Batch inference
    - Performance metrics
    """

    def __init__(self, config: InferenceConfig | None = None):
        self.config = config or InferenceConfig()
        self._vllm_available = False
        self._engine = None
        self._metrics = ServerMetrics()
        self._request_latencies: list[float] = []

        try:
            from vllm import AsyncLLMEngine
            self._vllm_available = True
        except ImportError:
            pass

    async def initialize(self) -> bool:
        """Initialize the vLLM engine (async)."""
        if not self._vllm_available:
            print(f"[Demo] vLLM not available — using mock inference")
            print(f"  Would load: {self.config.model}")
            print(f"  Config: tensor_parallel={self.config.tensor_parallel_size}, "
                  f"max_seqs={self.config.max_num_seqs}, quant={self.config.quantization}")
            return False

        from vllm import AsyncEngineArgs, AsyncLLMEngine

        engine_args = AsyncEngineArgs(
            model=self.config.model,
            tensor_parallel_size=self.config.tensor_parallel_size,
            max_model_len=self.config.max_model_len,
            gpu_memory_utilization=self.config.gpu_memory_utilization,
            max_num_seqs=self.config.max_num_seqs,
            dtype=self.config.dtype,
            quantization=self.config.quantization,
        )

        self._engine = AsyncLLMEngine.from_engine_args(engine_args)
        print(f"vLLM engine initialized: {self.config.model}")
        return True

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """
        Single request async inference.
        Uses PagedAttention for efficient KV cache management.
        """
        start = time.time()

        if not self._vllm_available or self._engine is None:
            # Demo: simulate inference
            await asyncio.sleep(0.05)  # Simulate 50ms latency
            demo_response = self._generate_demo_response(request.prompt)
            latency = (time.time() - start) * 1000
            tokens = len(demo_response.split())

            self._update_metrics(latency, tokens)
            return InferenceResponse(
                request_id=request.request_id,
                generated_text=demo_response,
                prompt_tokens=len(request.prompt.split()),
                completion_tokens=tokens,
                latency_ms=round(latency, 2),
                throughput_tokens_per_sec=round(tokens / (latency / 1000), 1),
            )

        from vllm import SamplingParams

        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
        )

        output = None
        async for out in self._engine.generate(
            request.prompt, sampling_params, request.request_id
        ):
            output = out

        latency = (time.time() - start) * 1000
        if output and output.outputs:
            text = output.outputs[0].text
            completion_tokens = len(output.outputs[0].token_ids)
        else:
            text, completion_tokens = "", 0

        self._update_metrics(latency, completion_tokens)
        return InferenceResponse(
            request_id=request.request_id,
            generated_text=text,
            prompt_tokens=len(request.prompt.split()),
            completion_tokens=completion_tokens,
            latency_ms=round(latency, 2),
            throughput_tokens_per_sec=round(completion_tokens / max(latency / 1000, 0.001), 1),
        )

    async def generate_stream(
        self, request: InferenceRequest
    ) -> AsyncGenerator[str, None]:
        """
        Streaming inference — yield tokens as they're generated.
        Enables real-time display without waiting for full completion.
        """
        if not self._vllm_available or self._engine is None:
            # Demo streaming
            words = self._generate_demo_response(request.prompt).split()
            for word in words:
                await asyncio.sleep(0.02)  # Simulate token generation speed
                yield word + " "
            return

        from vllm import SamplingParams

        sampling_params = SamplingParams(
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        prev_text = ""
        async for output in self._engine.generate(
            request.prompt, sampling_params, request.request_id
        ):
            if output.outputs:
                new_text = output.outputs[0].text
                delta = new_text[len(prev_text):]
                if delta:
                    yield delta
                prev_text = new_text

    async def batch_generate(
        self, requests: list[InferenceRequest]
    ) -> list[InferenceResponse]:
        """
        Batch inference — vLLM's continuous batching processes these together.
        Higher throughput than sequential single requests.
        """
        tasks = [self.generate(req) for req in requests]
        return await asyncio.gather(*tasks)

    def get_server_command(self) -> str:
        """Return the command to start vLLM as OpenAI-compatible server."""
        return (
            f"python -m vllm.entrypoints.openai.api_server \\\n"
            f"  --model {self.config.model} \\\n"
            f"  --host {self.config.host} \\\n"
            f"  --port {self.config.port} \\\n"
            f"  --tensor-parallel-size {self.config.tensor_parallel_size} \\\n"
            f"  --max-model-len {self.config.max_model_len} \\\n"
            f"  --gpu-memory-utilization {self.config.gpu_memory_utilization} \\\n"
            f"  --quantization {self.config.quantization or 'none'}"
        )

    def get_client_code(self) -> str:
        """Return OpenAI-compatible client code for vLLM server."""
        return f'''
# vLLM serves an OpenAI-compatible API
from openai import OpenAI

client = OpenAI(
    api_key="EMPTY",  # vLLM doesn't require auth by default
    base_url="http://{self.config.host}:{self.config.port}/v1",
)

response = client.chat.completions.create(
    model="{self.config.model}",
    messages=[{{"role": "user", "content": "What is the TAM for legal tech?"}}],
    temperature=0.3,
    max_tokens=512,
)
print(response.choices[0].message.content)
'''

    def get_metrics(self) -> ServerMetrics:
        return self._metrics

    def _update_metrics(self, latency: float, tokens: int):
        self._metrics.total_requests += 1
        self._metrics.successful_requests += 1
        self._request_latencies.append(latency)
        self._metrics.avg_latency_ms = round(
            sum(self._request_latencies) / len(self._request_latencies), 2
        )

    def _generate_demo_response(self, prompt: str) -> str:
        """Demo response based on prompt content."""
        prompt_lower = prompt.lower()
        if "legal" in prompt_lower or "law" in prompt_lower:
            return (
                "For a legal tech startup, focus on the $45.2B TAM growing at 18.9% CAGR. "
                "Target mid-market firms (1-50 attorneys) underserved by Harvey AI and Ironclad. "
                "Price at $299-999/month flat-rate. Get SOC2 Type I before enterprise sales. "
                "First 10 customers: offer 6 months free in exchange for case studies."
            )
        elif "market" in prompt_lower or "tam" in prompt_lower:
            return "The legal tech market is $45.2B TAM (2024) with 18.9% CAGR through 2030."
        else:
            return f"[Demo vLLM] Generated response for: {prompt[:80]}..."


async def demo_async():
    print("=" * 60)
    print("DEMO: vLLM Inference Engine")
    print("=" * 60)
    engine = VLLMInferenceEngine()

    print("\n[1] Initialize Engine")
    await engine.initialize()

    print("\n[2] Single Inference Request")
    request = InferenceRequest(
        prompt="What is the go-to-market strategy for a legal tech startup?",
        max_tokens=200,
        temperature=0.3,
    )
    response = await engine.generate(request)
    print(f"Request ID: {response.request_id}")
    print(f"Generated: {response.generated_text[:200]}...")
    print(f"Latency: {response.latency_ms:.1f}ms | Throughput: {response.throughput_tokens_per_sec:.1f} tok/s")

    print("\n[3] Streaming Generation")
    stream_req = InferenceRequest(prompt="Explain the legal tech competitive landscape", stream=True)
    print("Streaming: ", end="", flush=True)
    async for token in engine.generate_stream(stream_req):
        print(token, end="", flush=True)
    print()

    print("\n[4] Batch Inference (3 concurrent requests)")
    batch_requests = [
        InferenceRequest(prompt=f"Question {i}: What is the best pricing for legal SaaS?")
        for i in range(3)
    ]
    batch_results = await engine.batch_generate(batch_requests)
    for i, r in enumerate(batch_results):
        print(f"  Request {i+1}: {r.latency_ms:.1f}ms, {r.throughput_tokens_per_sec:.1f} tok/s")

    print("\n[5] Server Launch Command")
    print(engine.get_server_command())

    print("\n[6] OpenAI-Compatible Client Code")
    print(engine.get_client_code())

    print("\n[7] Server Metrics")
    metrics = engine.get_metrics()
    print(f"  Total requests: {metrics.total_requests}")
    print(f"  Avg latency: {metrics.avg_latency_ms:.1f}ms")


def demo():
    asyncio.run(demo_async())


if __name__ == "__main__":
    demo()
