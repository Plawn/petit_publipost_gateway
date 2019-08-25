import copy
import json
from typing import Dict, List, Tuple

from ..constants import FIELD_NAME_OPTION, INFO_FIELD_NAME
from ..ReplacerMiddleware import MultiReplacer
from . import utils
from .utils import ThisFallbackAction


def bench(log_file: str) -> callable:
    import time

    def _bench(func: callable) -> callable:
        def f(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            duration = time.time() - start
            with open(log_file, 'a') as f:
                f.write(f'{duration}\n')
            return res
        return f
    return _bench


class Model:
    """To safely replace with jinja2 template
    """

    start = '{{'
    end = '}}'
    sep = '.'

    def __init__(self, strings: List[str], replacer: MultiReplacer):
        self.structure = None
        self.replacer = replacer
        self.fallback_action = ThisFallbackAction(
            FIELD_NAME_OPTION, self.replacer)

        self.load(strings, self.replacer)

    def load(self, strings_and_info: List[Tuple[str, Dict[str, str]]], replacer: MultiReplacer):
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
            l = string.split(self.sep)
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
                        if not 'use_prev' in infos:
                            d[item] = {
                                FIELD_NAME_OPTION: f'{self.start}{replacer.to_doc(string)[0]}{self.end}',
                                INFO_FIELD_NAME: infos}
                        else:
                            del infos['use_prev']
                            d[item] = {
                                FIELD_NAME_OPTION: f'{self.start}{replacer.to_doc(string)[0]}{self.end}'}
                            if INFO_FIELD_NAME not in last_node[last_prev]:
                                last_node[last_prev] = {INFO_FIELD_NAME: infos}
                            else:
                                last_node[last_prev][INFO_FIELD_NAME].update(
                                    infos)
                previous.append(item)
        self.structure = res

    # @bench('without.csv')

    def merge(self, _input: dict, ensure_keys=True) -> dict:
        """
        """
        d1 = copy.deepcopy(self.structure)
        utils.merge_dict(d1, _input)
        if ensure_keys:
            utils.ensure_keys(d1, self.fallback_action)
        return d1

    def to_json(self) -> dict:
        return self.structure
