terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

# ---------------------------------------------------------------------------
# BigQuery dataset
# ---------------------------------------------------------------------------

resource "google_bigquery_dataset" "main" {
  project    = var.project_id
  dataset_id = var.dataset_id
  location   = var.location

  description = "POC-10: Schema evolution harness dataset. Managed by Terraform."

  # Safety: do not destroy data on terraform destroy without confirmation.
  delete_contents_on_destroy = false

  labels = {
    env = "dev"
    poc = "poc10"
    managed_by = "terraform"
  }
}

# ---------------------------------------------------------------------------
# Service Account for the pipeline
# ---------------------------------------------------------------------------

resource "google_service_account" "pipeline_sa" {
  project      = var.project_id
  account_id   = "poc10-pipeline-sa"
  display_name = "POC-10 Pipeline Service Account"
  description  = "Used by the idempotent load pipeline and migration runner."
}

# ---------------------------------------------------------------------------
# IAM: grant the SA dataEditor on the dataset (covers insert, update, query)
# ---------------------------------------------------------------------------

resource "google_bigquery_dataset_iam_binding" "editor" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.main.dataset_id
  role       = "roles/bigquery.dataEditor"

  members = [
    "serviceAccount:${google_service_account.pipeline_sa.email}",
  ]
}

# ---------------------------------------------------------------------------
# IAM: grant the SA dataViewer (belt-and-suspenders for SELECT workloads)
# ---------------------------------------------------------------------------

resource "google_bigquery_dataset_iam_binding" "viewer" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.main.dataset_id
  role       = "roles/bigquery.dataViewer"

  members = [
    "serviceAccount:${google_service_account.pipeline_sa.email}",
  ]
}

# ---------------------------------------------------------------------------
# IAM: grant the SA jobUser at project level so it can run BQ query jobs
# ---------------------------------------------------------------------------

resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# ---------------------------------------------------------------------------
# Baseline trades table (v0 schema)
# ---------------------------------------------------------------------------

resource "google_bigquery_table" "trades" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.main.dataset_id
  table_id   = "trades"

  description = "Baseline trades table. Schema evolves via migration runner."

  schema = jsonencode([
    {
      name = "trade_id"
      type = "STRING"
      mode = "REQUIRED"
      description = "Unique trade identifier."
    },
    {
      name = "symbol"
      type = "STRING"
      mode = "REQUIRED"
      description = "Instrument symbol (e.g. RELIANCE, NSE:NIFTY50)."
    },
    {
      name = "amount"
      type = "FLOAT64"
      mode = "REQUIRED"
      description = "Trade notional amount in base currency."
    },
    {
      name = "ccy"
      type = "STRING"
      mode = "REQUIRED"
      description = "Currency code (ISO 4217). Deprecated in v2 — use currency_code."
    },
    {
      name = "traded_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
      description = "UTC timestamp of trade execution."
    },
    {
      name = "_load_id"
      type = "STRING"
      mode = "REQUIRED"
      description = "Idempotency key set by the pipeline load job."
    }
  ])

  deletion_protection = false

  labels = {
    env = "dev"
    poc = "poc10"
  }

  depends_on = [google_bigquery_dataset.main]
}
