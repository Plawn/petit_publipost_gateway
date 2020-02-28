from .BaseReplacer import BaseReplacer
from ..constants import PREV_TOKEN
import re

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
            infos = {'type': {
                'list': res[0].split('T')},
                PREV_TOKEN: True
            }
            return text, infos
        return text, {}

    def to_doc(self, text: str) -> str:
        return text
