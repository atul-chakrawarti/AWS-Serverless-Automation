"""
Task 6: Audit S3 Buckets for Public Access and Notify

Checks every bucket in the account for public exposure via three
signals: the account/bucket-level Block Public Access configuration,
the bucket policy's IsPublic status, and public ACL grants. Publishes
an SNS alert naming any bucket found to be public or under-protected.

Environment variables:
    SNS_TOPIC_ARN - ARN of the SNS topic to publish alerts to (required)
"""

import os
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")
sns_client = boto3.client("sns")

PUBLIC_GRANTEE_URIS = {
    "http://acs.amazonaws.com/groups/global/AllUsers",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
}


def block_public_access_disabled(bucket_name):
    """Returns True if Block Public Access is missing or not fully enabled."""
    try:
        response = s3_client.get_public_access_block(Bucket=bucket_name)
        config = response["PublicAccessBlockConfiguration"]
        return not all([
            config.get("BlockPublicAcls", False),
            config.get("IgnorePublicAcls", False),
            config.get("BlockPublicPolicy", False),
            config.get("RestrictPublicBuckets", False),
        ])
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
            # No config at all = not blocked
            return True
        raise


def bucket_policy_is_public(bucket_name):
    try:
        response = s3_client.get_bucket_policy_status(Bucket=bucket_name)
        return response["PolicyStatus"]["IsPublic"]
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return False
        raise


def acl_has_public_grant(bucket_name):
    try:
        response = s3_client.get_bucket_acl(Bucket=bucket_name)
        for grant in response.get("Grants", []):
            grantee = grant.get("Grantee", {})
            uri = grantee.get("URI")
            if uri in PUBLIC_GRANTEE_URIS:
                return True
        return False
    except ClientError as exc:
        print(f"WARN: could not read ACL for {bucket_name}: {exc}")
        return False


def lambda_handler(event, context):
    topic_arn = os.environ.get("SNS_TOPIC_ARN")
    if not topic_arn:
        raise ValueError("SNS_TOPIC_ARN environment variable is required")

    all_buckets = s3_client.list_buckets().get("Buckets", [])
    print(f"Auditing {len(all_buckets)} bucket(s)")

    public_buckets = []

    for bucket in all_buckets:
        name = bucket["Name"]
        try:
            bpa_disabled = block_public_access_disabled(name)
            policy_public = bucket_policy_is_public(name)
            acl_public = acl_has_public_grant(name)

            is_public = bpa_disabled or policy_public or acl_public

            print(
                f"{name}: BlockPublicAccessDisabled={bpa_disabled}, "
                f"PolicyIsPublic={policy_public}, ACLHasPublicGrant={acl_public} "
                f"-> {'PUBLIC' if is_public else 'private'}"
            )

            if is_public:
                public_buckets.append(name)
        except ClientError as exc:
            print(f"ERROR auditing bucket {name}: {exc}")

    if public_buckets:
        message = (
            "AWS S3 Public Access Audit Alert:\n\n"
            "The following bucket(s) may be publicly accessible:\n"
            + "\n".join(f"- {b}" for b in public_buckets)
        )
        sns_client.publish(
            TopicArn=topic_arn,
            Subject="S3 Public Bucket Alert",
            Message=message,
        )
        print(f"Alert published for {len(public_buckets)} bucket(s): {public_buckets}")
    else:
        print("No public buckets found.")

    return {
        "statusCode": 200,
        "bucketsAudited": len(all_buckets),
        "publicBuckets": public_buckets,
    }
