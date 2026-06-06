# Keras: Visual Guide & Architecture Diagrams

## 1. Keras Ecosystem Architecture

```mermaid
flowchart TD
    subgraph API["🎨 Keras API (High-Level)"]
        SEQ["📋 Sequential API<br/>Simple stacking"]
        FUNC["🔀 Functional API<br/>Multi-input/output"]
        SUB["🧪 Subclassing API<br/>Full control"]
    end

    subgraph Backend["⚡ Keras 3 Multi-Backend"]
        TF["🟠 TensorFlow"]
        JAX["🔵 JAX"]
        PT["🔴 PyTorch"]
    end

    subgraph Hardware["🖥️ Hardware Targets"]
        CPU["💻 CPU"]
        GPU["🎮 GPU (CUDA)"]
        TPU["⚡ TPU"]
    end

    SEQ & FUNC & SUB --> TF & JAX & PT
    TF --> CPU & GPU & TPU
    JAX --> CPU & GPU & TPU
    PT --> CPU & GPU

    style API fill:#2ECC71,color:#fff,stroke:#27AE60
    style Backend fill:#3498DB,color:#fff,stroke:#2980B9
    style Hardware fill:#9B59B6,color:#fff,stroke:#8E44AD
    style SEQ fill:#27AE60,color:#fff
    style FUNC fill:#27AE60,color:#fff
    style SUB fill:#27AE60,color:#fff
    style TF fill:#FF6F00,color:#fff
    style JAX fill:#2980B9,color:#fff
    style PT fill:#EE4C2C,color:#fff
    style CPU fill:#8E44AD,color:#fff
    style GPU fill:#8E44AD,color:#fff
    style TPU fill:#8E44AD,color:#fff
```

## 2. Model Building APIs Comparison

```mermaid
flowchart LR
    subgraph Sequential["📋 Sequential (Linear)"]
        S1["📥 Input(784)"] --> S2["🔵 Dense(256)"] --> S3["🔵 Dense(128)"] --> S4["📤 Dense(10)"]
    end

    subgraph Functional["🔀 Functional (DAG)"]
        F_IN["📥 Input"] --> F1["🔵 Dense(256)"]
        F_IN --> F2["🟢 Dense(128)"]
        F1 & F2 --> F_MERGE["🔗 Concatenate"]
        F_MERGE --> F_OUT["📤 Dense(10)"]
    end

    subgraph Subclass["🧪 Subclassing (Freedom)"]
        SC["📦 class MyModel(keras.Model)"]
        SC --> CALL["⚙️ def call(self, x)"]
        CALL --> LOGIC["🧠 Custom logic<br/>Conditionals<br/>Dynamic graphs"]
    end

    style Sequential fill:#0f3460,color:#fff,stroke:#533483
    style Functional fill:#1a1a2e,color:#fff,stroke:#e94560
    style Subclass fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style S1 fill:#3498DB,color:#fff
    style S2 fill:#2980B9,color:#fff
    style S3 fill:#2980B9,color:#fff
    style S4 fill:#E74C3C,color:#fff
    style F_IN fill:#3498DB,color:#fff
    style F1 fill:#2980B9,color:#fff
    style F2 fill:#2ECC71,color:#fff
    style F_MERGE fill:#F39C12,color:#fff
    style F_OUT fill:#E74C3C,color:#fff
    style SC fill:#9B59B6,color:#fff
    style CALL fill:#8E44AD,color:#fff
    style LOGIC fill:#E67E22,color:#fff
```

## 3. Training Loop Flow

```mermaid
sequenceDiagram
    participant Data as 📦 Dataset
    participant Model as 🧠 Keras Model
    participant Loss as 📉 Loss Function
    participant Opt as ⚙️ Optimizer
    participant CB as 🔔 Callbacks

    CB->>CB: on_epoch_begin()

    loop Each Batch
        Data->>Model: x_batch
        Model->>Loss: predictions vs y_batch
        Loss->>Opt: gradients
        Opt->>Model: update weights
    end

    CB->>CB: on_epoch_end()
    CB->>CB: EarlyStopping check
    CB->>CB: ReduceLROnPlateau check
    CB->>CB: ModelCheckpoint save
```

## 4. Layer Types Overview

```mermaid
flowchart TD
    subgraph Core["🔵 Core Layers"]
        DENSE["🧠 Dense<br/>Fully connected"]
        ACT["⚡ Activation<br/>relu, sigmoid"]
        DROP["💧 Dropout<br/>Regularization"]
    end

    subgraph Conv["🟢 Convolutional"]
        C2D["🖼️ Conv2D<br/>Image features"]
        POOL["📐 MaxPooling2D<br/>Downsample"]
        BN["📊 BatchNorm<br/>Stabilize"]
    end

    subgraph Seq["🟣 Sequence"]
        LSTM2["🔄 LSTM<br/>Long sequences"]
        GRU2["⚡ GRU<br/>Faster LSTM"]
        ATT2["👁️ Attention<br/>Self-attention"]
    end

    subgraph Special["🟠 Special"]
        EMB["📝 Embedding<br/>Token → vector"]
        FLAT["📏 Flatten<br/>Reshape"]
        CONCAT["🔗 Concatenate<br/>Merge branches"]
    end

    Core --> |"Tabular data"| DENSE
    Conv --> |"Images"| C2D
    Seq --> |"Time series / text"| LSTM2
    Special --> |"NLP / multi-input"| EMB

    style Core fill:#3498DB,color:#fff,stroke:#2980B9
    style Conv fill:#2ECC71,color:#fff,stroke:#27AE60
    style Seq fill:#9B59B6,color:#fff,stroke:#8E44AD
    style Special fill:#E67E22,color:#fff,stroke:#D35400
    style DENSE fill:#2980B9,color:#fff
    style ACT fill:#2980B9,color:#fff
    style DROP fill:#2980B9,color:#fff
    style C2D fill:#27AE60,color:#fff
    style POOL fill:#27AE60,color:#fff
    style BN fill:#27AE60,color:#fff
    style LSTM2 fill:#8E44AD,color:#fff
    style GRU2 fill:#8E44AD,color:#fff
    style ATT2 fill:#8E44AD,color:#fff
    style EMB fill:#D35400,color:#fff
    style FLAT fill:#D35400,color:#fff
    style CONCAT fill:#D35400,color:#fff
```

## 5. Callbacks Pipeline

```mermaid
flowchart TD
    START["🚀 Training Start"] --> EPOCH["📅 Epoch Start"]
    EPOCH --> BATCH["🔄 Batch Loop"]
    BATCH --> EPOCH_END["📊 Epoch End"]

    EPOCH_END --> ES{"🛑 EarlyStopping<br/>val_loss improved?"}
    ES -->|"✅ Yes"| RLROP{"📉 ReduceLROnPlateau<br/>Still improving?"}
    ES -->|"❌ No, patience exceeded"| STOP["🏁 Stop Training<br/>Restore best weights"]

    RLROP -->|"✅ Yes"| CKPT["💾 ModelCheckpoint<br/>Save if best"]
    RLROP -->|"❌ No"| REDUCE["⬇️ Reduce LR × 0.5"]
    REDUCE --> CKPT

    CKPT --> TB["📈 TensorBoard<br/>Log metrics"]
    TB --> NEXT_EPOCH["➡️ Next Epoch"]
    NEXT_EPOCH --> EPOCH

    style START fill:#2ECC71,color:#fff
    style EPOCH fill:#3498DB,color:#fff
    style BATCH fill:#9B59B6,color:#fff
    style EPOCH_END fill:#F39C12,color:#fff
    style ES fill:#E74C3C,color:#fff
    style RLROP fill:#E67E22,color:#fff
    style STOP fill:#C0392B,color:#fff
    style CKPT fill:#2ECC71,color:#fff
    style REDUCE fill:#F39C12,color:#fff
    style TB fill:#3498DB,color:#fff
    style NEXT_EPOCH fill:#9B59B6,color:#fff
```

## 6. Transfer Learning Workflow

```mermaid
flowchart TD
    subgraph Phase1["🔒 Phase 1: Feature Extraction"]
        BASE["🏗️ Pre-trained Base<br/>(EfficientNet, ResNet)<br/>🔒 Frozen"]
        HEAD1["🎯 New Head<br/>Dense → Softmax<br/>🔓 Trainable"]
        BASE --> HEAD1
        LR1["⚡ Learning Rate: 1e-3<br/>Train 10 epochs"]
    end

    subgraph Phase2["🔓 Phase 2: Fine-Tuning"]
        TOP["🔝 Top Layers<br/>🔓 Unfrozen"]
        BOTTOM["🔒 Bottom Layers<br/>Still Frozen"]
        HEAD2["🎯 Head<br/>🔓 Trainable"]
        BOTTOM --> TOP --> HEAD2
        LR2["🔬 Learning Rate: 1e-5<br/>Train 10 more epochs"]
    end

    Phase1 --> Phase2

    style Phase1 fill:#0f3460,color:#fff,stroke:#533483
    style Phase2 fill:#1a1a2e,color:#fff,stroke:#e94560
    style BASE fill:#3498DB,color:#fff
    style HEAD1 fill:#2ECC71,color:#fff
    style LR1 fill:#F39C12,color:#fff
    style TOP fill:#E74C3C,color:#fff
    style BOTTOM fill:#9B59B6,color:#fff
    style HEAD2 fill:#2ECC71,color:#fff
    style LR2 fill:#E67E22,color:#fff
```

## 7. Deployment Options

```mermaid
flowchart LR
    MODEL["📦 Trained Keras Model<br/>.keras file"]

    MODEL --> SERVING["🐳 TF Serving<br/>REST/gRPC API<br/>Docker + K8s"]
    MODEL --> LITE["📱 TF Lite<br/>Mobile / Edge<br/>Android / iOS"]
    MODEL --> TFJS["🌐 TF.js<br/>Browser<br/>Web apps"]
    MODEL --> ONNX2["🔀 ONNX<br/>Cross-platform<br/>Any runtime"]
    MODEL --> SM["☁️ SageMaker<br/>AWS managed<br/>Auto-scaling"]

    SERVING --> PROD["🏢 Production"]
    LITE --> MOBILE["📱 Mobile"]
    TFJS --> WEB["🌐 Web"]
    ONNX2 --> CROSS["🔀 Cross-Platform"]

    style MODEL fill:#3498DB,color:#fff
    style SERVING fill:#E74C3C,color:#fff
    style LITE fill:#2ECC71,color:#fff
    style TFJS fill:#F39C12,color:#fff
    style ONNX2 fill:#9B59B6,color:#fff
    style SM fill:#E67E22,color:#fff
    style PROD fill:#C0392B,color:#fff
    style MOBILE fill:#27AE60,color:#fff
    style WEB fill:#D68910,color:#fff
    style CROSS fill:#8E44AD,color:#fff
```

## 8. Keras vs PyTorch Decision Guide

```mermaid
flowchart TD
    START2["🤔 Choose Framework"] --> Q1{"🔍 Primary Goal?"}

    Q1 -->|"Rapid prototyping"| KERAS["✅ Keras<br/>model.fit() workflow"]
    Q1 -->|"Research / custom"| PYTORCH["✅ PyTorch<br/>Full control"]
    Q1 -->|"Mobile deployment"| KERAS2["✅ Keras + TF Lite"]
    Q1 -->|"HuggingFace models"| PYTORCH2["✅ PyTorch ecosystem"]
    Q1 -->|"Multi-backend"| KERAS3["✅ Keras 3<br/>TF + JAX + PyTorch"]
    Q1 -->|"Production scale"| BOTH["🔄 Both work<br/>Keras: TF Serving<br/>PyTorch: TorchServe"]

    style START2 fill:#3498DB,color:#fff
    style Q1 fill:#9B59B6,color:#fff
    style KERAS fill:#2ECC71,color:#fff
    style PYTORCH fill:#EE4C2C,color:#fff
    style KERAS2 fill:#27AE60,color:#fff
    style PYTORCH2 fill:#E74C3C,color:#fff
    style KERAS3 fill:#F39C12,color:#fff
    style BOTH fill:#E67E22,color:#fff
```

## 9. Financial Time Series with Keras

```mermaid
flowchart TD
    subgraph Data["📥 Data Pipeline"]
        OHLCV["📊 OHLCV Data<br/>374 NSE symbols"]
        FEAT["⚙️ Feature Engineering<br/>RSI, MACD, Bollinger"]
        WINDOW["📐 Sliding Window<br/>60-day lookback"]
    end

    subgraph Model["🧠 LSTM Model"]
        INPUT["📥 Input(60, 12)<br/>60 days × 12 features"]
        LSTM_1["🔄 LSTM(128)<br/>return_sequences=True"]
        DROP_1["💧 Dropout(0.3)"]
        LSTM_2["🔄 LSTM(64)"]
        DENSE_1["🧠 Dense(32, relu)"]
        OUT["📤 Dense(3, softmax)<br/>Buy / Hold / Sell"]
    end

    subgraph Deploy["🚀 Production"]
        PRED["📊 Daily Prediction<br/>After market close"]
        SIGNAL["📡 Signal Generation<br/>Confidence threshold"]
        EXEC["⚡ Execution<br/>Next market open"]
    end

    OHLCV --> FEAT --> WINDOW --> INPUT
    INPUT --> LSTM_1 --> DROP_1 --> LSTM_2 --> DENSE_1 --> OUT
    OUT --> PRED --> SIGNAL --> EXEC

    style Data fill:#0f3460,color:#fff,stroke:#533483
    style Model fill:#1a1a2e,color:#fff,stroke:#e94560
    style Deploy fill:#1a1a2e,color:#fff,stroke:#2ECC71
    style OHLCV fill:#3498DB,color:#fff
    style FEAT fill:#9B59B6,color:#fff
    style WINDOW fill:#00B4D8,color:#fff
    style INPUT fill:#E74C3C,color:#fff
    style LSTM_1 fill:#E67E22,color:#fff
    style DROP_1 fill:#F39C12,color:#fff
    style LSTM_2 fill:#E67E22,color:#fff
    style DENSE_1 fill:#D35400,color:#fff
    style OUT fill:#C0392B,color:#fff
    style PRED fill:#2ECC71,color:#fff
    style SIGNAL fill:#27AE60,color:#fff
    style EXEC fill:#1ABC9C,color:#fff
```

## 10. Learning Path

```mermaid
graph TD
    subgraph W1["📗 Week 1: Basics"]
        W1A["📋 Sequential API<br/>Dense layers"]
        W1B["⚙️ Loss & Optimizers<br/>Compile + fit"]
        W1C["🔢 MNIST classification"]
    end

    subgraph W2["📘 Week 2: Intermediate"]
        W2A["🔀 Functional API<br/>Multi-input"]
        W2B["🔔 Callbacks<br/>Early stopping"]
        W2C["🖼️ Conv2D, LSTM<br/>Image + sequence"]
    end

    subgraph W3["📙 Week 3: Advanced"]
        W3A["🧪 Custom layers<br/>Custom training"]
        W3B["🏗️ Transfer learning<br/>EfficientNet"]
        W3C["⚡ Mixed precision<br/>tf.data pipelines"]
    end

    subgraph W4["📕 Week 4: Production"]
        W4A["📦 Model export<br/>SavedModel format"]
        W4B["🐳 TF Serving<br/>TF Lite"]
        W4C["📈 Monitoring<br/>A/B testing"]
    end

    W1 --> W2 --> W3 --> W4

    style W1 fill:#2ECC71,color:#fff,stroke:#27AE60
    style W2 fill:#3498DB,color:#fff,stroke:#2980B9
    style W3 fill:#E67E22,color:#fff,stroke:#D35400
    style W4 fill:#E74C3C,color:#fff,stroke:#C0392B
    style W1A fill:#27AE60,color:#fff
    style W1B fill:#27AE60,color:#fff
    style W1C fill:#27AE60,color:#fff
    style W2A fill:#2980B9,color:#fff
    style W2B fill:#2980B9,color:#fff
    style W2C fill:#2980B9,color:#fff
    style W3A fill:#D35400,color:#fff
    style W3B fill:#D35400,color:#fff
    style W3C fill:#D35400,color:#fff
    style W4A fill:#C0392B,color:#fff
    style W4B fill:#C0392B,color:#fff
    style W4C fill:#C0392B,color:#fff
```
