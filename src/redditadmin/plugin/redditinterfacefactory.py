import praw

from ..utility.botcredentials import BotCredentials
from ..utility.exceptions import InvalidBotCredentialsError
from ..utility.redditinterface import RedditInterface


class RedditInterfaceFactory:
    """Factory for RedditInterface objects"""

    __botCredentials: BotCredentials

    def __init__(
            self,
            bot_credentials: BotCredentials
    ):
        praw_reddit = praw.Reddit(
            user_agent=bot_credentials.get_user_agent,
            client_id=bot_credentials.get_client_id,
            client_secret=bot_credentials.get_client_secret,
            username=bot_credentials.getusername,
            password=bot_credentials.get_password
        )
        if not self.__authenticated(praw_reddit):
            raise InvalidBotCredentialsError

        self.__botCredentials = bot_credentials

    @staticmethod
    def __authenticated(praw_reddit_instance: praw.Reddit) -> bool:
        """
        Convenience method to authenticate bot credentials
        provided to Reddit instance
        """

        return not praw_reddit_instance.read_only

    def get_reddit_interface(self) -> RedditInterface:
        """Retrieve new Reddit Interface"""

        bot_credentials = self.__botCredentials
        praw_reddit = praw.Reddit(
            user_agent=bot_credentials.get_user_agent,
            client_id=bot_credentials.get_client_id,
            client_secret=bot_credentials.get_client_secret,
            username=bot_credentials.getusername,
            password=bot_credentials.get_password
        )
        return RedditInterface(praw_reddit)
