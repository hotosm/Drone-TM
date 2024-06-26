# resource "aws_route53_record" "enketo_subdomain" {
#   zone_id = var.route53_zone_id
#   name    = var.enketo_subdomain
#   type    = "CNAME"
#   ttl     = 300
#   records = [aws_lb.load_balancer.dns_name]
# }

# resource "aws_route53_record" "kpi_subdomain" {
#   zone_id = var.route53_zone_id
#   name    = var.kpi_subdomain
#   type    = "CNAME"
#   ttl     = 300
#   records = [aws_lb.load_balancer.dns_name]
# }

# resource "aws_route53_record" "kobocat_subdomain" {
#   zone_id = var.route53_zone_id
#   name    = var.kobocat_subdomain
#   type    = "CNAME"
#   ttl     = 300
#   records = [aws_lb.load_balancer.dns_name]
# }

# resource "aws_route53_record" "zite_subdomain" {
#   zone_id = var.route53_zone_id
#   name    = var.zite_subdomain
#   type    = "CNAME"
#   ttl     = 300
#   records = [aws_lb.load_balancer.dns_name]
# }
