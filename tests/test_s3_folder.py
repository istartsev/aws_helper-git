import time

from coverage.annotate import os

from tests.base import BaseTest

_TEST_ROOT_FOLDER = 'SecureTest/TestFolders'
_TEST_FILES_COUNT = 10


class TestS3Folder(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._folder_name = 'test_folder_name_%s' % time.time()
        cls._test_files = cls._generate_random_files(_TEST_FILES_COUNT)

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


class TestGenFolder(BaseTest):
    def setUp(self):
        self._test_files_count = _TEST_FILES_COUNT
        self._big_folder = os.path.join(_TEST_ROOT_FOLDER, 'bigOne')
        folder = self._client.get_folder(self._big_folder)
        if folder['KeyCount'] < self._test_files_count:
            i = 0
            files = self._generate_random_files(self._test_files_count, 10)
            for file in files:
                self._client.upload_file(file, os.path.join(
                    self._big_folder, file.split('/')[-1]))
                i = i + 1

    def testListGenFolder(self):
        i = 0
        for _ in self._client.get_folder_objects(self._big_folder,
                                                 max_keys=3):
            i = i + 1

        self.assertEqual(i, self._test_files_count)

    def tearDown(self):
        self._client.delete_folder(self._big_folder)
