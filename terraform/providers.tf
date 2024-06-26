# Terraform provider

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67.0"
    }
  }
}

provider "aws" {
  # region and profile is for the architecture
  region                   = "ap-south-1"
  shared_credentials_files = ["${path.module}/.aws/credentials"]
  profile                  = "default"


  default_tags {
    tags = {
      Environment = "NAXA-DTM"
      Application = "DTM"
      Team        = "NAXA-Developers"
      Creator     = "NAXA"
      Owner       = "NAXA"
    }
  }
}
