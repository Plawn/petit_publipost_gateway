import json
import os
from datetime import timedelta
from typing import Dict

import minio

from .template_engine.ReplacerMiddleware import (FuncReplacer,
                                                 MultiReplacer)
from .minio_creds import MinioCreds, MinioPath
from .templator import Templator

# should be env or config variable
TIME_DELTA = timedelta(days=1)
OUTPUT_DIRECTORY_TOKEN = 'output_bucket'

# placeholder for now
BASE_REPLACER = MultiReplacer(
    [
        FuncReplacer(),
    ]
)


class TemplateDB:
    """Holds everything to publipost all types of templates
    """

    def __init__(self, manifest: dict, temp_folder: str, minio_creds: MinioCreds):
        self.minio_creds = minio_creds
        self.minio_instance = minio.Minio(
            self.minio_creds.host, self.minio_creds.key, self.minio_creds.password)
        self.manifest: Dict[str, Dict[str, str]] = manifest
        self.temp_folder = temp_folder
        self.templators: Dict[str, Templator] = {}
        self.init()

    def init(self):
        self.__init_templators()
        for templator in self.templators.values():
            templator.pull_templates()

    def render_template(self, _type: str, name: str, data: Dict[str, str],  output: str):
        return self.templators[_type].render(name, data, output)

    def __init_templators(self):
        for bucket_name, settings in self.manifest.items():
            try:
                self.templators[settings['type']] = Templator(
                    self.minio_instance, self.temp_folder, MinioPath(bucket_name), MinioPath(settings[OUTPUT_DIRECTORY_TOKEN]), TIME_DELTA, BASE_REPLACER)
            except Exception as e:
                print(e)

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }
