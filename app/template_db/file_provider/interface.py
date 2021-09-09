from __future__ import annotations
from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Any, Dict, Generator, Optional, Tuple
import io

# to create a file


class File(ABC):
    def __init__(self, path: Path, last_modified_at):
        self.path = path
        self.last_modified_at = last_modified_at
        self.content: Optional[io.BytesIO] = None

    @abstractmethod
    def load(self):
        """Fills the content field

        The content field should always be explicitly filled 
        when requested and not automatically loaded
        """
        ...

    @abstractmethod
    def write(self):
        """
        Write the file to it's path

        not needed in this context
        """
        ...


class Path(ABC):
    @abstractstaticmethod
    def of(**kwargs) -> Path:
        pass

    @abstractmethod
    @property
    def value() -> str:
        ...

    @abstractmethod
    def __repr__(self):
        ...

    @abstractmethod
    @property
    def full(self) -> Tuple[str, Dict]:
        ...

    @abstractmethod
    def join(self, other_path: Path) -> Path:
        """
        like os.path.join
        """
        pass

    def __add__(self, other_path: Path) -> Path:
        return self.join(other_path)


class FileProvider(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod
    def list_files(self, directory: str) -> Generator[File, None, None]:
        ...

    @abstractmethod
    def get_file(self, path: Path) -> File:
        ...

    @abstractstaticmethod
    def of(**kwargs) -> FileProvider:
        ...

    @abstractmethod
    def configure_body(self) -> Dict[str, Any]:
        ...


if __name__ == '__main__':
    a = FileProvider()
    for file in a.list_files('root'):
        print(file)
