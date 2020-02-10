from typing import Dict, Set, Tuple, List
import subprocess
import os
import time
import Fancy_term as term
from datetime import timedelta
from .template_engine import from_strings_to_dict

RUN_TOKEN = 'script'
PORT_TOKEN = 'ports'
HOST_TOKEN = 'host'
BEFORE_SCRIPT_TOKEN = 'before_script'
AWAIT_FILE_TOKEN = 'await_file'
AFTER_TOKEN = 'after_script'

# not used for now
AWAIT_FILE_EVENT = 'await_event'


success_printer = term.Smart_print(term.Style(
    color=term.colors.green, substyles=[term.substyles.bold]))
error_printer = term.Smart_print(term.Style(
    color=term.colors.red, substyles=[term.substyles.bold]))
info_printer = term.Smart_print(term.Style(
    color=term.colors.yellow, substyles=[term.substyles.bold]))
