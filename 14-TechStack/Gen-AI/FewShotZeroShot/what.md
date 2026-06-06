# Few-Shot & Zero-Shot Learning: Complete Guide

## 1. What are Few-Shot and Zero-Shot Learning?

These are techniques for performing tasks with minimal or no labeled examples, leveraging pre-trained models' ability to generalize.

| Paradigm | Examples Provided | How It Works |
|----------|------------------|--------------|
| **Zero-shot** | 0 examples | Model uses its pre-training knowledge + task description |
| **One-shot** | 1 example per class | Model learns from a single demonstration |
| **Few-shot** | 2-10 examples per class | Model learns from a handful of demonstrations |

**Why it matters:** Labeling data is expensive. In finance, you may have only 5 examples of a rare event (market crash, regulatory action). Few-shot learning lets you build classifiers without thousands of labels.

---

## 2. Zero-Shot Classification

### With LLMs (Prompt-Based)
```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{
        "role": "user",
        "content": """Classify this financial headline into one category:
Categories: earnings, regulatory, M&A, dividend, market

Headline: "SEBI tightens F&O margin requirements for retail traders"

Category:"""
    }],
)
# Output: "regulatory"
```

### With HuggingFace Zero-Shot Pipeline
```python
from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

result = classifier(
    "RELIANCE announces ₹15 per share dividend",
    candidate_labels=["earnings", "regulatory", "M&A", "dividend", "market"],
)
# {'labels': ['dividend', 'earnings', ...], 'scores': [0.92, 0.04, ...]}
```

### With Sentence Embeddings
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Define categories by description (no examples needed)
categories = {
    "earnings": "Company quarterly or annual financial results, profit, revenue, EPS",
    "regulatory": "Government regulation, SEBI rules, compliance, policy changes",
    "M&A": "Mergers, acquisitions, takeovers, buyouts, joint ventures",
    "dividend": "Dividend declaration, payout, ex-date, record date",
}

cat_embeddings = {k: model.encode(v) for k, v in categories.items()}

def classify_zero_shot(text):
    text_emb = model.encode(text)
    scores = {k: np.dot(text_emb, v) / (np.linalg.norm(text_emb) * np.linalg.norm(v))
              for k, v in cat_embeddings.items()}
    return max(scores, key=scores.get)

classify_zero_shot("TATA acquires British Steel for $1.5B")
# "M&A"
```

---

## 3. Few-Shot Classification

### With LLMs (In-Context Learning)
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{
        "role": "user",
        "content": """Classify financial headlines as positive, negative, or neutral.

Examples:
"RELIANCE profit surges 30% YoY" → positive
"SEBI bans insider trading at XYZ Corp" → negative
"Market closed flat amid low volumes" → neutral
"TCS misses revenue estimates by 5%" → negative
"NIFTY hits all-time high of 25,000" → positive

Now classify:
"HDFC Bank reports moderate growth in Q3 deposits" →"""
    }],
)
# Output: "neutral"
```

### With SetFit (Few-Shot Fine-Tuning)
```python
from setfit import SetFitModel, SetFitTrainer

# Only 8 examples per class!
train_data = [
    ("RELIANCE profit surges 30%", "positive"),
    ("TCS misses revenue estimates", "negative"),
    ("Market closed flat", "neutral"),
    ("INFY raises guidance for FY26", "positive"),
    ("RBI hikes repo rate by 25bps", "negative"),
    ("Sensex trades in narrow range", "neutral"),
    ("HDFC merger boosts banking index", "positive"),
    ("Adani stocks crash 20%", "negative"),
]

model = SetFitModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
trainer = SetFitTrainer(
    model=model,
    train_dataset=train_data,
    num_iterations=20,        # Contrastive learning iterations
    num_epochs=1,
)
trainer.train()

# Now classify new text
model.predict(["WIPRO declares special dividend of ₹5"])
# ["positive"]
```

### With Prototypical Networks
```python
import torch
import torch.nn.functional as F

class PrototypicalNetwork:
    """Learn class prototypes from few examples, classify by distance."""
    def __init__(self, encoder):
        self.encoder = encoder  # Pre-trained sentence encoder

    def compute_prototypes(self, support_set):
        """Average embedding per class = prototype."""
        prototypes = {}
        for text, label in support_set:
            emb = self.encoder.encode(text)
            prototypes.setdefault(label, []).append(emb)
        return {k: torch.tensor(v).mean(dim=0) for k, v in prototypes.items()}

    def classify(self, query_text, prototypes):
        """Classify by nearest prototype."""
        query_emb = torch.tensor(self.encoder.encode(query_text))
        distances = {label: F.cosine_similarity(query_emb.unsqueeze(0), proto.unsqueeze(0))
                     for label, proto in prototypes.items()}
        return max(distances, key=distances.get)
```

---

## 4. Demonstration Selection Strategies

Choosing the right examples dramatically impacts few-shot performance.

### Similarity-Based Selection
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def select_demonstrations(query, examples, k=5):
    """Select k most similar examples to the query."""
    query_emb = model.encode(query)
    example_embs = model.encode([e["text"] for e in examples])

    similarities = np.dot(example_embs, query_emb)
    top_k = np.argsort(similarities)[-k:][::-1]

    return [examples[i] for i in top_k]
```

### Diversity-Based Selection
```python
def select_diverse_demonstrations(examples, k=5):
    """Select k diverse examples (cover all classes, maximize spread)."""
    embeddings = model.encode([e["text"] for e in examples])
    selected = [0]  # Start with first example

    for _ in range(k - 1):
        # Select example most distant from all selected
        max_min_dist = -1
        best_idx = -1
        for i in range(len(examples)):
            if i in selected:
                continue
            min_dist = min(np.dot(embeddings[i], embeddings[j]) for j in selected)
            if min_dist > max_min_dist:
                max_min_dist = min_dist
                best_idx = i
        selected.append(best_idx)

    return [examples[i] for i in selected]
```

---

## 5. Zero-Shot for NER, Summarization, QA

### Zero-Shot NER
```python
# LLM-based zero-shot NER
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": """Extract entities from this text. Return JSON.
Entity types: STOCK_SYMBOL, AMOUNT, METRIC, DATE, ORGANIZATION

Text: "RELIANCE reported EPS of ₹42.5 for Q3 FY25, beating SEBI expectations"

Entities:"""
    }],
)
# {"entities": [{"text": "RELIANCE", "type": "STOCK_SYMBOL"}, ...]}
```

### Zero-Shot Summarization
```python
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
summary = summarizer(long_text, max_length=130, min_length=30)
# No examples needed — model was pre-trained on CNN/DailyMail
```

---

## 6. Best Practices

1. **Start with zero-shot** — Test if the pre-trained model already knows the task
2. **Add examples only if needed** — More examples help, but diminishing returns after 5-10
3. **Order matters** — Recency bias: models weight later examples more heavily
4. **Diversify examples** — Cover all classes and edge cases in demonstrations
5. **Use similar examples** — Retrieve demonstrations similar to the query (kNN retrieval)
6. **Format consistency** — Keep input/output format identical across examples
7. **Calibrate confidence** — Zero-shot confidence scores are often miscalibrated
8. **Evaluate properly** — Don't evaluate on the same examples used as demonstrations

---

## 7. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Wrong example format confuses model | Be consistent: same delimiter, same label format |
| Too many examples → context overflow | 3-5 examples is usually enough; use retrieval for selection |
| Label leakage in demonstrations | Never include test examples in few-shot demonstrations |
| Zero-shot for rare concepts | Model can't classify what it hasn't seen; switch to few-shot |
| Recency bias (last example dominates) | Shuffle example order; test multiple orderings |
| Expecting fine-tuned accuracy | Few-shot ≠ fine-tuned; if you need >95% accuracy, fine-tune |

---

## 8. Few-Shot vs Fine-Tuning vs Zero-Shot

| Aspect | Zero-Shot | Few-Shot (In-Context) | Few-Shot (SetFit) | Full Fine-Tuning |
|--------|-----------|----------------------|-------------------|-----------------|
| Labeled data needed | 0 | 3-10 | 8-50 per class | 1000+ |
| Training required | No | No | Minutes | Hours |
| Accuracy | Good (80-85%) | Better (85-90%) | Very good (88-93%) | Best (93-97%) |
| Cost | Inference only | Inference (higher token count) | Small training + fast inference | Large training + fast inference |
| Flexibility | Change task via prompt | Change task via examples | Retrain for new task | Retrain for new task |
| Best for | Prototyping, dynamic tasks | When examples available | Small labeled datasets | Production accuracy |

---

## 9. Dynamic Few-Shot with Retrieval

Instead of static examples, retrieve the most relevant demonstrations for each query:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Pre-compute embeddings for demonstration bank
demo_bank = [
    {"text": "RELIANCE Q3 earnings crush estimates", "label": "BULLISH"},
    {"text": "FII selling intensifies for 5th straight session", "label": "BEARISH"},
    {"text": "RBI keeps repo rate unchanged at 6.5%", "label": "NEUTRAL"},
    # ... 100+ demonstrations
]

model = SentenceTransformer("all-MiniLM-L6-v2")
demo_embeddings = model.encode([d["text"] for d in demo_bank])

def get_dynamic_examples(query: str, k: int = 3):
    query_emb = model.encode([query])
    similarities = np.dot(demo_embeddings, query_emb.T).flatten()
    top_k = np.argsort(similarities)[-k:][::-1]
    return [demo_bank[i] for i in top_k]

# Each query gets its OWN best examples
query = "NIFTY IT index falls 3% on weak guidance"
examples = get_dynamic_examples(query)  # Returns most similar financial headlines
```

**Why dynamic > static:** Relevant examples give better accuracy than random ones. 20-30% accuracy improvement for diverse task distributions.

---

## 10. SetFit: Few-Shot without Prompts

SetFit trains a sentence transformer on few examples — no LLM needed at inference time.

```python
from setfit import SetFitModel, SetFitTrainer, sample_dataset
from datasets import Dataset

# Just 8 examples per class!
train_data = Dataset.from_dict({
    "text": [
        "Strong Q4 numbers, revenue up 25%",
        "SEBI slaps penalty on promoter for insider trading",
        "Company announces 1:1 bonus share",
        "Management downgrades full year guidance",
        # ... 4 more per class
    ],
    "label": [1, 0, 1, 0, ...],  # 1=bullish, 0=bearish
})

model = SetFitModel.from_pretrained("sentence-transformers/paraphrase-mpnet-base-v2")
trainer = SetFitTrainer(model=model, train_dataset=train_data, num_iterations=20)
trainer.train()

# Inference: no LLM, no tokens, < 10ms per prediction
preds = model.predict(["FII flows turn positive", "Credit downgrade by Moody's"])
```

**Advantages:** No ongoing LLM cost, sub-10ms latency, works offline, ~90% accuracy with 8 examples per class.

---

## 11. Evaluation: Measuring Few-Shot Performance

```python
# Rigorous few-shot evaluation framework
def evaluate_few_shot(llm, task, num_shots_range=[0, 1, 3, 5, 10], n_trials=5):
    """Test how performance scales with number of examples."""
    results = {}
    for k in num_shots_range:
        trial_scores = []
        for trial in range(n_trials):
            # Randomly sample k demonstrations (different each trial)
            demos = random.sample(demo_bank, k) if k > 0 else []
            prompt = build_prompt(demos, task)
            
            scores = []
            for test_case in test_set:
                pred = llm.predict(prompt + test_case["text"])
                scores.append(pred == test_case["label"])
            
            trial_scores.append(np.mean(scores))
        
        results[f"{k}-shot"] = {
            "mean_accuracy": np.mean(trial_scores),
            "std": np.std(trial_scores),
        }
    return results
# Typical output: 0-shot: 78%, 1-shot: 83%, 3-shot: 87%, 5-shot: 89%
```

**Key insight:** Few-shot accuracy saturates after 5-10 examples. More examples = more tokens = more cost, but diminishing accuracy returns.
