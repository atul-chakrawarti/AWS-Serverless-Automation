"""
Task 3: Auto-Tagging EC2 Instances on Launch

Triggered by an EventBridge rule matching:
    source: aws.ec2
    detail-type: "EC2 Instance State-change Notification"
    detail.state: running

Tags the newly running instance with LaunchDate and Owner (bonus:
Owner is looked up from CloudTrail if not passed in explicitly).

Environment variables:
    ENVIRONMENT_TAG - Value for the 'Environment' tag (default: "Dev")
"""

import os
import boto3
from datetime import datetime, timezone

ec2_client = boto3.client("ec2")
cloudtrail_client = boto3.client("cloudtrail")


def get_launching_user(instance_id):
    """
    Bonus: look up the IAM identity that launched this instance by
    searching recent CloudTrail events for RunInstances referencing
    this instance ID. Falls back to 'Unknown' if not found (CloudTrail
    lookup can lag a few minutes behind the actual API call).
    """
    try:
        response = cloudtrail_client.lookup_events(
            LookupAttributes=[
                {"AttributeKey": "EventName", "AttributeValue": "RunInstances"}
            ],
            MaxResults=20,
        )
        for event in response.get("Events", []):
            if instance_id in event.get("CloudTrailEvent", ""):
                username = event.get("Username", "Unknown")
                return username
    except Exception as exc:
        print(f"CloudTrail lookup failed: {exc}")
    return "Unknown"


def lambda_handler(event, context):
    detail = event.get("detail", {})
    instance_id = detail.get("instance-id")

    if not instance_id:
        print("No instance-id found in event; nothing to tag.")
        return {"statusCode": 400, "message": "No instance-id in event"}

    launch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    environment = os.environ.get("ENVIRONMENT_TAG", "Dev")
    owner = get_launching_user(instance_id)

    tags = [
        {"Key": "LaunchDate", "Value": launch_date},
        {"Key": "Environment", "Value": environment},
        {"Key": "Owner", "Value": owner},
    ]

    ec2_client.create_tags(Resources=[instance_id], Tags=tags)

    print(f"Tagged instance {instance_id} with: {tags}")

    return {
        "statusCode": 200,
        "instanceId": instance_id,
        "tagsApplied": tags,
    }
