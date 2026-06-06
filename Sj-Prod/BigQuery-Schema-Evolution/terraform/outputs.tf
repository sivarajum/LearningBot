output "dataset_id" {
  description = "The BigQuery dataset ID created by this module."
  value       = google_bigquery_dataset.main.dataset_id
}

output "dataset_full_id" {
  description = "Fully qualified dataset ID: {project}.{dataset_id}."
  value       = "${var.project_id}.${google_bigquery_dataset.main.dataset_id}"
}

output "trades_table_id" {
  description = "Fully qualified ID of the baseline trades table."
  value       = "${var.project_id}.${google_bigquery_dataset.main.dataset_id}.trades"
}

output "pipeline_sa_email" {
  description = "Email address of the pipeline service account."
  value       = google_service_account.pipeline_sa.email
}

output "pipeline_sa_name" {
  description = "Full resource name of the pipeline service account."
  value       = google_service_account.pipeline_sa.name
}
