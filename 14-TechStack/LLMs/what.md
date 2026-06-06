# Large Language Models (LLMs): Comprehensive Guide

## Overview

Large Language Models (LLMs) are advanced AI systems trained on vast amounts of text data to understand and generate human-like text. They represent a breakthrough in natural language processing, enabling applications from conversational AI to code generation, content creation, and complex reasoning tasks.

## Core Concepts

### Transformer Architecture

The foundation of modern LLMs is the Transformer architecture, introduced in the 2017 paper "Attention is All You Need" by Vaswani et al.

```python
import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        # Q, K, V: [batch_size, num_heads, seq_len, d_k]
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attention_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)

        return output, attention_weights

    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)

        # Linear transformations and reshape
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # Attention
        attn_output, attn_weights = self.scaled_dot_product_attention(Q, K, V, mask)

        # Concatenate heads and put through final linear layer
        attn_output = attn_output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )

        output = self.W_o(attn_output)
        return output, attn_weights

class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )

        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Multi-head attention with residual connection
        attn_output, _ = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x
```

### Key LLM Architectures

#### GPT (Generative Pre-trained Transformer)

```python
class GPT(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, max_seq_len):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_len, d_model)

        self.layers = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_model * 4)
            for _ in range(num_layers)
        ])

        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)

    def forward(self, input_ids):
        seq_len = input_ids.size(1)
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)

        # Token + positional embeddings
        x = self.token_embedding(input_ids) + self.position_embedding(positions)

        # Create causal mask for autoregressive generation
        causal_mask = torch.tril(torch.ones(seq_len, seq_len)).bool()
        causal_mask = causal_mask.to(input_ids.device)

        # Transformer layers
        for layer in self.layers:
            x = layer(x, causal_mask)

        x = self.ln_f(x)
        logits = self.head(x)

        return logits

    def generate(self, input_ids, max_new_tokens, temperature=1.0):
        for _ in range(max_new_tokens):
            # Get logits for the next token
            logits = self(input_ids)[:, -1, :]

            # Apply temperature
            logits = logits / temperature

            # Sample from distribution
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            # Append to sequence
            input_ids = torch.cat([input_ids, next_token], dim=1)

        return input_ids
```

#### BERT (Bidirectional Encoder Representations from Transformers)

```python
class BERT(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, num_layers, max_seq_len):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(max_seq_len, d_model)
        self.segment_embedding = nn.Embedding(2, d_model)  # For next sentence prediction

        self.layers = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_model * 4)
            for _ in range(num_layers)
        ])

        self.ln_f = nn.LayerNorm(d_model)

        # Task-specific heads
        self.mlm_head = nn.Linear(d_model, vocab_size)  # Masked language modeling
        self.nsp_head = nn.Linear(d_model, 2)  # Next sentence prediction

    def forward(self, input_ids, segment_ids, attention_mask=None):
        seq_len = input_ids.size(1)
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)

        # Embeddings
        x = (self.token_embedding(input_ids) +
             self.position_embedding(positions) +
             self.segment_embedding(segment_ids))

        # Create attention mask
        if attention_mask is not None:
            attention_mask = attention_mask.unsqueeze(1).unsqueeze(2)
            attention_mask = attention_mask.to(dtype=next(self.parameters()).dtype)
            attention_mask = (1.0 - attention_mask) * -10000.0

        # Transformer layers (bidirectional)
        for layer in self.layers:
            x = layer(x, attention_mask)

        x = self.ln_f(x)

        # Get [CLS] token representation for classification tasks
        cls_representation = x[:, 0, :]

        return x, cls_representation

    def mlm_forward(self, input_ids, segment_ids, masked_positions):
        """Forward pass for masked language modeling"""
        x, _ = self(input_ids, segment_ids)

        # Get representations for masked positions
        masked_representations = x[torch.arange(x.size(0)).unsqueeze(1), masked_positions]

        # Predict masked tokens
        mlm_logits = self.mlm_head(masked_representations)

        return mlm_logits

    def nsp_forward(self, cls_representation):
        """Forward pass for next sentence prediction"""
        nsp_logits = self.nsp_head(cls_representation)
        return nsp_logits
```

## Training Techniques

### Pre-training Objectives

#### Masked Language Modeling (MLM)

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset

class MLMDataset(Dataset):
    def __init__(self, texts, tokenizer, max_len=512, mask_prob=0.15):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.mask_prob = mask_prob

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]

        # Tokenize
        tokens = self.tokenizer.encode(text, max_length=self.max_len, truncation=True)

        # Create masked version
        masked_tokens, labels = self._mask_tokens(tokens)

        return {
            'input_ids': torch.tensor(masked_tokens),
            'labels': torch.tensor(labels)
        }

    def _mask_tokens(self, tokens):
        """Apply masking to tokens for MLM"""
        labels = [-100] * len(tokens)  # -100 is ignored in loss computation

        for i, token in enumerate(tokens):
            if token in [self.tokenizer.cls_token_id, self.tokenizer.sep_token_id]:
                continue

            # Randomly mask tokens
            rand = torch.rand(1).item()
            if rand < self.mask_prob:
                # 80% mask, 10% random, 10% keep original
                rand = torch.rand(1).item()
                if rand < 0.8:
                    tokens[i] = self.tokenizer.mask_token_id
                elif rand < 0.9:
                    tokens[i] = torch.randint(100, self.tokenizer.vocab_size - 100, (1,)).item()

                labels[i] = token

        return tokens, labels

def mlm_loss(mlm_logits, labels):
    """Compute masked language modeling loss"""
    loss_fn = nn.CrossEntropyLoss()
    # Flatten logits and labels
    mlm_logits = mlm_logits.view(-1, mlm_logits.size(-1))
    labels = labels.view(-1)
    # Only compute loss on masked positions
    masked_positions = labels != -100
    return loss_fn(mlm_logits[masked_positions], labels[masked_positions])
```

#### Next Sentence Prediction (NSP)

```python
class NSPDataset(Dataset):
    def __init__(self, texts, tokenizer, max_len=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts) - 1  # Need pairs

    def __getitem__(self, idx):
        # Get two consecutive sentences
        sentence_a = self.texts[idx]
        sentence_b = self.texts[idx + 1]

        # 50% of the time, use actual next sentence
        # 50% of the time, use random sentence
        if torch.rand(1).item() < 0.5:
            label = 1  # Is next sentence
        else:
            random_idx = torch.randint(0, len(self.texts), (1,)).item()
            sentence_b = self.texts[random_idx]
            label = 0  # Is not next sentence

        # Tokenize
        encoded = self.tokenizer(
            sentence_a, sentence_b,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoded['input_ids'].squeeze(),
            'attention_mask': encoded['attention_mask'].squeeze(),
            'token_type_ids': encoded['token_type_ids'].squeeze(),
            'label': torch.tensor(label)
        }

def nsp_loss(nsp_logits, labels):
    """Compute next sentence prediction loss"""
    loss_fn = nn.CrossEntropyLoss()
    return loss_fn(nsp_logits, labels)
```

#### Causal Language Modeling

```python
class CausalLMDataset(Dataset):
    def __init__(self, texts, tokenizer, max_len=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]

        # Tokenize
        tokens = self.tokenizer.encode(text, max_length=self.max_len, truncation=True)

        # Shift for causal prediction
        input_ids = tokens[:-1]
        labels = tokens[1:]

        return {
            'input_ids': torch.tensor(input_ids),
            'labels': torch.tensor(labels)
        }

def causal_lm_loss(logits, labels):
    """Compute causal language modeling loss"""
    loss_fn = nn.CrossEntropyLoss()
    # Shift logits to align with labels
    shift_logits = logits[..., :-1, :].contiguous()
    shift_labels = labels[..., 1:].contiguous()

    return loss_fn(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
```

### Fine-tuning Techniques

#### Supervised Fine-tuning

```python
class ClassificationHead(nn.Module):
    def __init__(self, hidden_size, num_classes):
        super().__init__()
        self.classifier = nn.Linear(hidden_size, num_classes)

    def forward(self, hidden_states):
        # Use [CLS] token for classification
        cls_representation = hidden_states[:, 0, :]
        logits = self.classifier(cls_representation)
        return logits

def fine_tune_for_classification(model, train_dataloader, num_epochs=3):
    """Fine-tune a pre-trained model for classification"""

    # Add classification head
    classifier = ClassificationHead(model.config.hidden_size, num_classes=2)
    model.classifier = classifier

    # Set up optimizer
    optimizer = torch.optim.AdamW([
        {'params': model.parameters(), 'lr': 2e-5},
        {'params': classifier.parameters(), 'lr': 1e-3}
    ])

    model.train()

    for epoch in range(num_epochs):
        total_loss = 0

        for batch in train_dataloader:
            input_ids = batch['input_ids']
            attention_mask = batch['attention_mask']
            labels = batch['labels']

            # Forward pass
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = model.classifier(outputs.last_hidden_state)

            # Compute loss
            loss = nn.CrossEntropyLoss()(logits, labels)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch + 1}, Loss: {total_loss / len(train_dataloader)}")

    return model
```

#### Parameter-Efficient Fine-tuning (PEFT)

```python
class LoRALayer(nn.Module):
    def __init__(self, original_layer, rank=8, alpha=16):
        super().__init__()
        self.original_layer = original_layer
        self.rank = rank
        self.alpha = alpha

        # Freeze original parameters
        for param in self.original_layer.parameters():
            param.requires_grad = False

        # LoRA parameters
        self.lora_A = nn.Parameter(torch.randn(original_layer.in_features, rank))
        self.lora_B = nn.Parameter(torch.zeros(rank, original_layer.out_features))

        # Scaling factor
        self.scaling = alpha / rank

    def forward(self, x):
        # Original forward pass
        original_output = self.original_layer(x)

        # LoRA adaptation
        lora_output = (x @ self.lora_A @ self.lora_B) * self.scaling

        return original_output + lora_output

def apply_lora_to_model(model, rank=8):
    """Apply LoRA to transformer layers"""
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear) and 'attention' in name:
            # Replace with LoRA layer
            parent_name = '.'.join(name.split('.')[:-1])
            child_name = name.split('.')[-1]

            parent_module = model
            for part in parent_name.split('.'):
                parent_module = getattr(parent_module, part)

            setattr(parent_module, child_name, LoRALayer(module, rank))

    return model
```

#### Instruction Tuning

```python
class InstructionDataset(Dataset):
    def __init__(self, instructions, responses, tokenizer, max_len=512):
        self.instructions = instructions
        self.responses = responses
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.instructions)

    def __getitem__(self, idx):
        instruction = self.instructions[idx]
        response = self.responses[idx]

        # Format as instruction-response pair
        text = f"Instruction: {instruction}\nResponse: {response}"

        # Tokenize
        tokens = self.tokenizer.encode(text, max_length=self.max_len, truncation=True)

        return {
            'input_ids': torch.tensor(tokens),
            'labels': torch.tensor(tokens)  # For causal LM, labels = input_ids
        }

def instruction_tune_model(model, train_dataloader, num_epochs=3):
    """Instruction-tune a language model"""

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    model.train()

    for epoch in range(num_epochs):
        total_loss = 0

        for batch in train_dataloader:
            input_ids = batch['input_ids']
            labels = batch['labels']

            # Forward pass
            outputs = model(input_ids=input_ids, labels=labels)
            loss = outputs.loss

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch + 1}, Loss: {total_loss / len(train_dataloader)}")

    return model
```

## Deployment and Inference

### Model Quantization

```python
import torch
from torch.quantization import quantize_dynamic

def quantize_model(model, quantization_config=None):
    """Quantize a model for efficient inference"""

    if quantization_config is None:
        quantization_config = torch.quantization.get_default_qconfig('fbgemm')

    # Prepare model for quantization
    model.eval()
    model.qconfig = quantization_config

    # Fuse layers where possible
    torch.quantization.fuse_modules(model, [['conv', 'bn']], inplace=True)

    # Prepare for quantization
    torch.quantization.prepare(model, inplace=True)

    # Calibrate with sample data
    with torch.no_grad():
        for batch in calibration_dataloader:
            model(batch['input_ids'])

    # Convert to quantized model
    torch.quantization.convert(model, inplace=True)

    return model

# Dynamic quantization (simpler approach)
def dynamic_quantize_model(model):
    """Apply dynamic quantization"""
    quantized_model = quantize_dynamic(
        model,
        {torch.nn.Linear},  # Quantize linear layers
        dtype=torch.qint8
    )

    return quantized_model
```

### Model Serving

```python
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LLM API")

# Load model and tokenizer
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Add padding token if missing
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

class GenerateRequest(BaseModel):
    prompt: str
    max_length: int = 50
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True

class GenerateResponse(BaseModel):
    generated_text: str
    input_length: int
    output_length: int

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    try:
        # Tokenize input
        inputs = tokenizer(
            request.prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        input_length = len(inputs['input_ids'][0])

        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_length=request.max_length + input_length,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=request.do_sample,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        # Decode generated text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        output_length = len(outputs[0])

        return GenerateResponse(
            generated_text=generated_text,
            input_length=input_length,
            output_length=output_length
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Batch Inference Optimization

```python
import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM

class BatchInferenceEngine:
    def __init__(self, model_name, batch_size=8, max_length=512):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()

        # Move to GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        self.batch_size = batch_size
        self.max_length = max_length

        # Enable optimizations
        torch.backends.cudnn.benchmark = True
        if torch.cuda.is_available():
            self.model = torch.compile(self.model)

    def generate_batch(self, prompts, **generation_kwargs):
        """Generate text for a batch of prompts"""

        # Tokenize all prompts
        inputs = self.tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **generation_kwargs
            )

        # Decode batch
        generated_texts = []
        for output in outputs:
            text = self.tokenizer.decode(output, skip_special_tokens=True)
            generated_texts.append(text)

        return generated_texts

    def process_dataset(self, dataset, output_file):
        """Process a large dataset in batches"""

        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        with open(output_file, 'w') as f:
            for batch in dataloader:
                prompts = batch['prompt']

                # Generate responses
                responses = self.generate_batch(
                    prompts,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True
                )

                # Write results
                for prompt, response in zip(prompts, responses):
                    f.write(f"Prompt: {prompt}\n")
                    f.write(f"Response: {response}\n")
                    f.write("-" * 50 + "\n")
```

## Advanced Techniques

### Retrieval-Augmented Generation (RAG)

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline

class RAGSystem:
    def __init__(self, retriever_model="all-MiniLM-L6-v2", generator_model="facebook/bart-large-cnn"):
        # Initialize retriever
        self.retriever = SentenceTransformer(retriever_model)

        # Initialize generator
        self.generator = pipeline("summarization", model=generator_model)

        # Document store
        self.documents = []
        self.doc_embeddings = None

    def add_documents(self, documents):
        """Add documents to the knowledge base"""
        self.documents.extend(documents)

        # Compute embeddings
        self.doc_embeddings = self.retriever.encode(self.documents)

    def retrieve(self, query, top_k=3):
        """Retrieve relevant documents for a query"""
        # Encode query
        query_embedding = self.retriever.encode([query])

        # Compute similarities
        similarities = cosine_similarity(query_embedding, self.doc_embeddings)[0]

        # Get top-k documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        retrieved_docs = [self.documents[i] for i in top_indices]

        return retrieved_docs

    def generate_answer(self, query, context_docs):
        """Generate answer using retrieved context"""

        # Combine query and context
        context = " ".join(context_docs)
        input_text = f"Query: {query}\nContext: {context}\nAnswer:"

        # Generate answer
        result = self.generator(
            input_text,
            max_length=150,
            min_length=50,
            do_sample=False
        )

        return result[0]['summary_text']

    def answer_query(self, query):
        """End-to-end RAG pipeline"""
        # Retrieve relevant documents
        context_docs = self.retrieve(query)

        # Generate answer
        answer = self.generate_answer(query, context_docs)

        return answer, context_docs
```

### Fine-tuning with Reinforcement Learning (RLHF)

```python
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForCausalLM

class RewardModel(nn.Module):
    def __init__(self, model_name):
        super().__init__()
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.reward_head = nn.Linear(self.model.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs.last_hidden_state

        # Use the last token's representation for reward
        reward = self.reward_head(last_hidden_state[:, -1, :])

        return reward

def ppo_step(model, tokenizer, batch, reward_model, optimizer, epsilon=0.2):
    """Single PPO optimization step"""

    prompts = batch['prompt']
    responses = batch['response']
    rewards = batch['reward']

    # Tokenize
    inputs = tokenizer(
        [f"{p} {r}" for p, r in zip(prompts, responses)],
        return_tensors="pt",
        padding=True,
        truncation=True
    )

    # Get old log probabilities
    with torch.no_grad():
        old_outputs = model(**inputs)
        old_logits = old_outputs.logits
        old_log_probs = torch.log_softmax(old_logits, dim=-1)

    # Get rewards from reward model
    with torch.no_grad():
        reward_scores = reward_model(
            inputs['input_ids'],
            inputs['attention_mask']
        ).squeeze()

    # Compute advantages (simplified)
    advantages = reward_scores - reward_scores.mean()

    # PPO update
    for _ in range(4):  # Multiple epochs
        # Get new log probabilities
        new_outputs = model(**inputs)
        new_logits = new_outputs.logits
        new_log_probs = torch.log_softmax(new_logits, dim=-1)

        # Compute ratio
        ratio = torch.exp(new_log_probs - old_log_probs)

        # PPO objective
        surr1 = ratio * advantages.unsqueeze(-1).unsqueeze(-1)
        surr2 = torch.clamp(ratio, 1-epsilon, 1+epsilon) * advantages.unsqueeze(-1).unsqueeze(-1)

        policy_loss = -torch.min(surr1, surr2).mean()

        # Update model
        optimizer.zero_grad()
        policy_loss.backward()
        optimizer.step()

    return policy_loss.item()
```

### Model Compression and Distillation

```python
class DistillationTrainer:
    def __init__(self, teacher_model, student_model, temperature=2.0, alpha=0.5):
        self.teacher = teacher_model
        self.student = student_model
        self.temperature = temperature
        self.alpha = alpha

        # Set teacher to eval mode
        self.teacher.eval()

    def distillation_loss(self, student_logits, teacher_logits, labels):
        """Compute distillation loss"""

        # Soft targets from teacher
        teacher_soft = torch.softmax(teacher_logits / self.temperature, dim=-1)
        student_soft = torch.log_softmax(student_logits / self.temperature, dim=-1)

        # KL divergence loss
        distillation_loss = nn.KLDivLoss(reduction='batchmean')(
            student_soft, teacher_soft
        ) * (self.temperature ** 2)

        # Hard targets loss
        hard_loss = nn.CrossEntropyLoss()(student_logits, labels)

        # Combined loss
        loss = self.alpha * distillation_loss + (1 - self.alpha) * hard_loss

        return loss

    def train_step(self, batch, optimizer):
        """Single training step"""

        input_ids = batch['input_ids']
        labels = batch['labels']

        # Teacher forward pass
        with torch.no_grad():
            teacher_outputs = self.teacher(input_ids)
            teacher_logits = teacher_outputs.logits

        # Student forward pass
        student_outputs = self.student(input_ids)
        student_logits = student_outputs.logits

        # Compute loss
        loss = self.distillation_loss(student_logits, teacher_logits, labels)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        return loss.item()
```

## Evaluation and Benchmarks

### Perplexity Calculation

```python
def calculate_perplexity(model, tokenizer, texts):
    """Calculate perplexity on a dataset"""

    model.eval()
    total_loss = 0
    total_tokens = 0

    with torch.no_grad():
        for text in texts:
            # Tokenize
            inputs = tokenizer(text, return_tensors="pt")
            input_ids = inputs['input_ids']

            # Get model outputs
            outputs = model(input_ids, labels=input_ids)
            loss = outputs.loss

            # Accumulate
            total_loss += loss.item() * input_ids.size(1)
            total_tokens += input_ids.size(1)

    # Calculate perplexity
    avg_loss = total_loss / total_tokens
    perplexity = torch.exp(torch.tensor(avg_loss))

    return perplexity.item()
```

### ROUGE and BLEU Scores

```python
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def evaluate_generation_quality(predictions, references):
    """Evaluate generation quality using ROUGE and BLEU"""

    rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    smoothing = SmoothingFunction().method1

    rouge_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
    bleu_scores = []

    for pred, ref in zip(predictions, references):
        # ROUGE scores
        scores = rouge.score(ref, pred)
        for key in rouge_scores:
            rouge_scores[key].append(scores[key].fmeasure)

        # BLEU score
        pred_tokens = pred.split()
        ref_tokens = ref.split()
        bleu = sentence_bleu([ref_tokens], pred_tokens, smoothing_function=smoothing)
        bleu_scores.append(bleu)

    # Average scores
    results = {
        'rouge1': sum(rouge_scores['rouge1']) / len(rouge_scores['rouge1']),
        'rouge2': sum(rouge_scores['rouge2']) / len(rouge_scores['rouge2']),
        'rougeL': sum(rouge_scores['rougeL']) / len(rouge_scores['rougeL']),
        'bleu': sum(bleu_scores) / len(bleu_scores)
    }

    return results
```

### Human Evaluation Frameworks

```python
import pandas as pd
from typing import List, Dict

class HumanEvaluationFramework:
    def __init__(self, evaluation_criteria):
        self.criteria = evaluation_criteria  # e.g., ['fluency', 'relevance', 'coherence']

    def create_evaluation_form(self, model_outputs: List[str], references: List[str] = None):
        """Create evaluation forms for human raters"""

        evaluation_data = []

        for i, output in enumerate(model_outputs):
            entry = {
                'sample_id': i,
                'model_output': output,
                'reference': references[i] if references else None
            }

            # Add rating fields for each criterion
            for criterion in self.criteria:
                entry[f'{criterion}_rating'] = None  # To be filled by human raters
                entry[f'{criterion}_comments'] = None

            evaluation_data.append(entry)

        return pd.DataFrame(evaluation_data)

    def analyze_ratings(self, ratings_df: pd.DataFrame):
        """Analyze human evaluation ratings"""

        analysis = {}

        for criterion in self.criteria:
            ratings = ratings_df[f'{criterion}_rating'].dropna()

            analysis[criterion] = {
                'mean': ratings.mean(),
                'std': ratings.std(),
                'median': ratings.median(),
                'min': ratings.min(),
                'max': ratings.max()
            }

        return analysis

    def inter_rater_agreement(self, ratings_df: pd.DataFrame, raters: List[str]):
        """Calculate inter-rater agreement using Cohen's Kappa"""

        from sklearn.metrics import cohen_kappa_score

        agreements = {}

        for criterion in self.criteria:
            rater_columns = [f'{criterion}_rating_{rater}' for rater in raters]

            if len(rater_columns) == 2:
                # Cohen's Kappa for two raters
                kappa = cohen_kappa_score(
                    ratings_df[rater_columns[0]],
                    ratings_df[rater_columns[1]]
                )
                agreements[criterion] = kappa

        return agreements
```

## Ethical Considerations and Safety

### Bias Detection and Mitigation

```python
from transformers import pipeline
import torch

class BiasDetector:
    def __init__(self, model_name="unitary/toxic-bert"):
        self.toxicity_classifier = pipeline("text-classification", model=model_name)

    def detect_toxicity(self, texts: List[str]):
        """Detect toxic content in generated text"""

        results = self.toxicity_classifier(texts)

        toxicity_scores = []
        for result in results:
            # Assuming binary classification with 'toxic' label
            score = result[0]['score'] if result[0]['label'] == 'toxic' else 1 - result[0]['score']
            toxicity_scores.append(score)

        return toxicity_scores

    def filter_outputs(self, texts: List[str], threshold: float = 0.5):
        """Filter out toxic or biased content"""

        toxicity_scores = self.detect_toxicity(texts)

        filtered_texts = []
        for text, score in zip(texts, toxicity_scores):
            if score < threshold:
                filtered_texts.append(text)

        return filtered_texts

class FairnessEvaluator:
    def __init__(self, protected_attributes):
        self.protected_attributes = protected_attributes

    def evaluate_demographic_parity(self, predictions, sensitive_attributes):
        """Evaluate demographic parity"""

        groups = {}
        for attr in self.protected_attributes:
            unique_values = set(sensitive_attributes[attr])
            groups[attr] = unique_values

        parity_scores = {}

        for attr, values in groups.items():
            for value in values:
                mask = [sa[attr] == value for sa in sensitive_attributes]
                group_predictions = [p for p, m in zip(predictions, mask) if m]

                if group_predictions:
                    positive_rate = sum(group_predictions) / len(group_predictions)
                    parity_scores[f"{attr}_{value}"] = positive_rate

        return parity_scores

    def evaluate_equal_opportunity(self, predictions, labels, sensitive_attributes):
        """Evaluate equal opportunity"""

        opportunity_scores = {}

        for attr in self.protected_attributes:
            unique_values = set(sensitive_attributes[attr])

            for value in unique_values:
                mask = [sa[attr] == value for sa in sensitive_attributes]
                group_predictions = [p for p, m in zip(predictions, mask) if m]
                group_labels = [l for l, m in zip(labels, mask) if m]

                # True positive rate for this group
                tp = sum(p and l for p, l in zip(group_predictions, group_labels))
                fn = sum(not p and l for p, l in zip(group_predictions, group_labels))

                if tp + fn > 0:
                    tpr = tp / (tp + fn)
                    opportunity_scores[f"{attr}_{value}"] = tpr

        return opportunity_scores
```

### Safety Alignment

```python
class SafetyFilter:
    def __init__(self, safety_model_path):
        # Load safety classification model
        self.safety_model = pipeline("text-classification", model=safety_model_path)

    def is_safe(self, text: str, threshold: float = 0.8):
        """Check if text is safe to generate"""

        result = self.safety_model(text)[0]

        # Assuming higher score means safer
        return result['score'] > threshold

    def detoxify_response(self, response: str, detox_model):
        """Attempt to detoxify unsafe responses"""

        if not self.is_safe(response):
            # Use detoxification model to rewrite
            detoxified = detox_model(response)
            return detoxified

        return response

class ConstitutionalAI:
    def __init__(self, base_model, critique_model, revision_model):
        self.base_model = base_model
        self.critique_model = critique_model
        self.revision_model = revision_model

    def generate_with_constitution(self, prompt: str, constitution_rules: List[str]):
        """Generate text following constitutional guidelines"""

        # Initial generation
        response = self.base_model.generate(prompt)

        # Critique based on constitution
        critiques = []
        for rule in constitution_rules:
            critique = self.critique_model.generate(f"Rule: {rule}\nResponse: {response}\nCritique:")
            critiques.append(critique)

        # Revision based on critiques
        combined_critiques = "\n".join(critiques)
        revision_prompt = f"Original: {response}\nCritiques: {combined_critiques}\nRevised:"

        revised_response = self.revision_model.generate(revision_prompt)

        return revised_response
```

## Best Practices

### Development Best Practices
1. **Start Small**: Begin with smaller models and datasets for experimentation
2. **Data Quality**: Ensure high-quality, diverse training data
3. **Version Control**: Track model versions, data versions, and code changes
4. **Reproducibility**: Use fixed random seeds and document all hyperparameters
5. **Modular Design**: Build reusable components and pipelines

### Training Best Practices
1. **Progressive Training**: Start with smaller datasets and gradually scale
2. **Regular Validation**: Monitor training metrics and validate frequently
3. **Early Stopping**: Prevent overfitting with appropriate stopping criteria
4. **Gradient Clipping**: Prevent gradient explosion in large models
5. **Mixed Precision**: Use FP16 training for memory efficiency

### Deployment Best Practices
1. **Model Optimization**: Quantize and compress models for production
2. **Scalable Serving**: Use load balancing and auto-scaling
3. **Monitoring**: Track performance, latency, and error rates
4. **Fallback Strategies**: Have backup models or responses
5. **A/B Testing**: Gradually roll out model updates

### Ethical Best Practices
1. **Bias Audits**: Regularly audit models for bias and fairness
2. **Transparency**: Document model decisions and limitations
3. **User Consent**: Obtain consent for data usage
4. **Harm Mitigation**: Implement safety filters and content moderation
5. **Continuous Monitoring**: Monitor for emerging issues and biases

Large Language Models represent one of the most significant advances in AI, enabling unprecedented capabilities in natural language understanding and generation. However, they require careful development, deployment, and monitoring to ensure safe, ethical, and beneficial applications.
