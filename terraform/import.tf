import {
  id = "projects/${var.project_id}/instances/emil-ai-postgres-${var.environment}"
  to = google_sql_database_instance.db
}

import {
  id = "projects/${var.project_id}/instances/emil-ai-postgres-${var.environment}/databases/emil_ai_db"
  to = google_sql_database.database
}
