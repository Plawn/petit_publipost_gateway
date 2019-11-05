import copy
import json
import re
from typing import Dict, Generator, Set, Union
import os
import docx
from docxtpl import DocxTemplate as _docxTemplate
import uuid
from ..base_template_engine import TemplateEngine
from ..ReplacerMiddleware import MultiReplacer
from . import utils
from ..model_handler import Model, SyntaxtKit
from ...minio_creds import PullInformations, MinioPath

TEMP_FOLDER = 'temp'
SYNTAX_KIT = SyntaxtKit('{{', '}}', '.')


class docxTemplate(_docxTemplate):
    """Proxying the real class in order to be able to copy.copy the template docx file
    """

    def __init__(self, filename: str = '', document=None):
        self.crc_to_new_media = {}
        self.crc_to_new_embedded = {}
        self.pic_to_replace = {}
        self.pic_map = {}
        self.docx = document if document is not None else docx.Document(
            filename)


# placeholder for now
def add_infos(_dict: dict) -> None:
    """Will add infos to the field on the fly
    """
    _dict.update({'traduction': ''})


class DocxTemplator(TemplateEngine):
    """
    """
    requires_env = []

    def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):

        self.pull_infos = pull_infos

        self.filename = pull_infos.local
        self.doc: docxTemplate = None
        self.model: Model = None
        self.replacer = replacer
        # easier for now
        self.temp_dir = temp_dir
        self.init()

    def __load_fields(self) -> None:
        fields: Set[str] = set(re.findall(
            r"\{{(.*?)\}}", self.doc.get_xml(), re.MULTILINE))
        cleaned = list()
        for field in utils.xml_cleaner(fields):
            field, additional_infos = self.replacer.from_doc(field)
            add_infos(additional_infos)
            cleaned.append((field.strip(), additional_infos))
        self.model = Model(cleaned, self.replacer, SYNTAX_KIT)

    def init(self) -> None:
        """Loads the document from the filename and inits it's values
        """
        # pulling template from the bucket
        doc = self.pull_infos.minio.get_object(
            self.pull_infos.remote.bucket,
            self.pull_infos.remote.filename)
        print('writing to ', self.filename)
        with open(self.filename, 'wb') as file_data:
            for d in doc.stream(32*1024):
                file_data.write(d)
        self.doc = docxTemplate(self.filename)
        self.__load_fields()

    def to_json(self) -> dict:
        return self.model.structure

    def apply_template(self, data: Dict[str, str]) -> docxTemplate:
        """
        Applies the data to the template and returns a `Template`
        """

        # kinda ugly i know but
        # we can avoid re reading the file from the disk as we already cached it
        doc = copy.copy(self.doc.docx)
        renderer = docxTemplate(document=doc)
        # here we restore the content of the docx inside the new renderer
        renderer.render(data)
        return doc

    def render_to(self, data: Dict[str, str], path: MinioPath) -> None:
        save_path = os.path.join(self.temp_dir, str(uuid.uuid4()))
        doc = self.apply_template(data)
        doc.save(save_path)

        try:
            self.pull_infos.minio.fput_object(
                path.bucket, path.filename, save_path)
        except:
            raise Exception('Failed to upload file')
        finally:
            os.remove(save_path)
