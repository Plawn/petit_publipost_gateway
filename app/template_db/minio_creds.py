"""Minio Stuff
"""
import minio

class MinioCreds:
    def __init__(self, host: str, key: str, password: str):
        self.key = key
        self.password = password
        self.host = host


class MinioPath:
    def __init__(self, bucket: str, filename: str = ''):
        self.bucket = bucket
        self.filename = filename

    def to_json(self):
        return {
            'bucket': self.bucket,
            'filename': self.filename,
        }


class PullInformations:
    def __init__(self, local: str, remote: MinioPath, minio_instance: minio.Minio):
        self.local = local
        self.remote = remote
        self.minio = minio_instance
