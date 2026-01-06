/**
 * GCP Infrastructure for Tree Management API
 *
 * Creates:
 * - GCS bucket for data persistence
 * - Service account with minimal permissions
 * - IAM bindings for secure access
 *
 * PRODUCTION BEST PRACTICES:
 * - This Terraform should be executed by a dedicated service account with minimal permissions
 * - Apply changes via CI/CD pipeline (GitHub Actions, GitLab CI, Cloud Build)
 * - Use remote state backend (GCS) with state locking
 * - Implement approval workflows for production changes
 * - Never apply manually in production environments
 *
 * Example CI/CD setup:
 *   1. Store Terraform state in GCS bucket with versioning
 *   2. Use Workload Identity Federation for GitHub Actions
 *   3. Require PR approval before terraform apply
 *   4. Run terraform plan on every PR
 */

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GCS bucket for tree data storage
resource "google_storage_bucket" "tree_data" {
  name          = "${var.project_id}-tree-api-data"
  location      = var.region
  force_destroy = var.environment == "dev" ? true : false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    environment = var.environment
    application = "tree-api"
    managed_by  = "terraform"
  }
}

# Service account for the API
resource "google_service_account" "tree_api" {
  account_id   = "tree-api-${var.environment}"
  display_name = "Tree API Service Account (${var.environment})"
  description  = "Service account for Tree Management API"
}

# Grant service account access to the bucket
resource "google_storage_bucket_iam_member" "tree_api_bucket_access" {
  bucket = google_storage_bucket.tree_data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.tree_api.email}"
}

# Output values for application configuration
output "bucket_name" {
  description = "Name of the GCS bucket for tree data"
  value       = google_storage_bucket.tree_data.name
}

output "service_account_email" {
  description = "Email of the service account"
  value       = google_service_account.tree_api.email
}

output "bucket_url" {
  description = "URL of the GCS bucket"
  value       = "gs://${google_storage_bucket.tree_data.name}"
}

