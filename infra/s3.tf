resource "aws_s3_bucket" "code" {
  bucket_prefix = "phishing-code-"
  force_destroy = true
}

resource "aws_s3_object" "app" {
  bucket = aws_s3_bucket.code.id
  key    = "app.zip"
  source = "${path.module}/app.zip"
  etag   = filemd5("${path.module}/app.zip")
}