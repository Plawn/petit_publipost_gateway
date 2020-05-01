import logging
import threading
from typing import *
import uuid


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
    """The AutoConfigurer could'nt complete the configuration of the service
    """
    pass


class AutoConfigurer:
    """
    This class is useful when using another service which is not syncronyzed with this one
    Using the check_live function and the configure function this will try to keep the service up and running

    :param name: Name of the service
    :param check_live: function () -> bool used to check if the service is live
    :param configure: function () -> None used to configure the service if down
    :param check_up_time: time between checks, default 30 seconds
    """

    def __init__(self, name: str, check_live: check_live_func, configure: configure_func, logger: logging.Logger,
                 post_configuration: configure_func = None,  mount=True, check_up_time=base_check_up_time):
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
        self.logger = logger

        self.full_reload_scheduled = False

        self.post_conf_hooks = {}
        self.pre_conf_hooks = {}
        self.on_check_hooks = {}

        self.force_configure_lock = threading.Lock()
        self.force_configure_queue = []

        self.__init()

        if mount:
            self.__mount()

    def __init(self) -> None:
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def __mount(self) -> None:
        try:
            self.configuring = True
            self.configure()
            self.up = True
        except:
            self.up = False
        finally:
            self.configuring = False

    def is_up(self) -> bool:
        """Returns wether the service is up or not
        """
        return self.up

    def is_configuring(self) -> bool:
        """Returns wether the service is being configured or not
        """
        return self.configuring

    def force_configure(self, schedule_full: bool) -> None:
        """
        force trigger a check of the current configuration

        If the service is already being configured then it will wait for 
        the end of the configuration without actually triggering another configuration
        """
        if not self.configuring:
            # if we are not configuring we acquire the lock
            # then we configure
            with self.force_configure_lock:
                self.logger.warning(
                    f'service is not configured -> trying to configure | {self.name}')
                self.configuring = True
                self.configure()
                self.up = True
                self.logger.info(
                    f'service successfully configured | {self.name}')
                self.configuring = False
                self.full_reload_scheduled = schedule_full
        else:
            # if we are already configuring it means that the precedent block is being executed already
            # which means that we don't need to configure
            # but we need to check if the precendent configuration was successful
            with self.force_configure_lock:
                if not self.up:
                    raise FailedToConfigure(f'{self}')

    def run(self):
        while not self.stopped:
            self.event.wait(base_check_up_time)
            self.event.clear()
            try:
                if not self.check_live() or self.full_reload_scheduled:
                    self.up = False
                    self.logger.warning(
                        f'service is not configured -> trying to configure | {self.name}')
                    self.configuring = True

                    # to bind other actions cleanly
                    self.__run_pre_hooks()

                    self.configure()
                    self.up = True
                    self.logger.info(
                        f'service successfully configured | {self.name}')
                    if self.post_configuration:
                        self.post_configuration()
                        self.full_reload_scheduled = False

                    # to bind other actions cleanly
                    self.__run_post_hooks()
                else:
                    self.up = True
                    self.logger.info(f'service is up | {self.name}')
                    self.logger.info(f'running check hooks')
                    self.__run_on_check_hooks()
            except FailedToConfigure:
                self.up = False
                self.logger.error(f'failed to configure service | {self.name}')
            except Exception as e:
                self.up = False
                self.logger.error(f'service is down | {self.name}')
            finally:
                self.configuring = False

    def stop(self):
        """To stop the worker
        """
        self.stopped = True
        self.event.set()

    def __run_hooks(self, hooks: dict):
        for name, hook in hooks.items():
            try:
                hook()
            except Exception as e:
                self.logger.warning(f'Hook {name} failed | {e}')

    def __run_pre_hooks(self):
        self.__run_hooks(self.pre_conf_hooks)

    def __run_post_hooks(self):
        self.__run_hooks(self.post_conf_hooks)

    def __run_on_check_hooks(self):
        self.__run_hooks(self.on_check_hooks)

    def register_post_hook(self, name: str, func: configure_func):
        """Registers a hook to be executed just after the configuration
        """
        self.post_conf_hooks[name] = func

    def register_pre_hook(self, name: str, func: configure_func):
        """Registers a hook to be executed just before the configuration
        """
        self.pre_conf_hooks[name] = func

    def register_on_check_hook(self, name: str, func: configure_func):
        """Registers a hook to be executed just after the `up_check` returns `True`
        """
        self.on_check_hooks[name] = func
