"""
Module providing various utility methods
for submissions and comments
"""
from typing import List, Union

from praw import Reddit
from praw.models import Submission, Comment, Subreddit

# TODO: Unpushshift
def retrieveSubmissionsFromSubreddit(
        reddit: Reddit,
        subredditName: str,
        fromTime: str,
        filters: List[str]
) -> List[Submission]:
    """
    Retrieves all submissions from a given subreddit
    after the provided time containing only filtered info
    """
    # return list(
    #     reddit.subreddit.search_submissions(
    #         subreddit=subredditName,
    #         after=fromTime,
    #         filter=filters
    #     )
    # )
    raise NotImplementedError


def retrieveSelectSubmissions(
        prawReddit: Reddit,
        submissionIds: List[str]
) -> List[Submission]:
    """
    Retrieves submissions with the given
    submissionIds
    """

    submissions = []

    for submissionId in submissionIds:
        submissions.append(
            prawReddit.submission(submissionId)
        )

    return submissions


def isRemoved(
        contribution: Union[Submission, Comment]
) -> bool:
    """
    Checks if provided comment or
    submission is removed
    """

    try:
        author = contribution.author
    except AttributeError:
        author = None
    return author is None or author == '[Deleted]' or \
        contribution.banned_by is not None
