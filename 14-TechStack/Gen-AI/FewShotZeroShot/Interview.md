# Few-Shot & Zero-Shot Learning: Interview Questions

## Beginner Level

### Q1: What is the difference between zero-shot, one-shot, and few-shot learning?
**Answer:**

| Type | Examples Given | Description |
|------|--------------|-------------|
| **Zero-shot** | 0 | Model performs task using only instructions/descriptions, no examples |
| **One-shot** | 1 | Model sees one example per class before classifying |
| **Few-shot** | 2-10 | Model sees a handful of examples per class |

```python
# Zero-shot: just describe the task
prompt_zero = "Classify as positive or negative: 'RELIANCE profit surges 30%'"

# One-shot: provide one example
prompt_one = """
"TCS beats estimates" → positive
"RELIANCE profit surges 30%" →"""

# Few-shot: provide multiple examples
prompt_few = """
"TCS beats estimates" → positive
"Adani stocks crash" → negative
"Market flat" → neutral
"RELIANCE profit surges 30%" →"""
```

---

### Q2: How does HuggingFace zero-shot classification work under the hood?
**Answer:**

It uses a model trained on Natural Language Inference (NLI) — specifically, it converts classification into entailment:

```python
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Under the hood, for each candidate label, it creates:
# Premise: "SEBI bans insider trading at XYZ Corp"
# Hypothesis: "This text is about regulatory."
# → NLI model outputs: entailment=0.85, neutral=0.10, contradiction=0.05
# The entailment score becomes the classification score

result = classifier(
    "SEBI bans insider trading at XYZ Corp",
    candidate_labels=["regulatory", "earnings", "M&A"],
)
print(result["labels"][0])   # "regulatory"
print(result["scores"][0])   # 0.85
```

The model evaluates each label independently, so you can add/remove labels without retraining.

---

### Q3: When should you use few-shot learning vs fine-tuning?
**Answer:**

| Factor | Few-Shot | Fine-Tuning |
|--------|----------|-------------|
| Labeled data | <50 examples | 1000+ examples |
| Task changes frequently | ✅ Just change prompt | ❌ Retrain each time |
| Accuracy requirements | Good (85-90%) | Best (93-97%) |
| Latency | Higher (longer prompt) | Lower (no examples in prompt) |
| Cost | Per-token (more tokens) | Training cost + cheap inference |

**Rule of thumb:** Start with few-shot. If accuracy is insufficient and you have data, fine-tune.

---

### Q4: What is in-context learning (ICL)?
**Answer:**

In-context learning is the ability of LLMs to learn from examples provided in the prompt, without any parameter updates. The model "learns" the task pattern from demonstrations at inference time.

```python
# The model was never trained on stock classification specifically,
# but learns the pattern from the examples in the prompt:
prompt = """
Classify the sentiment:
"TCS beats estimates" → bullish
"Adani stocks crash 20%" → bearish
"Market volume low" → neutral
"NIFTY hits all-time high" → bullish
"RBI hikes rates" →"""
# Model outputs: "bearish" — learned the pattern in-context
```

Key insight: ICL works because LLMs have seen similar patterns during pre-training. They don't actually update weights — they just pattern-match.

---

### Q5: What is SetFit and why is it useful?
**Answer:**

SetFit is a few-shot fine-tuning framework that achieves near full fine-tuning accuracy with only 8-16 examples per class. It works in two stages:

```python
from setfit import SetFitModel, SetFitTrainer

# Stage 1: Contrastive learning on sentence pairs
# Stage 2: Train a classification head on embeddings

model = SetFitModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Only 8 examples total!
train_data = [
    ("RELIANCE surges 15%", "bullish"),
    ("TCS misses estimates", "bearish"),
    ("Market trades flat", "neutral"),
    ("INFY raises guidance", "bullish"),
    ("Adani crashes 20%", "bearish"),
    ("Low volume day", "neutral"),
    ("HDFC merger approved", "bullish"),
    ("SEBI penalty on broker", "bearish"),
]

trainer = SetFitTrainer(model=model, train_dataset=train_data)
trainer.train()

model.predict(["WIPRO announces buyback"])  # ["bullish"]
```

**Advantages:** No prompt engineering needed, fast training (minutes), works offline, competitive accuracy.

---

## Intermediate Level

### Q6: How does demonstration ordering affect few-shot performance?
**Answer:**

Example order can cause 10-30% accuracy swings. LLMs exhibit **recency bias** — they weight the last few examples more heavily.

```python
# Order 1: Last example is "positive"
prompt_v1 = """
"Stock crashes" → negative
"Market flat" → neutral
"Huge profit growth" → positive
"RELIANCE announced results" →"""

# Order 2: Last example is "negative"
prompt_v2 = """
"Huge profit growth" → positive
"Market flat" → neutral
"Stock crashes" → negative
"RELIANCE announced results" →"""

# v1 and v2 may give DIFFERENT answers for the same input!
```

**Mitigations:**
1. Test multiple orderings and use majority vote
2. Shuffle and average across runs
3. Use balanced ordering: alternate positive/negative examples
4. Put the most representative example last

---

### Q7: Explain how prototypical networks work for few-shot learning.
**Answer:**

Prototypical networks learn a metric space where classification is done by computing distances to class **prototypes** (mean embeddings of each class).

```python
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")

# Support set: 3 examples per class
support = {
    "bullish": [
        "Stock surges 20% on strong earnings",
        "Company beats revenue estimates",
        "Analyst upgrades to buy rating",
    ],
    "bearish": [
        "Stock plummets after fraud allegations",
        "Company misses quarterly targets",
        "Analyst downgrades to sell",
    ],
}

# Compute prototype (mean embedding) per class
prototypes = {}
for label, texts in support.items():
    embeddings = encoder.encode(texts)
    prototypes[label] = torch.tensor(embeddings).mean(dim=0)

# Classify query by nearest prototype
query = "INFY raises FY26 guidance significantly"
query_emb = torch.tensor(encoder.encode(query))

distances = {
    label: F.cosine_similarity(query_emb.unsqueeze(0), proto.unsqueeze(0)).item()
    for label, proto in prototypes.items()
}
print(distances)  # {"bullish": 0.72, "bearish": 0.31}
predicted = max(distances, key=distances.get)  # "bullish"
```

---

### Q8: How do you retrieve the best demonstrations for a query?
**Answer:**

Use **kNN retrieval** to find the most similar examples from a pool:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Pool of labeled examples
pool = [
    {"text": "TCS quarterly results beat expectations", "label": "positive"},
    {"text": "SEBI fines broker for violation", "label": "negative"},
    {"text": "Market trades flat on Monday", "label": "neutral"},
    {"text": "INFY raises annual guidance", "label": "positive"},
    {"text": "Adani stocks crash after report", "label": "negative"},
    # ... hundreds more
]

# Pre-compute embeddings
pool_embeddings = model.encode([e["text"] for e in pool])

def get_few_shot_examples(query, k=5, balanced=True):
    query_emb = model.encode(query)
    similarities = np.dot(pool_embeddings, query_emb)

    if balanced:
        # Select top example per class
        by_label = {}
        for idx in np.argsort(similarities)[::-1]:
            label = pool[idx]["label"]
            if label not in by_label:
                by_label[label] = pool[idx]
            if len(by_label) >= k:
                break
        return list(by_label.values())
    else:
        top_k = np.argsort(similarities)[-k:][::-1]
        return [pool[i] for i in top_k]

examples = get_few_shot_examples("RELIANCE announces ₹15 dividend", k=3)
```

---

### Q9: What is Pattern-Exploiting Training (PET)?
**Answer:**

PET combines prompt-based zero/few-shot learning with semi-supervised learning. It converts classification tasks into cloze-style fill-in-the-blank problems:

```python
# Traditional classification:
# Input: "Stock surges 20%"
# Label: "positive"

# PET cloze pattern:
# "Stock surges 20%. Overall, it was [MASK]."
# Model fills: "great" (maps to positive) or "terrible" (maps to negative)

# Multiple patterns for same task:
patterns = [
    "{text}. This is [MASK] news.",          # → "good"/"bad"
    "{text}. The sentiment is [MASK].",      # → "positive"/"negative"
    "The following is [MASK]: {text}",       # → "great"/"terrible"
]

# Verbalizer maps predicted words to labels:
verbalizer = {
    "positive": ["good", "great", "positive", "wonderful"],
    "negative": ["bad", "terrible", "negative", "awful"],
}

# PET algorithm:
# 1. Few-shot: Train small model on each pattern separately
# 2. Annotate: Use ensemble to soft-label unlabeled data
# 3. Final: Train standard classifier on soft-labeled + original data
```

PET achieves strong results with 10-50 examples by leveraging MLM pre-training.

---

### Q10: How do you calibrate zero-shot confidence scores?
**Answer:**

Zero-shot scores are often poorly calibrated (model says 95% confident but is wrong 40% of the time). Calibration improves decision-making.

```python
import numpy as np
from sklearn.calibration import CalibratedClassifierCV

# Problem: raw zero-shot scores
raw_scores = classifier("market data", candidate_labels=["positive", "negative"])
# scores: [0.95, 0.05] — but model is often wrong at 0.95!

# Solution 1: Temperature scaling
def calibrate_temperature(logits, temperature=2.0):
    """Higher temperature → softer probabilities."""
    scaled = logits / temperature
    return np.exp(scaled) / np.exp(scaled).sum()

# Solution 2: Contextual calibration (Zhao et al., 2021)
# Get bias from content-free input
content_free = classifier("N/A", candidate_labels=["positive", "negative"])
bias = np.array(content_free["scores"])

# Subtract bias from actual predictions
actual = classifier("RELIANCE profit surges", candidate_labels=["positive", "negative"])
raw = np.array(actual["scores"])

calibrated = raw / bias
calibrated = calibrated / calibrated.sum()  # Re-normalize
print(calibrated)  # More accurate confidence
```

---

## Advanced Level

### Q11: Design a few-shot financial document classification system for an Indian brokerage.
**Answer:**

```python
from sentence_transformers import SentenceTransformer
from setfit import SetFitModel
import anthropic
import numpy as np
from typing import Literal
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    label: str
    confidence: float
    method: str  # "zero-shot", "few-shot-icl", "setfit"

class FinancialDocClassifier:
    """Multi-strategy classifier: zero-shot → few-shot → fine-tuned fallback."""

    CATEGORIES = ["earnings", "regulatory", "M&A", "dividend", "AGM",
                  "compliance", "corporate_action", "market_update"]

    def __init__(self):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = anthropic.Anthropic()
        self.setfit_model = None
        self.example_pool = self._load_example_pool()
        self.pool_embeddings = self.encoder.encode(
            [e["text"] for e in self.example_pool]
        )

    def classify(self, text: str, min_confidence: float = 0.8) -> ClassificationResult:
        """Cascade: zero-shot → few-shot ICL → SetFit."""
        # Stage 1: Zero-shot (cheapest)
        result = self._zero_shot(text)
        if result.confidence >= min_confidence:
            return result

        # Stage 2: Few-shot ICL (moderate cost)
        examples = self._retrieve_examples(text, k=5)
        result = self._few_shot_icl(text, examples)
        if result.confidence >= min_confidence:
            return result

        # Stage 3: SetFit (most accurate)
        if self.setfit_model:
            return self._setfit_predict(text)

        return result  # Return best effort

    def _zero_shot(self, text: str) -> ClassificationResult:
        from transformers import pipeline
        clf = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        result = clf(text, candidate_labels=self.CATEGORIES)
        return ClassificationResult(
            label=result["labels"][0],
            confidence=result["scores"][0],
            method="zero-shot",
        )

    def _retrieve_examples(self, query: str, k: int = 5) -> list:
        query_emb = self.encoder.encode(query)
        sims = np.dot(self.pool_embeddings, query_emb)
        # Balanced: pick top per category
        by_cat = {}
        for idx in np.argsort(sims)[::-1]:
            cat = self.example_pool[idx]["label"]
            if cat not in by_cat and len(by_cat) < k:
                by_cat[cat] = self.example_pool[idx]
        return list(by_cat.values())

    def _few_shot_icl(self, text: str, examples: list) -> ClassificationResult:
        demo_str = "\n".join(f'"{e["text"]}" → {e["label"]}' for e in examples)
        response = self.client.messages.create(
            model="claude-haiku-4-20250514",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": f"""Classify this financial document. Reply with ONLY the category and confidence (0-1).

Categories: {', '.join(self.CATEGORIES)}

Examples:
{demo_str}

Document: "{text}"
Classification:""",
            }],
        )
        parts = response.content[0].text.strip().split()
        return ClassificationResult(
            label=parts[0], confidence=float(parts[1]) if len(parts) > 1 else 0.85,
            method="few-shot-icl",
        )
```

---

### Q12: How do you handle class imbalance in few-shot settings?
**Answer:**

Class imbalance is even more problematic in few-shot — one extra example of a class can shift predictions significantly.

```python
# Problem: 5 "positive" examples but only 1 "negative"
# → Model is biased toward "positive"

# Solution 1: Balanced sampling (equal examples per class)
def balanced_few_shot_prompt(pool, k_per_class=2):
    by_label = {}
    for ex in pool:
        by_label.setdefault(ex["label"], []).append(ex)

    selected = []
    for label, examples in by_label.items():
        selected.extend(examples[:k_per_class])
    return selected

# Solution 2: Class-conditional calibration
def calibrated_prediction(scores, class_prior):
    """Adjust scores by inverse class frequency."""
    adjusted = {label: score / class_prior.get(label, 1.0)
                for label, score in scores.items()}
    total = sum(adjusted.values())
    return {k: v / total for k, v in adjusted.items()}

# Solution 3: Augment minority class examples
def augment_minority(examples, target_count=5):
    """Paraphrase minority class examples using LLM."""
    minority = [e for e in examples if e["label"] == "negative"]
    if len(minority) >= target_count:
        return examples

    for ex in minority[:target_count - len(minority)]:
        paraphrase = llm_paraphrase(ex["text"])
        examples.append({"text": paraphrase, "label": "negative"})
    return examples
```

---

### Q13: Compare Meta-Learning approaches (MAML, Prototypical, Matching) for few-shot.
**Answer:**

| Approach | Core Idea | Pros | Cons |
|----------|-----------|------|------|
| **MAML** | Learn initialization that adapts in few gradient steps | Task-agnostic, flexible | Expensive (second-order gradients), unstable |
| **Prototypical** | Classify by distance to class prototype (mean embedding) | Simple, fast, scalable | Assumes spherical clusters |
| **Matching Networks** | Attention over support set for each query | Handles complex distributions | Slower at inference, no prototype reuse |
| **Siamese** | Learn similarity function between pairs | Good for verification (same/different) | Doesn't scale to many classes |

```python
# MAML pseudocode — learn a good starting point
for task in meta_train_tasks:
    # Inner loop: adapt to task with few examples
    theta_prime = theta - alpha * grad(loss(theta, task.support))

    # Outer loop: optimize initial theta
    theta = theta - beta * grad(loss(theta_prime, task.query))

# At test time: few gradient steps from theta → good performance
```

For text classification, **Prototypical Networks + pre-trained encoders** are the practical choice — simple, fast, and competitive with MAML without the training complexity.
