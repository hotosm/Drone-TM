#Subnet Groups for DB
resource "aws_db_subnet_group" "db_subnet_grp" {
  name        = "${var.project_name}-db-subnetgrp"
  description = "Subnet group for databases"
  subnet_ids  = var.vpc_public_subnets[*]
  tags = {
    Name = "${var.project_name}-db-subnetgrp"
  }
}

#Document DB parameter group
# resource "aws_docdb_cluster_parameter_group" "doc_db_pmg" {
#   family      = "docdb5.0"
#   name        = "${var.project_name}-document-db-pmg"
#   description = "docdb cluster parameter group for ${var.project_name}"

#   parameter {
#     name  = "tls"
#     value = "disabled"
#   }
# }

# #Document DB cluster
# resource "aws_docdb_cluster" "docdb" {
#   cluster_identifier              = "${var.project_name}-docdb-cluster"
#   engine                          = "docdb"
#   master_username                 = var.document_db_root_username
#   master_password                 = var.document_db_root_password
#   backup_retention_period         = 7
#   preferred_backup_window         = "01:15-02:15"
#   skip_final_snapshot             = true
#   deletion_protection             = false
#   db_subnet_group_name            = aws_db_subnet_group.db_subnet_grp.id
#   vpc_security_group_ids          = [var.docdb_sec_grp]
#   db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.doc_db_pmg.name
# }

#Add Instance to DocumentDB cluster
# resource "aws_docdb_cluster_instance" "docdb_cluster_instances" {
#   count              = 1
#   identifier         = "docdb-cluster-${var.project_name}-${count.index}"
#   cluster_identifier = aws_docdb_cluster.docdb.id
#   instance_class     = "db.t3.medium"
# }

# PostgreSQL
resource "aws_db_instance" "postgresql_cluster" {
  identifier                      = "${var.project_name}-db-postgresql"
  allocated_storage               = 45
  max_allocated_storage           = 100
  engine                          = "postgres"
  engine_version                  = "16.2" # The new version is 14.6-R1 - Please Sijan double check
  auto_minor_version_upgrade      = false
  instance_class                  = "db.t3.micro"
  db_name                         = "dbadmin"
  username                        = var.postgresql_root_username
  password                        = var.postgresql_root_password
  skip_final_snapshot             = true
  apply_immediately               = true
  deletion_protection             = false
  publicly_accessible             = true
  delete_automated_backups        = false
  backup_retention_period         = 7
  backup_window                   = "01:15-02:15"
  db_subnet_group_name            = aws_db_subnet_group.db_subnet_grp.id
  vpc_security_group_ids          = [var.psql_sec_grp]
  enabled_cloudwatch_logs_exports = [
    "postgresql",
  ]
  tags                            = {
    Name = "${var.project_name}-db-postgresql"
  }
}
