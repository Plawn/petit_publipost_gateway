import minio
from .better_publiposting import DocxTemplate
import os
import json
from typing import Dict
from .minio_creds import MinioCreds, MinioPath
from datetime import timedelta
import shutil

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

def from_filename(filename: str) -> str:
    return filename.split('.')[0]


class Templator:
    def __init__(self, minio_instance: minio.Minio, temp_dir: str, minio_path: MinioPath, output_folder: str, class_separator: str):
        remote_template_directory = minio_path.bucket
        self.remote_template_directory = remote_template_directory
        self.local_template_directory = os.path.join(
            temp_dir, self.remote_template_directory)
        self.output_folder = output_folder
        self.class_separator = class_separator
        self.templates: Dict[str, DocxTemplate] = {}
        self.minio_instance = minio_instance

        # removing cache on startup
        if os.path.exists(self.local_template_directory):
            shutil.rmtree(self.local_template_directory)
        os.mkdir(self.local_template_directory)
        os.mkdir(os.path.join(self.local_template_directory, 'temp'))

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
                    os.path.join(self.local_template_directory, filename), self.class_separator)
            except Exception as err:
                # import traceback
                # traceback.print_exc()
                print(err)

    def to_json(self):
        return {
            name: template.to_json() for name, template in self.templates.items()
        }

    def render(self, template_name: str, data: Dict[str, str], output_name: str) -> str:
        res: Dict[str, str] = {}
        for _type, val in data.items():
            for key, value in val.items():
                res[self.class_separator.join((_type, key))] = value
        doc = self.templates[template_name].apply_template(res)
        save_path = os.path.join(
            self.local_template_directory, 'temp', output_name)

        # if we could stream the resulting file it would be even better
        doc.save(save_path)
        self.minio_instance.fput_object(
            self.output_folder, output_name, save_path)
        os.remove(save_path)
        return self.minio_instance.presigned_get_object(
            self.output_folder,
            output_name,
            expires=TIME_DELTA)


class TemplateDB:
    def __init__(self, manifest_path: MinioPath, temp_folder: str, minio_creds: MinioCreds):
        self.minio_creds = minio_creds
        self.minio_instance = minio.Minio(
            self.minio_creds.host, self.minio_creds.key, self.minio_creds.password)
        self.manifest_path = manifest_path
        self.manifest: Dict[str, Dict[str, str]] = None
        self.get_manifest()
        self.temp_folder = temp_folder
        self.templators: Dict[str, Templator] = {}
        self._init()

    def _init(self):
        self.__init_templators()
        for templator in self.templators.values():
            templator.pull_templates()

    def get_manifest(self):
        doc = self.minio_instance.get_object(self.manifest_path.bucket,
                                             self.manifest_path.filename)
        with open(os.path.join(self.manifest_path.filename), 'wb') as file_data:
            for d in doc.stream(32*1024):
                file_data.write(d)
        with open(os.path.join(self.manifest_path.filename), 'r') as f:
            self.manifest = json.load(f)

    def render_template(self, _type: str, name: str, data: Dict[str, str], output: str):
        return self.templators[_type].render(name, data, output)

    def __init_templators(self):
        for bucket_name, settings in self.manifest.items():
            self.templators[settings['type']] = Templator(
                self.minio_instance, self.temp_folder, MinioPath(bucket_name), settings['output_folder'], settings['class_separator'])

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }
