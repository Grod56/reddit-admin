import logging
import time
from abc import ABC, abstractmethod
from typing import Callable


class Program(ABC):
    """Class representing a simple program"""

    def __init__(self, program_name: str):
        self._programLogger = logging.getLogger(
            program_name
        )        

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the program"""

        raise NotImplementedError()


class RecurringProgram(Program, ABC):
    """Class encapsulating a looping program type"""

    def __init__(
            self,
            program_name: str,
            stop_condition: Callable[..., bool],
            cooldown: float = 0
    ):
        super().__init__(program_name)
        self._stopCondition = stop_condition
        self._cooldown = cooldown

    def execute(self, *args, **kwargs):
        while not self._stopCondition():
            self._run_nature_core(*args, **kwargs)
            if self._cooldown and self._cooldown > 0:
                time.sleep(self._cooldown)

    @abstractmethod
    def _run_nature_core(self, *args, **kwargs):
        """Run core program"""

        raise NotImplementedError()