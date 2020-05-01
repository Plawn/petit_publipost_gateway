import os
import subprocess
import time
from datetime import timedelta
from typing import Dict, List, Set, Tuple

import Fancy_term as term
import yaml

from .template_engine import from_strings_to_dict

RUN_TOKEN = 'script'
PORT_TOKEN = 'ports'
HOST_TOKEN = 'host'


success_printer = term.Smart_print(term.Style(
    color=term.colors.green, substyles=[term.substyles.bold]))
error_printer = term.Smart_print(term.Style(
    color=term.colors.red, substyles=[term.substyles.bold]))
info_printer = term.Smart_print(term.Style(
    color=term.colors.yellow, substyles=[term.substyles.bold]))


def conf_loader(filename:str):
    with open(filename, 'r') as f:
        conf: Dict[str, object] = yaml.safe_load(f)
    return conf
