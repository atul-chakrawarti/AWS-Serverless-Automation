# AWS Serverless Automation

Six AWS Lambda + Boto3 automation projects built for the "AWS
Automation with Lambda & Boto3" assignment. Each task is self-contained
in its own directory with the Lambda handler, least-privilege IAM
inline policy, trust policy, deployment screenshots, and a README
documenting the steps followed, testing approach, and a short
discussion of the managed-AWS alternative to the custom Lambda solution.

All functions target **Python 3.12** runtime and follow least-privilege
IAM (scoped inline policies, no `*FullAccess` managed policies).
Deployed and tested in **AWS account 280768229384**, region `us-east-1`.

## Status

| Directory | Assignment | Status | Screenshots |
|---|---|---|---|
| [`Task1`](./Task1) | Automated S3 Bucket Cleanup (objects older than 30 days) | ✅ Deployed & tested | [11 screenshots](./Task1/screenshots) |
| [`Task2`](./Task2) | Automated EBS Snapshot Creation and Cleanup | ✅ Deployed & tested | [7 screenshots](./Task2/screenshots) |
| [`Task3`](./Task3) | Auto-Tagging EC2 Instances on Launch | ✅ Deployed & tested | [8 screenshots](./Task3/screenshots) |
| [`Task4`](./Task4) | Daily AWS Cost Alert Using Cost Explorer API and SNS | ✅ Deployed & tested | [10 screenshots](./Task4/screenshots) |
| [`Task5`](./Task5) | Restore an EC2 Instance from the Latest Snapshot | ⏳ Code ready, not yet deployed | — |
| [`Task6`](./Task6) | Audit S3 Buckets for Public Access and Notify | ⏳ Code ready, not yet deployed | — |

The assignment only requires 4 of 6 tasks for grading; Tasks 1–4 are
fully deployed, tested end-to-end, and documented with screenshots.
Tasks 5–6 have complete, ready-to-deploy code and IAM policies but
haven't been run in the AWS console yet.

## Deployed Resource Reference

| Task | Lambda function | IAM role | Key resource |
|---|---|---|---|
| Task1 | `s3-lambda` | `s3-cleanup-lambda-role` | Bucket: `atulchakrawarti` |
| Task2 | `ebs-snapshot-cleanup` | `ebs-snapshot-lambda-role` | Volume: `vol-0b5b3717a57a66d22` |
| Task3 | `ec2-auto-tag-on-launch` | `ec2-auto-tag-lambda-role` | EventBridge rule: `ec2-running-auto-tag-rule` |
| Task4 | `daily-cost-alert` | `cost-alert-lambda-role` | SNS topic: `aws-cost-alerts`, EventBridge rule: `daily-cost-check-rule` |

## Structure (per task)
```
TaskN/
├── lambda_function.py     # Lambda handler (Boto3)
├── iam_policy.json        # Least-privilege inline IAM policy
├── trust_policy.json      # Lambda execution role trust policy
├── eventbridge_pattern.json / other supporting config (where applicable)
├── screenshots/           # IAM role, Lambda config, test output, logs, final result
└── README.md              # Steps followed, testing notes, discussion point
```

## General Setup Notes
- Region used throughout: `us-east-1`.
- EventBridge (formerly CloudWatch Events) used for all scheduling/event
  rules.
- `t3.micro` used for any EC2 instances.
- A $1 AWS Budget Alert was set up before starting, and all test
  resources (EC2 instances, snapshots, buckets) were cleaned up
  immediately after capturing screenshots for each task.
- Lambda code for Task1, Task2, and Task4 hardcodes the real deployed
  resource (bucket name, volume ID, SNS topic ARN respectively) as a
  default, while still honoring the environment variable override if
  set — this keeps the code runnable as-is while matching what's
  actually configured in the console.
