import copy
import re
from typing import Dict, Generator, Set, Union

import docx
from docxtpl import DocxTemplate as _docxTemplate
from lxml import etree

from .ReplacerMiddleware import MultiReplacer
from . import utils
from .model_handler import Model
import json

def change_keys(obj: dict, convert: callable)->dict:
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


class docxTemplate(_docxTemplate):
    """Proxying the real class in order to be able to copy.copy the template docx file
    """

    def __init__(self, filename: str = ''):
        self.crc_to_new_media = {}
        self.crc_to_new_embedded = {}
        self.pic_to_replace = {}
        self.pic_map = {}
        if filename != '':
            self.docx = docx.Document(filename)
        else:
            self.docx = None


# placeholder for now
def add_infos(_dict: dict) -> None:
    """Will add infos to the field on the fly
    """
    _dict.update({'traduction': ''})


class DocxTemplate:
    """
    """
    class_separator = '.'

    def __init__(self, filename: str, replacer: MultiReplacer):

        self.filename = filename
        self.doc: docxTemplate = None
        self.model: Model = None
        self.replacer = replacer
        self.init()

    def __load_fields(self) -> None:
        fields: Set[str] = set(re.findall(
            r"\{{(.*?)\}}", self.doc.get_xml(), re.MULTILINE))
        cleaned = list()
        for field in utils.xml_cleaner(fields):
            field, additional_infos = self.replacer.from_doc(field)
            add_infos(additional_infos)
            cleaned.append((field.strip(), additional_infos))
        self.model = Model(cleaned, self.replacer)

    def init(self, filename='') -> None:
        """Loads the document from the filename and inits it's values
        """
        self.doc = docxTemplate(filename if filename != '' else self.filename)
        self.__load_fields()

    def to_json(self) -> dict:
        # return {
        #     name:
        #         {field.name: field.to_json() for field in fields}
        #     for name, fields in self.fields.items()
        # }
        return self.model.structure

    def apply_template(self, data: Dict[str, str]) -> docxTemplate:
        # kinda ugly i know
        doc = copy.copy(self.doc.docx)
        renderer = docxTemplate()
        renderer.docx = doc
        
        data = self.model.merge(data)
        data = self.re_transform(data)
        
        renderer.render(data)
        return doc

    def re_transform(self, data: dict):
        return change_keys(data, lambda x: self.replacer.to_doc(x)[0])