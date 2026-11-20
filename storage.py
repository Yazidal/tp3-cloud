import os
import boto3
from botocore.config import Config


def get_s3():
    kwargs = {
        "region_name": os.getenv("S3_REGION", "eu-west-1"),
        "config": Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    }
    # Ces variables existent en local (MinIO) et seront ABSENTES sur AWS :
    # boto3 utilisera alors le rôle d'instance.
    if os.getenv("S3_ENDPOINT_URL"):
        kwargs["endpoint_url"] = os.environ["S3_ENDPOINT_URL"]
    if os.getenv("S3_ACCESS_KEY"):
        kwargs["aws_access_key_id"] = os.environ["S3_ACCESS_KEY"]
        kwargs["aws_secret_access_key"] = os.environ["S3_SECRET_KEY"]
    return boto3.client("s3", **kwargs)


BUCKET = os.environ["S3_BUCKET"]