output "instance_id" {
  description = "ID de l'instance EC2"
  value       = aws_instance.cryptobot.id
}

output "public_ip" {
  description = "IP publique de l'instance EC2"
  value       = aws_instance.cryptobot.public_ip
}

output "public_dns" {
  description = "DNS public"
  value       = aws_instance.cryptobot.public_dns
}

output "security_group_id" {
  description = "ID du groupe de sécurité"
  value       = aws_security_group.cryptobot_sg.id
}
