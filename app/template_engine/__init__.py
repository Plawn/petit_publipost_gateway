from __future__ import annotations
from .docx_publiposting import DocxTemplate
from .xlsx_publisposting import XlsxTemplate
from .ReplacerMiddleware import MultiReplacer
from typing import Dict

DOCX = 'docx'
XLSX = 'xlsx'


class TemplateEngine:
    def __init__(self, filename: str, replacer: MultiReplacer):
        pass

    def apply_template(self, data: Dict[str, str]) -> TemplateEngine:
        pass


template_engines: Dict[str, TemplateEngine] = {
    DOCX: DocxTemplate,
    XLSX: XlsxTemplate
}
