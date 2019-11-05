from __future__ import annotations
from .base_template_engine import Template, TemplateEngine
from .docx_publiposting import DocxTemplator
from .xlsx_publisposting import XlsxTemplator
from .ReplacerMiddleware import MultiReplacer
from typing import Dict

DOCX = 'docx'
XLSX = 'xlsx'

template_engines: Dict[str, TemplateEngine] = {
    DOCX: DocxTemplator,
    XLSX: XlsxTemplator
}


# should check here if all template_engines are correct