# Seaborn Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import seaborn as sns
import matplotlib.pyplot as plt

# Set style
sns.set_style("whitegrid")

# Basic plot
sns.scatterplot(data=df, x='x', y='y', hue='category')
plt.show()
```

### 2. **Statistical Plots**
```python
# Distribution
sns.displot(data=df, x='value', kde=True)

# Regression
sns.regplot(data=df, x='x', y='y')

# Categorical
sns.boxplot(data=df, x='category', y='value')
```

### 3. **Heatmaps**
```python
correlation = df.corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.show()
```

## Level 2 – Production Patterns

### Advanced Plots
```python
# Pair plot
sns.pairplot(df, hue='category')

# Facet grid
g = sns.FacetGrid(df, col='category')
g.map(sns.scatterplot, 'x', 'y')
```

### Customization
```python
sns.set_palette("husl")
sns.set_context("paper", font_scale=1.5)
```

## Level 3 – Architect Playbook

### Publication Quality
```python
# Configure for publication
sns.set_style("white")
fig, ax = plt.subplots(figsize=(10, 6))
sns.plot(data=df, ax=ax)
plt.savefig('publication_plot.png', dpi=300, bbox_inches='tight')
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Set style | `sns.set_style()` | Set style |
| Plot | `sns.scatterplot()` | Create plot |
| Save | `plt.savefig()` | Save figure |

## Checklist Before Production

- [ ] Choose appropriate plot types
- [ ] Use consistent styling
- [ ] Optimize for publication
- [ ] Test visualizations
- [ ] Document plot choices
