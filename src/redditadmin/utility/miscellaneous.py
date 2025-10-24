import praw


class InitializationError(Exception):
    """
    Raised when the initialization of a module fails
    """

    def __init__(self, *args):
        super().__init__(self, args)


class BotInitializationError(InitializationError):
    """
    Raised when the initialization of a bot module fails
    """

    def __init__(self, *args):
        super().__init__(*args)


def is_reddit_authenticated(praw_reddit_instance: praw.Reddit) -> bool:
    """
    Convenience method to authenticate bot credentials
    provided to Reddit instance
    """

    return not praw_reddit_instance.read_only
