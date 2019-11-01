from typing import Dict, Set
import subprocess
import os
import time
import Fancy_term as term
from datetime import timedelta

RUN_TOKEN = 'script'
PORT_TOKEN = 'ports'
HOST_TOKEN = 'host'
BEFORE_SCRIPT_TOKEN = 'before_script'
AWAIT_FILE_TOKEN = 'await_file'


# not used for now
AWAIT_FILE_EVENT = 'await_event'


success_printer = term.Smart_print(term.Style(
    color=term.colors.green, substyles=[term.substyles.bold]))
error_printer = term.Smart_print(term.Style(
    color=term.colors.red, substyles=[term.substyles.bold]))


class State:
    def __init__(self):
        self.used_ports: Dict[str, Set[int]] = {}


def start_service(state: State, service_infos: dict, max_wait: timedelta = timedelta(seconds = 10)):
    # not using max wait for now, but should timeout on it later
    if BEFORE_SCRIPT_TOKEN in service_infos:
        for command in service_infos[BEFORE_SCRIPT_TOKEN]:
            subprocess.call(command, shell=True)
    if RUN_TOKEN in service_infos:
        ports = service_infos[PORT_TOKEN]
        if ports is not None and len(ports) > 0:
            for port in ports:
                host = service_infos[HOST_TOKEN]
                if host in state.used_ports:
                    s = state.used_ports[host]
                    if port not in s:
                        s.add(port)
                    else:
                        raise Exception(
                            f'Attemtping to start a service on a used port {port}')
                else:
                    state.used_ports[host] = set([port])

        # if everytthing is good then start
        for command in service_infos[RUN_TOKEN]:
            subprocess.call(command, shell=True)

        if AWAIT_FILE_TOKEN in service_infos:
            await_file_exist(set(service_infos[AWAIT_FILE_TOKEN]))


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
