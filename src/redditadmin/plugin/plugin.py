import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from ..program.program import Program
from ..utility.redditinterface import RedditInterface
from ..utility.exceptions import InitializationError

T = TypeVar("T", bound=Program)


class Plugin(Generic[T], ABC):
    """
    Class responsible for generating multiple
    instances of a specific program
    """

    _programCommand: str
    _pluginLogger: logging.Logger
    _isPluginShutDown: bool

    def __init__(
            self,
            program_command: str,
    ):
        self._programCommand = program_command
        self._pluginLogger = logging.getLogger(
            program_command
        )
        self._isPluginShutDown = False

    @abstractmethod
    def get_program(self, reddit_interface: RedditInterface) -> T:
        """Get new program instance"""

        raise NotImplementedError

    def get_program_command(self) -> str:
        """Get the program command string"""
        return self._programCommand

    def is_shut_down(self) -> bool:
        """Check if plugin is shut down"""
        return self._isPluginShutDown

    def shut_down(self):
        """Shut down the plugin"""
        self._isPluginShutDown = True

    def __eq__(self, value) -> bool:
        return isinstance(value, Plugin) and \
               self.get_program_command() == value.get_program_command()


class PluginInitializationError(InitializationError):
    """
    Class to encapsulate an error in the initialization
    of a plugin module
    """

    def __init__(self, *args):
        super().__init__(*args)
