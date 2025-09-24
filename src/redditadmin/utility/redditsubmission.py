from praw.models import Submission


class RedditSubmission:
    """
    Class encapsulating a submission
    """

    __submissionId: str

    def __init__(self, submission_id):
        self.__submissionId = submission_id

    @property
    def get_submission_id(self):
        return self.__submissionId

    @classmethod
    def get_submission_from_id(
            cls, submission_id: str
    ):
        """
        Returns a SimpleSubmission object from
        the provided submissionId
        """
        return RedditSubmission(submission_id)

    @classmethod
    def get_submission_from_praw_submission(
            cls, praw_submission: Submission
    ):
        """
        Returns a SimpleSubmission object from
        the provided PRAW submission
        """
        return RedditSubmission(praw_submission.id)
