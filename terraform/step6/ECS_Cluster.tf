#CREATE NAMESPACE
resource "aws_service_discovery_http_namespace" "namespace" {
  name        = "${var.project_name}-${var.vpc_name}-namespace"
  description = "Namespace for service discovery"
}

# Create a new ECS cluster
resource "aws_ecs_cluster" "cluster" {
  name = var.ecs_cluster_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}
