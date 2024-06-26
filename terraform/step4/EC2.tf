# PEM key
resource "tls_private_key" "rsa_key_for_ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "${var.vpc_name}-EC2-instance-SSH-key"
  public_key = tls_private_key.rsa_key_for_ssh.public_key_openssh
}

resource "local_file" "ssh_private_key" {
  content  = tls_private_key.rsa_key_for_ssh.private_key_pem
  filename = "${path.module}/Pem_key/dtm.pem"
}


# # TEST EC2 on private subnet
# resource "aws_instance" "ec2-private" {
#   ami                         = var.private_ec2_instance_ami
#   instance_type               = "t2.micro"
#   key_name                    = aws_key_pair.ssh_key.key_name
#   subnet_id                   = var.vpc_private_subnets[0]
#   vpc_security_group_ids      = [var.ec2_sec_grp]
#   iam_instance_profile        = "${var.project_name}-ec2-profile"
#   user_data                   = file("${path.module}/Userdata/ec2-base.sh")
#   associate_public_ip_address = false

#   root_block_device{
#     volume_size = "40"
#   }

#   metadata_options {
#     http_endpoint = "enabled"
#     http_tokens   = "required"
#   }

#   tags = {
#     Name = "${var.project_name}-ec2-private-test"
#   }
# }


# TEST EC2 on Public subnet
resource "aws_instance" "ec2-public" {
  ami           = var.public_ec2_instance_ami
  instance_type = "t2.micro"
  tags = {
    Name = "ec2-public-test-dtm"
  }
  root_block_device {
    volume_size = "40"
  }
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
  key_name                    = aws_key_pair.ssh_key.key_name
  subnet_id                   = var.vpc_public_subnets[0]
  vpc_security_group_ids      = [var.ec2_sec_grp]
  associate_public_ip_address = true
}


#Elastic IP for Public EC2
resource "aws_eip" "ec2-eip" {
  instance = aws_instance.ec2-public.id
  vpc      = true
  tags = {
    "Name" = "${var.project_name}-public-ec2-eip"
  }
}
