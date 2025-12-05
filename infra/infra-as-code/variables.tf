variable "aws_region" {
  description = "AWS region to deploy in"
  type        = string
  default     = "eu-west-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_pair_name" {
  description = "Name of the EC2 key pair"
  type        = string
}

variable "root_volume_size" {
  description = "Root volume size in GB"
  type        = number
  default     = 16
}

variable "instance_name" {
  description = "Name tag of the EC2 instance"
  type        = string
  default     = "cryptobot-terraform"
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed for SSH access"
  type        = string
}
