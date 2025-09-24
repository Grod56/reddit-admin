# -*- coding: utf-8 -*
from praw import Reddit


class RedditInterface:
    """
    Class holding tools to interface with the Reddit API
    """

    __prawReddit: Reddit

    def __init__(self, praw_reddit: Reddit):
        self.__prawReddit = praw_reddit

    @property
    def get_praw_reddit(self):
        """Retrieve the interface's PrawReddit instance"""

        return self.__prawReddit
