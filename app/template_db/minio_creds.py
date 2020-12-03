"""Minio Stuff
"""
import minio
from minio import Minio


class MinioCreds:
    def __init__(self, host: str, accessKey: str, passKey: str, secure: bool):
        self.key = accessKey
        self.password = passKey
        self.host = host
        self.secure = secure

    def as_client(self) -> Minio:
        return minio.Minio(
            self.host,
            access_key=self.key,
            secret_key=self.password,
            secure=self.secure
        )


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
