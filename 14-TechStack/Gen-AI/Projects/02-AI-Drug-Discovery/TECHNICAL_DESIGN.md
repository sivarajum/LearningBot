# AI Drug Discovery Pipeline — Technical Design Document

**Version:** 1.0 | **Date:** March 6, 2026 | **Status:** Pre-Implementation Blueprint

---

## 1. System Overview

An end-to-end AI drug discovery platform that accelerates the path from disease target identification to clinical candidate selection — combining protein structure prediction (AlphaFold), molecular generation (VAE/Diffusion), virtual screening, ADMET prediction, and multi-agent literature synthesis. Inspired by Insilico Medicine, Recursion, and Isomorphic Labs.

---

## 2. High-Level Architecture

```mermaid
graph TB
    subgraph INPUT["📥 Input Layer"]
        style INPUT fill:#1e3a5f,color:#e0e0e0,stroke:#4a90d9,stroke-width:2px
        DISEASE["🦠 Disease Target<br/>Gene / Protein"]:::blue
        LIT["📚 Literature<br/>PubMed, bioRxiv"]:::green
        PDB["🧬 Protein DB<br/>PDB, UniProt"]:::purple
    end

    subgraph PIPELINE["🧪 5-Stage Discovery Pipeline"]
        style PIPELINE fill:#2d1b4e,color:#e0e0e0,stroke:#8e6cc0,stroke-width:2px
        S1["Stage 1: Target Discovery<br/>BioLinkBERT + Neo4j KG"]:::green
        S2["Stage 2: Structure Prediction<br/>AlphaFold 3 + ESMFold"]:::purple
        S3["Stage 3: Molecule Generation<br/>MolVAE + DiffSBDD"]:::blue
        S4["Stage 4: Virtual Screening<br/>AutoDock-GPU + ADMET"]:::orange
        S5["Stage 5: Clinical Intelligence<br/>Trial Analyzer + Safety"]:::red
    end

    subgraph AGENTS["🤖 CrewAI Agent Team"]
        style AGENTS fill:#1a3a2e,color:#e0e0e0,stroke:#4caf50,stroke-width:2px
        RD["🎯 Research Director<br/>Claude Opus"]:::purple
        LA["📖 Literature Agent<br/>GPT-4o + PubMed RAG"]:::blue
        SA["🧬 Structure Agent<br/>ESMFold API"]:::green
        MA["⚗️ Molecule Agent<br/>RDKit + GenAI"]:::orange
        SC["🔬 Screening Agent<br/>AutoDock + ADMET"]:::red
        CA["🏥 Clinical Agent<br/>Trial Analyzer"]:::teal
    end

    subgraph OUT["📤 Output"]
        style OUT fill:#1a2a3a,color:#e0e0e0,stroke:#42a5f5,stroke-width:2px
        CAND["💊 Drug Candidates<br/>Ranked by score"]:::teal
        RPT["📊 Research Report<br/>PDF + interactive"]:::blue
        DASH["📈 Dashboard<br/>Pipeline progress"]:::green
    end

    INPUT --> PIPELINE
    PIPELINE --> OUT
    AGENTS --> PIPELINE

    S1 --> S2 --> S3 --> S4 --> S5

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0,stroke-width:1px
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32,stroke-width:1px
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100,stroke-width:1px
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A,stroke-width:1px
    classDef red fill:#F44336,color:#fff,stroke:#C62828,stroke-width:1px
    classDef teal fill:#009688,color:#fff,stroke:#00695C,stroke-width:1px
```

---

## 3. Pipeline State Machine

```mermaid
stateDiagram-v2
    [*] --> DiseaseInput : User provides disease/target

    state TargetDiscovery {
        [*] --> LitSearch : PubMed + bioRxiv
        LitSearch --> KGBuild : Neo4j knowledge graph
        KGBuild --> TargetRank : Score druggable targets
        TargetRank --> [*]
    }

    state StructurePrediction {
        [*] --> FetchPDB : Known structures
        FetchPDB --> AlphaFold : Unknown → predict
        AlphaFold --> BindingSite : Identify pockets
        BindingSite --> [*]
    }

    state MoleculeGeneration {
        [*] --> SeedLibrary : ZINC/ChEMBL seeds
        SeedLibrary --> VAEGenerate : MolVAE latent space
        VAEGenerate --> DiffSBDD : Structure-based design
        DiffSBDD --> PPOOptimize : RL optimization
        PPOOptimize --> [*]
    }

    state VirtualScreening {
        [*] --> Docking : AutoDock-GPU
        Docking --> ADMET : Absorption, Distribution...
        ADMET --> ToxFilter : Toxicity prediction
        ToxFilter --> [*]
    }

    state ClinicalIntelligence {
        [*] --> TrialSearch : ClinicalTrials.gov
        TrialSearch --> SafetyProfile : Adverse event analysis
        SafetyProfile --> CandidateRank : Final scoring
        CandidateRank --> [*]
    }

    DiseaseInput --> TargetDiscovery
    TargetDiscovery --> StructurePrediction
    StructurePrediction --> MoleculeGeneration
    MoleculeGeneration --> VirtualScreening
    VirtualScreening --> ClinicalIntelligence
    ClinicalIntelligence --> [*] : 💊 Drug candidates
```

---

## 4. Module Deep Dives

### 4.1 Stage 1: Target Discovery

```mermaid
flowchart LR
    subgraph TD["🎯 Target Discovery"]
        style TD fill:#1a3a2e,color:#e0e0e0,stroke:#4caf50,stroke-width:2px
        PM["PubMed Search<br/>BioLinkBERT NER"]:::green
        BX["bioRxiv Scanner<br/>Recent preprints"]:::green
        KG["Neo4j Knowledge Graph<br/>Disease → Gene → Pathway"]:::purple
        RANK["Target Ranking<br/>Druggability + Novelty"]:::orange
    end

    PM --> KG
    BX --> KG
    KG --> RANK

    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
```

### 4.2 Stage 2: Protein Structure Prediction

```mermaid
flowchart LR
    subgraph SP["🧬 Structure Prediction"]
        style SP fill:#2d1b4e,color:#e0e0e0,stroke:#8e6cc0,stroke-width:2px
        SEQ["Amino Acid Sequence<br/>UniProt"]:::blue
        PDB2["PDB Lookup<br/>Known structures"]:::grey
        AF["AlphaFold 3<br/>Structure prediction<br/>pLDDT confidence"]:::purple
        ESM["ESMFold<br/>Fast backup<br/>Single-sequence"]:::green
        BIND["Binding Site Detection<br/>fpocket / P2Rank"]:::orange
        VISUAL["3D Visualization<br/>py3Dmol"]:::teal
    end

    SEQ --> PDB2
    PDB2 -->|not found| AF
    PDB2 -->|found| BIND
    AF --> BIND
    SEQ --> ESM
    BIND --> VISUAL

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef teal fill:#009688,color:#fff,stroke:#00695C
    classDef grey fill:#546E7A,color:#fff,stroke:#37474F
```

### 4.3 Stage 3: Molecule Generation

```mermaid
flowchart LR
    subgraph MG["⚗️ Molecule Generation"]
        style MG fill:#3a2a1a,color:#e0e0e0,stroke:#ff9800,stroke-width:2px
        ZINC["ZINC / ChEMBL<br/>Seed molecules"]:::blue
        SMILES["SMILES Encoding<br/>Molecular representation"]:::grey
        VAE["MolVAE<br/>Latent space exploration"]:::purple
        DIFF["DiffSBDD<br/>Structure-based diffusion"]:::purple
        PPO["PPO RL Optimizer<br/>QED + SA + Docking"]:::orange
        RDKIT["RDKit Validation<br/>Chemical feasibility"]:::green
    end

    ZINC --> SMILES --> VAE
    VAE --> PPO
    DIFF --> PPO
    PPO --> RDKIT

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef grey fill:#546E7A,color:#fff,stroke:#37474F
```

### 4.4 Stage 4: Virtual Screening

```mermaid
flowchart LR
    subgraph VS["🔬 Virtual Screening"]
        style VS fill:#3a1a1a,color:#e0e0e0,stroke:#ef5350,stroke-width:2px
        MOLS["Generated<br/>Molecules"]:::blue
        DOCK["AutoDock-GPU<br/>Binding affinity"]:::orange
        ADMET2["ADMET Prediction<br/>XGBoost ensemble"]:::green
        TOX["Toxicity Filter<br/>DeepTox model"]:::red
        RANK2["Composite Score<br/>Weighted ranking"]:::purple
    end

    MOLS --> DOCK
    MOLS --> ADMET2
    MOLS --> TOX
    DOCK --> RANK2
    ADMET2 --> RANK2
    TOX --> RANK2

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef red fill:#F44336,color:#fff,stroke:#C62828
```

### 4.5 Stage 5: Clinical Intelligence

```mermaid
flowchart LR
    subgraph CI["🏥 Clinical Intelligence"]
        style CI fill:#1a2a3a,color:#e0e0e0,stroke:#42a5f5,stroke-width:2px
        TRIALS["ClinicalTrials.gov<br/>Historical data"]:::blue
        SAFETY["Safety Profile<br/>Adverse event RAG"]:::red
        PATENT["Patent Landscape<br/>Freedom-to-operate"]:::orange
        REPORT["Final Report<br/>Ranked candidates"]:::green
    end

    TRIALS --> SAFETY --> REPORT
    PATENT --> REPORT

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef red fill:#F44336,color:#fff,stroke:#C62828
```

---

## 5. Multi-Agent Orchestration

```mermaid
sequenceDiagram
    participant U as 👤 Researcher
    participant RD as 🎯 Research Director
    participant LA as 📖 Literature Agent
    participant SA as 🧬 Structure Agent
    participant MA as ⚗️ Molecule Agent
    participant SC as 🔬 Screening Agent
    participant CA as 🏥 Clinical Agent

    U->>RD: "Find drug candidates for KRAS G12C mutation"
    RD->>LA: Search literature for KRAS G12C
    LA-->>RD: 847 papers, 12 key targets, 3 known inhibitors

    RD->>SA: Predict KRAS G12C structure + binding sites
    SA-->>RD: 3D structure (pLDDT=92), 2 binding pockets identified

    RD->>MA: Generate molecules targeting pocket-1
    MA-->>RD: 5,000 molecules generated, 1,200 pass Lipinski

    RD->>SC: Screen 1,200 candidates (docking + ADMET)
    SC-->>RD: Top 50 ranked: best Kd=12nM, ADMET pass=38

    RD->>CA: Check clinical landscape for top 50
    CA-->>RD: 2 similar compounds in Phase II, 5 patents relevant

    RD->>U: 📊 Report: 15 novel candidates, top 5 recommended
```

---

## 6. Technology Justification

| Component | Chosen | Alternative | Why Chosen |
|-----------|--------|-------------|------------|
| **Structure Prediction** | AlphaFold 3 | RoseTTAFold | SOTA accuracy, handles complexes + ligands |
| **Fast Backup** | ESMFold | OmegaFold | Single-sequence (no MSA), 60× faster |
| **Knowledge Graph** | Neo4j | Amazon Neptune | Mature graph DB, Cypher query language, great for bio networks |
| **NER/NLP** | BioLinkBERT | SciBERT | Pre-trained on PubMed + link prediction, domain-specific |
| **Molecule Generation** | MolVAE + DiffSBDD | REINVENT | VAE for exploration + diffusion for structure-based = best coverage |
| **RL Optimization** | PPO | DQN, A2C | Stable, sample-efficient, proven in molecular optimization |
| **Docking** | AutoDock-GPU | Vina, Glide | Free, GPU-accelerated, well-validated |
| **ADMET** | XGBoost ensemble | Random Forest | Higher accuracy on ADMET benchmarks |
| **Multi-agent** | CrewAI | AutoGen | Better role specialization, hierarchical delegation |
| **Literature RAG** | LlamaIndex + PubMed | LangChain | Superior for scientific document indexing |

---

## 7. Data Flow Summary

```mermaid
flowchart TD
    IN["Disease / Gene Target"]:::blue --> TD2["Target Discovery<br/>Neo4j KG + PubMed RAG"]:::green
    TD2 --> SP2["Structure Prediction<br/>AlphaFold 3 + fpocket"]:::purple
    SP2 --> MG2["Molecule Generation<br/>MolVAE + DiffSBDD + PPO"]:::orange
    MG2 --> VS2["Virtual Screening<br/>AutoDock-GPU + ADMET"]:::red
    VS2 --> CI2["Clinical Intelligence<br/>Trials + Safety + Patents"]:::teal
    CI2 --> OUT2["📊 Drug Candidates Report"]:::blue

    classDef blue fill:#2196F3,color:#fff,stroke:#1565C0
    classDef green fill:#4CAF50,color:#fff,stroke:#2E7D32
    classDef orange fill:#FF9800,color:#fff,stroke:#E65100
    classDef purple fill:#9C27B0,color:#fff,stroke:#6A1B9A
    classDef red fill:#F44336,color:#fff,stroke:#C62828
    classDef teal fill:#009688,color:#fff,stroke:#00695C
```

---

## 8. Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Target ID time | < 2 weeks | From disease input to validated target list |
| Molecules generated per run | > 10,000 | MolVAE + DiffSBDD combined output |
| ADMET prediction accuracy | > 85% | Validated against experimental data |
| Docking hit rate | > 15% | Molecules with Kd < 100nM |
| Clinical report time | < 1 day | Automated clinical landscape analysis |
| Pipeline cost per run | < $50 | All compute + API costs |

---

## 9. GenAI Skills Matrix

| Skill | Module | Role |
|-------|--------|------|
| LangGraph | Pipeline orchestrator | 5-stage state machine with branching |
| CrewAI | Agent team | 6-agent hierarchical delegation |
| RAG | Literature search | PubMed + bioRxiv scientific paper retrieval |
| Advanced RAG | Knowledge synthesis | Multi-source fusion, citation tracking |
| LlamaIndex | Document indexing | Scientific paper chunking + querying |
| Embeddings | Similarity search | Protein sequence + molecular embeddings |
| Vector DBs | Pinecone | Protein structures + molecular fingerprints |
| OpenAI GPT | Molecule agent | Code generation for RDKit workflows |
| Claude API | Research Director | High-reasoning orchestration + report writing |
| Gemini API | Fast analysis | Quick ADMET result interpretation |
| Guardrails | Safety | Chemical feasibility + toxicity validation |
| Prompt Engineering | All agents | Domain-specific scientific prompts |
| PEFT Fine-tuning | BioLinkBERT | Domain-specific NER fine-tuning |
| HuggingFace | Models | ESMFold, BioLinkBERT, MolVAE |
| Transfer Learning | ADMET models | General chemistry → drug-specific models |
| Distributed Training | Molecule VAE | Multi-GPU training on ZINC dataset |
| Model Quantization | ESMFold | INT8 for faster structure prediction |
| vLLM | Self-hosted | Fast inference for domain models |
| AWS AI/ML | SageMaker | Training jobs + model hosting |
