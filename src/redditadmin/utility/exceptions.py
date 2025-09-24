class InitializationError(Exception):
    """
    Class to encapsulate an error in the
    initialization of a module
    """

    def __init__(self, *args):
        super().__init__(self, args)


class BotInitializationError(InitializationError):
    """
    Class to encapsulate an error in the
    initialization of a bot module
    """

    def __init__(self, *args):
        super().__init__(*args)


class InvalidBotCredentialsError(Exception):
    """
    Class encapsulating an exception raised
    when provided bot credentials are invalid
    """

    def __init__(self, *args):
        super().__init__(self, args)