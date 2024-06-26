#Create a dtm target group for the load balancer
resource "aws_lb_target_group" "dtm_target_group" {
  name        = "dtm-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"


  health_check {
    interval            = 40
    path                = "/"
    port                = 8000
    protocol            = "HTTP"
    timeout             = 30
    healthy_threshold   = 2
    unhealthy_threshold = 4
    matcher             = "200-400"
  }
}


#Create a dtm-Fastapi target group for the load balancer
resource "aws_lb_target_group" "fastapi_target_group" {
  name        = "fastapi-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"


  health_check {
    interval            = 30
    path                = "/"
    port                = 8000
    protocol            = "HTTP"
    timeout             = 29
    healthy_threshold   = 5
    unhealthy_threshold = 10
    matcher             = "404"
  }
}
