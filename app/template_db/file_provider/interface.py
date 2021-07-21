from abc import ABC, abstractmethod
from typing import Generator, Optional
import io


class File(ABC):
    def __init__(self, last_modified_at, path: str):
        self.path: str = path
        self.last_modified_at = last_modified_at
        self.content: Optional[io.BytesIO] = None

    @abstractmethod
    def download(self):
        ...


class Path(ABC):
    pass


class BaseFileProvider(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def list_files(self, directory: str) -> Generator[Path, None, None]:
        ...

    @abstractmethod
    def get_file(self, path: Path) -> File:
        ...


if __name__ == '__main__':
    a = BaseFileProvider()
    for file in a.list_files('root'):
        print(file)
