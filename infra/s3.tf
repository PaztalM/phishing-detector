resource "aws_s3_bucket" "code" {
  bucket_prefix = "phishing-code-"
  force_destroy = true
}