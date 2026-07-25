# Task 6: Audit S3 Buckets for Public Access and Notify

## Objective
Detect any S3 bucket that is publicly accessible — via Block Public
Access settings, bucket policy, or ACL — and alert via SNS.

## Files
| File | Purpose |
|---|---|
| `lambda_function.py` | Audits every bucket's Block Public Access, policy status, and ACL |
| `iam_policy.json` | Inline policy for read-only S3 audit checks + SNS publish |
| `trust_policy.json` | Lambda execution role trust policy |

## Steps Followed

1. **SNS Setup** — Created topic `s3-public-access-alerts`, subscribed
   my email, confirmed the subscription.

2. **IAM Role** — Created `s3-audit-lambda-role` with the trust policy
   and attached `iam_policy.json` inline after replacing
   `REPLACE_WITH_ACCOUNT_ID` / `REPLACE_WITH_TOPIC_NAME`.

3. **Lambda Function** — Runtime Python 3.12. Environment variable:
   - `SNS_TOPIC_ARN = arn:aws:sns:us-east-1:<account-id>:s3-public-access-alerts`
   Timeout increased to 30s (loops over every bucket in the account,
   3 API calls each).

4. **EventBridge** — Created scheduled rule `daily-s3-audit-rule` with
   `rate(1 day)`, targeting this function.

5. **Testing** — Since April 2023 new buckets ship with **Block Public
   Access enabled and ACLs disabled by default**, so a fresh bucket
   won't trip the audit on its own. To validate detection:
   - Created a disposable test bucket.
   - Disabled Block Public Access on it.
   - Attached a public-read bucket policy (`Principal: "*"`,
     `Action: "s3:GetObject"`).
   - Ran the function manually and confirmed the SNS alert named the
     test bucket.
   - **Immediately re-enabled Block Public Access and removed the
     public policy** after the test to avoid leaving the bucket exposed.

## Detection Logic
A bucket is flagged as public if **any** of the following is true:
- `get_public_access_block` config is missing, or any of its four
  flags (`BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`,
  `RestrictPublicBuckets`) is `False`.
- `get_bucket_policy_status` reports `IsPublic: true`.
- `get_bucket_acl` contains a grant to the `AllUsers` or
  `AuthenticatedUsers` predefined group.

## Screenshots to Capture
- [ ] IAM Role
- [ ] Lambda Configuration
- [ ] Test Invocation/Output (against the deliberately public test bucket)
- [ ] CloudWatch Logs
- [ ] Final Result (SNS alert email + bucket re-secured)
