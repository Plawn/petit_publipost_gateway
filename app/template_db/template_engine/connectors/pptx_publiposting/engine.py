import json
from dataclasses import dataclass
from typing import *

import requests

from ....minio_creds import PullInformations
from ...base_template_engine import TemplateEngine
from ...model_handler import Model, SyntaxtKit
from ...ReplacerMiddleware import MultiReplacer

EXT = '.pptx'

SYNTAX_KIT = SyntaxtKit('{{', '}}')


@dataclass
class Settings:
    host: str
    secure: bool


class PptxTemplator(TemplateEngine):

    requires_env = (
        'host',
        'secure',
    )

    supported_extensions = {'pptx'}

    def __init__(self, filename:str, pull_infos: PullInformations, replacer: MultiReplacer):
        super().__init__(filename, pull_infos, replacer)
        PptxTemplator.registered_templates.append(self)

    def _load_fields(self, fields: List[str] = None) -> None:
        if fields is None:
            fields = self._get_placeholders()
        fields = [self.replacer.from_doc(i) for i in fields]
        self.model = Model(fields, self.replacer, SYNTAX_KIT)
