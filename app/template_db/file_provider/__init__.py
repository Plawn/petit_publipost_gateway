from .interface import FileProvider, Path
from dataclasses import dataclass

@dataclass
class PullInformations:
    remote: Path
    file_provider: FileProvider