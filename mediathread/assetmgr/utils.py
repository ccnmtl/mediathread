import boto3
import requests
from django.conf import settings
from os.path import basename, splitext, join
from PIL import Image
from pi_heif import register_heif_opener
from s3sign.utils import create_presigned_url, s3_config, upload_file
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
    return boto3.client(
        's3', config=s3_config,
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
) -> str:
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
    tmp_jpeg = join('/tmp/', filename)
    rgb_im.save(tmp_jpeg)

    # upload to S3, return source url
    s3_client = get_s3_client(aws_key, aws_secret)
    mime_type = 'image/jpeg'

    data = upload_file(
        s3_client, bucket, mime_type, object_name,
        s3_sign_view_settings.get('max_file_size'),
        s3_sign_view_settings.get('acl'),
        s3_sign_view_settings.get('expiration_time'),
        s3_sign_view_settings.get('private')
    )
    print(data)
