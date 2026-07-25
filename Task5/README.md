# Task 5: Restore an EC2 Instance from the Latest Snapshot

## Objective
Automate disaster recovery: find the most recent snapshot of a volume,
register an AMI from it, and launch a replacement instance.

## Files
| File | Purpose |
|---|---|
| `lambda_function.py` | Finds latest snapshot → registers AMI → launches instance |
| `iam_policy.json` | Inline policy for snapshot/image/instance actions |
| `trust_policy.json` | Lambda execution role trust policy |

## Steps Followed

1. **Prerequisite** — Reused Task 2's Lambda to create at least one
   tagged snapshot of a test instance's root volume; noted the
   `SOURCE_VOLUME_ID`.

2. **IAM Role** — Created `ec2-restore-lambda-role` with the trust
   policy and attached `iam_policy.json` inline
   (`DescribeSnapshots`, `RegisterImage`/`CreateImage`,
   `DescribeImages`, `RunInstances`, `CreateTags`).

3. **Lambda Function** — Runtime Python 3.12. Environment variables:
   - `SOURCE_VOLUME_ID = vol-xxxxxxxx`
   - `SUBNET_ID = subnet-xxxxxxxx` (a subnet in the same AZ as the source volume)
   - `SECURITY_GROUP_ID = sg-xxxxxxxx`
   - `ROOT_DEVICE_NAME = /dev/xvda` (matches the source volume's root device)
   Timeout increased to **60s**, since `register_image` + waiting for
   the AMI to become `available` can take longer than the 3s default.

4. **Testing** — Manually invoked with `{}`. Confirmed in the EC2
   console: a new AMI appeared under **AMIs**, and a new `t3.micro`
   instance appeared tagged `RestoredFrom=<snapshot-id>` and reached
   the `running` state with the source volume's data intact.
   **Terminated the test instance immediately after verifying**, and
   deregistered the test AMI + deleted its backing snapshot to avoid
   ongoing storage charges.

## Notes
- `register_image` requires the source snapshot's volume to have a
  device/architecture combination compatible with HVM virtualization;
  confirm `RootDeviceName` matches what the original AMI used.
- This pairs naturally with **Task 2** — Task 2 keeps a rolling set of
  recent snapshots, and Task 5 is the "break glass" recovery action
  that consumes the latest one.

## Screenshots to Capture
- [ ] IAM Role
- [ ] Lambda Configuration
- [ ] Test Invocation/Output
- [ ] CloudWatch Logs
- [ ] Final Result (new instance running with restored data, then terminated)
