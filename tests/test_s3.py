import filecmp
import shutil
import errno
import os

from unittest import TestCase

import time

import botocore
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
        cls._clearTestFolder()
        super().tearDownClass()

    @classmethod
    def _isBucketExist(cls, bucket_name):
        response = cls._client.list_buckets()
        bl = [bucket['Name'] for bucket in response['Buckets']]

        if bucket_name in bl:
            return True
        return False

    @classmethod
    def _generateRandomFiles(cls, count=10):
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

                with open(filename, 'w') as file:
                    file.write(cls._fake.text())

                files.append(filename)

            return files
        except Exception as e:
            print(str(e))


class TestS3File(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._filename = cls._generateRandomFiles(1)[0]

    def testUploadDownloadFile(self):
        dw_filename = self._filename + '_dw'
        self._client.upload_file(self._filename, self._filename)
        self._client.download_file(self._filename, dw_filename)

        result = filecmp.cmp(self._filename, dw_filename)
        self.assertTrue(result)

        dw_filename_2 = self._filename + '_dw_2'
        self._client.download_fileobj(self._filename, dw_filename_2)

        result = filecmp.cmp(self._filename, dw_filename_2)
        self.assertTrue(result)

        self._client.delete_file(self._filename)
        with self.assertRaises(botocore.exceptions.ClientError):
            self._client.download_file(self._filename, dw_filename)


_TEST_ROOT_FOLDER = 'SecureTest/TestFolders'
_TEST_FILES_COUNT = 5


class TestS3Folder(BaseTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._folder_name = 'test_forder_name_%s' % time.time()
        cls._test_files = cls._generateRandomFiles(_TEST_FILES_COUNT)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def testCreateListDeleteFolder(self):
        full_folder_name = os.path.join(_TEST_ROOT_FOLDER, self._folder_name)

        self._client.create_folder(full_folder_name)
        folder = self._client.get_folder(full_folder_name)

        self.assertEqual(folder['KeyCount'], 1)
        self.assertIsNotNone(folder, 'Folder was not created')

        for file in self._test_files:
            self._client.upload_file(file,
                                     os.path.join(full_folder_name, file))

        folder = self._client.get_folder(full_folder_name)
        self.assertEqual(folder['KeyCount'], _TEST_FILES_COUNT + 1)

        self._client.delete_folder(full_folder_name)

        folder = self._client.get_folder(full_folder_name)
        self.assertEqual(folder['KeyCount'], 0)


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

