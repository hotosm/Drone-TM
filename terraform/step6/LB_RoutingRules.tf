#Assign dtm routing rule to Listener
resource "aws_lb_listener_rule" "dtm_routing" {
  listener_arn = aws_lb_listener.http_lb_listener.arn
  priority     = 5

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.dtm_target_group.arn
  }

  condition {
    host_header {
      values = ["${var.dtm_subdomain}.${var.domain}"]
    }
  }
}

#Assign dtm routing rule to Listener
resource "aws_lb_listener_rule" "dtm_redirect_routing" {
  listener_arn = aws_lb_listener.http_lb_listener.arn
  priority     = 6

  action {
    type = "redirect"

    redirect {
      host        = "${var.dtm_subdomain}.${var.domain}"
      status_code = "HTTP_301"
    }
  }

  condition {
    host_header {
      values = ["${var.domain}"]
    }
  }
}
