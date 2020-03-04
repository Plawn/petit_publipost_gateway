from typing import Tuple
from .BaseReplacer import BaseReplacer, ReplacerData

TYPE_SYMBOL = 'type'

to_replace_begin = ReplacerData('__', '("')
to_replace_end = ReplacerData('__', '")')
to_replace_sep = ReplacerData(',', '","')


class FuncReplacer(BaseReplacer):

    @staticmethod
    def from_doc(text: str) -> Tuple[str, dict]:
        """
        will transform __DDE__ -> ("DDE")
        will transoform mission.getStudentDoc__#student,REM__ -> mission.getStudentDoc(#student,"REM")
        """
        if to_replace_begin.doc_side in text:
            i = text.index(to_replace_begin.doc_side)
            params_string = text[i+2:-2]
            params = []
            for p in params_string.split(','):
                if p.startswith('#'):
                    params.append(p)
                else:
                    params.append(f'"{p}"')
            
            e = text[:i] + f'({",".join(params)})'
            return (e, {})
        return (text, {})

    @staticmethod
    def to_doc(text: str) -> str:
        if to_replace_begin.other_side in text:

            return (text
                    .replace(to_replace_begin.other_side, to_replace_begin.doc_side, 1)
                    .replace(to_replace_end.other_side, to_replace_end.doc_side, 1)
                    .replace(to_replace_sep.other_side, to_replace_sep.doc_side))
        return text
