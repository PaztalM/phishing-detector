output "db_address" {
  description = "RDS hostname, used as DB_HOST on the servers"
  value       = aws_db_instance.main.address
}

output "db_secret_arn" {
  description = "Secrets Manager ARN of the AWS-managed database password"
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}

output "app_url" {
  description = "Public URL of the app through the load balancer"
  value       = "http://${aws_lb.main.dns_name}"
}