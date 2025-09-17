variable "location" {
  type = string
  default = "europe-west4"
}

variable "environment" {
  type = string
}

variable "gcp_sa_email" {
  type = string
}

variable "cloud_run_proxy_port" {
  type = number
  default = 8000
}

variable "cloud_run_service_name" {
  type = string
}

variable "artifact_reg_repo" {
  type = string
}

variable "artifact_image_name" {
  type = string
}

variable "artifact_image_tag" {
  type = string
}

variable "db_user" {
  type = string
  sensitive = true
}

variable "db_password" {
  type = string
  sensitive = true
}

variable "db_name" {
  type = string
  sensitive = true
}

variable "db_port" {
  type = number
  default = 5432
}

variable "cache_enabled" {
  type = string
}
