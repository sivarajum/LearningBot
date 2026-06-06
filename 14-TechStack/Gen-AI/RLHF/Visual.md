# RLHF: Visual Guide & Architecture Diagrams

## Table of Contents
1. [RLHF 3-Stage Pipeline Overview](#rlhf-3-stage-pipeline-overview)
2. [Reward Model Training Flow](#reward-model-training-flow)
3. [PPO Training Loop](#ppo-training-loop)
4. [DPO vs PPO Comparison](#dpo-vs-ppo-comparison)
5. [RLHF Alternatives Comparison](#rlhf-alternatives-comparison)
6. [InstructGPT Architecture](#instructgpt-architecture)
7. [Constitutional AI Flow](#constitutional-ai-flow)
8. [Learning Path](#learning-path)
9. [Performance Comparison](#performance-comparison)

---

## RLHF 3-Stage Pipeline Overview

### Complete RLHF Pipeline

```mermaid
graph TD
    subgraph Stage1["Stage 1: Supervised Fine-Tuning (SFT)"]
        A1["Pre-trained LLM<br/>(GPT, Llama, etc.)"] --> A2["Curated Dataset<br/>(prompt, response) pairs"]
        A2 --> A3["Standard Cross-Entropy Loss<br/>L = -Σ log P(yᵢ | y<ᵢ, x)"]
        A3 --> A4["SFT Model<br/>(instruction-following)"]
    end

    subgraph Stage2["Stage 2: Reward Model Training"]
        B1["SFT Model generates<br/>multiple responses per prompt"] --> B2["Human Annotators rank<br/>Response A > Response B"]
        B2 --> B3["Bradley-Terry Pairwise Loss<br/>L = -log σ(r(x,yₐ) - r(x,yᵦ))"]
        B3 --> B4["Reward Model<br/>(scalar score per response)"]
    end

    subgraph Stage3["Stage 3: RL Optimization (PPO)"]
        C1["Prompts from distribution"] --> C2["Policy generates response"]
        C2 --> C3["Reward Model scores response"]
        C3 --> C4["PPO Update with KL penalty<br/>L = -E[R(x,y)] + β·KL(π‖π_ref)"]
        C4 --> C5["Aligned Model<br/>(helpful, harmless, honest)"]
    end

    A4 --> B1
    A4 -.->|"Initialize RM from SFT"| B3
    A4 -.->|"Reference Model (frozen)"| C4
    B4 --> C3

    style Stage1 fill:#E3F2FD,stroke:#1565C0
    style Stage2 fill:#FFF3E0,stroke:#E65100
    style Stage3 fill:#E8F5E9,stroke:#2E7D32
    style A4 fill:#BBDEFB
    style B4 fill:#FFE0B2
    style C5 fill:#C8E6C9
```

### Data Requirements per Stage

```mermaid
graph LR
    subgraph SFT["Stage 1: SFT"]
        S1["10K-100K<br/>(prompt, response) pairs"]
        S2["Human-written<br/>demonstrations"]
    end

    subgraph RM["Stage 2: Reward Model"]
        R1["30K-100K<br/>pairwise comparisons"]
        R2["Human annotators<br/>rank responses"]
    end

    subgraph PPO["Stage 3: PPO"]
        P1["10K-50K<br/>prompts (no labels)"]
        P2["Reward model<br/>provides signal"]
    end

    S1 --> R1
    R1 --> P1

    S2 --> |"Quality > Quantity"| S1
    R2 --> |"73%+ agreement"| R1
    P2 --> |"Automated scoring"| P1

    style SFT fill:#E3F2FD
    style RM fill:#FFF3E0
    style PPO fill:#E8F5E9
```

---

## Reward Model Training Flow

### Preference Data Collection

```mermaid
sequenceDiagram
    participant P as Prompt Pool
    participant M as SFT Model
    participant H as Human Annotators
    participant RM as Reward Model

    P ->> M: Sample prompt
    M ->> M: Generate Response A
    M ->> M: Generate Response B
    M ->> M: Generate Response C
    M ->> M: Generate Response D

    M ->> H: Present all 4 responses
    H ->> H: Rank: A > C > D > B

    Note over H: Creates C(4,2) = 6 pairs

    H ->> RM: Pair 1: A > C ✓
    H ->> RM: Pair 2: A > D ✓
    H ->> RM: Pair 3: A > B ✓
    H ->> RM: Pair 4: C > D ✓
    H ->> RM: Pair 5: C > B ✓
    H ->> RM: Pair 6: D > B ✓

    RM ->> RM: Train with Bradley-Terry loss
    RM ->> RM: Learn scalar reward function r(prompt, response) → ℝ
```

### Reward Model Architecture

```mermaid
graph TD
    INPUT["Input: [prompt] + [response]<br/>Tokenized sequence"] --> EMBED["Token Embeddings<br/>+ Position Embeddings"]
    EMBED --> TRANSFORMER["Transformer Backbone<br/>(initialized from SFT model)"]
    TRANSFORMER --> LAST_TOKEN["Extract Last Token<br/>Hidden State h_T"]
    LAST_TOKEN --> LINEAR["Linear Projection<br/>h_T → ℝ (scalar)"]
    LINEAR --> REWARD["Reward Score<br/>r(x, y) ∈ (-∞, +∞)"]

    subgraph Training["Training: Pairwise Ranking"]
        CHOSEN["r(x, y_chosen)"] --> DIFF["Compute Difference<br/>r(chosen) - r(rejected)"]
        REJECTED["r(x, y_rejected)"] --> DIFF
        DIFF --> SIGMOID["σ(difference)"]
        SIGMOID --> LOSS["L = -log σ(r_w - r_l)"]
    end

    REWARD --> CHOSEN
    REWARD --> REJECTED

    style INPUT fill:#E8F4F8
    style TRANSFORMER fill:#FF6B6B,color:#fff
    style REWARD fill:#C8E6C9
    style Training fill:#FFF3E0
```

### Reward Model Quality Checks

```mermaid
graph TD
    RM["Trained Reward Model"] --> CHECK1["Accuracy Check<br/>Agreement with held-out prefs > 70%"]
    RM --> CHECK2["Length Bias Check<br/>Correlation(reward, length) < 0.3"]
    RM --> CHECK3["Position Bias Check<br/>Swap A/B → same preference?"]
    RM --> CHECK4["Calibration Check<br/>Score distribution is smooth"]
    RM --> CHECK5["OOD Robustness<br/>Performance on unseen topics"]

    CHECK1 --> |"Pass"| DEPLOY["Deploy for PPO Training"]
    CHECK2 --> |"Pass"| DEPLOY
    CHECK3 --> |"Pass"| DEPLOY
    CHECK4 --> |"Pass"| DEPLOY
    CHECK5 --> |"Pass"| DEPLOY

    CHECK1 --> |"Fail"| FIX1["More diverse training data"]
    CHECK2 --> |"Fail"| FIX2["Add length normalization"]
    CHECK3 --> |"Fail"| FIX3["Shuffle presentation order"]
    CHECK4 --> |"Fail"| FIX4["Adjust loss margin"]
    CHECK5 --> |"Fail"| FIX5["Add OOD examples to training"]

    style RM fill:#FF6B6B,color:#fff
    style DEPLOY fill:#C8E6C9
    style FIX1 fill:#FFCDD2
    style FIX2 fill:#FFCDD2
    style FIX3 fill:#FFCDD2
    style FIX4 fill:#FFCDD2
    style FIX5 fill:#FFCDD2
```

---

## PPO Training Loop

### PPO Training Architecture (4 Models)

```mermaid
graph TD
    subgraph Models["4 Models in Memory"]
        POLICY["Policy Model π_θ<br/>(being optimized)"]
        REF["Reference Model π_ref<br/>(frozen SFT copy)"]
        RM["Reward Model R_φ<br/>(frozen, trained in Stage 2)"]
        VALUE["Value Head V_ψ<br/>(estimates expected reward)"]
    end

    PROMPT["Batch of Prompts"] --> POLICY
    POLICY --> |"Generate responses"| RESPONSES["Generated Responses y"]
    RESPONSES --> RM
    RESPONSES --> REF
    RM --> |"Score quality"| REWARD["Reward Score R(x,y)"]
    REF --> |"Compute log probs"| KL["KL Divergence<br/>KL(π_θ ‖ π_ref)"]

    REWARD --> COMBINED["Combined Reward<br/>R(x,y) - β·KL"]
    KL --> COMBINED

    VALUE --> |"Estimate future reward"| ADVANTAGE["Advantage Estimate<br/>A = R_combined - V(s)"]
    COMBINED --> ADVANTAGE

    ADVANTAGE --> PPO_UPDATE["PPO Clipped Update<br/>min(r·A, clip(r, 1-ε, 1+ε)·A)"]
    PPO_UPDATE --> POLICY

    style POLICY fill:#FF6B6B,color:#fff
    style REF fill:#4ECDC4,color:#fff
    style RM fill:#FFE0B2
    style VALUE fill:#B3E5FC
    style COMBINED fill:#E1BEE7
    style PPO_UPDATE fill:#C8E6C9
```

### Detailed PPO Step-by-Step

```mermaid
sequenceDiagram
    participant Prompts as Prompt Batch
    participant Policy as Policy π_θ
    participant Ref as Reference π_ref
    participant RM as Reward Model
    participant Value as Value Head
    participant Optim as PPO Optimizer

    Note over Prompts,Optim: Each PPO iteration

    Prompts ->> Policy: Sample batch of prompts
    Policy ->> Policy: Generate responses (sampling)

    Policy ->> RM: Send (prompt, response) pairs
    RM ->> RM: Compute reward scores r(x, y)
    RM -->> Optim: Reward: R = [3.2, 1.8, 4.1, ...]

    Policy ->> Ref: Send same responses
    Ref ->> Ref: Compute log P_ref(y|x)
    Policy ->> Policy: Compute log P_θ(y|x)
    Note over Policy,Ref: KL = log P_θ - log P_ref

    Policy -->> Optim: KL divergence per token
    Value -->> Optim: Value estimates V(s)

    Note over Optim: Combined reward = R - β·KL
    Note over Optim: Advantage A = Combined - V(s)
    Note over Optim: Ratio r = P_θ(new) / P_θ(old)
    Note over Optim: Clipped objective = min(r·A, clip(r)·A)

    Optim ->> Policy: Update policy weights
    Optim ->> Value: Update value head

    Note over Optim: Adaptive KL: if KL > target → increase β
```

### KL Divergence Dynamics

```mermaid
graph LR
    subgraph KL_Low["KL Too Low (≈0)"]
        L1["Model barely changed from SFT"]
        L2["Not learning preferences"]
        L3["Action: Decrease β"]
    end

    subgraph KL_Sweet["KL Sweet Spot (3-10)"]
        M1["Model learning preferences"]
        M2["Still coherent language"]
        M3["Diverse outputs"]
    end

    subgraph KL_High["KL Too High (>15)"]
        H1["Model diverging from SFT"]
        H2["Risk of reward hacking"]
        H3["Action: Increase β"]
    end

    KL_Low --> |"Relax constraint"| KL_Sweet
    KL_Sweet --> |"On target"| KL_Sweet
    KL_High --> |"Tighten constraint"| KL_Sweet

    style KL_Low fill:#FFCDD2
    style KL_Sweet fill:#C8E6C9
    style KL_High fill:#FFCDD2
```

---

## DPO vs PPO Comparison

### Side-by-Side Architecture

```mermaid
graph TD
    subgraph PPO_Pipeline["PPO-based RLHF (Classic)"]
        direction TB
        PP1["Preference Data<br/>(chosen, rejected)"] --> PP2["Train Reward Model"]
        PP2 --> PP3["Reward Model R_φ"]
        PP4["Prompts"] --> PP5["Policy generates response"]
        PP5 --> PP3
        PP3 --> PP6["Reward signal"]
        PP5 --> PP7["Reference model<br/>computes KL"]
        PP6 --> PP8["PPO Update<br/>(clipped surrogate)"]
        PP7 --> PP8
        PP8 --> PP9["Policy + Value Head update"]
    end

    subgraph DPO_Pipeline["DPO (Direct Preference Optimization)"]
        direction TB
        DP1["Preference Data<br/>(chosen, rejected)"] --> DP2["Direct Policy Training"]
        DP3["Reference Model<br/>(frozen SFT)"] --> DP2
        DP2 --> DP4["Log-ratio computation<br/>β(log π/π_ref chosen - log π/π_ref rejected)"]
        DP4 --> DP5["Binary cross-entropy loss"]
        DP5 --> DP6["Policy update<br/>(standard backprop)"]
    end

    style PPO_Pipeline fill:#FFF3E0,stroke:#E65100
    style DPO_Pipeline fill:#E3F2FD,stroke:#1565C0
    style PP3 fill:#FFE0B2
    style PP8 fill:#FFCC80
    style DP2 fill:#BBDEFB
    style DP5 fill:#90CAF9
```

### Decision Flowchart: PPO vs DPO

```mermaid
flowchart TD
    START["Which alignment method?"] --> Q1{"Do you have<br/>preference data<br/>(chosen/rejected)?"}
    Q1 --> |"Yes"| Q2{"GPU memory<br/>budget?"}
    Q1 --> |"No, only good/bad labels"| KTO["Use KTO<br/>(unpaired preferences)"]
    Q1 --> |"No preference data at all"| SPIN["Use SPIN<br/>(self-play)"]

    Q2 --> |"< 40 GB (1-2 GPUs)"| Q3{"Need exploration<br/>beyond training data?"}
    Q2 --> |"> 100 GB (4+ GPUs)"| Q4{"Is maximum<br/>performance critical?"}

    Q3 --> |"No"| DPO["Use DPO<br/>✅ Simple, efficient"]
    Q3 --> |"Yes"| ORPO["Use ORPO<br/>✅ No ref model needed"]

    Q4 --> |"Yes, at any cost"| PPO["Use PPO<br/>⭐ Gold standard"]
    Q4 --> |"Good-enough is fine"| DPO2["Use DPO with LoRA<br/>✅ Best ROI"]

    style START fill:#E8F4F8
    style DPO fill:#C8E6C9
    style DPO2 fill:#C8E6C9
    style PPO fill:#FFE0B2
    style KTO fill:#E1BEE7
    style ORPO fill:#B3E5FC
    style SPIN fill:#FFCDD2
```

### Resource Comparison

```mermaid
graph TD
    subgraph PPO_Resources["PPO Resources (7B model)"]
        PPO_M1["Policy: 14 GB"]
        PPO_M2["Reference: 14 GB"]
        PPO_M3["Reward Model: 14 GB"]
        PPO_M4["Value Head: 14 GB"]
        PPO_TOTAL["Total: ~56 GB + optimizer states"]
    end

    subgraph DPO_Resources["DPO Resources (7B model)"]
        DPO_M1["Policy: 14 GB"]
        DPO_M2["Reference: 14 GB"]
        DPO_TOTAL["Total: ~28 GB + optimizer states"]
    end

    subgraph ORPO_Resources["ORPO Resources (7B model)"]
        ORPO_M1["Policy: 14 GB"]
        ORPO_TOTAL["Total: ~14 GB + optimizer states"]
    end

    style PPO_Resources fill:#FFCDD2
    style DPO_Resources fill:#FFF9C4
    style ORPO_Resources fill:#C8E6C9
    style PPO_TOTAL fill:#EF9A9A
    style DPO_TOTAL fill:#FFF176
    style ORPO_TOTAL fill:#A5D6A7
```

---

## RLHF Alternatives Comparison

### Evolution of Alignment Methods

```mermaid
timeline
    title Evolution of LLM Alignment Methods
    2017 : PPO (Schulman et al.)
         : Standard RL algorithm adapted for LLMs
    2022 : InstructGPT (Ouyang et al.)
         : PPO-based RLHF at scale
         : Constitutional AI (Bai et al.)
         : AI feedback replaces humans
    2023 : DPO (Rafailov et al.)
         : Direct optimization, no RM needed
         : IPO (Azar et al.)
         : Robust DPO variant
         : Llama 2 Multi-objective RLHF
    2024 : KTO (Ethayarajh et al.)
         : Works with unpaired data
         : ORPO (Hong et al.)
         : No reference model needed
         : SPIN (Chen et al.)
         : Self-play fine-tuning
    2025 : Online DPO, GRPO (DeepSeek R1)
         : Hybrid approaches dominate
```

### Method Taxonomy

```mermaid
graph TD
    ROOT["LLM Alignment Methods"] --> ONLINE["Online Methods<br/>(generate during training)"]
    ROOT --> OFFLINE["Offline Methods<br/>(fixed preference data)"]
    ROOT --> SELF["Self-Improvement<br/>(no human data)"]

    ONLINE --> PPO["PPO<br/>⭐ Gold standard<br/>4 models, complex"]
    ONLINE --> ONLINE_DPO["Online DPO<br/>Generate + DPO<br/>Best of both worlds"]
    ONLINE --> GRPO["GRPO<br/>(DeepSeek R1)<br/>Group relative policy opt."]

    OFFLINE --> DPO["DPO<br/>Direct preference opt.<br/>Simple, 2 models"]
    OFFLINE --> IPO["IPO<br/>Identity preference opt.<br/>More robust than DPO"]
    OFFLINE --> KTO["KTO<br/>Kahneman-Tversky opt.<br/>Unpaired data OK"]
    OFFLINE --> ORPO["ORPO<br/>Odds ratio pref. opt.<br/>No ref model, 1 model"]

    SELF --> CAI["Constitutional AI<br/>Self-critique + revise<br/>Principle-based"]
    SELF --> SPIN["SPIN<br/>Self-play fine-tuning<br/>Iterative self-improvement"]
    SELF --> RLAIF["RLAIF<br/>AI-generated preferences<br/>Scalable"]

    style ROOT fill:#150458,color:#fff
    style ONLINE fill:#FF6B6B,color:#fff
    style OFFLINE fill:#4ECDC4,color:#fff
    style SELF fill:#45B7D1,color:#fff
    style PPO fill:#FFE0B2
    style DPO fill:#C8E6C9
    style ORPO fill:#B3E5FC
    style CAI fill:#E1BEE7
```

### Feature Matrix

```mermaid
graph TD
    subgraph Matrix["Alignment Method Feature Matrix"]
        direction TB

        subgraph Header[""]
            H1["Method"]
            H2["Needs RM?"]
            H3["Needs Ref?"]
            H4["Paired Data?"]
            H5["Memory"]
            H6["Stability"]
        end

        subgraph Row1["PPO"]
            R1A["PPO"] --- R1B["✅ Yes"]
            R1B --- R1C["✅ Yes"]
            R1C --- R1D["❌ No"]
            R1D --- R1E["4x model"]
            R1E --- R1F["⚠️ Tricky"]
        end

        subgraph Row2["DPO"]
            R2A["DPO"] --- R2B["❌ No"]
            R2B --- R2C["✅ Yes"]
            R2C --- R2D["✅ Yes"]
            R2D --- R2E["2x model"]
            R2E --- R2F["✅ Good"]
        end

        subgraph Row3["ORPO"]
            R3A["ORPO"] --- R3B["❌ No"]
            R3B --- R3C["❌ No"]
            R3C --- R3D["✅ Yes"]
            R3D --- R3E["1x model"]
            R3E --- R3F["✅ Great"]
        end

        subgraph Row4["KTO"]
            R4A["KTO"] --- R4B["❌ No"]
            R4B --- R4C["✅ Yes"]
            R4C --- R4D["❌ No"]
            R4D --- R4E["2x model"]
            R4E --- R4F["✅ Good"]
        end
    end

    style Matrix fill:#FAFAFA
    style Row1 fill:#FFCDD2
    style Row2 fill:#C8E6C9
    style Row3 fill:#B3E5FC
    style Row4 fill:#E1BEE7
```

---

## InstructGPT Architecture

### Full InstructGPT Pipeline

```mermaid
graph TD
    subgraph Step1["Step 1: Collect Demonstration Data"]
        S1A["API Prompts<br/>(user queries)"] --> S1B["40 Labelers write<br/>ideal responses"]
        S1B --> S1C["~13K (prompt, response)"]
    end

    subgraph Step2["Step 2: Train SFT Model"]
        S1C --> S2A["Fine-tune GPT-3<br/>(175B params)"]
        S2A --> S2B["SFT Model<br/>(follows instructions)"]
    end

    subgraph Step3["Step 3: Collect Comparison Data"]
        S2B --> S3A["Generate K=4-9<br/>responses per prompt"]
        S3A --> S3B["Labelers rank all<br/>K responses"]
        S3B --> S3C["~33K comparisons<br/>(C(K,2) pairs each)"]
    end

    subgraph Step4["Step 4: Train Reward Model"]
        S3C --> S4A["Initialize from<br/>GPT-3 6B"]
        S4A --> S4B["Replace final layer<br/>with scalar head"]
        S4B --> S4C["Reward Model<br/>r(prompt, response) → ℝ"]
    end

    subgraph Step5["Step 5: Optimize with PPO"]
        S4C --> S5A["Score generated<br/>responses"]
        S2B -.-> |"Reference policy"| S5B["KL constraint<br/>π_θ close to π_ref"]
        S5A --> S5C["PPO training<br/>~31K prompts"]
        S5B --> S5C
        S5C --> S5D["InstructGPT<br/>(1.3B or 175B)"]
    end

    style Step1 fill:#E3F2FD
    style Step2 fill:#FFF3E0
    style Step3 fill:#FCE4EC
    style Step4 fill:#E8F5E9
    style Step5 fill:#F3E5F5
    style S5D fill:#CE93D8,color:#fff
```

### InstructGPT Key Results

```mermaid
graph LR
    subgraph Results["InstructGPT Results (2022)"]
        direction TB

        subgraph WinRate["Human Preference Win Rate"]
            GPT3["GPT-3 175B<br/>(SFT only)<br/>29%"]
            IGPT["InstructGPT 1.3B<br/>(with RLHF)<br/>71%"]
        end

        subgraph Truth["TruthfulQA"]
            GPT3T["GPT-3<br/>22%"]
            IGPTT["InstructGPT<br/>43%"]
        end

        subgraph Toxic["Toxicity (RealToxicityPrompts)"]
            GPT3X["GPT-3<br/>Baseline"]
            IGPTX["InstructGPT<br/>-25% toxicity"]
        end
    end

    style Results fill:#FAFAFA
    style GPT3 fill:#FFCDD2
    style IGPT fill:#C8E6C9
    style GPT3T fill:#FFCDD2
    style IGPTT fill:#C8E6C9
    style GPT3X fill:#FFCDD2
    style IGPTX fill:#C8E6C9
```

---

## Constitutional AI Flow

### Constitutional AI (CAI) Pipeline

```mermaid
graph TD
    subgraph Phase1["Phase 1: Supervised (Critique + Revision)"]
        P1A["Red-team prompt<br/>(adversarial query)"] --> P1B["Model generates<br/>initial response"]
        P1B --> P1C["Self-Critique<br/>against Constitution"]
        P1C --> P1D["Self-Revision<br/>improved response"]
        P1D --> P1E["(original, revised) pair"]
    end

    subgraph Constitution["Constitution (Principles)"]
        C1["1. Choose the most helpful response"]
        C2["2. Avoid harmful or toxic content"]
        C3["3. Be honest, don't fabricate"]
        C4["4. Avoid stereotypes and bias"]
        C5["5. Respect user privacy"]
    end

    subgraph Phase2["Phase 2: RL (RLAIF)"]
        P2A["AI evaluates responses<br/>using Constitution"] --> P2B["Preference pairs generated<br/>(revised > original)"]
        P2B --> P2C["Train Reward Model<br/>on AI preferences"]
        P2C --> P2D["PPO training<br/>(standard RLHF)"]
        P2D --> P2E["Aligned Model<br/>(Claude)"]
    end

    Constitution --> P1C
    Constitution --> P2A
    P1E --> P2A

    style Phase1 fill:#E3F2FD,stroke:#1565C0
    style Phase2 fill:#E8F5E9,stroke:#2E7D32
    style Constitution fill:#FFF3E0,stroke:#E65100
    style P2E fill:#CE93D8,color:#fff
```

### Critique-Revision Cycle (Detail)

```mermaid
sequenceDiagram
    participant User as Red-Team Prompt
    participant Model as Base Model
    participant Critic as Self-Critique
    participant Reviser as Self-Revision
    participant Dataset as Training Data

    User ->> Model: "How do I hack a WiFi network?"
    Model ->> Model: Generate initial response
    Model -->> Critic: "Here's how to hack WiFi: Step 1..."

    Note over Critic: Apply Principle #2:<br/>"Avoid harmful content"
    Critic ->> Critic: "This response teaches illegal hacking.<br/>It should refuse and suggest legal alternatives."

    Critic -->> Reviser: Critique + original response
    Reviser ->> Reviser: Generate revised response
    Reviser -->> Dataset: "I can't help with unauthorized network access.<br/>If you need to test your own network security,<br/>here are legal penetration testing tools..."

    Note over Dataset: (original=harmful, revised=safe)<br/>becomes training pair

    Dataset ->> Dataset: Accumulate thousands of pairs
    Dataset -->> Dataset: Use for RM training (Phase 2)
```

### RLHF vs Constitutional AI

```mermaid
graph TD
    subgraph RLHF_Path["Standard RLHF"]
        RA["Hire 40+ annotators"] --> RB["Collect 33K+ comparisons"]
        RB --> RC["Train Reward Model"]
        RC --> RD["PPO Training"]
        RD --> RE["Aligned Model"]
        RB -.-> RCOST["Cost: $100K-$1M"]
        RB -.-> RTIME["Time: Months"]
    end

    subgraph CAI_Path["Constitutional AI"]
        CA["Write 20 principles"] --> CB["Model self-critiques"]
        CB --> CC["Generate preference pairs (unlimited)"]
        CC --> CD["Train Reward Model"]
        CD --> CE["PPO Training"]
        CE --> CF["Aligned Model"]
        CA -.-> CCOST["Cost: Compute only"]
        CA -.-> CTIME["Time: Days"]
    end

    style RLHF_Path fill:#FFCDD2
    style CAI_Path fill:#C8E6C9
    style RCOST fill:#EF9A9A
    style CCOST fill:#A5D6A7
    style RE fill:#E57373,color:#fff
    style CF fill:#66BB6A,color:#fff
```

---

## Learning Path

### RLHF Learning Roadmap

```mermaid
graph TD
    subgraph Beginner["🟢 Beginner (Week 1-2)"]
        B1["Understand the problem<br/>Why alignment matters"] --> B2["3-stage pipeline<br/>SFT → RM → PPO"]
        B2 --> B3["Preference data formats<br/>chosen vs rejected"]
        B3 --> B4["Run SFTTrainer<br/>Fine-tune a small model"]
    end

    subgraph Intermediate["🟡 Intermediate (Week 3-4)"]
        I1["PPO algorithm details<br/>KL penalty, clipping"] --> I2["Reward model training<br/>Bradley-Terry loss"]
        I2 --> I3["DPO: simpler alternative<br/>DPOTrainer end-to-end"]
        I3 --> I4["Reward hacking<br/>Failure modes & fixes"]
    end

    subgraph Advanced["🔴 Advanced (Week 5-8)"]
        A1["Scale to 70B+ models<br/>LoRA, DeepSpeed, QLoRA"] --> A2["Multi-objective RLHF<br/>Helpfulness vs Safety"]
        A2 --> A3["Constitutional AI<br/>RLAIF, self-play"]
        A3 --> A4["Compare all methods<br/>DPO, ORPO, KTO, IPO, SPIN"]
    end

    subgraph Expert["⚫ Expert (Ongoing)"]
        E1["Design RLHF pipelines<br/>for production"] --> E2["Custom reward models<br/>Domain-specific alignment"]
        E2 --> E3["Research frontiers<br/>Online DPO, GRPO"]
        E3 --> E4["Alignment evaluation<br/>Red-teaming, benchmarks"]
    end

    B4 --> I1
    I4 --> A1
    A4 --> E1

    style Beginner fill:#C8E6C9
    style Intermediate fill:#FFF9C4
    style Advanced fill:#FFCDD2
    style Expert fill:#CFD8DC
```

### Prerequisites Map

```mermaid
graph LR
    subgraph Prerequisites["Prerequisites"]
        PR1["Python proficiency"]
        PR2["PyTorch basics"]
        PR3["Transformers library"]
        PR4["RL fundamentals<br/>(policy, reward, value)"]
        PR5["Fine-tuning LLMs<br/>(SFT experience)"]
    end

    subgraph Core_RLHF["Core RLHF"]
        C1["Reward modeling"]
        C2["PPO for LLMs"]
        C3["KL penalty"]
    end

    subgraph Modern["Modern Methods"]
        M1["DPO"]
        M2["ORPO"]
        M3["KTO"]
    end

    subgraph Applied["Applied"]
        A1["Production deployment"]
        A2["Red-teaming"]
        A3["Evaluation"]
    end

    PR1 & PR2 --> PR3
    PR3 & PR4 --> PR5
    PR5 --> C1 & C2
    C1 & C2 --> C3
    C3 --> M1 & M2 & M3
    M1 & M2 & M3 --> A1 & A2 & A3

    style Prerequisites fill:#E3F2FD
    style Core_RLHF fill:#FFF3E0
    style Modern fill:#E8F5E9
    style Applied fill:#F3E5F5
```

---

## Performance Comparison

### Method Performance on Benchmarks

```mermaid
xychart-beta
    title "Alignment Method Performance (MT-Bench, 7B models)"
    x-axis ["SFT Only", "PPO", "DPO", "IPO", "KTO", "ORPO"]
    y-axis "MT-Bench Score" 4.0 --> 7.5
    bar [5.2, 6.8, 6.5, 6.3, 6.4, 6.6]
```

### Training Cost Comparison

```mermaid
xychart-beta
    title "Relative Training Cost (normalized to DPO = 1.0)"
    x-axis ["ORPO", "DPO", "KTO", "IPO", "PPO"]
    y-axis "Relative Cost" 0 --> 5
    bar [0.6, 1.0, 1.1, 1.0, 4.5]
```

### Comprehensive Comparison Table

| Aspect | PPO | DPO | IPO | KTO | ORPO | SPIN |
|--------|-----|-----|-----|-----|------|------|
| **Year** | 2022 | 2023 | 2023 | 2024 | 2024 | 2024 |
| **Models in memory** | 4 | 2 | 2 | 2 | 1 | 2 |
| **Needs reward model** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Needs reference model** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Needs paired preferences** | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Training stability** | ⚠️ Low | ✅ High | ✅ Very high | ✅ High | ✅ Very high | ✅ High |
| **GPU memory (7B)** | ~56 GB | ~28 GB | ~28 GB | ~28 GB | ~14 GB | ~28 GB |
| **Training speed** | Slow | Fast | Fast | Fast | Fastest | Medium |
| **Online exploration** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **MT-Bench (7B)** | 6.8 | 6.5 | 6.3 | 6.4 | 6.6 | 6.1 |
| **Implementation complexity** | High | Low | Low | Medium | Very low | Medium |
| **Used in production** | ChatGPT, Llama 2 | Zephyr, many | Research | Research | Research | Research |
| **Best for** | Maximum quality | Default choice | Robust training | Unpaired data | Memory-constrained | No pref data |

### When to Use Each Method (Decision Matrix)

```mermaid
graph TD
    Q1{"What data do<br/>you have?"} --> |"Paired preferences<br/>(chosen, rejected)"| Q2{"Memory<br/>budget?"}
    Q1 --> |"Only good/bad labels<br/>(unpaired)"| KTO["✅ KTO"]
    Q1 --> |"No preference data"| Q5{"Have strong<br/>base model?"}

    Q2 --> |"Limited<br/>(< 24 GB)"| ORPO["✅ ORPO"]
    Q2 --> |"Moderate<br/>(24-48 GB)"| Q3{"Priority?"}
    Q2 --> |"Unlimited<br/>(8×A100)"| PPO["✅ PPO"]

    Q3 --> |"Simplicity"| DPO["✅ DPO"]
    Q3 --> |"Robustness"| IPO["✅ IPO"]

    Q5 --> |"Yes"| SPIN["✅ SPIN"]
    Q5 --> |"No"| SFT_FIRST["Do SFT first,<br/>then revisit"]

    style Q1 fill:#E8F4F8
    style DPO fill:#C8E6C9
    style PPO fill:#FFE0B2
    style KTO fill:#E1BEE7
    style ORPO fill:#B3E5FC
    style IPO fill:#FFF9C4
    style SPIN fill:#FFCDD2
    style SFT_FIRST fill:#CFD8DC
```

---

## Key Takeaways Diagram

```mermaid
mindmap
  root((RLHF))
    Core Pipeline
      Stage 1: SFT
        Instruction following
        Curated demonstrations
      Stage 2: Reward Model
        Human preferences
        Bradley-Terry loss
        Scalar reward output
      Stage 3: PPO
        Policy optimization
        KL divergence penalty
        Reward maximization
    Modern Alternatives
      DPO
        No reward model
        Simple loss function
        Default choice
      ORPO
        No reference model
        Lowest memory
        Built-in SFT
      KTO
        Unpaired data
        Prospect theory
        Practical
      IPO
        Robust DPO
        Squared loss
        Anti-overfit
    Advanced Topics
      Scaling
        LoRA / QLoRA
        DeepSpeed ZeRO
        Distributed PPO
      Multi-Objective
        Helpfulness vs Safety
        Constraint optimization
        Llama 2 approach
      Constitutional AI
        Self-critique
        No human annotators
        Principle-based
    Production
      Reward Hacking
        Length gaming
        Sycophancy
        Style exploitation
      Evaluation
        MT-Bench
        AlpacaEval
        Red-teaming
      Key Libraries
        trl
        transformers
        peft
        deepspeed
```
