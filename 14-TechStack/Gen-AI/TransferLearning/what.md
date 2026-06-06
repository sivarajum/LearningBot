# Transfer Learning: Complete Guide

## 1. What is Transfer Learning?

Transfer learning reuses a model trained on one task (source) as the starting point for a different task (target). Instead of training from scratch, you leverage learned representations — dramatically reducing data and compute needs.

**Why it works:** Deep networks learn hierarchical features:
- **Early layers:** Universal features (edges, textures, word frequencies)
- **Middle layers:** Domain-general patterns (shapes, phrases, syntax)
- **Later layers:** Task-specific features (faces, sentiment, stock signals)

---

## 2. Core Strategies

### Feature Extraction (Freeze Base)
```python
import torch
from torchvision import models

# Load pre-trained ResNet (trained on ImageNet: 14M images, 1000 classes)
base = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

# Freeze ALL base layers
for param in base.parameters():
    param.requires_grad = False

# Replace final classifier for your task
base.fc = torch.nn.Sequential(
    torch.nn.Linear(2048, 256),
    torch.nn.ReLU(),
    torch.nn.Dropout(0.3),
    torch.nn.Linear(256, num_classes),
)
# Only the new head trains
```

### Fine-Tuning (Unfreeze Gradually)
```python
# Phase 1: Train head only (5 epochs, lr=1e-3)
optimizer = torch.optim.Adam(base.fc.parameters(), lr=1e-3)
train(model, optimizer, epochs=5)

# Phase 2: Unfreeze top layers (10 epochs, lr=1e-5)
for param in base.layer4.parameters():
    param.requires_grad = True
optimizer = torch.optim.Adam([
    {"params": base.layer4.parameters(), "lr": 1e-5},  # Low LR for pre-trained
    {"params": base.fc.parameters(), "lr": 1e-4},       # Higher LR for new head
], lr=1e-5)
train(model, optimizer, epochs=10)
```

### Full Fine-Tuning
```python
# Unfreeze everything — only when you have large dataset (>50K samples)
for param in base.parameters():
    param.requires_grad = True

optimizer = torch.optim.Adam(base.parameters(), lr=1e-5)  # Very low LR!
train(model, optimizer, epochs=20)
```

---

## 3. When to Use Which Strategy

| Scenario | Strategy | Reason |
|----------|----------|--------|
| Small dataset (<1K), similar domain | Feature extraction | Avoid overfitting |
| Small dataset, different domain | Feature extraction + last 2 layers | Adapt top features |
| Medium dataset (1K-50K), similar domain | Fine-tune top layers | Best balance |
| Large dataset (>50K) | Full fine-tuning | Enough data to adapt everything |
| Tiny dataset (<100) | Feature extraction only | High overfit risk |

---

## 4. Transfer Learning for NLP

### BERT for Sentiment (HuggingFace)
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments

# Load pre-trained BERT
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=3,  # positive, neutral, negative
)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Fine-tune on financial data
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,     # Low LR for fine-tuning
    warmup_steps=500,       # Gradual LR warmup
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)
trainer.train()
```

### Domain-Specific Pre-training (Continue Pre-training)
```python
from transformers import AutoModelForMaskedLM, DataCollatorForLanguageModeling

# Continue pre-training BERT on financial text
model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=True, mlm_probability=0.15
)

# Train on financial corpus (earnings calls, annual reports, news)
training_args = TrainingArguments(
    output_dir="./finance-bert",
    num_train_epochs=5,
    per_device_train_batch_size=32,
    learning_rate=5e-5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=financial_corpus,
    data_collator=data_collator,
)
trainer.train()
# Now use "finance-bert" as base for downstream tasks
```

---

## 5. Transfer Learning for Computer Vision

### Keras / TensorFlow
```python
import keras
from keras import layers

# EfficientNet pre-trained on ImageNet
base = keras.applications.EfficientNetV2B0(
    weights="imagenet", include_top=False, input_shape=(224, 224, 3)
)

# Phase 1: Feature extraction
base.trainable = False
model = keras.Sequential([
    base,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation="softmax"),
])
model.compile(optimizer=keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy")
model.fit(train_ds, epochs=10, validation_data=val_ds)

# Phase 2: Fine-tune top 20 layers
base.trainable = True
for layer in base.layers[:-20]:
    layer.trainable = False
model.compile(optimizer=keras.optimizers.Adam(1e-5), loss="sparse_categorical_crossentropy")
model.fit(train_ds, epochs=10, validation_data=val_ds)
```

### PyTorch
```python
import torchvision.models as models
import torch.nn as nn

# Vision Transformer (ViT)
model = models.vit_b_16(weights=models.ViT_B_16_Weights.IMAGENET1K_V1)

# Replace classification head
model.heads = nn.Sequential(
    nn.Linear(768, 256),
    nn.GELU(),
    nn.Dropout(0.3),
    nn.Linear(256, num_classes),
)

# Freeze all except head
for name, param in model.named_parameters():
    if "heads" not in name:
        param.requires_grad = False
```

---

## 6. Transfer Learning for Time Series (Financial)

```python
# Pre-train on general stock data, fine-tune on specific sector
import torch.nn as nn

class TimeSeriesTransfer(nn.Module):
    def __init__(self, pretrained_encoder):
        super().__init__()
        self.encoder = pretrained_encoder  # Pre-trained on 500 stocks
        # Freeze encoder
        for param in self.encoder.parameters():
            param.requires_grad = False
        # New head for specific task
        self.head = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        features = self.encoder(x)  # Learned stock patterns
        return self.head(features)  # Predict specific stock

# Pre-trained encoder: LSTM trained on 500 NSE stocks, 5 years
# Fine-tune head on: RELIANCE last 1 year → predicts next-day direction
```

---

## 7. Best Practices

1. **Lower learning rate for pre-trained layers** — 10-100x smaller than new layers
2. **Warmup schedule** — Start with very low LR, ramp up over 500-1000 steps
3. **Freeze, then unfreeze gradually** — Bottom → top, not all at once
4. **Data augmentation** — Especially with small datasets to prevent overfitting
5. **Use discriminative LR** — Different LR per layer group (lower LR for earlier layers)
6. **Match preprocessing** — Use same normalization as source model training
7. **Monitor validation loss** — Overfitting starts fast with small datasets
8. **Choose closest source domain** — FinBERT > BERT for financial tasks

---

## 8. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Too high learning rate | Pre-trained weights destroyed ("catastrophic forgetting") |
| Wrong input preprocessing | Must match source model (ImageNet mean/std for vision) |
| Unfreezing too early | Train head first, THEN unfreeze gradually |
| Expecting miracles with tiny data | Feature extraction only; don't fine-tune with < 100 samples |
| Ignoring domain gap | The farther source→target, the more layers to fine-tune |
| Not using warmup | Large initial gradients damage pre-trained features |

---

## 9. Domain Adaptation vs Transfer Learning

| Aspect | Transfer Learning | Domain Adaptation |
|--------|-------------------|-------------------|
| Definition | Reuse model for new task | Adapt model to distribution shift |
| Example | ImageNet → medical images | English NER → Hindi NER |
| Labels needed | Some labeled target data | Can be unsupervised |
| Techniques | Fine-tuning, feature extraction | Adversarial training, MMD |
| When to use | Different task, similar domain | Same task, different domain |

---

## 10. Transfer Learning for NLP

### Pre-trained Language Models
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# BERT → Financial sentiment (transfer from general → domain)
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

# Already fine-tuned on financial text — one-step transfer!
inputs = tokenizer("RELIANCE Q3 earnings beat expectations by 15%", return_tensors="pt")
outputs = model(**inputs)
# logits: [positive, negative, neutral]
```

### Multi-Stage Transfer
```
General LLM (GPT/LLaMA) → Domain Pre-training (financial corpus)
    → Task Fine-tuning (sentiment classification)
    → Adapter Tuning (SEBI compliance generation)
```

**Key insight:** Each stage narrows the domain. Start broad, end specific.

---

## 11. Transfer Learning for Time Series (Financial)

```python
import torch
import torch.nn as nn

class FinancialTransferModel(nn.Module):
    """Transfer general time series model to NSE stock prediction."""
    
    def __init__(self, pretrained_encoder, num_stocks=374):
        super().__init__()
        self.encoder = pretrained_encoder  # Pre-trained on general time series
        
        # Freeze encoder (feature extraction)
        for param in self.encoder.parameters():
            param.requires_grad = False
        
        # New financial prediction head
        self.financial_head = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Linear(64, 3),  # UP, DOWN, NEUTRAL
        )
    
    def forward(self, ohlcv_sequence):
        features = self.encoder(ohlcv_sequence)  # Reuse learned patterns
        return self.financial_head(features)
```

### What Transfers Well in Finance
| Source → Target | Transfer Quality | Why |
|----------------|-----------------|-----|
| S&P 500 → NIFTY50 | ✅ High | Similar market structure, correlated moves |
| Crypto → Equities | ⚠️ Medium | Different volatility, similar technical patterns |
| Weather → Stock returns | ❌ Low | No meaningful feature overlap |
| NLP sentiment → Financial NLP | ✅ High | Language patterns transfer, domain vocab differs |
| Image classification → Chart patterns | ✅ High | Visual pattern recognition transfers well |

---

## 12. Advanced: Multi-Task Transfer Learning

```python
# Shared encoder, multiple task-specific heads
class MultiTaskFinancialModel(nn.Module):
    def __init__(self, shared_encoder):
        super().__init__()
        self.encoder = shared_encoder  # Shared backbone
        
        # Task 1: Direction prediction
        self.direction_head = nn.Linear(512, 3)
        # Task 2: Volatility regime
        self.volatility_head = nn.Linear(512, 4)
        # Task 3: Sector rotation signal
        self.sector_head = nn.Linear(512, 11)
    
    def forward(self, x):
        features = self.encoder(x)
        return {
            "direction": self.direction_head(features),
            "volatility": self.volatility_head(features),
            "sector": self.sector_head(features),
        }
```

**Benefit:** Shared encoder learns richer features from multiple tasks simultaneously. The direction head benefits from volatility signals and vice versa.

---

## 13. Decision Framework: When to Use Transfer Learning

| Scenario | Approach | Expected Improvement |
|----------|----------|---------------------|
| < 100 labeled samples | Feature extraction only (freeze all) | 20-40% vs from scratch |
| 100-10K labeled samples | Fine-tune top layers only | 30-50% improvement |
| 10K-100K samples | Gradual unfreezing | 10-20% improvement |
| > 100K samples | Full fine-tuning (or train from scratch) | 5-10% improvement |
| Same domain, different task | LoRA/Adapter tuning | Cost-efficient, ~95% of full FT |
| Cross-domain transfer | Domain adaptation techniques needed | Variable |

**Rule of thumb:** Transfer learning helps most when target data is scarce and source domain is related.
