from __future__ import annotations
from .base_template_engine import TemplateEngine, NEVER_PULLED
from .docx_publiposting import DocxTemplator
from .xlsx_publisposting import XlsxTemplator
from .pptx_publiposting import PptxTemplator
from .ReplacerMiddleware import MultiReplacer
from typing import Dict
from .model_handler import from_strings_to_dict

DOCX = 'docx'
XLSX = 'xlsx'
PPTX = 'pptx'

template_engines: Dict[str, TemplateEngine] = {
    DOCX: DocxTemplator,
    XLSX: XlsxTemplator,
    PPTX: PptxTemplator,
}


# should check here if all template_engines are correct