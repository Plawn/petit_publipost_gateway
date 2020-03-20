"""
Base class
"""
from __future__ import annotations
from abc import abstractmethod, ABC
from .ReplacerMiddleware import MultiReplacer
from typing import Dict, Tuple, Set, List
from ..minio_creds import PullInformations, MinioPath
from .model_handler import Model, SyntaxtKit
from ..template_db import RenderOptions, ConfigOptions
import requests
import json
import threading
import uuid
import logging


def make_token():
    return str(uuid.uuid4())


class Template(ABC):
    @abstractmethod
    def save(self, filename: str):
        pass


class TemplateEngine(ABC):
    requires_env: Tuple[str] = []

    registered_templates: List[TemplateEngine] = []
    url = ''
    ext  = ''

    base_check_up_time = 30
    __conf: ConfigOptions = None

    __configuring = False
    __auto_check_thread: threading.Thread = None
    __auto_check_event: threading.Event = None
    __running: bool = False

    __up: bool = False

    @classmethod
    def check_env(cls, env: dict) -> bool:
        missing_keys: Set[str] = set()
        for key in cls.requires_env:
            if key not in env:
                missing_keys.add(key)
        return len(missing_keys) == 0, missing_keys

    @abstractmethod
    def __init__(self, pull_infos: PullInformations, replacer: MultiReplacer, temp_dir: str, settings: dict):
        self.model = Model([], replacer, SyntaxtKit('', '', ''))
        self.replacer = replacer

    def render_to(self, data: dict, path: MinioPath, options: RenderOptions) -> None:
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

    @classmethod
    def configure(cls, env: ConfigOptions, ext:str) -> None:
        if cls.__configuring:
            raise Exception('Already geeting configured')
        cls.__configuring = True
        cls.__conf = env
        cls.ext = ext
        settings = cls.__conf.env

        cls.url = f"http{'s' if settings['secure'] else ''}://{settings['host']}"

        if cls.__auto_check_thread is not None:
            cls.__running = False
            cls.__auto_check_event.set()

        event = threading.Event()

        def check_live():
            while cls.__running:
                event.wait(cls.base_check_up_time)
                event.clear()
                try:
                    # print('get live', threading.get_ident())
                    res = requests.get(cls.url + '/live')
                    cls.__up = res.status_code < 300
                    if not cls.__up:
                        logging.warning(
                            f'engine down {cls} trying to configure')
                        cls.configure(cls.__conf, cls.ext)
                except:
                    cls.__up = False

        cls.__running = True
        cls.__auto_check_thread = threading.Thread(target=check_live)
        cls.__auto_check_event = event

        cls.__auto_check_thread.start()

        cls._configure()

        cls.__configuring = False

    def get_fields(self) -> List[str]:
        return self.model.fields

    @classmethod
    def _re_register_templates(cls):
        for template in cls.registered_templates:
            template.init()

    @classmethod
    def is_up(cls) -> bool:
        return cls.__up

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'

    @classmethod
    def set_up(cls):
        cls.__up = True

    @classmethod
    def set_down(cls):
        cls.__up = False

    @abstractmethod
    def init(self):
        pass

    @classmethod
    def _configure(cls) -> None:
        creds: MinioCreds = cls.__conf.minio
        data = {
            'host': creds.host,
            'access_key': creds.key,
            'pass_key': creds.password,
            'secure': creds.secure,
        }
        res = None
        try:
            res = json.loads(requests.post(cls.url + '/configure',
                                           json=data).text)
            cls.set_up()
            cls._re_register_templates()
        except:
            if res is not None and res['error']:
                return logging.error(f'Failed to configure "{cls.ext}" handler but server responded')                
            return logging.error(f'Failed to connect to "{cls.ext}" handler')
            
        logging.info(f'Successfuly started "{cls.ext}" handler')