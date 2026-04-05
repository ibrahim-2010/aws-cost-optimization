module "budget_alerts" {
  source = "./modules/budget-alerts"

  environment       = var.environment
  budget_amount     = var.monthly_budget_amount
  alert_email       = var.alert_email
  anomaly_threshold = "50"
}

module "tagging_enforcement" {
  source = "./modules/tagging-enforcement"

  environment      = var.environment
  config_s3_bucket = aws_s3_bucket.config_bucket.id
}

module "scheduled_shutdown" {
  source = "./modules/scheduled-shutdown"

  environment = var.environment
}

resource "aws_s3_bucket" "config_bucket" {
  bucket = "${var.environment}-aws-config-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_policy" "config_bucket_policy" {
  bucket = aws_s3_bucket.config_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "config.amazonaws.com" }
      Action    = "s3:PutObject"
      Resource  = "${aws_s3_bucket.config_bucket.arn}/*"
      Condition = {
        StringEquals = {
          "s3:x-amz-acl" = "bucket-owner-full-control"
        }
      }
    },
    {
      Effect    = "Allow"
      Principal = { Service = "config.amazonaws.com" }
      Action    = "s3:GetBucketAcl"
      Resource  = aws_s3_bucket.config_bucket.arn
    }]
  })
}

data "aws_caller_identity" "current" {}