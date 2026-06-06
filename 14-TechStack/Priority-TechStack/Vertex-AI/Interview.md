# Vertex AI - Interview Questions (Basic to Advanced)

## 🎯 Interview Preparation Guide

Practice these questions to ace your Vertex AI interviews. Answers are tailored to your POC projects.

---

## 🟢 BASIC LEVEL Questions

### Q1: What is Vertex AI?

**Answer:**
"Vertex AI is Google Cloud's unified machine learning platform that provides end-to-end ML capabilities. It combines AutoML for quick model training and custom training for full control. I used it in Module 02 to train a churn prediction model using AutoML, and in Module 04 for custom training with MLflow integration."

**Key Points:**
- Unified ML platform
- AutoML + Custom training
- Production-ready deployment
- Built-in monitoring

---

### Q2: What's the difference between AutoML and Custom Training?

**Answer:**
"AutoML is a no-code solution where you just provide data and labels, and Vertex AI handles everything - feature engineering, model selection, hyperparameter tuning. Custom Training gives you full control - you write your own code, choose algorithms, and customize the entire pipeline.

In Module 02, I used AutoML for quick prototyping. In Module 04, I used Custom Training because I needed specific preprocessing and wanted to integrate with MLflow for experiment tracking."

**Key Points:**
- AutoML: Fast, no-code, less control
- Custom: Slower, full control, your code
- Choose based on requirements

---

### Q3: How do you deploy a model in Vertex AI?

**Answer:**
"Deployment involves creating an endpoint and deploying the model to it. Here's the process:

1. Register model in Model Registry
2. Create an endpoint
3. Deploy model to endpoint with machine type and scaling config
4. Endpoint provides REST API for predictions

In Module 02, I deployed the AutoML model like this:
```python
endpoint = model.deploy(
    endpoint=aiplatform.Endpoint.create(display_name="churn-endpoint"),
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=10
)
```

The endpoint auto-scales based on traffic and provides sub-100ms latency."

**Key Points:**
- Model Registry → Endpoint → Deployment
- Auto-scaling
- REST API access

---

## 🟡 INTERMEDIATE LEVEL Questions

### Q4: How would you handle model versioning in Vertex AI?

**Answer:**
"Vertex AI Model Registry handles versioning automatically. When you upload a model, you can create multiple versions. Each version tracks:
- Training code
- Hyperparameters
- Training data
- Performance metrics

In production, you can deploy multiple versions with traffic splitting for A/B testing. For example, 90% traffic to v1, 10% to v2, then gradually shift if v2 performs better.

I implemented this in Module 04 where I track model versions in MLflow and then register them in Vertex AI for deployment."

**Key Points:**
- Model Registry versions
- Traffic splitting
- A/B testing capability

---

### Q5: Explain how you would monitor a production model.

**Answer:**
"Vertex AI Model Monitoring provides drift detection and performance tracking. I set it up like this:

1. **Data Drift**: Compare production data distribution with training data
2. **Prediction Drift**: Monitor prediction distribution changes
3. **Feature Attribution**: Track which features drive predictions

In Module 04, I integrated monitoring that:
- Samples 10% of predictions
- Compares feature distributions
- Alerts when drift exceeds 5% threshold
- Triggers retraining pipeline automatically

The monitoring job runs continuously and sends alerts to Cloud Monitoring, which I can view in dashboards."

**Key Points:**
- Drift detection
- Sampling strategy
- Automated alerts
- Integration with monitoring

---

### Q6: How do Vertex AI Pipelines work?

**Answer:**
"Vertex AI Pipelines use Kubeflow Pipelines to create reusable ML workflows. Each pipeline consists of components (data prep, training, evaluation) that run in sequence or parallel.

In Module 04, I designed a pipeline with:
1. Data ingestion from BigQuery
2. Feature engineering
3. Model training
4. Evaluation
5. Conditional deployment (only if accuracy > 80%)

The pipeline is defined as Python functions with decorators, compiled to JSON, and run on Vertex AI. It tracks all artifacts, parameters, and metrics automatically."

**Key Points:**
- Kubeflow Pipelines
- Component-based
- Artifact tracking
- Conditional logic

---

## 🔴 ADVANCED LEVEL Questions

### Q7: How would you design a system for A/B testing ML models in production?

**Answer:**
"Here's my approach:

**Architecture:**
1. Deploy both models to same endpoint with traffic splitting
2. Log predictions with model version ID
3. Track business metrics (conversion, revenue) per model
4. Use statistical tests to determine winner

**Implementation:**
```python
# Deploy v1 with 50% traffic
model_v1.deploy(endpoint, traffic_split={"0": 50})

# Deploy v2 with 50% traffic  
model_v2.deploy(endpoint, traffic_split={"1": 50})

# Monitor metrics
# Gradually shift: 30/70, then 0/100 if v2 wins
```

**Key Considerations:**
- Statistical significance (need enough samples)
- Business metrics, not just accuracy
- Gradual rollout to minimize risk
- Rollback plan if new model fails

I'd implement this with Vertex AI endpoints for traffic management and Cloud Monitoring for metrics tracking."

**Key Points:**
- Traffic splitting
- Metrics tracking
- Statistical significance
- Gradual rollout

---

### Q8: How do you optimize costs for Vertex AI training and serving?

**Answer:**
"Cost optimization strategies:

**Training:**
1. **Preemptible VMs**: 80% cost savings, acceptable for training
2. **Right-sizing**: Use smallest machine that fits your needs
3. **Early stopping**: Stop training when metrics plateau
4. **Spot instances**: For non-critical training jobs

**Serving:**
1. **Scale to zero**: No traffic = no cost (Cloud Run)
2. **Right-sizing**: Use smaller instances when possible
3. **Caching**: Cache predictions to reduce compute
4. **Batch predictions**: For non-real-time use cases

**Example from Module 04:**
```python
# Training with preemptible VMs
job.run(use_preemptible_vms=True)  # 80% savings

# Endpoint with scale-to-zero
endpoint.deploy(
    min_replica_count=0,  # Scale to zero
    max_replica_count=5
)
```

This reduced my training costs by 80% and serving costs by 60% during low-traffic periods."

**Key Points:**
- Preemptible VMs for training
- Scale-to-zero for serving
- Right-sizing
- Caching strategies

---

### Q9: How would you handle model retraining in production?

**Answer:**
"Automated retraining pipeline:

**Trigger Conditions:**
1. Scheduled (weekly/monthly)
2. Data drift detected
3. Performance degradation
4. New data threshold reached

**Pipeline Design:**
```python
# Monitor for drift
if drift_detected or performance_degraded:
    # Trigger retraining pipeline
    pipeline_job = aiplatform.PipelineJob(
        template_path="retrain_pipeline.json"
    )
    pipeline_job.run()
    
    # Evaluate new model
    if new_model_accuracy > current_model_accuracy:
        # Deploy with canary
        deploy_canary(new_model, traffic=10%)
        # Monitor, then full rollout
```

**Key Components:**
- Drift detection (Module 06)
- Automated pipeline trigger
- Model evaluation
- Canary deployment
- Rollback capability

In Module 04, I integrated this with MLflow for experiment tracking and Vertex AI Pipelines for orchestration."

**Key Points:**
- Automated triggers
- Evaluation before deployment
- Canary rollout
- Rollback strategy

---

### Q10: Design a system for real-time ML predictions at scale (1M requests/day).

**Answer:**
"Here's my architecture:

**Components:**
1. **API Gateway**: Rate limiting, authentication
2. **Load Balancer**: Distribute traffic
3. **Vertex AI Endpoint**: Auto-scaling (1-100 replicas)
4. **Caching Layer**: Redis for frequent predictions
5. **Monitoring**: Real-time metrics and alerts

**Flow:**
```
Request → API Gateway → Cache Check → 
  → If miss: Vertex AI Endpoint → Cache Store → Response
  → If hit: Return cached → Response
```

**Scaling:**
- Endpoint auto-scales based on QPS
- Cache reduces endpoint load by 60-70%
- Load balancer handles traffic spikes

**Optimization:**
- Batch similar requests
- Use smaller model instances
- Implement request queuing for bursts

**From Module 04:**
I achieved <100ms latency with this architecture, handling 12 QPS average with peaks up to 50 QPS."

**Key Points:**
- Multi-layer architecture
- Caching strategy
- Auto-scaling
- Performance optimization

---

## 🎯 System Design Questions

### Q11: Design an ML platform using Vertex AI.

**Answer:**
"**Architecture:**

**Data Layer:**
- BigQuery for data warehouse
- Cloud Storage for raw data
- Feature Store for feature management

**Training Layer:**
- Vertex AI Workbench for development
- Vertex AI Training (AutoML + Custom)
- MLflow for experiment tracking
- Model Registry for versioning

**Serving Layer:**
- Vertex AI Endpoints for real-time
- Batch Prediction for large datasets
- API Gateway for access control

**Operations:**
- Vertex AI Pipelines for automation
- Model Monitoring for drift detection
- Cloud Monitoring for observability
- CI/CD with GitHub Actions

**Key Features:**
- Multi-tenant support
- Model versioning
- A/B testing
- Automated retraining
- Cost optimization

This is essentially what I built in Module 04, scaled for enterprise use."

---

## 💡 STAR Framework Examples

### Situation: Implementing ML Pipeline on Vertex AI

**Situation**: Needed to build production ML pipeline for churn prediction.

**Task**: Design and implement end-to-end pipeline using Vertex AI.

**Action**: 
- Used Vertex AI Custom Training with scikit-learn
- Integrated MLflow for experiment tracking
- Built Vertex AI Pipeline for automation
- Set up Model Monitoring for drift detection
- Deployed to Vertex AI Endpoint with auto-scaling

**Result**: 
- Deployed production system with 95% accuracy
- <100ms prediction latency
- Automated retraining on drift detection
- 60% cost reduction with optimization

---

## 📊 Quick Reference

### Key Concepts to Remember

1. **AutoML**: Quick, no-code training
2. **Custom Training**: Full control, your code
3. **Endpoints**: Production serving with auto-scaling
4. **Pipelines**: Automated ML workflows
5. **Monitoring**: Drift detection and alerts
6. **Model Registry**: Versioning and management
7. **Feature Store**: Feature management
8. **Cost Optimization**: Preemptible VMs, scale-to-zero

### Common Interview Topics

- Training vs Serving
- AutoML vs Custom
- Cost optimization
- Monitoring and drift
- A/B testing
- Pipeline design
- Scaling strategies

---

## ✅ Practice Checklist

- [ ] Can explain Vertex AI in 2 minutes
- [ ] Understand AutoML vs Custom Training
- [ ] Know deployment process
- [ ] Understand monitoring
- [ ] Can design pipelines
- [ ] Know cost optimization
- [ ] Can explain your POC usage
- [ ] Ready for system design questions

---

**Remember**: Connect every answer to your actual POC projects. Real experience > theoretical knowledge.

