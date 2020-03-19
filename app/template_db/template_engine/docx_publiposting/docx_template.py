import copy
import json
import os
import re
from dataclasses import dataclass
from typing import Dict, Generator, List, Set, Union

import requests

from ...minio_creds import MinioCreds, MinioPath, PullInformations
from ..base_template_engine import TemplateEngine
from ...template_db import RenderOptions, ConfigOptions
from ..model_handler import Model, SyntaxtKit
from ..ReplacerMiddleware import MultiReplacer
from . import utils

TEMP_FOLDER = 'temp'
SYNTAX_KIT = SyntaxtKit('{{', '}}', '.')


@dataclass
class Settings:
    host: str
    secure: bool

# placeholder for now


def add_infos(_dict: dict) -> None:
    """Will add infos to the field on the fly
    """
    _dict.update({'traduction': ''})


class DocxTemplator(TemplateEngine):
    """
    """
    requires_env = []

    def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):

        self.pull_infos = pull_infos

        self.filename = pull_infos.local
        self.doc: docxTemplate = None
        self.model: Model = None
        self.replacer = replacer
        # easier for now
        self.settings = Settings(settings['host'], settings['secure'])
        self.temp_dir = temp_dir
        self.url: str = None
        self.init()

    @staticmethod
    def configure(env: ConfigOptions):
        settings = env.env
        creds: MinioCreds = env.minio
        url = f"http{'s' if settings['secure'] else ''}://{settings['host']}"
        data = {
            'host': creds.host,
            'access_key': creds.key,
            'pass_key': creds.password,
            'secure': creds.secure
        }
        res = json.loads(requests.post(url + '/configure',
                                       json=data).text)
        if res['error']:
            raise

    def __load_fields(self) -> None:
        res = json.loads(requests.post(self.url + '/get_placeholders',
                                       json={'name': self.pull_infos.remote.filename}).text)
        fields: List[str] = res
        cleaned = []
        for field in fields:
            field, additional_infos = self.replacer.from_doc(field)
            add_infos(additional_infos)
            cleaned.append((field.strip(), additional_infos))
        self.model = Model(cleaned, self.replacer, SYNTAX_KIT)

    def init(self) -> None:
        """Loads the document from the filename and inits it's values
        """
        self.url = f"http{'s' if self.settings.secure else ''}://{self.settings.host}"
        res = json.loads(requests.post(self.url + '/load_templates', json=[
            {
                'bucket_name': self.pull_infos.remote.bucket,
                'template_name': self.pull_infos.remote.filename
            }
        ]).text)
        if len(res['success']) < 1:
            raise Exception(f'failed to import {self.filename}')
        self.__load_fields()
