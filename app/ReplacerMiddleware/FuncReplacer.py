from .BaseReplacer import BaseReplacer, ReplacerData

class FuncReplacer(BaseReplacer):
    to_replace_begin = ReplacerData('__', '("')
    to_replace_end = ReplacerData('__', '")')
    to_replace_sep = ReplacerData(',', '","')

    def from_doc(self, text: str) -> str:
        if self.to_replace_begin.doc_side in text:
            return (text
                    .replace(self.to_replace_begin.doc_side, self.to_replace_begin.other_side, 1)
                    .replace(self.to_replace_end.doc_side, self.to_replace_end.other_side, 1)
                    .replace(self.to_replace_sep.doc_side, self.to_replace_sep.other_side)), {'function': ['str']}
        return text, {}

    #
    def to_doc(self, text: str) -> str:
        if self.to_replace_begin.other_side in text:
            return (text
                    .replace(self.to_replace_begin.other_side, self.to_replace_begin.doc_side, 1)
                    .replace(self.to_replace_end.other_side, self.to_replace_end.doc_side, 1)
                    .replace(self.to_replace_sep.other_side, self.to_replace_sep.doc_side)), {}
        return text, {}