from urllib.parse import urlparse
import logging
import boto3
from botocore.exceptions import ClientError


def create_presigned_url(
        bucket_name, object_name,
        expiration=3600,
        aws_key=None, aws_secret=None):
    """Generate a presigned URL to share an S3 object

    From: https://boto3.amazonaws.com/v1/documentation/api/latest/
                                 guide/s3-presigned-urls.html
    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to
        remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret)

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name,
                    'Key': object_name},
            ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def get_signed_s3_url(url, bucket, aws_key, aws_secret):
    url = urlparse(url)
    object_name = url.path.lstrip('/')
    return create_presigned_url(
        bucket, object_name, 3600,
        aws_key, aws_secret)
