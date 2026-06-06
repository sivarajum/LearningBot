# Matplotlib Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import matplotlib.pyplot as plt
import numpy as np

# Basic plot
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
plt.show()
```

### 2. **Multiple Plots**
```python
fig, axes = plt.subplots(2, 2)
axes[0, 0].plot(x, y)
axes[0, 1].scatter(x, y)
plt.show()
```

### 3. **Styling**
```python
plt.plot(x, y, color='blue', linestyle='--', marker='o', label='sin')
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('Plot Title')
plt.legend()
plt.show()
```

## Level 2 – Production Patterns

### Advanced Plots
```python
# Histogram
plt.hist(data, bins=30)

# Bar chart
plt.bar(categories, values)

# Heatmap
import seaborn as sns
sns.heatmap(data, annot=True)
```

### Customization
```python
plt.style.use('seaborn')
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y)
ax.set_xlabel('X', fontsize=12)
ax.set_ylabel('Y', fontsize=12)
plt.tight_layout()
plt.savefig('plot.png', dpi=300)
```

## Level 3 – Architect Playbook

### Publication Quality
```python
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
# Create publication-quality plots
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Plot | `plt.plot()` | Line plot |
| Scatter | `plt.scatter()` | Scatter plot |
| Save | `plt.savefig()` | Save figure |
| Show | `plt.show()` | Display plot |

## Checklist Before Production

- [ ] Use appropriate plot types
- [ ] Set proper figure size
- [ ] Add labels and titles
- [ ] Use consistent styling
- [ ] Save in appropriate format
- [ ] Optimize for publication
