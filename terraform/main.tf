terraform {
  backend "gcs" {
    bucket = "elifapa-terraform-state"
    prefix = "env/dev/terraform/state"
  }
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.8.0"
    }
  }
}

provider "google" {
  project = "ae-terraform-2025"
  region  = var.location
}

data "google_project" "ae_project" {
}

data "google_artifact_registry_docker_image" "my_image" {
  location      = var.location
  repository_id = var.artifact_reg_repo
  image_name    = "${var.artifact_image_name}:${var.artifact_image_tag}"
}

data "google_compute_default_service_account" "default" {
}

locals {
  onprem = ["77.169.112.68"]
  wibaut_xebia = ["37.17.221.89"]
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database_instance" "postgres_instance" {
  name             = "elif-postgres-instance-${random_id.db_name_suffix.hex}"
  project          = data.google_project.ae_project.project_id
  region           = var.location
  database_version = "POSTGRES_17"  # match Postgres 17.0 image version

  settings {
    tier = "db-custom-1-3840"  # machine type
    ip_configuration {
        ipv4_enabled = true # public IP
        dynamic "authorized_networks" {
            for_each = local.onprem
            iterator = onprem

            content {
              name  = "onprem-${onprem.key}"
              value = onprem.value
            }
        }
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "default_db" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres_instance.name
}

resource "google_sql_user" "default_user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres_instance.name
  password = var.db_password
}

# Enable Cloud SQL Admin API in the project
resource "google_project_service" "cloud_sql_admin" {
  project = data.google_project.ae_project.project_id
  service = "sqladmin.googleapis.com"
  disable_on_destroy = true
}

# Enable Artifact Registry API
resource "google_project_service" "artifact_registry" {
  project = data.google_project.ae_project.project_id
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = true
}

# IAM binding for GitHub Service Account to act as Cloud Run's runtime SA
resource "google_service_account_iam_member" "github_sa_service_account_user" {
  service_account_id = data.google_compute_default_service_account.default.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.gcp_sa_email}"
}

resource "google_cloud_run_v2_service" "easyconvert-api-service" {
  name     = var.cloud_run_service_name
  location = var.location
  ingress = "INGRESS_TRAFFIC_ALL"
  template {
    containers {
      name = var.cloud_run_service_name
      image = data.google_artifact_registry_docker_image.my_image.self_link #"${var.location}-docker.pkg.dev/${data.google_project.ae_project.project_id}/${data.google_artifact_registry_docker_image.my_image.repository_id}/easyconvert-api:latest"
      ports {
        container_port = var.cloud_run_proxy_port
      }
      env {
        name  = "DB_HOST"
        value = "/cloudsql/${google_sql_database_instance.postgres_instance.connection_name}" #unix socket #google_sql_database_instance.postgres_instance.public_ip_address #tcp connection
      }
      env {
        name  = "DB_PORT"
        value = var.db_port
      }
      env {
        name  = "DB_USER"
        value = var.db_user
      }
      env {
        name  = "DB_PASSWORD"
        value = var.db_password
      }
      env {
        name  = "DB_DB"
        value = var.db_name
      }
      env {
        name  = "CACHE_ENABLED"
        value = var.cache_enabled
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres_instance.connection_name]
      }
    }
  }
  deletion_protection = false
  depends_on = [
    google_project_service.cloud_sql_admin,
    google_project_service.artifact_registry,
    google_service_account_iam_member.github_sa_service_account_user
  ]
}

# Bind IAM policy to Cloud Run to allow access only to my user
resource "google_cloud_run_v2_service_iam_binding" "private_access" {
  project  = google_cloud_run_v2_service.easyconvert-api-service.project
  location = google_cloud_run_v2_service.easyconvert-api-service.location
  name     = google_cloud_run_v2_service.easyconvert-api-service.name
  role     = "roles/run.invoker"
  members = [
    # "allUsers",
    "user:eapaydin@xccelerated.io",
    "serviceAccount:${var.gcp_sa_email}"
  ]
}

# # Bind IAM role roles/cloudsql.client for Cloud Run service account
# resource "google_project_iam_member" "cloudsql_client" {
#   project = data.google_project.ae_project.project_id
#   role    = "roles/cloudsql.client"
#   member  = "serviceAccount:${data.google_project.ae_project.number}-compute@developer.gserviceaccount.com"
# }
