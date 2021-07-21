from ..template_db import MultiAdapter
from .func_replacer import SpelFuncAdapter
from .list_replacer import SpelListAdapter

__all__ = ['SpelFuncAdapter', 'SpelListAdapter']

SPEL_TRANSFORMER = MultiAdapter([
    SpelFuncAdapter()
])
