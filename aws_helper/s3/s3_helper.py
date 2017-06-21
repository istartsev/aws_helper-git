import os.path

from aws_helper.base import BaseAWS3Helper

BLOCK_SIZE = 10 * 1024 * 1024


class S3Helper(BaseAWS3Helper):
    def __init__(self, access_key, secret_key, bucket_name=None, region=None):
        super().__init__('s3', region, access_key, secret_key)
        self._bucket_name = bucket_name

    '''Buckets'''
    def list_buckets(self):
        return self._client.list_buckets()

    def create_bucket(self, bucket_name):
        self._client.create_bucket(Bucket=bucket_name)

    def delete_bucket(self, bucket_name):
        bucket = self._resource.Bucket(bucket_name)
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()

    '''Files'''
    def upload_file(self, source, destination):
        self._client.upload_file(source, self._bucket_name, destination)

    def upload_fileobj1(self, source, destination):
        with source as data:
            self._client.upload_fileobj(data, self._bucket_name, destination)

    def download_file(self, source, destination):
        self._client.download_file(self._bucket_name, source, destination)

    def download_fileobj(self, source, destination):
        with open(destination, 'wb') as data:
            self._client.download_fileobj(self._bucket_name, source, data)

    def delete_file(self, filename):
        self._client.delete_object(Bucket=self._bucket_name, Key=filename)

    '''Folder'''
    def get_folder(self, folder_name):
        return self._client.list_objects_v2(Bucket=self._bucket_name,
                                            Prefix=folder_name)

    def get_folder_objects(self, folder_name, max_keys=100):
        more_objects = True
        found_token = False
        folder_name = os.path.join(folder_name, '')
        while more_objects:
            if not found_token:
                response = self._client.list_objects_v2(
                    Bucket=self._bucket_name,
                    Prefix=folder_name,
                    Delimiter="/",
                    MaxKeys=max_keys)
            else:
                response = self._client.list_objects_v2(
                    Bucket=self._bucket_name,
                    Prefix=folder_name,
                    ContinuationToken=found_token,
                    Delimiter="/",
                    MaxKeys=max_keys)
            # use copy_object or copy_from
            for source in response["Contents"]:
                yield source["Key"]

            # Now check there is more objects to list
            if "NextContinuationToken" in response:
                found_token = response["NextContinuationToken"]
                more_objects = True
            else:
                more_objects = False

    def create_folder(self, folder_name):
        return self._client.put_object(Bucket=self._bucket_name,
                                       Body='',
                                       Key=os.path.join(folder_name, ''))

    def delete_folder(self, folder_name):
        for key in self.get_folder(folder_name)['Contents']:
            self._client.delete_object(Bucket=self._bucket_name,
                                       Key=key['Key'])

    def move_object(self, source, destination):
        self._client.copy_object(Bucket=self._bucket_name,
                                 CopySource=source, Key=destination)
