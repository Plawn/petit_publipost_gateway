from typing import Tuple
from dataclasses import dataclass

class BaseReplacer:
    def from_doc(self, text: str) -> Tuple[str, dict]:
        return text, {}

    def to_doc(self, text: str) -> str:
        return text

@dataclass
class ReplacerData:
    doc_side:str
    other_side:str
