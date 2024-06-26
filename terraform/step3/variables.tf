#VARIABLES

variable "ecr_names" {
  type = list(string)
}

variable "kms_key" {
  type = string
}
