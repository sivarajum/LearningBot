# LLMOps: Comprehensive Guide

## Core Concepts

### LLMOps Fundamentals

LLMOps (Large Language Model Operations) is the practice of operationalizing large language models in production environments. It encompasses the entire lifecycle of LLM development, deployment, and maintenance, ensuring reliable, scalable, and cost-effective AI applications.

**Key Principles:**
- **Reproducibility**: Consistent model training and deployment
- **Scalability**: Handle varying loads and model sizes
- **Reliability**: Robust error handling and fallback mechanisms
- **Monitoring**: Comprehensive observability and performance tracking
- **Cost Efficiency**: Optimize resource usage and inference costs
- **Security**: Protect models and data throughout the lifecycle

### LLM Lifecycle Management

The LLM lifecycle includes several interconnected stages that require careful orchestration and monitoring.

**Lifecycle Stages:**
1. **Data Preparation**: Curate and preprocess training data
2. **Model Training**: Train or fine-tune models on infrastructure
3. **Model Evaluation**: Assess model performance and quality
4. **Model Deployment**: Serve models for inference
5. **Model Monitoring**: Track performance in production
6. **Model Updates**: Retrain and redeploy improved versions

## Model Training Infrastructure

### Distributed Training Setup

```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling
)
import os
from datasets import load_dataset

class DistributedLLMTrainer:
    def __init__(self, model_name="gpt2", dataset_name="wikitext"):
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.world_size = torch.cuda.device_count()

    def setup_distributed(self, rank, world_size):
        """Initialize distributed training"""
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'

        # Initialize the process group
        dist.init_process_group("nccl", rank=rank, world_size=world_size)
        torch.cuda.set_device(rank)

    def cleanup_distributed(self):
        """Clean up distributed training"""
        dist.destroy_process_group()

    def prepare_dataset(self):
        """Load and preprocess dataset"""
        # Load dataset
        dataset = load_dataset(self.dataset_name, "wikitext-2-raw-v1")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Tokenization function
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=512
            )

        # Tokenize dataset
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False  # Causal language modeling
        )

        return tokenized_dataset, data_collator, tokenizer

    def train_model(self, rank, world_size):
        """Train model in distributed fashion"""
        self.setup_distributed(rank, world_size)

        try:
            # Load model
            model = AutoModelForCausalLM.from_pretrained(self.model_name)
            model = model.to(rank)
            model = DDP(model, device_ids=[rank])

            # Prepare dataset
            dataset, data_collator, tokenizer = self.prepare_dataset()

            # Training arguments
            training_args = TrainingArguments(
                output_dir=f"./results_{rank}",
                overwrite_output_dir=True,
                num_train_epochs=3,
                per_device_train_batch_size=4,
                per_device_eval_batch_size=4,
                gradient_accumulation_steps=2,
                learning_rate=5e-5,
                weight_decay=0.01,
                logging_dir=f"./logs_{rank}",
                logging_steps=100,
                save_steps=500,
                evaluation_strategy="steps",
                eval_steps=500,
                save_total_limit=2,
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                dataloader_num_workers=4,
                ddp_find_unused_parameters=False,
            )

            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=dataset["train"],
                eval_dataset=dataset["validation"],
                data_collator=data_collator,
                tokenizer=tokenizer,
            )

            # Train the model
            trainer.train()

            # Save the model (only on rank 0)
            if rank == 0:
                trainer.save_model("./final_model")
                tokenizer.save_pretrained("./final_model")

        finally:
            self.cleanup_distributed()

    def start_training(self):
        """Start distributed training"""
        mp.spawn(
            self.train_model,
            args=(self.world_size,),
            nprocs=self.world_size,
            join=True
        )

# Usage
if __name__ == "__main__":
    trainer = DistributedLLMTrainer()
    trainer.start_training()
```

### Fine-tuning Pipeline

```python
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch
from datasets import Dataset
import json
import wandb
from datetime import datetime

class LLMFineTuner:
    def __init__(self, base_model_name="microsoft/DialoGPT-medium",
                 output_dir="./fine_tuned_model"):
        self.base_model_name = base_model_name
        self.output_dir = output_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model_and_tokenizer(self):
        """Load base model and tokenizer"""
        print(f"Loading model: {self.base_model_name}")

        tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            load_in_8bit=True if self.device == "cuda" else False,
        )

        return model, tokenizer

    def prepare_lora_config(self):
        """Configure LoRA for efficient fine-tuning"""
        lora_config = LoraConfig(
            r=16,  # Rank
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],  # Attention layers
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        return lora_config

    def prepare_dataset(self, data_path, tokenizer):
        """Prepare dataset for fine-tuning"""
        # Load custom dataset
        with open(data_path, 'r') as f:
            data = json.load(f)

        # Convert to HuggingFace dataset
        dataset = Dataset.from_list(data)

        def tokenize_function(examples):
            # Format conversation
            conversations = []
            for conv in examples["conversations"]:
                formatted = ""
                for turn in conv:
                    if turn["role"] == "user":
                        formatted += f"User: {turn['content']}\n"
                    elif turn["role"] == "assistant":
                        formatted += f"Assistant: {turn['content']}\n"
                conversations.append(formatted)

            return tokenizer(
                conversations,
                truncation=True,
                padding="max_length",
                max_length=512,
                return_tensors="pt"
            )

        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )

        return tokenized_dataset

    def setup_training_arguments(self, run_name):
        """Configure training arguments"""
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            gradient_accumulation_steps=2,
            learning_rate=2e-4,
            weight_decay=0.01,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=True if self.device == "cuda" else False,
            report_to="wandb",
            run_name=run_name,
            push_to_hub=False,
        )

        return training_args

    def fine_tune(self, data_path, run_name=None):
        """Execute fine-tuning pipeline"""

        if run_name is None:
            run_name = f"llm_finetune_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize wandb
        wandb.init(project="llm-finetuning", name=run_name)

        try:
            # Load model and tokenizer
            model, tokenizer = self.load_model_and_tokenizer()

            # Prepare LoRA
            lora_config = self.prepare_lora_config()
            model = prepare_model_for_kbit_training(model)
            model = get_peft_model(model, lora_config)

            # Prepare dataset
            dataset = self.prepare_dataset(data_path, tokenizer)
            train_test_split = dataset.train_test_split(test_size=0.1)
            train_dataset = train_test_split["train"]
            eval_dataset = train_test_split["test"]

            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )

            # Training arguments
            training_args = self.setup_training_arguments(run_name)

            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                data_collator=data_collator,
                tokenizer=tokenizer,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
            )

            # Train the model
            print("Starting fine-tuning...")
            trainer.train()

            # Save the model
            trainer.save_model(self.output_dir)
            tokenizer.save_pretrained(self.output_dir)

            # Log final metrics
            final_metrics = trainer.evaluate()
            wandb.log({"final_eval_loss": final_metrics["eval_loss"]})

            print(f"Fine-tuning completed. Model saved to {self.output_dir}")
            return self.output_dir

        finally:
            wandb.finish()

# Usage example
if __name__ == "__main__":
    fine_tuner = LLMFineTuner(
        base_model_name="microsoft/DialoGPT-medium",
        output_dir="./fine_tuned_chatbot"
    )

    # Fine-tune on custom dataset
    model_path = fine_tuner.fine_tune("conversation_data.json")
```

## Model Deployment and Serving

### FastAPI Model Server

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uvicorn
import psutil
import GPUtil
from datetime import datetime
import json
from cachetools import TTLCache
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    max_length: int = Field(100, ge=10, le=500)
    temperature: float = Field(0.7, ge=0.1, le=2.0)
    top_p: float = Field(0.9, ge=0.1, le=1.0)
    do_sample: bool = True
    num_return_sequences: int = Field(1, ge=1, le=5)
    user_id: Optional[str] = None

class GenerationResponse(BaseModel):
    generated_texts: List[str]
    generation_time: float
    model_name: str
    request_id: str

class ModelServer:
    def __init__(self, model_name: str, device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Response cache
        self.cache = TTLCache(maxsize=1000, ttl=300)  # 5-minute cache

        # Metrics
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "avg_generation_time": 0.0,
            "total_generation_time": 0.0
        }

        # Load model
        self.load_model()

    def load_model(self):
        """Load the model and tokenizer"""
        logger.info(f"Loading model: {self.model_name}")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=self.device,
                load_in_8bit=True if torch.cuda.is_available() else False,
            )

            # Create generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
            )

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def generate_cache_key(self, request: GenerationRequest) -> str:
        """Generate cache key for request"""
        request_dict = request.dict()
        request_dict.pop('user_id', None)  # Don't cache user-specific requests
        key_string = json.dumps(request_dict, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def generate_text(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text asynchronously"""
        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}"

        try:
            # Check cache
            cache_key = self.generate_cache_key(request)
            if cache_key in self.cache:
                logger.info(f"Cache hit for request {request_id}")
                return self.cache[cache_key]

            # Update metrics
            self.metrics["requests_total"] += 1

            # Generate in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._generate_text_sync,
                request
            )

            # Calculate generation time
            generation_time = time.time() - start_time

            # Update metrics
            self.metrics["requests_success"] += 1
            self.metrics["total_generation_time"] += generation_time
            self.metrics["avg_generation_time"] = (
                self.metrics["total_generation_time"] / self.metrics["requests_success"]
            )

            response = GenerationResponse(
                generated_texts=result,
                generation_time=generation_time,
                model_name=self.model_name,
                request_id=request_id
            )

            # Cache response
            self.cache[cache_key] = response

            logger.info(f"Generated text for request {request_id} in {generation_time:.2f}s")
            return response

        except Exception as e:
            # Update metrics
            self.metrics["requests_failed"] += 1

            logger.error(f"Failed to generate text for request {request_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    def _generate_text_sync(self, request: GenerationRequest) -> List[str]:
        """Synchronous text generation"""
        try:
            outputs = self.generator(
                request.prompt,
                max_length=request.max_length,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=request.do_sample,
                num_return_sequences=request.num_return_sequences,
                pad_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )

            # Extract generated texts
            generated_texts = []
            for output in outputs:
                text = output['generated_text'].strip()
                generated_texts.append(text)

            return generated_texts

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics"""
        return {
            **self.metrics,
            "cache_size": len(self.cache),
            "cache_maxsize": self.cache.maxsize,
            "system_memory": psutil.virtual_memory().percent,
            "gpu_memory": self.get_gpu_memory() if torch.cuda.is_available() else None,
            "timestamp": datetime.now().isoformat()
        }

    def get_gpu_memory(self) -> Dict[str, float]:
        """Get GPU memory usage"""
        try:
            gpus = GPUtil.getGPUs()
            return {f"gpu_{i}": gpu.memoryUtil * 100 for i, gpu in enumerate(gpus)}
        except:
            return {}

# FastAPI app
app = FastAPI(title="LLM Model Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model server instance
model_server = None

@app.on_event("startup")
async def startup_event():
    """Initialize model server on startup"""
    global model_server
    model_name = os.getenv("MODEL_NAME", "microsoft/DialoGPT-medium")
    model_server = ModelServer(model_name)
    logger.info("Model server initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model_server
    if model_server:
        model_server.executor.shutdown(wait=True)
    logger.info("Model server shutdown")

@app.post("/generate", response_model=GenerationResponse)
async def generate_text(request: GenerationRequest):
    """Generate text endpoint"""
    return await model_server.generate_text(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_server is not None
    }

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint"""
    return model_server.get_metrics()

@app.post("/reload_model")
async def reload_model(model_name: str, background_tasks: BackgroundTasks):
    """Reload model endpoint"""
    async def reload():
        global model_server
        logger.info(f"Reloading model: {model_name}")
        old_server = model_server
        model_server = ModelServer(model_name)

        # Cleanup old server
        if old_server:
            old_server.executor.shutdown(wait=True)

        logger.info("Model reloaded successfully")

    background_tasks.add_task(reload)
    return {"message": "Model reload initiated"}

if __name__ == "__main__":
    uvicorn.run(
        "model_server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=1,
        reload=False
    )
```

### Model A/B Testing Framework

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import random
import hashlib
import json
from datetime import datetime, timedelta
import statistics
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ModelVariant(ABC):
    """Abstract base class for model variants"""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
        self.requests = 0
        self.responses = 0
        self.errors = 0
        self.total_latency = 0.0

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using this model variant"""
        pass

    def record_request(self):
        """Record incoming request"""
        self.requests += 1

    def record_response(self, latency: float):
        """Record successful response"""
        self.responses += 1
        self.total_latency += latency

    def record_error(self):
        """Record error"""
        self.errors += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        success_rate = self.responses / max(self.requests, 1)
        avg_latency = self.total_latency / max(self.responses, 1)

        return {
            "name": self.name,
            "weight": self.weight,
            "requests": self.requests,
            "responses": self.responses,
            "errors": self.errors,
            "success_rate": success_rate,
            "avg_latency": avg_latency
        }

class APIModelVariant(ModelVariant):
    """Model variant that calls an external API"""

    def __init__(self, name: str, api_url: str, api_key: str, weight: float = 1.0):
        super().__init__(name, weight)
        self.api_url = api_url
        self.api_key = api_key

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text via API call"""
        import aiohttp
        import time

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "prompt": prompt,
                    "max_tokens": kwargs.get("max_tokens", 100),
                    "temperature": kwargs.get("temperature", 0.7)
                }

                async with session.post(self.api_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        latency = time.time() - start_time
                        self.record_response(latency)
                        return result["generated_text"]
                    else:
                        self.record_error()
                        raise Exception(f"API call failed: {response.status}")

        except Exception as e:
            self.record_error()
            raise e

class LocalModelVariant(ModelVariant):
    """Model variant that uses a local model"""

    def __init__(self, name: str, model_server_url: str, weight: float = 1.0):
        super().__init__(name, weight)
        self.model_server_url = model_server_url

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text via local model server"""
        import aiohttp
        import time

        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "prompt": prompt,
                    "max_length": kwargs.get("max_length", 100),
                    "temperature": kwargs.get("temperature", 0.7)
                }

                async with session.post(f"{self.model_server_url}/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        latency = time.time() - start_time
                        self.record_response(latency)
                        return result["generated_texts"][0]
                    else:
                        self.record_error()
                        raise Exception(f"Model server call failed: {response.status}")

        except Exception as e:
            self.record_error()
            raise e

class TrafficSplitter:
    """Handles traffic splitting between model variants"""

    def __init__(self, variants: List[ModelVariant], sticky_routing: bool = False):
        self.variants = variants
        self.sticky_routing = sticky_routing
        self.user_assignments = {}  # user_id -> variant_name

        # Calculate cumulative weights for weighted random selection
        self.cumulative_weights = []
        cumulative = 0
        for variant in variants:
            cumulative += variant.weight
            self.cumulative_weights.append(cumulative)

        self.total_weight = cumulative

    def get_variant(self, user_id: Optional[str] = None) -> ModelVariant:
        """Get variant for user using consistent hashing or random selection"""

        if self.sticky_routing and user_id:
            # Use consistent hashing for sticky routing
            if user_id in self.user_assignments:
                variant_name = self.user_assignments[user_id]
                return next(v for v in self.variants if v.name == variant_name)

            # Assign user to variant
            hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            variant_index = hash_value % len(self.variants)
            variant = self.variants[variant_index]
            self.user_assignments[user_id] = variant.name
            return variant

        else:
            # Weighted random selection
            rand_value = random.uniform(0, self.total_weight)
            for i, cumulative_weight in enumerate(self.cumulative_weights):
                if rand_value <= cumulative_weight:
                    return self.variants[i]

        # Fallback to first variant
        return self.variants[0]

class ABTestingFramework:
    """A/B testing framework for LLM variants"""

    def __init__(self, traffic_splitter: TrafficSplitter):
        self.traffic_splitter = traffic_splitter
        self.experiments = {}
        self.metrics_history = defaultdict(list)

    def start_experiment(self, experiment_name: str, variants: List[str],
                        duration_days: int = 7):
        """Start a new A/B test experiment"""

        experiment = {
            "name": experiment_name,
            "variants": variants,
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(days=duration_days),
            "status": "running",
            "metrics": defaultdict(dict)
        }

        self.experiments[experiment_name] = experiment
        logger.info(f"Started experiment: {experiment_name}")

    async def generate_text(self, prompt: str, user_id: Optional[str] = None,
                          experiment_name: Optional[str] = None, **kwargs) -> Tuple[str, str]:
        """Generate text using appropriate variant"""

        # Get variant
        variant = self.traffic_splitter.get_variant(user_id)

        # Record request
        variant.record_request()

        try:
            # Generate text
            start_time = time.time()
            result = await variant.generate(prompt, **kwargs)
            latency = time.time() - start_time

            # Record successful response
            variant.record_response(latency)

            # Update experiment metrics if applicable
            if experiment_name and experiment_name in self.experiments:
                self.update_experiment_metrics(experiment_name, variant.name, latency)

            return result, variant.name

        except Exception as e:
            # Record error
            variant.record_error()
            raise e

    def update_experiment_metrics(self, experiment_name: str, variant_name: str, latency: float):
        """Update metrics for experiment"""

        if experiment_name not in self.experiments:
            return

        experiment = self.experiments[experiment_name]
        current_time = datetime.now()

        if variant_name not in experiment["metrics"]:
            experiment["metrics"][variant_name] = {
                "requests": 0,
                "responses": 0,
                "errors": 0,
                "total_latency": 0.0,
                "timestamps": []
            }

        metrics = experiment["metrics"][variant_name]
        metrics["requests"] += 1
        metrics["responses"] += 1
        metrics["total_latency"] += latency
        metrics["timestamps"].append(current_time)

        # Keep only last 1000 timestamps for memory efficiency
        if len(metrics["timestamps"]) > 1000:
            metrics["timestamps"] = metrics["timestamps"][-1000:]

    def get_experiment_results(self, experiment_name: str) -> Dict[str, Any]:
        """Get results for an experiment"""

        if experiment_name not in self.experiments:
            return {"error": "Experiment not found"}

        experiment = self.experiments[experiment_name]
        results = {
            "experiment_name": experiment_name,
            "status": experiment["status"],
            "start_time": experiment["start_time"].isoformat(),
            "end_time": experiment["end_time"].isoformat(),
            "variants": {}
        }

        for variant_name, metrics in experiment["metrics"].items():
            if metrics["responses"] > 0:
                avg_latency = metrics["total_latency"] / metrics["responses"]
                success_rate = metrics["responses"] / metrics["requests"]
            else:
                avg_latency = 0.0
                success_rate = 0.0

            results["variants"][variant_name] = {
                "requests": metrics["requests"],
                "responses": metrics["responses"],
                "errors": metrics["errors"],
                "avg_latency": avg_latency,
                "success_rate": success_rate
            }

        return results

    def get_variant_metrics(self) -> Dict[str, Any]:
        """Get current metrics for all variants"""

        return {
            variant.name: variant.get_metrics()
            for variant in self.traffic_splitter.variants
        }

    def stop_experiment(self, experiment_name: str):
        """Stop an experiment"""

        if experiment_name in self.experiments:
            self.experiments[experiment_name]["status"] = "completed"
            logger.info(f"Stopped experiment: {experiment_name}")

# Usage example
async def main():
    # Create model variants
    variants = [
        APIModelVariant("gpt-3.5-turbo", "https://api.openai.com/v1/completions", "sk-...", 0.7),
        LocalModelVariant("fine-tuned-model", "http://localhost:8000", 0.3)
    ]

    # Create traffic splitter
    traffic_splitter = TrafficSplitter(variants, sticky_routing=True)

    # Create A/B testing framework
    ab_tester = ABTestingFramework(traffic_splitter)

    # Start experiment
    ab_tester.start_experiment("model_comparison", ["gpt-3.5-turbo", "fine-tuned-model"], 7)

    # Generate text
    result, variant_used = await ab_tester.generate_text(
        "Hello, how are you?",
        user_id="user123",
        experiment_name="model_comparison"
    )

    print(f"Generated: {result} using {variant_used}")

    # Get experiment results
    results = ab_tester.get_experiment_results("model_comparison")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

## Model Monitoring and Evaluation

### Comprehensive Model Monitoring

```python
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import json
import hashlib
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import torch
from transformers import pipeline
import asyncio
import aiohttp
import time

logger = logging.getLogger(__name__)

class ModelMonitor:
    """Comprehensive monitoring system for LLM models"""

    def __init__(self, model_name: str, monitoring_window_hours: int = 24):
        self.model_name = model_name
        self.monitoring_window = timedelta(hours=monitoring_window_hours)

        # Metrics storage
        self.metrics_history = defaultdict(lambda: deque(maxlen=10000))

        # Performance baselines
        self.baselines = {
            "avg_latency": 0.0,
            "p95_latency": 0.0,
            "error_rate": 0.0,
            "throughput": 0.0
        }

        # Quality monitoring
        self.quality_metrics = {
            "toxicity_score": [],
            "relevance_score": [],
            "coherence_score": [],
            "factual_accuracy": []
        }

        # Drift detection
        self.reference_distribution = None
        self.drift_threshold = 0.1

        # Alert thresholds
        self.alert_thresholds = {
            "latency_p95": 5.0,  # seconds
            "error_rate": 0.05,  # 5%
            "toxicity_score": 0.8,  # 80%
            "drift_score": 0.2
        }

    def record_request(self, request_data: Dict[str, Any]):
        """Record incoming request"""
        timestamp = datetime.now()

        self.metrics_history["requests"].append({
            "timestamp": timestamp,
            "user_id": request_data.get("user_id"),
            "prompt_length": len(request_data.get("prompt", "")),
            "parameters": request_data
        })

    def record_response(self, response_data: Dict[str, Any], latency: float):
        """Record model response"""
        timestamp = datetime.now()

        self.metrics_history["responses"].append({
            "timestamp": timestamp,
            "latency": latency,
            "output_length": len(response_data.get("generated_text", "")),
            "finish_reason": response_data.get("finish_reason"),
            "model_version": response_data.get("model_version")
        })

        # Update rolling statistics
        self._update_statistics(latency)

    def record_error(self, error_type: str, error_message: str):
        """Record error"""
        timestamp = datetime.now()

        self.metrics_history["errors"].append({
            "timestamp": timestamp,
            "error_type": error_type,
            "error_message": error_message
        })

    def _update_statistics(self, latency: float):
        """Update rolling statistics"""
        self.metrics_history["latencies"].append(latency)

        # Keep only recent data
        cutoff_time = datetime.now() - self.monitoring_window
        self.metrics_history["latencies"] = deque(
            [l for t, l in zip(self.metrics_history["response_timestamps"],
                             self.metrics_history["latencies"])
             if t > cutoff_time],
            maxlen=10000
        )

    def evaluate_quality(self, prompt: str, response: str) -> Dict[str, float]:
        """Evaluate response quality"""
        quality_scores = {}

        try:
            # Toxicity detection
            quality_scores["toxicity"] = self._check_toxicity(response)

            # Relevance score (simple keyword matching)
            quality_scores["relevance"] = self._check_relevance(prompt, response)

            # Coherence score (basic length and structure check)
            quality_scores["coherence"] = self._check_coherence(response)

            # Factual accuracy (placeholder - would need fact-checking API)
            quality_scores["factual_accuracy"] = self._check_factual_accuracy(response)

            # Store quality metrics
            for metric, score in quality_scores.items():
                self.quality_metrics[metric].append(score)

                # Keep only recent scores
                if len(self.quality_metrics[metric]) > 1000:
                    self.quality_metrics[metric] = self.quality_metrics[metric][-1000:]

        except Exception as e:
            logger.error(f"Quality evaluation failed: {e}")

        return quality_scores

    def _check_toxicity(self, text: str) -> float:
        """Check text toxicity (placeholder implementation)"""
        # In production, use a proper toxicity detection model
        toxic_words = ["hate", "violence", "offensive"]
        text_lower = text.lower()
        toxicity_score = sum(1 for word in toxic_words if word in text_lower) / len(toxic_words)
        return min(toxicity_score, 1.0)

    def _check_relevance(self, prompt: str, response: str) -> float:
        """Check response relevance to prompt"""
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())

        if not prompt_words:
            return 0.0

        overlap = len(prompt_words.intersection(response_words))
        return overlap / len(prompt_words)

    def _check_coherence(self, text: str) -> float:
        """Check text coherence"""
        # Simple coherence check based on length and sentence structure
        sentences = text.split('.')
        if len(sentences) < 2:
            return 0.3

        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        coherence_score = min(avg_sentence_length / 20, 1.0)  # Normalize
        return coherence_score

    def _check_factual_accuracy(self, text: str) -> float:
        """Check factual accuracy (placeholder)"""
        # In production, integrate with fact-checking APIs or knowledge bases
        return 0.8  # Placeholder score

    def detect_drift(self, current_data: pd.DataFrame) -> float:
        """Detect data drift"""
        if self.reference_distribution is None:
            # Initialize reference distribution
            self.reference_distribution = self._calculate_distribution(current_data)
            return 0.0

        current_distribution = self._calculate_distribution(current_data)

        # Calculate distribution difference (simple KL divergence approximation)
        drift_score = self._calculate_distribution_difference(
            self.reference_distribution, current_distribution
        )

        return drift_score

    def _calculate_distribution(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate data distribution"""
        # Simple distribution based on text length
        lengths = data['text_length'] if 'text_length' in data.columns else [len(str(x)) for x in data.iloc[:, 0]]
        return {
            "mean_length": np.mean(lengths),
            "std_length": np.std(lengths),
            "min_length": np.min(lengths),
            "max_length": np.max(lengths)
        }

    def _calculate_distribution_difference(self, ref: Dict[str, float], curr: Dict[str, float]) -> float:
        """Calculate difference between distributions"""
        # Simple Euclidean distance
        diff_sum = 0
        for key in ref.keys():
            if key in curr:
                diff_sum += (ref[key] - curr[key]) ** 2

        return np.sqrt(diff_sum)

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics"""
        now = datetime.now()
        window_start = now - self.monitoring_window

        # Filter recent data
        recent_responses = [r for r in self.metrics_history["responses"] if r["timestamp"] > window_start]
        recent_errors = [e for e in self.metrics_history["errors"] if e["timestamp"] > window_start]

        # Calculate metrics
        if recent_responses:
            latencies = [r["latency"] for r in recent_responses]
            metrics = {
                "total_requests": len(recent_responses),
                "avg_latency": np.mean(latencies),
                "p50_latency": np.percentile(latencies, 50),
                "p95_latency": np.percentile(latencies, 95),
                "p99_latency": np.percentile(latencies, 99),
                "min_latency": np.min(latencies),
                "max_latency": np.max(latencies),
                "throughput": len(recent_responses) / self.monitoring_window.total_seconds() * 3600  # per hour
            }
        else:
            metrics = {
                "total_requests": 0,
                "avg_latency": 0.0,
                "p50_latency": 0.0,
                "p95_latency": 0.0,
                "p99_latency": 0.0,
                "min_latency": 0.0,
                "max_latency": 0.0,
                "throughput": 0.0
            }

        # Error metrics
        total_requests = len(recent_responses) + len(recent_errors)
        metrics["error_rate"] = len(recent_errors) / max(total_requests, 1)
        metrics["total_errors"] = len(recent_errors)

        # Quality metrics
        metrics["quality_scores"] = {}
        for metric_name, scores in self.quality_metrics.items():
            if scores:
                recent_scores = scores[-100:]  # Last 100 scores
                metrics["quality_scores"][metric_name] = {
                    "current": np.mean(recent_scores),
                    "min": np.min(recent_scores),
                    "max": np.max(recent_scores),
                    "std": np.std(recent_scores)
                }

        return metrics

    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alerts based on thresholds"""
        alerts = []
        metrics = self.get_current_metrics()

        # Latency alert
        if metrics["p95_latency"] > self.alert_thresholds["latency_p95"]:
            alerts.append({
                "type": "latency",
                "severity": "high",
                "message": f"P95 latency ({metrics['p95_latency']:.2f}s) exceeds threshold ({self.alert_thresholds['latency_p95']}s)",
                "value": metrics["p95_latency"],
                "threshold": self.alert_thresholds["latency_p95"]
            })

        # Error rate alert
        if metrics["error_rate"] > self.alert_thresholds["error_rate"]:
            alerts.append({
                "type": "error_rate",
                "severity": "high",
                "message": f"Error rate ({metrics['error_rate']:.2%}) exceeds threshold ({self.alert_thresholds['error_rate']:.2%})",
                "value": metrics["error_rate"],
                "threshold": self.alert_thresholds["error_rate"]
            })

        # Quality alerts
        for metric_name, scores in metrics["quality_scores"].items():
            threshold_key = f"{metric_name}_score"
            if threshold_key in self.alert_thresholds:
                if scores["current"] > self.alert_thresholds[threshold_key]:
                    alerts.append({
                        "type": "quality",
                        "severity": "medium",
                        "message": f"{metric_name} score ({scores['current']:.2f}) exceeds threshold ({self.alert_thresholds[threshold_key]})",
                        "value": scores["current"],
                        "threshold": self.alert_thresholds[threshold_key]
                    })

        return alerts

    def update_baselines(self):
        """Update performance baselines"""
        metrics = self.get_current_metrics()

        # Simple exponential moving average for baselines
        alpha = 0.1  # Smoothing factor

        self.baselines["avg_latency"] = (
            alpha * metrics["avg_latency"] + (1 - alpha) * self.baselines["avg_latency"]
        )
        self.baselines["p95_latency"] = (
            alpha * metrics["p95_latency"] + (1 - alpha) * self.baselines["p95_latency"]
        )
        self.baselines["error_rate"] = (
            alpha * metrics["error_rate"] + (1 - alpha) * self.baselines["error_rate"]
        )
        self.baselines["throughput"] = (
            alpha * metrics["throughput"] + (1 - alpha) * self.baselines["throughput"]
        )

# Integration with model server
class MonitoredModelServer:
    """Model server with integrated monitoring"""

    def __init__(self, model_name: str, monitor: ModelMonitor):
        self.model_name = model_name
        self.monitor = monitor
        # Model loading code here...

    async def generate_with_monitoring(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text with monitoring"""
        # Record request
        self.monitor.record_request(request)

        start_time = time.time()

        try:
            # Generate response
            response = await self._generate_text(request)

            # Record response
            latency = time.time() - start_time
            self.monitor.record_response(response, latency)

            # Evaluate quality
            quality_scores = self.monitor.evaluate_quality(
                request["prompt"],
                response["generated_text"]
            )

            # Add quality scores to response
            response["quality_scores"] = quality_scores

            return response

        except Exception as e:
            # Record error
            self.monitor.record_error(type(e).__name__, str(e))
            raise e

    async def _generate_text(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Actual text generation logic"""
        # Implementation depends on your model
        return {
            "generated_text": "Sample response",
            "finish_reason": "stop",
            "model_version": self.model_name
        }

    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get monitoring data"""
        return {
            "metrics": self.monitor.get_current_metrics(),
            "alerts": self.monitor.check_alerts(),
            "baselines": self.monitor.baselines
        }
```

## Cost Optimization and Scaling

### Cost Optimization Strategies

```python
from typing import Dict, List, Any, Optional, Tuple
import time
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import json
import os

logger = logging.getLogger(__name__)

class CostOptimizer:
    """Cost optimization system for LLM deployments"""

    def __init__(self):
        self.cost_metrics = defaultdict(float)
        self.usage_patterns = defaultdict(lambda: deque(maxlen=1000))
        self.pricing_tiers = {
            "gpt-3.5-turbo": {
                "input_per_1k": 0.0015,
                "output_per_1k": 0.002
            },
            "gpt-4": {
                "input_per_1k": 0.03,
                "output_per_1k": 0.06
            },
            "claude-2": {
                "input_per_1k": 0.008,
                "output_per_1k": 0.024
            }
        }

        # Optimization strategies
        self.strategies = {
            "caching": self._optimize_caching,
            "batching": self._optimize_batching,
            "model_selection": self._optimize_model_selection,
            "prompt_optimization": self._optimize_prompts
        }

    def track_cost(self, model_name: str, input_tokens: int, output_tokens: int,
                   request_type: str = "api_call"):
        """Track cost for a request"""
        if model_name not in self.pricing_tiers:
            logger.warning(f"Unknown model: {model_name}")
            return

        pricing = self.pricing_tiers[model_name]
        input_cost = (input_tokens / 1000) * pricing["input_per_1k"]
        output_cost = (output_tokens / 1000) * pricing["output_per_1k"]
        total_cost = input_cost + output_cost

        # Update cost metrics
        self.cost_metrics["total_cost"] += total_cost
        self.cost_metrics[f"{model_name}_cost"] += total_cost
        self.cost_metrics["total_requests"] += 1

        # Track usage pattern
        self.usage_patterns[model_name].append({
            "timestamp": datetime.now(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost,
            "request_type": request_type
        })

    def get_cost_summary(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get cost summary for time window"""
        cutoff_time = datetime.now() - time_window
        total_cost = 0.0
        model_costs = defaultdict(float)
        request_count = 0

        for model_name, usage_history in self.usage_patterns.items():
            for usage in usage_history:
                if usage["timestamp"] > cutoff_time:
                    total_cost += usage["cost"]
                    model_costs[model_name] += usage["cost"]
                    request_count += 1

        return {
            "total_cost": total_cost,
            "model_costs": dict(model_costs),
            "request_count": request_count,
            "avg_cost_per_request": total_cost / max(request_count, 1),
            "time_window_hours": time_window.total_seconds() / 3600
        }

    def _optimize_caching(self, requests: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float]:
        """Optimize by caching similar requests"""
        # Simple caching strategy - group similar prompts
        cache_hits = 0
        optimized_requests = []

        prompt_cache = {}

        for request in requests:
            prompt = request["prompt"]
            cache_key = hash(prompt)  # Simple hashing

            if cache_key in prompt_cache:
                # Cache hit - reuse previous result
                request["cached_result"] = prompt_cache[cache_key]
                cache_hits += 1
            else:
                optimized_requests.append(request)

        savings_percentage = cache_hits / max(len(requests), 1)
        return optimized_requests, savings_percentage

    def _optimize_batching(self, requests: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Optimize by batching requests"""
        batch_size = 10  # Configurable
        batches = []

        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batches.append(batch)

        return batches

    def _optimize_model_selection(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize by selecting appropriate models based on task complexity"""
        optimized_requests = []

        for request in requests:
            prompt_length = len(request["prompt"].split())
            task_complexity = self._assess_complexity(request["prompt"])

            # Select model based on complexity and cost
            if task_complexity == "simple" or prompt_length < 50:
                request["model"] = "gpt-3.5-turbo"  # Cheaper model
            elif task_complexity == "complex" or prompt_length > 200:
                request["model"] = "gpt-4"  # More capable model
            else:
                request["model"] = "claude-2"  # Balanced option

            optimized_requests.append(request)

        return optimized_requests

    def _assess_complexity(self, prompt: str) -> str:
        """Assess prompt complexity (simplified)"""
        complex_keywords = ["analyze", "compare", "explain", "design", "optimize"]
        prompt_lower = prompt.lower()

        complexity_score = sum(1 for keyword in complex_keywords if keyword in prompt_lower)

        if complexity_score >= 2:
            return "complex"
        elif complexity_score == 1:
            return "medium"
        else:
            return "simple"

    def _optimize_prompts(self, requests: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float]:
        """Optimize prompts to reduce token usage"""
        total_original_tokens = 0
        total_optimized_tokens = 0

        for request in requests:
            original_prompt = request["prompt"]
            total_original_tokens += len(original_prompt.split())

            # Simple prompt optimization
            optimized_prompt = self._compress_prompt(original_prompt)
            request["prompt"] = optimized_prompt
            total_optimized_tokens += len(optimized_prompt.split())

        savings_percentage = 1 - (total_optimized_tokens / max(total_original_tokens, 1))
        return requests, savings_percentage

    def _compress_prompt(self, prompt: str) -> str:
        """Compress prompt to reduce token count (simplified)"""
        # Remove unnecessary whitespace and repeated words
        import re

        # Basic compression
        compressed = re.sub(r'\s+', ' ', prompt.strip())

        # Remove redundant phrases (simplified example)
        redundant_phrases = ["please", "kindly", "I would like you to"]
        for phrase in redundant_phrases:
            compressed = compressed.replace(phrase, "")

        return compressed.strip()

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        recommendations = []
        cost_summary = self.get_cost_summary()

        # High cost alert
        if cost_summary["total_cost"] > 100:  # Configurable threshold
            recommendations.append({
                "type": "high_cost",
                "priority": "high",
                "message": f"Total cost (${cost_summary['total_cost']:.2f}) exceeds threshold",
                "action": "Review usage patterns and consider model optimization"
            })

        # Model cost analysis
        model_costs = cost_summary["model_costs"]
        if model_costs:
            most_expensive = max(model_costs.items(), key=lambda x: x[1])
            recommendations.append({
                "type": "model_cost",
                "priority": "medium",
                "message": f"Most expensive model: {most_expensive[0]} (${most_expensive[1]:.2f})",
                "action": "Consider using cheaper alternatives for simple tasks"
            })

        # Caching opportunity
        usage_patterns = list(self.usage_patterns.values())
        if usage_patterns and len(usage_patterns[0]) > 10:
            # Check for repeated patterns
            recent_requests = [req for pattern in usage_patterns for req in list(pattern)[-10:]]
            unique_prompts = len(set(req.get("prompt", "") for req in recent_requests))
            total_requests = len(recent_requests)

            if unique_prompts / total_requests < 0.5:  # Less than 50% unique
                recommendations.append({
                    "type": "caching",
                    "priority": "medium",
                    "message": f"Low prompt diversity ({unique_prompts}/{total_requests} unique)",
                    "action": "Implement response caching to reduce costs"
                })

        return recommendations

class AutoScaler:
    """Automatic scaling system for LLM deployments"""

    def __init__(self, min_instances: int = 1, max_instances: int = 10):
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.current_instances = min_instances

        # Scaling metrics
        self.request_queue = deque(maxlen=1000)
        self.response_times = deque(maxlen=1000)

        # Scaling thresholds
        self.scale_up_threshold = 0.8  # 80% utilization
        self.scale_down_threshold = 0.3  # 30% utilization
        self.cooldown_period = 300  # 5 minutes between scaling actions

        self.last_scale_time = 0

    def record_request(self):
        """Record incoming request"""
        self.request_queue.append(time.time())

    def record_response_time(self, response_time: float):
        """Record response time"""
        self.response_times.append(response_time)

    def should_scale_up(self) -> bool:
        """Check if should scale up"""
        if len(self.request_queue) < 10:  # Need minimum data
            return False

        # Check queue length (requests waiting)
        recent_requests = [t for t in self.request_queue if time.time() - t < 60]  # Last minute
        queue_length = len(recent_requests)

        # Check average response time
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            response_time_threshold = 2.0  # 2 seconds
        else:
            avg_response_time = 0

        # Scale up if high queue or slow responses
        utilization = min(queue_length / 10, avg_response_time / response_time_threshold)

        return utilization > self.scale_up_threshold and self.current_instances < self.max_instances

    def should_scale_down(self) -> bool:
        """Check if should scale down"""
        if len(self.request_queue) < 10:
            return False

        # Check utilization over last 5 minutes
        recent_requests = [t for t in self.request_queue if time.time() - t < 300]
        avg_requests_per_minute = len(recent_requests) / 5

        # Scale down if low utilization
        utilization = avg_requests_per_minute / (self.current_instances * 10)  # 10 requests/min per instance

        return utilization < self.scale_down_threshold and self.current_instances > self.min_instances

    def scale(self) -> Optional[str]:
        """Perform scaling action if needed"""
        current_time = time.time()

        # Check cooldown period
        if current_time - self.last_scale_time < self.cooldown_period:
            return None

        if self.should_scale_up():
            self.current_instances = min(self.current_instances + 1, self.max_instances)
            self.last_scale_time = current_time
            return f"scaled_up_to_{self.current_instances}"

        elif self.should_scale_down():
            self.current_instances = max(self.current_instances - 1, self.min_instances)
            self.last_scale_time = current_time
            return f"scaled_down_to_{self.current_instances}"

        return None

    def get_status(self) -> Dict[str, Any]:
        """Get current scaling status"""
        return {
            "current_instances": self.current_instances,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "queue_length": len(self.request_queue),
            "avg_response_time": sum(self.response_times) / max(len(self.response_times), 1),
            "last_scale_time": self.last_scale_time
        }

# Usage example
def create_cost_optimized_system():
    """Create a cost-optimized LLM system"""

    cost_optimizer = CostOptimizer()
    auto_scaler = AutoScaler(min_instances=2, max_instances=20)

    # Configuration for different models
    model_configs = {
        "gpt-3.5-turbo": {
            "cost_per_1k_input": 0.0015,
            "cost_per_1k_output": 0.002,
            "max_tokens": 4096
        },
        "gpt-4": {
            "cost_per_1k_input": 0.03,
            "cost_per_1k_output": 0.06,
            "max_tokens": 8192
        }
    }

    return {
        "cost_optimizer": cost_optimizer,
        "auto_scaler": auto_scaler,
        "model_configs": model_configs
    }
```

This comprehensive guide covers LLMOps fundamentals, distributed training infrastructure, model deployment and serving, A/B testing frameworks, monitoring and evaluation systems, and cost optimization strategies. The code examples demonstrate production-ready implementations for managing the complete LLM lifecycle in enterprise environments.
