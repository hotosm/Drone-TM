# CREATE S3 Bucket
resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.s3_bucket_name
  tags = {
    Name = "${var.s3_bucket_name}"
  }
}


resource "aws_s3_bucket" "alb_logs_s3_bucket" {
  bucket = "${var.s3_bucket_name}-alb-logs"
  tags = {
    Name = "${var.s3_bucket_name}-alb-logs"
  }
}

resource "aws_s3_bucket_policy" "allow_loadbalancer_to_logs_bucket" {
  bucket = aws_s3_bucket.alb_logs_s3_bucket.id
  policy = data.aws_iam_policy_document.allow_loadbalancer_to_logs_bucket.json
}

data "aws_iam_policy_document" "allow_loadbalancer_to_logs_bucket" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::718504428378:root"]
      # Here Change identifier "718504428378" on basis of loadbalancer region
      # We're using 718504428378 as our loadbalancer is on region ap-south-1
    }

    actions = [
      "s3:PutObject",
    ]

    resources = [
      "${aws_s3_bucket.alb_logs_s3_bucket.arn}/*",
    ]
  }
  statement {
    principals {
      type        = "Service"
      identifiers = ["delivery.logs.amazonaws.com"]
    }

    actions = [
      "s3:GetBucketAcl",
    ]

    resources = [
      "${aws_s3_bucket.alb_logs_s3_bucket.arn}"
    ]
  }

}
