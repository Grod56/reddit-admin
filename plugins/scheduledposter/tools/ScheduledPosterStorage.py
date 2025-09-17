from plugins.scheduledposter.tools.CompletedSubmissionDAO import CompletedSubmissionDAO
from plugins.scheduledposter.tools.ScheduledSubmissionDAO import ScheduledSubmissionDAO


class ScheduledPosterStorage:
    """
    Class holding storage DAOs used by the
    Scheduled Poster
    """

    __scheduledSubmissionDAO: ScheduledSubmissionDAO
    __completedSubmissionDAO: CompletedSubmissionDAO

    def __init__(
            self,
            scheduledSubmissionDAO: ScheduledSubmissionDAO,
            completedSubmissionDAO: CompletedSubmissionDAO
    ):

        self.__scheduledSubmissionDAO = scheduledSubmissionDAO
        self.__completedSubmissionDAO = completedSubmissionDAO

    @property
    def getScheduledSubmissionDAO(self):
        return self.__scheduledSubmissionDAO

    @property
    def getCompletedSubmissionDAO(self):
        return self.__completedSubmissionDAO
