from abc import ABC, abstractmethod
from typing import Tuple


class BaseAdapter(ABC):
    @abstractmethod
    def from_doc(self, text: str) -> Tuple[str, dict]:
        ...

    @abstractmethod
    def to_doc(self, text: str) -> str:
        ...

