#!/usr/bin/env python3
"""
Delete orphaned AWS resources (unattached EBS volumes, unassociated EIPs).
Runs in dry-run mode by default — pass --execute to actually delete.
"""

import boto3
import argparse


def cleanup_volumes(ec2, dry_run=True):
    """Delete unattached EBS volumes."""
    volumes = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )["Volumes"]

    print(f"\nFound {len(volumes)} unattached EBS volumes")
    for v in volumes:
        vid = v["VolumeId"]
        size = v["Size"]
        if dry_run:
            print(f"  [DRY RUN] Would delete {vid} ({size}GB)")
        else:
            ec2.delete_volume(VolumeId=vid)
            print(f"  [DELETED] {vid} ({size}GB)")


def cleanup_eips(ec2, dry_run=True):
    """Release unassociated Elastic IPs."""
    addresses = ec2.describe_addresses()["Addresses"]
    unassociated = [
        a for a in addresses
        if "InstanceId" not in a and "NetworkInterfaceId" not in a
    ]

    print(f"\nFound {len(unassociated)} unassociated Elastic IPs")
    for a in unassociated:
        alloc_id = a["AllocationId"]
        ip = a["PublicIp"]
        if dry_run:
            print(f"  [DRY RUN] Would release {ip} ({alloc_id})")
        else:
            ec2.release_address(AllocationId=alloc_id)
            print(f"  [RELEASED] {ip} ({alloc_id})")


def main():
    parser = argparse.ArgumentParser(description="Cleanup orphaned AWS resources")
    parser.add_argument("--profile", default="default")
    parser.add_argument("--region", default="us-east-2")
    parser.add_argument("--execute", action="store_true",
                        help="Actually delete resources (default is dry-run)")
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ec2 = session.client("ec2")

    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"Running in {mode} mode")

    cleanup_volumes(ec2, dry_run=not args.execute)
    cleanup_eips(ec2, dry_run=not args.execute)


if __name__ == "__main__":
    main()
