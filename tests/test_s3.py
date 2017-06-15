import filecmp
import shutil
import errno
import os

from unittest import TestCase

import time
from faker import Faker

from aws_helper.s3 import s3_helper as s3
from tests.settings import S3Settings


class BaseTest(TestCase):
    @classmethod
    def _clearTestFolder(cls):
        try:
            shutil.rmtree(S3Settings.TEST_FOLDER)
        except Exception as error:
            print('Failed to clear TestFolder. The reason:', str(error))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Clearing folder with test data
        cls._clearTestFolder()

        cls._client = s3.S3Helper(S3Settings.S3_ACCESS_KEY,
                                  S3Settings.S3_SECRET_KEY, None, None)

    @classmethod
    def tearDownClass(cls):
        cls._clearTestFolder()
        super().tearDownClass()

    @classmethod
    def _isBucketExist(cls, bucket_name):
        response = cls._client.list_buckets()
        bl = [bucket['Name'] for bucket in response['Buckets']]

        if bucket_name in bl:
            return True
        return False


class TestS3File(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Need to create a test bucket if it doesn't not exist
        if cls._isBucketExist(S3Settings.BUCKET_NAME):
            cls._client.create_bucket(S3Settings.BUCKET_NAME)

        # Reinitialize _client with the preset bucket
        cls._client = s3.S3Helper(S3Settings.S3_ACCESS_KEY,
                                  S3Settings.S3_SECRET_KEY,
                                  S3Settings.BUCKET_NAME)
        cls._fake = Faker()
        cls._filename = '%s/test.file' % S3Settings.TEST_FOLDER

        if not os.path.exists(os.path.dirname(cls._filename)):
            try:
                os.makedirs(os.path.dirname(cls._filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(cls._filename, 'w') as file:
            file.write(cls._fake.text())

    def testUploadDownloadFile(self):
        dw_filename = self._filename + '_dw'
        self._client.upload_file(self._filename, self._filename)
        self._client.download_file_new(self._filename, dw_filename)

        result = filecmp.cmp(self._filename, dw_filename)
        self.assertTrue(result)git




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

        self._client.delete_bucket(self._bucket_name)
        self.assertFalse(self._isBucketExist(self._bucket_name))

