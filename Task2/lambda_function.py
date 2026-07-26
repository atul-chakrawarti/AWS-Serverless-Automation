"""
Task 2: Automated EBS Snapshot Creation and Cleanup

Creates a snapshot of a specified EBS volume, tags it, then deletes any
snapshots (owned by this account, tagged CreatedBy=Lambda-Backup) that
are older than a retention period.

Environment variables:
    VOLUME_ID         - EBS volume ID to snapshot (falls back to
                        DEFAULT_VOLUME_ID below if not set)
    RETENTION_DAYS    - Age threshold for cleanup in days (default: 30)
    RETENTION_MINUTES - Optional override for quick testing
"""

import os
import boto3
from datetime import datetime, timedelta, timezone

ec2_client = boto3.client("ec2")

TAG_KEY = "CreatedBy"
TAG_VALUE = "Lambda-Backup"

# Default volume used for this deployment; override via VOLUME_ID env var
DEFAULT_VOLUME_ID = "vol-0b5b3717a57a66d22"


def get_cutoff_time():
    retention_minutes = os.environ.get("RETENTION_MINUTES")
    if retention_minutes:
        delta = timedelta(minutes=int(retention_minutes))
    else:
        retention_days = int(os.environ.get("RETENTION_DAYS", "30"))
        delta = timedelta(days=retention_days)
    return datetime.now(timezone.utc) - delta


def create_snapshot(volume_id):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    response = ec2_client.create_snapshot(
        VolumeId=volume_id,
        Description=f"Automated backup of {volume_id} on {today}",
        TagSpecifications=[
            {
                "ResourceType": "snapshot",
                "Tags": [
                    {"Key": TAG_KEY, "Value": TAG_VALUE},
                    {"Key": "SourceVolume", "Value": volume_id},
                    {"Key": "CreatedDate", "Value": today},
                ],
            }
        ],
    )
    snapshot_id = response["SnapshotId"]
    print(f"Created snapshot: {snapshot_id} for volume {volume_id}")
    return snapshot_id


def cleanup_old_snapshots(cutoff_time):
    deleted_ids = []
    paginator = ec2_client.get_paginator("describe_snapshots")
    page_iterator = paginator.paginate(
        OwnerIds=["self"],
        Filters=[{"Name": f"tag:{TAG_KEY}", "Values": [TAG_VALUE]}],
    )

    for page in page_iterator:
        for snap in page.get("Snapshots", []):
            start_time = snap["StartTime"]  # timezone-aware
            if start_time < cutoff_time:
                snap_id = snap["SnapshotId"]
                try:
                    ec2_client.delete_snapshot(SnapshotId=snap_id)
                    deleted_ids.append(snap_id)
                    print(f"Deleted old snapshot: {snap_id} (created {start_time.isoformat()})")
                except Exception as exc:
                    print(f"ERROR deleting {snap_id}: {exc}")

    return deleted_ids


def lambda_handler(event, context):
    volume_id = os.environ.get("VOLUME_ID", DEFAULT_VOLUME_ID)

    cutoff_time = get_cutoff_time()
    print(f"Volume: {volume_id}")
    print(f"Cleanup cutoff time (UTC): {cutoff_time.isoformat()}")

    created_snapshot_id = create_snapshot(volume_id)
    deleted_snapshot_ids = cleanup_old_snapshots(cutoff_time)

    print(f"Created: {created_snapshot_id}")
    print(f"Total deleted: {len(deleted_snapshot_ids)} -> {deleted_snapshot_ids}")

    return {
        "statusCode": 200,
        "createdSnapshot": created_snapshot_id,
        "deletedSnapshots": deleted_snapshot_ids,
    }
