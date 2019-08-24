from . import utils
from lxml import etree
import docx
import re
from typing import Dict, Set, Generator, Union
import copy
from .interfaces import Document


class TableData:
    def __init__(self, data:dict):
        
        self.title = data['settings']['title']
        self.rows = data['rows']


class Field:
    def __init__(self, name: str, trad: str):
        self.name = name
        self.trad = trad

    def to_json(self):
        return {
            'traduction': self.trad,
        }


class DocxTemplate:
    """
    """

    def __init__(self, filename: str, class_separator: str):

        self.filename = filename
        self.doc: Document = None
        self.fields: Dict[str, Field] = {}
        self.class_separator = class_separator
        self.init()

    def __load_fields(self):
        xml = etree.tostring(
            self.doc._element.body, encoding='unicode', pretty_print=False)
        fields: Set[str] = set(re.findall(r"\{{(.*?)\}}", xml, re.MULTILINE))
        res = {}
        for field in utils.xml_cleaner(fields):
            _type, value = field.split(self.class_separator)
            if _type in res:
                res[_type].append(Field(value, ''))
            else:
                res[_type] = [Field(value, '')]
        self.fields = res

    def init(self, filename=''):
        """Loads the document from the filename and inits it's values
        """
        self.doc = docx.Document(filename if filename != '' else self.filename)
        self.__load_fields()

    def to_json(self):
        return {
            name:
                {field.name: field.to_json() for field in fields}
            for name, fields in self.fields.items()
        }

    def apply_template(self, data: Dict[str, str], tables_data: Dict[str, Dict[str, str]]) -> docx.Document:
        doc = copy.copy(self.doc)
        utils.docx_replace(doc, data)
        utils.render_tables(doc, tables_data)
        return doc
