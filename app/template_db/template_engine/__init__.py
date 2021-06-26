from __future__ import annotations

from typing import Dict, Type

from .base_template_engine import NEVER_PULLED, EngineDown, TemplateEngine
from .connectors import (DocxTemplator, HtmlTemplator, PptxTemplator,
                         XlsxTemplator)
from .constants import PREV_TOKEN
from .model_handler import from_strings_to_dict
from .ReplacerMiddleware import BaseReplacer, MultiAdaptater

DOCX = 'docx'
XLSX = 'xlsx'
PPTX = 'pptx'
HTML = 'html'

template_engines: Dict[str, Type[TemplateEngine]] = {
    DOCX: DocxTemplator,
    XLSX: XlsxTemplator,
    PPTX: PptxTemplator,
    HTML: HtmlTemplator,
}


# should check here if all template_engines are correct
