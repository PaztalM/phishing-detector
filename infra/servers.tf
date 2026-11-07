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
    region     = "eu-north-1"
    db_host    = aws_db_instance.main.address
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "phishing-app"
    }
  }
}

resource "aws_autoscaling_group" "app" {
  name                = "phishing-app-asg"
  min_size            = 2
  max_size            = 2
  desired_capacity    = 2
  vpc_zone_identifier = [aws_subnet.public_a.id, aws_subnet.public_b.id]
  target_group_arns   = [aws_lb_target_group.app.arn]

  launch_template {
    id      = aws_launch_template.app.id
    version = aws_launch_template.app.latest_version
  }

  health_check_type         = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Project"
    value               = "phishing-detector"
    propagate_at_launch = true
  }

  depends_on = [aws_s3_object.app]
}