# Keras: Complete Guide

## 1. What is Keras?

Keras is a high-level deep learning API that runs on top of TensorFlow, JAX, or PyTorch. It provides a clean, Pythonic interface for building and training neural networks with minimal boilerplate.

**Key points:**
- Default high-level API for TensorFlow (tf.keras)
- Multi-backend since Keras 3.0 (TensorFlow, JAX, PyTorch)
- Focus on developer experience and rapid prototyping
- Production-ready with TensorFlow Serving, TF Lite, TF.js

---

## 2. Core Concepts

### Sequential API (Simple Models)
```python
import keras
from keras import layers

model = keras.Sequential([
    layers.Input(shape=(784,)),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.2),
    layers.Dense(10, activation="softmax"),
])
model.summary()
```

### Functional API (Complex Models)
```python
inputs = keras.Input(shape=(784,))
x = layers.Dense(256, activation="relu")(inputs)
x = layers.Dropout(0.3)(x)
x = layers.Dense(128, activation="relu")(x)
outputs = layers.Dense(10, activation="softmax")(x)
model = keras.Model(inputs=inputs, outputs=outputs)
```

### Subclassing API (Full Control)
```python
class StockPredictor(keras.Model):
    def __init__(self):
        super().__init__()
        self.lstm = layers.LSTM(128, return_sequences=True)
        self.lstm2 = layers.LSTM(64)
        self.dense = layers.Dense(32, activation="relu")
        self.output_layer = layers.Dense(1)

    def call(self, inputs, training=False):
        x = self.lstm(inputs)
        x = self.lstm2(x)
        x = self.dense(x)
        return self.output_layer(x)
```

---

## 3. Key Features

### Layers
| Layer | Purpose | Example |
|-------|---------|---------|
| `Dense` | Fully connected | Classification, regression |
| `Conv2D` | Image features | Image classification |
| `LSTM` | Sequence modeling | Time series, text |
| `GRU` | Faster LSTM variant | Stock price prediction |
| `Attention` | Self-attention | Transformer blocks |
| `Embedding` | Token → vector | NLP preprocessing |
| `BatchNormalization` | Stabilize training | Deep networks |
| `Dropout` | Regularization | Prevent overfitting |

### Losses
```python
# Classification
keras.losses.SparseCategoricalCrossentropy()   # Integer labels
keras.losses.BinaryCrossentropy()              # Binary
keras.losses.CategoricalCrossentropy()         # One-hot labels

# Regression
keras.losses.MeanSquaredError()                # Stock price prediction
keras.losses.MeanAbsoluteError()               # Robust to outliers
keras.losses.Huber(delta=1.0)                  # Hybrid MSE/MAE
```

### Optimizers
```python
keras.optimizers.Adam(learning_rate=1e-3)      # Default choice
keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=0.01)  # With L2 reg
keras.optimizers.SGD(learning_rate=0.01, momentum=0.9)         # Classic
keras.optimizers.RMSprop(learning_rate=1e-3)   # RNN-friendly
```

---

## 4. Installation

```bash
# Keras 3 (multi-backend)
pip install keras

# With TensorFlow backend (most common)
pip install tensorflow keras

# With JAX backend
pip install jax jaxlib keras
export KERAS_BACKEND=jax

# With PyTorch backend
pip install torch keras
export KERAS_BACKEND=torch

# Verify
python -c "import keras; print(keras.__version__); print(keras.backend.backend())"
```

---

## 5. Beginner Examples

### Image Classification (MNIST)
```python
import keras
from keras import layers
from keras.datasets import mnist

# Load data
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(-1, 28, 28, 1).astype("float32") / 255.0
x_test = x_test.reshape(-1, 28, 28, 1).astype("float32") / 255.0

# Build model
model = keras.Sequential([
    layers.Input(shape=(28, 28, 1)),
    layers.Conv2D(32, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(10, activation="softmax"),
])

# Compile & train
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
model.fit(x_train, y_train, epochs=5, batch_size=32, validation_split=0.1)
model.evaluate(x_test, y_test)
```

### Binary Classification (Tabular)
```python
model = keras.Sequential([
    layers.Input(shape=(num_features,)),
    layers.Dense(64, activation="relu"),
    layers.BatchNormalization(),
    layers.Dense(32, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(1, activation="sigmoid"),
])
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy", "AUC"])
```

---

## 6. Intermediate Patterns

### Callbacks
```python
callbacks = [
    keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6
    ),
    keras.callbacks.ModelCheckpoint(
        "best_model.keras", save_best_only=True, monitor="val_loss"
    ),
    keras.callbacks.TensorBoard(log_dir="./logs"),
    keras.callbacks.CSVLogger("training_log.csv"),
]

model.fit(x_train, y_train, epochs=100, callbacks=callbacks, validation_split=0.2)
```

### Custom Training Loop
```python
optimizer = keras.optimizers.Adam(1e-3)
loss_fn = keras.losses.MeanSquaredError()

@tf.function
def train_step(x, y):
    with tf.GradientTape() as tape:
        predictions = model(x, training=True)
        loss = loss_fn(y, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    return loss

for epoch in range(epochs):
    for x_batch, y_batch in train_dataset:
        loss = train_step(x_batch, y_batch)
```

### Data Pipeline (tf.data)
```python
import tensorflow as tf

dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
dataset = (
    dataset
    .shuffle(10000)
    .batch(32)
    .prefetch(tf.data.AUTOTUNE)
    .cache()
)
model.fit(dataset, epochs=10)
```

### Time Series (LSTM for Stock Prediction)
```python
import numpy as np

# Prepare sequences: [t-59, t-58, ..., t] → predict t+1
def create_sequences(data, seq_length=60):
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i - seq_length:i])
        y.append(data[i])
    return np.array(X), np.array(y)

X, y = create_sequences(prices_normalized, seq_length=60)

model = keras.Sequential([
    layers.Input(shape=(60, 1)),
    layers.LSTM(128, return_sequences=True),
    layers.Dropout(0.2),
    layers.LSTM(64),
    layers.Dropout(0.2),
    layers.Dense(32, activation="relu"),
    layers.Dense(1),
])
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2, callbacks=callbacks)
```

---

## 7. Advanced Patterns

### Multi-Input / Multi-Output Model
```python
# Technical indicators input
technical_input = keras.Input(shape=(60, 10), name="technical")  # 60 days × 10 features
# Sentiment input
sentiment_input = keras.Input(shape=(60, 1), name="sentiment")

# Technical branch
x1 = layers.LSTM(64, return_sequences=True)(technical_input)
x1 = layers.LSTM(32)(x1)

# Sentiment branch
x2 = layers.LSTM(16)(sentiment_input)

# Merge
merged = layers.Concatenate()([x1, x2])
x = layers.Dense(64, activation="relu")(merged)
x = layers.Dropout(0.3)(x)

# Two outputs
price_pred = layers.Dense(1, name="price")(x)
direction_pred = layers.Dense(1, activation="sigmoid", name="direction")(x)

model = keras.Model(
    inputs=[technical_input, sentiment_input],
    outputs=[price_pred, direction_pred],
)
model.compile(
    optimizer="adam",
    loss={"price": "mse", "direction": "binary_crossentropy"},
    loss_weights={"price": 1.0, "direction": 0.5},
)
```

### Custom Layer
```python
class AttentionLayer(keras.layers.Layer):
    def __init__(self, units, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.W = self.add_weight(shape=(input_shape[-1], self.units), initializer="glorot_uniform")
        self.b = self.add_weight(shape=(self.units,), initializer="zeros")
        self.u = self.add_weight(shape=(self.units,), initializer="glorot_uniform")

    def call(self, inputs):
        score = keras.ops.tanh(keras.ops.matmul(inputs, self.W) + self.b)
        attention_weights = keras.ops.softmax(keras.ops.sum(score * self.u, axis=-1, keepdims=True), axis=1)
        return keras.ops.sum(inputs * attention_weights, axis=1)
```

### Transfer Learning
```python
# Use pre-trained model (freeze base, train head)
base_model = keras.applications.EfficientNetV2B0(
    weights="imagenet", include_top=False, input_shape=(224, 224, 3)
)
base_model.trainable = False

model = keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation="softmax"),
])

# Train head
model.compile(optimizer=keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy")
model.fit(train_ds, epochs=10)

# Fine-tune top layers
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False
model.compile(optimizer=keras.optimizers.Adam(1e-5), loss="sparse_categorical_crossentropy")
model.fit(train_ds, epochs=10)
```

### Keras 3 Multi-Backend
```python
import os
os.environ["KERAS_BACKEND"] = "jax"  # or "torch" or "tensorflow"
import keras

# Same code works on all backends
model = keras.Sequential([layers.Dense(64, activation="relu"), layers.Dense(10)])
model.compile(optimizer="adam", loss="mse")
# Uses JAX's JIT compilation automatically
```

---

## 8. Best Practices

1. **Start simple** — Sequential → Functional → Subclass only when needed
2. **Use callbacks** — EarlyStopping + ReduceLROnPlateau always
3. **Normalize inputs** — StandardScaler or MinMaxScaler before feeding data
4. **Batch normalization** — After Dense/Conv layers for deep nets
5. **Learning rate schedule** — Start 1e-3, reduce on plateau
6. **Validation split** — Always use 10-20% for monitoring
7. **Save/Load properly** — Use `.keras` format (not `.h5`)
8. **Mixed precision** — `keras.mixed_precision.set_global_policy("mixed_float16")` for 2x speedup on GPU
9. **Prefetch data** — `tf.data.AUTOTUNE` for I/O-bound training
10. **Profile** — Use TensorBoard profiler to find bottlenecks

---

## 9. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Overfitting | Add Dropout, reduce model size, data augmentation |
| Vanishing gradients | Use ReLU/GELU, BatchNorm, residual connections |
| Slow training | Mixed precision, larger batch size, prefetch data |
| NaN loss | Lower learning rate, gradient clipping, check data |
| Bad convergence | Learning rate warmup, Adam optimizer, normalize data |
| OOM (GPU) | Reduce batch size, use mixed precision, gradient accumulation |
| `.h5` format issues | Use `.keras` format instead (Keras 3 default) |

---

## 10. Keras vs PyTorch Comparison

| Feature | Keras | PyTorch |
|---------|-------|---------|
| Learning curve | Gentle, high-level | Steeper, more explicit |
| Debugging | Harder (graph mode) | Easy (eager by default) |
| Production | TF Serving, TF Lite, TF.js | TorchServe, ONNX |
| Research | Good but less flexible | Dominant in research |
| Multi-backend | ✅ (Keras 3: TF, JAX, PyTorch) | ❌ PyTorch only |
| Mobile | TF Lite (excellent) | PyTorch Mobile (improving) |
| Training loop | `model.fit()` or custom | Always manual loop |

**When to use Keras:** Rapid prototyping, production with TF ecosystem, multi-backend needs.
**When to use PyTorch:** Research, custom architectures, HuggingFace ecosystem.

---

## 11. Saving & Deployment

```python
# Save (Keras 3 format)
model.save("model.keras")
model = keras.models.load_model("model.keras")

# Export for TF Serving
model.export("saved_model_dir")

# Convert to TF Lite (mobile)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Convert to ONNX (cross-platform)
# pip install tf2onnx
import tf2onnx
tf2onnx.convert.from_keras(model, output_path="model.onnx")
```
