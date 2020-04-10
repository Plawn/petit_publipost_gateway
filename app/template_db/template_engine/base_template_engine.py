"""
Base class
"""
from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Tuple

import requests

from ..minio_creds import MinioPath, PullInformations
from ..template_db import ConfigOptions, RenderOptions
from .health_checker import AutoConfigurer, FailedToConfigure
from .model_handler import Model, SyntaxtKit
from .ReplacerMiddleware import MultiReplacer


def make_url(settings: dict) -> str:
    return f"http{'s' if settings['secure'] else ''}://{settings['host']}"


NEVER_PULLED = -1


class TemplateEngine(ABC):
    requires_env: Tuple[str] = []

    registered_templates: List[TemplateEngine] = []
    url = ''
    ext = ''

    __conf: ConfigOptions = None

    __auto_checker: HealthChecker = None

    # this exists only for interface purposes
    @abstractmethod
    def __init__(self, filename: str, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        self.model = Model([], replacer, SyntaxtKit('', '', ''))
        self.pull_infos = pull_infos
        self.replacer = replacer
        self.pulled_at = NEVER_PULLED
        self.filename = filename

    @abstractmethod
    def init(self):
        self.pulled_at = time.time()
        pass

    @classmethod
    def check_env(cls, env: dict) -> bool:
        missing_keys: Set[str] = set()
        for key in cls.requires_env:
            if key not in env:
                missing_keys.add(key)
        return len(missing_keys) == 0, missing_keys

    @classmethod
    def register(cls, env: ConfigOptions, ext: str) -> None:
        cls.__conf = env
        cls.ext = ext
        settings = cls.__conf.env
        cls.url = make_url(settings)
        cls.__auto_checker = AutoConfigurer(
            cls.__name__,
            check_live=cls._check_live,
            configure=cls._configure,
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
            'access_key': creds.key,
            'pass_key': creds.password,
            'secure': creds.secure,
        }
        res = requests.post(cls.url + '/configure', json=data)
        if res.status_code >= 300:
            raise FailedToConfigure

    @classmethod
    def _re_register_templates(cls):
        for template in cls.registered_templates:
            try:
                template.init()
            except:
                logging.warning(f'Failed to init {template}')

    def render_to(self, data: dict, path: MinioPath, options: RenderOptions) -> None:
        # should make a dataclass here
        data = {
            'data': data,
            'template_name': self.pull_infos.remote.filename,
            'output_bucket': path.bucket,
            'output_name': path.filename,
            'options': options.compile_options,
            'push_result': options.push_result,
        }
        res = requests.post(self.url + '/publipost', json=data)
        result = json.loads(res.text)
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
