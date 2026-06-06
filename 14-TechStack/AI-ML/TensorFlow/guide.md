# TensorFlow Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```python
import tensorflow as tf

# Check GPU
print(tf.config.list_physical_devices('GPU'))
```

### 2. **Keras Sequential**
```python
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    tf.keras.layers.Dense(10, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))
```

### 3. **Functional API**
```python
inputs = tf.keras.Input(shape=(784,))
x = tf.keras.layers.Dense(128, activation='relu')(inputs)
outputs = tf.keras.layers.Dense(10, activation='softmax')(x)
model = tf.keras.Model(inputs=inputs, outputs=outputs)
```

## Level 2 – Production Patterns

### Custom Layers
```python
class MyLayer(tf.keras.layers.Layer):
    def __init__(self, units=32):
        super(MyLayer, self).__init__()
        self.units = units
    
    def build(self, input_shape):
        self.w = self.add_weight(
            shape=(input_shape[-1], self.units),
            initializer='random_normal',
            trainable=True
        )
    
    def call(self, inputs):
        return tf.matmul(inputs, self.w)
```

### Transfer Learning
```python
base_model = tf.keras.applications.ResNet50(
    weights='imagenet',
    include_top=False
)
base_model.trainable = False

model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(num_classes)
])
```

### Data Pipeline
```python
dataset = tf.data.Dataset.from_tensor_slices((X, y))
dataset = dataset.batch(32).prefetch(tf.data.AUTOTUNE)

model.fit(dataset, epochs=10)
```

## Level 3 – Architect Playbook

### Distributed Training
```python
strategy = tf.distribute.MirroredStrategy()

with strategy.scope():
    model = create_model()
    model.compile(...)

model.fit(X_train, y_train, epochs=10)
```

### Model Serving
```python
# Save model
model.save('saved_model/')

# Serve with TensorFlow Serving
# docker run -p 8501:8501 \
#   -v /path/to/saved_model:/models/model/1 \
#   tensorflow/serving
```

### TensorFlow Lite
```python
# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_saved_model('saved_model/')
tflite_model = converter.convert()

# Save
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Save model | `model.save('path')` | Save model |
| Load model | `tf.keras.models.load_model('path')` | Load model |
| Export | `tf.saved_model.save()` | Export SavedModel |
| Convert | `tf.lite.TFLiteConverter` | Convert to TFLite |

## Checklist Before Production

- [ ] Implement proper data pipelines
- [ ] Set up distributed training if needed
- [ ] Optimize model (quantization, pruning)
- [ ] Set up model versioning
- [ ] Implement proper logging
- [ ] Set up monitoring
- [ ] Configure deployment
- [ ] Test model performance
