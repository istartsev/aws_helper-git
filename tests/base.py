import shutil
from unittest import TestCase

import time

import errno
from coverage.annotate import os
from faker import Faker

from aws_helper.s3 import s3_helper as s3
from tests.settings import S3Settings


class BaseTest(TestCase):
    @classmethod
    def _clear_test_folder(cls):
        try:
            shutil.rmtree(S3Settings.TEST_FOLDER)
        except Exception as error:
            print('Failed to clear TestFolder. The reason:', str(error))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Clearing folder with test data
        cls._clear_test_folder()
        cls._fake = Faker()
        cls._client = s3.S3Helper(S3Settings.S3_ACCESS_KEY,
                                  S3Settings.S3_SECRET_KEY, None, None)

        # Need to create a test bucket if it doesn't exist
        if cls._isBucketExist(S3Settings.BUCKET_NAME):
            cls._client.create_bucket(S3Settings.BUCKET_NAME)

        # Reinitialize _client with the preset bucket
        cls._client = s3.S3Helper(S3Settings.S3_ACCESS_KEY,
                                  S3Settings.S3_SECRET_KEY,
                                  S3Settings.BUCKET_NAME)

    @classmethod
    def tearDownClass(cls):
        cls._clear_test_folder()
        super().tearDownClass()

    @classmethod
    def _isBucketExist(cls, bucket_name):
        response = cls._client.list_buckets()
        bl = [bucket['Name'] for bucket in response['Buckets']]

        if bucket_name in bl:
            return True
        return False

    @classmethod
    def _generate_random_files(cls, count=10, filesize=10240):
        try:
            files = []
            for _ in range(count):

                filename = os.path.join(S3Settings.TEST_FOLDER,
                                        str(time.time()))
                if not os.path.exists(os.path.dirname(filename)):
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                with open(filename, 'wb') as file:
                    file.write(os.urandom(filesize))

                files.append(filename)

            return files
        except Exception as e:
            print(str(e))
