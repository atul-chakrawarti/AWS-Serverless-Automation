# Task 2: Automated EBS Snapshot Creation and Cleanup

## Objective
Create a snapshot of an EBS volume on a schedule, tag it, and delete
snapshots older than a retention period.

## Files
| File | Purpose |
|---|---|
| `lambda_function.py` | Creates a snapshot, then deletes stale tagged snapshots |
| `iam_policy.json` | Inline policy for snapshot lifecycle actions |
| `trust_policy.json` | Lambda execution role trust policy |

## Steps Followed

1. **EBS Setup** — Identified an existing EBS volume (root volume of a
   t3.micro test instance) and noted its Volume ID (`vol-xxxxxxxx`).

2. **IAM Role** — Created `ebs-snapshot-lambda-role` with the trust
   policy above and attached `iam_policy.json` inline. EC2 snapshot
   APIs don't support fine-grained resource ARNs the way S3 does, so
   the policy is scoped to the specific **actions** only
   (`CreateSnapshot`, `DescribeSnapshots`, `DeleteSnapshot`,
   `CreateTags`) rather than `*FullAccess`.

3. **Lambda Function** — Runtime Python 3.12. Environment variables:
   - `VOLUME_ID = vol-xxxxxxxx`
   - `RETENTION_DAYS = 30` (used `RETENTION_MINUTES=5` temporarily
     while testing cleanup logic, then removed it).
   Timeout set to 30s.

4. **EventBridge** — Created a scheduled rule
   (`ebs-weekly-snapshot-rule`) using a rate expression
   `rate(7 days)`, targeting this Lambda function.

5. **Testing** — Manually invoked with `{}`. Verified in the EC2 →
   Snapshots console that a new snapshot appeared tagged
   `CreatedBy=Lambda-Backup`, and that CloudWatch Logs printed the
   created snapshot ID. Lowered `RETENTION_MINUTES` briefly to confirm
   old tagged snapshots get deleted on a subsequent run.

## Discussion Point: Lambda vs. AWS Data Lifecycle Manager (DLM)

**AWS Data Lifecycle Manager** automates this exact create/retain/delete
snapshot pattern natively, with no code. You'd still choose **Lambda**
when you need: custom retention logic that isn't just "age-based" (e.g.
"keep the last 5, plus one per month for a year"), cross-account/
cross-region snapshot copies for disaster recovery, or a notification
(SNS/Slack) fired at snapshot completion/failure — none of which DLM
supports out of the box.

## Screenshots to Capture
- [ ] IAM Role
- [ ] Lambda Configuration
- [ ] Test Invocation/Output
- [ ] CloudWatch Logs
- [ ] Final Result (EC2 → Snapshots console)
