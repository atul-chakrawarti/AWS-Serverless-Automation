# AWS Serverless Automation

Six AWS Lambda + Boto3 automation projects built for the "AWS
Automation with Lambda & Boto3" assignment. Each task is self-contained
in its own directory with the Lambda handler, least-privilege IAM
inline policy, trust policy, and a README documenting the steps
followed, testing approach, and a short discussion of the managed-AWS
alternative to the custom Lambda solution.

All functions target **Python 3.12** runtime and follow least-privilege
IAM (scoped inline policies, no `*FullAccess` managed policies).

| Directory | Assignment |
|---|---|
| [`Task1`](./Task1) | Automated S3 Bucket Cleanup (objects older than 30 days) |
| [`Task2`](./Task2) | Automated EBS Snapshot Creation and Cleanup |
| [`Task3`](./Task3) | Auto-Tagging EC2 Instances on Launch |
| [`Task4`](./Task4) | Daily AWS Cost Alert Using Cost Explorer API and SNS |
| [`Task5`](./Task5) | Restore an EC2 Instance from the Latest Snapshot |
| [`Task6`](./Task6) | Audit S3 Buckets for Public Access and Notify |

## Structure (per task)
```
TaskN/
├── lambda_function.py     # Lambda handler (Boto3)
├── iam_policy.json        # Least-privilege inline IAM policy
├── trust_policy.json      # Lambda execution role trust policy
├── eventbridge_pattern.json / other supporting config (where applicable)
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
