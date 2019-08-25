from typing import Tuple


class BaseReplacer:
    def from_doc(self, text: str) -> Tuple[str, dict]:
        return text, {}

    def to_doc(self, text: str) -> Tuple[str, dict]:
        return text, {}


class ReplacerData:
    def __init__(self, doc_side: str, other_side: str):
        self.doc_side = doc_side
        self.other_side = other_side
