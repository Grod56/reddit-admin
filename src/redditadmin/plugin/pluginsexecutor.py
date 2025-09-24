# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Dict


class PluginsExecutor(ABC):
    """
    Class responsible for executing plugins
    """

    _isPluginsExecutorShutDown: bool
    _pluginsExecutorLogger: logging.Logger

    def __init__(self, plugins_executor_name: str):
        self._pluginsExecutorLogger = logging.getLogger(
            plugins_executor_name
        )
        self._isPluginsExecutorShutDown = False

    @abstractmethod
    def execute_program(self, program_command):
        """Execute the provided program command"""

        raise NotImplementedError

    @abstractmethod
    def get_program_statuses(self) -> Dict[str, str]:
        """Get the executed program statuses"""

        raise NotImplementedError

    def shut_down(self, *args):
        """Shut down the plugins executor"""

        self._isPluginsExecutorShutDown = True

    def is_shut_down(self) -> bool:
        """Check if the Plugins Executor is shut down"""

        return self._isPluginsExecutorShutDown

    def _inform_if_shut_down(self):
        """
        Convenience method to check shutdown status and log
        if plugins executor is shut down
        """

        if self._isPluginsExecutorShutDown:
            self._pluginsExecutorLogger.warning(
                "The plugins executor cannot execute any more program "
                "after it has been shut down"
            )
