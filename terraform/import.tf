import {
  id = "projects/${var.project_id}/instances/emil-ai-postgres-${var.environment}"
  to = google_sql_database_instance.db
}
