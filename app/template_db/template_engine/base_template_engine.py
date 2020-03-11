"""
Empty interfaces for static typing linting



"""
from abc import abstractmethod, ABC
from .ReplacerMiddleware import MultiReplacer
from typing import Dict, Tuple, Set, List
from ..minio_creds import PullInformations
from .model_handler import Model, SyntaxtKit


class Template(ABC):
    @abstractmethod
    def save(self, filename: str):
        pass


class TemplateEngine(ABC):
    requires_env: Tuple[str] = []

    @classmethod
    def check_env(cls, env: dict) -> bool:
        missing_keys: Set[str] = set()
        for key in cls.requires_env:
            if key not in env:
                missing_keys.add(key)
        return len(missing_keys) == 0, missing_keys

    @abstractmethod
    def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        self.model = Model([], replacer, SyntaxtKit('', '', ''))
        self.replacer = replacer

    @abstractmethod
    def render_to(self, data: Dict[str, str], filename: str) -> None:
        pass

    def to_json(self) -> dict:
        return self.model.structure

    @staticmethod
    def configure(env: dict):
        return False

    def get_fields(self) -> List[str]:
        return self.model.fields

    def __repr__(self):
        return f'<{self.__class__.__name__}>'
