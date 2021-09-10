from urllib.parse import urlparse
import boto3
from s3sign.utils import create_presigned_url, s3_config


def get_signed_s3_url(url, bucket, aws_key, aws_secret):
    s3_client = boto3.client(
        's3', config=s3_config,
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret)

    url = urlparse(url)
    object_name = url.path.lstrip('/')
    object_name = object_name.replace(bucket + '/', '')
    return create_presigned_url(s3_client, bucket, object_name, 3600)
