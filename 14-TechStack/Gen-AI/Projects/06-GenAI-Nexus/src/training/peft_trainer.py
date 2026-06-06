"""
Gen-AI Tool: PEFT (Parameter-Efficient Fine-Tuning)
=====================================================
Demonstrates: LoRA fine-tuning, QLoRA, adapter configuration,
PEFT model wrapping, trainable parameter reduction, and
domain-specific fine-tuning for startup Q&A.

Role in GenAI Nexus: Fine-tune a compact LLM (LLaMA-3.2-1B) on startup
advisory Q&A pairs to create a specialized startup advisor model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Startup Q&A pairs for LoRA fine-tuning
STARTUP_QA_PAIRS = [
    {
        "instruction": "What is the ideal pricing for a B2B SaaS legal tech product targeting small law firms?",
        "response": (
            "For small law firms (1-10 attorneys), target $200-500/month per firm (not per user). "
            "Key principles: flat-rate pricing (lawyers hate surprises), annual discount of 20%, "
            "free 14-day trial. Starter at $199/mo, Professional at $499/mo. "
            "Benchmark: Clio charges $49-149/user/month. Your AI offering should justify premium."
        ),
    },
    {
        "instruction": "How should a legal tech startup approach SOC2 certification?",
        "response": (
            "SOC2 Type I timeline: 3 months, cost $15-25K. Start immediately — enterprise deals require it. "
            "Use AWS (pre-built controls), Vanta or Drata for automation (~$12K/yr), "
            "Tugboat Logic for evidence collection. "
            "Quick wins: MFA everywhere, encryption at rest/transit, access logs, incident response plan. "
            "Get Type I first (point-in-time), then Type II (12-month window) before enterprise sales push."
        ),
    },
    {
        "instruction": "What are the best acquisition channels for a legal tech B2B SaaS?",
        "response": (
            "Ranked by CAC efficiency: "
            "1. Bar association partnerships ($0 CAC, 10-20 leads/event). "
            "2. Practice management marketplace (Clio, MyCase) — 150K potential customers. "
            "3. Founder content on LinkedIn (builds trust with attorneys). "
            "4. Referral program (attorneys trust peer recommendations above all). "
            "5. Google Ads — 'contract review software' $3-8 CPC. "
            "Avoid: cold email (spam filters), billboards, podcast ads (low intent)."
        ),
    },
    {
        "instruction": "When should a startup raise a seed round vs bootstrap?",
        "response": (
            "Raise seed when: (1) Market requires speed — competitors well-funded, (2) "
            "Capital can 10x growth that bootstrapping can't, (3) $500K+ ARR not reachable in 18 months solo. "
            "Bootstrap when: (1) High-margin SaaS, (2) Strong founder network for first customers, "
            "(3) You value control > speed, (4) Market is niche/slow-moving. "
            "Legal tech: lean toward raising — Harvey AI proves capital accelerates distribution."
        ),
    },
    {
        "instruction": "What is a good LTV/CAC ratio for B2B SaaS?",
        "response": (
            "Healthy: LTV/CAC > 3x. Excellent: > 5x. "
            "For legal tech at $299/mo (Starter): "
            "Avg tenure = 18 months → LTV = $299 × 18 = $5,382. "
            "Target CAC < $1,800 for 3x ratio. "
            "Track: payback period (LTV/CAC months) < 18 months, NRR > 100%, logo churn < 5%/yr. "
            "At 3x+ ratio, growth is self-funding — key metric for Series A readiness."
        ),
    },
]


@dataclass
class LoRAConfig:
    """LoRA hyperparameters."""

    r: int = 8                   # Rank — lower = fewer params, higher = more capacity
    lora_alpha: int = 16         # LoRA scaling factor
    target_modules: list[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    lora_dropout: float = 0.1
    bias: str = "none"           # "none" | "all" | "lora_only"


@dataclass
class TrainingConfig:
    base_model: str = "meta-llama/Llama-3.2-1B"
    output_dir: str = "./data/peft_model"
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-4
    max_seq_length: int = 512
    use_4bit: bool = True        # QLoRA (4-bit quantization)


@dataclass
class PEFTResult:
    base_model: str
    trainable_params: int
    total_params: int
    trainable_pct: float
    epochs: int
    final_loss: float


class PEFTTrainer:
    """
    PEFT LoRA fine-tuner for startup advisory LLM.

    Demonstrates:
    - LoRA configuration (rank, alpha, target modules)
    - QLoRA: LoRA + 4-bit quantization (runs on consumer GPU)
    - PEFT model wrapping with get_peft_model()
    - Training loop with Hugging Face Trainer
    - Trainable parameter analysis
    - Model merging (merge LoRA weights back to base)
    """

    def __init__(self, lora_config: LoRAConfig | None = None, training_config: TrainingConfig | None = None):
        self.lora_config = lora_config or LoRAConfig()
        self.training_config = training_config or TrainingConfig()
        self._peft_available = False
        self._model = None
        self._tokenizer = None

        try:
            import peft  # noqa: F401
            self._peft_available = True
        except ImportError:
            pass

    def prepare_model(self) -> bool:
        """Load base model + apply LoRA adapters."""
        if not self._peft_available:
            print(
                f"[Demo] Would prepare {self.training_config.base_model} with LoRA\n"
                f"  LoRA rank={self.lora_config.r}, alpha={self.lora_config.lora_alpha}\n"
                f"  Target modules: {self.lora_config.target_modules}\n"
                f"  QLoRA (4-bit): {self.training_config.use_4bit}"
            )
            return False

        try:
            import torch
            from peft import LoraConfig, TaskType, get_peft_model
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

            # QLoRA: 4-bit quantization
            bnb_config = None
            if self.training_config.use_4bit:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                )

            self._tokenizer = AutoTokenizer.from_pretrained(self.training_config.base_model)
            self._tokenizer.pad_token = self._tokenizer.eos_token

            base_model = AutoModelForCausalLM.from_pretrained(
                self.training_config.base_model,
                quantization_config=bnb_config,
                device_map="auto",
            )

            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.lora_config.r,
                lora_alpha=self.lora_config.lora_alpha,
                target_modules=self.lora_config.target_modules,
                lora_dropout=self.lora_config.lora_dropout,
                bias=self.lora_config.bias,
            )

            self._model = get_peft_model(base_model, peft_config)
            self._model.print_trainable_parameters()
            return True

        except Exception as e:
            print(f"[Warning] Model preparation failed: {e}")
            return False

    def train(self, qa_pairs: list[dict] | None = None) -> PEFTResult:
        """Fine-tune with LoRA on startup Q&A data."""
        data = qa_pairs or STARTUP_QA_PAIRS

        if not self._peft_available or self._model is None:
            # Demo: simulate training stats
            print(f"[Demo] LoRA fine-tuning on {len(data)} Q&A pairs")
            print(f"  Base model: {self.training_config.base_model}")
            print(f"  LoRA rank: {self.lora_config.r} | Alpha: {self.lora_config.lora_alpha}")

            # Typical LoRA stats: ~0.1% trainable params
            total = 1_000_000_000  # 1B model
            trainable = int(total * 0.001)  # 0.1%

            for epoch in range(self.training_config.num_epochs):
                loss = 2.1 - epoch * 0.4
                print(f"  Epoch {epoch+1}/{self.training_config.num_epochs} — loss: {loss:.3f}")

            return PEFTResult(
                base_model=self.training_config.base_model,
                trainable_params=trainable,
                total_params=total,
                trainable_pct=0.1,
                epochs=self.training_config.num_epochs,
                final_loss=2.1 - (self.training_config.num_epochs - 1) * 0.4,
            )

        try:
            from datasets import Dataset
            from transformers import DataCollatorForLanguageModeling, Trainer, TrainingArguments

            # Format data as instruction-tuning format
            def format_sample(sample: dict) -> str:
                return (
                    f"### Instruction:\n{sample['instruction']}\n\n"
                    f"### Response:\n{sample['response']}\n"
                )

            texts = [format_sample(s) for s in data]
            encodings = self._tokenizer(
                texts,
                truncation=True,
                max_length=self.training_config.max_seq_length,
                padding="max_length",
            )
            dataset = Dataset.from_dict(encodings)

            training_args = TrainingArguments(
                output_dir=self.training_config.output_dir,
                num_train_epochs=self.training_config.num_epochs,
                per_device_train_batch_size=self.training_config.batch_size,
                learning_rate=self.training_config.learning_rate,
                logging_steps=1,
                save_strategy="no",
                report_to="none",
            )

            trainer = Trainer(
                model=self._model,
                args=training_args,
                train_dataset=dataset,
                data_collator=DataCollatorForLanguageModeling(self._tokenizer, mlm=False),
            )

            trainer.train()

            trainable = sum(p.numel() for p in self._model.parameters() if p.requires_grad)
            total = sum(p.numel() for p in self._model.parameters())

            return PEFTResult(
                base_model=self.training_config.base_model,
                trainable_params=trainable,
                total_params=total,
                trainable_pct=round(trainable / total * 100, 2),
                epochs=self.training_config.num_epochs,
                final_loss=trainer.state.log_history[-1].get("loss", 0.0),
            )

        except Exception as e:
            print(f"Training error: {e}")
            return PEFTResult(
                base_model=self.training_config.base_model,
                trainable_params=0,
                total_params=0,
                trainable_pct=0.0,
                epochs=0,
                final_loss=0.0,
            )

    def generate(self, instruction: str, max_new_tokens: int = 200) -> str:
        """Generate startup advice from fine-tuned model."""
        if not self._peft_available or self._model is None:
            # Demo: return relevant Q&A from training data
            for qa in STARTUP_QA_PAIRS:
                if any(word in instruction.lower() for word in qa["instruction"].lower().split()[:5]):
                    return f"[Demo LoRA Response]\n{qa['response']}"
            return f"[Demo] LoRA model would answer: {instruction}"

        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)

        with __import__("torch").no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.3,
                do_sample=True,
            )

        response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("### Response:\n")[-1].strip()


def demo():
    print("=" * 60)
    print("DEMO: PEFT / LoRA Fine-Tuning")
    print("=" * 60)
    trainer = PEFTTrainer()

    print("\n[1] Prepare Model with LoRA Adapters")
    trainer.prepare_model()

    print("\n[2] LoRA Configuration")
    print(f"  Rank (r): {trainer.lora_config.r}")
    print(f"  Alpha: {trainer.lora_config.lora_alpha}")
    print(f"  Target modules: {trainer.lora_config.target_modules}")
    print(f"  QLoRA (4-bit): {trainer.training_config.use_4bit}")
    print(f"  Trainable params (typical): ~0.1% of {trainer.training_config.base_model}")

    print(f"\n[3] Fine-tune on {len(STARTUP_QA_PAIRS)} Startup Q&A Pairs")
    result = trainer.train()
    print(f"\n  Base model: {result.base_model}")
    print(f"  Trainable params: {result.trainable_pct:.1f}% ({result.trainable_params:,} / {result.total_params:,})")
    print(f"  Final loss: {result.final_loss:.3f}")

    print("\n[4] Generate Startup Advice")
    questions = [
        "What is the ideal pricing for a legal tech SaaS?",
        "When should a startup raise seed funding?",
        "What is a good LTV/CAC ratio?",
    ]
    for q in questions:
        print(f"\n  Q: {q}")
        answer = trainer.generate(q)
        print(f"  A: {answer[:200]}...")


if __name__ == "__main__":
    demo()
