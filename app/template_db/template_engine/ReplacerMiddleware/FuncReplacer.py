from typing import Tuple
from .BaseReplacer import BaseReplacer, ReplacerData

TYPE_SYMBOL = 'type'

to_replace_begin = ReplacerData('__', '(')
to_replace_end = ReplacerData('__', ')')
to_replace_sep = ReplacerData('_', ',')
to_replace_context = ReplacerData('_', '#')


class FuncReplacer(BaseReplacer):

    @staticmethod
    def from_doc(text: str):
        """
        will transform __DDE__ -> ("DDE")
        will transoform mission.getStudentDoc___student,REM__ -> mission.getStudentDoc(#student,"REM")
        """
        if to_replace_begin.doc_side in text:
            i = text.index(to_replace_begin.doc_side)
            params_string = text[i+2:-2]
            params = params_string.split(to_replace_sep.doc_side)
            for j, value in enumerate(params):
                if value == '':
                    if params[j+1] == '':
                        raise Exception(f'Invalid syntax while parsing: "{text}"')
                    params[j+1] = to_replace_context.other_side + params[j+1]
            params = (i for i in params if i != "")
            params = (
                f'"{i}"' if i[0] != to_replace_context.other_side else i for i in params)

            return (text[:i] + f'({to_replace_sep.other_side.join(params)})', {})
        return (text, {})

    @staticmethod
    def to_doc(text: str) -> str:
        if to_replace_begin.other_side in text:
            return (text
                    .replace(to_replace_begin.other_side, to_replace_begin.doc_side, 1)
                    .replace(to_replace_end.other_side, to_replace_end.doc_side, 1)
                    .replace(to_replace_context.other_side, to_replace_context.doc_side)
                    .replace('"', '')
                    .replace(to_replace_sep.other_side, to_replace_sep.doc_side)
                    )
        return text

def test(test_string: str):
    res = FuncReplacer.from_doc(test_string)[0]
    print(res)

    verify = FuncReplacer.to_doc(res)
    print(verify)
    print(verify == test_string)


test_strings = [
    'mission.getStudentDoc___student_REM__',
    'mission.getStudentDoc__REM__'
]

if __name__ == '__main__':
    for test_string in test_strings:
        test(test_string)
