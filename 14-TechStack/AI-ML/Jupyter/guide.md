# Jupyter Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Jupyter
pip install jupyter

# Start notebook
jupyter notebook

# Or JupyterLab
pip install jupyterlab
jupyter lab
```

### 2. **Basic Usage**
```python
# Cell 1: Import
import pandas as pd
import numpy as np

# Cell 2: Load data
df = pd.read_csv("data.csv")

# Cell 3: Explore
df.head()
df.describe()

# Cell 4: Visualize
import matplotlib.pyplot as plt
df.plot()
plt.show()
```

### 3. **Magic Commands**
```python
# Time execution
%time df.groupby('category').sum()

# Profile code
%prun my_function()

# Run shell command
!ls -la

# Load extension
%load_ext autoreload
%autoreload 2
```

## Level 2 – Production Patterns

### Widgets
```python
import ipywidgets as widgets
from IPython.display import display

slider = widgets.IntSlider(value=10, min=0, max=100)
text = widgets.Text(value='Hello')

def update_text(change):
    text.value = f"Value: {change.new}"

slider.observe(update_text, names='value')
display(slider, text)
```

### Version Control
```bash
# Install nbdime
pip install nbdime

# Configure Git
nbdime config-git --enable --global

# Diff notebooks
nbdiff notebook1.ipynb notebook2.ipynb
```

### Sharing
```bash
# Convert to HTML
jupyter nbconvert notebook.ipynb --to html

# Convert to PDF
jupyter nbconvert notebook.ipynb --to pdf

# Publish to Jupyter Book
jupyter-book build mybook/
```

## Level 3 – Architect Playbook

### JupyterHub
```yaml
# docker-compose.yml
version: '3'
services:
  hub:
    image: jupyterhub/jupyterhub
    volumes:
      - ./jupyterhub_config.py:/srv/jupyterhub/jupyterhub_config.py
    ports:
      - "8000:8000"
```

### Custom Kernels
```bash
# Install kernel
python -m ipykernel install --user --name myenv --display-name "Python (myenv)"

# List kernels
jupyter kernelspec list
```

### Production Deployment
```dockerfile
FROM jupyter/scipy-notebook
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY notebooks/ /home/jovyan/work/
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Start notebook | `jupyter notebook` | Start server |
| Start lab | `jupyter lab` | Start JupyterLab |
| List kernels | `jupyter kernelspec list` | View kernels |
| Convert | `jupyter nbconvert` | Convert format |
| Install extension | `jupyter nbextension install` | Install extension |

## Checklist Before Production

- [ ] Set up proper authentication
- [ ] Configure resource limits
- [ ] Set up version control
- [ ] Implement proper backup
- [ ] Configure sharing and collaboration
- [ ] Set up monitoring
- [ ] Optimize performance
- [ ] Set up proper security
