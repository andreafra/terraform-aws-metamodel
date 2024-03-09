terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.40.0"
    }
  }
}

# propose a terraform AWS infrastructure where there are 3 instances on different subnets
# that communicate with each other via HTTPS, with one of them accessing the internet and
# the other two not.

provider "aws" {
  region = "eu-west-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.0.0/24"
}

resource "aws_subnet" "main2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "main3" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "main" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.main.id
}

resource "aws_route_table_association" "main2" {
  subnet_id      = aws_subnet.main2.id
  route_table_id = aws_route_table.main.id
}

resource "aws_route_table_association" "main3" {
  subnet_id      = aws_subnet.main3.id
  route_table_id = aws_route_table.main.id
}

resource "aws_security_group" "main" {
  name   = "main"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "main2" {
  name   = "main2"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "main3" {
  name   = "main3"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "main" {
  ami                    = "ami-0c2b8ca1dad447f8a"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.main.id
  vpc_security_group_ids = [aws_security_group.main.id]
}

resource "aws_instance" "main2" {
  ami                    = "ami-0c2b8ca1dad447f8a"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.main2.id
  vpc_security_group_ids = [aws_security_group.main2.id]
}

resource "aws_instance" "main3" {
  ami                    = "ami-0c2b8ca1dad447f8a"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.main3.id
  vpc_security_group_ids = [aws_security_group.main3.id]
}

resource "aws_eip" "main" {
  vpc = true
}

resource "aws_eip" "main2" {
  vpc = true
}

resource "aws_eip" "main3" {
  vpc = true
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.main.id
  subnet_id     = aws_subnet.main.id
}

resource "aws_nat_gateway" "main2" {
  allocation_id = aws_eip.main2.id
  subnet_id     = aws_subnet.main2.id
}

resource "aws_nat_gateway" "main3" {
  allocation_id = aws_eip.main3.id
  subnet_id     = aws_subnet.main3.id
}
