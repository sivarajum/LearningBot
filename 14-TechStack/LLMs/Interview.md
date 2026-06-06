# LLMs Interview Questions and Answers

## Beginner Level Questions

### Q1: What are Large Language Models (LLMs) and how do they work?

**Answer:**
Large Language Models (LLMs) are AI systems trained on vast amounts of text data to understand and generate human-like text. They use deep neural networks, particularly Transformer architectures, to learn patterns in language.

**How They Work:**
1. **Training**: Trained on massive text corpora (billions of parameters)
2. **Architecture**: Based on Transformer architecture with attention mechanisms
3. **Tokenization**: Text converted to tokens (subwords or words)
4. **Embeddings**: Tokens converted to vector representations
5. **Attention**: Models attend to relevant parts of input
6. **Generation**: Generate text token by token using probabilities

**Key Characteristics:**
- **Scale**: Billions of parameters
- **Pre-training**: Trained on diverse text data
- **Fine-tuning**: Can be fine-tuned for specific tasks
- **Generative**: Generate coherent text
- **Context-aware**: Understand context and generate relevant responses

### Q2: Explain the Transformer architecture.

**Answer:**

**Transformer Architecture:**
- **Encoder-Decoder**: Original Transformer has encoder and decoder
- **Self-Attention**: Allows model to attend to all positions
- **Multi-Head Attention**: Multiple attention mechanisms in parallel
- **Positional Encoding**: Adds positional information to tokens
- **Feed-Forward Networks**: Processes attended representations
- **Layer Normalization**: Normalizes activations
- **Residual Connections**: Helps with gradient flow

**Key Components:**
- **Attention Mechanism**: Computes relationships between tokens
- **Encoder**: Processes input sequence
- **Decoder**: Generates output sequence
- **Embeddings**: Convert tokens to vectors

**Example:**
```python
import torch
import torch.nn as nn

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
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.d_k ** 0.5)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)
        
        output = output.transpose(1, 2).contiguous().view(
            batch_size, -1, self.d_model
        )
        
        return self.W_o(output)
```

### Q3: What is the difference between encoder-only, decoder-only, and encoder-decoder models?

**Answer:**

**Encoder-Only Models:**
- **Examples**: BERT, RoBERTa
- **Use Cases**: Classification, NER, sentiment analysis
- **Architecture**: Bidirectional attention
- **Training**: Masked language modeling

**Decoder-Only Models:**
- **Examples**: GPT, GPT-2, GPT-3, GPT-4
- **Use Cases**: Text generation, completion
- **Architecture**: Autoregressive, causal attention
- **Training**: Next token prediction

**Encoder-Decoder Models:**
- **Examples**: T5, BART
- **Use Cases**: Translation, summarization, QA
- **Architecture**: Encoder processes input, decoder generates output
- **Training**: Sequence-to-sequence tasks

### Q4: Explain attention mechanisms in Transformers.

**Answer:**

**Attention Mechanism:**
- Allows model to focus on relevant parts of input
- Computes relationships between all token pairs
- Uses query, key, and value vectors
- Produces weighted combination of values

**Types of Attention:**

**1. Self-Attention:**
- Attention within same sequence
- Computes relationships between tokens
- Used in encoder and decoder

**2. Cross-Attention:**
- Attention between different sequences
- Decoder attends to encoder output
- Used in encoder-decoder models

**3. Masked Self-Attention:**
- Causal attention in decoder
- Prevents attending to future tokens
- Used in autoregressive models

**Scaled Dot-Product Attention:**
```python
def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
    
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    attention_weights = torch.softmax(scores, dim=-1)
    output = torch.matmul(attention_weights, V)
    
    return output, attention_weights
```

### Q5: What is fine-tuning and how does it work?

**Answer:**

**Fine-tuning:**
- Adapting pre-trained LLM to specific task
- Updates model weights for task-specific data
- More efficient than training from scratch
- Requires less data and computation

**Fine-tuning Methods:**

**1. Full Fine-tuning:**
- Updates all model parameters
- Most flexible but computationally expensive
- Best for large datasets

**2. Parameter-Efficient Fine-tuning (PEFT):**
- Updates only subset of parameters
- LoRA, Adapter, Prompt Tuning
- More efficient, less memory

**3. Few-Shot Learning:**
- Uses few examples in prompt
- No weight updates
- Quick adaptation

**Example:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer

# Load pre-trained model
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Fine-tuning
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=500,
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

## Intermediate Level Questions

### Q6: Explain prompt engineering and its techniques.

**Answer:**

**Prompt Engineering:**
- Designing effective prompts for LLMs
- Maximizes model performance
- Reduces need for fine-tuning
- Improves output quality

**Techniques:**

**1. Zero-Shot Learning:**
- No examples in prompt
- Direct instruction
- Relies on pre-training

**2. Few-Shot Learning:**
- Few examples in prompt
- Demonstrates desired behavior
- Improves performance

**3. Chain-of-Thought:**
- Step-by-step reasoning
- Improves complex reasoning
- Better accuracy

**4. Role-Playing:**
- Assign roles to model
- Context-specific behavior
- Better persona consistency

**Example:**
```python
# Zero-shot
prompt = "Translate English to French: Hello, how are you?"

# Few-shot
prompt = """
Translate English to French:
Hello -> Bonjour
Goodbye -> Au revoir
Thank you -> Merci
Hello, how are you? ->
"""

# Chain-of-thought
prompt = """
Solve: A store has 15 apples. They sell 6. How many are left?
Step 1: Start with 15 apples
Step 2: Subtract 6 sold
Step 3: 15 - 6 = 9
Answer: 9 apples
"""
```

### Q7: What are the challenges and limitations of LLMs?

**Answer:**

**Challenges:**

**1. Hallucinations:**
- Generate factually incorrect information
- Confidently present false information
- Difficult to detect and prevent

**2. Bias:**
- Reflect training data biases
- Generate biased or harmful content
- Require bias mitigation

**3. Context Window:**
- Limited context length
- Cannot process very long documents
- Requires chunking or summarization

**4. Computational Cost:**
- Expensive to train and deploy
- High memory requirements
- Slow inference for large models

**5. Safety and Security:**
- Vulnerable to prompt injection
- Can generate harmful content
- Require safety measures

**Mitigation Strategies:**
- Fine-tuning on high-quality data
- Prompt engineering and validation
- Human-in-the-loop systems
- Safety filters and content moderation
- RAG for accurate information

### Q8: Explain LLM evaluation metrics.

**Answer:**

**Evaluation Metrics:**

**1. Perplexity:**
- Measures model uncertainty
- Lower is better
- Used for language modeling

**2. BLEU:**
- N-gram overlap with reference
- Used for translation and generation
- Range: 0-1 (higher is better)

**3. ROUGE:**
- Recall-oriented evaluation
- Used for summarization
- ROUGE-L, ROUGE-1, ROUGE-2

**4. Human Evaluation:**
- Human judges rate outputs
- More reliable but expensive
- Fluency, relevance, accuracy

**5. Task-Specific Metrics:**
- Accuracy for classification
- F1-score for NER
- Exact match for QA

**Example:**
```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def calculate_perplexity(text):
    encodings = tokenizer(text, return_tensors="pt")
    max_length = model.config.n_positions
    stride = 512
    
    nlls = []
    for i in range(0, encodings.input_ids.size(1), stride):
        begin_loc = max(i + stride - max_length, 0)
        end_loc = min(i + stride, encodings.input_ids.size(1))
        trg_len = end_loc - i
        
        input_ids = encodings.input_ids[:, begin_loc:end_loc]
        target_ids = input_ids.clone()
        target_ids[:, :-trg_len] = -100
        
        with torch.no_grad():
            outputs = model(input_ids, labels=target_ids)
            neg_log_likelihood = outputs.loss * trg_len
        
        nlls.append(neg_log_likelihood)
    
    ppl = torch.exp(torch.stack(nlls).sum() / end_loc)
    return ppl.item()
```

## Advanced Level Questions

### Q9: Explain parameter-efficient fine-tuning methods (LoRA, Adapters).

**Answer:**

**Parameter-Efficient Fine-tuning:**

**1. LoRA (Low-Rank Adaptation):**
- Decomposes weight updates into low-rank matrices
- Reduces trainable parameters
- Maintains model performance
- Efficient memory usage

**2. Adapters:**
- Adds small adapter layers
- Freezes original model
- Trains only adapters
- Modular and reusable

**3. Prompt Tuning:**
- Learns soft prompts
- No model weight updates
- Very parameter-efficient
- Task-specific prompts

**Example (LoRA):**
```python
from peft import LoraConfig, get_peft_model

# LoRA configuration
lora_config = LoraConfig(
    r=16,  # Rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Train only LoRA parameters
for param in model.parameters():
    if param.requires_grad:
        print(param.shape)  # Only LoRA parameters
```

### Q10: Explain LLM inference optimization techniques.

**Answer:**

**Inference Optimization:**

**1. Quantization:**
- Reduce precision (FP32 -> INT8)
- Faster inference
- Lower memory usage
- Minimal accuracy loss

**2. Pruning:**
- Remove unnecessary parameters
- Smaller model size
- Faster inference
- Maintains performance

**3. Knowledge Distillation:**
- Train smaller model from larger model
- Transfer knowledge
- Faster inference
- Smaller model size

**4. Caching:**
- Cache key-value pairs
- Reuse computations
- Faster generation
- Reduces computation

**5. Batching:**
- Process multiple requests together
- Better GPU utilization
- Higher throughput
- Lower latency per request

**Example:**
```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# Quantization
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)

model = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    quantization_config=quantization_config
)
```

---

## Key Takeaways

1. **LLMs are large neural networks** trained on vast text data
2. **Transformer architecture** with attention mechanisms is foundation
3. **Fine-tuning** adapts pre-trained models to specific tasks
4. **Prompt engineering** maximizes model performance
5. **LLMs have limitations** including hallucinations and bias
6. **Evaluation metrics** measure model performance
7. **Parameter-efficient fine-tuning** reduces training costs
8. **Inference optimization** improves deployment efficiency

