from .BaseReplacer import BaseReplacer
import re

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
            return text, {'type':
                          {'list': res[0].split('T')},
                          'use_prev': True}
        return text, {}

    def to_doc(self, text: str) -> str:
        return text, {}
