terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 8.0"
    }
  }
}
variable "project_id" { type = string }
variable "bucket_name" { type = string }
variable "location" {
  type    = string
  default = "US-CENTRAL1"
}
variable "kms_key_name" {
  type    = string
  default = null
}
provider "google" { project = var.project_id }
resource "google_storage_bucket" "records" {
  name                        = var.bucket_name
  location                    = var.location
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  versioning { enabled = true }
  labels = {
    owner          = "records-platform"
    classification = "internal"
    environment    = "test"
  }
  dynamic "encryption" {
    for_each = var.kms_key_name == null ? [] : [var.kms_key_name]
    content { default_kms_key_name = encryption.value }
  }
}
output "bucket_name" { value = google_storage_bucket.records.name }
