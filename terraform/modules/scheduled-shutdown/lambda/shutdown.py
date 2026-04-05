import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Stop or start EC2 and RDS instances tagged for auto-shutdown."""
    tag_key = os.environ.get("TARGET_TAG_KEY", "AutoShutdown")
    tag_value = os.environ.get("TARGET_TAG_VALUE", "true")
    action = os.environ.get("ACTION", "stop")

    ec2 = boto3.client("ec2")
    rds = boto3.client("rds")

    # --- EC2 ---
    filters = [
        {"Name": f"tag:{tag_key}", "Values": [tag_value]},
    ]

    if action == "stop":
        filters.append({"Name": "instance-state-name", "Values": ["running"]})
    else:
        filters.append({"Name": "instance-state-name", "Values": ["stopped"]})

    reservations = ec2.describe_instances(Filters=filters)["Reservations"]
    instance_ids = [
        i["InstanceId"]
        for r in reservations
        for i in r["Instances"]
    ]

    if instance_ids:
        if action == "stop":
            ec2.stop_instances(InstanceIds=instance_ids)
            logger.info(f"Stopped EC2 instances: {instance_ids}")
        else:
            ec2.start_instances(InstanceIds=instance_ids)
            logger.info(f"Started EC2 instances: {instance_ids}")
    else:
        logger.info(f"No EC2 instances to {action}")

    # --- RDS ---
    db_instances = rds.describe_db_instances()["DBInstances"]
    for db in db_instances:
        db_tags = rds.list_tags_for_resource(
            ResourceName=db["DBInstanceArn"]
        )["TagList"]
        tag_match = any(
            t["Key"] == tag_key and t["Value"] == tag_value for t in db_tags
        )

        if not tag_match:
            continue

        if action == "stop" and db["DBInstanceStatus"] == "available":
            rds.stop_db_instance(DBInstanceIdentifier=db["DBInstanceIdentifier"])
            logger.info(f"Stopped RDS: {db['DBInstanceIdentifier']}")
        elif action == "start" and db["DBInstanceStatus"] == "stopped":
            rds.start_db_instance(DBInstanceIdentifier=db["DBInstanceIdentifier"])
            logger.info(f"Started RDS: {db['DBInstanceIdentifier']}")

    return {
        "statusCode": 200,
        "body": f"Completed {action} action. EC2: {len(instance_ids)} instances"
    }