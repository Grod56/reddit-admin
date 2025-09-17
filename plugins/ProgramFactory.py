# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from botapplicationtools.general.RedditInterface import RedditInterface
from botapplicationtools.program.Program import Program


T = TypeVar("T", bound=Program)

class ProgramFactory(Generic[T], ABC):
    """
    Class responsible for running multiple
    instances of a specific program
    """

    _programCommand: str
    _programFactoryLogger: logging.Logger
    _isProgramFactoryShutDown: bool

    def __init__(
            self,
            programCommand: str,
    ):
        self._programCommand = programCommand
        self._programFactoryLogger = logging.getLogger(
            programCommand
        )
        self._isProgramFactoryShutDown = False

    @abstractmethod
    def getProgram(self, redditInterface: RedditInterface) -> T:
        """Get new program instance"""

        raise NotImplementedError
    
    def getProgramCommand(self) -> str:
        """Get the program command string"""
        return self._programCommand

    def isShutDown(self) -> bool:
        """Check if Program Runner is shut down"""
        return self._isProgramFactoryShutDown

    def shutDown(self):
        """Shut down the Program Runner"""
        self._isProgramFactoryShutDown = True

    def __eq__(self, value) -> bool:
        return isinstance(value, ProgramFactory) and \
            self.getProgramCommand() == value.getProgramCommand()