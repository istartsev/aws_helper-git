import time

from aws_helper.s3 import s3_helper as s3
from tests.base import BaseTest
from tests.settings import S3Settings


class TestS3Bucket(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._bucket_name = 'TEST_AWS_Helper_bucket_%f' % time.time()
        cls._client = s3.S3Helper(S3Settings.S3_ACCESS_KEY,
                                  S3Settings.S3_SECRET_KEY)

    def testCreateDeleteBucket(self):
        self._client.create_bucket(self._bucket_name)
        self.assertTrue(self._isBucketExist(self._bucket_name))

        client = s3.S3Helper(S3Settings.S3_ACCESS_KEY,
                             S3Settings.S3_SECRET_KEY, self._bucket_name)
        client.create_folder('temp')

        self._client.delete_bucket(self._bucket_name)
        self.assertFalse(self._isBucketExist(self._bucket_name))
