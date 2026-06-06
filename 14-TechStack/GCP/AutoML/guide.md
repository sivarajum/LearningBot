# AutoML Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Quick Setup
```bash
gcloud config set project <PROJECT_ID>
gcloud services enable automl.googleapis.com
```

### 2. Core Capabilities
- Vision (image classification, object detection)
- Natural Language (text classification, entity extraction)
- Tables (tabular prediction), Translation, Video Intelligence

### 3. Basic Flow
1) Import labeled data (GCS/BigQuery)  
2) Train AutoML model (UI/CLI)  
3) Evaluate; iterate on data/labels  
4) Deploy or batch predict

## Level 2 – Production Patterns

### Data & Training
- Clean, balanced datasets; enough examples per class
- Separate train/val/test; avoid leakage; stratified splits
- Hyperparameters auto-managed; iterate with better data/labels

### Deployment
- Batch vs online prediction; choose by latency/volume
- Traffic split for new models; rollback plan
- Model export options (some products) for edge

### Security & Cost
- CMEK support varies by product; check before training
- Control dataset locations; delete stale datasets/models
- Monitor prediction costs; schedule batch when possible

## Level 3 – Architect Playbook

### Governance
- Track datasets, versions, and labeling guidelines
- Maintain model cards: purpose, data, known limitations
- Audit logs; least-privilege IAM; VPC-SC for sensitive data

### Quality & Monitoring
- Evaluate precision/recall per class; confusion matrices
- Monitor drift in input data; re-label and retrain cadence
- A/B model performance; human-in-loop for low confidence

### Integrations
- Pipelines for automated re-training (Vertex Pipelines)
- Serve via endpoints or batch to BigQuery/Storage
- Pair with Feature Store for consistency (tables)

## Ops Cheat Sheet

| Task | Command/Console | Note |
| --- | --- | --- |
| Import data | Console/CLI | GCS/BQ |
| Train | Console/CLI (automated) | choose objective |
| Deploy | `gcloud ai endpoints deploy-model ...` (Vertex) | online |
| Batch predict | `gcloud ai batch-predictions create ...` | offline |
| Evaluate | Console metrics | class-level |

## Architecture Patterns

```mermaid
flowchart LR
  Data[Data (GCS/BQ)] --> Label[Labeling/Prep]
  Label --> Train[AutoML Training]
  Train --> Eval[Evaluation]
  Eval --> Deploy[Endpoint/Batch Predict]
  Deploy --> Monitor[Monitoring/Drift]
  Train --> Registry[Model Registry]
```

## Checklist Before Production
- [ ] Dataset quality checked; class balance acceptable
- [ ] Evaluation reviewed per class; thresholds chosen
- [ ] Deployment mode chosen (batch/online); rollback path
- [ ] IAM least privilege; VPC-SC/CMEK where supported
- [ ] Monitoring for drift/costs; retrain plan defined

## Learning Path Links
- Track: `LearningTracks/MLOps-GCP/track.md`
- Projects: `Projects/GCP-MLOps/starter/01-automl-train.md` and `Projects/Integrated/mlops-gcp-capstone.md`
- Mastery: `Mastery/GCP-AutoML/` (quiz, scenarios, flashcards)

