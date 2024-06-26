# Create dtm service to run on the cluster
resource "aws_ecs_service" "dtm_service" {
  name                   = "dtm"
  cluster                = aws_ecs_cluster.cluster.id
  task_definition        = aws_ecs_task_definition.dtm.arn
  desired_count          = 1
  launch_type            = "FARGATE"
  enable_execute_command = true
  force_new_deployment   = true
  health_check_grace_period_seconds = 15


  load_balancer {
    target_group_arn = aws_lb_target_group.dtm_target_group.arn
    container_name   = "dtm"
    container_port   = 8000
  }

  network_configuration {
    assign_public_ip = false
    subnets          = var.vpc_private_subnets[*]
    security_groups  = [var.ecs_sec_grp]
  }

  deployment_controller {
    type = "ECS"
  }
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}

# resource "aws_ecs_service" "dtm_worker_service" {
#   name                   = "dtm-worker"
#   cluster                = aws_ecs_cluster.cluster.id
#   task_definition        = aws_ecs_task_definition.dtm_worker.arn
#   desired_count          = 1
#   launch_type            = "FARGATE"
#   enable_execute_command = true
#   force_new_deployment   = true

#   network_configuration {
#     assign_public_ip = false
#     subnets          = var.vpc_private_subnets[*]
#     security_groups  = [var.ecs_sec_grp]
#   }

#   deployment_controller {
#     type = "ECS"
#   }
#   deployment_circuit_breaker {
#     enable   = true
#     rollback = true
#   }
# }
