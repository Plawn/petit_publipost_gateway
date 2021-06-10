from ..template_db import MultiReplacer
from .func_replacer import FuncReplacer
from .list_replacer import ListReplacer

__all__ = ['ListReplacer', 'FuncReplacer']

SPEL_TRANSFORMER = MultiReplacer([
    FuncReplacer()
])
