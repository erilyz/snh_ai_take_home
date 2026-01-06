/**
 * AWS Infrastructure for Tree Management API
 *
 * Creates:
 * - S3 bucket for data persistence
 * - IAM role and policy for secure access
 * - Bucket versioning and lifecycle policies
 *
 * PRODUCTION BEST PRACTICES:
 * - This Terraform should be executed by a dedicated IAM role with minimal permissions
 * - Apply changes via CI/CD pipeline (GitHub Actions, GitLab CI, AWS CodePipeline)
 * - Use remote state backend (S3) with DynamoDB state locking
 * - Implement approval workflows for production changes
 * - Never apply manually in production environments
 *
 * Example CI/CD setup:
 *   1. Store Terraform state in S3 bucket with versioning and encryption
 *   2. Use DynamoDB table for state locking
 *   3. Use OIDC provider for GitHub Actions authentication
 *   4. Require PR approval before terraform apply
 *   5. Run terraform plan on every PR
 */

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# S3 bucket for tree data storage
resource "aws_s3_bucket" "tree_data" {
  bucket = "${var.project_name}-tree-api-data-${var.environment}"
  
  tags = {
    Environment = var.environment
    Application = "tree-api"
    ManagedBy   = "terraform"
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "tree_data" {
  bucket = aws_s3_bucket.tree_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle policy to manage old versions
resource "aws_s3_bucket_lifecycle_configuration" "tree_data" {
  bucket = aws_s3_bucket.tree_data.id
  
  rule {
    id     = "delete-old-versions"
    status = "Enabled"
    
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "tree_data" {
  bucket = aws_s3_bucket.tree_data.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role for the API
resource "aws_iam_role" "tree_api" {
  name = "tree-api-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Environment = var.environment
    Application = "tree-api"
  }
}

# IAM policy for S3 bucket access
resource "aws_iam_role_policy" "tree_api_s3_access" {
  name = "tree-api-s3-access"
  role = aws_iam_role.tree_api.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.tree_data.arn,
          "${aws_s3_bucket.tree_data.arn}/*"
        ]
      }
    ]
  })
}

# Instance profile for EC2 instances
resource "aws_iam_instance_profile" "tree_api" {
  name = "tree-api-${var.environment}"
  role = aws_iam_role.tree_api.name
}

# Output values for application configuration
output "bucket_name" {
  description = "Name of the S3 bucket for tree data"
  value       = aws_s3_bucket.tree_data.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.tree_data.arn
}

output "iam_role_arn" {
  description = "ARN of the IAM role"
  value       = aws_iam_role.tree_api.arn
}

output "instance_profile_name" {
  description = "Name of the instance profile"
  value       = aws_iam_instance_profile.tree_api.name
}

