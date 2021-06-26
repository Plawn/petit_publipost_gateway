from ..template_db import MultiAdaptater
from .func_replacer import SpelFuncAdapter
from .list_replacer import SpelListAdapter

__all__ = ['ListReplacer', 'FuncReplacer']

SPEL_TRANSFORMER = MultiAdaptater([
    SpelFuncAdapter()
])
