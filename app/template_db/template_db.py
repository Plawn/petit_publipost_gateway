import logging
import threading
import traceback
from datetime import timedelta
from typing import Any, Dict, List, Optional, Set

import minio

from .data_objects import ConfigOptions, ManifestEntry, RenderOptions
from .minio_creds import MinioCreds, MinioPath
from .template_engine import TemplateEngine, template_engines
from .template_engine.model_handler.utils import from_strings_to_dict
from .template_engine.ReplacerMiddleware import MultiReplacer
from .templator import Templator


def check_minio_instance(minio_instance: minio.Minio) -> bool:
    try:
        _ = minio_instance.list_buckets()
        return True
    except:
        return False


class TemplateDB:
    """Holds everything to publipost all types of templates
    """

    def __init__(
        self,
        manifest: Dict[str, ManifestEntry],
        engine_settings: Dict[str, Any],
        time_delta: timedelta,
        minio_creds: MinioCreds,
        node_transformer: Optional[MultiReplacer] = None,
        cache_validation_interval: float = -1,
        logger: Optional[logging.Logger] = None
    ):
        self.minio_creds: MinioCreds = minio_creds
        self.minio_instance = self.minio_creds.as_client()
        self.logger = logger or logging.getLogger(
            f'TemplateDB_logger{id(self)}')
        # doing this to check if the minio instance is correct
        if not check_minio_instance(self.minio_instance):
            raise Exception('Invalid minio creds')
        self.manifest: Dict[str, ManifestEntry] = manifest
        self.replacer: MultiReplacer = node_transformer or MultiReplacer([])
        self.templators: Dict[str, Templator] = {}
        self.time_delta = time_delta
        self.engine_settings = engine_settings
        self.engines: Dict[str, TemplateEngine] = None
        self.loading: bool = True
        self.cache_handler: Optional[threading.Thread] = None
        self.lock = threading.RLock()

        self.cache_validation_interval: float = cache_validation_interval

        self.__initialized: bool = False

    def init(self) -> None:
        if self.__initialized:
            raise Exception('Already initialized')
        self.loading = True
        self.__init_engines()
        self.load_templates()

        if self.cache_validation_interval != -1:
            self.__start_cache_handler()
        self.loading = False

        self.__initialized = True

    def __init_engines(self) -> None:
        self.engines = self.__init_template_servers()
        self.__init_templators()

    def load_templates(self) -> None:
        # to be thread-safe
        with self.lock:
            for templator in self.templators.values():
                templator.pull_templates()

    def render_template(self, templator_name: str, template_name: str, data: Dict[str, Any],  output_name: str, options: RenderOptions):
        return self.templators[templator_name].render(template_name, data, output_name, options)

    def add_connector(self):
        raise NotImplementedError

    def __init_template_servers(self) -> None:
        available_engines: Dict[str, TemplateEngine] = {}
        # reverse the way it's done
        for name, engine in template_engines.items():
            if name not in self.engine_settings:
                self.logger.warning(f'No configuration for engine {name}')
                continue
            env = self.engine_settings[name]
            ok, missing = engine.check_env(env)
            settings = ConfigOptions(env, self.minio_creds)
            if ok:
                try:
                    engine.register(settings, name, self.logger)
                    self.logger.info(
                        f'Successfuly registered "{name}" engine'
                    )
                except Exception as e:
                    traceback.print_exc()
                    self.logger.error(e)
            else:
                self.logger.error(
                    f'Invalid env for handler "{name}" | missing keys {missing}')
            available_engines[name] = engine
        return available_engines

    def __init_templators(self):
        for bucket_name, settings in self.manifest.items():
            try:
                self.templators[settings.export_name] = Templator(
                    self.minio_instance,
                    MinioPath(bucket_name),
                    MinioPath(settings.output_bucket),
                    self.time_delta,
                    self.replacer,
                    self.engine_settings,
                    self.engines,
                    self.logger
                )
            except Exception as e:
                self.logger.error(
                    f'Failed to initialize {bucket_name} templator')
                traceback.print_exc()

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }

    def __handle_cache(self):
        for templator in self.templators.values():
            try:
                templator.handle_cache()
            except:
                self.logger.error(f'Failed to handle cache for {templator}')

    def __start_cache_handler(self):
        e = threading.Event()
        time_between_checks = self.cache_validation_interval

        def f():
            self.logger.info(
                f'cache handler started, will run every {time_between_checks}'
            )
            while True:
                self.__handle_cache()
                e.wait(time_between_checks)
        # daemon = True, to make the thread die at the end
        t = threading.Thread(target=f, daemon=True)
        t.start()
        self.cache_handler = t
