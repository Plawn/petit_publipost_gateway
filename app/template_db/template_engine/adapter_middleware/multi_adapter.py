from typing import List, Tuple
from .base_adapter import BaseAdapter

class MultiAdapter:
    def __init__(self, replacers: List[BaseAdapter]):
        self.replacers = replacers

    def from_doc(self, text: str) -> Tuple[str, dict]:
        res = {}
        for replacer in self.replacers:
            text, addtional_infos = replacer.from_doc(text)
            res.update(addtional_infos)
        return text, res

    def to_doc(self, text: str) -> str:
        for replacer in self.replacers:
            text = replacer.to_doc(text)
        return text
