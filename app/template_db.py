import json
import os
from datetime import timedelta
from typing import Dict

import minio

from .better_publiposting import DocxTemplate
from .minio_creds import MinioCreds, MinioPath
from .templator import Templator
from .ReplacerMiddleware import FuncReplacer, MultiReplacer, ListReplacer


# should be env or config variable
TIME_DELTA = timedelta(days=1)

# Struct of manifest
# Minimal configuration :
# {
#     "<bucket_template_name>": {
#         "class_separator": "::",
#         "output_folder":"new-output",
#         "type":"mission"
#     },
#    ...
# }

# placeholder for now
BASE_REPLACER = MultiReplacer(
    [
        FuncReplacer(),
        ListReplacer()
    ]
)


class TemplateDB:
    """Holds everything to publipost all types of templates
    """
    def __init__(self, manifest_path: MinioPath, temp_folder: str, minio_creds: MinioCreds):
        self.minio_creds = minio_creds
        self.minio_instance = minio.Minio(
            self.minio_creds.host, self.minio_creds.key, self.minio_creds.password)
        self.manifest_path = manifest_path
        self.manifest: Dict[str, Dict[str, str]] = None
        self.get_manifest()
        self.temp_folder = temp_folder
        self.templators: Dict[str, Templator] = {}
        self.init()

    def init(self):
        self.get_manifest()
        self.__init_templators()
        for templator in self.templators.values():
            templator.pull_templates()

    def get_manifest(self):
        doc = self.minio_instance.get_object(self.manifest_path.bucket,
                                             self.manifest_path.filename)
        with open(os.path.join(self.manifest_path.filename), 'wb') as file_data:
            for d in doc.stream(32 * 1024):  # 32 kilobytes buffer
                file_data.write(d)
        with open(os.path.join(self.manifest_path.filename), 'r') as f:
            self.manifest = json.load(f)

    def render_template(self, _type: str, name: str, data: Dict[str, str],  output: str):
        return self.templators[_type].render(name, data, output)

    def __init_templators(self):
        # see manifest definition
        for bucket_name, settings in self.manifest.items():
            self.templators[settings['type']] = Templator(
                self.minio_instance, self.temp_folder, MinioPath(bucket_name), settings['output_folder'], timedelta, BASE_REPLACER)

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }
