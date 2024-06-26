#VARIABLES

variable "project_name" {
  type = string
}

variable "vpc_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "aws_account" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "vpc_private_subnets" {
  type = list(string)
}

variable "vpc_private_subnets_count" {
  type = list(string)
}

variable "vpc_public_subnets" {
  type = list(string)
}

variable "ecs_cluster_name" {
  type = string
}

variable "ecs_loadbalancer_name" {
  type = string
}

variable "ecs_task_role_name" {
  type = string
}

variable "ecs_sec_grp" {
  type = string
}

variable "SSL_certificate_arn" {
  type = string
}

variable "load_balancer_sec_grp" {
  type = string
}


variable "s3_bucket_name" {
  type = string
}

variable "kms_key" {
  type = string
}

# ====================== IMAGES ==================== #

variable "dtm_fastapi_image" {
  type    = string
  default = "dtm-fastapi-image"
}

variable "alb_logs_s3_bucket" {
  type = string
}

# ====================== Routing Rules Domains ==================== #
variable "domain" {
  type    = string
  default = "yourdomain.com"
}

variable "dtm_subdomain" {
  type    = string
  default = "yoursubdomain.com"
}
