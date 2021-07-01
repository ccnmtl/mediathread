from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class S3PrivateStorage(S3Boto3Storage):
    default_acl = 'private'
    location = 'private'

    def __init__(self):
        super(S3PrivateStorage, self).__init__()
        self.bucket_name = getattr(
            settings,
            'S3_PRIVATE_STORAGE_BUCKET_NAME',
            'mediathread-private-uploads')


private_storage = S3PrivateStorage()
