import traceback
import logging
import os
import shutil
import time
import traceback
import uuid
from typing import Dict, List, Tuple
import datetime
import Fancy_term as term
import minio

from .minio_creds import MinioPath, PullInformations
from .template_db import RenderOptions
from .template_engine import NEVER_PULLED, TemplateEngine, template_engines
from .template_engine.model_handler.utils import change_keys
from .template_engine.ReplacerMiddleware import MultiReplacer

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

    def __init__(self, minio_instance: minio.Minio, minio_path: MinioPath,
                 output_path: MinioPath, time_delta: datetime.timedelta,
                 replacer: MultiReplacer, engine_settings: dict,
                 available_engines: Dict[str, TemplateEngine], logger: logging.Logger):
        self.remote_template_bucket = minio_path.bucket
        self.local_template_directory = os.path.join(
            'temp', self.remote_template_bucket)
        self.output_path = output_path
        self.templates: Dict[str, TemplateEngine] = {}
        self.minio_instance = minio_instance
        self.time_delta = time_delta
        self.replacer = replacer
        self.engine_settings = engine_settings
        self.verbose = True
        self.available_engines: Dict[str, TemplateEngine] = available_engines
        self.logger = logger

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
                template = self.available_engines[ext](filename,
                                                       pull_infos, self.replacer, self.engine_settings[ext])
                self.templates[name] = template
                template.init()
                if self.verbose:
                    self.logger.info(
                        f'\t- Successfully registered "{name}" using {template}')
                return template.get_fields()
            else:
                self.logger.error(f'Engine not available | {ext}')
        except Exception as err:
            # import traceback; traceback.print_exc();
            self.logger.error(
                f'\t- Error importing "{name}" from {self.remote_template_bucket}\t| {err}')
            raise

    def pull_templates(self) -> Tuple[List[str], List[str]]:
        """Downloading and caching all templates from Minio
        """
        self.logger.info(
            f'Initialising templates from bucket "{self.remote_template_bucket}"')

        filenames = (obj.object_name for obj in self.minio_instance.list_objects(
            self.remote_template_bucket, recursive=True))
        successes, fails = [], []
        for filename in filenames:
            try:
                self.pull_template(filename)
                successes.append(filename)
            except:
                fails.append(filename)

        self.logger.info(
            f'Initialisation finished for bucket "{self.remote_template_bucket}"')
        return successes, fails

    def to_json(self):
        return {
            name: template.get_fields() for name, template in self.templates.items()
        }

    def render(self, template_name: str, data: Dict[str, str], output_name: str, options: RenderOptions) -> str:
        output_name = os.path.join(self.output_path.filename, output_name)

        engine = self.templates[template_name]
        if not engine.is_up():
            engine.reconfigure()
        # to know if we want to ensure_keys or have an error
        should_ensure_keys = ENSURE_KEYS in options.compile_options

        data = change_keys(engine.model.merge(
            data, should_ensure_keys), engine.replacer.to_doc)

        result = engine.render_to(
            data, MinioPath(self.output_path.bucket, output_name), options)

        if options.push_result:
            return self.minio_instance.presigned_get_object(
                self.output_path.bucket,
                output_name,
                expires=self.time_delta)
        else:
            return result

    # TODO: cut this in smaller pieces

    def handle_cache(self):
        """this methods checks the bucket for template updates or new templates
        """
        modified_at = (
            (obj.object_name, obj.last_modified.timestamp())
            for obj in self.minio_instance.list_objects(self.remote_template_bucket, recursive=True)
        )
        # TODO: should cache this after
        loaded_filenames: Dict[str, TemplateEngine] = {
            template.filename: template for template in self.templates.values()
        }
        to_reload: List[TemplateEngine] = []
        to_load: List[str] = []
        for filename, _modified_at in modified_at:
            if filename in loaded_filenames:
                pulled_at = loaded_filenames[filename].pulled_at
                # -1 means that we never pulled the file before
                if pulled_at < _modified_at:
                    self.logger.info(f'Scheduled "{filename}" for reload')
                    to_reload.append(loaded_filenames[filename])
            else:
                self.logger.info(
                    f'New template detected "{filename}" -> scheduled for initial load')
                to_load.append(filename)

        # the easy part -> reloading the existing ones
        for template in to_reload:
            try:
                template.init()
            except Exception as e:
                self.logger.error(e)

        # the other part -> registering the other templates
        for filename in to_load:
            try:
                self.pull_template(filename)
            except:
                self.logger.warning(f'Failed to pull template {filename}')
