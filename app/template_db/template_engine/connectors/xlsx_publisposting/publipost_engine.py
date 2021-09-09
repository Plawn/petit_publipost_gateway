from dataclasses import dataclass
from typing import List, Optional

from .....template_db.file_provider import PullInformations
from ...base_template_engine import TemplateEngine
from ...model_handler import Model, SyntaxtKit
from ...adapter_middleware import MultiAdapter

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

    supported_extensions = {'xlsx'}

    def __init__(self, filename: str,  pull_infos: PullInformations, replacer: MultiAdapter):
        super().__init__(filename, pull_infos, replacer)
        # should have a parent engine here instead
        XlsxTemplator.registered_templates.append(self)

    def _load_fields(self, fields: Optional[List[str]] = None) -> None:
        if fields is None:
            fields = self._get_placeholders()
        fields = [self.replacer.from_doc(i) for i in fields]
        self.model = Model(fields, self.replacer, SYNTAX_KIT)
