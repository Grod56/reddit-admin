import praw

from botapplicationtools.general.botcredentials.BotCredentials import BotCredentials
from botapplicationtools.general.botcredentials.InvalidBotCredentialsError import InvalidBotCredentialsError
from botapplicationtools.general.RedditInterface import RedditInterface


class RedditInterfaceFactory:
    """Factory for RedditInterface objects"""

    __botCredentials: BotCredentials

    def __init__(
            self,
            botCredentials: BotCredentials
    ):
        prawReddit = praw.Reddit(
            user_agent=botCredentials.getUserAgent,
            client_id=botCredentials.getClientId,
            client_secret=botCredentials.getClientSecret,
            username=botCredentials.getUsername,
            password=botCredentials.getPassword
        )
        if not self.__authenticated(prawReddit):
            raise InvalidBotCredentialsError

        self.__botCredentials = botCredentials

    @staticmethod
    def __authenticated(prawRedditInstance: praw.Reddit) -> bool:
        """
        Convenience method to authenticate bot credentials
        provided to Reddit instance
        """

        return not prawRedditInstance.read_only

    def getRedditInterface(self) -> RedditInterface:
        """Retrieve new Reddit Interface"""

        botCredentials = self.__botCredentials
        prawReddit = praw.Reddit(
            user_agent=botCredentials.getUserAgent,
            client_id=botCredentials.getClientId,
            client_secret=botCredentials.getClientSecret,
            username=botCredentials.getUsername,
            password=botCredentials.getPassword
        )
        return RedditInterface(prawReddit)
