resource "aws_db_subnet_group" "main" {
  name       = "phishing-db-subnets"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "phishing-db-subnets"
  }
}