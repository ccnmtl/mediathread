import boto3
import requests
import os
import tempfile
from django.conf import settings
from django.utils import timezone
from os.path import basename, splitext
from PIL import Image
from pi_heif import register_heif_opener
from s3sign.utils import (
    DEFAULT_AWS_REGION,
    create_presigned_url, s3_config, get_object_name, upload_file
)
from urllib.parse import urlparse


s3_sign_view_settings = {
    'private': True,
    'root': 'private/',
    'acl': None,
    'expiration_time': 3600 * 8,  # 8 hours
    'max_file_size': 50000000,  # 50mb
}


def get_s3_private_bucket_name() -> str:
    return getattr(
        settings,
        'S3_PRIVATE_STORAGE_BUCKET_NAME',
        'mediathread-private-uploads')


def get_s3_client(aws_key, aws_secret):
    aws_region_name = DEFAULT_AWS_REGION
    if hasattr(settings, 'AWS_S3_REGION_NAME'):
        aws_region_name = settings.AWS_S3_REGION_NAME

    return boto3.client(
        's3', config=s3_config,
        region_name=aws_region_name,
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret)


def get_signed_s3_url(url: str, bucket: str, aws_key: str, aws_secret: str):
    s3_client = get_s3_client(aws_key, aws_secret)

    url = urlparse(url)
    object_name = url.path.lstrip('/')
    object_name = object_name.replace(bucket + '/', '')
    return create_presigned_url(s3_client, bucket, object_name, 3600)


def convert_heic_to_jpg(
        url: str, request: object, bucket: str,
        aws_key: str, aws_secret: str
) -> dict:
    """
    Given an heic image url, convert it to a JPEG. This comprises a
    few steps:
    * Download the file
    * Do the conversion
    * Upload jpeg to S3
    * Return new url
    """
    response = requests.get(url, stream=True)

    # Sort out the new filename
    parsed_url = urlparse(url)
    filename = splitext(basename(parsed_url.path))[0]
    filename = filename + '.jpg'

    # Open the file and convert it
    register_heif_opener()
    im = Image.open(response.raw)
    rgb_im = im.convert('RGB')
    tmp_jpeg, tmp_jpeg_path = tempfile.mkstemp(suffix='.jpg')
    rgb_im.save(tmp_jpeg_path)
    width, height = rgb_im.size

    # upload to S3, return source url
    s3_client = get_s3_client(aws_key, aws_secret)
    object_name = get_object_name(timezone.now(), '.jpg',
                                  s3_sign_view_settings.get('root'))
    uploaded = upload_file(s3_client, tmp_jpeg_path, bucket, object_name)

    os.remove(tmp_jpeg_path)

    data = {
        'url': url,
        'width': width,
        'height': height,
    }

    if uploaded:
        url = 'https://{}.s3.amazonaws.com/{}'.format(bucket, object_name)
        data['url'] = url

    return data
