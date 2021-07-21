from __future__ import annotations

from typing import Dict, Type

from .base_template_engine import NEVER_PULLED, EngineDown, TemplateEngine
from .connectors import (DocxTemplator, HtmlTemplator, PptxTemplator,
                         XlsxTemplator, PDFTemplator)
from .constants import PREV_TOKEN
from .model_handler import from_strings_to_dict
from .adapter_middleware import BaseAdapter, MultiAdapter

DOCX = 'docx'
XLSX = 'xlsx'
PPTX = 'pptx'
HTML = 'html'
PDF = 'pdf'

template_engines: Dict[str, Type[TemplateEngine]] = {
    DOCX: DocxTemplator,
    XLSX: XlsxTemplator,
    PPTX: PptxTemplator,
    HTML: HtmlTemplator,
    PDF: PDFTemplator,
}

__all__ = [
    'template_engines',
    'BaseAdapter', 'MultiAdapter',
    'from_strings_to_dict',
    'NEVER_PULLED', 'EngineDown', 'PREV_TOKEN',
    'TemplateEngine'
]

# should check here if all template_engines are correct
