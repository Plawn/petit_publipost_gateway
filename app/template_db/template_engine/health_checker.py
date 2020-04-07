from typing import *
import threading
import logging


def check_live_func() -> bool:
    """Can raise Exception
    """
    pass


def configure_func() -> None:
    """Can raise Exception
    """
    pass


base_check_up_time = 30

class FailedToConfigure(Exception):
    pass

class HealthChecker:
    """
    This class is useful when using another service which is not syncronyzed with this one
    Using the check_live function and the configure function this will try to keep the service up and running

    :param name: Name of the service
    :param check_live: function () -> bool used to check if the service is live
    :param configure: function () -> None used to configure the service if down
    :param check_up_time: time between checks, default 30 seconds
    """
    def __init__(self, name: str, check_live: check_live_func, configure: configure_func, post_configuration:configure_func=None,mount=True,check_up_time=base_check_up_time):
        self.name = name
        self.event = threading.Event()
        self.check_live = check_live
        self.configure = configure
        self.check_up_time = check_up_time
        self.post_configuration = post_configuration
        self.up = False
        self.stopped = False
        self.thread: threading.Thread = None
        self.configuring = True
        self.init()
        if mount:
            self.__mount()

    def init(self) -> None:
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def __mount(self) -> None:
        try :
            self.configuring = True
            self.configure()
            self.up = True
        except:
            self.up = False
        finally:
            self.configuring = False

    def is_up(self) -> bool:
        return self.up

    def is_configuring(self) -> bool:
        return self.configuring


    def run(self):
        while not self.stopped:
            self.event.wait(base_check_up_time)
            try:
                if not self.check_live():
                    self.up = False
                    logging.warning(
                        f'service is not configured -> trying to configure | {self.name}')
                    self.configuring = True
                    self.configure()
                    self.up = True
                    logging.info(f'service successfully configured | {self.name}')
                    if self.post_configuration:
                        self.post_configuration()
                else:
                    self.up = True
                    logging.info(f'service is up | {self.name}')
            except FailedToConfigure:
                self.up = False
                logging.error(f'failed to configure service | {self.name}')
            except Exception as e:
                self.up = False
                logging.error(f'service is down | {self.name}')
            finally:
                self.configuring = False

    def stop(self):
        self.stopped = True
        self.event.set()
