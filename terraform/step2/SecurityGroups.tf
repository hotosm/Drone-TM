# EC2 security group
resource "aws_security_group" "ec2_sec_grp" {
  name_prefix = "${var.project_name}-ec2_sec_grp"
  description = "Allow ssh for EC2"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ec2_sec_grp"
  }
}

# RDS security group
resource "aws_security_group" "psql_sec_grp" {
  name_prefix = "${var.project_name}-psql_sec_grp"
  description = "Allow PostgreSQL access"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-psql_sec_grp"
  }
}

# Document DB Security group
resource "aws_security_group" "doc_db_sec_grp" {
  name_prefix = "${var.project_name}-doc_db_sec_grp"
  description = "Allow Document DB access"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-doc_db_sec_grp"
  }
}

# ElastiCache Redis DB Security group
resource "aws_security_group" "redis_sec_grp" {
  name_prefix = "${var.project_name}-redis_sec_grp"
  description = "Allow Elasticache"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6380
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-redis_sec_grp"
  }
}

# ECS security group
resource "aws_security_group" "ecs_sec_grp" {
  name_prefix = "${var.project_name}-ecs_sec_grp"
  description = "Allow ECS traffic"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8005
    to_port     = 8005
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ecs_sec_grp"
  }
}

# Load Balancer Security Group
resource "aws_security_group" "load_balancer_sec_grp" {
  name_prefix = "${var.project_name}-load_balancer_sec_grp"
  description = "Allow ALB HTTP and HTTPS"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-load_balancer_sec_grp"
  }
}
