from datetime import timedelta
import yaml
import os
from .template_db import MinioCreds, TemplateDB
from typing import Dict
import shutil
import threading

# should be env or config variable
TIME_DELTA = timedelta(days=1)
TEMP_DIR = 'temp'
MANIFEST_TOKEN = 'manifest'

# should be somewhere else
# preparing temp dir
if os.path.exists(TEMP_DIR):
    print(f'deleting temp dir {TEMP_DIR}')
    shutil.rmtree(TEMP_DIR)
os.mkdir(TEMP_DIR)


try:
    conf_filename: str = os.environ['CONF_FILE']
except:
    raise Exception('missing "CONF_FILE" env')

with open(conf_filename, 'r') as f:
    settings: Dict[str, object] = yaml.load(f)

manifest = settings[MANIFEST_TOKEN]

minio_creds = MinioCreds(
    settings['MINIO_HOST'],
    settings['MINIO_KEY'],
    settings['MINIO_PASS'],
    settings['SECURE'],
)

engine_settings = settings['engine_settings']

template_db = TemplateDB(
    manifest,
    engine_settings,
    TIME_DELTA,
    TEMP_DIR,
    minio_creds
)

def load_db():
    template_db.full_init()


t = threading.Thread(target=load_db)
t.start()