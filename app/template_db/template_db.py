import traceback
import json
import os
import logging
from typing import Dict, Set, List

import minio
from .data_objects import RenderOptions, ConfigOptions
from .template_engine.ReplacerMiddleware import (FuncReplacer,
                                                 MultiReplacer)
from .template_engine import template_engines, TemplateEngine
from .minio_creds import MinioCreds, MinioPath
from .template_engine.model_handler.utils import from_strings_to_dict
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
        # doing this to check if the minio instance is correct
        self.minio_instance.list_buckets()
        self.manifest: Dict[str, Dict[str, str]] = manifest
        self.temp_folder = temp_folder
        self.templators: Dict[str, Templator] = {}
        self.time_delta = time_delta
        self.engine_settings = engine_settings
        self.engines: Dict[str, TemplateEngine] = None
        self.loading = True

    def full_init(self):
        self.loading = True
        self.__init_engines()
        self.load_templates()
        self.loading = False

    def __init_engines(self):
        self.engines = self.__init_template_servers()
        self.__init_templators()

    def load_templates(self):
        for templator in self.templators.values():
            templator.pull_templates()

    def render_template(self, _type: str, name: str, data: Dict[str, str],  output: str, options: RenderOptions):
        # with this we can avoid transforming the data if we want to
        if options.transform_data:
            data: Dict[str, object] = from_strings_to_dict(data)
        return self.templators[_type].render(name, data, output, options)

    def __init_template_servers(self) -> None:
        available_engines: Dict[str, TemplateEngine] = {}
        for name, engine in template_engines.items():
            env = self.engine_settings[name]
            ok, missing = engine.check_env(env)
            settings = ConfigOptions(env, self.minio_creds)
            if ok:
                try:
                    engine.register(settings, name)
                    logging.info(f'Successfuly registered "{name}" handler')
                except Exception as e:
                    error_printer(
                        f'Failed to register server {engine}')
                    logging.error(traceback.format_exc())
            else:
                logging.error(f'Invalid env for handler "{name}" | missing keys {missing}')
            available_engines[name] = engine
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
