# Starter: Cloud Build CI for Service
- Goal: build/test Docker image via Cloud Build trigger.
- Steps: cloudbuild.yaml with build+test; trigger on main; store image in Artifact Registry; use digest output.
- Validation: build succeeds; image stored with digest; tests pass.
