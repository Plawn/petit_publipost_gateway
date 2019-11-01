from ..base_template_engine import TemplateEngine
from ..model_handler import Model, SyntaxtKit
import requests
from ...minio_creds import PullInformations, MinioPath
import json

EXT = '.xlsx'

SYNTAX_KIT = SyntaxtKit('${', '}', '.')

class XlsxTemplator(TemplateEngine):
    def __init__(self, pull_infos: PullInformations, replacer, temp_dir, settings):

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

    def render_to(self, data: dict, path: MinioPath):
        data = {'data': data, 'template_name': self.pull_infos.remote.filename,
                'output_bucket': path.bucket, 'output_name': path.filename}
        res = requests.post(self.url + '/publipost', json=data)
        return json.loads(res.text)

    def __load_fields(self):
        res = json.loads(requests.post(self.url + '/get_placeholders',
                                       json={'name': self.pull_infos.remote.filename}).text)
        res = [(i, {}) for i in res]
        self.model = Model(res, self.replacer, SYNTAX_KIT)

    def _init(self):
        self.url = f"http{'s' if self.settings['secure'] else ''}://{self.settings['host']}:{self.settings['port']}"
        res = json.loads(requests.post(self.url + '/load_templates', json=[
            {'bucket_name': self.pull_infos.remote.bucket,
                'template_name': self.pull_infos.remote.filename}
        ]).text)
        if len(res['success']) < 1:
            raise Exception(f'failed to import {self.filename}')
        self.__load_fields()

    def to_json(self):
        return self.model.to_json()
