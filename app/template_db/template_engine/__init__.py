from __future__ import annotations
from .base_template_engine import TemplateEngine, NEVER_PULLED
from .connectors import DocxTemplator, XlsxTemplator, PptxTemplator
from .ReplacerMiddleware import MultiReplacer, BaseReplacer
from typing import Dict
from .model_handler import from_strings_to_dict
from .constants import PREV_TOKEN

DOCX = 'docx'
XLSX = 'xlsx'
PPTX = 'pptx'

template_engines: Dict[str, TemplateEngine] = {
    DOCX: DocxTemplator,
    XLSX: XlsxTemplator,
    PPTX: PptxTemplator,
}


# should check here if all template_engines are correct
