from . import utils
from lxml import etree
import docx
from docxtpl import DocxTemplate as _docxTemplate
import re
from typing import Dict, Set, Generator, Union
import copy
from .model_handler import Model
from ..ReplacerMiddleware import MultiReplacer

#     def __getattr__(self, name):
# return getattr(self.docx, name)


def change_keys(obj, convert):
    """
    Recursively goes through the dictionary obj and replaces keys with the convert function.
    """
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)[0]] = change_keys(v, convert)
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
def add_infos(_dict: dict):
    _dict.update({'tradution': ''})


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

    def __load_fields(self):
        # xml = etree.tostring(
        #     self.doc.get_xml() , encoding='unicode', pretty_print=False)
        fields: Set[str] = set(re.findall(
            r"\{{(.*?)\}}", self.doc.get_xml(), re.MULTILINE))
        cleaned = list()
        for field in utils.xml_cleaner(fields):
            field, additional_infos = self.replacer.from_doc(field)
            add_infos(additional_infos)
            cleaned.append((field.strip(), additional_infos))
        self.model = Model(cleaned)

    def init(self, filename=''):
        """Loads the document from the filename and inits it's values
        """
        self.doc = docxTemplate(filename if filename != '' else self.filename)
        self.__load_fields()

    def to_json(self):
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
        data = self.re_transform(data)
        merged = self.model.merge(data)
        renderer.render(merged)
        return doc

    def re_transform(self, data: dict):
        return change_keys(data, self.replacer.to_doc)
