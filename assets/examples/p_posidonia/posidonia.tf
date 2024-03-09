terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.40.0"
    }
  }
}

# initialise an AWS terrform model
provider "aws" {
  region = "us-east-1"
}

# setup a network called vpc
resource "aws_vpc" "vpc" {
  cidr_block = "10.0.0.0/16"
}

# setup 3 subnets called subnet1, subnet2, subnet3
# subnet1 and subnet2 must be able to communicate with each other

resource "aws_subnet" "subnet1" {
  vpc_id     = aws_vpc.vpc.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "subnet2" {
  vpc_id     = aws_vpc.vpc.id
  cidr_block = "10.0.2.0/24"
}

resource "aws_subnet" "subnet3" {
  vpc_id     = aws_vpc.vpc.id
  cidr_block = "10.0.3.0/24"
}

# setup a VM instance that host a database
# and is connected to subnet1, subnet2, subnet3

resource "aws_instance" "database" {
  ami                    = "ami-0c2b8ca1dad447f8a"
  instance_type          = "t2.micro"
  vpc_security_group_ids = [aws_security_group.database.id]
  # create 3 interfaces to connect to the 3 subnets
  network_interface {
    network_interface_id = aws_subnet.subnet1.id
    device_index         = 0
  }

  network_interface {
    network_interface_id = aws_subnet.subnet2.id
    device_index         = 1
  }

  network_interface {
    network_interface_id = aws_subnet.subnet3.id
    device_index         = 2
  }

  security_groups = [aws_security_group.database.id]
}

# setup a aws_launch_configuration for a vm called gestaut
resource "aws_launch_configuration" "gestaut" {
  image_id      = "XXXXXXXXXXXXXXXXXXXXX"
  instance_type = "t2.micro"
  # create a security group called database
  # that allows traffic from the database to the database
  security_groups = [aws_security_group.database.id]
}
# same for elasticsearch
resource "aws_launch_configuration" "elasticsearch" {
  image_id      = "XXXXXXXXXXXXXXXXXXXXX"
  instance_type = "t2.micro"
  # create a security group called database
  # that allows traffic from the database to the database
  security_groups = [aws_security_group.elasticsearch.id]
}
# same for edi
resource "aws_launch_configuration" "edi" {
  image_id      = "XXXXXXXXXXXXXXXXXXXXX"
  instance_type = "t2.micro"
  # create a security group called database
  # that allows traffic from the database to the database
  security_groups = [aws_security_group.edi.id]
}


# setup an autoscaling group for a vm instance called gestaut
resource "aws_autoscaling_group" "gestaut" {
  launch_configuration = aws_launch_configuration.gestaut.name
  vpc_zone_identifier  = [aws_subnet.subnet2.id]
  min_size             = 1
  max_size             = 3
  desired_capacity     = 1
}

resource "aws_autoscaling_group" "elasticsearch" {
  launch_configuration = aws_launch_configuration.elasticsearch.name
  vpc_zone_identifier  = [aws_subnet.subnet1.id]
  min_size             = 1
  max_size             = 3
  desired_capacity     = 1
}

resource "aws_autoscaling_group" "edi" {
  launch_configuration = aws_launch_configuration.edi.name
  vpc_zone_identifier  = [aws_subnet.subnet3.id]
  min_size             = 1
  max_size             = 3
  desired_capacity     = 1
}

# create a security group for instance database
resource "aws_security_group" "database" {
  name = "database"
}

resource "aws_vpc_security_group_egress_rule" "database_out" {
  security_group_id = aws_security_group.database.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 0
  to_port           = 0
  ip_protocol       = -1
}

resource "aws_vpc_security_group_ingress_rule" "database_in" {
  security_group_id = aws_security_group.database.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 1521
  to_port           = 1521
  ip_protocol       = "tcp"
}

resource "aws_security_group" "elasticsearch" {
  name = "elasticsearch"
}

resource "aws_vpc_security_group_egress_rule" "elasticsearch_out" {
  security_group_id = aws_security_group.elasticsearch.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 0
  to_port           = 0
  ip_protocol       = -1
}

resource "aws_vpc_security_group_ingress_rule" "elasticsearch_http" {
  security_group_id = aws_security_group.elasticsearch.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "elasticsearch_https" {
  security_group_id = aws_security_group.elasticsearch.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "elasticsearch_es" {
  security_group_id = aws_security_group.elasticsearch.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 9200
  to_port           = 9200
  ip_protocol       = "tcp"
}


resource "aws_security_group" "edi" {
  name = "edi"
}

resource "aws_vpc_security_group_egress_rule" "edi_out" {
  security_group_id = aws_security_group.edi.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 0
  to_port           = 0
  ip_protocol       = -1
}

resource "aws_vpc_security_group_ingress_rule" "edi_http" {
  security_group_id = aws_security_group.edi.id
  cidr_ipv4         = "84.124.78.66/32"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "edi_https" {
  security_group_id = aws_security_group.edi.id
  cidr_ipv4         = "84.124.78.66/32"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "edi_ftp" {
  security_group_id = aws_security_group.edi.id
  cidr_ipv4         = "84.124.78.66/32"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}
