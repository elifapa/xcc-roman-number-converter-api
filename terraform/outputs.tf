output "gcp_project"{
  value = data.google_project.ae_project.project_id
}

output "db_instance_unix_socket" {
  value = google_sql_database_instance.postgres_instance.connection_name
}

output "db_instance_public_ip" {
  value = google_sql_database_instance.postgres_instance.public_ip_address
}

output "my_image" {
  value = data.google_artifact_registry_docker_image.my_image
}

output "service_url" {
  value = google_cloud_run_v2_service.easyconvert-api-service.uri
}
