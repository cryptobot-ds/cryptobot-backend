terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Optionnel : récupérer le VPC par défaut
data "aws_vpc" "default" {
  default = true
}

# Liste des subnets du VPC par défaut
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}


# Groupe de sécurité pour CryptoBot
resource "aws_security_group" "cryptobot_sg" {
  name        = "cryptobot-sg"
  description = "Security group for CryptoBot EC2 (SSH, HTTP, FastAPI, Streamlit)"
  vpc_id      = data.aws_vpc.default.id

  # SSH
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  # HTTP (Nginx ou autre)
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # FastAPI
  ingress {
    description = "FastAPI"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Streamlit
  ingress {
    description = "Streamlit"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Sortant : tout autorisé
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cryptobot-sg"
  }
}

# AMI Ubuntu 24.04 LTS (dernière version dispo)
data "aws_ami" "ubuntu_24_04" {
  most_recent = true

  owners = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "cryptobot" {
  ami           = data.aws_ami.ubuntu_24_04.id
  instance_type = var.instance_type

  # Prend le premier subnet du VPC par défaut
  subnet_id              = data.aws_subnets.default.ids[0]
  vpc_security_group_ids = [aws_security_group.cryptobot_sg.id]

  key_name = var.key_pair_name

  associate_public_ip_address = true

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
  }

  tags = {
    Name    = var.instance_name
    Project = "cryptobot"
    Env     = "dev"
  }


  ################################
  # 1) Connexion SSH pour provisioners
  ################################
  connection {
    type        = "ssh"
    host        = self.public_ip
    user        = "ubuntu"
    private_key = file("C:/Users/brice/.ssh/loginAwsIrlande.pem")
  }

  
  ################################
  # 2) Créer le dossier Ansible sur l'EC2
  ################################
  provisioner "remote-exec" {
    inline = [
      "mkdir -p /home/ubuntu/ansible"
    ]
  }

  ################################
  # 3) Copier les playbooks Ansible sur l'EC2
  ################################
  provisioner "file" {
    source      = "${path.module}/../config-as-code/"
    destination = "/home/ubuntu/ansible"
  }

  ################################
  # 4) Installer Ansible + lancer les playbooks
  ################################
  provisioner "remote-exec" {
    inline = [
      "echo '=== Mise à jour des paquets ==='",
      "sudo apt-get update -y",

      "echo '=== Installation de python3-pip et ansible ==='",
      "sudo apt-get install -y python3-pip ansible",

      "echo '=== Vérification version Ansible ==='",
      "ansible --version || echo 'Ansible non disponible ?'",

      "echo '=== Contenu de /home/ubuntu ==='",
      "ls -al /home/ubuntu",

      "echo '=== Contenu de /home/ubuntu/ansible (si existe) ==='",
      "ls -al /home/ubuntu/ansible || echo 'Dossier /home/ubuntu/ansible introuvable'",

      "echo '=== Lancement des playbooks en local ==='",
      # Playbook 1 : installer Docker
      # on n’a même plus besoin du cd si on utilise le chemin absolu :
      "ansible-playbook -i 'localhost,' -c local /home/ubuntu/ansible/install_docker.yml",
      # "ansible-playbook -i 'localhost,' -c local install_docker.yml",
      # Playbook 2 : déployer ton projet CryptoBot
    #   "ansible-playbook -i 'localhost,' -c local deploy_cryptobot.yml"
    ]
  }

  timeouts {
    create = "30m"
  }
}

