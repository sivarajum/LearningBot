# Transfer Learning: Interview Questions & Answers

## Beginner Level

### Q1: What is transfer learning and why is it important?
**A:** Transfer learning reuses knowledge from a model trained on task A to improve performance on task B. It's important because:

1. **Less data needed** — Fine-tune with 1K samples instead of training from scratch with 1M
2. **Faster training** — Hours instead of weeks (GPT-3 cost $4.6M to train from scratch)
3. **Better performance** — Pre-trained features give a strong starting point
4. **Democratizes ML** — Small teams can build on top of BERT, ResNet, etc.

### Q2: Explain the difference between feature extraction and fine-tuning.
**A:**

| Approach | What Changes | When to Use | Risk |
|----------|-------------|-------------|------|
| **Feature extraction** | Only new head trains; base is frozen | Small dataset (<1K), similar domain | Low (can't overfit base) |
| **Fine-tuning** | Head + some/all base layers train | Medium-large dataset, need adaptation | Higher (catastrophic forgetting) |

```python
# Feature extraction: freeze base
for param in model.base.parameters():
    param.requires_grad = False  # 🔒 Frozen

# Fine-tuning: unfreeze top layers
for param in model.base.layer4.parameters():
    param.requires_grad = True   # 🔓 Trainable
```

### Q3: Why use a lower learning rate when fine-tuning?
**A:** Pre-trained weights encode valuable patterns. A high learning rate destroys them ("catastrophic forgetting").

```python
# BAD: Same LR for everything
optimizer = Adam(model.parameters(), lr=1e-3)  # ❌ Destroys pre-trained features

# GOOD: Discriminative learning rates
optimizer = Adam([
    {"params": model.base.parameters(), "lr": 1e-5},    # Low: preserve features
    {"params": model.head.parameters(), "lr": 1e-3},    # High: learn new task fast
])
```

Rule of thumb: Pre-trained layers get 10-100x smaller LR than new layers.

### Q4: What is domain shift and how does it affect transfer learning?
**A:** Domain shift = difference between source training data and target data.

| Source → Target | Domain Shift | Strategy |
|----------------|-------------|----------|
| ImageNet → dog breeds | Low (both natural images) | Feature extraction works |
| ImageNet → medical X-rays | High (very different images) | Fine-tune more layers |
| BERT (Wikipedia) → FinBERT (finance) | Medium (same language, different vocab) | Continue pre-training + fine-tune |
| English BERT → Hindi NER | High (different language) | Use multilingual base (XLM-R) |

Larger domain shift → more layers need fine-tuning → more data required.

---

## Intermediate Level

### Q5: How do you decide which layers to freeze/unfreeze?
**A:** Gradual unfreezing from top to bottom:

```python
# Step 1: Train only new head (2-3 epochs)
for param in model.parameters():
    param.requires_grad = False
for param in model.head.parameters():
    param.requires_grad = True

# Step 2: Unfreeze last block (5 epochs)
for param in model.layer4.parameters():
    param.requires_grad = True

# Step 3: Unfreeze more if still improving (5 epochs)
for param in model.layer3.parameters():
    param.requires_grad = True

# Monitor: If val_loss increases → stop unfreezing (overfitting)
```

**Decision criteria:**
- **Small data** → Freeze more (only head, maybe last block)
- **Large domain shift** → Unfreeze more (need to adapt representations)
- **Large dataset** → Can safely unfreeze more layers
- **Validation loss going up** → Too much unfreezing, re-freeze

### Q6: Compare transfer learning approaches for NLP: feature extraction vs fine-tuning vs continued pre-training.
**A:**

| Approach | Process | When |
|----------|---------|------|
| **Feature extraction** | Use BERT embeddings as frozen features → train classifier on top | Quick prototyping, very small data |
| **Fine-tuning** | Unfreeze BERT + add task head, train end-to-end with low LR | Most common, medium data |
| **Continued pre-training** | Pre-train BERT further on domain text (MLM), THEN fine-tune | Domain-specific vocabulary (finance, medical, legal) |

```python
# Continued pre-training for finance
# Step 1: MLM on financial corpus (no labels needed)
model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased")
trainer.train(financial_corpus)  # Learns: "EPS", "P/E", "SEBI", etc.
model.save_pretrained("finance-bert")

# Step 2: Fine-tune on labeled task
model = AutoModelForSequenceClassification.from_pretrained("finance-bert", num_labels=3)
trainer.train(labeled_sentiment_data)
```

### Q7: How do you handle class imbalance in transfer learning?
**A:** Transfer learning doesn't solve class imbalance — you still need these techniques:

```python
# 1. Weighted loss function
from sklearn.utils.class_weight import compute_class_weight
weights = compute_class_weight("balanced", classes=[0, 1, 2], y=y_train)
criterion = nn.CrossEntropyLoss(weight=torch.tensor(weights))

# 2. Focal loss (for extreme imbalance)
class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, alpha=0.25):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-ce_loss)
        return (self.alpha * (1 - pt) ** self.gamma * ce_loss).mean()

# 3. Oversampling minority class in DataLoader
from torch.utils.data import WeightedRandomSampler
sampler = WeightedRandomSampler(sample_weights, num_samples=len(dataset))
loader = DataLoader(dataset, sampler=sampler, batch_size=32)
```

---

## Advanced Level

### Q8: Design a transfer learning pipeline for financial document classification.
**A:**

```python
class FinancialDocClassifier:
    def __init__(self):
        # Step 1: Start with domain-adapted model
        self.base_model = "ProsusAI/finbert"  # Already adapted for finance

    def train(self, train_data, val_data):
        model = AutoModelForSequenceClassification.from_pretrained(
            self.base_model, num_labels=5  # earnings, regulatory, M&A, dividend, other
        )

        # Discriminative learning rates
        optimizer = AdamW([
            {"params": model.bert.embeddings.parameters(), "lr": 1e-6},
            {"params": model.bert.encoder.layer[:6].parameters(), "lr": 5e-6},
            {"params": model.bert.encoder.layer[6:].parameters(), "lr": 1e-5},
            {"params": model.classifier.parameters(), "lr": 5e-4},
        ])

        # Warmup + cosine decay
        scheduler = get_cosine_schedule_with_warmup(
            optimizer, num_warmup_steps=500, num_training_steps=total_steps
        )

        # Gradual unfreezing
        for epoch in range(10):
            if epoch < 2:
                freeze_below_layer(model, 10)  # Only top 2 layers + head
            elif epoch < 5:
                freeze_below_layer(model, 6)   # Top 6 layers + head
            else:
                pass  # All unfrozen

        return model
```

### Q9: What is catastrophic forgetting and how do you prevent it?
**A:** Catastrophic forgetting = model loses source knowledge when fine-tuned on target task.

**Prevention techniques:**

| Technique | How It Works |
|-----------|-------------|
| **Low learning rate** | Minimal weight changes to pre-trained layers |
| **Gradual unfreezing** | Unfreeze top layers first, then deeper |
| **EWC (Elastic Weight Consolidation)** | Penalize changes to "important" weights |
| **Learning rate warmup** | Start near zero, ramp up slowly |
| **Replay buffer** | Mix source domain samples into training |
| **Progressive training** | Start with frozen base, slowly increase trainable params |

```python
# EWC: Add penalty for changing important weights
class EWC:
    def __init__(self, model, fisher_matrix, old_params, lambda_=1000):
        self.fisher = fisher_matrix  # Importance of each weight
        self.old_params = old_params
        self.lambda_ = lambda_

    def penalty(self, model):
        loss = 0
        for name, param in model.named_parameters():
            loss += (self.fisher[name] * (param - self.old_params[name]) ** 2).sum()
        return self.lambda_ * loss

# Training with EWC
loss = task_loss + ewc.penalty(model)
```

### Q10: How do you evaluate if transfer learning is actually helping?
**A:** Compare against baselines:

```python
# Baseline 1: Train from scratch
scratch_model = MyModel(pretrained=False)
scratch_acc = train_and_eval(scratch_model)

# Baseline 2: Feature extraction only
frozen_model = MyModel(pretrained=True, freeze_base=True)
frozen_acc = train_and_eval(frozen_model)

# Baseline 3: Fine-tuned
finetuned_model = MyModel(pretrained=True, freeze_base=False)
finetuned_acc = train_and_eval(finetuned_model)

# Compare
# If frozen_acc >> scratch_acc → pre-trained features are useful
# If finetuned_acc >> frozen_acc → fine-tuning adds value
# If scratch_acc ≈ finetuned_acc → transfer learning not helping (domain too different)
```

Also track: training time, convergence speed (epochs to reach X accuracy), and data efficiency (performance vs dataset size curve).

---

## Advanced Level (5 Additional Q&As)

### Q11: How would you apply transfer learning for a financial time series prediction task on NSE data?
**A:** Transfer from general time series → financial domain:

```python
# Step 1: Pre-train encoder on general time series (weather, energy, sales)
pretrained_encoder = TimeSeriesTransformer.from_pretrained("general-ts-encoder")

# Step 2: Add financial prediction head
class NSEPredictor(nn.Module):
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder  # Frozen initially
        self.head = nn.Sequential(
            nn.Linear(512, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 3),  # UP, DOWN, NEUTRAL
        )
    
    def forward(self, ohlcv):
        with torch.no_grad():
            features = self.encoder(ohlcv)  # Reuse temporal patterns
        return self.head(features)

# Step 3: Gradual unfreezing
# Phase 1: Train head only (10 epochs, lr=1e-3)
# Phase 2: Unfreeze last 2 encoder layers (10 epochs, lr=1e-5)
```

Key insight: Temporal patterns (trends, seasonality, mean-reversion) transfer well across domains.

### Q12: Explain multi-task transfer learning and when it outperforms single-task.
**A:** Multi-task trains shared features across multiple objectives simultaneously:

- **Shared encoder** learns richer representations than any single task
- Direction prediction benefits from volatility features, and vice versa
- Acts as implicit regularization — prevents overfitting to any single task
- Works best when tasks are **related but not identical** (complementary signals)

Example: Predicting {direction, volatility regime, sector rotation} simultaneously improves each individual task by 5-15% vs training separately.

### Q13: What is progressive resizing / curriculum transfer learning?
**A:** Train on easier/smaller data first, then gradually increase difficulty:

1. **Vision:** Train on 64×64 images → 128×128 → 256×256 (faster convergence)
2. **NLP:** Train on shorter sequences → longer sequences
3. **Financial:** Train on stable market periods → volatile periods → crisis periods

This combines transfer learning with curriculum learning — the model transfers knowledge from simpler patterns to complex ones.

### Q14: How do you handle negative transfer? When does transfer learning hurt?
**A:** Negative transfer occurs when source knowledge hurts target performance:

**Detection:** Fine-tuned accuracy < training-from-scratch accuracy

**Causes:**
- Source and target domains too different (ImageNet → audio spectrograms)
- Source model overfit to source-specific artifacts
- Feature overlap is misleading (similar features, different meanings)

**Mitigation:**
- Use domain similarity metrics before transferring
- Try feature extraction first (safer than fine-tuning)
- Use selective transfer (transfer only certain layers)
- Apply domain adversarial training (DANN) to learn domain-invariant features

### Q15: Design a transfer learning system for multi-market stock prediction (US → India).
**A:** Architecture:

```
Source: S&P 500 model (5 years data, 500 stocks, trained from scratch)
    ↓ Transfer shared market dynamics encoder
Target: NIFTY 500 model (2 years data, limited labels)
    ↓ Fine-tune with domain adaptation

Challenges:
- Different trading hours, holidays, circuit breaker rules
- Currency effects (USD vs INR)
- Regulatory differences (SEBI vs SEC)
- Market microstructure differences (lot sizes, tick sizes)

Solutions:
1. Normalize features to market-relative (z-score within market)
2. Use domain-invariant features: returns, volatility, volume profile
3. Exclude market-specific features: absolute price, market cap in local currency
4. Apply adversarial domain adaptation (discriminator penalizes market-specific features)
```
