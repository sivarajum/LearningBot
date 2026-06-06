"""
Gen-AI Tool: Transfer Learning
================================
Demonstrates: Fine-tuning DistilBERT for legal domain, feature
extraction from pre-trained models, domain adaptation, evaluation,
and serving the adapted model.

Role in GenAI Nexus: Adapt a pre-trained DistilBERT to the legal tech
domain — improves classification and NER accuracy on legal text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Domain-specific training samples for fine-tuning
LEGAL_DOMAIN_DATA = [
    # (text, label) — legal domain classification
    ("This agreement shall be governed by the laws of California", "contract"),
    ("The party of the first part hereby agrees to indemnify", "contract"),
    ("Annual recurring revenue grew 150% year over year", "financial"),
    ("Series A funding closed at $5M pre-money valuation of $20M", "financial"),
    ("AI system achieves 94% accuracy on contract clause extraction", "technical"),
    ("Transformer architecture fine-tuned on legal corpus", "technical"),
    ("Market size for legal tech estimated at $45 billion by 2025", "market"),
    ("TAM expansion driven by AI adoption in mid-market firms", "market"),
    ("Product-led growth strategy targeting solo practitioners", "strategy"),
    ("Beachhead market: NDA review for 1-10 attorney firms", "strategy"),
]

LABEL_MAP = {"contract": 0, "financial": 1, "technical": 2, "market": 3, "strategy": 4}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}


@dataclass
class TransferConfig:
    base_model: str = "distilbert-base-uncased"
    num_labels: int = len(LABEL_MAP)
    learning_rate: float = 2e-5
    batch_size: int = 8
    epochs: int = 3
    max_length: int = 128


@dataclass
class FineTuneResult:
    base_model: str
    num_labels: int
    epochs_trained: int
    final_accuracy: float
    domain: str = "legal_tech"


@dataclass
class DomainPrediction:
    text: str
    predicted_label: str
    confidence: float
    all_scores: dict[str, float] = field(default_factory=dict)


class TransferLearningAdapter:
    """
    Transfer Learning adapter for domain adaptation.

    Demonstrates:
    - Loading pre-trained HuggingFace model
    - Adding classification head for domain labels
    - Fine-tuning on domain-specific data
    - Feature extraction (frozen base, only head trained)
    - Full fine-tuning (all layers updated)
    - Model evaluation on domain test set
    """

    def __init__(self, config: TransferConfig | None = None):
        self.config = config or TransferConfig()
        self._model = None
        self._tokenizer = None
        self._transformers_available = False
        self._fine_tuned = False

        try:
            import transformers  # noqa: F401
            self._transformers_available = True
        except ImportError:
            pass

    def load_base_model(self, mode: str = "full_finetune") -> bool:
        """
        Load pre-trained model for fine-tuning.

        Args:
            mode: "full_finetune" (all layers) | "feature_extraction" (head only)
        """
        if not self._transformers_available:
            print(f"[Demo] Would load {self.config.base_model} for {mode}")
            return False

        try:
            from transformers import AutoTokenizer, DistilBertForSequenceClassification

            self._tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
            self._model = DistilBertForSequenceClassification.from_pretrained(
                self.config.base_model,
                num_labels=self.config.num_labels,
            )

            if mode == "feature_extraction":
                # Freeze base model — only train classification head
                for param in self._model.distilbert.parameters():
                    param.requires_grad = False
                trainable = sum(p.numel() for p in self._model.parameters() if p.requires_grad)
                print(f"Feature extraction mode: {trainable:,} trainable params (head only)")
            else:
                trainable = sum(p.numel() for p in self._model.parameters())
                print(f"Full fine-tune mode: {trainable:,} trainable params")

            return True
        except Exception as e:
            print(f"[Warning] Could not load model: {e}")
            return False

    def fine_tune(
        self, data: list[tuple[str, str]] | None = None
    ) -> FineTuneResult:
        """
        Fine-tune the model on domain-specific data.
        Uses simple training loop to demonstrate the pattern.
        """
        training_data = data or LEGAL_DOMAIN_DATA

        if not self._transformers_available or self._model is None:
            # Demo mode: simulate training
            print(f"[Demo] Fine-tuning {self.config.base_model} on {len(training_data)} samples")
            for epoch in range(self.config.epochs):
                acc = 0.62 + epoch * 0.08
                print(f"  Epoch {epoch+1}/{self.config.epochs} — loss: {0.9 - epoch*0.2:.3f}, acc: {acc:.3f}")

            self._fine_tuned = True
            return FineTuneResult(
                base_model=self.config.base_model,
                num_labels=self.config.num_labels,
                epochs_trained=self.config.epochs,
                final_accuracy=0.78,
            )

        try:
            import torch
            from torch.optim import AdamW
            from torch.utils.data import DataLoader, Dataset

            class TextDataset(Dataset):
                def __init__(self, data, tokenizer, max_len):
                    self.data = data
                    self.tokenizer = tokenizer
                    self.max_len = max_len

                def __len__(self):
                    return len(self.data)

                def __getitem__(self, idx):
                    text, label = self.data[idx]
                    enc = self.tokenizer(
                        text,
                        truncation=True,
                        padding="max_length",
                        max_length=self.max_len,
                        return_tensors="pt",
                    )
                    return {
                        "input_ids": enc["input_ids"].squeeze(),
                        "attention_mask": enc["attention_mask"].squeeze(),
                        "labels": torch.tensor(LABEL_MAP[label]),
                    }

            dataset = TextDataset(training_data, self._tokenizer, self.config.max_length)
            loader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)

            optimizer = AdamW(self._model.parameters(), lr=self.config.learning_rate)
            self._model.train()

            final_acc = 0.0
            for epoch in range(self.config.epochs):
                total_loss, correct, total = 0.0, 0, 0
                for batch in loader:
                    optimizer.zero_grad()
                    outputs = self._model(**{k: v for k, v in batch.items()})
                    loss = outputs.loss
                    loss.backward()
                    optimizer.step()

                    preds = outputs.logits.argmax(dim=-1)
                    correct += (preds == batch["labels"]).sum().item()
                    total += len(batch["labels"])
                    total_loss += loss.item()

                final_acc = correct / total
                print(f"  Epoch {epoch+1}: loss={total_loss/len(loader):.3f}, acc={final_acc:.3f}")

            self._fine_tuned = True
            return FineTuneResult(
                base_model=self.config.base_model,
                num_labels=self.config.num_labels,
                epochs_trained=self.config.epochs,
                final_accuracy=final_acc,
            )

        except Exception as e:
            print(f"Training error: {e}")
            self._fine_tuned = True
            return FineTuneResult(
                base_model=self.config.base_model,
                num_labels=self.config.num_labels,
                epochs_trained=0,
                final_accuracy=0.0,
            )

    def predict(self, texts: list[str]) -> list[DomainPrediction]:
        """Classify texts using the fine-tuned model."""
        if not self._transformers_available or self._model is None:
            # Demo predictions
            labels = list(LABEL_MAP.keys())
            return [
                DomainPrediction(
                    text=text,
                    predicted_label=labels[i % len(labels)],
                    confidence=0.82 + i * 0.02,
                    all_scores={l: round(0.8 if l == labels[i % len(labels)] else 0.05, 3) for l in labels},
                )
                for i, text in enumerate(texts)
            ]

        import torch

        self._model.eval()
        results = []

        with torch.no_grad():
            for text in texts:
                enc = self._tokenizer(
                    text,
                    truncation=True,
                    max_length=self.config.max_length,
                    return_tensors="pt",
                )
                outputs = self._model(**enc)
                probs = torch.softmax(outputs.logits, dim=-1)[0].tolist()
                pred_idx = probs.index(max(probs))

                results.append(
                    DomainPrediction(
                        text=text,
                        predicted_label=ID_TO_LABEL[pred_idx],
                        confidence=round(max(probs), 4),
                        all_scores={ID_TO_LABEL[i]: round(p, 4) for i, p in enumerate(probs)},
                    )
                )

        return results

    def extract_features(self, text: str) -> list[float]:
        """
        Extract [CLS] token embedding as document representation.
        Useful for downstream ML tasks without full fine-tuning.
        """
        if not self._transformers_available or self._model is None:
            import hashlib
            import math
            import random

            seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
            rng = random.Random(seed)
            raw = [rng.gauss(0, 1) for _ in range(768)]  # DistilBERT hidden size
            mag = math.sqrt(sum(x * x for x in raw))
            return [x / mag for x in raw]

        import torch

        self._model.eval()
        with torch.no_grad():
            enc = self._tokenizer(
                text, truncation=True, max_length=128, return_tensors="pt"
            )
            # Get hidden states from base model
            base = self._model.distilbert(**enc)
            cls_embedding = base.last_hidden_state[:, 0, :].squeeze().tolist()
        return cls_embedding


def demo():
    print("=" * 60)
    print("DEMO: Transfer Learning — DistilBERT Domain Adaptation")
    print("=" * 60)

    adapter = TransferLearningAdapter()

    print("\n[1] Load Base Model (Feature Extraction Mode)")
    loaded = adapter.load_base_model(mode="feature_extraction")
    print(f"Loaded: {loaded}")

    print("\n[2] Fine-tune on Legal Tech Data")
    result = adapter.fine_tune(LEGAL_DOMAIN_DATA)
    print(f"Final accuracy: {result.final_accuracy:.1%}")
    print(f"Model: {result.base_model} | Labels: {result.num_labels}")

    print("\n[3] Domain Classification")
    test_texts = [
        "The contract shall be governed by New York state law",
        "ARR grew from $500K to $2.1M in 12 months",
        "Transformer model achieves 94% F1 on NER task",
        "Legal tech TAM estimated at $45B growing at 18.9% CAGR",
        "PLG strategy drives organic growth through product virality",
    ]
    predictions = adapter.predict(test_texts)
    for pred in predictions:
        print(f"\n  Text: {pred.text[:60]}...")
        print(f"  Predicted: {pred.predicted_label} (confidence={pred.confidence:.1%})")

    print("\n[4] Feature Extraction ([CLS] embedding)")
    text = "AI legal document analyzer for law firms"
    features = adapter.extract_features(text)
    print(f"Text: {text}")
    print(f"Feature vector dimensions: {len(features)}")
    print(f"First 5 values: {[round(f, 4) for f in features[:5]]}")


if __name__ == "__main__":
    demo()
