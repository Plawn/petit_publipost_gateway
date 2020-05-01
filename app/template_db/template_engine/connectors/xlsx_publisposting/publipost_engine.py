import json
from dataclasses import dataclass
from typing import *

import requests

from ....minio_creds import MinioCreds, MinioPath, PullInformations
from ....template_db import ConfigOptions, RenderOptions
from ...base_template_engine import TemplateEngine
from ...model_handler import Model, SyntaxtKit
from ...ReplacerMiddleware import MultiReplacer

EXT = '.xlsx'

SYNTAX_KIT = SyntaxtKit('${', '}', '.')


@dataclass
class Settings:
    host: str
    secure: bool


class XlsxTemplator(TemplateEngine):

    requires_env = (
        'host',
        'secure',
    )

    def __init__(self, filename: str, pull_infos: PullInformations, replacer: MultiReplacer, settings: dict):
        super().__init__(filename, pull_infos, replacer, settings)
        XlsxTemplator.registered_templates.append(self)

        self.settings = Settings(settings['host'], settings['secure'])

    def _load_fields(self, fields: List[str] = None) -> None:
        res = requests.post(self.url + '/get_placeholders',
                            json={'name': self.exposed_as}).json()
        res = [self.replacer.from_doc(i) for i in res]
        self.model = Model(res, self.replacer, SYNTAX_KIT)
