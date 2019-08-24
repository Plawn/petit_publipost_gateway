import json
from typing import Tuple, List, Dict
import copy
from collections.abc import Mapping


def merge_dict(d1: dict, d2: dict):
    """
    Modifies d1 in-place to contain values from d2.  If any value
    in d1 is a dictionary (or dict-like), *and* the corresponding
    value in d2 is also a dictionary, then merge them in-place.
    """
    for k, v2 in d2.items():
        v1 = d1.get(k)  # returns None if v1 has no value for this key
        if (isinstance(v1, Mapping) and isinstance(v2, Mapping)):
            merge_dict(v1, v2)
        else:
            d1[k] = v2


class Model:
    """To safely replace with jinja2 template
    """

    start = '{{'
    end = '}}'
    sep = '.'

    def __init__(self, strings: List[str]):
        self.structure = None
        self.load(strings)

    def load(self, strings_and_info: List[Tuple[str, Dict[str, str]]]):
        """
        Makes a model for a given list of string like :

        mission.document.name => {
            mission: {
                document: {
                    name: "mission.document.name"
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
                                'name': f'{self.start}{string}{self.end}', 'info': infos}
                        else:
                            del infos['use_prev']
                            d[item] = {
                                'name': f'{self.start}{string}{self.end}'}
                            last_node[last_prev].update(infos)
                previous.append(item)
        self.structure = res

    def merge(self, _input: dict):
        d1 = copy.deepcopy(self.structure)
        merge_dict(d1, _input)
        return d1

    def to_json(self):
        return self.structure


if __name__ == '__main__':
    with open('file.txt', 'r') as f:
        lines = f.readlines()

    with open('merge.json', 'r') as f:
        to_merge = json.load(f)

    model = Model(line.strip() for line in lines)
    print(to_merge)
    s = json.dumps(model.structure, indent=4)
    # print(s)
    # with open('res.json', 'w') as f:
    #     f.write(s)
    print(model.merge(to_merge))
    print(model.structure)
