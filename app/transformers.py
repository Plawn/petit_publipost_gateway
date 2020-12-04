from dataclasses import dataclass
from typing import Tuple
from .template_db import BaseReplacer, MultiReplacer, PREV_TOKEN

import re

TYPE_SYMBOL = 'type'


@dataclass
class ReplacerData:
    doc_side: str
    other_side: str


to_replace_begin = ReplacerData('__', '(')
to_replace_end = ReplacerData('__', ')')
to_replace_sep = ReplacerData('_', ',')
to_replace_context = ReplacerData('_', '#')


class FuncReplacer(BaseReplacer):
    def from_doc(self, text: str):
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
                        raise Exception(
                            f'Invalid syntax while parsing: "{text}"'
                        )
                    params[j+1] = to_replace_context.other_side + params[j+1]
            params = (i for i in params if i != "")
            params = (
                f'"{i}"' if i[0] != to_replace_context.other_side else i for i in params
            )

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


# have to admit that, this is ugly


class ListReplacer(BaseReplacer):
    # I and T are used to delimit our stuff
    regex = re.compile(r'II(.*)II')

    def from_doc(self, text: str) -> str:
        res = self.regex.findall(text)
        if len(res) > 0:
            pre_node = text.split('II')[-1].strip()
            nodes = pre_node.split('.')
            text = re.sub(self.regex, '.', text).replace(
                '.'+pre_node, '').strip()
            text = '.'.join([nodes[0], text, '.'.join(nodes[1:])])
            infos = {
                'type': {
                    'list': res[0].split('T'),
                },
                PREV_TOKEN: True
            }
            return text, infos
        return text, {}

    def to_doc(self, text: str) -> str:
        return text


PHOENIX_NODE_TRANSFORMER = MultiReplacer([FuncReplacer()])


if __name__ == '__main__':
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
    for test_string in test_strings:
        test(test_string)
