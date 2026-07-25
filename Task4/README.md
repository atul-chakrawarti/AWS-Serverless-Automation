# Task 4: Daily AWS Cost Alert Using Cost Explorer API and SNS

## Objective
Check month-to-date AWS spend daily via the Cost Explorer API and send
an SNS email alert if spend crosses a threshold.

## Files
| File | Purpose |
|---|---|
| `lambda_function.py` | Queries Cost Explorer, publishes SNS alert if over threshold |
| `iam_policy.json` | Inline policy scoped to `ce:GetCostAndUsage` + one SNS topic |
| `trust_policy.json` | Lambda execution role trust policy |

## Steps Followed

1. **SNS Setup** — Created topic `aws-cost-alerts` in `us-east-1`,
   subscribed my email, and confirmed the subscription from the
   confirmation email.

2. **IAM Role** — Created `cost-alert-lambda-role` with the trust
   policy, and attached `iam_policy.json` inline after replacing
   `REPLACE_WITH_ACCOUNT_ID` and `REPLACE_WITH_TOPIC_NAME` with the
   real account ID and `aws-cost-alerts`.

3. **Lambda Function** — Runtime Python 3.12. Environment variables:
   - `SNS_TOPIC_ARN = arn:aws:sns:us-east-1:<account-id>:aws-cost-alerts`
   - `COST_THRESHOLD_USD = 50`
   Timeout increased to 15s (Cost Explorer can be a bit slow to respond).

4. **EventBridge** — Created a scheduled rule `daily-cost-check-rule`
   using `cron(0 8 * * ? *)` (8 AM UTC daily), targeting this function.

5. **Testing** — Temporarily set `COST_THRESHOLD_USD=0.01` and manually
   invoked the function **only a few times** (Cost Explorer API calls
   cost ~$0.01/₹1 each — avoided repeated/scheduled testing runs).
   Confirmed the SNS email alert arrived, then reset the threshold to
   `50` for the real daily schedule.

## Discussion Point: Lambda vs. AWS Budgets

**AWS Budgets** is the managed, no-code alternative for simple
threshold alerts and is the right default for most accounts. You'd
still write custom Lambda logic like this when you need: **per-service
or per-tag cost breakdowns** in the alert body, delivery to
**Slack/Teams/webhook** instead of just email/SNS, or **anomaly-based**
logic (e.g. "alert if today's spend is 2x the 7-day average") that
Budgets' flat-threshold model can't express.

## Screenshots to Capture
- [ ] IAM Role
- [ ] Lambda Configuration
- [ ] Test Invocation/Output
- [ ] CloudWatch Logs
- [ ] Final Result (SNS email alert received)
