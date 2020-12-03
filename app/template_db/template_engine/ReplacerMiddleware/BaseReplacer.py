from abc import ABC, abstractmethod
from typing import Tuple


class BaseReplacer(ABC):
    @abstractmethod
    def from_doc(self, text: str) -> Tuple[str, dict]:
        ...

    @abstractmethod
    def to_doc(self, text: str) -> str:
        ...

