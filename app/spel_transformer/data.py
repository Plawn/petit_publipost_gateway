from dataclasses import dataclass

@dataclass
class ReplacerData:
    doc_side: str
    other_side: str


to_replace_begin = ReplacerData('__', '(')
to_replace_end = ReplacerData('__', ')')
to_replace_sep = ReplacerData('_', ',')
to_replace_context = ReplacerData('_', '#')


TYPE_SYMBOL = 'type'