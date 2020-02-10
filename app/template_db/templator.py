import datetime
import os
import shutil
from typing import Dict
import uuid
import minio
from typing import Tuple
import Fancy_term as term
from .template_engine import template_engines, TemplateEngine
from .template_engine.ReplacerMiddleware import MultiReplacer
from .minio_creds import MinioPath, PullInformations
from .utils import error_printer, success_printer, info_printer
from .template_engine.model_handler.utils import change_keys


TEMP_FOLDER = 'temp'


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
        # placeholder
        self.verbose = True
        self.available_engines: Dict[str, TemplateEngine] = available_engines

        self.__init_cache()

    def __init_cache(self):
        # removing cache on startup
        if os.path.exists(self.local_template_directory):
            shutil.rmtree(self.local_template_directory)
        os.mkdir(self.local_template_directory)
        os.mkdir(self.temp_folder)

    def pull_templates(self):
        """Downloading and caching all templates from Minio
        """
        if self.verbose:
            info_printer(
                f'Importing template from bucket "{self.remote_template_bucket}"')

        filenames = (obj.object_name for obj in self.minio_instance.list_objects(
            self.remote_template_bucket))
        for filename in filenames:
            try:
                name, ext = from_filename(filename)
                local_filename = os.path.join(
                    self.local_template_directory, filename)
                pull_infos = PullInformations(local_filename, MinioPath(
                    self.remote_template_bucket, filename), self.minio_instance)
                templator = self.available_engines[ext](
                    pull_infos, self.replacer, self.temp_folder, self.engine_settings[ext])
                self.templates[name] = templator
                if self.verbose:
                    success_printer(
                        f'\t- Successfully imported "{name}" using {templator}')
            except Exception as err:
                import traceback
                traceback.print_exc()
                error_printer(
                    f'\t- Error importing "{name}" from {self.remote_template_bucket} | {err}')

    def to_json(self):
        return {
            name: template.get_fields() for name, template in self.templates.items()
        }

    def render(self, template_name: str, data: Dict[str, str], output_name: str) -> str:
        output_name = os.path.join(self.output_path.filename, output_name)

        engine = self.templates[template_name]

        data = change_keys(engine.model.merge(data), engine.replacer.to_doc)
        engine.render_to(
            data, MinioPath(self.output_path.bucket, output_name))

        return self.minio_instance.presigned_get_object(
            self.output_path.bucket,
            output_name,
            expires=self.time_delta)
