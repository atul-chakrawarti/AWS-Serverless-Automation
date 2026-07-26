"""
Task 4: Daily AWS Cost Alert Using Cost Explorer API and SNS

Queries month-to-date UnblendedCost via the Cost Explorer API and
publishes an SNS alert if spend exceeds a configured threshold.

Environment variables:
    SNS_TOPIC_ARN     - ARN of the SNS topic to publish alerts to (falls
                        back to DEFAULT_SNS_TOPIC_ARN below if not set)
    COST_THRESHOLD_USD - Dollar threshold to alert on (default: "50")

Note: Cost Explorer's ce:GetCostAndUsage is billed per API call
(roughly $0.01/call, i.e. ~₹1). Do not schedule this to run more
often than daily, and avoid re-running it repeatedly while testing.
"""

import os
import boto3
from datetime import date, timedelta

ce_client = boto3.client("ce")
sns_client = boto3.client("sns")

# Default topic used for this deployment; override via SNS_TOPIC_ARN env var
DEFAULT_SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:280768229384:aws-cost-alerts"


def get_month_to_date_cost():
    today = date.today()
    start_of_month = today.replace(day=1).isoformat()
    # Cost Explorer's End date is exclusive, so use tomorrow to include today
    end_date = (today + timedelta(days=1)).isoformat()

    response = ce_client.get_cost_and_usage(
        TimePeriod={"Start": start_of_month, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
    )

    results = response.get("ResultsByTime", [])
    if not results:
        return 0.0

    amount_str = results[0]["Total"]["UnblendedCost"]["Amount"]
    return float(amount_str)


def lambda_handler(event, context):
    topic_arn = os.environ.get("SNS_TOPIC_ARN", DEFAULT_SNS_TOPIC_ARN)

    threshold = float(os.environ.get("COST_THRESHOLD_USD", "50"))

    current_spend = get_month_to_date_cost()
    print(f"Month-to-date UnblendedCost: ${current_spend:.4f}")
    print(f"Threshold: ${threshold:.2f}")

    alert_sent = False
    if current_spend > threshold:
        message = (
            f"AWS Cost Alert: Month-to-date spend is ${current_spend:.2f}, "
            f"which exceeds your threshold of ${threshold:.2f}."
        )
        sns_client.publish(
            TopicArn=topic_arn,
            Subject="AWS Cost Alert - Threshold Exceeded",
            Message=message,
        )
        alert_sent = True
        print("Alert published to SNS.")
    else:
        print("Spend is within threshold; no alert sent.")

    return {
        "statusCode": 200,
        "currentSpend": current_spend,
        "threshold": threshold,
        "alertSent": alert_sent,
    }
