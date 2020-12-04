"""
Base class
"""
from __future__ import annotations

import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Set, Tuple

import requests

from ..minio_creds import MinioCreds, MinioPath, PullInformations
from .auto_configurer import AutoConfigurer, FailedToConfigure
from .model_handler import Model, SyntaxtKit
from .ReplacerMiddleware import MultiReplacer

if TYPE_CHECKING:
    from ..data_objects import RenderOptions
    from ..template_db import ConfigOptions
    from ..templator import CompileOptions


def make_url(settings: dict) -> str:
    return f"http{'s' if settings['secure'] else ''}://{settings['host']}"


NEVER_PULLED = -1


class EngineDown(Exception):
    """The engine is down and cannot answer"""


class TemplateEngine(ABC):
    requires_env: Iterable[str] = []

    registered_templates: List[TemplateEngine] = []
    url = ''
    ext = ''
    logger: Optional[logging.Logger] = None
    __conf: Optional[ConfigOptions] = None
    __auto_checker: Optional[AutoConfigurer] = None

    def __init__(self, filename: str, pull_infos: PullInformations, replacer: MultiReplacer):

        self.model: Optional[Model] = None
        self.pull_infos: PullInformations = pull_infos
        self.replacer: MultiReplacer = replacer
        self.pulled_at: int = NEVER_PULLED
        self.filename: str = filename

        """To ensure that we don't have name collision when using it with multiple buckets
        """
        self.exposed_as: str = self.get_exposed_as()

        self.performing_init: bool = False
        """Lock to handle, threaded context
        """
        self.__init_lock = threading.Lock()

    def get_exposed_as(self):
        """To ensure that we don't have name collision when using it with multiple buckets
        """
        return f'{self.pull_infos.remote.bucket}/{self.pull_infos.remote.filename}'

    @classmethod
    def check_env(cls, env: dict) -> bool:
        missing_keys: Set[str] = set()
        for key in cls.requires_env:
            if key not in env:
                missing_keys.add(key)
        return len(missing_keys) == 0, missing_keys

    @classmethod
    def register(cls, env: ConfigOptions, ext: str, logger: logging.Logger) -> None:
        cls.__conf = env
        cls.ext = ext
        cls.logger = logger
        settings = cls.__conf.env
        cls.url = make_url(settings)
        cls.__auto_checker = AutoConfigurer(
            cls.__name__,
            check_live=cls._check_live,
            configure=cls._configure,
            logger=cls.logger,
            post_configuration=cls._re_register_templates
        )

    @classmethod
    def _check_live(cls):
        return requests.get(cls.url + '/live').status_code < 300

    @classmethod
    def is_up(cls) -> bool:
        return cls.__auto_checker.is_up() if cls.__auto_checker is not None else False

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'

    @classmethod
    def is_configuring(cls):
        if cls.__auto_checker is None:
            return True
        return cls.__auto_checker.is_configuring()

    @classmethod
    def _configure(cls) -> None:
        creds: MinioCreds = cls.__conf.minio
        data = {
            'host': creds.host,
            'access_key': creds.accessKey,
            'pass_key': creds.passKey,
            'secure': creds.secure,
        }
        try:
            res = requests.post(cls.url + '/configure', json=data)
            if res.status_code >= 300:
                raise FailedToConfigure
        except:
            raise EngineDown(cls.__name__)

    @classmethod
    def _re_register_templates(cls):
        for template in cls.registered_templates:
            try:
                template.init()
            except:
                cls.logger.warning(f'Failed to init {template}')

    def render_to(self, data: dict, path: MinioPath, options: RenderOptions) -> None:
        if not self.is_up():
            self.reconfigure()

        # should make a dataclass here
        data = {
            'data': data,
            'template_name': self.exposed_as,
            'output_bucket': path.bucket,
            'output_name': path.filename,
            'options': options.compile_options,
            'push_result': options.push_result,
        }
        res = requests.post(self.url + '/publipost', json=data)
        result = res.json()
        if 'error' in result:
            if result['error']:
                raise Exception('An error has occured')
        return result

    def to_json(self) -> dict:
        return self.model.structure

    def get_fields(self) -> List[str]:
        if self.model is not None and self.is_up():
            return self.model.fields
        return None

    @classmethod
    def remove_template(cls, template_name: str) -> None:
        res = requests.delete(
            cls.url + '/remove_template',
            json={'template_name': template_name}
        )
        if res.status_code >= 400:
            raise Exception(f'failed to remove template | {res}')

    @classmethod
    def list(cls):
        return requests.get(cls.url + '/list').json()

    def reconfigure(self, init: bool = True):
        self.__auto_checker.force_configure(False)
        if init:
            self.init()

    @abstractmethod
    def _load_fields(self, fields: Optional[List[str]] = None) -> None:
        ...

    def init(self) -> None:
        """Loads the document from the filename and inits it's values
        """
        if not self.performing_init:
            with self.__init_lock:
                self.performing_init = True
                try:
                    if not self.is_up():
                        self.reconfigure(init=False)
                    res = requests.post(
                        self.url + '/load_templates',
                        json=[{
                            'bucket_name': self.pull_infos.remote.bucket,
                            'template_name': self.pull_infos.remote.filename,
                            'exposed_as': self.exposed_as
                        }])
                    result = res.json()
                    successes = result['success']
                    if len(result['success']) < 1:
                        raise Exception(f'Failed to import {self.filename}')
                    fields = successes[0]['fields']
                    self._load_fields(fields)
                    self.pulled_at = time.time()
                except:
                    self.pulled_at = NEVER_PULLED
                finally:
                    self.performing_init = False
        else:
            with self.__init_lock:
                if not self.is_up():
                    raise Exception(f'Failed to init {self.filename}')
