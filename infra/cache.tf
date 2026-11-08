resource "aws_elasticache_subnet_group" "main" {
  name       = "phishing-cache-subnets"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "phishing-cache"
  engine               = "redis"
  engine_version       = "7.1"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.cache.id]
}

output "cache_address" {
  description = "ElastiCache Redis endpoint, used as REDIS_HOST on the servers"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}