import logging
import threading
import traceback
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional, Set, Type

from .data_objects import ManifestEntry, RenderOptions
from .file_provider import FileProvider
from .template_engine import TemplateEngine, template_engines
from .template_engine.adapter_middleware import MultiAdapter
from .templator import Templator


@dataclass
class ConfigOptions:
    env: dict
    minio: FileProvider


class TemplateDB:
    """Holds everything to publipost all types of templates
    """

    def __init__(
        self,
        manifest: Dict[str, ManifestEntry],
        engine_settings: Dict[str, Any],
        time_delta: timedelta,
        file_provider: FileProvider,
        node_transformer: Optional[MultiAdapter] = None,
        cache_validation_interval: float = -1,
        logger: Optional[logging.Logger] = None
    ):
        self.file_provider: FileProvider = file_provider
        self.logger = logger or logging.getLogger(
            f'TemplateDB_logger{id(self)}'
        )
        self.manifest: Dict[str, ManifestEntry] = manifest
        self.adapter: MultiAdapter = node_transformer or MultiAdapter([])
        self.templators: Dict[str, Templator] = {}
        self.time_delta: timedelta = time_delta
        """Engine Name -> settings
        """
        self.engine_settings: Dict[str, Any] = engine_settings
        self.engines: Dict[str, TemplateEngine] = {}
        self.loading: bool = True
        self.cache_handler: Optional[threading.Thread] = None
        self.lock = threading.RLock()

        self.cache_validation_interval: float = cache_validation_interval

        self.__initialized: bool = False

        self.available_connectors: Dict[str, Type[TemplateEngine]] = {}

    def init(self) -> None:
        # doing this to check if the minio instance is correct
        if not check_minio_instance(self.minio_instance):
            raise Exception('Invalid S3 credentials')
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

    def use_default_connectors(self):
        """Will bind the integrated docx, pptx and xlsx, html connector to this instance
        """
        for engine in template_engines.values():
            self.add_connector(engine)

    def render_template(
        self,
        templator_name: str,
        template_name: str,
        data: Dict[str, Any],
        output_name: str,
        options: RenderOptions
    ) -> str:
        return self.templators[templator_name].render(template_name, data, output_name, options)

    def get_templator(self, templator_name: str) -> Optional[Templator]:
        """Returns the given templator from the templator pool

        use this if you want to manually reload one templator
        """
        return self.templators.get(templator_name)

    def add_connector(self, connector: Type[TemplateEngine]):
        for ext in connector.supported_extensions:
            self.available_connectors[ext] = connector

    def __init_template_servers(self) -> None:
        if len(self.available_connectors) == 0:
            raise Exception('No connectors bound')
        available_engines: Dict[str, TemplateEngine] = {}
        # reverse the way it's done
        for ext, env in self.engine_settings.items():
            if ext not in self.available_connectors:
                self.logger.warning(
                    f'No configuration for engine {ext}, we have {list(self.available_connectors.keys())}'
                )
                continue
            engine = self.available_connectors[ext]
            ok, missing = engine.check_env(env)
            if ok:
                try:
                    settings = ConfigOptions(env, self.minio_creds)
                    engine.register(settings, self.logger)
                    self.logger.info(
                        f'Successfuly registered "{ext}" engine'
                    )
                except Exception as e:
                    traceback.print_exc()
                    self.logger.error(e)
            else:
                self.logger.error(
                    f'Invalid env for handler "{ext}" | missing keys {missing}'
                )
            available_engines[ext] = engine
        return available_engines

    def __init_templators(self):
        for bucket_name, settings in self.manifest.items():
            try:
                self.templators[settings.export_name] = Templator(
                    self.file_provider,
                    MinioPath(bucket_name),
                    MinioPath(settings.output_bucket),
                    self.time_delta,
                    self.adapter,
                    self.engine_settings,
                    self.engines,
                    self.logger
                )
            except Exception as e:
                self.logger.error(
                    f'Failed to initialize {bucket_name} templator | {e}'
                )
                traceback.print_exc()

    def to_json(self):
        return {
            name: templator.to_json() for name, templator in self.templators.items()
        }

    def __handle_cache(self):
        for templator in self.templators.values():
            try:
                templator.handle_cache()
            except Exception as e:
                self.logger.error(f'Failed to handle cache for {templator} | {e}')

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
