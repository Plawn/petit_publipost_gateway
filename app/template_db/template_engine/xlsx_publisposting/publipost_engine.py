from ..base_template_engine import TemplateEngine
from ..model_handler import Model, SyntaxtKit
import requests
from ...minio_creds import PullInformations, MinioPath, MinioCreds
from ..ReplacerMiddleware import MultiReplacer
import json
from dataclasses import dataclass
from ...template_db import RenderOptions, ConfigOptions

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

    def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        XlsxTemplator.registered_templates.append(self)

        self.pull_infos = pull_infos
        self.filename = pull_infos.local
        self.replacer = replacer
        self.temp_dir = temp_dir
        self.model: Model = None
        self.url: str = None
        self.settings = Settings(settings['host'], settings['secure'])

    def __load_fields(self):
        res = json.loads(requests.post(self.url + '/get_placeholders',
                                       json={'name': self.pull_infos.remote.filename}).text)
        res = [(i, {}) for i in res]
        self.model = Model(res, self.replacer, SYNTAX_KIT)

    def init(self):
        res = json.loads(requests.post(XlsxTemplator.url + '/load_templates', json=[
            {
                'bucket_name': self.pull_infos.remote.bucket,
                'template_name': self.pull_infos.remote.filename
            }
        ]).text)
        if len(res['success']) < 1:
            raise Exception(f'failed to import {self.filename}')
        self.__load_fields()
