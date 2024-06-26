#VARIABLES

variable "aws_region" {
  type = string
}

variable "project_name" {
  type = string
}

variable "vpc_name" {
  type = string
}

variable "vpc_cidr_block" {
  type = string
}

variable "vpc_private_subnets" {
  type = list(string)
}

variable "vpc_public_subnets" {
  type = list(string)
}

variable "availability_zones" {
  type = list(string)
}
