from dataclasses import dataclass
from typing import List, Optional

from ....minio_creds import PullInformations
from ...base_template_engine import TemplateEngine
from ...model_handler import Model, SyntaxtKit
from ...ReplacerMiddleware import MultiReplacer

SYNTAX_KIT = SyntaxtKit('{{', '}}')


@dataclass
class Settings:
    host: str
    secure: bool


def add_infos(_dict: dict) -> None:
    """Will add infos to the field on the fly
    """
    _dict.update({'traduction': ''})


class DocxTemplator(TemplateEngine):
    """
    """
    requires_env = []
    supported_extensions = {'docx'}

    def __init__(self, filename:str, pull_infos: PullInformations, replacer: MultiReplacer):
        DocxTemplator.registered_templates.append(self)
        super().__init__(filename, pull_infos, replacer)

    def _load_fields(self, fields: Optional[List[str]] = None) -> None:
        if fields is None:
            fields: List[str] = self._get_placeholders()
        cleaned = []
        for field in fields:
            field, additional_infos = self.replacer.from_doc(field)
            add_infos(additional_infos)
            cleaned.append((field.strip(), additional_infos))
        self.model = Model(cleaned, self.replacer, SYNTAX_KIT)
