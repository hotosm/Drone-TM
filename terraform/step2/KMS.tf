# KMS key for ECR encryption
resource "aws_kms_key" "encryption_key_ecr" {
  description             = "KMS ECR key 1"
  key_usage               = "ENCRYPT_DECRYPT"
  deletion_window_in_days = 7
  is_enabled              = true
  enable_key_rotation     = true
  tags = {
    "Name" = "${var.project_name}-ecr-key"
  }
}

resource "aws_kms_alias" "kms_alias_ecr" {
  name          = "alias/${var.project_name}-ecr-key"
  target_key_id = aws_kms_key.encryption_key_ecr.key_id
}
