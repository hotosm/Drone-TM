#CREATE AUTOSCALING TARGET FOR dtm
resource "aws_appautoscaling_target" "dtm_scaling_target" {
  max_capacity       = 3
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.cluster.name}/${aws_ecs_service.dtm_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

#CREATE AUTOSCALING POLICY FOR dtm
resource "aws_appautoscaling_policy" "dtm_scaling_policy" {
  name               = "dtm-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dtm_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dtm_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dtm_scaling_target.service_namespace
  depends_on         = [aws_appautoscaling_target.dtm_scaling_target]

  target_tracking_scaling_policy_configuration {
    target_value       = 40
    scale_in_cooldown  = 30
    scale_out_cooldown = 10
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}


#CREATE AUTOSCALING TARGET FOR dtm WORKER
# resource "aws_appautoscaling_target" "dtm_worker_scaling_target" {
#   max_capacity       = 1
#   min_capacity       = 1
#   resource_id        = "service/${aws_ecs_cluster.cluster.name}/${aws_ecs_service.dtm_worker_service.name}"
#   scalable_dimension = "ecs:service:DesiredCount"
#   service_namespace  = "ecs"
# }

# #CREATE AUTOSCALING POLICY FOR dtm WORKER
# resource "aws_appautoscaling_policy" "dtm_worker_scaling_policy" {
#   name               = "dtm-worker-scaling-policy"
#   policy_type        = "TargetTrackingScaling"
#   resource_id        = aws_appautoscaling_target.dtm_worker_scaling_target.id
#   scalable_dimension = aws_appautoscaling_target.dtm_worker_scaling_target.scalable_dimension
#   service_namespace  = aws_appautoscaling_target.dtm_worker_scaling_target.service_namespace
#   depends_on         = [aws_appautoscaling_target.dtm_worker_scaling_target]

#   target_tracking_scaling_policy_configuration {
#     target_value       = 40
#     scale_in_cooldown  = 30
#     scale_out_cooldown = 10
#     predefined_metric_specification {
#       predefined_metric_type = "ECSServiceAverageCPUUtilization"
#     }
#   }
# }
