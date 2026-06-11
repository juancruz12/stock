variable "project_id" {
  type        = string
  description = "emil-ai-preprod"
}

variable "environment" {
  type        = string
  description = "preprod"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "emilAiDatabase"
}

variable "image_tag" {
  type        = string
  description = "958d4f16309b05e98ccb2e6502cf0899f94c1502"
}