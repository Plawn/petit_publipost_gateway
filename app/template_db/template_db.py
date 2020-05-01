import json
import logging
import os
import subprocess
import threading
import traceback
from datetime import timedelta
from typing import Dict, List, Set

import minio

from .data_objects import ConfigOptions, RenderOptions
from .minio_creds import MinioCreds, MinioPath
from .template_engine import TemplateEngine, template_engines
from .template_engine.model_handler.utils import from_strings_to_dict
from .template_engine.ReplacerMiddleware import FuncReplacer, MultiReplacer
from .templator import Templator

OUTPUT_DIRECTORY_TOKEN = 'output_bucket'

# placeholder for now


def check_minio_instance(minio_instance: minio.Minio):
    try:
        res = minio_instance.list_buckets()
        return True
    except:
        return False


class TemplateDB:
    """Holds everything to publipost all types of templates
    """

    def __init__(self, manifest: dict, engine_settings: dict, time_delta: timedelta, temp_folder: str,
                 minio_creds: MinioCreds, node_transformer: MultiReplacer, cache_validation_interval=-1):
        self.minio_creds = minio_creds
        self.minio_instance = minio.Minio(
            self.minio_creds.host,
            access_key=self.minio_creds.key,
            secret_key=self.minio_creds.password,
            secure=self.minio_creds.secure
        )
        # doing this to check if the minio instance is correct
        if not check_minio_instance(self.minio_instance):
            raise Exception('Invalid minio creds')
        self.manifest: Dict[str, Dict[str, str]] = manifest
        self.replacer = node_transformer
        self.temp_folder = temp_folder
        self.templators: Dict[str, Templator] = {}
        self.time_delta = time_delta
        self.engine_settings = engine_settings
        self.engines: Dict[str, TemplateEngine] = None
        self.loading = True
        self.cache_handler: threading.Thread = None
        self.lock = threading.RLock()
        # default for now
        # TODO: set it as a setting
        self.cache_validation_interval = cache_validation_interval

        self.__first_loaded = False

    def full_init(self):
        if self.__first_loaded:
            raise Exception('Already initialized')
        self.loading = True
        self.__init_engines()
        self.load_templates()

        if self.cache_validation_interval != -1:
            self.start_cache_handler()
        self.loading = False

        self.__first_loaded = True

    def __init_engines(self):
        self.engines = self.__init_template_servers()
        self.__init_templators()

    def load_templates(self):
        # to be thread-safe
        with self.lock:
            for templator in self.templators.values():
                templator.pull_templates()

    def render_template(self, _type: str, name: str, data: Dict[str, str],  output: str, options: RenderOptions):
        return self.templators[_type].render(name, data, output, options)

    def __init_template_servers(self) -> None:
        available_engines: Dict[str, TemplateEngine] = {}
        for name, engine in template_engines.items():
            if name not in self.engine_settings:
                logging.warning(f'No configuration for engine {name}')
                continue
            env = self.engine_settings[name]
            ok, missing = engine.check_env(env)
            settings = ConfigOptions(env, self.minio_creds)
            if ok:
                try:
                    engine.register(settings, name)
                    logging.info(f'Successfuly registered "{name}" handler')
                except Exception as e:
                    logging.error(e)
            else:
                logging.error(
                    f'Invalid env for handler "{name}" | missing keys {missing}')
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
                    self.replacer,
                    self.engine_settings,
                    self.engines
                )
            except Exception as e:
                traceback.print_exc()

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }

    def handle_cache(self):
        for templator in self.templators.values():
            try:
                templator.handle_cache()
            except:
                logging.error(f'Failed to handle cache for {templator}')

    def start_cache_handler(self):
        e = threading.Event()
        time_between_checks = self.cache_validation_interval

        def f():
            logging.info(
                f'cache handler started, will run every {time_between_checks}')
            while True:
                self.handle_cache()
                e.wait(time_between_checks)
        t = threading.Thread(target=f)
        t.start()
        self.cache_handler = t
