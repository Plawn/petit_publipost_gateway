from ..base_template_engine import TemplateEngine
from ..model_handler import Model, SyntaxtKit
import requests
from ...minio_creds import PullInformations, MinioPath
from ..ReplacerMiddleware import BaseReplacer
import json

EXT = '.xlsx'

SYNTAX_KIT = SyntaxtKit('${', '}', '.')


class XlsxTemplator(TemplateEngine):

    requires_env = (
        'host',
        'secure',
    )

    def __init__(self, pull_infos: PullInformations, replacer: BaseReplacer, temp_dir: str, settings: dict):

        self.pull_infos = pull_infos
        self.filename = pull_infos.local
        self.replacer = replacer
        self.temp_dir = temp_dir
        self.settings = settings
        self.url: str = None
        self.model = None
        self._init()

    def apply_template(self, data):
        raise Exception('not available on this type')

    def render_to(self, data: dict, path: MinioPath) -> None:
        data = {'data': data, 'template_name': self.pull_infos.remote.filename,
                'output_bucket': path.bucket, 'output_name': path.filename}
        res = requests.post(self.url + '/publipost', json=data)
        error = json.loads(res.text)
        if error['error']:
            raise Exception('An error has occured')

    def __load_fields(self):
        res = json.loads(requests.post(self.url + '/get_placeholders',
                                       json={'name': self.pull_infos.remote.filename}).text)
        res = [(i, {}) for i in res]
        self.model = Model(res, self.replacer, SYNTAX_KIT)

    def _init(self):
        self.url = f"http{'s' if self.settings['secure'] else ''}://{self.settings['host']}"
        res = json.loads(requests.post(self.url + '/load_templates', json=[
            {'bucket_name': self.pull_infos.remote.bucket,
                'template_name': self.pull_infos.remote.filename}
        ]).text)
        if len(res['success']) < 1:
            raise Exception(f'failed to import {self.filename}')
        self.__load_fields()

    def to_json(self):
        return self.model.to_json()
