from collections.abc import Mapping
from typing import List, Dict, Tuple, Set, Iterable

from ..ReplacerMiddleware import MultiReplacer


class FallbackAction:
    def __init__(self, field_name: str, replacer: MultiReplacer):
        self.field_name = field_name

    def prepare_fallback(self, _dict: dict, key: str) -> None:
        pass


# ugly name i know
class MissingPlaceholderFallbackAction(FallbackAction):
    def __init__(self, field_name: str, replacer: MultiReplacer):
        super().__init__(field_name, replacer)
        self.replacer = replacer

    def prepare_fallback(self, _dict: dict, key: str) -> None:
        """
        Prevents error by recreating the missing keys in the input data, 
        we won't have missing fields so we can avoid errors and let the placeholder in place
        """
        new_key = self.replacer.to_doc(key)
        _dict[new_key] = _dict[key][self.field_name]
        if key != new_key:
            del _dict[key]


def merge_dict(d1: dict, d2: dict):
    """
    Modifies d1 in-place to contain values from d2.  If any value
    in d1 is a dictionary (or dict-like), *and* the corresponding
    value in d2 is also a dictionary, then merge them in-place.
    """
    for key, v2 in d2.items():
        v1 = d1.get(key)  # returns None if v1 has no value for this key
        if (isinstance(v1, Mapping) and isinstance(v2, Mapping)):
            merge_dict(v1, v2)
        else:
            d1[key] = v2


def ensure_keys(d: dict, fallback_action: FallbackAction):
    for key, item in d.items():
        if isinstance(item, Mapping) and fallback_action.field_name in item:
            fallback_action.prepare_fallback(d, key)
        else:
            if isinstance(item, Mapping):
                ensure_keys(item, fallback_action)


def change_keys(obj: dict, convert: callable) -> dict:
    """
    Recursively goes through the dictionary obj and replaces keys with the convert function.
    """
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = change_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(change_keys(v, convert) for v in obj)
    else:
        return obj
    return new


def prepare_name(string: str) -> Tuple[str, str]:
    top_level, *other_level = string.split('.')
    return top_level, '.'.join(other_level)


def prepare_names(strings: Iterable[str]) -> Dict[str, List[str]]:
    d: Dict[str, Set[str]] = {}
    for string in strings:
        top_level, rest = prepare_name(string)
        if top_level in d:
            d[top_level].add(rest)
        else:
            d[top_level] = {rest}
    return {i: list(j) for i, j in d.items()}


def from_strings_to_dict(data: Dict[str, str]):
    """
    Makes a model for a given list of string like :

    "mission.document.name": "test" => {
        mission: {
            document: {
                name: "test"
            }
        }
    }
    """
    res = {}
    for key, value in data.items():
        l = key.split('.')
        previous = []
        end = len(l) - 1
        for i, item in enumerate(l):
            d = res
            last_node = None
            for prev in previous[:-1]:
                d = d[prev]
                last_node = d

            if len(previous) > 0:
                d = d[previous[-1]]

            if item not in d:
                if i != end:
                    d[item] = {}
                else:
                    d[item] = value
            previous.append(item)
    return res
