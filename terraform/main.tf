resource "google_sql_database_instance" "db" {
  # El nombre ahora es dinámico: emil-ia-postgres-preprod o emil-ia-postgres-prod
  name             = "emil-ai-postgres-${var.environment}"
  region           = "us-central1"
  database_version = "POSTGRES_16"

  settings {
    tier = "db-f1-micro"
    edition = "ENTERPRISE"

    location_preference {
      zone = "us-central1-a"
    }

    ip_configuration {
      ipv4_enabled = true
    }
  }

  # Para pruebas en pre-prod podrías querer cambiarlo a false, pero lo dejamos true por seguridad
  deletion_protection = false 
}

data "google_project" "current" {
  project_id = var.project_id
}

resource "google_project_iam_member" "cloudrun_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
}

resource "google_sql_user" "postgres_user" {
  name     = "postgres"
  instance = google_sql_database_instance.db.name
  password = var.db_password # Usa exactamente la misma variable que le pasás al contenedor
}

resource "google_sql_database" "database" {
  name     = "emil_ai_db"
  instance = google_sql_database_instance.db.name
}

resource "google_cloud_run_v2_service" "backend" {
  name                = "stock-api-${var.environment}"
  location            = "us-central1"
  deletion_protection = false

  template {
    # 1. Limpiamos las labels quitando el bloque intruso
    labels = {
      "commit-sha" = var.image_tag
      "managed-by" = "github-actions"
    }

    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/cloud-run-source-deploy/stock-api:${var.image_tag}"
      
      env {
        name  = "CLOUD_SQL_CONNECTION_NAME"
        value = google_sql_database_instance.db.connection_name
      }
      env {
        name  = "DB_USER"
        value = "postgres"
      }
      env {
        name  = "DB_PASSWORD"
        value = var.db_password
      }
      env {
        name  = "DB_NAME"
        value = google_sql_database.database.name
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    # 3. El volumen queda apuntando dinámicamente al connection_name nativo
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.db.connection_name]
      }
    }
  }
}

resource "google_vertex_ai_reasoning_engine" "agente_rag" {
  provider     = google.us_east1
  # Nombre dinámico para el agente
  display_name = "rag-agent-${var.environment}"
  region       = "us-east1"
  description  = "RAG Document Assistant - ${var.environment}"

  spec {
    agent_framework = "google-adk"

    deployment_spec {
      container_concurrency = 9
      max_instances         = 10
      min_instances         = 1
      
      resource_limits = {
        "cpu"    = "4"
        "memory" = "8Gi"
      }

      env {
        name  = "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
        value = "true"
      }
      env {
        name  = "GOOGLE_CLOUD_REGION"
        value = "us-east1"
      }
      env {
        name  = "NUM_WORKERS"
        value = "1"
      }
      env {
        name  = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
        value = "true"
      }
    }

    source_code_spec {
      inline_source {
      source_archive = filebase64("${path.module}/build/source.tar.gz")
    }
      python_spec {
        entrypoint_module = "rag.agent_engine_app"
        entrypoint_object = "agent_engine"
        requirements_file = "requirements.txt"
        version           = "3.12"
      }
    }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].class_methods
    ]
  }
}