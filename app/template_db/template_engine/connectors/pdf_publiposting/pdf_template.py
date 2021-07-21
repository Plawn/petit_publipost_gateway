from dataclasses import dataclass
from typing import List, Optional

from ....minio_creds import PullInformations
from ...base_template_engine import TemplateEngine
from ...model_handler import Model, SyntaxtKit
from ...adapter_middleware import MultiAdapter

EXT = '.pdf'

SYNTAX_KIT = SyntaxtKit('{{', '}}')


@dataclass
class Settings:
    host: str
    secure: bool


class PDFTemplator(TemplateEngine):

    requires_env = (
        'host',
        'secure',
    )

    supported_extensions = {'xlsx'}

    def __init__(self, filename: str,  pull_infos: PullInformations, replacer: MultiAdapter):
        super().__init__(filename, pull_infos, replacer)
        PDFTemplator.registered_templates.append(self)

    def _load_fields(self, fields: Optional[List[str]] = None) -> None:
        if fields is None:
            fields = self._get_placeholders()
        fields = [self.replacer.from_doc(i) for i in fields]
        self.model = Model(fields, self.replacer, SYNTAX_KIT)
