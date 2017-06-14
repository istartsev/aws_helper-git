import filecmp
import shutil
import errno
import os

from unittest import TestCase
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
        try:
            super().setUpClass()
            # Clearing folder with test data
            cls._clearTestFolder()

            cls._client = s3.S3Helper(None, None,
                                      S3Settings.S3_ACCESS_KEY,
                                      S3Settings.S3_SECRET_KEY)
            response = cls._client.list_buckets()
            bl = [bucket['Name'] for bucket in response['Buckets']]

            # Need to create a test bucket if it doesn't not exist
            if S3Settings.BUCKET_NAME not in bl:
                cls._client.create_bucket(S3Settings.BUCKET_NAME)

            # Reinitialize _client with the preset bucket
            cls._client = s3.S3Helper(S3Settings.BUCKET_NAME, None,
                                      S3Settings.S3_ACCESS_KEY,
                                      S3Settings.S3_SECRET_KEY)
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

        except Exception as error:
            print(str(error))
            raise

    @classmethod
    def tearDownClass(cls):
        cls._clearTestFolder()
        super().tearDownClass()


class TestS3(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def testUploadDownloadFile(self):
        try:
            dw_filename = self._filename + '_dw'
            self._client.upload_file(self._filename, self._filename)
            self._client.download_file_new(self._filename, dw_filename)

            result = filecmp.cmp(self._filename, dw_filename)
            self.assertTrue(result)

        except Exception as error:
            print(str(error))
            raise
