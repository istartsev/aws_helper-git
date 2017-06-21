import filecmp
import io
import time
from multiprocessing import Process

import botocore.exceptions

from tests.base import BaseTest


class TestS3File(BaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._filename = cls._generate_random_files(1)[0]

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
        with self.assertRaises(botocore.ClientError):
            self._client.download_file(self._filename, dw_filename)


from collections import deque

from concurrent.futures import ThreadPoolExecutor

io_pool_exc = ThreadPoolExecutor()

class LoopedIO(deque):
    def __init__(self, size=10, timeout=60):
        super().__init__(maxlen=size)
        self._timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def write(self, chunk, *args, **kwargs):

        tries = self._timeout
        while tries:
            if self.__len__() < self.maxlen:
                break
            time.sleep(1)
            tries -= 1

        if self.__len__() >= self.maxlen:
            raise TimeoutError

        self.append(chunk)
        return self.__len__()

    def read(self, *args, **kwargs):
        tries = self._timeout
        while tries:
            if self.__len__() != 0:
                break
            time.sleep(1)
            tries -= 1

        if self.__len__() == 0:
            raise TimeoutError

        return self.pop()


class TestS3FileSocket(BaseTest):
    @classmethod
    def setUpClass(cls):
        try:
            super().setUpClass()
            cls._filename = cls._generate_random_files(1, 23 * 1024 * 1024)[0]
        except Exception as e:
            print(e)

    def testBigFileRAMUpload(self):
        sf = LoopedIO(size=1)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._client.upload_fileobj1, sf,
                                     'stream_test_%s' %
                                     time.time())

            with open(self._filename, 'rb') as f:
                def read1k():
                    return f.read(8*1024*1024)

                for piece in iter(read1k, b''):
                    sf.write(piece)

            print(future.result())

    def testSocketUpload(self):
        sf = LoopedIO(size=1)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._client.upload_fileobj1, sf,
                                     'stream_test_%s' %
                                     time.time())

            with open(self._filename, 'rb') as f:
                def read1k():
                    return f.read(8*1024*1024)

                for piece in iter(read1k, b''):
                    sf.write(piece)

            print(future.result())

