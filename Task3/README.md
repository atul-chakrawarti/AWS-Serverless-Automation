# Task 3: Auto-Tagging EC2 Instances on Launch

## Objective
Automatically tag newly launched EC2 instances for tracking, ownership,
and cost allocation the moment they enter the `running` state.

## Files
| File | Purpose |
|---|---|
| `lambda_function.py` | Tags the instance on the state-change event |
| `iam_policy.json` | Inline policy for tagging + CloudTrail lookup (bonus) |
| `eventbridge_pattern.json` | Event pattern used for the EventBridge rule |
| `trust_policy.json` | Lambda execution role trust policy |

## Steps Followed

1. **IAM Role** — Created `ec2-auto-tag-lambda-role` with the trust
   policy, and attached `iam_policy.json` inline
   (`ec2:CreateTags`, `ec2:DescribeInstances`, plus
   `cloudtrail:LookupEvents` for the bonus owner-lookup).

2. **Lambda Function** — Runtime Python 3.12. Set environment variable
   `ENVIRONMENT_TAG=Dev`. Default timeout is fine here (fast function).

3. **EventBridge Rule** — Created rule `ec2-running-auto-tag-rule` in
   the EventBridge console with the custom event pattern in
   `eventbridge_pattern.json`, and added this Lambda function as the
   target.

4. **Testing** — Launched a new `t3.micro` test instance. Within ~10–30
   seconds of it reaching `running`, checked the EC2 console **Tags**
   tab and confirmed `LaunchDate`, `Environment`, and `Owner` appeared.

5. **Bonus (Owner from CloudTrail)** — `get_launching_user()` calls
   `cloudtrail:LookupEvents` filtered to `RunInstances` and scans recent
   events for the launched instance ID, extracting the IAM
   principal (`Username`) that made the call. Note: CloudTrail event
   delivery can lag a few minutes, so on a very fresh instance this may
   briefly resolve to `"Unknown"` — this is expected and documented,
   not a bug.

## Screenshots to Capture
- [ ] IAM Role
- [ ] Lambda Configuration
- [ ] EventBridge Rule (event pattern + target)
- [ ] Test Invocation/Output (or real instance launch + resulting tags)
- [ ] CloudWatch Logs
- [ ] Final Result (EC2 instance tags)
