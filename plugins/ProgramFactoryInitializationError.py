# -*- coding: utf-8 -*

from botapplicationtools.general.exceptions.InitializationError import InitializationError


class ProgramFactoryInitializationError(InitializationError):
    """
    Class to encapsulate an error in the initialization
    of a program factory module
    """

    def __init__(self, *args):
        super().__init__(*args)
