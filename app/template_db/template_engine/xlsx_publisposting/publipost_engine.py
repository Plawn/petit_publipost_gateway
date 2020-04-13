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

    def __init__(self, filename:str, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        super().__init__(filename, pull_infos, replacer, temp_dir, settings)
        XlsxTemplator.registered_templates.append(self)

        self.temp_dir = temp_dir
        self.model: Model = None
        self.url: str = None
        self.settings = Settings(settings['host'], settings['secure'])

    def __load_fields(self):
        res = requests.post(XlsxTemplator.url + '/get_placeholders',
                                       json={'name': self.pull_infos.remote.filename}).json()
        res = [(i, {}) for i in res]
        self.model = Model(res, self.replacer, SYNTAX_KIT)

    def init(self):
        if not self.is_up():
            raise Exception('Engine down')
        res = requests.post(XlsxTemplator.url + '/load_templates', json=[
            {
                'bucket_name': self.pull_infos.remote.bucket,
                'template_name': self.pull_infos.remote.filename
            }
        ]).json()
        if len(res['success']) < 1:
            raise Exception(f'failed to import {self.filename}')
        self.__load_fields()
        super().init()
