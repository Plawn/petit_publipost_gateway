import os
import shutil
import threading
from datetime import timedelta
from typing import Dict

import yaml

from .template_db import MinioCreds, TemplateDB
from .transformers import PHOENIX_NODE_TRANSFORMER
from .template_db.utils import conf_loader

# should be env or config variable
TIME_DELTA = timedelta(days=1)
MANIFEST_TOKEN = 'manifest'


try:
    conf_filename: str = os.environ['CONF_FILE']
except:
    raise Exception('missing "CONF_FILE" env')

with open(conf_filename, 'r') as f:
    conf: Dict[str, object] = yaml.safe_load(f)

manifest = conf[MANIFEST_TOKEN]

minio_creds = MinioCreds(**conf['minio'])

engine_settings = conf['engine_settings']
cache_validation_interval: float = conf['cache_validation_interval']


template_db = TemplateDB(
    manifest,
    engine_settings,
    TIME_DELTA,
    minio_creds,
    node_transformer=PHOENIX_NODE_TRANSFORMER,
    cache_validation_interval=cache_validation_interval
)

