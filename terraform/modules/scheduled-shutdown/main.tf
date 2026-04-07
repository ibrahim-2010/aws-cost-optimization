data "archive_file" "shutdown_lambda" {
  type        = "zip"
  source_file = "${path.module}/lambda/shutdown.py"
  output_path = "${path.module}/lambda/shutdown.zip"
}

resource "aws_lambda_function" "shutdown" {
  filename         = data.archive_file.shutdown_lambda.output_path
  function_name    = "${var.environment}-scheduled-shutdown"
  role             = aws_iam_role.lambda_role.arn
  handler          = "shutdown.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120
  source_code_hash = data.archive_file.shutdown_lambda.output_base64sha256

  environment {
    variables = {
      TARGET_TAG_KEY   = "AutoShutdown"
      TARGET_TAG_VALUE = "true"
      ACTION           = "stop"
    }
  }
}

resource "aws_lambda_function" "startup" {
  filename         = data.archive_file.shutdown_lambda.output_path
  function_name    = "${var.environment}-scheduled-startup"
  role             = aws_iam_role.lambda_role.arn
  handler          = "shutdown.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120
  source_code_hash = data.archive_file.shutdown_lambda.output_base64sha256

  environment {
    variables = {
      TARGET_TAG_KEY   = "AutoShutdown"
      TARGET_TAG_VALUE = "true"
      ACTION           = "start"
    }
  }
}

# Stop at 7 PM EST (midnight UTC) weekdays
resource "aws_cloudwatch_event_rule" "shutdown_schedule" {
  name                = "${var.environment}-shutdown-schedule"
  schedule_expression = "cron(0 0 ? * MON-FRI *)"
}

# Start at 7 AM EST (noon UTC) weekdays
resource "aws_cloudwatch_event_rule" "startup_schedule" {
  name                = "${var.environment}-startup-schedule"
  schedule_expression = "cron(0 12 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "shutdown_target" {
  rule = aws_cloudwatch_event_rule.shutdown_schedule.name
  arn  = aws_lambda_function.shutdown.arn
}

resource "aws_cloudwatch_event_target" "startup_target" {
  rule = aws_cloudwatch_event_rule.startup_schedule.name
  arn  = aws_lambda_function.startup.arn
}

resource "aws_lambda_permission" "allow_shutdown" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.shutdown.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.shutdown_schedule.arn
}

resource "aws_lambda_permission" "allow_startup" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.startup.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.startup_schedule.arn
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.environment}-shutdown-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_ec2" {
  name = "${var.environment}-lambda-ec2-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ec2:DescribeInstances", "ec2:StopInstances", "ec2:StartInstances"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["rds:DescribeDBInstances", "rds:StopDBInstance", "rds:StartDBInstance"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}