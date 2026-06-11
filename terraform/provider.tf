terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 7.0" # O la versión estable actual
    }
  }
  # El bucket y el prefijo se inyectan por ambiente desde GitHub Actions.
  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

# Proveedor secundario exclusivo para recursos en us-east1
provider "google" {
  alias   = "us_east1" # <--- Este es el nombre clave
  project = var.project_id
  region  = "us-east1"
}