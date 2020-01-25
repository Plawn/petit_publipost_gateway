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


class State:
    def __init__(self):
        self.used_ports: Dict[str, Set[int]] = {}


CommandReturn = Tuple[int, str, str]


def run_command(cmd: str, communicate=True) -> CommandReturn:
    proc = None
    if not communicate:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            universal_newlines=True)
    else:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True)
    std_out, std_err = proc.communicate()
    return proc.returncode, std_out, std_err


def prepare_command(command: str) -> str:
    if command[-1] == '?':
        if command[-2] == '!':
            # if we have "!" -> no communicate
            return command[:-2], True, False
        return command[:-1], True, True
    return command, False, True


def run_script(commands: List[str]) -> None:
    for command in commands:
        command, can_fail, communicate = prepare_command(command)
        code, out, err = run_command(command, communicate)
        if code != 0 and not can_fail:
            raise Exception(f'failed to run command {command} -> {err}')


def start_service(state: State, service_infos: dict, max_wait: timedelta = timedelta(seconds=10)):
    # not using max wait for now, but should timeout on it later
    if BEFORE_SCRIPT_TOKEN in service_infos:
        run_script(service_infos[BEFORE_SCRIPT_TOKEN])

    if RUN_TOKEN in service_infos:
        if PORT_TOKEN in service_infos:
            ports = service_infos[PORT_TOKEN]
            if ports is not None and len(ports) > 0:
                for port in ports:
                    full_host: str = service_infos[HOST_TOKEN]
                    host = full_host.split(':')[0]
                    if host in state.used_ports:
                        s = state.used_ports[host]
                        if port not in s:
                            s.add(port)
                        else:
                            raise Exception(
                                f'Attemtping to start a service on a used port {port} | host = {host}')
                    else:
                        state.used_ports[host] = set([port])

        # if everytthing is good then start
        run_script(service_infos[RUN_TOKEN])

        if AWAIT_FILE_TOKEN in service_infos:
            await_file_exist(set(service_infos[AWAIT_FILE_TOKEN]))

        if AFTER_TOKEN in service_infos:
            run_script(service_infos[AFTER_TOKEN])


def await_file_exist(filenames: Set[str], sleep_precision=1):
    """Awaits that all given files exist then return

    sleep precision can be altered if you want to be faster or slower

    base is 1 sec
    """
    while len(filenames) > 0:
        filenames_to_remove: Set[str] = set()
        for filename in filenames:
            if os.path.exists(filename):
                filenames_to_remove.add(filename)
            else:
                time.sleep(sleep_precision)
        # can't modify the size of filenames while iterating over it
        # so we note what needs to be deleted and do it later on
        for filename in filenames_to_remove:
            filenames.remove(filename)
