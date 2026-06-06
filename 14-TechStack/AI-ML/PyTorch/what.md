# PyTorch: Dynamic Neural Networks and Deep Learning

## Overview

PyTorch is an open-source machine learning framework that provides tensor computation with strong GPU acceleration and deep learning capabilities. It emphasizes flexibility, ease of use, and dynamic computation graphs.

## Core Architecture

### PyTorch Tensors and Operations

PyTorch's fundamental data structure is the tensor, similar to NumPy arrays but with GPU acceleration:

```python
import torch
import torch.nn as nn

# Creating tensors
x = torch.tensor([1, 2, 3, 4, 5])  # 1D tensor
y = torch.randn(3, 4)              # Random 3x4 tensor
z = torch.zeros(2, 3, 4)           # 3D tensor of zeros

# Tensor operations
a = torch.randn(3, 4)
b = torch.randn(3, 4)
c = a + b                          # Element-wise addition
d = torch.matmul(a, b.t())         # Matrix multiplication

# GPU operations
if torch.cuda.is_available():
    device = torch.device('cuda')
    x_gpu = x.to(device)
    y_gpu = y.to(device)
    z_gpu = x_gpu + y_gpu
```

### Dynamic Computation Graphs

PyTorch uses dynamic computation graphs that are built on-the-fly during execution:

```python
# Dynamic graph construction
def dynamic_function(x):
    if x.sum() > 0:
        y = x * 2
    else:
        y = x / 2
    return y

x = torch.randn(5)
y = dynamic_function(x)  # Graph built dynamically

# Gradient computation
y.backward()  # Automatically computes gradients
print(x.grad)  # Access gradients
```

### Autograd: Automatic Differentiation

PyTorch's autograd system automatically computes gradients for tensor operations:

```python
# Automatic differentiation
x = torch.randn(3, requires_grad=True)
y = torch.randn(3, requires_grad=True)
z = x * y + torch.sin(x)

# Compute gradients
z.backward(torch.ones_like(z))
print(x.grad)  # dz/dx
print(y.grad)  # dz/dy

# Higher-order derivatives
x = torch.randn(1, requires_grad=True)
y = x ** 3
first_grad = torch.autograd.grad(y, x, create_graph=True)[0]
second_grad = torch.autograd.grad(first_grad, x)[0]
print(second_grad)  # d²y/dx² = 6x
```

## Building Neural Networks

### nn.Module: The Base Class

All neural network modules inherit from nn.Module:

```python
class SimpleNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Usage
model = SimpleNet(784, 128, 10)
input_tensor = torch.randn(32, 784)  # Batch of 32, 784 features each
output = model(input_tensor)
```

### Sequential API

For simple sequential architectures:

```python
# Sequential model
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 10),
    nn.Softmax(dim=1)
)

# Forward pass
x = torch.randn(32, 784)
output = model(x)
```

### Custom Layers and Operations

Creating specialized layers and operations:

```python
class CustomLayer(nn.Module):
    def __init__(self, in_features, out_features):
        super(CustomLayer, self).__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.randn(out_features))

    def forward(self, x):
        return torch.matmul(x, self.weight.t()) + self.bias

class ComplexModel(nn.Module):
    def __init__(self):
        super(ComplexModel, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(64, 3, 2, stride=2),
            nn.Sigmoid()
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded
```

## Training and Optimization

### Optimizers

PyTorch provides various optimization algorithms:

```python
import torch.optim as optim

# Model and loss
model = SimpleNet(784, 128, 10)
criterion = nn.CrossEntropyLoss()

# Different optimizers
optimizer_sgd = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
optimizer_adam = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
optimizer_adamw = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)

# Learning rate schedulers
scheduler = optim.lr_scheduler.StepLR(optimizer_adam, step_size=30, gamma=0.1)
scheduler_cosine = optim.lr_scheduler.CosineAnnealingLR(optimizer_adam, T_max=100)
```

### Training Loops

Custom training loops with gradient computation:

```python
def train_epoch(model, train_loader, optimizer, criterion, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)

        # Zero gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        # Backward pass
        loss.backward()

        # Update weights
        optimizer.step()

        # Statistics
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    return running_loss / len(train_loader), 100. * correct / total

# Training loop
for epoch in range(num_epochs):
    train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, device)
    val_loss, val_acc = validate_epoch(model, val_loader, criterion, device)

    print(f'Epoch {epoch+1}: Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%, '
          f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
```

### Loss Functions

Built-in and custom loss functions:

```python
# Classification losses
cross_entropy = nn.CrossEntropyLoss()
bce_loss = nn.BCELoss()
bce_with_logits = nn.BCEWithLogitsLoss()

# Regression losses
mse_loss = nn.MSELoss()
l1_loss = nn.L1Loss()
smooth_l1 = nn.SmoothL1Loss()

# Custom loss
class CustomLoss(nn.Module):
    def __init__(self, alpha=0.5, beta=1.0):
        super(CustomLoss, self).__init__()
        self.alpha = alpha
        self.beta = beta
        self.mse = nn.MSELoss()
        self.l1 = nn.L1Loss()

    def forward(self, pred, target):
        mse_term = self.mse(pred, target)
        l1_term = self.l1(pred, target)
        return self.alpha * mse_term + self.beta * l1_term
```

## Data Loading and Processing

### torch.utils.data

PyTorch's data loading utilities:

```python
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, data, labels, transform=None):
        self.data = data
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        label = self.labels[idx]

        if self.transform:
            sample = self.transform(sample)

        return sample, label

# Create dataset and dataloader
dataset = CustomDataset(data, labels, transform=transform)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)

# Built-in datasets
from torchvision.datasets import MNIST
mnist_dataset = MNIST(root='./data', train=True, download=True,
                     transform=transforms.ToTensor())
```

### Data Transformations

Image and data preprocessing:

```python
import torchvision.transforms as transforms

# Image transformations
transform = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# Custom transforms
class RandomNoise(object):
    def __init__(self, noise_factor=0.1):
        self.noise_factor = noise_factor

    def __call__(self, tensor):
        noise = torch.randn_like(tensor) * self.noise_factor
        return tensor + noise

# Apply transforms
transformed_dataset = CustomDataset(data, labels,
                                   transform=transforms.Compose([
                                       transforms.ToTensor(),
                                       RandomNoise(0.1)
                                   ]))
```

## Advanced Neural Network Architectures

### Convolutional Neural Networks (CNNs)

```python
class CNNModel(nn.Module):
    def __init__(self, num_classes=10):
        super(CNNModel, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x
```

### Recurrent Neural Networks (RNNs)

```python
class RNNModel(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_layers, num_classes):
        super(RNNModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size)
        self.rnn = nn.LSTM(embed_size, hidden_size, num_layers,
                          batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, num_classes)  # *2 for bidirectional

    def forward(self, x):
        embedded = self.embedding(x)
        output, (hidden, cell) = self.rnn(embedded)

        # Use last hidden state
        hidden = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        out = self.fc(hidden)
        return out

# Alternative: GRU
self.rnn = nn.GRU(embed_size, hidden_size, num_layers,
                 batch_first=True, dropout=0.5)
```

### Transformer Architecture

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)

        # Linear transformations and reshape
        Q = self.w_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # Attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.d_k ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attention = torch.softmax(scores, dim=-1)

        # Apply attention to values
        context = torch.matmul(attention, V)

        # Concatenate heads and put through final linear layer
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.w_o(context)
        return output

class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super(TransformerBlock, self).__init__()
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
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # Feed forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))
        return x
```

## Model Saving and Loading

### Checkpoint Management

```python
# Save model checkpoint
def save_checkpoint(model, optimizer, epoch, loss, filepath):
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss
    }
    torch.save(checkpoint, filepath)

# Load model checkpoint
def load_checkpoint(model, optimizer, filepath):
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    epoch = checkpoint['epoch']
    loss = checkpoint['loss']
    return model, optimizer, epoch, loss

# Save best model
best_loss = float('inf')
for epoch in range(num_epochs):
    # Training loop
    train_loss = train_epoch(model, train_loader, optimizer, criterion, device)

    if train_loss < best_loss:
        best_loss = train_loss
        save_checkpoint(model, optimizer, epoch, train_loss, 'best_model.pth')
```

### Model Serialization

```python
# Save entire model
torch.save(model, 'model.pth')
loaded_model = torch.load('model.pth')

# Save state dict only (recommended)
torch.save(model.state_dict(), 'model_state.pth')
model.load_state_dict(torch.load('model_state.pth'))

# Cross-device loading
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.load_state_dict(torch.load('model_state.pth', map_location=device))
```

## Distributed Training

### DataParallel (Single Machine, Multi-GPU)

```python
# Wrap model for multi-GPU
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)

model.to(device)

# Training loop remains the same
# PyTorch automatically splits batch across GPUs
```

### DistributedDataParallel (Multi-Machine)

```python
import torch.distributed as dist
import torch.multiprocessing as mp

def setup_distributed(rank, world_size):
    # Initialize process group
    dist.init_process_group(
        backend='nccl',
        init_method='tcp://127.0.0.1:23456',
        world_size=world_size,
        rank=rank
    )

def cleanup_distributed():
    dist.destroy_process_group()

def train_distributed(rank, world_size, model, train_dataset):
    setup_distributed(rank, world_size)

    # Wrap model
    model = nn.parallel.DistributedDataParallel(model, device_ids=[rank])

    # Create distributed sampler
    train_sampler = torch.utils.data.distributed.DistributedSampler(
        train_dataset, num_replicas=world_size, rank=rank
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                             sampler=train_sampler, num_workers=4)

    # Training loop
    for epoch in range(num_epochs):
        train_sampler.set_epoch(epoch)
        train_epoch(model, train_loader, optimizer, criterion)

    cleanup_distributed()

# Launch distributed training
if __name__ == '__main__':
    world_size = torch.cuda.device_count()
    mp.spawn(train_distributed, args=(world_size,), nprocs=world_size)
```

## Performance Optimization

### JIT Compilation (TorchScript)

```python
# Convert model to TorchScript
model = SimpleNet(784, 128, 10)

# Tracing (recommended for inference)
example_input = torch.randn(1, 784)
traced_model = torch.jit.trace(model, example_input)
traced_model.save('traced_model.pt')

# Scripting (for dynamic control flow)
@torch.jit.script
def scripted_function(x):
    if x.sum() > 0:
        return x * 2
    else:
        return x / 2

# Load and run
loaded_model = torch.jit.load('traced_model.pt')
output = loaded_model(input_tensor)
```

### Memory Optimization

```python
# Gradient accumulation for large batches
accumulation_steps = 4
optimizer.zero_grad()

for i, (inputs, labels) in enumerate(train_loader):
    outputs = model(inputs)
    loss = criterion(outputs, labels) / accumulation_steps
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()

# Memory-efficient evaluation
with torch.no_grad():
    model.eval()
    for inputs, labels in test_loader:
        outputs = model(inputs)
        # No gradients computed

# Gradient checkpointing
from torch.utils.checkpoint import checkpoint

def custom_forward(*inputs):
    return model(*inputs)

output = checkpoint(custom_forward, input1, input2)
```

### Mixed Precision Training

```python
from torch.cuda.amp import autocast, GradScaler

# Initialize scaler
scaler = GradScaler()

model = model.to(device)
optimizer = torch.optim.Adam(model.parameters())

for epoch in range(num_epochs):
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()

        # Automatic mixed precision
        with autocast():
            outputs = model(inputs)
            loss = criterion(outputs, labels)

        # Scale gradients
        scaler.scale(loss).backward()

        # Update weights
        scaler.step(optimizer)
        scaler.update()
```

## Model Interpretability

### Integrated Gradients

```python
def integrated_gradients(inputs, model, target_class, baseline=None, steps=50):
    if baseline is None:
        baseline = torch.zeros_like(inputs)

    # Scale inputs
    alphas = torch.linspace(0, 1, steps).to(inputs.device)
    scaled_inputs = baseline + alphas[:, None, None, None] * (inputs - baseline)

    # Compute gradients
    model.eval()
    gradients = []

    for scaled_input in scaled_inputs:
        scaled_input.requires_grad_(True)
        output = model(scaled_input.unsqueeze(0))
        score = output[0, target_class]
        gradient = torch.autograd.grad(score, scaled_input)[0]
        gradients.append(gradient)

    gradients = torch.stack(gradients)
    avg_gradients = torch.mean(gradients, dim=0)

    # Compute integrated gradients
    integrated_grads = (inputs - baseline) * avg_gradients
    return integrated_grads
```

### SHAP Integration

```python
import shap

# Create explainer
explainer = shap.DeepExplainer(model, background_data)

# Explain predictions
shap_values = explainer.shap_values(test_data)

# Visualize
shap.summary_plot(shap_values, test_data)
shap.waterfall_plot(explainer.expected_value[0], shap_values[0][0], test_data[0])
```

## PyTorch Ecosystem

### torchvision

Computer vision utilities:

```python
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights

# Pre-trained models
model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
model.eval()

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# Datasets
train_dataset = torchvision.datasets.CIFAR10(
    root='./data', train=True, download=True, transform=preprocess
)
```

### torchtext

Natural language processing:

```python
import torchtext
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

# Tokenization
tokenizer = get_tokenizer('basic_english')

# Build vocabulary
def yield_tokens(data_iter):
    for text, _ in data_iter:
        yield tokenizer(text)

vocab = build_vocab_from_iterator(yield_tokens(train_iter), specials=["<unk>"])
vocab.set_default_index(vocab["<unk>"])

# Text processing pipeline
text_pipeline = lambda x: vocab(tokenizer(x))
label_pipeline = lambda x: int(x)

# Create data loader
def collate_batch(batch):
    label_list, text_list, offsets = [], [], [0]
    for (_label, _text) in batch:
        label_list.append(label_pipeline(_label))
        processed_text = torch.tensor(text_pipeline(_text), dtype=torch.int64)
        text_list.append(processed_text)
        offsets.append(processed_text.size(0))

    label_list = torch.tensor(label_list, dtype=torch.int64)
    offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
    text_list = torch.cat(text_list)
    return label_list, text_list, offsets
```

### torchaudio

Audio processing:

```python
import torchaudio
from torchaudio.transforms import MelSpectrogram, AmplitudeToDB

# Audio loading and preprocessing
waveform, sample_rate = torchaudio.load('audio.wav')

# Convert to mel spectrogram
mel_transform = MelSpectrogram(sample_rate=sample_rate, n_mels=128)
mel_spec = mel_transform(waveform)

# Convert to decibels
db_transform = AmplitudeToDB()
db_spec = db_transform(mel_spec)

# Audio datasets
dataset = torchaudio.datasets.LIBRISPEECH('./data', url='train-clean-100', download=True)
```

## Best Practices

### Code Organization

```python
# models/
# ├── __init__.py
# ├── base_model.py
# ├── resnet.py
# └── transformer.py

# utils/
# ├── __init__.py
# ├── data_utils.py
# ├── training_utils.py
# └── metrics.py

# config/
# ├── __init__.py
# └── config.py

# train.py
# evaluate.py
# predict.py
```

### Reproducibility

```python
# Set random seeds
torch.manual_seed(42)
torch.cuda.manual_seed(42)
torch.cuda.manual_seed_all(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

import numpy as np
np.random.seed(42)

import random
random.seed(42)
```

### Error Handling and Debugging

```python
# Gradient clipping to prevent exploding gradients
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# NaN detection
def check_nan(tensor, name):
    if torch.isnan(tensor).any():
        print(f"NaN detected in {name}")
        return True
    return False

# During training
loss.backward()
check_nan(loss, "loss")

for name, param in model.named_parameters():
    if param.grad is not None:
        check_nan(param.grad, f"grad_{name}")
```

### Performance Monitoring

```python
import time
from torch.profiler import profile, record_function, ProfilerActivity

# Simple timing
start_time = time.time()
output = model(input_tensor)
inference_time = time.time() - start_time

# Detailed profiling
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
            record_shapes=True) as prof:
    with record_function("model_inference"):
        output = model(input_tensor)

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

This comprehensive guide covers PyTorch's core concepts, advanced features, ecosystem integrations, and best practices for building scalable deep learning applications.
