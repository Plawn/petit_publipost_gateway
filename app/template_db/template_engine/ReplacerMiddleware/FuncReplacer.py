from typing import Tuple
from .BaseReplacer import BaseReplacer, ReplacerData
# from ..better_publiposting.model_handler import INFO_FIELD_NAME

TYPE_SYMBOL = 'type'

to_replace_begin = ReplacerData('__', '("')
to_replace_end = ReplacerData('__', '")')
to_replace_sep = ReplacerData(',', '","')


class FuncReplacer(BaseReplacer):

    @staticmethod
    def from_doc(text: str) -> Tuple[str, dict]:
        if to_replace_begin.doc_side in text:
            return (text
                    .replace(to_replace_begin.doc_side, to_replace_begin.other_side, 1)
                    .replace(to_replace_end.doc_side, to_replace_end.other_side, 1)
                    .replace(to_replace_sep.doc_side, to_replace_sep.other_side)), {TYPE_SYMBOL: {'function': {'args': ['String']}}}
            # String for now as we only have one argument for one function
            # -> should make it better
        return text, {}

    @staticmethod
    def to_doc(text: str) -> str:
        if to_replace_begin.other_side in text:

            return (text
                    .replace(to_replace_begin.other_side, to_replace_begin.doc_side, 1)
                    .replace(to_replace_end.other_side, to_replace_end.doc_side, 1)
                    .replace(to_replace_sep.other_side, to_replace_sep.doc_side))
        return text
