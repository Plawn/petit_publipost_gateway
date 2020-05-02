import os
import shutil
import threading
from datetime import timedelta
from typing import Dict

import yaml

from .template_db import MinioCreds, TemplateDB
from .template_db.template_engine.ReplacerMiddleware import (FuncReplacer,
                                                             MultiReplacer)
from .template_db.utils import conf_loader

# should be env or config variable
TIME_DELTA = timedelta(days=1)
MANIFEST_TOKEN = 'manifest'

CACHE_VALIDATION_INTERVAL = 60

PHOENIX_NODE_TRANSFORMER = MultiReplacer([
    FuncReplacer
])

try:
    conf_filename: str = os.environ['CONF_FILE']
except:
    raise Exception('missing "CONF_FILE" env')

with open(conf_filename, 'r') as f:
    conf: Dict[str, object] = yaml.safe_load(f)

manifest = conf[MANIFEST_TOKEN]

minio_creds = MinioCreds(
    conf['MINIO_HOST'],
    conf['MINIO_KEY'],
    conf['MINIO_PASS'],
    conf['SECURE'],
)

engine_settings = conf['engine_settings']

template_db = TemplateDB(
    manifest,
    engine_settings,
    TIME_DELTA,
    minio_creds,
    node_transformer=PHOENIX_NODE_TRANSFORMER,
    cache_validation_interval=CACHE_VALIDATION_INTERVAL
)


def load_db():
    template_db.full_init()


# async initialization
t = threading.Thread(target=load_db)
t.start()
