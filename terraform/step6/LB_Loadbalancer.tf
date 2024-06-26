# CREATE APPLICATION LOADBALANCER
resource "aws_lb" "load_balancer" {
  name                       = var.ecs_loadbalancer_name
  internal                   = false
  load_balancer_type         = "application"
  drop_invalid_header_fields = true
  subnets                    = var.vpc_public_subnets[*]
  security_groups            = [var.load_balancer_sec_grp]

  enable_deletion_protection       = false
  enable_cross_zone_load_balancing = true
  idle_timeout                     = 180

  access_logs {
    bucket  = var.alb_logs_s3_bucket
    prefix  = "${var.project_name}-lb"
    enabled = true
  }

  tags = {
    Name = var.ecs_loadbalancer_name
  }
}

# ASSIGN HTTPS LISTENER TO ALB
resource "aws_lb_listener" "http_lb_listener" {
  load_balancer_arn = aws_lb.load_balancer.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_lb_target_group.dtm_target_group.arn
    type             = "forward"
  }
}

# # ASSIGN HTTP LISTENER TO ALB
# resource "aws_lb_listener" "http_lb_listener" {
#   load_balancer_arn = aws_lb.load_balancer.arn
#   port              = 80
#   protocol          = "HTTP"

#   default_action {
#     type = "redirect"

#     redirect {
#       port        = "443"
#       protocol    = "HTTPS"
#       status_code = "HTTP_301"
#     }
#   }
# }
