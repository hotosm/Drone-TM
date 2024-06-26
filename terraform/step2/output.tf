output "ec2_sec_grp" {
  value = aws_security_group.ec2_sec_grp
}

output "psql_sec_grp" {
  value = aws_security_group.psql_sec_grp
}

output "docdb_sec_grp" {
  value = aws_security_group.doc_db_sec_grp
}

output "redis_sec_grp" {
  value = aws_security_group.redis_sec_grp
}

output "ecs_sec_grp" {
  value = aws_security_group.ecs_sec_grp
}

output "ecs_final_role_name" {
  value = aws_iam_role.ecs_role.name
}

output "load_balancer_sec_grp" {
  value = aws_security_group.load_balancer_sec_grp
}

output "kms_key" {
  value = aws_kms_key.encryption_key_ecr
}

output "kms_key_name" {
  value = aws_kms_alias.kms_alias_ecr
}

output "alb_logs_s3_bucket" {
  value = aws_s3_bucket.alb_logs_s3_bucket
}
