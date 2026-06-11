resource "google_sql_database_instance" "db_prod" {
  name             = "emil-ia-postgres-mvp"
  region           = "us-central1"
  database_version = "POSTGRES_16" # <--- Cambiado de 15 a 16

  settings {
    tier = "db-f1-micro" # Confirmá en la consola si usás db-f1-micro u otro tier (ej. db-custom-1-3840)

    location_preference {
      zone = "us-central1-a" # <--- Esto evita que intente destruirla
    }

    ip_configuration {
      ipv4_enabled = true
    }
  }

  deletion_protection = true # <--- Clave para que nunca te la borre por error
}

resource "google_sql_database" "database" {
  name     = "postgres"
  instance = google_sql_database_instance.db_prod.name
}

resource "google_cloud_run_v2_service" "backend_prod" {
  name     = "stock-api"
  location = "us-central1"

  template {
    # Mantenemos las etiquetas reales del deploy
    labels = {
      "commit-sha" = "958d4f16309b05e98ccb2e6502cf0899f94c1502"
      "managed-by" = "github-actions"
    }

    containers {
      # Imagen exacta que recuperó el plan
      image = "us-central1-docker.pkg.dev/project-76b5e515-21a1-4a89-82f/cloud-run-source-deploy/stock-api:958d4f16309b05e98ccb2e6502cf0899f94c1502"
      
      # Inyección de las variables de entorno para la DB
      env {
        name  = "CLOUD_SQL_CONNECTION_NAME"
        value = "project-76b5e515-21a1-4a89-82f:us-central1:emil-ia-postgres-mvp"
      }
      env {
        name  = "DB_USER"
        value = "postgres"
      }
      env {
        name  = "DB_PASSWORD"
        value = "root" 
      }
      env {
        name  = "DB_NAME"
        value = "postgres"
      }

      # Montado del socket de conexión de Cloud SQL
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    # Declaración del volumen del proxy de Cloud SQL
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = ["project-76b5e515-21a1-4a89-82f:us-central1:emil-ia-postgres-mvp"]
      }
    }
  }
}


resource "google_vertex_ai_reasoning_engine" "agente_rag" {
  provider     = google.us_east1
  display_name = "rag-agent"
  region       = "us-east1"
  description  = "RAG Document Assistant"

  spec {
    # El framework que recuperó el plan
    agent_framework = "google-adk"

    # Mantenemos las especificaciones de despliegue y límites de hardware
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

    # Esta es la especificación del código Python real de tu Agent Garden
    source_code_spec {
      python_spec {
        entrypoint_module = "rag.agent_engine_app"
        entrypoint_object = "agent_engine"
        requirements_file = "rag/app_utils/.requirements.txt"
        version           = "3.12"
      }
    }
  }
  
  # TRUCO DE MAGIA: Como la API de Google genera los class_methods de forma dinámica 
  # basándose en los métodos de tu clase Python (get_session, list_sessions, etc.),
  # le decimos a Terraform que ignore los cambios en esa propiedad para que no se vuelva loco intentando trackear el JSON.
  lifecycle {
    ignore_changes = [
      spec[0].class_methods
    ]
  }
}