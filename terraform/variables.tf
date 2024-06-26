# ====================== GLOBALS ==================== #

variable "aws_region" {
  type    = string
  default = "your_aws_region"
}

variable "aws_account" {
  type    = string
  default = "aws_account_id"
}

variable "project_name" {
  type    = string
  default = "your_project_name"
}


# ====================== VPC ==================== #
variable "vpc_name" {
  type    = string
  default = "your_vpc_name"
}

variable "vpc_cidr_block" {
  type    = string
  default = "vpccidrblock"
}

variable "vpc_private_subnets" {
  type    = list(string)
  default = ["vpcprivatecidrblock"]
}

variable "vpc_public_subnets" {
  type    = list(string)
  default = ["vpcpubliccidrblock"]
}

variable "availability_zones" {
  type    = list(string)
  default = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
}


# ====================== ECR ==================== #
variable "ecr_names" {
  type    = list(string)
  default = ["your_ecr_name"]
}



# # ====================== EFS ==================== #
# variable "efs_creation_token" {
#   type        = string
#   default     = "zite-data"
#   description = "Creation token for the EFS file system"
# }

# ====================== EC2 ==================== #
variable "public_ec2_instance_ami" {
  type    = string
  default = "yourec2_public_ami_image_name" #Ubuntu Server 22.04 LTS
}

variable "private_ec2_instance_ami" {
  type    = string
  default = "your_ec2_private_ami_name" #Ubuntu Server 22.04 LTS
}


# ====================== ECS ==================== #
variable "ecs_cluster_name" {
  type        = string
  default     = "dtm-ecs-cluster"
  description = "Cluster name for ECS cluster"
}

variable "ecs_loadbalancer_name" {
  type        = string
  default     = "dtm-load-balancer"
  description = "Cluster name for ECS cluster"
}

variable "ecs_task_role_name" {
  type        = string
  default     = "dtmecsTaskExecutionRole"
  description = "IAM role used in the ECS Tasks"
}


# ====================== ALB ==================== #
variable "SSL_certificate_arn" {
  type        = string
  description = "SSL Certificate ARN for zite.zite.io"
  default     = "ssl-certificate-arn"
}


# ====================== S3 ==================== #
variable "s3_bucket_name" {
  type    = string
  default = "s3bucketname"
}


variable "postgresql_root_username" {
  type        = string
  default     = "postgresusername"
  description = "Root username for PostgreSQL"
}

variable "postgresql_root_password" {
  type        = string
  default     = "postgrespassword"
  description = "Root user password for PostgreSQL"
}
