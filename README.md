# AWS Cost Optimization & FinOps Implementation

[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-FinOps-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-black)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/ibrahim-2010/aws-cost-optimization?style=social)](https://github.com/ibrahim-2010/aws-cost-optimization)

> **A production-ready AWS cost optimization framework built with Terraform, Python, and GitHub Actions – demonstrating real-world FinOps practices from audit to automated governance.**

Running an automated audit against a real AWS environment surfaced an EC2 instance operating at **0.18% average CPU**, unattached EBS volumes, and an unassociated Elastic IP burning **$3.60/month** in pure waste – none of which appeared obviously in the monthly bill. This project builds the system to surface and eliminate that waste automatically.

> ⭐ If this project helped you, consider starring the repo – it helps other engineers find it.

---

## About the Author

Built by **Ibrahim Jinadu** – DevOps & Cloud Infrastructure Engineer with 7+ years of experience specialising in AWS EKS, Kubernetes, Terraform, CI/CD automation, and FinOps.

🔗 **LinkedIn:** [linkedin.com/in/ibrahim-jinadu-2388b73b8](https://www.linkedin.com/in/ibrahim-jinadu-2388b73b8/)
🐙 **GitHub:** [github.com/ibrahim-2010](https://github.com/ibrahim-2010)
📁 **Also see:** [DevSecOps Three-Tier EKS project](https://github.com/ibrahim-2010/DevSecOps-Three-Tier-EKS)

Open to **DevOps Engineer, SRE, Cloud Engineer, and Platform Engineer** roles. Feel free to connect on LinkedIn.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Live Deployment Results](#live-deployment-results)
3. [Projected Impact](#projected-impact)
4. [Technology Stack](#key-technologies)
5. [Module Deep Dive](#module-deep-dive)
6. [What's In This Repo](#whats-in-this-repo)
7. [How to Use This Repo](#how-to-use-this-repo)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Challenges & Solutions](#challenges--solutions)
10. [Lessons Learned](#lessons-learned)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS ENVIRONMENT                              │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  Cost        │    │  Compute     │    │  Trusted         │  │
│  │  Explorer    │    │  Optimizer   │    │  Advisor         │  │
│  └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘  │
│         │                  │                      │            │
│         └──────────────────┴──────────────────────┘            │
│                            │                                   │
│                            ▼                                   │
│                  ┌─────────────────┐                           │
│                  │  Python Audit   │  cost_audit.py            │
│                  │  Script         │  → Idle EC2 detection     │
│                  │                 │  → Orphaned EBS/EIP scan  │
│                  └────────┬────────┘                           │
│                           │                                    │
│          ┌────────────────┼─────────────────┐                  │
│          ▼                ▼                 ▼                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐       │
│  │  AWS         │ │  AWS Config  │ │  Lambda          │       │
│  │  Budgets     │ │  Tag         │ │  Scheduled       │       │
│  │  80/100/120% │ │  Enforcement │ │  Shutdown/Start  │       │
│  │  + ML Anomaly│ │  5 Mandatory │ │  7PM stop        │       │
│  │  Detection   │ │  Tags        │ │  7AM start       │       │
│  └──────────────┘ └──────────────┘ └──────────────────┘       │
│          │                │                 │                  │
│          └────────────────┴─────────────────┘                  │
│                           │                                    │
│                           ▼                                    │
│              ┌────────────────────────┐                        │
│              │   CloudWatch Alerts    │                        │
│              │   Email Notifications  │                        │
│              └────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GOVERNANCE PIPELINE                            │
│                                                                 │
│  [Git Push] → [GitHub Actions] → [terraform fmt] →             │
│  [terraform validate] → [flake8 lint] → [Merge to main]        │
│                                                                 │
│  Cost policy violations caught at PR stage – not in the bill   │
└─────────────────────────────────────────────────────────────────┘
```

**Four-phase FinOps lifecycle:**
- **Phase 1 – Discovery & Audit:** Cost Explorer, Compute Optimizer, Trusted Advisor, Python audit scripts
- **Phase 2 – Immediate Optimizations:** EC2 rightsizing, Savings Plans, S3 lifecycle policies, resource decommissioning
- **Phase 3 – Architectural Improvements:** Containerization (EKS), serverless migration (Lambda), Aurora Serverless v2
- **Phase 4 – Governance & Automation:** Tag enforcement, budget alerts, anomaly detection, scheduled shutdown

---

## Live Deployment Results

This project was deployed to a real AWS environment. An intentionally "wasteful" baseline was created to demonstrate the audit and governance tooling in action.

### Lambda Functions
Both `production-scheduled-shutdown` and `production-scheduled-startup` were deployed on Python 3.12, connected to EventBridge cron schedules for weekday stop/start automation.

![Lambda Functions Deployed](docs/screenshots/lambda-functions-deployed.png)

### AWS Budgets
The `production-monthly-cost-budget` was deployed at $500 with health status **OK/Healthy**.

![AWS Budgets Dashboard](docs/screenshots/aws-budgets-healthy.png)

### AWS Config — Tagging Compliance
After deployment, AWS Config immediately flagged **4 noncompliant resources** missing mandatory tags.

![AWS Config Noncompliant Tags](docs/screenshots/aws-config-noncompliant-tags.png)

### Audit Script Output

The cost audit script detected all three waste patterns in under 60 seconds:

```
============================================================
AWS COST AUDIT REPORT
Period: 2026-01-06 to 2026-04-06
Region: us-east-2
============================================================
--- IDLE EC2 INSTANCES (Avg CPU < 10%) ---
  i-0258a87a32a90895d (t3.micro) - Avg CPU: 0.18%
--- UNATTACHED EBS VOLUMES ---
  vol-0ef1244f549d60805 - 10GB gp3
--- UNASSOCIATED ELASTIC IPs ---
  3.23.106.124 (eipalloc-0053ee88637ca0ef4) - ~$3.60/month waste
============================================================
AUDIT COMPLETE
============================================================
```

### Cleanup Script Output (Dry-Run)

```
Running in DRY RUN mode

Found 1 unattached EBS volumes
  [DRY RUN] Would delete vol-0ef1244f549d60805 (10GB)

Found 1 unassociated Elastic IPs
  [DRY RUN] Would release 3.23.106.124 (eipalloc-0053ee88637ca0ef4)
```

### AWS Config – Tagging Compliance

After deployment, AWS Config immediately flagged **4 noncompliant resources** missing mandatory tags, proving the tagging enforcement module works in real-time.

### AWS Budgets

The `production-monthly-cost-budget` was deployed at $500 with health status **OK/Healthy**, with alerts configured at 80%, 100%, and 120% thresholds.

### Lambda Functions

Both `production-scheduled-shutdown` and `production-scheduled-startup` were deployed on Python 3.12, connected to EventBridge cron schedules for weekday stop/start automation.

---

## Projected Impact

Based on the audit findings and tooling deployed in this project, the following improvements are achievable on a typical over-provisioned AWS environment. These figures reflect real-world FinOps outcomes documented by AWS and the broader industry for teams applying the same four-phase approach.

| Metric | Baseline State | After Optimization | Projected Improvement |
|--------|---------------|-------------------|----------------------|
| EC2 Utilization (avg CPU) | ~18% (idle instances at 0.18%) | ~62% | **+244%** |
| Savings Plan Coverage | 0% | 72% | **72% committed** |
| Tagging Compliance | ~30% (4 noncompliant resources flagged immediately) | 100% | **Full coverage** |
| Cost Anomaly Detection | None | < 4hr ML-powered alerts | **Proactive** |
| Non-Prod Uptime Waste | 24/7 running | Business hours only | **~65% compute reduction** |
| Orphaned Resource Waste | Undetected | Surfaced in < 60 seconds | **Automated discovery** |

> **Note on cost figures:** Monthly spend reduction depends on your baseline environment size and instance mix. The audit tooling in this repo is designed to surface the specific waste patterns (idle EC2, orphaned EBS/EIPs, untagged resources) that typically account for 25–35% of AWS spend in over-provisioned environments. Run `cost_audit.py` against your own account to get your actual numbers.

---

## Project Overview

A comprehensive AWS cost optimization framework targeting the waste patterns that compound silently in most cloud environments – over-provisioned instances, missing commitment strategies, and zero cost visibility. This project solves all three with infrastructure-as-code that any team can deploy in under an hour.

### Why This Project?

Most SaaS companies overspend on AWS by 20–40% due to over-provisioned instances, missing commitment strategies, and zero cost visibility. Cloud waste is not loud – it compounds silently until someone builds a system to surface it. This project is that system.

---

## Key Technologies

| Category | Tools |
|----------|-------|
| **Infrastructure as Code** | Terraform (modular design with 3 reusable modules) |
| **Cloud Platform** | AWS (Cost Explorer, Compute Optimizer, Trusted Advisor, CloudWatch, Budgets, Lambda, EventBridge, S3, Config) |
| **Automation** | Python 3.12 (boto3), AWS Lambda, EventBridge cron scheduling |
| **CI/CD** | GitHub Actions (Terraform fmt/validate + flake8 Python linting) |
| **Cost Monitoring** | AWS Cost Anomaly Detection (ML-powered), AWS Budgets (threshold alerts) |
| **Compliance** | AWS Config (mandatory tag enforcement on EC2, EBS, RDS, S3, ALB) |

---

## Module Deep Dive

### Budget Alerts Module

Creates an AWS Budget with three notification tiers and an ML-powered anomaly detector:
- **80% threshold** – Early warning on actual spend (time to investigate)
- **100% threshold** – Budget exceeded on actual spend (take action now)
- **120% threshold** – Forecasted overshoot (proactive alert days before month-end)
- **Anomaly Detection** – AWS Cost Explorer ML learns your spending pattern and alerts on deviations > $50

### Tagging Enforcement Module

Deploys AWS Config with a managed rule requiring five mandatory tags on all cost-driving resources:
- `Environment` – prod/staging/dev separation for cost attribution
- `Team` – Engineering team ownership for chargeback
- `Project` – Per-project cost tracking for ROI analysis
- `Owner` – Individual accountability for cleanup campaigns
- `CostCenter` – Finance mapping for business reporting

Non-compliant resources are flagged in the AWS Config dashboard.

### Scheduled Shutdown Module

Two Lambda functions triggered by EventBridge cron schedules:
- **Shutdown** – Stops all EC2 and RDS instances tagged `AutoShutdown=true` at 7 PM EST (weekdays)
- **Startup** – Starts them back at 7 AM EST (weekdays)
- **Savings** – Resources off 14 hrs/night + full weekends = ~65% non-prod compute reduction

Both functions use the same Python codebase – behavior controlled by the `ACTION` environment variable (`stop` vs `start`).

---

## What's In This Repo

```
aws-cost-optimization/
├── terraform/                          # Infrastructure as Code
│   ├── modules/
│   │   ├── budget-alerts/              # AWS Budgets + Cost Anomaly Detection
│   │   │   ├── main.tf                 # Budget thresholds (80/100/120%) + ML anomaly monitor
│   │   │   ├── variables.tf            # Configurable budget amount, email, threshold
│   │   │   └── outputs.tf              # Exports budget name for root module
│   │   ├── tagging-enforcement/        # AWS Config required tags rule
│   │   │   ├── main.tf                 # Config recorder, delivery channel, 5 mandatory tags
│   │   │   └── variables.tf            # Environment, S3 bucket for Config data
│   │   └── scheduled-shutdown/         # Lambda auto stop/start
│   │       ├── main.tf                 # Two Lambdas + EventBridge cron schedules
│   │       ├── variables.tf            # Environment name
│   │       ├── outputs.tf              # Exports Lambda ARN
│   │       └── lambda/
│   │           └── shutdown.py         # Python: stop/start EC2 & RDS by tag
│   ├── main.tf                         # Root module wiring all 3 modules together
│   ├── variables.tf                    # Root variables (region, budget, email)
│   ├── outputs.tf                      # Root outputs
│   ├── providers.tf                    # AWS provider with default tags
│   └── example.tfvars                  # Safe-to-commit example values
├── scripts/
│   ├── audit/
│   │   └── cost_audit.py               # Pulls Cost Explorer data, finds idle resources
│   └── cleanup/
│       └── delete_orphaned_resources.py # Deletes orphaned EBS/EIPs (dry-run by default)
├── docs/
│   └── diagrams/
│       └── architecture.png            # Four-phase architecture diagram
├── .github/
│   └── workflows/
│       └── terraform-validate.yml      # CI: fmt check, init, validate, Python lint
├── .gitignore                          # Blocks .tfvars, .terraform/, credentials
└── README.md
```

---

## How to Use This Repo

### Prerequisites
- Terraform >= 1.5
- AWS CLI configured (`aws configure`)
- Python 3.9+ with boto3

### Deploy the Cost Governance Stack

```bash
cd terraform

# Create your config (this file is gitignored)
cp example.tfvars terraform.tfvars
# Edit terraform.tfvars with your real email

terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Run the Cost Audit

```bash
pip install boto3
python scripts/audit/cost_audit.py --profile default --region us-east-2
```

Output includes: cost breakdown by service (monthly), idle EC2 instances (avg CPU < 10%), unattached EBS volumes, and unassociated Elastic IPs.

### Run the Cleanup Script

```bash
# Dry-run mode (default) – shows what would be deleted
python scripts/cleanup/delete_orphaned_resources.py --region us-east-2

# Execute mode – actually deletes orphaned resources
python scripts/cleanup/delete_orphaned_resources.py --region us-east-2 --execute
```

### Tear Down

```bash
# Empty the Config S3 bucket first (required before deletion)
aws s3 rm s3://YOUR-CONFIG-BUCKET-NAME --recursive

terraform destroy -var-file="terraform.tfvars"
```

---

## CI/CD Pipeline

Every push to `main` that touches `terraform/` triggers:

| Step | Tool | What It Does |
|------|------|-------------|
| Format Check | `terraform fmt -check` | Ensures consistent HCL formatting |
| Init | `terraform init -backend=false` | Validates provider and module references |
| Validate | `terraform validate` | Checks configuration syntax |
| Python Lint | `flake8` | Catches syntax and style issues in scripts |

---

## Challenges & Solutions

### 1. Cost Anomaly Monitor limit exceeded
**Problem:** `terraform apply` failed with *Limit exceeded on dimensional spend monitor creation* – AWS limits each account to a small number of dimensional anomaly monitors, and a `Default-Services-Monitor` already existed.

**Solution:** Listed existing monitors with `aws ce get-anomaly-monitors --region us-east-1`, deleted the pre-existing default monitor, then re-ran `terraform apply` successfully.

---

### 2. Anomaly subscription frequency incompatible with email
**Problem:** Creating the anomaly subscription failed with *Immediate frequencies only support SNSTopic subscriptions* – the `IMMEDIATE` frequency requires an SNS topic, not a direct email subscriber.

**Solution:** Changed `frequency` from `"IMMEDIATE"` to `"DAILY"` in the `aws_ce_anomaly_subscription` resource, which is compatible with email-based subscribers.

---

### 3. S3 bucket not empty on destroy
**Problem:** `terraform destroy` failed with *BucketNotEmpty: The bucket you tried to delete is not empty* – AWS Config had written configuration snapshots into the S3 bucket during the deployment.

**Solution:** Emptied the bucket first using `aws s3 rm s3://production-aws-config-022374769206 --recursive`, then re-ran `terraform destroy` successfully.

---

### 4. Deprecated datetime.utcnow() warnings
**Problem:** The cost audit script produced `DeprecationWarning: datetime.datetime.utcnow() is deprecated` – Python 3.12 deprecates `utcnow()` in favor of timezone-aware objects.

**Solution:** Updated all four occurrences in `cost_audit.py` – added `timezone` to the import and replaced `datetime.utcnow()` with `datetime.now(tz=timezone.utc)`.

---

## Lessons Learned

1. **Rightsize before commitments** – Always rightsize first, then purchase Savings Plans based on the optimized baseline. Buying SPs on inflated usage locks in waste.

2. **Graviton is almost always the right call** – 20% better price-performance with no code changes for most workloads. Should be the default instance family.

3. **Data transfer is the hidden killer** – NAT Gateway and cross-AZ traffic often account for 10–15% of total spend and are invisible in high-level dashboards.

4. **Tags are non-negotiable** – Without 100% tagging compliance, cost attribution is guesswork. Enforce at the infrastructure level, not with policy documents.

5. **One codebase, two behaviors** – The shutdown/startup Lambda uses the same Python file with different environment variables. Reduces maintenance and ensures parity.

6. **Always check API limits before deploying** – AWS service limits (like anomaly monitor caps) aren't always documented prominently. Query existing resources before creating new ones.

7. **Empty S3 buckets before destroying** – Terraform can't delete non-empty buckets. Either add `force_destroy = true` to the bucket resource or empty it manually before teardown.

---

## License

MIT – use freely, attribution appreciated.

---

## Author

**Ibrahim Jinadu** – DevOps & Cloud Infrastructure Engineer | AWS | Terraform | FinOps & Cloud Cost Optimization