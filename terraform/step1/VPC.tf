# CREATE VPC
resource "aws_vpc" "project_vpc" {
  cidr_block                           = var.vpc_cidr_block
  enable_dns_hostnames                 = true
  enable_network_address_usage_metrics = true
  enable_dns_support                   = true
  tags = {
    Name = "${var.project_name}-${var.vpc_name}"
  }
}

# CREATE INTERNET GATEWAY for the public subnets
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.project_vpc.id
  tags = {
    Name = "${var.project_name}-${var.vpc_name}-igw"
  }
}

# CREATE ELASTIC IP for nat
resource "aws_eip" "nat_eip" {
  vpc = true
  tags = {
    Name = "${var.project_name}-${var.vpc_name}-eip"
  }
  depends_on = [aws_internet_gateway.igw]
}

# CREATE NAT GATEWAY
resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet[0].id
  tags = {
    Name = "${var.project_name}-${var.vpc_name}-nat"
  }
  depends_on = [aws_internet_gateway.igw]
}



# ========================== PRIVATE SUBNETS ======================= #

# Create Private Subnets
resource "aws_subnet" "private_subnet" {
  count                   = length(var.vpc_private_subnets)
  vpc_id                  = aws_vpc.project_vpc.id
  cidr_block              = var.vpc_private_subnets[count.index]
  availability_zone       = var.availability_zones[count.index % length(var.availability_zones)]
  map_public_ip_on_launch = false
  tags = {
    Name = "${var.project_name}-${var.vpc_name}-private-subnet-${count.index}"
  }
}

# ROUTE TABLES for private Subnets
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.project_vpc.id
  tags = {
    Name = "${var.vpc_name}-private-route-table"
  }
}

resource "aws_route" "private_nat_gateway" {
  route_table_id         = aws_route_table.private_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat_gateway.id
}

resource "aws_route_table_association" "private_subnet_association" {
  count          = length(aws_subnet.private_subnet)
  route_table_id = aws_route_table.private_route_table.id
  subnet_id      = aws_subnet.private_subnet[count.index].id
}



# ========================== PUBLIC SUBNETS ======================= #

#Create Public Subnets
resource "aws_subnet" "public_subnet" {
  count                   = length(var.vpc_public_subnets)
  cidr_block              = var.vpc_public_subnets[count.index]
  vpc_id                  = aws_vpc.project_vpc.id
  availability_zone       = var.availability_zones[count.index % length(var.availability_zones)]
  map_public_ip_on_launch = false
  tags = {
    Name = "${var.project_name}-${var.vpc_name}-public-subnet-${count.index}"
  }
}

# ROUTE TABLES for public Subnets
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.project_vpc.id
  tags = {
    Name = "${var.vpc_name}-public-route-table"
  }
}

resource "aws_route" "public_internet_gateway" {
  route_table_id         = aws_route_table.public_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_subnet_association" {
  count          = length(aws_subnet.public_subnet)
  subnet_id      = aws_subnet.public_subnet[count.index].id
  route_table_id = aws_route_table.public_route_table.id
}



# ========================== DEFAULT SG ======================= #

# VPC's Default Security Group
resource "aws_security_group" "default" {
  name        = "${var.vpc_name}-default-sg"
  description = "Default security group to allow inbound/outbound from the VPC"
  vpc_id      = aws_vpc.project_vpc.id
  ingress {
    from_port = "0"
    to_port   = "0"
    protocol  = "-1"
    self      = true
  }
  egress {
    from_port = "0"
    to_port   = "0"
    protocol  = "-1"
    self      = "true"
  }
  tags = {
    Name = "${var.vpc_name}-default-sg"
  }
  depends_on = [aws_vpc.project_vpc]
}
