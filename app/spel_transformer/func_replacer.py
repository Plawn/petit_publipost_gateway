from typing import Tuple

from ..template_db import BaseAdapter
from .data import (to_replace_begin, to_replace_context, to_replace_end,
                   to_replace_sep)


def find_end(s: str) -> int:
    i = 0
    for i, char in enumerate(s):
        if char == '_':
            if i < len(s) - 3:
                if s[i + 1] == '_' and s[i + 2] == '.':
                    return i
            elif i < len(s) - 2:
                if s[i + 1] == '_':
                    return i
    return i


class SpelFuncAdapter(BaseAdapter):
    def from_doc(self, text: str) -> Tuple[str, dict]:
        """
        will transform __DDE__ -> ("DDE")
        will transform mission.getStudentDoc___student_REM__ -> mission.getStudentDoc(#student,"REM")
        """
        # TODO: +1 and +2 should be explained
        if to_replace_begin.doc_side in text:
            i = text.index(to_replace_begin.doc_side)
            end_of_func = i + 2 + find_end(text[i + 2:])
            params_string = text[i + 2:end_of_func]
            params = params_string.split(to_replace_sep.doc_side)

            for j, value in enumerate(params):
                if value == '':
                    if j + 1 < len(params):
                        print(params, params_string, len(params), j)
                        if params[j + 1] == '' and j != len(params) - 2:
                            raise Exception(
                                f'Invalid syntax while parsing: "{text}"'
                            )
                        if params[j + 1] != '':
                            params[j + 1] = to_replace_context.other_side + \
                                params[j + 1]
            params = (i for i in params if i != "")
            params = (
                f'"{i}"' if i[0] != to_replace_context.other_side else i for i in params
            )

            return (
                text[:i] + f'({to_replace_sep.other_side.join(params)})' +
                self.from_doc(text[end_of_func + 2:])[0],
                {}
            )
        return (text, {})

    def to_doc(self, text: str) -> str:
        if to_replace_begin.other_side in text:
            while '(' in text:
                text = (text.replace(to_replace_begin.other_side, to_replace_begin.doc_side, 1)
                        .replace(to_replace_end.other_side, to_replace_end.doc_side, 1)
                        .replace(to_replace_context.other_side, to_replace_context.doc_side)
                        .replace('"', '')
                        .replace(to_replace_sep.other_side, to_replace_sep.doc_side)
                        )
            return text
        return text
