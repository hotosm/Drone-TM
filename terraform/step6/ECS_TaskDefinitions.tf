# Define a task definition for the fastapi service
resource "aws_ecs_task_definition" "dtm" {
  family                   = "fastapi-tdf"
  execution_role_arn       = "arn:aws:iam::${var.aws_account}:role/${var.ecs_task_role_name}"
  task_role_arn            = "arn:aws:iam::${var.aws_account}:role/${var.ecs_task_role_name}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512

  container_definitions = <<TASK_DEFINATION
  [
    {
      "name" : "dtm",
      "image" : "${var.dtm_fastapi_image}",
      "essential": true,
      "portMappings" : [
        {
          "name" : "dtm-8000-tcp",
          "containerPort" : 8000,
          "hostPort" : 8000,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [],
      "environmentFiles" : [
        {
          "value" : "arn:aws:s3:::${var.s3_bucket_name}/envfile.env",
          "type" : "s3"
        }
      ],
      "mountPoints" : [],
      "volumesFrom" : [],
      "logConfiguration" : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-create-group" : "true",
          "awslogs-group" : "/ecs/${var.project_name}-fastapi-tdf",
          "awslogs-region" : "${var.aws_region}",
          "awslogs-stream-prefix" : "ecs"
        }
      },
      "healthCheck": {
        "command": [
            "CMD-SHELL",
            "curl --fail http://localhost:8000/admin/login/ || exit 0"
        ],
        "interval": 30,
        "timeout": 10,
        "retries": 2,
        "startPeriod": 10
      }
    }
  ]
  TASK_DEFINATION
  runtime_platform {
    cpu_architecture        = "X86_64"
    operating_system_family = "LINUX"
  }
}


# resource "aws_ecs_task_definition" "dtm_worker" {
#   family                   = "dtm-worker-tdf"
#   execution_role_arn       = "arn:aws:iam::${var.aws_account}:role/${var.ecs_task_role_name}"
#   task_role_arn            = "arn:aws:iam::${var.aws_account}:role/${var.ecs_task_role_name}"
#   network_mode             = "awsvpc"
#   requires_compatibilities = ["FARGATE"]
#   cpu                      = 512
#   memory                   = 2048

#   container_definitions = <<TASK_DEFINATION
#   [
#     {
#       "name" : "dtm-worker",
#       "image" : "${var.dtm_fastapi_image}",
#       "essential": true,
#       "portMappings" : [],
#       "essential" : true,
#       "entrypoint": ["celery", "-A", "dtm", "worker", "-l", "INFO", "--autoscale=12,4", "-Q", "default,manage_forms,submission,longqueue,workflow"],
#       "environment" : [],
#       "environmentFiles" : [
#         {
#           "value" : "arn:aws:s3:::${var.s3_bucket_name}/envfile.env",
#           "type" : "s3"
#         }
#       ]
#     }
#   ]
#   TASK_DEFINATION
#   runtime_platform {
#     cpu_architecture        = "X86_64"
#     operating_system_family = "LINUX"
#   }
# }
