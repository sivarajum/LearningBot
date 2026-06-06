variable "project_id" {
  description = "GCP project ID that owns the BigQuery resources."
  type        = string
  default     = "ai-trading-prod"
}

variable "dataset_id" {
  description = "BigQuery dataset ID for the schema evolution harness."
  type        = string
  default     = "poc10_schema_evolution"

  validation {
    condition     = can(regex("^[a-zA-Z0-9_]+$", var.dataset_id))
    error_message = "dataset_id may only contain letters, digits, and underscores."
  }
}

variable "location" {
  description = "BigQuery dataset and resource location (multi-region or region)."
  type        = string
  default     = "US"

  validation {
    condition     = contains(["US", "EU", "us-central1", "us-east1", "europe-west1", "asia-east1"], var.location)
    error_message = "location must be one of: US, EU, us-central1, us-east1, europe-west1, asia-east1."
  }
}
