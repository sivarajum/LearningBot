# Jupyter (Tools) Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
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

# Cell 2: Load data
df = pd.read_csv("data.csv")

# Cell 3: Analyze
df.describe()
```

### 3. **Magic Commands**
```python
%time df.groupby('category').sum()
%matplotlib inline
!ls -la
```

## Level 2 – Production Patterns

### Widgets
```python
import ipywidgets as widgets

slider = widgets.IntSlider(value=10, min=0, max=100)
display(slider)
```

### Version Control
```bash
pip install nbdime
nbdime config-git --enable
```

## Level 3 – Architect Playbook

### JupyterHub
```yaml
# docker-compose.yml
services:
  hub:
    image: jupyterhub/jupyterhub
    ports:
      - "8000:8000"
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Start | `jupyter notebook` | Start server |
| Convert | `jupyter nbconvert` | Convert format |
| Install kernel | `python -m ipykernel install` | Add kernel |

## Checklist Before Production

- [ ] Set up proper authentication
- [ ] Configure resource limits
- [ ] Set up version control
- [ ] Implement proper backup
- [ ] Configure sharing
- [ ] Set up monitoring
