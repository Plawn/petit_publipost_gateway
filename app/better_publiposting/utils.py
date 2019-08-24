from typing import Dict, List, Generator, Iterable


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