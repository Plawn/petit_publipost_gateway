import copy
import json
from typing import Any, Dict, List, Tuple

from ..constants import FIELD_NAME_OPTION, INFO_FIELD_NAME, PREV_TOKEN
from ..adapter_middleware import MultiAdapter
from . import utils
from .utils import MissingPlaceholderFallbackAction


class SyntaxtKit:
    """Used with a model to make it able to reconstruct missing placeholders
    """
    __slots__ = ('start', 'end')

    def __init__(self, start: str, end: str):
        self.start = start
        self.end = end


StringAndInfos = List[Tuple[str, Dict[str, str]]]

BASE_KIT = SyntaxtKit('{{', '}}')


class Model:
    """To safely replace with jinja2 template
    """

    def __init__(self, strings_and_info: StringAndInfos, replacer: MultiAdapter, syntax_kit: SyntaxtKit):
        self.syntax: SyntaxtKit = syntax_kit
        self.structure: dict = None
        self.replacer = replacer
        self.fallback_action = MissingPlaceholderFallbackAction(
            FIELD_NAME_OPTION, self.replacer)

        # TODO:
        # should use a better abstraction here
        # phoenix fields
        self.fields = utils.prepare_names((i[0] for i in strings_and_info))
        self.load(strings_and_info, self.replacer)

    def load(self, strings_and_info: StringAndInfos, replacer: MultiAdapter):
        """
        Makes a model for a given list of string like :

        mission.document.name => {
            mission: {
                document: {
                    name: "{{mission.document.name}}"
                }
            }
        }
        This way we will merge the model with the input in order to ensure that placeholder are replaced with what we want
        """
        res = {}
        for string, infos in strings_and_info:
            l = string.split('.')
            previous = []
            end = len(l) - 1
            for i, item in enumerate(l):
                d = res
                last_node = None
                last_prev = None
                for prev in previous[:-1]:
                    d = d[prev]
                    last_node = d
                    last_prev = prev

                if len(previous) > 0:
                    d = d[previous[-1]]
                    last_prev = previous[-1]

                if item not in d:
                    if i != end:
                        d[item] = {}
                    else:
                        # this is kinda over-kill and not really used for the moment
                        # if this gets to complicated just remove the PREV_TOKEN, INFO_FIELD_NAME options
                        # but keep the FIELD_NAME_OPTION it's used and very important
                        # Strings and infos could le loaded from a json file located with the file
                        if not PREV_TOKEN in infos:
                            d[item] = {
                                FIELD_NAME_OPTION: f'{self.syntax.start}{replacer.to_doc(string)}{self.syntax.end}',
                                INFO_FIELD_NAME: infos
                            }
                        else:
                            del infos[PREV_TOKEN]
                            d[item] = {
                                FIELD_NAME_OPTION: f'{self.syntax.start}{replacer.to_doc(string)}{self.syntax.end}'
                            }
                            if INFO_FIELD_NAME not in last_node[last_prev]:
                                last_node[last_prev] = {INFO_FIELD_NAME: infos}
                            else:
                                last_node[last_prev][INFO_FIELD_NAME].update(
                                    infos)
                previous.append(item)
        self.structure = res

    def merge(self, _input: dict, ensure_keys: bool = True) -> Dict[str, Any]:
        """
        """
        d1 = copy.deepcopy(self.structure)
        utils.merge_dict(d1, _input)
        if ensure_keys:
            utils.ensure_keys(d1, self.fallback_action)
        return d1

    def to_json(self) -> Dict[str, Any]:
        return self.structure
