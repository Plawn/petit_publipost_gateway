from ..base_template_engine import TemplateEngine
from ..model_handler import Model, SyntaxtKit
import requests
from ...minio_creds import PullInformations, MinioPath, MinioCreds
from ..ReplacerMiddleware import MultiReplacer
import json
from dataclasses import dataclass
from ...template_db import RenderOptions, ConfigOptions
from typing import *

EXT = '.xlsx'

SYNTAX_KIT = SyntaxtKit('${', '}', '.')


@dataclass
class Settings:
    host: str
    secure: bool


class PptxTemplator(TemplateEngine):

    requires_env = (
        'host',
        'secure',
    )

    def __init__(self, filename: str, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        super().__init__(filename, pull_infos, replacer, temp_dir, settings)
        PptxTemplator.registered_templates.append(self)

        self.temp_dir = temp_dir
        self.model: Model = None
        self.url: str = None
        self.settings = Settings(settings['host'], settings['secure'])

    def _load_fields(self, fields: List[str] = None) -> None:
        res = requests.post(PptxTemplator.url + '/get_placeholders',
                            json={'name': self.exposed_as}).json()
        res = [(i, {}) for i in res]
        self.model = Model(res, self.replacer, SYNTAX_KIT)
