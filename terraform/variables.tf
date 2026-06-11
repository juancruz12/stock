variable "project_id" {
  type        = string
  description = "emil-ai-preprod"
}

variable "environment" {
  type        = string
  description = "preprod"

  validation {
    condition     = contains(["dev", "preprod", "prod"], var.environment)
    error_message = "environment must be dev, preprod, or prod."
  }
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "emilAiDatabase"
}

variable "rag_corpus" {
  type        = string
  description = "projects/<project-number>/locations/us-east1/ragCorpora/<corpus-id>"
}

variable "image_tag" {
  type        = string
  description = "958d4f16309b05e98ccb2e6502cf0899f94c1502"
}