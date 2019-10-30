"""
Empty interfaces for static typing linting



"""
from abc import abstractmethod, ABC
from .ReplacerMiddleware import MultiReplacer
from typing import Dict


class Template(ABC):
    @abstractmethod
    def save(self, filename: str):
        pass


class TemplateEngine(ABC):
    @abstractmethod
    def __init__(self, filename: str, replacer: MultiReplacer):
        pass

    @abstractmethod
    def apply_template(self, data: Dict[str, str]) -> Template:
        pass

    @abstractmethod
    def render_to(self, data: Dict[str, str], filename: str) -> None:
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__}>'
