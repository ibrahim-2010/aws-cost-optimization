variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "monthly_budget_amount" {
  description = "Monthly budget in USD"
  type        = number
  default     = 500
}

variable "alert_email" {
  description = "Email for budget alerts"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook for cost alerts"
  type        = string
  default     = ""
  sensitive   = true
}