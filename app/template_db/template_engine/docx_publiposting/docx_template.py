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

    def __init__(self, filename: str, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        DocxTemplator.registered_templates.append(self)
        super().__init__(filename, pull_infos, replacer, temp_dir, settings)

        self.model: Model = None
        # easier for now
        self.settings = Settings(settings['host'], settings['secure'])
        self.temp_dir = temp_dir

    def _load_fields(self, fields: List[str] = None) -> None:
        if fields is None:
            res = requests.post(DocxTemplator.url + '/get_placeholders',
                                json={'name': self.exposed_as}).json()
            fields: List[str] = res
        cleaned = []
        for field in fields:
            field, additional_infos = self.replacer.from_doc(field)
            add_infos(additional_infos)
            cleaned.append((field.strip(), additional_infos))
        self.model = Model(cleaned, self.replacer, SYNTAX_KIT)
