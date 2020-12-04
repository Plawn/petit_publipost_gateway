from dataclasses import dataclass
from typing import List
from .minio_creds import MinioCreds

@dataclass
class ConfigOptions:
    env: dict
    minio: MinioCreds


@dataclass
class RenderOptions:
    push_result: bool
    transform_data: bool
    compile_options: List[str]

@dataclass
class ManifestEntry:
    export_name: str
    output_bucket: str