# PyTorch Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import torch
import torch.nn as nn

# Check CUDA
print(torch.cuda.is_available())
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

### 2. **Basic Tensors**
```python
# Create tensors
x = torch.tensor([1, 2, 3])
y = torch.randn(3, 4)
z = torch.zeros(2, 3)

# Operations
a = torch.randn(3, 4)
b = torch.randn(3, 4)
c = a + b
d = torch.matmul(a, b.t())
```

### 3. **Simple Neural Network**
```python
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

model = Net().to(device)
```

## Level 2 – Production Patterns

### Training Loop
```python
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
```

### Data Loading
```python
from torch.utils.data import Dataset, DataLoader

class MyDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

dataset = MyDataset(X, y)
loader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Transfer Learning
```python
import torchvision.models as models

# Load pretrained model
model = models.resnet18(pretrained=True)

# Freeze layers
for param in model.parameters():
    param.requires_grad = False

# Replace classifier
model.fc = nn.Linear(model.fc.in_features, num_classes)
```

## Level 3 – Architect Playbook

### Distributed Training
```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel

# Initialize
dist.init_process_group(backend='nccl')
model = DistributedDataParallel(model)

# Training with DDP
# Run with: torchrun --nproc_per_node=4 train.py
```

### Model Optimization
```python
# TorchScript
model_scripted = torch.jit.script(model)
model_scripted.save('model.pt')

# ONNX export
torch.onnx.export(model, dummy_input, "model.onnx")
```

### Production Deployment
```python
# TorchServe
torch-model-archiver \
    --model-name mymodel \
    --version 1.0 \
    --serialized-file model.pth \
    --handler handler.py

torchserve --start --model-store model-store --models mymodel
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Save model | `torch.save(model.state_dict(), 'model.pth')` | Save weights |
| Load model | `model.load_state_dict(torch.load('model.pth'))` | Load weights |
| Export ONNX | `torch.onnx.export()` | Export to ONNX |
| Profile | `torch.profiler` | Profile model |

## Checklist Before Production

- [ ] Implement proper data loading
- [ ] Set up distributed training if needed
- [ ] Optimize model (quantization, pruning)
- [ ] Set up model versioning
- [ ] Implement proper logging
- [ ] Set up monitoring
- [ ] Configure deployment pipeline
- [ ] Test model performance
