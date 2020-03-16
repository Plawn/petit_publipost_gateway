from dataclasses import dataclass
from typing import List
from .minio_creds import MinioCreds

@dataclass
class ConfigOptions:
    env: dict
    minio: MinioCreds


@dataclass
class RenderOptions:
    transform_data: bool
    compile_options: List[str]
    push_result: bool