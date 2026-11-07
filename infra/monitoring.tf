locals {
  alb_dim = aws_lb.main.arn_suffix
  tg_dim  = aws_lb_target_group.app.arn_suffix
  asg_dim = aws_autoscaling_group.app.name
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "phishing-detector"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Healthy vs unhealthy servers"
          region = "eu-north-1"
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", "TargetGroup", local.tg_dim, "LoadBalancer", local.alb_dim, { stat = "Minimum" }],
            ["AWS/ApplicationELB", "UnHealthyHostCount", "TargetGroup", local.tg_dim, "LoadBalancer", local.alb_dim, { stat = "Maximum" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Requests to the load balancer"
          region = "eu-north-1"
          period = 60
          stat   = "Sum"
          metrics = [
            [{ expression = "FILL(m1, 0)", label = "Requests", id = "e1" }],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", local.alb_dim, { id = "m1", visible = false }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Success vs failure"
          region = "eu-north-1"
          period = 60
          stat   = "Sum"
          metrics = [
            [{ expression = "FILL(m1, 0)", label = "2XX (success)", id = "e1" }],
            [{ expression = "FILL(m2, 0)", label = "4XX (client error)", id = "e2" }],
            [{ expression = "FILL(m3, 0)", label = "5XX from the app", id = "e3" }],
            [{ expression = "FILL(m4, 0)", label = "5XX from the ALB", id = "e4" }],
            ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", local.alb_dim, { id = "m1", visible = false }],
            ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", local.alb_dim, { id = "m2", visible = false }],
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", local.alb_dim, { id = "m3", visible = false }],
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", local.alb_dim, { id = "m4", visible = false }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Response time (seconds)"
          region = "eu-north-1"
          period = 60
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", local.alb_dim, { stat = "Average" }],
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", local.alb_dim, { stat = "p95" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          title  = "Server CPU (%)"
          region = "eu-north-1"
          period = 60
          metrics = [
            ["AWS/EC2", "CPUUtilization", "AutoScalingGroupName", local.asg_dim, { stat = "Average" }],
            ["AWS/EC2", "CPUUtilization", "AutoScalingGroupName", local.asg_dim, { stat = "Maximum" }]
          ]
        }
      }
    ]
  })
}