"""
Task 1: Automated S3 Bucket Cleanup (Objects Older Than 30 Days)

Deletes objects in a target S3 bucket whose LastModified timestamp is
older than a configurable retention period (default 30 days).

Environment variables:
    BUCKET_NAME     - Name of the S3 bucket to clean up (required)
    RETENTION_DAYS  - Age threshold in days (default: 30). For testing,
                      you can temporarily use RETENTION_MINUTES instead.
    RETENTION_MINUTES - Optional override for quick testing (e.g. "5").
                         If set, this takes precedence over RETENTION_DAYS.
"""

import os
import boto3
from datetime import datetime, timedelta, timezone

s3_client = boto3.client("s3")


def get_cutoff_time():
    """Compute the cutoff datetime; supports minute-level testing."""
    retention_minutes = os.environ.get("RETENTION_MINUTES")
    if retention_minutes:
        delta = timedelta(minutes=int(retention_minutes))
    else:
        retention_days = int(os.environ.get("RETENTION_DAYS", "30"))
        delta = timedelta(days=retention_days)
    return datetime.now(timezone.utc) - delta


def lambda_handler(event, context):
    bucket_name = os.environ.get("BUCKET_NAME")
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable is required")

    cutoff_time = get_cutoff_time()
    print(f"Bucket: {bucket_name}")
    print(f"Cutoff time (UTC): {cutoff_time.isoformat()}")

    deleted_objects = []
    paginator = s3_client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket_name):
        contents = page.get("Contents", [])
        if not contents:
            continue

        objects_to_delete = []
        for obj in contents:
            last_modified = obj["LastModified"]  # already timezone-aware (UTC)
            if last_modified < cutoff_time:
                objects_to_delete.append({"Key": obj["Key"]})

        if objects_to_delete:
            # delete_objects supports up to 1000 keys per call
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i + 1000]
                response = s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={"Objects": batch, "Quiet": False},
                )
                for deleted in response.get("Deleted", []):
                    deleted_objects.append(deleted["Key"])
                for error in response.get("Errors", []):
                    print(f"ERROR deleting {error['Key']}: {error['Message']}")

    print(f"Total objects deleted: {len(deleted_objects)}")
    for key in deleted_objects:
        print(f"Deleted: {key}")

    return {
        "statusCode": 200,
        "bucket": bucket_name,
        "deletedCount": len(deleted_objects),
        "deletedObjects": deleted_objects,
    }
