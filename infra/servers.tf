data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_launch_template" "app" {
  name_prefix   = "phishing-app-"
  image_id      = data.aws_ssm_parameter.al2023.value
  instance_type = "t3.micro"

  iam_instance_profile {
    name = aws_iam_instance_profile.app.name
  }

  vpc_security_group_ids = [aws_security_group.app.id]

  metadata_options {
    http_tokens = "required"
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh.tftpl", {
    bucket     = aws_s3_bucket.code.id
    secret_arn = aws_db_instance.main.master_user_secret[0].secret_arn
    region     = "us-east-1"
    db_host    = aws_db_instance.main.address
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "phishing-app"
    }
  }
}