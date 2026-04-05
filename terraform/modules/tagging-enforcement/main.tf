locals {
  required_tags = ["Environment", "Team", "Project", "Owner", "CostCenter"]
}

resource "aws_config_config_rule" "required_tags" {
  name = "${var.environment}-required-tags"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "Team"
    tag3Key = "Project"
    tag4Key = "Owner"
    tag5Key = "CostCenter"
  })

  scope {
    compliance_resource_types = [
      "AWS::EC2::Instance",
      "AWS::EC2::Volume",
      "AWS::RDS::DBInstance",
      "AWS::S3::Bucket",
      "AWS::ElasticLoadBalancingV2::LoadBalancer",
    ]
  }

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_configuration_recorder" "main" {
  name     = "${var.environment}-config-recorder"
  role_arn = aws_iam_role.config_role.arn

  recording_group {
    all_supported                 = false
    include_global_resource_types = false
    resource_types = [
      "AWS::EC2::Instance",
      "AWS::EC2::Volume",
      "AWS::RDS::DBInstance",
      "AWS::S3::Bucket",
      "AWS::ElasticLoadBalancingV2::LoadBalancer",
    ]
  }
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.environment}-config-delivery"
  s3_bucket_name = var.config_s3_bucket

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true

  depends_on = [aws_config_delivery_channel.main]
}

resource "aws_iam_role" "config_role" {
  name = "${var.environment}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "config.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "config_policy" {
  role       = aws_iam_role.config_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}