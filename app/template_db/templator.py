from __future__ import annotations

import datetime
import logging
import os
from typing import (TYPE_CHECKING, Any, Dict, Generator,
                    List, Literal, Tuple, Type)

import minio

from .minio_creds import MinioPath, PullInformations
from .template_engine import NEVER_PULLED, TemplateEngine, template_engines
from .template_engine.model_handler.utils import change_keys
from .template_engine.ReplacerMiddleware import MultiAdaptater

if TYPE_CHECKING:
    from .data_objects import RenderOptions

ENSURE_KEYS = 'ensure_keys'

CompileOptions = Literal['ensure_keys']


def from_filename(filename: str) -> Tuple[str, str]:
    *name, ext = filename.split('.')
    return '.'.join(name), ext


class Templator:
    """
    Holds the logic to :

        - load from minio
        - text replacement
        - render
        - push to minio
    """

    def __init__(
        self,
        minio_instance: minio.Minio,
        minio_path: MinioPath,
        output_path: MinioPath,
        time_delta: datetime.timedelta,
        replacer: MultiAdaptater,
        engine_settings: dict,
        available_engines: Dict[str, TemplateEngine],
        logger: logging.Logger
    ):
        self.remote_template_bucket: str = minio_path.bucket
        self.output_path: str = output_path
        self.templates: Dict[str, TemplateEngine] = {}
        self.minio_instance = minio_instance
        self.time_delta = time_delta
        self.replacer = replacer
        self.engine_settings = engine_settings
        self.verbose: bool = True
        self.available_engines: Dict[str,
                                     Type[TemplateEngine]] = available_engines
        self.logger = logger

    def pull_template(self, filename: str) -> List[str]:
        """Downloading and caching one template from Minio
        """
        try:
            name, ext = from_filename(filename)
            pull_infos = PullInformations(
                MinioPath(self.remote_template_bucket, filename),
                self.minio_instance
            )
            if ext in self.available_engines:
                engine = self.available_engines[ext]
                template = engine(filename, pull_infos, self.replacer)
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
                f'\t- Error importing "{filename}" from {self.remote_template_bucket}\t| {err}'
            )
            raise err

    def pull_templates(self) -> Tuple[List[str], List[str]]:
        """Downloading and caching all templates from Minio
        """
        self.logger.info(
            f'Initialising templates from bucket "{self.remote_template_bucket}"'
        )

        filenames: Generator[str, None, None] = (
            obj.object_name for obj in self.minio_instance.list_objects(self.remote_template_bucket)
        )
        successes: List[str] = []
        fails: List[str] = []
        for filename in filenames:
            try:
                self.pull_template(filename)
                successes.append(filename)
            except:
                fails.append(filename)

        self.logger.info(
            f'Initialisation finished for bucket "{self.remote_template_bucket}"'
        )
        return successes, fails

    def to_json(self) -> Dict[str, List[str]]:
        return {
            name: template.get_fields() for name, template in self.templates.items()
        }

    def __get_engine_instance(self, template_name: str) -> TemplateEngine:
        return self.templates[template_name]

    def render(self, template_name: str, data: Dict[str, Any], output_name: str, options: RenderOptions) -> str:
        output_name = os.path.join(self.output_path.filename, output_name)

        template = self.__get_engine_instance(template_name)
        if not template.is_up():
            template.reconfigure()
        # to know if we want to ensure_keys or have an error
        should_ensure_keys = ENSURE_KEYS in options.compile_options

        rendered_data = change_keys(
            template.model.merge(data, should_ensure_keys),
            template.replacer.to_doc
        )

        result = template.render_to(
            rendered_data,
            MinioPath(self.output_path.bucket, output_name),
            options
        )

        # if push_result == True, then the engine,
        # will push the result directly to the S3
        if options.push_result:
            return self.minio_instance.presigned_get_object(
                self.output_path.bucket,
                output_name,
                expires=self.time_delta
            )
        else:
            return result

    # TODO: cut this in smaller pieces

    def handle_cache(self):
        """this methods checks the bucket for template updates or new templates
        """
        modified_at = (
            (obj.object_name, obj.last_modified.timestamp())
            for obj in self.minio_instance.list_objects(self.remote_template_bucket)
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
