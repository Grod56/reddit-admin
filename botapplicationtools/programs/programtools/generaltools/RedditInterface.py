# -*- coding: utf-8 -*
from praw import Reddit

class RedditInterface:
    """
    Class holding tools to interface with the Reddit API
    """

    __prawReddit: Reddit

    def __init__(self, prawReddit):
        self.__prawReddit = prawReddit

    @property
    def getPrawReddit(self):
        """Retrieve the interface's PrawReddit instance"""

        return self.__prawReddit
