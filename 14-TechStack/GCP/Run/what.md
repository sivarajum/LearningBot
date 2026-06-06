# Google Cloud Run: Comprehensive Guide

## Overview

Cloud Run is a fully managed serverless platform that automatically scales stateless containers. It abstracts away infrastructure management, allowing you to focus on code while paying only for what you use.

## Core Concepts

### What is Google Cloud Run?

Cloud Run is a fully managed serverless platform that automatically scales stateless containers. It abstracts away infrastructure management, allowing you to focus on code while paying only for what you use.

## Key Features

**Serverless**: No infrastructure management

**Auto-scaling**: Scales to zero and up automatically

**Container-based**: Run any containerized application

**Pay-per-use**: Pay only for request processing time

**HTTPS**: Automatic SSL certificates

**Integration**: Works with Cloud Build and other GCP services

## Installation

# Deploy container to Cloud Run
gcloud run deploy SERVICE_NAME \
    --image gcr.io/PROJECT_ID/IMAGE \
    --platform managed \
    --region us-central1

# Deploy from source
gcloud run deploy SERVICE_NAME \
    --source . \
    --platform managed

## Getting Started

```python
# Flask app for Cloud Run
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Cloud Run!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
```

## Advanced Usage

```yaml
# Cloud Run service configuration
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/my-app
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
```

## Best Practices

1. Make containers stateless
2. Use environment variables for configuration
3. Set appropriate CPU and memory limits
4. Implement health checks
5. Use Cloud Run Jobs for batch processing
6. Configure concurrency appropriately
7. Use Cloud Run for both HTTP and gRPC services

## References

- Official documentation: 
- GitHub repository:
