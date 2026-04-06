#!/usr/bin/env python3
"""
AWS Cost Audit Script
Pulls spend data from Cost Explorer and identifies top cost drivers.
"""

import boto3
import json
import argparse
from datetime import datetime, timedelta, timezone


def get_cost_by_service(ce_client, start_date, end_date):
    """Get cost breakdown by AWS service."""
    response = ce_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    return response["ResultsByTime"]


def get_idle_resources(ec2_client, cw_client):
    """Find EC2 instances with avg CPU < 10% over 14 days."""
    idle_instances = []
    reservations = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )["Reservations"]

    for res in reservations:
        for instance in res["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]

            try:
                cpu_stats = cw_client.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName="CPUUtilization",
                    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    StartTime=datetime.now(tz=timezone.utc) - timedelta(days=14),
                    EndTime=datetime.now(tz=timezone.utc),
                    Period=86400,
                    Statistics=["Average"],
                )

                if cpu_stats["Datapoints"]:
                    avg_cpu = sum(d["Average"] for d in cpu_stats["Datapoints"]) / len(
                        cpu_stats["Datapoints"]
                    )
                    if avg_cpu < 10:
                        idle_instances.append(
                            {
                                "InstanceId": instance_id,
                                "InstanceType": instance_type,
                                "AvgCPU": round(avg_cpu, 2),
                            }
                        )
            except Exception as e:
                print(f"  Skipping {instance_id}: {e}")

    return idle_instances


def get_unattached_volumes(ec2_client):
    """Find EBS volumes not attached to any instance."""
    volumes = ec2_client.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )["Volumes"]

    return [
        {
            "VolumeId": v["VolumeId"],
            "Size_GB": v["Size"],
            "VolumeType": v["VolumeType"],
            "Created": v["CreateTime"].isoformat(),
        }
        for v in volumes
    ]


def get_unassociated_eips(ec2_client):
    """Find Elastic IPs not associated with any instance."""
    addresses = ec2_client.describe_addresses()["Addresses"]
    return [
        {"AllocationId": a["AllocationId"], "PublicIp": a["PublicIp"]}
        for a in addresses
        if "InstanceId" not in a and "NetworkInterfaceId" not in a
    ]


def main():
    parser = argparse.ArgumentParser(description="AWS Cost Audit")
    parser.add_argument("--profile", default="default", help="AWS profile name")
    parser.add_argument("--region", default="us-east-2", help="AWS region")
    parser.add_argument("--months", type=int, default=3, help="Months of cost data")
    args = parser.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ce = session.client("ce")
    ec2 = session.client("ec2")
    cw = session.client("cloudwatch")

    end_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    start_date = (datetime.now(tz=timezone.utc) - timedelta(days=args.months * 30)).strftime(
        "%Y-%m-%d"
    )

    print("=" * 60)
    print("AWS COST AUDIT REPORT")
    print(f"Period: {start_date} to {end_date}")
    print(f"Region: {args.region}")
    print("=" * 60)

    # Cost by service
    print("\n--- COST BY SERVICE (Monthly) ---")
    cost_data = get_cost_by_service(ce, start_date, end_date)
    for period in cost_data:
        print(f"\nMonth: {period['TimePeriod']['Start']}")
        services = sorted(
            period["Groups"], key=lambda x: float(x["Metrics"]["UnblendedCost"]["Amount"]), reverse=True
        )
        for svc in services[:10]:
            amount = float(svc["Metrics"]["UnblendedCost"]["Amount"])
            if amount > 0.01:
                print(f"  {svc['Keys'][0]:40s} ${amount:>10.2f}")

    # Idle instances
    print("\n--- IDLE EC2 INSTANCES (Avg CPU < 10%) ---")
    idle = get_idle_resources(ec2, cw)
    if idle:
        for i in idle:
            print(f"  {i['InstanceId']} ({i['InstanceType']}) - Avg CPU: {i['AvgCPU']}%")
    else:
        print("  No idle instances found")

    # Unattached EBS
    print("\n--- UNATTACHED EBS VOLUMES ---")
    volumes = get_unattached_volumes(ec2)
    if volumes:
        for v in volumes:
            print(f"  {v['VolumeId']} - {v['Size_GB']}GB {v['VolumeType']}")
    else:
        print("  No unattached volumes found")

    # Unassociated EIPs
    print("\n--- UNASSOCIATED ELASTIC IPs ---")
    eips = get_unassociated_eips(ec2)
    if eips:
        for e in eips:
            print(f"  {e['PublicIp']} ({e['AllocationId']}) - ~$3.60/month waste")
    else:
        print("  No unassociated EIPs found")

    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()