from typing import Generator, Iterable


def xml_cleaner(words: Iterable) -> Generator[str, None, None]:
    """Enlève les tags XML résiduels pour une liste de mots"""
    for word in words:
        chars = list()
        in_tag = False
        for char in word:
            if char == "<":
                in_tag = True
            elif char == ">":
                in_tag = False
            elif not in_tag:
                chars.append(char)
        yield ''.join(chars)


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