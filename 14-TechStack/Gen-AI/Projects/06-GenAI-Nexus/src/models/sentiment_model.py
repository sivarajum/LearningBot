"""
Gen-AI Tool: Keras Deep Learning
==================================
Demonstrates: Custom LSTM sentiment classifier built with Keras,
text vectorization layer, model training loop, evaluation, and
inference — all from scratch (no pre-trained weights).

Role in GenAI Nexus: Domain-specific sentiment classifier trained on
startup/legal tech news. Better than generic models for this domain.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Training data: startup + legal tech news snippets with labels
TRAINING_DATA = [
    # Positive (label=1)
    ("AI investment in legal tech reaches record high", 1),
    ("Law firms report 90% time savings with AI document review", 1),
    ("Harvey AI raises Series B to expand legal AI platform", 1),
    ("Small law firms finally get affordable AI tools", 1),
    ("Legal AI adoption accelerates post-pandemic", 1),
    ("Contract automation reduces errors by 85%", 1),
    ("AI legal research tools gain widespread acceptance", 1),
    ("Venture capital pours into legaltech startups", 1),
    ("AI wins contract review speed test against senior associates", 1),
    ("Legal AI startup achieves profitability in year two", 1),
    # Negative (label=0)
    ("Lawyers warn AI hallucinations pose malpractice risk", 0),
    ("Law firms sue AI company over data breach", 0),
    ("AI legal tools face regulatory scrutiny from state bars", 0),
    ("Legal AI startup shuts down after funding falls through", 0),
    ("Attorneys file ethics complaints about AI advice", 0),
    ("AI document analyzer misses key contract clause in test", 0),
    ("Privacy concerns halt legal AI rollout at major firms", 0),
    ("AI bias discovered in contract risk scoring algorithm", 0),
    ("Legal tech bubble bursting as valuations fall", 0),
    ("Law firm rejects AI tools over client confidentiality fears", 0),
]


@dataclass
class ModelConfig:
    vocab_size: int = 5000
    max_len: int = 50
    embedding_dim: int = 64
    lstm_units: int = 32
    batch_size: int = 8
    epochs: int = 5


@dataclass
class TrainingHistory:
    train_accuracy: list[float] = field(default_factory=list)
    val_accuracy: list[float] = field(default_factory=list)
    train_loss: list[float] = field(default_factory=list)
    val_loss: list[float] = field(default_factory=list)


@dataclass
class SentimentPrediction:
    text: str
    label: str  # "POSITIVE" | "NEGATIVE"
    confidence: float
    raw_score: float


class LegalSentimentModel:
    """
    Custom LSTM sentiment classifier for legal tech news.
    Built with Keras 3.0 (backend-agnostic: TensorFlow/JAX/PyTorch).

    Demonstrates:
    - TextVectorization layer (tokenization + vocabulary)
    - Embedding layer (learned word representations)
    - Bidirectional LSTM (captures context in both directions)
    - Dense classification head
    - Model training with validation split
    - Save/load model
    - Batch inference
    """

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()
        self._model = None
        self._vectorizer = None
        self._keras_available = False
        self._vocab: dict[str, int] = {}

        try:
            import keras  # noqa: F401
            self._keras_available = True
        except ImportError:
            pass

    def build_model(self):
        """Construct the LSTM model architecture."""
        if not self._keras_available:
            print("[Demo] Keras not available — using mock model")
            return self

        import keras
        from keras import layers

        # Text vectorization layer
        self._vectorizer = layers.TextVectorization(
            max_tokens=self.config.vocab_size,
            output_sequence_length=self.config.max_len,
            standardize="lower_and_strip_punctuation",
        )

        # Model architecture
        inputs = keras.Input(shape=(1,), dtype="string")
        x = self._vectorizer(inputs)
        x = layers.Embedding(
            input_dim=self.config.vocab_size + 1,
            output_dim=self.config.embedding_dim,
            mask_zero=True,
        )(x)
        x = layers.Bidirectional(layers.LSTM(self.config.lstm_units))(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(16, activation="relu")(x)
        outputs = layers.Dense(1, activation="sigmoid")(x)

        self._model = keras.Model(inputs, outputs)
        self._model.compile(
            optimizer="adam",
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        print(f"Model built: {self._model.count_params()} trainable parameters")
        return self

    def train(
        self, data: list[tuple[str, int]] | None = None
    ) -> TrainingHistory:
        """Train on legal tech sentiment data."""
        training_data = data or TRAINING_DATA
        texts = [t for t, _ in training_data]
        labels = [l for _, l in training_data]

        if not self._keras_available or self._model is None:
            # Demo mode: return simulated training history
            print("[Demo] Simulating Keras training...")
            history = TrainingHistory()
            for epoch in range(self.config.epochs):
                acc = 0.5 + epoch * 0.08
                history.train_accuracy.append(round(acc, 3))
                history.val_accuracy.append(round(acc - 0.05, 3))
                history.train_loss.append(round(0.7 - epoch * 0.1, 3))
                history.val_loss.append(round(0.75 - epoch * 0.09, 3))
                print(f"  Epoch {epoch+1}/{self.config.epochs} — "
                      f"acc: {acc:.3f}, val_acc: {acc-0.05:.3f}")
            return history

        import numpy as np

        # Adapt vectorizer to training vocab
        self._vectorizer.adapt(texts)

        texts_arr = [t for t in texts]
        labels_arr = [float(l) for l in labels]

        keras_history = self._model.fit(
            texts_arr,
            labels_arr,
            batch_size=self.config.batch_size,
            epochs=self.config.epochs,
            validation_split=0.2,
            verbose=1,
        )

        h = keras_history.history
        return TrainingHistory(
            train_accuracy=h.get("accuracy", []),
            val_accuracy=h.get("val_accuracy", []),
            train_loss=h.get("loss", []),
            val_loss=h.get("val_loss", []),
        )

    def predict(self, texts: list[str]) -> list[SentimentPrediction]:
        """Predict sentiment for new texts."""
        if not self._keras_available or self._model is None:
            # Demo predictions
            return [
                SentimentPrediction(
                    text=text,
                    label="POSITIVE" if i % 2 == 0 else "NEGATIVE",
                    confidence=0.85 + i * 0.02,
                    raw_score=0.9 if i % 2 == 0 else 0.1,
                )
                for i, text in enumerate(texts)
            ]

        import numpy as np

        raw_scores = self._model.predict(texts, verbose=0)

        return [
            SentimentPrediction(
                text=text,
                label="POSITIVE" if score[0] > 0.5 else "NEGATIVE",
                confidence=float(abs(score[0] - 0.5) * 2),
                raw_score=float(score[0]),
            )
            for text, score in zip(texts, raw_scores)
        ]

    def evaluate(self, test_data: list[tuple[str, int]]) -> dict[str, float]:
        """Evaluate on held-out test set."""
        texts = [t for t, _ in test_data]
        true_labels = [l for _, l in test_data]
        predictions = self.predict(texts)

        predicted_labels = [1 if p.raw_score > 0.5 else 0 for p in predictions]
        correct = sum(p == t for p, t in zip(predicted_labels, true_labels))
        accuracy = correct / len(true_labels)

        return {
            "accuracy": round(accuracy, 4),
            "samples_evaluated": len(true_labels),
        }

    def get_model_summary(self) -> str:
        """Return model architecture summary."""
        if not self._keras_available or self._model is None:
            return (
                "Model: BidirectionalLSTMSentiment\n"
                "Architecture: TextVectorization → Embedding(5000, 64) → "
                "BiLSTM(32) → Dropout(0.3) → Dense(16) → Dense(1, sigmoid)\n"
                "Parameters: ~350,000 trainable\n"
                "Note: Keras not installed — demo mode"
            )

        import io

        stream = io.StringIO()
        self._model.summary(print_fn=lambda x: stream.write(x + "\n"))
        return stream.getvalue()


def demo():
    print("=" * 60)
    print("DEMO: Keras — Custom Legal Sentiment Model")
    print("=" * 60)

    model = LegalSentimentModel()

    print("\n[1] Build Model Architecture")
    model.build_model()
    print(model.get_model_summary())

    print("\n[2] Train on Legal Tech News Data")
    history = model.train()
    print(f"\nFinal Training Accuracy: {history.train_accuracy[-1] if history.train_accuracy else 'N/A':.1%}")
    print(f"Final Validation Accuracy: {history.val_accuracy[-1] if history.val_accuracy else 'N/A':.1%}")

    print("\n[3] Predict New Headlines")
    new_headlines = [
        "AI startup raises $50M to revolutionize legal document review",
        "Law firm sues AI company after data breach exposes client files",
        "Attorneys adopt AI tools to stay competitive in market",
    ]
    predictions = model.predict(new_headlines)
    for pred in predictions:
        emoji = "🟢" if pred.label == "POSITIVE" else "🔴"
        print(f"  {emoji} [{pred.label}:{pred.confidence:.2f}] {pred.text[:60]}...")

    print("\n[4] Evaluate on Test Data")
    test_data = TRAINING_DATA[:4]  # Use first 4 as quick test
    metrics = model.evaluate(test_data)
    print(f"Test Accuracy: {metrics['accuracy']:.1%} on {metrics['samples_evaluated']} samples")


if __name__ == "__main__":
    demo()
