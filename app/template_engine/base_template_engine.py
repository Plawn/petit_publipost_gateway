"""
Empty interfaces for static typing linting



"""
from abc import abstractmethod, ABC
from .ReplacerMiddleware import MultiReplacer
from typing import Dict
from ..minio_creds import PullInformations
from .model_handler import Model

class Template(ABC):
    @abstractmethod
    def save(self, filename: str):
        pass


class TemplateEngine(ABC):
    @abstractmethod
    def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        self.model = Model([], replacer)
        self.replacer = replacer

    @abstractmethod
    def apply_template(self, data: Dict[str, str]) -> Template:
        pass

    @abstractmethod
    def render_to(self, data: Dict[str, str], filename: str) -> None:
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__}>'
