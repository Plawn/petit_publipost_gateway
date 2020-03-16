"""
Empty interfaces for static typing linting



"""
from abc import abstractmethod, ABC
from .ReplacerMiddleware import MultiReplacer
from typing import Dict, Tuple, Set, List
from ..minio_creds import PullInformations, MinioPath
from .model_handler import Model, SyntaxtKit
from ..template_db import RenderOptions, ConfigOptions
import requests
import json

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

    def render_to(self, data: dict, path: MinioPath, options: RenderOptions) -> None:
        data = {
            'data': data,
            'template_name': self.pull_infos.remote.filename,
            'output_bucket': path.bucket,
            'output_name': path.filename,
            'options': options.compile_options,
            'push_result':options.push_result,
        }
        res = requests.post(self.url + '/publipost', json=data)
        result = json.loads(res.text)
        if 'error' in result:
            if result['error']:
                raise Exception('An error has occured')
        return result

    def to_json(self) -> dict:
        return self.model.structure

    @staticmethod
    def configure(env: ConfigOptions):
        return False

    def get_fields(self) -> List[str]:
        return self.model.fields

    def __repr__(self):
        return f'<{self.__class__.__name__}>'
