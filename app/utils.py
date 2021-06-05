import os
from datetime import timedelta
from functools import lru_cache
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel
from pydantic.fields import Field

from .template_db import MinioCreds
from .template_db.data_objects import ManifestEntry

CONF_FILE_TOKEN = 'CONF_FILE'


class Settings(BaseModel):
    s3: MinioCreds
    cache_validation_interval: int
    manifest: Dict[str, ManifestEntry]
    engine_settings: Dict[str, Any]
    push_result_validity_time: timedelta = Field(
        default_factory=lambda value: timedelta(seconds=value)
    )


@lru_cache()
def get_settings():
    conf_filename: Optional[str] = os.environ.get(CONF_FILE_TOKEN)
    if conf_filename is None:
        raise Exception('missing "CONF_FILE" file')

    with open(conf_filename, 'r') as f:
        conf: Dict[str, object] = yaml.safe_load(f)
    return Settings(**conf)
