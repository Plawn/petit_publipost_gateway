import traceback
import logging
import datetime
import os
import shutil
import uuid
from typing import Dict, List, Tuple

import Fancy_term as term
import minio

from .minio_creds import MinioPath, PullInformations
from .template_engine import TemplateEngine, template_engines
from .template_db import RenderOptions
from .template_engine.model_handler.utils import change_keys
from .template_engine.ReplacerMiddleware import MultiReplacer
from .utils import error_printer, info_printer, success_printer

TEMP_FOLDER = 'temp'
ENSURE_KEYS = 'ensure_keys'

def from_filename(filename: str) -> Tuple[str, str]:
    *name, ext = filename.split('.')
    return '.'.join(name), ext


class Templator:
    """
    Holds the logic to :

        - 'load from minio'
        - 'text replacement'
        - 'render'
        - 'push to minio'
    """

    def __init__(self, minio_instance: minio.Minio, temp_dir: str, minio_path: MinioPath,
                 output_path: MinioPath, time_delta: datetime.timedelta,
                 replacer: MultiReplacer, engine_settings: dict,
                 available_engines: Dict[str, TemplateEngine]):
        self.remote_template_bucket = minio_path.bucket
        self.local_template_directory = os.path.join(
            temp_dir, self.remote_template_bucket)
        self.output_path = output_path
        self.templates: Dict[str, TemplateEngine] = {}
        self.minio_instance = minio_instance
        self.time_delta = time_delta
        self.replacer = replacer
        self.engine_settings = engine_settings
        self.temp_folder = os.path.join(
            self.local_template_directory, TEMP_FOLDER)
        self.verbose = True
        self.available_engines: Dict[str, TemplateEngine] = available_engines

        self.__init_cache()

    # should be deprecated too

    def __init_cache(self):
        # removing cache on startup
        if os.path.exists(self.local_template_directory):
            shutil.rmtree(self.local_template_directory)
        os.mkdir(self.local_template_directory)
        os.mkdir(self.temp_folder)

    def pull_template(self, filename: str) -> List[str]:
        """Downloading and caching one template from Minio
        """
        try:
            name, ext = from_filename(filename)
            # there is no need for local_filename now that all the engines are remote
            local_filename = os.path.join(
                self.local_template_directory, filename)
            pull_infos = PullInformations(local_filename, MinioPath(
                self.remote_template_bucket, filename), self.minio_instance)
            if ext in self.available_engines:
                template = self.available_engines[ext](
                    pull_infos, self.replacer, self.temp_folder, self.engine_settings[ext])
                self.templates[name] = template
                template.init()
                if self.verbose:
                    success_printer(
                        f'\t- Successfully imported "{name}" using {template}')
                    logging.info(f'\t- Successfully imported "{name}" using {template}')
                return template.get_fields()
            else:
                logging.error('Engine not available')
        except Exception as err:
            logging.error(
                f'\t- Error importing "{name}" from {self.remote_template_bucket} | {err}')
            logging.error(traceback.format_exc())
            raise

    def pull_templates(self) -> Tuple[List[str], List[str]]:
        """Downloading and caching all templates from Minio
        """
        if self.verbose:
            info_printer(
                f'Importing templates from bucket "{self.remote_template_bucket}"')
                
        logging.info(f'Importing templates from bucket "{self.remote_template_bucket}"')

        filenames = (obj.object_name for obj in self.minio_instance.list_objects(
            self.remote_template_bucket))
        successes, fails = [], []
        for filename in filenames:
            try:
                self.pull_template(filename)
                successes.append(filename)
            except:
                fails.append(filename)

        if self.verbose:
            info_printer(
                f'Import finished for bucket "{self.remote_template_bucket}"')
        logging.info(f'Import finished for bucket "{self.remote_template_bucket}"')
        return successes, fails

    def to_json(self):
        return {
            name: template.get_fields() for name, template in self.templates.items()
        }

    def render(self, template_name: str, data: Dict[str, str], output_name: str, options: RenderOptions) -> str:
        output_name = os.path.join(self.output_path.filename, output_name)

        engine = self.templates[template_name]

        # to know if we want to ensure_keys or have an error
        ensure_keys = ENSURE_KEYS in options.compile_options

        data = change_keys(engine.model.merge(
            data, ensure_keys), engine.replacer.to_doc)

        result = engine.render_to(
            data, MinioPath(self.output_path.bucket, output_name), options)

        if options.push_result:
            return self.minio_instance.presigned_get_object(
                self.output_path.bucket,
                output_name,
                expires=self.time_delta)
        else:
            return result
