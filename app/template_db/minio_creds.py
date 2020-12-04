"""Minio Stuff
"""
import minio
from minio import Minio
from pydantic.main import BaseModel


class MinioCreds(BaseModel):
    accessKey: str
    passKey: str
    host: str
    secure: bool

    def as_client(self) -> Minio:
        return minio.Minio(
            self.host,
            access_key=self.accessKey,
            secret_key=self.passKey,
            secure=self.secure
        )


class MinioPath:
    def __init__(self, bucket: str, filename: str = ''):
        self.bucket = bucket
        self.filename = filename


class PullInformations:
    def __init__(self, remote: MinioPath, minio_instance: minio.Minio):
        self.remote = remote
        self.minio = minio_instance
