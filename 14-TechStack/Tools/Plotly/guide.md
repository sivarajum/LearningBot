# Plotly Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import plotly.graph_objects as go
import plotly.express as px

# Basic plot
fig = px.scatter(df, x='x', y='y', color='category')
fig.show()
```

### 2. **Interactive Features**
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers'))
fig.update_layout(
    title='Interactive Plot',
    xaxis_title='X',
    yaxis_title='Y'
)
fig.show()
```

### 3. **Dash Basics**
```python
from dash import Dash, html, dcc

app = Dash(__name__)
app.layout = html.Div([
    html.H1('Dashboard'),
    dcc.Graph(figure=fig)
])
app.run_server(debug=True)
```

## Level 2 – Production Patterns

### Advanced Dashboards
```python
app.layout = html.Div([
    dcc.Dropdown(id='dropdown', options=[...]),
    dcc.Graph(id='graph'),
    dcc.Interval(id='interval', interval=1000)
])

@app.callback(
    Output('graph', 'figure'),
    Input('dropdown', 'value')
)
def update_graph(value):
    # Update logic
    return figure
```

## Level 3 – Architect Playbook

### Deployment
```python
# Deploy to Dash Enterprise or cloud
# Configure for production
app.run_server(host='0.0.0.0', port=8050, debug=False)
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Create plot | `px.scatter()` | Create plot |
| Show | `fig.show()` | Display plot |
| Export | `fig.write_html()` | Export HTML |
| Run Dash | `app.run_server()` | Start server |

## Checklist Before Production

- [ ] Optimize for performance
- [ ] Set up proper authentication
- [ ] Configure for production
- [ ] Test interactivity
- [ ] Set up monitoring
- [ ] Optimize data loading
