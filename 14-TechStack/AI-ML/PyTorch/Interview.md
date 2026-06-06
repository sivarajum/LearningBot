# PyTorch Interview Questions & Answers

## Core PyTorch Fundamentals

### Q1: What is PyTorch and how does it differ from TensorFlow?

**Answer:**
PyTorch is an open-source machine learning framework based on the Torch library, primarily developed by Facebook's AI Research lab (FAIR). Key differences from TensorFlow:

**Dynamic vs Static Graphs:**
- PyTorch: Dynamic computation graph (eager execution) - builds graph on-the-fly during execution
- TensorFlow (v1): Static computation graph - define graph first, then execute

**Ease of Use:**
- PyTorch: More Pythonic, easier debugging, intuitive for researchers
- TensorFlow: More production-focused, better for deployment

**Community:**
- PyTorch: Strong research community, especially in academia
- TensorFlow: Larger enterprise adoption, more production tools

**Code Example:**
```python
# PyTorch - Dynamic
x = torch.randn(3, 3)
y = torch.randn(3, 3)
z = x + y  # Graph built here

# TensorFlow v1 - Static
x = tf.placeholder(tf.float32, [3, 3])
y = tf.placeholder(tf.float32, [3, 3])
z = tf.add(x, y)  # Graph defined
# Then execute in session
```

### Q2: Explain PyTorch's autograd system.

**Answer:**
Autograd is PyTorch's automatic differentiation engine that computes gradients automatically. Key components:

**Function Objects:** Each operation creates a Function object that stores forward computation and implements backward pass.

**Computational Graph:** Dynamic graph where nodes are tensors, edges are functions.

**Gradient Computation:** Uses chain rule to compute gradients backward through the graph.

**Key Features:**
- Automatic differentiation
- Dynamic graph construction
- Memory efficient (gradients freed after use)
- Supports higher-order derivatives

**Example:**
```python
x = torch.tensor(2.0, requires_grad=True)
y = x ** 2 + 3 * x + 1
y.backward()  # Computes dy/dx
print(x.grad)  # Output: 7.0 (2*2 + 3)
```

### Q3: What are tensors in PyTorch and how do they differ from NumPy arrays?

**Answer:**
Tensors are multi-dimensional arrays similar to NumPy arrays but with additional capabilities:

**Similarities:**
- Multi-dimensional arrays
- Same mathematical operations
- Broadcasting support

**Differences:**
- GPU acceleration support
- Automatic differentiation
- Gradient computation
- Device management (CPU/GPU)

**Key Methods:**
```python
# Creation
t = torch.tensor([1, 2, 3])  # From list
t = torch.randn(3, 3)         # Random normal
t = torch.zeros(2, 3)         # Zeros

# Device management
t = t.to('cuda')              # Move to GPU
t = t.cpu()                   # Move to CPU

# Gradient tracking
t.requires_grad_(True)        # Enable gradients
```

## Neural Networks

### Q4: How do you create a neural network in PyTorch?

**Answer:**
Neural networks are created by subclassing `nn.Module`. Key components:

**Required Methods:**
- `__init__`: Define layers
- `forward`: Define forward pass

**Best Practices:**
- Use `nn.Sequential` for simple networks
- Proper weight initialization
- Device handling

**Example:**
```python
class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

# Usage
model = SimpleNN(784, 128, 10)
```

### Q5: Explain the difference between `torch.nn` and `torch.nn.functional`.

**Answer:**
Both provide neural network operations but serve different purposes:

**torch.nn (Modules):**
- Stateful layers (have parameters)
- Maintain internal state
- Used in `nn.Module` subclasses
- Example: `nn.Linear`, `nn.Conv2d`

**torch.nn.functional (Functions):**
- Stateless operations
- No learnable parameters
- Pure functions
- Example: `F.relu`, `F.conv2d`

**When to use which:**
- Use `nn` modules in model definitions
- Use `functional` for custom layers or when you need more control

**Example:**
```python
# Using modules
self.conv = nn.Conv2d(3, 64, 3)
out = self.conv(x)

# Using functional
out = F.conv2d(x, weight, bias)
```

### Q6: How does batch normalization work in PyTorch?

**Answer:**
Batch normalization normalizes layer inputs across a mini-batch to stabilize training:

**Formula:**
```
μ = (1/m) Σ x_i    # Batch mean
σ² = (1/m) Σ (x_i - μ)²    # Batch variance
x̂ = (x - μ) / √(σ² + ε)   # Normalize
y = γ * x̂ + β    # Scale and shift
```

**Benefits:**
- Faster convergence
- Higher learning rates possible
- Regularization effect
- Reduces internal covariate shift

**PyTorch Implementation:**
```python
# During training
bn = nn.BatchNorm2d(64)
bn.train()  # Uses batch statistics

# During inference
bn.eval()   # Uses running statistics
```

## Training and Optimization

### Q7: Explain the training loop in PyTorch.

**Answer:**
Standard training loop involves several key steps:

**Basic Training Loop:**
```python
for epoch in range(num_epochs):
    for batch in dataloader:
        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, targets)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

**Key Components:**
- **Data Loading:** Use `DataLoader` for batching
- **Forward Pass:** Model prediction
- **Loss Calculation:** Compare prediction vs target
- **Gradient Zeroing:** Clear previous gradients
- **Backward Pass:** Compute gradients
- **Parameter Update:** Apply optimizer

### Q8: What optimizers are available in PyTorch and when to use them?

**Answer:**

**SGD (Stochastic Gradient Descent):**
```python
optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
```
- Simple, well-understood
- Good for convex problems
- Use with momentum for acceleration

**Adam (Adaptive Moment Estimation):**
```python
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.999))
```
- Adaptive learning rates
- Good default choice
- Works well for sparse gradients

**AdamW:**
```python
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
```
- Decoupled weight decay
- Better generalization than Adam
- Preferred for modern architectures

**RMSprop:**
```python
optimizer = torch.optim.RMSprop(model.parameters(), lr=0.001, alpha=0.99)
```
- Good for RNNs
- Adapts learning rate based on gradient magnitude

### Q9: How do you handle overfitting in PyTorch?

**Answer:**
Multiple techniques to prevent overfitting:

**Regularization Techniques:**
```python
# L2 Regularization (Weight Decay)
optimizer = torch.optim.Adam(model.parameters(), weight_decay=1e-4)

# Dropout
self.dropout = nn.Dropout(p=0.5)

# Batch Normalization
self.bn = nn.BatchNorm1d(hidden_size)
```

**Data Augmentation:**
```python
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor()
])
```

**Early Stopping:**
```python
best_loss = float('inf')
patience = 10
counter = 0

for epoch in range(max_epochs):
    # Training
    train_loss = train_epoch(model, train_loader)

    # Validation
    val_loss = validate_epoch(model, val_loader)

    if val_loss < best_loss:
        best_loss = val_loss
        counter = 0
        torch.save(model.state_dict(), 'best_model.pth')
    else:
        counter += 1
        if counter >= patience:
            break
```

## Data Handling

### Q10: How do you create custom datasets in PyTorch?

**Answer:**
Create custom datasets by subclassing `torch.utils.data.Dataset`:

**Required Methods:**
- `__len__`: Return dataset size
- `__getitem__`: Return single sample

**Example:**
```python
class CustomDataset(Dataset):
    def __init__(self, data_paths, transform=None):
        self.data_paths = data_paths
        self.transform = transform

    def __len__(self):
        return len(self.data_paths)

    def __getitem__(self, idx):
        # Load data
        image = Image.open(self.data_paths[idx])
        label = self.get_label(self.data_paths[idx])

        # Apply transforms
        if self.transform:
            image = self.transform(image)

        return image, label
```

**DataLoader Usage:**
```python
dataset = CustomDataset(data_paths, transform=transform)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)
```

### Q11: What is the difference between `Dataset` and `DataLoader`?

**Answer:**

**Dataset:**
- Abstract class for data access
- Implements `__len__` and `__getitem__`
- Loads individual samples
- No batching or shuffling

**DataLoader:**
- Wraps Dataset for batching
- Handles shuffling, sampling
- Supports parallel data loading
- Memory efficient with iterators

**Key Parameters:**
```python
dataloader = DataLoader(
    dataset=dataset,
    batch_size=32,           # Batch size
    shuffle=True,            # Shuffle data
    num_workers=4,           # Parallel workers
    pin_memory=True,         # Faster GPU transfer
    drop_last=True           # Drop incomplete batches
)
```

## Advanced Topics

### Q12: How does PyTorch handle GPU training?

**Answer:**
PyTorch provides seamless GPU support:

**Device Management:**
```python
# Check GPU availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Move model to GPU
model = model.to(device)

# Move data to GPU
inputs, targets = inputs.to(device), targets.to(device)
```

**Multi-GPU Training:**
```python
# DataParallel (Single machine, multiple GPUs)
model = nn.DataParallel(model)

# DistributedDataParallel (Multiple machines)
model = nn.parallel.DistributedDataParallel(model)
```

**Memory Management:**
```python
# Clear cache
torch.cuda.empty_cache()

# Memory summary
print(torch.cuda.memory_summary())
```

### Q13: Explain TorchScript and when to use it.

**Answer:**
TorchScript converts PyTorch models to a serializable format for production:

**Two Ways to Convert:**
```python
# Tracing (Recommended for inference)
model.eval()
traced_model = torch.jit.trace(model, example_input)

# Scripting (Handles control flow)
scripted_model = torch.jit.script(model)
```

**Benefits:**
- Performance optimization
- C++ deployment
- Model serialization
- Removes Python dependency

**Use Cases:**
- Production deployment
- Mobile/embedded devices
- Performance-critical applications

### Q14: How do you debug PyTorch models?

**Answer:**
Multiple debugging techniques:

**Gradient Checking:**
```python
from torch.autograd import gradcheck

def test_function(x):
    return x ** 2

x = torch.randn(3, 3, requires_grad=True)
assert gradcheck(test_function, x)
```

**Hook Functions:**
```python
def hook_fn(module, input, output):
    print(f"Module: {module.__class__.__name__}")
    print(f"Input shape: {input[0].shape}")
    print(f"Output shape: {output.shape}")

handle = model.layer.register_forward_hook(hook_fn)
```

**TensorBoard Integration:**
```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter()
writer.add_scalar('Loss/train', train_loss, epoch)
writer.add_graph(model, input_tensor)
```

**Common Issues:**
- Vanishing/exploding gradients
- NaN/inf values
- Incorrect tensor shapes
- Device mismatches

### Q15: How do you implement transfer learning in PyTorch?

**Answer:**
Transfer learning reuses pre-trained models:

**Feature Extraction:**
```python
# Load pre-trained model
model = torchvision.models.resnet50(pretrained=True)

# Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# Replace classifier
model.fc = nn.Linear(2048, num_classes)

# Only train classifier
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
```

**Fine-tuning:**
```python
# Unfreeze some layers
for param in model.layer4.parameters():
    param.requires_grad = True

# Lower learning rate for pre-trained layers
optimizer = torch.optim.Adam([
    {'params': model.layer4.parameters(), 'lr': 1e-4},
    {'params': model.fc.parameters(), 'lr': 1e-3}
])
```

**Best Practices:**
- Use appropriate pre-trained models
- Freeze early layers, fine-tune later layers
- Use smaller learning rates for pre-trained weights
- Data augmentation crucial

## Performance and Optimization

### Q16: How do you optimize PyTorch model performance?

**Answer:**
Multiple optimization strategies:

**Mixed Precision Training:**
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    with autocast():
        outputs = model(inputs)
        loss = criterion(outputs, targets)

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

**Model Quantization:**
```python
# Dynamic quantization
quantized_model = torch.quantization.quantize_dynamic(
    model, {nn.Linear}, dtype=torch.qint8
)
```

**Just-In-Time (JIT) Compilation:**
```python
# Compile model
compiled_model = torch.compile(model)

# Or use TorchScript
scripted_model = torch.jit.script(model)
```

### Q17: Explain gradient accumulation in PyTorch.

**Answer:**
Gradient accumulation simulates larger batch sizes with limited GPU memory:

**Implementation:**
```python
accumulation_steps = 4
optimizer.zero_grad()

for i, (inputs, targets) in enumerate(dataloader):
    outputs = model(inputs)
    loss = criterion(outputs, targets) / accumulation_steps
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**Benefits:**
- Effective batch size = batch_size × accumulation_steps
- Memory efficient
- Better gradient estimates

### Q18: How do you handle imbalanced datasets in PyTorch?

**Answer:**
Several techniques for imbalanced data:

**Weighted Loss:**
```python
# Calculate class weights
class_counts = torch.bincount(labels)
class_weights = 1.0 / class_counts.float()
class_weights = class_weights / class_weights.sum()

# Weighted loss
criterion = nn.CrossEntropyLoss(weight=class_weights)
```

**Weighted Sampling:**
```python
from torch.utils.data import WeightedRandomSampler

# Sample weights for each class
sample_weights = class_weights[labels]

# Create sampler
sampler = WeightedRandomSampler(sample_weights, len(sample_weights))
dataloader = DataLoader(dataset, sampler=sampler, batch_size=batch_size)
```

**Oversampling/Undersampling:**
```python
# Oversample minority class
majority_count = (labels == 0).sum()
minority_count = (labels == 1).sum()
oversample_ratio = majority_count // minority_count

# Custom dataset with oversampling logic
```

## Common Pitfalls and Best Practices

### Q19: What are common PyTorch mistakes and how to avoid them?

**Answer:**

**Gradient Accumulation Without Proper Zeroing:**
```python
# Wrong
for batch in dataloader:
    loss = model(batch)
    loss.backward()  # Gradients accumulate across batches!
    optimizer.step()

# Correct
for batch in dataloader:
    optimizer.zero_grad()
    loss = model(batch)
    loss.backward()
    optimizer.step()
```

**In-place Operations on Tensors with requires_grad:**
```python
# Wrong
x = torch.tensor(1.0, requires_grad=True)
x.add_(1)  # In-place operation breaks gradient flow

# Correct
x = torch.tensor(1.0, requires_grad=True)
x = x + 1  # Out-of-place operation
```

**Device Mismatches:**
```python
# Wrong
model = model.cuda()
inputs = inputs  # Still on CPU
outputs = model(inputs)  # Error!

# Correct
device = torch.device('cuda')
model = model.to(device)
inputs = inputs.to(device)
```

### Q20: How do you save and load PyTorch models?

**Answer:**
Multiple ways to save/load models:

**Save/Load State Dict (Recommended):**
```python
# Save
torch.save(model.state_dict(), 'model.pth')

# Load
model = MyModel()
model.load_state_dict(torch.load('model.pth'))
model.eval()
```

**Save/Load Entire Model:**
```python
# Save
torch.save(model, 'model.pth')

# Load
model = torch.load('model.pth')
```

**Checkpointing:**
```python
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}

torch.save(checkpoint, 'checkpoint.pth')

# Load checkpoint
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
```

**Best Practices:**
- Save state_dict, not entire model
- Include optimizer state for resuming training
- Use .pth or .pt extensions
- Save to CPU format for portability

## Production and Deployment

### Q21: How do you deploy PyTorch models to production?

**Answer:**
Multiple deployment strategies:

**TorchServe:**
```python
# Create model archive
torch-model-archiver --model-name mymodel \
    --version 1.0 \
    --model-file model.py \
    --serialized-file model.pth \
    --handler handler.py

# Serve model
torchserve --start --model-store model_store --models mymodel=mymodel.mar
```

**ONNX Export:**
```python
# Export to ONNX
torch.onnx.export(model, dummy_input, "model.onnx")

# Load with ONNX Runtime
import onnxruntime as ort
ort_session = ort.InferenceSession("model.onnx")
```

**Flask/FastAPI API:**
```python
from fastapi import FastAPI, File

app = FastAPI()
model = load_model()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = preprocess_image(file)
    with torch.no_grad():
        prediction = model(image)
    return {"prediction": prediction.tolist()}
```

### Q22: How do you monitor PyTorch model performance in production?

**Answer:**
Comprehensive monitoring strategies:

**Model Metrics:**
```python
# Prediction latency
start_time = time.time()
with torch.no_grad():
    prediction = model(input)
latency = time.time() - start_time

# Model accuracy drift
# Compare predictions with ground truth periodically
```

**System Metrics:**
```python
# GPU utilization
gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()

# CPU usage, memory usage
import psutil
cpu_percent = psutil.cpu_percent()
memory_percent = psutil.virtual_memory().percent
```

**Logging and Alerting:**
```python
import logging

# Log predictions and metrics
logging.info(f"Prediction: {prediction}, Latency: {latency}")

# Alert on anomalies
if latency > threshold:
    alert_system.send_alert("High latency detected")
```

**A/B Testing:**
```python
# Route traffic between model versions
if random.random() < 0.5:
    prediction = model_v1(input)
else:
    prediction = model_v2(input)

# Compare performance metrics
```

This comprehensive set of interview questions covers PyTorch fundamentals, advanced concepts, best practices, and real-world applications. Focus on understanding core concepts rather than memorizing syntax, as PyTorch evolves rapidly.
