from ..utility.exceptions import InitializationError


class PluginsExecutorInitializationError(InitializationError):
    """
    Class to encapsulate an error in the initialization
    of a Plugins Executor module
    """

    def __init__(self, *args):
        super().__init__(*args)
