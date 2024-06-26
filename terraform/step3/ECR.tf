# CREATE AWS PRIVATE REPO
resource "aws_ecr_repository" "private_repo" {
  count = length(var.ecr_names)
  name  = var.ecr_names[count.index]
  #image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = var.kms_key
  }
  tags = {
    Name = "Private ECR Repository for ${var.ecr_names[count.index]}"
  }
}


resource "aws_ecr_lifecycle_policy" "only_3_image" {
  count      = length(aws_ecr_repository.private_repo)
  repository = aws_ecr_repository.private_repo.* [count.index].name
  depends_on = [aws_ecr_repository.private_repo]
  policy     = <<EOF
  {
    "rules": [
      {
        "rulePriority": 1,
        "description": "Save 3 copies of tagged images",
        "selection": {
          "tagStatus": "tagged",
          "tagPrefixList": ["master", "staging", "develop", "aws"],
          "countType": "imageCountMoreThan",
          "countNumber": 3
        },
        "action": {
          "type": "expire"
        }
      },
      {
        "rulePriority": 2,
        "description": "Delete all untagged images",
        "selection": {
          "tagStatus": "untagged",
          "countType": "sinceImagePushed",
          "countUnit": "days",
          "countNumber": 1
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }
  EOF
}
