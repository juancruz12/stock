terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0" # O la versión estable actual
    }
  }
  # Bloque de backend para guardar el estado en el bucket que creaste
  backend "gcs" {
    bucket = "emil-ai-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = "project-76b5e515-21a1-4a89-82f"
  region  = "us-central1"
}

# Proveedor secundario exclusivo para recursos en us-east1
provider "google" {
  alias   = "us_east1" # <--- Este es el nombre clave
  project = "project-76b5e515-21a1-4a89-82f"
  region  = "us-east1"
}