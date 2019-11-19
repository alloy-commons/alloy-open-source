import json
import os

import boto3
import requests
from botocore.exceptions import ClientError
from dateutil.parser import parse


def get_excludes():
    if "ENV_EXCLUDES" in os.environ:
        return os.environ["ENV_EXCLUDES"].replace(" ", "").split(",")
    else:
        return []


def message_formatter(event, region):
    message_color = "warning"

    event_id = event["id"]
    event_time = event["time"]
    parsed_time = parse(event_time)
    formatted_time = str(parsed_time.replace(microsecond=0))

    event_detail = event["detail"]
    container_name = event_detail["overrides"]["containerOverrides"][0]["name"]
    task_arn = event_detail["taskArn"]
    task_id = task_arn.split("/")[1]
    version = event_detail["version"]
    attachment_status = event_detail["attachments"][0]["status"]

    env_vars = event_detail["overrides"]["containerOverrides"][0]["environment"]
    excludes = get_excludes()
    env_vars_list = []
    for env_var in env_vars:
        if env_var["name"] in excludes:
            env_var_formatted = "%s=\"REDACTED\"" % env_var["name"]
        else:
            env_var_formatted = "%s=\"%s\"" % (env_var["name"], env_var["value"])
        env_vars_list.append(env_var_formatted)
    env_vars_formatted = "\n".join(env_vars_list)

    logs_url = "https://{reg}.console.aws.amazon.com/cloudwatch/home?region={reg}#logEventViewer:group={cn};stream=ecs/{cn}/{tid}".format(reg=region, cn=container_name, tid=task_id)

    container_status = event_detail["containers"][0]["lastStatus"]
    if "RUNNING" in container_status:
        message_color = "good"

    if "exitCode" in event_detail["containers"][0]:
        container_exit = event_detail["containers"][0]["exitCode"]
        container_status = "%s with exit code %s" % (container_status, container_exit)
        if int(container_exit) == 0:
            message_color = "good"
        else:
            message_color = "danger"

    attachment = {
        "attachments": [
            {
                "title": "%s is %s" % (container_name, container_status),
                "fields": [
                    {
                        "title": "Environment Variables",
                        "value": env_vars_formatted,
                        "short": "true"
                    },
                    {
                        "title": "Networking Status",
                        "value": attachment_status,
                        "short": "true"
                    }
                ],
                "actions": [
                    {
                        "type": "button",
                        "text": "Logs",
                        "url": logs_url
                    }
                ],
                "color": message_color,
                "footer": "Event id: %s (version: %s at %s)" % (event_id, version, formatted_time),
            }
        ]
    }

    return attachment


def get_secret(secret_name, region):
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            print("""Secrets Manager can't decrypt the protected secret text
            using the provided KMS key:""", e)
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            print("An error occurred on the server:", e)
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            print("The request had invalid params:", e)
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            print("The request was invalid due to:", e)
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("The requested secret " + secret_name + " was not found")
            raise e
        else:
            print("An error occurred:", e)
            raise e
    else:
        return get_secret_value_response["SecretString"]


def send_notification(message, region):
    secretmanager_secret_name = os.environ["SECRETMANAGER_SECRET_NAME"]
    if secretmanager_secret_name is None:
        slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    else:
        slack_webhook_url = get_secret(secretmanager_secret_name, region)

    if slack_webhook_url is None:
        print("""Slack webhook url is not set. This means that
        SLACK_WEBHOOK_URL environment variable is not set or an error occured
        when retriving the secret from secret manager""")

    req_data = json.dumps(message)
    req_headers = {"Content-type": "application/json"}

    response = requests.post(url=slack_webhook_url, headers=req_headers,
                             data=req_data)
    if response:
        print("Message successfully posted to Slack")
    else:
        print("An error has occurred while attempting to post to Slack")


def lambda_handler(event, context):
    print(json.dumps(event))

    region = event["region"]

    message = message_formatter(event, region)
    send_notification(message, region)


test_message = {
    "account": "667471847564",
    "region": "us-east-2",
    "detail": {
        "launchType": "FARGATE",
        "attachments": [
            {
                "status": "ATTACHED",
                "type": "eni",
                "id": "15613f8b-6dc1-4f3d-81b8-b4bc2c2e3a41",
                "details": [
                    {
                        "name": "subnetId",
                        "value": "subnet-0ef3692db124f204f"
                    },
                    {
                        "name": "networkInterfaceId",
                        "value": "eni-0c52462a536c2d40c"
                    },
                    {
                        "name": "macAddress",
                        "value": "06:83:93:f2:9c:84"
                    },
                    {
                        "name": "privateIPv4Address",
                        "value": "10.0.3.104"
                    }
                ]
            }
        ],
        "stoppingAt": "2019-11-19T21:13:34.795Z",
        "clusterArn": "arn:aws:ecs:us-east-2:667471847564:cluster/primary-cluster",
        "updatedAt": "2019-11-19T21:13:34.795Z",
        "desiredStatus": "STOPPED",
        "createdAt": "2019-11-19T20:38:07.789Z",
        "taskArn": "arn:aws:ecs:us-east-2:667471847564:task/e9511a82-9247-4239-89e9-ffd548ed9ee4",
        "group": "family:voterintake",
        "pullStartedAt": "2019-11-19T20:38:24.975Z",
        "version": 4,
        "stopCode": "EssentialContainerExited",
        "connectivityAt": "2019-11-19T20:38:12.433Z",
        "startedAt": "2019-11-19T20:38:27.975Z",
        "taskDefinitionArn": "arn:aws:ecs:us-east-2:667471847564:task-definition/voterintake:11",
        "containers": [
            {
                "containerArn": "arn:aws:ecs:us-east-2:667471847564:container/5abd8bf1-85db-4f66-a998-ad405f405bc4",
                "taskArn": "arn:aws:ecs:us-east-2:667471847564:task/e9511a82-9247-4239-89e9-ffd548ed9ee4",
                "name": "voterintake",
                "lastStatus": "STOPPED",
                "image": "667471847564.dkr.ecr.us-east-2.amazonaws.com/voterintake",
                "imageDigest": "sha256:7110eb6305145e51da2c7242f43b0db24866d036a5871cde0e3169c6f10bf72c",
                "runtimeId": "f5c93e14ca2eca383361d2599eeb6d5574254640db87175f3b2c593a610053bd",
                "networkInterfaces": [
                    {
                        "privateIpv4Address": "10.0.3.104",
                        "attachmentId": "15613f8b-6dc1-4f3d-81b8-b4bc2c2e3a41"
                    }
                ],
                "cpu": "0",
                "exitCode": 0
            }
        ],
        "executionStoppedAt": "2019-11-19T21:13:24Z",
        "memory": "12288",
        "lastStatus": "DEPROVISIONING",
        "connectivity": "CONNECTED",
        "platformVersion": "1.3.0",
        "overrides": {
            "containerOverrides": [
                {
                    "environment": [
                        {
                            "name": "VOTERINTAKE_OP",
                            "value": "convert-and-load"
                        },
                        {
                            "name": "VOTERINTAKE_STATE",
                            "value": "OH"
                        },
                        {
                            "name": "VOTERINTAKE_DATE",
                            "value": "20191109"
                        },
                        {
                            "name": "TMPDIR",
                            "value": "/data"
                        }
                    ],
                    "name": "voterintake"
                }
            ]
        },
        "pullStoppedAt": "2019-11-19T20:38:27.975Z",
        "stoppedReason": "Essential container in task exited",
        "cpu": "4096"
    },
    "detail-type": "ECS Task State Change",
    "source": "aws.ecs",
    "version": "0",
    "time": "2019-11-19T21:13:34Z",
    "id": "a87af632-7491-ac52-5953-9835d6813176",
    "resources": [
        "arn:aws:ecs:us-east-2:667471847564:task/e9511a82-9247-4239-89e9-ffd548ed9ee4"
    ]
}

message = message_formatter(test_message, "us-east-2")
print message
