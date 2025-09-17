from plugins.scheduledcrossposter.tools.CompletedCrosspostDAO import CompletedCrosspostDAO
from plugins.scheduledcrossposter.tools.ScheduledCrosspostDAO import ScheduledCrosspostDAO


class ScheduledCrossposterStorage:
    """
    Class holding storage DAOs used by the
    Scheduled Crossposter
    """

    __scheduledCrosspostDAO: ScheduledCrosspostDAO
    __completedCrosspostDAO: CompletedCrosspostDAO

    def __init__(
            self,
            scheduledCrosspostDAO: ScheduledCrosspostDAO,
            completedCrosspostDAO: CompletedCrosspostDAO
    ):
        self.__scheduledCrosspostDAO = scheduledCrosspostDAO
        self.__completedCrosspostDAO = completedCrosspostDAO

    @property
    def getScheduledCrosspostDAO(self):
        return self.__scheduledCrosspostDAO

    @property
    def getCompletedCrosspostDAO(self):
        return self.__completedCrosspostDAO
