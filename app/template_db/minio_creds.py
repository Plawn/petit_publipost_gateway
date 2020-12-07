"""Minio Stuff
"""
from dataclasses import dataclass
from minio import Minio
from pydantic import BaseModel


class MinioCreds(BaseModel):
    accessKey: str
    passKey: str
    host: str
    secure: bool

    def as_client(self) -> Minio:
        return Minio(
            self.host,
            access_key=self.accessKey,
            secret_key=self.passKey,
            secure=self.secure
        )


@dataclass
class MinioPath:
    bucket: str
    filename: str = ''


@dataclass
class PullInformations:
    remote: MinioPath
    minio: Minio
