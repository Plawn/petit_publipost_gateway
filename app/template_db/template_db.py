import traceback
import json
import os

from typing import Dict, Set

import minio

from .template_engine.ReplacerMiddleware import (FuncReplacer,
                                                 MultiReplacer)
from .template_engine import template_engines, TemplateEngine
from .minio_creds import MinioCreds, MinioPath
from .templator import Templator
from .utils import success_printer, error_printer
from datetime import timedelta
import subprocess

OUTPUT_DIRECTORY_TOKEN = 'output_bucket'

# placeholder for now
BASE_REPLACER = MultiReplacer([FuncReplacer])


class TemplateDB:
    """Holds everything to publipost all types of templates
    """

    def __init__(self, manifest: dict, engine_settings: dict, time_delta: timedelta, temp_folder: str, minio_creds: MinioCreds):
        self.minio_creds = minio_creds
        self.minio_instance = minio.Minio(
            self.minio_creds.host,
            access_key=self.minio_creds.key,
            secret_key=self.minio_creds.password,
            secure=self.minio_creds.secure
        )
        self.manifest: Dict[str, Dict[str, str]] = manifest
        self.temp_folder = temp_folder
        self.templators: Dict[str, Templator] = {}
        self.time_delta = time_delta
        self.engine_settings = engine_settings
        self.engines = None

    def full_init(self):
        self.__init_engines()
        self.init()

    def __init_engines(self):
        self.engines = self.__init_template_servers()
        self.__init_templators()

    def init(self):
        for templator in self.templators.values():
            templator.pull_templates()

    def render_template(self, _type: str, name: str, data: Dict[str, str],  output: str):
        return self.templators[_type].render(name, data, output)

    def __init_template_servers(self) -> None:
        available_engines: Dict[str, TemplateEngine] = {}
        for name, engine in template_engines.items():
            env = self.engine_settings[name]
            ok, missing = engine.check_env(env)
            # TODO : should make an object using a dataclass
            settings = {
                'env': env,
                'minio': self.minio_creds
            }
            if ok:
                try:
                    engine.configure(settings)
                    success_printer(f'Successfuly started "{name}" handler')
                    available_engines[name] = engine
                except Exception as e:
                    error_printer(
                        f'Failed to start server {engine}')
                    traceback.print_exc()
            else:
                error_printer(
                    f'Invalid env for handler "{name}" | missing keys {missing}')
        return available_engines

    def __init_templators(self):
        for bucket_name, settings in self.manifest.items():
            try:
                self.templators[settings['type']] = Templator(
                    self.minio_instance,
                    self.temp_folder,
                    MinioPath(bucket_name),
                    MinioPath(settings[OUTPUT_DIRECTORY_TOKEN]),
                    self.time_delta,
                    BASE_REPLACER,
                    self.engine_settings,
                    self.engines
                )
            except Exception as e:
                error_printer(e.__str__())
                traceback.print_exc()

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }
