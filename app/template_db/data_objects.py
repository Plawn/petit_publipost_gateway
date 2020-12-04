from dataclasses import dataclass
from typing import List

from .templator import CompileOptions


@dataclass
class RenderOptions:
    push_result: bool
    transform_data: bool
    compile_options: List[CompileOptions]


@dataclass
class ManifestEntry:
    export_name: str
    output_bucket: str
