# NLP (Natural Language Processing): Complete Guide

## 1. What is NLP?

Natural Language Processing is the field of AI that enables machines to understand, interpret, and generate human language. It bridges the gap between unstructured text data and structured, actionable information. Modern NLP is dominated by transformer-based models, but classical techniques remain essential for many production systems.

---

## 2. Core Concepts

### Text Preprocessing Pipeline
```
Raw Text → Tokenization → Lowercasing → Stopword Removal
→ Stemming/Lemmatization → Vectorization → Model Input
```

### Tokenization
```python
# Word-level
"RELIANCE stock rose 5%" → ["RELIANCE", "stock", "rose", "5%"]

# Subword (BPE — used by GPT, BERT)
"unbelievable" → ["un", "believ", "able"]

# Character-level
"stock" → ["s", "t", "o", "c", "k"]
```

```python
# spaCy tokenization
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("RELIANCE stock rose 5% on strong Q3 results")
tokens = [token.text for token in doc]
# ['RELIANCE', 'stock', 'rose', '5', '%', 'on', 'strong', 'Q3', 'results']
```

### Text Representation

| Method | Type | Dimension | Captures |
|--------|------|-----------|----------|
| Bag of Words | Sparse | vocabulary_size | Word frequency |
| TF-IDF | Sparse | vocabulary_size | Term importance |
| Word2Vec | Dense | 100-300 | Semantic similarity |
| GloVe | Dense | 50-300 | Co-occurrence patterns |
| BERT embeddings | Dense | 768-1024 | Contextual meaning |
| Sentence-BERT | Dense | 384-768 | Sentence-level semantics |

```python
# TF-IDF
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(documents)

# Sentence embeddings (modern approach)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["RELIANCE stock is bullish", "TCS earnings beat"])
```

---

## 3. Key NLP Tasks

### Named Entity Recognition (NER)
```python
import spacy
nlp = spacy.load("en_core_web_lg")

doc = nlp("RELIANCE Industries reported ₹23,566 crore profit for Q3 FY25")
for ent in doc.ents:
    print(f"{ent.text}: {ent.label_}")
# RELIANCE Industries: ORG
# ₹23,566 crore: MONEY
# Q3 FY25: DATE
```

### Sentiment Analysis
```python
from transformers import pipeline

sentiment = pipeline("sentiment-analysis",
                     model="ProsusAI/finbert")

results = sentiment([
    "RELIANCE beats expectations with record revenue",
    "TCS warns of client spending slowdown",
    "INFY maintains guidance, steady outlook",
])
# [{'label': 'positive', 'score': 0.94},
#  {'label': 'negative', 'score': 0.87},
#  {'label': 'neutral', 'score': 0.76}]
```

### Text Classification
```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

# Train classifier
clf = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000)),
    ("clf", LogisticRegression(max_iter=1000)),
])
clf.fit(train_texts, train_labels)

# Predict
labels = clf.predict(["Quarterly profit surged 20%"])
# ['earnings_positive']
```

### Topic Modeling
```python
from sklearn.decomposition import LatentDirichletAllocation

lda = LatentDirichletAllocation(n_components=5, random_state=42)
topics = lda.fit_transform(tfidf_matrix)

# Print top words per topic
for idx, topic in enumerate(lda.components_):
    top_words = [feature_names[i] for i in topic.argsort()[-10:]]
    print(f"Topic {idx}: {', '.join(top_words)}")
```

### Text Summarization
```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

long_text = """RELIANCE Industries Limited reported consolidated revenue
of ₹2,35,000 crore for Q3 FY25, marking a 7.5% year-over-year growth..."""

summary = summarizer(long_text, max_length=100, min_length=30)
print(summary[0]["summary_text"])
```

### Question Answering
```python
from transformers import pipeline

qa = pipeline("question-answering", model="deepset/roberta-base-squad2")

context = "RELIANCE reported Q3 FY25 revenue of ₹2,35,000 crore with net profit of ₹23,566 crore."
question = "What was RELIANCE's net profit?"

result = qa(question=question, context=context)
# {'answer': '₹23,566 crore', 'score': 0.95}
```

---

## 4. Transformers & Modern NLP

### BERT (Bidirectional Encoder Representations from Transformers)
```python
from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

inputs = tokenizer("RELIANCE stock is rising", return_tensors="pt")
outputs = model(**inputs)
embeddings = outputs.last_hidden_state  # (1, seq_len, 768)
cls_embedding = outputs.last_hidden_state[:, 0, :]  # Sentence representation
```

### Model Selection Guide

| Model | Size | Best For |
|-------|------|----------|
| BERT-base | 110M | Classification, NER, QA |
| RoBERTa | 125M | Better pre-training, general NLU |
| DistilBERT | 66M | Fast inference, mobile/edge |
| FinBERT | 110M | Financial sentiment analysis |
| XLM-RoBERTa | 550M | Multi-language NLP |
| DeBERTa-v3 | 184M | State-of-art on NLU benchmarks |

---

## 5. spaCy Pipeline

```python
import spacy

nlp = spacy.load("en_core_web_lg")

doc = nlp("Mukesh Ambani announced RELIANCE will invest ₹75,000 crore in green energy")

# Tokenization
tokens = [(t.text, t.pos_, t.dep_) for t in doc]

# Named Entities
entities = [(e.text, e.label_) for e in doc.ents]
# [('Mukesh Ambani', 'PERSON'), ('RELIANCE', 'ORG'), ('₹75,000 crore', 'MONEY')]

# Dependency Parsing
for token in doc:
    print(f"{token.text} --{token.dep_}--> {token.head.text}")

# Noun Chunks
chunks = [chunk.text for chunk in doc.noun_chunks]
# ['Mukesh Ambani', 'RELIANCE', '₹75,000 crore', 'green energy']
```

---

## 6. Financial NLP

### FinBERT for Market Sentiment
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

headlines = [
    "NIFTY hits all-time high amid strong FII inflows",
    "Banking stocks plunge on RBI policy tightening",
    "IT sector flat as dollar index stabilizes",
]

inputs = tokenizer(headlines, padding=True, truncation=True, return_tensors="pt")
outputs = model(**inputs)
probs = torch.softmax(outputs.logits, dim=1)
labels = ["positive", "negative", "neutral"]

for headline, prob in zip(headlines, probs):
    sentiment = labels[prob.argmax()]
    confidence = prob.max().item()
    print(f"{headline[:50]}... → {sentiment} ({confidence:.1%})")
```

### Custom NER for Indian Finance
```python
# Train spaCy NER for Indian financial entities
import spacy
from spacy.training import Example

nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Add custom labels
ner.add_label("STOCK_SYMBOL")
ner.add_label("INDEX")
ner.add_label("FINANCIAL_METRIC")
ner.add_label("INDIAN_CURRENCY")

# Training data
train_data = [
    ("RELIANCE PE ratio is 28.5 on NSE", {
        "entities": [(0, 8, "STOCK_SYMBOL"), (9, 17, "FINANCIAL_METRIC"), (33, 36, "INDEX")]
    }),
]
```

---

## 7. Best Practices

| Practice | Why |
|----------|-----|
| Always preprocess (lowercase, remove noise) | Consistency improves model accuracy |
| Use domain-specific models (FinBERT) | General models miss domain nuances |
| Evaluate on domain-specific test sets | Standard benchmarks don't reflect your data |
| Start with TF-IDF + LogReg baseline | Simple baseline before deep learning |
| Use spaCy for production NLP pipelines | Fast, efficient, GPU-accelerated |
| Fine-tune transformers on your data | Pre-trained models need domain adaptation |
| Handle class imbalance | Financial texts are heavily skewed (neutral > positive > negative) |

---

## 8. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Ignoring domain vocabulary | Financial terms ("short squeeze", "FII") need special handling |
| Using word-level tokenization for transformers | Use model's own tokenizer (BPE/WordPiece) |
| Not handling Hindi/multilingual text | Use XLM-RoBERTa or IndicBERT for Indian markets |
| Over-engineering with transformers | TF-IDF + LogReg beats BERT for many classification tasks |
| Ignoring data quality | Garbage in = garbage out. Clean your training data. |
| Not evaluating per-class metrics | Accuracy masks poor performance on minority classes |

---

## 9. Modern NLP Architecture: Transformers Deep Dive

### Attention Mechanism
```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None):
    """Core attention: Attention(Q,K,V) = softmax(QK^T / √d_k) V"""
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float("-inf"))
    weights = F.softmax(scores, dim=-1)
    return torch.matmul(weights, V), weights
```

### Multi-Head Attention
```python
class MultiHeadAttention(torch.nn.Module):
    def __init__(self, d_model=512, n_heads=8):
        super().__init__()
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.W_q = torch.nn.Linear(d_model, d_model)
        self.W_k = torch.nn.Linear(d_model, d_model)
        self.W_v = torch.nn.Linear(d_model, d_model)
        self.W_o = torch.nn.Linear(d_model, d_model)
    
    def forward(self, x):
        B, T, C = x.shape
        Q = self.W_q(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        out, _ = scaled_dot_product_attention(Q, K, V)
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.W_o(out)
```

---

## 10. NLP for Financial Markets (Indian Context)

### Financial NER with Custom Labels
```python
# Custom NER labels for Indian financial text
FINANCIAL_LABELS = [
    "STOCK_SYMBOL",    # RELIANCE, TCS, INFY
    "INDEX",           # NIFTY50, BANKNIFTY, SENSEX
    "FINANCIAL_METRIC",# PE, EPS, EBITDA, ROE
    "CURRENCY_VALUE",  # ₹2,450 crore, $1.2B
    "REGULATORY_BODY", # SEBI, RBI, NSE, BSE
    "EVENT",           # Q3 earnings, AGM, bonus issue
    "SECTOR",          # IT, Banking, Pharma
]
```

### Topic Modeling for Market Research
```python
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

# Discover hidden themes in analyst reports
vectorizer = CountVectorizer(max_features=5000, stop_words="english")
doc_term = vectorizer.fit_transform(analyst_reports)

lda = LatentDirichletAllocation(n_components=8, random_state=42)
lda.fit(doc_term)

# Topic 0: ["revenue", "growth", "margin", "EBITDA"] → Earnings Analysis
# Topic 1: ["FII", "DII", "inflow", "foreign"] → Flow Analysis
# Topic 2: ["SEBI", "regulation", "compliance", "penalty"] → Regulatory
```

---

## 11. Text Summarization

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

earnings_call = """
Reliance Industries reported consolidated revenue of ₹2.35 lakh crore 
for Q3 FY2025, up 12% YoY. EBITDA margin improved to 17.8%. The Jio 
platform added 8.2 million subscribers during the quarter. Retail business 
saw same-store sales growth of 14%. Management guided for 20% capex 
reduction in FY2026...
"""

summary = summarizer(earnings_call, max_length=80, min_length=30)
# "Reliance reported ₹2.35L cr revenue (+12% YoY) with 17.8% EBITDA margin. 
#  Jio added 8.2M subs. Retail SSG at 14%. Capex to reduce 20% in FY26."
```

---

## 12. NLP Pipeline Architecture

```
┌──────────────────────────────────────────────────────┐
│  Raw Text Input                                      │
│  "RELIANCE breaks above ₹3,000 resistance level"    │
├──────────────────────────────────────────────────────┤
│  Preprocessing (spaCy)                               │
│  Tokenize → Lemmatize → POS Tag → Dependency Parse   │
├──────────────────────────────────────────────────────┤
│  Feature Extraction                                  │
│  TF-IDF, Word2Vec, BERT Embeddings, FinBERT          │
├──────────────────────────────────────────────────────┤
│  Task Layer                                          │
│  NER: STOCK_SYMBOL(RELIANCE), CURRENCY(₹3,000)       │
│  Sentiment: BULLISH (0.87 confidence)                │
│  Classification: TECHNICAL_ANALYSIS                   │
├──────────────────────────────────────────────────────┤
│  Downstream Application                              │
│  Trading Signal → Signal Worker → Order Execution     │
└──────────────────────────────────────────────────────┘
```
