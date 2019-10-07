import copy
import re
from typing import Dict, Generator, Set, Union

from docxtpl import DocxTemplate as _docxTemplate

from ..ReplacerMiddleware import MultiReplacer
from . import utils
from ..base_template_engine import TemplateEngine
from .model_handler import Model
import json
import docx



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


class DocxTemplator(TemplateEngine):
    """
    """
    class_separator = '.'

    def __init__(self, filename: str, replacer: MultiReplacer):

        self.filename = filename
        self.doc: docxTemplate = None
        self.model: Model = None
        self.replacer = replacer
        self.init()

    def __repr__(self):
        return '<DocxTemplator>'


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
        return self.model.structure

    def apply_template(self, data: Dict[str, str]) -> docxTemplate:
        """
        Applies the data to the template and returns a `Template`
        """
        
        # kinda ugly i know
        # avoid re reading the file from the disk as we already cached it
        doc = copy.copy(self.doc.docx)
        renderer = docxTemplate()
        renderer.docx = doc
        # here we restore the content of the docx inside the new renderer
        
        data = self.model.merge(data)
        data = self.re_transform(data)
        
        renderer.render(data)
        return doc

    def re_transform(self, data: dict):
        return utils.change_keys(data, self.replacer.to_doc)


    