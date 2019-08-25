import datetime
import os
import shutil
from typing import Dict

import minio

from .better_publiposting import DocxTemplate
from .better_publiposting.ReplacerMiddleware import MultiReplacer
from .minio_creds import MinioPath

TEMP_FOLDER = 'temp'


def from_filename(filename: str) -> str:
    return filename.split('.')[0]


class Templator:
    """
    Holds the logic to :

        - 'load from minio'
        - 'text replacement'
        - 'render'
        - 'push to minio'
    """

    def __init__(self, minio_instance: minio.Minio, temp_dir: str, minio_path: MinioPath,
                 output_folder: str, time_delta: datetime.timedelta, replacer: MultiReplacer):
        self.remote_template_directory = minio_path.bucket
        self.local_template_directory = os.path.join(
            temp_dir, self.remote_template_directory)
        self.output_folder = output_folder
        self.templates: Dict[str, DocxTemplate] = {}
        self.minio_instance = minio_instance
        self.time_delta = time_delta
        self.replacer = replacer
        # removing cache on startup
        if os.path.exists(self.local_template_directory):
            shutil.rmtree(self.local_template_directory)
        os.mkdir(self.local_template_directory)
        os.mkdir(os.path.join(self.local_template_directory, TEMP_FOLDER))

    def pull_templates(self):
        """Downloading and caching all templates from Minio
        """
        filenames = (obj.object_name for obj in self.minio_instance.list_objects(
            self.remote_template_directory))
        for filename in filenames:
            try:
                doc = self.minio_instance.get_object(
                    self.remote_template_directory, filename)
                with open(os.path.join(self.local_template_directory, filename), 'wb') as file_data:
                    for d in doc.stream(32*1024):
                        file_data.write(d)
                self.templates[from_filename(filename)] = DocxTemplate(
                    os.path.join(self.local_template_directory, filename), self.replacer)
            except Exception as err:
                # import traceback
                # traceback.print_exc()
                print(err)

    def to_json(self):
        return {
            name: template.model.to_json() for name, template in self.templates.items()
        }

    def render(self, template_name: str, data: Dict[str, str], output_name: str) -> str:

        doc = self.templates[template_name].apply_template(data)
        save_path = os.path.join(
            self.local_template_directory, TEMP_FOLDER, output_name)

        # if we could stream the resulting file it would be even better
        # -> wouldn't have to save the file to the disk and then to read it again to push it to minio
        doc.save(save_path)
        self.minio_instance.fput_object(
            self.output_folder, output_name, save_path)
        os.remove(save_path)
        return self.minio_instance.presigned_get_object(
            self.output_folder,
            output_name,
            expires=self.time_delta)
