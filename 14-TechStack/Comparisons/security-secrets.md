# Secrets & Identity
- Secret Manager vs env vars vs files; prefer SM + workload identity.
- Workload Identity Federation for CI; short-lived tokens.
- Decision: never bake secrets; use SM + IAM; rotate via CI.
