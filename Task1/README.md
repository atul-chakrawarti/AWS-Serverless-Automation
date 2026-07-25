# Task 1: Automated S3 Bucket Cleanup (Objects Older Than 30 Days)

## Objective
Automatically delete objects from an S3 bucket that are older than a
retention period (30 days in production).

## Files
| File | Purpose |
|---|---|
| `lambda_function.py` | Lambda handler that lists and deletes stale objects |
| `iam_policy.json` | Least-privilege inline policy (scoped to one bucket) |
| `trust_policy.json` | Trust policy allowing Lambda to assume the execution role |

## Steps Followed

1. **S3 Setup**
   - Created an S3 bucket, e.g. `s3-cleanup-demo-<yourname>`, in `us-east-1`.
   - Uploaded several test files.
   - For testing, set the Lambda environment variable `RETENTION_MINUTES=5`
     instead of waiting 30 days, so recently uploaded files become
     "stale" quickly. Removed this variable (and relied on
     `RETENTION_DAYS=30`) for the final production configuration.

2. **IAM Role**
   - Created an execution role `s3-cleanup-lambda-role` using
     `trust_policy.json` as the trust relationship.
   - Attached `iam_policy.json` as an **inline policy**, after replacing
     `REPLACE_WITH_BUCKET_NAME` with the actual bucket name.

3. **Lambda Function**
   - Runtime: Python 3.12.
   - Created function `s3-stale-object-cleanup`, uploaded
     `lambda_function.py`, attached the IAM role above.
   - Set environment variable `BUCKET_NAME=<your-bucket-name>`.
   - Timeout increased to 30s (default 3s is often too short once a
     bucket has many objects).

4. **Testing**
   - Manually invoked the function from the Lambda console **Test** tab
     with an empty `{}` event (this function is not event-driven).
   - Confirmed in the S3 console that only the newer files remained and
     that CloudWatch Logs listed every deleted key.
   - Reset `RETENTION_MINUTES` to unset / `RETENTION_DAYS=30` afterward.

## Discussion Point: Lambda vs. S3 Lifecycle Rules

In production, **S3 Lifecycle Rules** handle "expire objects after N
days" natively with zero code and no compute cost. You'd reach for
**Lambda** instead when the deletion logic is more than a fixed-age
rule — for example: deleting objects that match a specific naming
pattern (e.g. `tmp/*`) combined with age, cross-referencing an external
database or DynamoDB table before deleting, or triggering a
downstream/cross-service action (like an SNS notification or an audit
log entry) at the moment of deletion. Lifecycle Rules can't do
conditional, cross-service, or event-driven logic — that's Lambda's job.

## Screenshots to Capture
- [ ] IAM Role (trust relationship + inline policy)
- [ ] Lambda Configuration (runtime, env vars, role)
- [ ] Test Invocation/Output
- [ ] CloudWatch Logs (deleted object keys)
- [ ] Final Result (S3 console showing only newer files remain)
