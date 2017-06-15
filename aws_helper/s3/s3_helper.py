import os.path

from aws_helper.base import BaseAWS3Helper

BLOCK_SIZE = 10 * 1024 * 1024


class S3Helper(BaseAWS3Helper):
    def __init__(self, access_key, secret_key, bucket_name=None, region=None):
        super().__init__('s3', region, access_key, secret_key)
        self._bucket_name = bucket_name

    def list_buckets(self):
        return self._client.list_buckets()

    def create_bucket(self, bucket_name):
        self._client.create_bucket(Bucket=bucket_name)

    def delete_bucket(self, bucket_name):
        bucket = self._resource.Bucket(bucket_name)
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()

    def upload_file(self, source, destination):
        self._client.upload_file(source, self._bucket_name, destination)

    def download_file_new(self, source, destination):
        self._client.download_file(self._bucket_name, source, destination)

    def download_fileobj(self, source, destination):
        with open(destination, 'wb') as data:
            self._client.download_fileobj(self._bucket_name, source, data)

    def download_file(self, source, destination):
        key = self._client.Object(self._bucket_name, source).get()
        with open(destination, 'w') as f:
            chunk = key['Body'].read(BLOCK_SIZE)
            while chunk:
                f.write(chunk)
                chunk = key['Body'].read(BLOCK_SIZE)

    def delete_file(self, filename):
        self._client.delete_object(Bucket=self._bucket_name, Key=filename)

    def delete_folder(self, folder_name):
        for key in self._client.Bucket(self._bucket_name).list(
                prefix=os.path.join(folder_name, '', '')):
            key.delete()
