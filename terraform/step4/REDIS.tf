# Redis subnet group
resource "aws_elasticache_subnet_group" "redis_subnet_grp" {
  name        = "${var.project_name}-redis-subnet-grp"
  description = "Subnet group for redis databases"
  subnet_ids  = var.vpc_private_subnets[*]
  tags = {
    Name = "${var.project_name}-redis-subnet-grp"
  }
}


# Redis-main
resource "aws_elasticache_cluster" "redis-main" {
  cluster_id           = "${var.project_name}-redis-main-cluster"
  engine               = "redis"
  node_type            = "cache.t2.small"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis4.0"
  engine_version       = "4.0.10"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet_grp.id
  security_group_ids   = [var.redis_sec_grp]
  apply_immediately    = true

  tags = {
    Name = "${var.project_name}-redis-main-cluster"
  }
}
