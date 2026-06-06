# Keras: Interview Questions & Answers

## Beginner Level

### Q1: What is Keras and how does it relate to TensorFlow?
**A:** Keras is a high-level deep learning API. Since TensorFlow 2.0, it's the official high-level API (`tf.keras`). With Keras 3.0, it became multi-backend — supporting TensorFlow, JAX, and PyTorch.

```python
# Keras 3: choose backend
import os
os.environ["KERAS_BACKEND"] = "jax"  # or "tensorflow" or "torch"
import keras

model = keras.Sequential([keras.layers.Dense(10)])  # Works on any backend
```

### Q2: Explain Sequential vs Functional vs Subclassing API.
**A:**

| API | When to Use | Complexity |
|-----|-------------|-----------|
| Sequential | Linear stack of layers | Simplest |
| Functional | Multi-input/output, shared layers, skip connections | Medium |
| Subclassing | Custom forward pass, dynamic behavior | Most flexible |

```python
# Sequential: simple linear model
model = keras.Sequential([layers.Dense(64), layers.Dense(10)])

# Functional: ResNet-style skip connections
inputs = keras.Input(shape=(64,))
x = layers.Dense(64, activation="relu")(inputs)
x = layers.Add()([x, inputs])  # Skip connection
model = keras.Model(inputs, x)

# Subclassing: dynamic behavior
class MyModel(keras.Model):
    def call(self, x, training=False):
        if training:
            x = self.dropout(x)
        return self.dense(x)
```

### Q3: What are callbacks and name 3 essential ones?
**A:** Callbacks are hooks that execute during training at specific points (epoch start/end, batch start/end).

1. **EarlyStopping** — Stop when val_loss stops improving (patience=5 means wait 5 epochs)
2. **ModelCheckpoint** — Save best model weights during training
3. **ReduceLROnPlateau** — Reduce learning rate when loss plateaus

```python
callbacks = [
    keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
    keras.callbacks.ModelCheckpoint("best.keras", save_best_only=True),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
]
```

### Q4: How do you handle overfitting in Keras?
**A:** Multiple strategies:

| Technique | Implementation |
|-----------|---------------|
| Dropout | `layers.Dropout(0.3)` — randomly zero out 30% of neurons |
| L2 regularization | `layers.Dense(64, kernel_regularizer=keras.regularizers.l2(0.01))` |
| Early stopping | `EarlyStopping(patience=5)` |
| Data augmentation | `layers.RandomFlip()`, `layers.RandomRotation(0.1)` |
| Batch normalization | `layers.BatchNormalization()` |
| Reduce model size | Fewer layers/units |

### Q5: What loss functions do you use for classification vs regression?
**A:**

| Task | Loss Function | Output Activation |
|------|--------------|-------------------|
| Binary classification | `binary_crossentropy` | `sigmoid` |
| Multi-class (int labels) | `sparse_categorical_crossentropy` | `softmax` |
| Multi-class (one-hot) | `categorical_crossentropy` | `softmax` |
| Regression | `mse` or `mae` | None (linear) |
| Regression with outliers | `huber` | None |

---

## Intermediate Level

### Q6: How do you implement a custom training loop in Keras?
**A:**

```python
model = build_model()
optimizer = keras.optimizers.Adam(1e-3)
loss_fn = keras.losses.MeanSquaredError()
train_metric = keras.metrics.MeanAbsoluteError()

for epoch in range(epochs):
    for x_batch, y_batch in train_dataset:
        with tf.GradientTape() as tape:
            preds = model(x_batch, training=True)
            loss = loss_fn(y_batch, preds)

        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))
        train_metric.update_state(y_batch, preds)

    print(f"Epoch {epoch}: MAE = {train_metric.result():.4f}")
    train_metric.reset_state()
```

Use custom loops when: you need gradient accumulation, multi-loss weighting, GANs, or non-standard training procedures.

### Q7: How do you build a multi-input model for stock prediction?
**A:**

```python
# Input 1: OHLCV time series (60 days × 5 features)
ohlcv_input = keras.Input(shape=(60, 5), name="ohlcv")
x1 = layers.LSTM(64, return_sequences=True)(ohlcv_input)
x1 = layers.LSTM(32)(x1)

# Input 2: Technical indicators (scalar features)
indicator_input = keras.Input(shape=(20,), name="indicators")
x2 = layers.Dense(32, activation="relu")(indicator_input)

# Input 3: Sentiment score
sentiment_input = keras.Input(shape=(1,), name="sentiment")

# Merge all
merged = layers.Concatenate()([x1, x2, sentiment_input])
x = layers.Dense(64, activation="relu")(merged)
x = layers.Dropout(0.3)(x)

# Outputs
price = layers.Dense(1, name="price")(x)
direction = layers.Dense(1, activation="sigmoid", name="direction")(x)

model = keras.Model(
    inputs=[ohlcv_input, indicator_input, sentiment_input],
    outputs=[price, direction],
)
model.compile(
    optimizer="adam",
    loss={"price": "mse", "direction": "binary_crossentropy"},
    loss_weights={"price": 1.0, "direction": 0.5},
    metrics={"direction": "accuracy"},
)
```

### Q8: How do you use tf.data for efficient data loading?
**A:**

```python
import tensorflow as tf

# From numpy arrays
dataset = tf.data.Dataset.from_tensor_slices((features, labels))

# Pipeline
dataset = (
    dataset
    .shuffle(buffer_size=10000)       # Randomize order
    .batch(32)                         # Mini-batches
    .prefetch(tf.data.AUTOTUNE)       # Overlap CPU prep with GPU compute
    .cache()                           # Cache in memory after first epoch
)

# From CSV files (large data)
dataset = tf.data.experimental.make_csv_dataset(
    "large_data.csv", batch_size=32, label_name="target"
)

# From generator (custom data)
def data_generator():
    for symbol in symbols:
        x, y = load_symbol_data(symbol)
        yield x, y

dataset = tf.data.Dataset.from_generator(
    data_generator, output_signature=(
        tf.TensorSpec(shape=(60, 5), dtype=tf.float32),
        tf.TensorSpec(shape=(), dtype=tf.float32),
    )
)
```

### Q9: How do you implement mixed precision training?
**A:** Mixed precision uses float16 for computation and float32 for accumulation — ~2x speedup on modern GPUs.

```python
# Global policy (easiest)
keras.mixed_precision.set_global_policy("mixed_float16")

model = keras.Sequential([
    layers.Dense(256, activation="relu"),   # Computes in float16
    layers.Dense(10),                        # Computes in float16
])

# IMPORTANT: Loss scaling happens automatically with model.fit()
# For custom loops, wrap optimizer:
optimizer = keras.optimizers.Adam(1e-3)
# Keras 3 handles loss scaling internally

# The final output layer should stay float32 for numerical stability
outputs = layers.Dense(10, dtype="float32")(x)
```

---

## Advanced Level

### Q10: Design a production Keras model serving pipeline.
**A:**

```python
# 1. Train and save
model.fit(train_ds, validation_data=val_ds, epochs=50, callbacks=callbacks)
model.save("stock_predictor.keras")

# 2. Export as SavedModel for TF Serving
model.export("serving/stock_predictor/1/")

# 3. Docker compose for TF Serving
# docker-compose.yml:
# services:
#   tf_serving:
#     image: tensorflow/serving
#     ports: ["8501:8501"]
#     volumes: ["./serving:/models"]
#     environment:
#       MODEL_NAME: stock_predictor

# 4. Client
import requests
import numpy as np

data = {"instances": [{"ohlcv": ohlcv.tolist(), "indicators": ind.tolist()}]}
response = requests.post("http://localhost:8501/v1/models/stock_predictor:predict", json=data)
prediction = response.json()["predictions"][0]

# 5. Monitoring
# - Track prediction latency
# - Monitor input drift (compare training vs serving distributions)
# - A/B test model versions via TF Serving's model versioning
```

### Q11: How do you implement a custom Keras layer with trainable weights?
**A:**

```python
class TemporalAttention(keras.layers.Layer):
    """Attention over time steps for sequence models."""
    def __init__(self, units, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        # input_shape: (batch, timesteps, features)
        feature_dim = input_shape[-1]
        self.W = self.add_weight(
            name="attn_weight", shape=(feature_dim, self.units),
            initializer="glorot_uniform", trainable=True,
        )
        self.V = self.add_weight(
            name="attn_v", shape=(self.units, 1),
            initializer="glorot_uniform", trainable=True,
        )

    def call(self, inputs):
        # Score each timestep
        score = keras.ops.tanh(keras.ops.matmul(inputs, self.W))    # (B, T, units)
        weights = keras.ops.softmax(keras.ops.matmul(score, self.V), axis=1)  # (B, T, 1)
        context = keras.ops.sum(inputs * weights, axis=1)  # (B, features)
        return context

    def get_config(self):
        config = super().get_config()
        config.update({"units": self.units})
        return config
```

### Q12: How do you handle class imbalance in Keras?
**A:**

```python
import numpy as np

# Method 1: Class weights (most common)
from sklearn.utils.class_weight import compute_class_weight
weights = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
class_weights = dict(enumerate(weights))
model.fit(X_train, y_train, class_weight=class_weights)

# Method 2: Sample weights (per-sample granularity)
sample_weights = np.where(y_train == 1, 5.0, 1.0)  # Upweight rare class
model.fit(X_train, y_train, sample_weight=sample_weights)

# Method 3: Focal loss (for extreme imbalance)
class FocalLoss(keras.losses.Loss):
    def __init__(self, gamma=2.0, alpha=0.25):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha

    def call(self, y_true, y_pred):
        y_pred = keras.ops.clip(y_pred, 1e-7, 1 - 1e-7)
        pt = y_true * y_pred + (1 - y_true) * (1 - y_pred)
        loss = -self.alpha * (1 - pt) ** self.gamma * keras.ops.log(pt)
        return keras.ops.mean(loss)

# Method 4: Oversampling with tf.data
pos_ds = train_ds.filter(lambda x, y: y == 1)
neg_ds = train_ds.filter(lambda x, y: y == 0)
balanced_ds = tf.data.Dataset.sample_from_datasets([pos_ds, neg_ds], weights=[0.5, 0.5])
```
