from dataclasses import dataclass
from typing import List, Optional

import requests

from ....minio_creds import PullInformations
from ...base_template_engine import TemplateEngine
from ...model_handler import Model, SyntaxtKit
from ...ReplacerMiddleware import MultiReplacer

EXT = '.xlsx'

SYNTAX_KIT = SyntaxtKit('{{', '}}')


@dataclass
class Settings:
    host: str
    secure: bool


class XlsxTemplator(TemplateEngine):

    requires_env = (
        'host',
        'secure',
    )

    def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer):
        super().__init__(pull_infos, replacer)
        XlsxTemplator.registered_templates.append(self)

    def _load_fields(self, fields: Optional[List[str]] = None) -> None:
        if fields is None:
            fields = self._get_placeholders()
        fields = [self.replacer.from_doc(i) for i in fields]
        self.model = Model(fields, self.replacer, SYNTAX_KIT)
