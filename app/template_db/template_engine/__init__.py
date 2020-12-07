from __future__ import annotations

from typing import Dict, Type

from .base_template_engine import NEVER_PULLED, TemplateEngine, EngineDown
from .connectors import DocxTemplator, PptxTemplator, XlsxTemplator
from .constants import PREV_TOKEN
from .model_handler import from_strings_to_dict
from .ReplacerMiddleware import BaseReplacer, MultiReplacer

DOCX = 'docx'
XLSX = 'xlsx'
PPTX = 'pptx'

template_engines: Dict[str, Type[TemplateEngine]] = {
    DOCX: DocxTemplator,
    XLSX: XlsxTemplator,
    PPTX: PptxTemplator,
}


# should check here if all template_engines are correct
