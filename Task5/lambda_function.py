"""
Task 5: Restore an EC2 Instance from the Latest Snapshot

Finds the most recent snapshot for a given source volume, registers an
AMI from it, and launches a new t3.micro instance from that AMI.

Environment variables:
    SOURCE_VOLUME_ID  - Volume ID whose snapshots we search (required)
    SUBNET_ID         - Subnet to launch the restored instance into (required)
    SECURITY_GROUP_ID - Security group for the restored instance (required)
    ROOT_DEVICE_NAME  - Root device name for the AMI (default: /dev/xvda)
"""

import os
import time
import boto3

ec2_client = boto3.client("ec2")


def find_latest_snapshot(volume_id):
    paginator = ec2_client.get_paginator("describe_snapshots")
    snapshots = []
    for page in paginator.paginate(
        OwnerIds=["self"],
        Filters=[{"Name": "volume-id", "Values": [volume_id]}],
    ):
        snapshots.extend(page.get("Snapshots", []))

    if not snapshots:
        raise ValueError(f"No snapshots found for volume {volume_id}")

    snapshots.sort(key=lambda s: s["StartTime"], reverse=True)
    latest = snapshots[0]
    print(f"Latest snapshot: {latest['SnapshotId']} (StartTime={latest['StartTime'].isoformat()})")
    return latest["SnapshotId"]


def register_ami_from_snapshot(snapshot_id, root_device_name):
    response = ec2_client.register_image(
        Name=f"restored-ami-{snapshot_id}-{int(time.time())}",
        Description=f"AMI restored from snapshot {snapshot_id}",
        Architecture="x86_64",
        RootDeviceName=root_device_name,
        BlockDeviceMappings=[
            {
                "DeviceName": root_device_name,
                "Ebs": {
                    "SnapshotId": snapshot_id,
                    "VolumeType": "gp3",
                    "DeleteOnTermination": True,
                },
            }
        ],
        VirtualizationType="hvm",
        EnaSupport=True,
    )
    ami_id = response["ImageId"]
    print(f"Registered AMI: {ami_id} from snapshot {snapshot_id}")

    waiter = ec2_client.get_waiter("image_available")
    waiter.wait(ImageIds=[ami_id], WaiterConfig={"Delay": 15, "MaxAttempts": 20})
    print(f"AMI {ami_id} is now available")
    return ami_id


def launch_instance(ami_id, snapshot_id, subnet_id, security_group_id):
    response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1,
        SubnetId=subnet_id,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "RestoredFrom", "Value": snapshot_id},
                    {"Key": "Name", "Value": f"restored-instance-{snapshot_id}"},
                ],
            }
        ],
    )
    instance_id = response["Instances"][0]["InstanceId"]
    print(f"Launched new instance: {instance_id}")
    return instance_id


def lambda_handler(event, context):
    source_volume_id = os.environ.get("SOURCE_VOLUME_ID")
    subnet_id = os.environ.get("SUBNET_ID")
    security_group_id = os.environ.get("SECURITY_GROUP_ID")
    root_device_name = os.environ.get("ROOT_DEVICE_NAME", "/dev/xvda")

    missing = [
        name for name, val in [
            ("SOURCE_VOLUME_ID", source_volume_id),
            ("SUBNET_ID", subnet_id),
            ("SECURITY_GROUP_ID", security_group_id),
        ] if not val
    ]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

    snapshot_id = find_latest_snapshot(source_volume_id)
    ami_id = register_ami_from_snapshot(snapshot_id, root_device_name)
    instance_id = launch_instance(ami_id, snapshot_id, subnet_id, security_group_id)

    print(f"Restore complete. New instance ID: {instance_id}")

    return {
        "statusCode": 200,
        "sourceSnapshot": snapshot_id,
        "amiId": ami_id,
        "newInstanceId": instance_id,
    }
