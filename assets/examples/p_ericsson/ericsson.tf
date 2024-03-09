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

data "aws_ami" "ubuntu" {
  filter {
    name   = "name"
    values = ["ami-0aedf6b1cb669b4c7"] # Centos
  }

  owners = ["canonical"]
}

# Create a VPC
resource "aws_vpc" "oam" {
  cidr_block = "10.0.0.0/24"
}

resource "aws_vpc" "net1" {

  cidr_block = "10.0.1.0/24"
}

resource "aws_vpc" "net2" {
  cidr_block = "16.0.2.0/24"
}

resource "aws_vpc" "net3" {
  cidr_block = "16.0.3.0/24"
}

# Create subnets for net "oam"
resource "aws_subnet" "subnet_oam_igw" {
  vpc_id     = aws_vpc.oam.id
  cidr_block = "16.0.0.0/26"
}

resource "aws_subnet" "subnet_oam_osint" {
  vpc_id     = aws_vpc.oam.id
  cidr_block = "16.0.0.64/26"
}

resource "aws_subnet" "subnet_oam_ewcf" {
  vpc_id     = aws_vpc.oam.id
  cidr_block = "16.0.0.128/26"
}

# Create subnets for net "net1"
resource "aws_subnet" "subnet_net1_igw" {
  vpc_id     = aws_vpc.net1.id
  cidr_block = "16.0.1.0/25"
}

resource "aws_subnet" "subnet_net1_osint" {
  vpc_id     = aws_vpc.net1.id
  cidr_block = "16.0.1.64/26"
}

resource "aws_subnet" "subnet_net1_ewcf" {
  vpc_id     = aws_vpc.net1.id
  cidr_block = "16.0.1.128/26"
}

# Subnets for net "net2"
resource "aws_subnet" "subnet_net2_igw" {
  vpc_id     = aws_vpc.net2.id
  cidr_block = "16.0.2.0/25"
}

# Subnets for net "net3"
resource "aws_subnet" "subnet_net3_osint" {
  vpc_id     = aws_vpc.net3.id
  cidr_block = "16.0.3.0/25"
}

resource "aws_subnet" "subnet_net3_ewcf" {
  vpc_id     = aws_vpc.net3.id
  cidr_block = "16.0.3.128/25"
}

# TODO: How to connect two subnets? Routing table?


# Keypair
resource "aws_key_pair" "ssh_key" {
  key_name   = "ssh_key"
  public_key = "ssh-rsa AAAA"
}

# Create a VM
#1
resource "aws_instance" "igw_vm" {
  ami                    = data.aws_ami.ubuntu
  instance_type          = "t3.small"
  vpc_security_group_ids = [aws_security_group.sg.id]

  network_interface {
    network_interface_id = aws_network_interface.igw_vm_oam.id
    device_index         = 0
  }

  network_interface {
    network_interface_id = aws_network_interface.igw_vm_net1.id
    device_index         = 1
  }

  network_interface {
    network_interface_id = aws_network_interface.igw_vm_net2.id
    device_index         = 2
  }
}

resource "aws_network_interface" "igw_vm_oam" {
  subnet_id  = aws_subnet.subnet_oam_igw
  private_ip = "10.0.0.10"
}

resource "aws_network_interface" "igw_vm_net1" {
  subnet_id  = aws_subnet.subnet_net1_igw
  private_ip = "10.0.1.10"
}

resource "aws_network_interface" "igw_vm_net2" {
  subnet_id  = aws_subnet.subnet_net2_igw
  private_ip = "10.0.2.10"
}

#2
resource "aws_instance" "osint_vm" {
  ami                    = data.aws_ami.ubuntu
  instance_type          = "t3.small"
  vpc_security_group_ids = [aws_security_group.sg.id]

  network_interface {
    network_interface_id = aws_network_interface.osint_vm_oam.id
    device_index         = 0
  }

  network_interface {
    network_interface_id = aws_network_interface.osint_vm_net1.id
    device_index         = 1
  }

  network_interface {
    network_interface_id = aws_network_interface.osint_vm_net3.id
    device_index         = 2
  }
}

resource "aws_network_interface" "osint_vm_oam" {
  subnet_id  = aws_subnet.subnet_oam_osint
  private_ip = "10.0.0.20"
}

resource "aws_network_interface" "osint_vm_net1" {
  subnet_id  = aws_subnet.subnet_net1_osint
  private_ip = "10.0.1.20"
}

resource "aws_network_interface" "osint_vm_net3" {
  subnet_id  = aws_subnet.subnet_net3_osint
  private_ip = "10.0.3.20"
}

#3
resource "aws_instance" "ewcf_vm" {
  ami                    = data.aws_ami.ubuntu
  instance_type          = "t3.small"
  vpc_security_group_ids = [aws_security_group.sg.id]

  network_interface {
    network_interface_id = aws_network_interface.ewcf_vm_oam.id
    device_index         = 0
  }

  network_interface {
    network_interface_id = aws_network_interface.ewcf_vm_net1.id
    device_index         = 1
  }

  network_interface {
    network_interface_id = aws_network_interface.ewcf_vm_net3.id
    device_index         = 2
  }
}

resource "aws_network_interface" "ewcf_vm_oam" {
  subnet_id  = aws_subnet.subnet_oam_ewcf
  private_ip = "10.0.0.30"
}

resource "aws_network_interface" "ewcf_vm_net1" {
  subnet_id  = aws_subnet.subnet_net1_ewcf
  private_ip = "10.0.1.30"
}

resource "aws_network_interface" "ewcf_vm_net3" {
  subnet_id  = aws_subnet.subnet_net3_ewcf
  private_ip = "10.0.3.30"
}

# TODO: Containers?

# Security Group
resource "aws_security_group" "sg" {
  name = "sg"
}

resource "aws_vpc_security_group_egress_rule" "icmp" {
  security_group_id = aws_security_group.sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = -1
  to_port           = -1
  ip_protocol       = "icmp"
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}
