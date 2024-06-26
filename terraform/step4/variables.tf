#VARIABLES

variable "project_name" {
  type = string
}

variable "vpc_name" {
  type = string
}

variable "vpc_private_subnets" {
  type = list(string)
}

variable "vpc_public_subnets" {
  type = list(string)
}

variable "ec2_sec_grp" {
  type = string
}


variable "psql_sec_grp" {
  type = string
}

variable "docdb_sec_grp" {
  type = string
}

variable "redis_sec_grp" {
  type = string
}


variable "public_ec2_instance_ami" {
  type = string
}

variable "private_ec2_instance_ami" {
  type = string
}


# variable "document_db_root_username" {
#   type = string
# }

# variable "document_db_root_password" {
#   type = string
# }

variable "postgresql_root_username" {
  type = string
}

variable "postgresql_root_password" {
  type = string
}
