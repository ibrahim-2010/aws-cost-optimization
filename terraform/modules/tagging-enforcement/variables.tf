variable "environment" {
  type = string
}

variable "config_s3_bucket" {
  description = "S3 bucket for AWS Config delivery"
  type        = string
}