# Modules

# VPC
module "step1" {
  source              = "./step1/"
  aws_region          = var.aws_region
  vpc_name            = var.vpc_name
  vpc_cidr_block      = var.vpc_cidr_block
  vpc_private_subnets = var.vpc_private_subnets
  vpc_public_subnets  = var.vpc_public_subnets
  availability_zones  = var.availability_zones
  project_name        = var.project_name
}

# ECR - KMS - IAM Roles/Policies - S3 - SECURITY GROUPS
module "step2" {
  source             = "./step2/"
  project_name       = var.project_name
  aws_account        = var.aws_account
  aws_region         = var.aws_region
  vpc_name           = var.vpc_name
  vpc_id             = module.step1.vpc_id
  s3_bucket_name     = var.s3_bucket_name
  ecs_task_role_name = var.ecs_task_role_name
  depends_on         = [module.step1]
}

# ECR
module "step3" {
  source     = "./step3/"
  ecr_names  = var.ecr_names
  kms_key    = module.step2.kms_key.arn
  depends_on = [module.step2]
}

# EC2 - REDIS - POSTGRESQL
module "step4" {
  source                    = "./step4/"
  public_ec2_instance_ami   = var.public_ec2_instance_ami
  private_ec2_instance_ami  = var.private_ec2_instance_ami
  project_name              = var.project_name
  vpc_name                  = var.vpc_name
  vpc_private_subnets       = module.step1.private_subnets_id
  vpc_public_subnets        = module.step1.public_subnets_id
  ec2_sec_grp               = module.step2.ec2_sec_grp.id
  psql_sec_grp              = module.step2.psql_sec_grp.id
  docdb_sec_grp             = module.step2.docdb_sec_grp.id
  redis_sec_grp             = module.step2.redis_sec_grp.id
  # document_db_root_username = var.document_db_root_username
  # document_db_root_password = var.document_db_root_password
  postgresql_root_username  = var.postgresql_root_username
  postgresql_root_password  = var.postgresql_root_password
}

# ECS - EFS - ALB
module "step6" {
  source                    = "./step6/"
  project_name              = var.project_name
  aws_account               = var.aws_account
  aws_region                = var.aws_region
  vpc_name                  = var.vpc_name
  vpc_id                    = module.step1.vpc_id
  vpc_private_subnets       = module.step1.private_subnets_id
  vpc_public_subnets        = module.step1.public_subnets_id
  vpc_private_subnets_count = var.vpc_private_subnets
  ecs_cluster_name          = var.ecs_cluster_name
  ecs_loadbalancer_name     = var.ecs_loadbalancer_name
  ecs_task_role_name        = module.step2.ecs_final_role_name
  ecs_sec_grp               = module.step2.ecs_sec_grp.id
  alb_logs_s3_bucket        = module.step2.alb_logs_s3_bucket.id
  kms_key                   = module.step2.kms_key.arn
  load_balancer_sec_grp     = module.step2.load_balancer_sec_grp.id
  SSL_certificate_arn       = var.SSL_certificate_arn
  s3_bucket_name            = var.s3_bucket_name
  depends_on                = [module.step4]
}
