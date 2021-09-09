
from __future__ import annotations
from abc import abstractmethod
import io
from typing import Any, Dict, Generator, Optional
import minio
from ....file_provider.interface import File, FileProvider, Path


class MinioPath(Path):
    def __init__(self, bucket: str, path: str) -> None:
        self.bucket = bucket
        self.path = path

    def of(bucket: str, path: Optional[str] = None) -> Path:
        return MinioPath(bucket, path)

    @property
    def value(self):
        return f's3:{self.bucket}:{self.path}'

    def full(self):
        return 's3', {
            'bucket': self.bucket,
            'path': self.path,
        }


class MinioFile(File):
    def load(self):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError


class MinioProvider(FileProvider):
    def __init__(self, host: str, accessKey: str, passKey: str, secure: bool):
        self.host = host
        self.access_key = accessKey
        self.secret_key = passKey
        self.secure = secure
        self.instance = minio.Minio(
            self.host,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

    @staticmethod
    def of(**kwargs) -> MinioProvider:
        return MinioProvider(**kwargs)

    def list_files(self, directory: MinioPath) -> Generator[File, None, None]:
        files = self.instance.list_objects(
            directory.bucket, prefix=directory.path
        )
        return (
            MinioFile(
                MinioPath(
                    directory.bucket,
                    f'{directory.path}/{f.object_name}',
                ), f.last_modified
            ) for f in files
        )

    def configure_body(self) -> Dict[str, Any]:
        return {
            'host': self.host,
            'access_key': self.access_key,
            'pass_key': self.secret_key,
            'secure': self.secure,
        }