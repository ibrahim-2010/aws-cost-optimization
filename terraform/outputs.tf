output "budget_name" {
  description = "Name of the monthly cost budget"
  value       = module.budget_alerts.budget_name
}

output "config_bucket" {
  description = "S3 bucket for AWS Config"
  value       = aws_s3_bucket.config_bucket.id
}

output "shutdown_lambda_arn" {
  description = "ARN of the shutdown Lambda function"
  value       = module.scheduled_shutdown.shutdown_lambda_arn
}

output "budget_name" {
  value = aws_budgets_budget.monthly_cost.name
}

output "shutdown_lambda_arn" {
  value = aws_lambda_function.shutdown.arn
}