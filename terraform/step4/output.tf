output "postgres_endpoint" {
  value = aws_db_instance.postgresql_cluster
}

# output "mongo_endpoint" {
#   value = aws_docdb_cluster_instance.docdb_cluster_instances[0].endpoint
# }

output "redis_main_endpoint" {
  value = aws_elasticache_cluster.redis-main.configuration_endpoint
}
