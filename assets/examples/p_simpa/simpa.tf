terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.40.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "net1" {
  cidr_block = "10.0.0.0/28"
}

resource "aws_subnet" "subnet1" {
  vpc_id     = aws_vpc.net1.id
  cidr_block = "10.0.0.0/28"
}

# create a vm instance with a centos ami, 2 cpu and 8 GB of memory, with an interface connected to net1

resource "aws_instance" "vm1" {
  ami                    = "ami-0b0dcb5067f052a63"
  instance_type          = "t2.micro"
  vpc_security_group_ids = []
  subnet_id              = aws_subnet.subnet1.id
}

