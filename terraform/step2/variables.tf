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

variable "s3_bucket_name" {
  type = string
}

variable "ecs_task_role_name" {
  type = string
}
