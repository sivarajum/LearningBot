# NLP: Interview Questions & Answers

## Beginner Level

### Q1: What is NLP and what are its main applications?
**A:** NLP enables machines to process human language. Key applications:
- **Sentiment Analysis** — Classify text as positive/negative/neutral (financial headlines)
- **Named Entity Recognition** — Extract entities: companies, people, amounts
- **Text Classification** — Categorize documents (spam, topic, intent)
- **Machine Translation** — Google Translate, DeepL
- **Question Answering** — Extract answers from documents
- **Summarization** — Condense long documents
- **Chatbots/Assistants** — Conversational AI (GPT, Claude)

### Q2: Explain tokenization and why subword tokenization is preferred.
**A:** Tokenization splits text into units (tokens) for model processing.

**Word-level:** "unbelievable" → ["unbelievable"] — fails on unseen words (OOV problem)
**Character-level:** "stock" → ["s","t","o","c","k"] — too granular, loses meaning
**Subword (BPE):** "unbelievable" → ["un","believ","able"] — best of both worlds

Subword tokenization (BPE, WordPiece, SentencePiece):
- Handles unseen words by breaking them into known subwords
- Fixed vocabulary size (30K-50K tokens)
- Used by all modern models (GPT, BERT, Claude)

```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("bert-base-uncased")
tok.tokenize("RELIANCE quarterly results")
# ['rel', '##iance', 'quarterly', 'results']
```

### Q3: What is TF-IDF and when should you use it?
**A:** TF-IDF (Term Frequency-Inverse Document Frequency) measures word importance.
- **TF:** How often a word appears in a document
- **IDF:** How rare a word is across all documents
- **TF-IDF = TF × IDF:** High for words frequent in one doc but rare overall

```python
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(max_features=5000)
X = tfidf.fit_transform(["RELIANCE profit rose", "TCS revenue fell"])
```

Use TF-IDF when: you need a simple baseline, explainable features, or computational efficiency. It's surprisingly competitive for text classification even against deep learning.

### Q4: What is Named Entity Recognition (NER)?
**A:** NER identifies and classifies named entities in text:

| Entity Type | Examples |
|-------------|---------|
| PERSON | Mukesh Ambani, Sundar Pichai |
| ORG | RELIANCE, TCS, SEBI |
| MONEY | ₹23,566 crore, $1 billion |
| DATE | Q3 FY25, January 2025 |
| GPE (Location) | India, Mumbai |

```python
import spacy
nlp = spacy.load("en_core_web_lg")
doc = nlp("SEBI fined RELIANCE ₹25 crore in Mumbai")
for ent in doc.ents:
    print(f"{ent.text} → {ent.label_}")
# SEBI → ORG, RELIANCE → ORG, ₹25 crore → MONEY, Mumbai → GPE
```

### Q5: Explain the difference between stemming and lemmatization.
**A:**
- **Stemming:** Crude suffix stripping. Fast but imprecise.
  - "running" → "run", "better" → "better" (misses it), "studies" → "studi"
- **Lemmatization:** Dictionary-based, returns valid words. Slower but accurate.
  - "running" → "run", "better" → "good", "studies" → "study"

```python
# Stemming (Porter)
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
stemmer.stem("running")  # "run"

# Lemmatization (spaCy)
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("The stocks were rising quickly")
[token.lemma_ for token in doc]  # ['the', 'stock', 'be', 'rise', 'quickly']
```

Use lemmatization for NLP tasks. Use stemming only for search indexing where speed matters.

---

## Intermediate Level

### Q6: How do transformers handle NLP differently than RNNs?
**A:**

| Aspect | RNNs (LSTM/GRU) | Transformers |
|--------|-----------------|-------------|
| Processing | Sequential (left to right) | Parallel (all tokens at once) |
| Long-range deps | Degrades over distance | Self-attention handles any distance |
| Training speed | Slow (sequential) | Fast (parallelizable, GPU-friendly) |
| Key mechanism | Hidden state recurrence | Self-attention + positional encoding |
| Context | Unidirectional or bidirectional | Bidirectional (BERT) or causal (GPT) |

Self-attention computes relationships between ALL token pairs simultaneously:
```
"The bank by the river" — "bank" attends to "river" → financial institution? No, riverbank.
"The bank approved the loan" — "bank" attends to "loan" → financial institution.
```

This attention mechanism is why transformers dominate modern NLP.

### Q7: Compare BERT vs GPT architecture for NLP tasks.
**A:**

| Feature | BERT (Encoder) | GPT (Decoder) |
|---------|---------------|---------------|
| Architecture | Encoder only | Decoder only |
| Attention | Bidirectional (sees full context) | Causal (left-to-right only) |
| Pre-training | Masked Language Model (fill blanks) | Next token prediction |
| Best for | Classification, NER, QA, embeddings | Text generation, chat, summarization |
| Fine-tuning | Add task head on [CLS] token | Few-shot prompting or fine-tune |

```python
# BERT: Classification (fine-tune for sentiment)
from transformers import BertForSequenceClassification
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)

# GPT: Generation (prompt-based)
from transformers import GPT2LMHeadModel
model = GPT2LMHeadModel.from_pretrained("gpt2")
```

**Rule of thumb:** Use BERT-family for understanding tasks (classify, extract). Use GPT-family for generation tasks (write, summarize, chat).

### Q8: How do you handle multi-language NLP for Indian markets?
**A:** Indian markets have English + Hindi + regional language content:

```python
# Option 1: XLM-RoBERTa (100+ languages)
from transformers import AutoModel
model = AutoModel.from_pretrained("xlm-roberta-large")

# Option 2: IndicBERT (Indian languages focused)
model = AutoModel.from_pretrained("ai4bharat/IndicBERTv2-MLM-Sam-TLM")

# Option 3: Language detection + routing
from langdetect import detect
lang = detect("रिलायंस के शेयर बढ़े")  # "hi"
if lang == "hi":
    model = hindi_sentiment_model
else:
    model = english_sentiment_model
```

### Q9: How do you evaluate NLP models beyond accuracy?
**A:**

| Metric | Task | Formula |
|--------|------|---------|
| **Precision** | Classification, NER | TP / (TP + FP) — how many predicted positives are correct |
| **Recall** | Classification, NER | TP / (TP + FN) — how many actual positives are found |
| **F1 Score** | Classification, NER | 2 × (P × R) / (P + R) — harmonic mean |
| **BLEU** | Translation, Generation | N-gram overlap with reference |
| **ROUGE** | Summarization | N-gram recall vs reference summary |
| **Exact Match** | QA | Binary — did it match exactly? |
| **Perplexity** | Language Model | How surprised the model is — lower is better |

```python
from sklearn.metrics import classification_report
print(classification_report(y_true, y_pred, target_names=["negative", "neutral", "positive"]))
```

For financial NLP: **F1-score per class** matters more than accuracy because classes are imbalanced (most headlines are neutral).

---

## Advanced Level

### Q10: Design a financial news NLP pipeline for trading signal generation.
**A:**

```python
class FinancialNewsPipeline:
    def __init__(self):
        self.ner = spacy.load("en_core_web_lg")
        self.sentiment = pipeline("sentiment-analysis", model="ProsusAI/finbert")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def process(self, headline: str) -> dict:
        # Step 1: NER — extract entities
        doc = self.ner(headline)
        entities = {ent.label_: ent.text for ent in doc.ents}
        symbols = self.map_entities_to_symbols(entities)

        # Step 2: Sentiment analysis
        sent = self.sentiment(headline)[0]

        # Step 3: Relevance scoring
        embedding = self.embedder.encode(headline)
        relevance = self.score_market_relevance(embedding)

        # Step 4: Signal generation
        signal = None
        if sent["score"] > 0.8 and relevance > 0.7:
            if sent["label"] == "positive":
                signal = "BULLISH"
            elif sent["label"] == "negative":
                signal = "BEARISH"

        return {
            "symbols": symbols,
            "sentiment": sent["label"],
            "confidence": sent["score"],
            "relevance": relevance,
            "signal": signal,
        }
```

### Q11: How do you fine-tune BERT for domain-specific NER?
**A:**

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
from datasets import Dataset

# Custom labels for Indian finance
labels = ["O", "B-STOCK", "I-STOCK", "B-INDEX", "I-INDEX",
          "B-AMOUNT", "I-AMOUNT", "B-METRIC", "I-METRIC"]

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
model = AutoModelForTokenClassification.from_pretrained(
    "bert-base-cased", num_labels=len(labels)
)

# Training data (BIO format)
# "RELIANCE P/E is 28.5" → ["B-STOCK", "B-METRIC", "O", "B-AMOUNT"]

training_args = TrainingArguments(
    output_dir="./ner-finance",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
)
trainer.train()
```

### Q12: How do you handle noisy, real-world financial text (tweets, forum posts)?
**A:**

```python
import re

def preprocess_financial_text(text: str) -> str:
    # 1. Normalize stock symbols: $RELIANCE, #RELIANCE → RELIANCE
    text = re.sub(r'[$#]([A-Z]{2,})', r'\1', text)

    # 2. Normalize numbers: 23,566 → 23566, 2.5K → 2500
    text = re.sub(r'(\d+),(\d{3})', r'\1\2', text)
    text = re.sub(r'(\d+\.?\d*)K\b', lambda m: str(float(m.group(1)) * 1000), text)
    text = re.sub(r'(\d+\.?\d*)Cr\b', lambda m: str(float(m.group(1)) * 10000000), text)

    # 3. Handle emojis (useful for sentiment)
    emoji_sentiment = {"🚀": "bullish", "📉": "bearish", "🔥": "positive"}

    # 4. Remove URLs but keep domain
    text = re.sub(r'https?://\S+', '', text)

    # 5. Handle abbreviations: PE → P/E, EPS → Earnings Per Share
    abbreviations = {"PE": "P/E ratio", "EPS": "earnings per share", "YoY": "year over year"}
    for abbr, full in abbreviations.items():
        text = re.sub(rf'\b{abbr}\b', full, text)

    return text.strip()
```

Key strategies:
- **Don't over-clean** — Capitalization and punctuation carry signal
- **Domain vocabulary** — Add financial terms to stopword exceptions
- **Emoji analysis** — Emojis are strong sentiment signals in social media
- **Noise-tolerant models** — RoBERTa handles noisy text better than BERT

---

## Advanced Level (5 Additional Q&As)

### Q13: How do you build a financial Named Entity Recognition (NER) system?
**A:**

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# 1. Use pre-trained financial NER
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
ner_pipe = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# 2. Custom financial entities (fine-tuned)
# Labels: STOCK, AMOUNT, METRIC, DATE, SECTOR, REGULATOR
financial_text = "SEBI approved RELIANCE FPO worth ₹23,566 Cr on March 15, targeting Energy sector"
entities = ner_pipe(financial_text)
# → [{"entity": "ORG", "word": "SEBI"}, {"entity": "ORG", "word": "RELIANCE"}, ...]

# 3. Custom training with domain-specific labels
from datasets import Dataset
train_data = Dataset.from_dict({
    "tokens": [["RELIANCE", "reports", "Q3", "EPS", "of", "₹45.2"]],
    "ner_tags": [[1, 0, 3, 4, 0, 2]],  # 0=O, 1=STOCK, 2=AMOUNT, 3=DATE, 4=METRIC
})
```

**Financial NER challenges:**
- Ambiguous entities: "NIFTY" = index name vs colloquial term
- Nested entities: "NIFTY Bank" contains "NIFTY" and is itself an entity
- Numerical context: "23,566" = price? volume? market cap? Depends on context

### Q14: How do you implement topic modeling for financial news clustering?
**A:**

```python
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# 1. Domain-specific embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. BERTopic for clustering financial news
topic_model = BERTopic(
    embedding_model=embedding_model,
    nr_topics=20,
    min_topic_size=10,
    language="english",
)

news_articles = [
    "RBI holds repo rate at 6.5%, flags inflation concerns",
    "SEBI introduces new margin rules for F&O trading",
    "NIFTY IT index rallies 3% on strong TCS earnings",
    # ... 10,000 articles
]

topics, probs = topic_model.fit_transform(news_articles)

# 3. Get topic labels
topic_info = topic_model.get_topic_info()
# Topic 0: ["rbi", "rate", "inflation", "monetary"] → Monetary Policy
# Topic 1: ["sebi", "margin", "regulation", "compliance"] → Regulatory
# Topic 2: ["earnings", "quarterly", "revenue", "profit"] → Earnings

# 4. Track topic trends over time
topics_over_time = topic_model.topics_over_time(news_articles, timestamps)
```

**Applications:**
- Real-time news clustering for sector-wise sentiment
- Identifying emerging themes before they impact markets
- Regulatory change detection (SEBI circular tracking)

### Q15: Explain the Transformer architecture internals — self-attention, positional encoding, and why they matter for financial text.
**A:**

```python
import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    """Core mechanism — each token attends to all other tokens."""
    def __init__(self, d_model=512, n_heads=8):
        super().__init__()
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        B, T, C = x.shape
        Q = self.W_q(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        attn = torch.softmax(scores, dim=-1)
        return torch.matmul(attn, V)  # Weighted sum of values

# Why this matters for financial text:
# "RELIANCE stock price fell after SEBI investigation"
# Attention allows "fell" to directly attend to "RELIANCE" and "investigation"
# capturing the causal relationship across the sentence
```

**Positional encoding** — Transformers have no notion of order, so position must be injected:
- Sinusoidal (original): Fixed math formula, generalizes to any length
- Learned (BERT): Trainable vectors, limited to max training length
- RoPE (modern LLMs): Rotary position embedding, better long-range
- ALiBi (efficient): Linear bias, no additional parameters

**For financial NLP:** Position matters because "NIFTY rose then fell" ≠ "NIFTY fell then rose" — same tokens, opposite meanings.

### Q16: How do you build a production NLP pipeline for real-time financial sentiment?
**A:**

```python
# Production architecture for processing 10K+ articles/day
class FinancialNLPPipeline:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0)
        self.sentiment = pipeline("sentiment-analysis", model="ProsusAI/finbert", device=0)
        self.ner = pipeline("ner", model="dslim/bert-base-NER", device=0, aggregation_strategy="simple")
    
    def process(self, article: str) -> dict:
        # 1. Summarize (reduce token count for downstream)
        if len(article.split()) > 200:
            summary = self.summarizer(article, max_length=100, min_length=30)[0]["summary_text"]
        else:
            summary = article
        
        # 2. Sentiment classification
        sent = self.sentiment(summary)[0]
        
        # 3. Entity extraction
        entities = self.ner(summary)
        stocks = [e["word"] for e in entities if e["entity_group"] == "ORG"]
        
        # 4. Signal generation
        return {
            "summary": summary,
            "sentiment": sent["label"],  # positive/negative/neutral
            "confidence": sent["score"],
            "stocks_mentioned": stocks,
            "signal": "BUY" if sent["label"] == "positive" and sent["score"] > 0.85 else "HOLD",
        }

# Batch processing with async
import asyncio
async def process_batch(articles: list[str]) -> list[dict]:
    pipeline = FinancialNLPPipeline()
    return [pipeline.process(a) for a in articles]
```

### Q17: What are the key differences between BERT, GPT, and T5 architectures for NLP tasks?
**A:**

| Feature | BERT | GPT | T5 |
|---------|------|-----|-----|
| **Architecture** | Encoder only | Decoder only | Encoder-Decoder |
| **Pre-training** | MLM + NSP | Causal LM (next token) | Span corruption |
| **Bidirectional** | ✅ Full | ❌ Left-to-right only | ✅ Encoder bidirectional |
| **Best for** | Classification, NER, QA | Generation, chat, code | Any text-to-text task |
| **Financial use** | Sentiment (FinBERT) | Analysis reports | Summarization, translation |
| **Context** | 512 tokens (original) | 128K+ (GPT-4) | 512-4096 tokens |
| **Fine-tuning** | Add classification head | Prompt tuning / LoRA | Prefix tuning |

**When to choose:**
- **BERT/RoBERTa**: Classification, sentiment, NER — fast inference, small model
- **GPT-4/Claude**: Complex reasoning, report generation — expensive, high quality
- **T5/FLAN-T5**: Versatile, good for instruction-following on moderate budgets
