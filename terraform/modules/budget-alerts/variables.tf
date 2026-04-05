variable "environment" {
  type = string
}

variable "budget_amount" {
  type = number
}

variable "alert_email" {
  type = string
}

variable "anomaly_threshold" {
  description = "Dollar threshold for anomaly alerts"
  type        = string
  default     = "50"
}