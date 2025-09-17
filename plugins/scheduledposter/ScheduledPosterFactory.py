from configparser import ConfigParser

from plugins.databasetools.databaseconnectionfactories.DatabaseConnectionFactory import \
    DatabaseConnectionFactory
from plugins.ProgramFactory import ProgramFactory
from plugins.scheduledposter.tools.CompletedSubmissionDAO import CompletedSubmissionDAO
from plugins.scheduledposter.tools.ScheduledPoster import ScheduledPoster
from plugins.scheduledposter.tools.ScheduledPosterStorage import ScheduledPosterStorage
from plugins.scheduledposter.tools.ScheduledSubmissionDAO import ScheduledSubmissionDAO


class ScheduledPosterFactory(ProgramFactory[ScheduledPoster]):
    """
    Class responsible for running multiple
    Scheduled Poster program instances
    """

    __databaseConnectionFactory: DatabaseConnectionFactory

    def __init__(
            self,
            databaseConnectionFactory: DatabaseConnectionFactory,
            configReader: ConfigParser
    ):
        super().__init__(
            "scheduledposter"
        )
        self.__databaseConnectionFactory = databaseConnectionFactory

    def getProgram(self, redditInterface):

        prawReddit = redditInterface.getPrawReddit

        connection = self.__databaseConnectionFactory.getConnection()
        scheduledPosterStorage = ScheduledPosterStorage(
            ScheduledSubmissionDAO(connection),
            CompletedSubmissionDAO(connection)
        )

        return ScheduledPoster(
            prawReddit,
            scheduledPosterStorage,
            self.isShutDown
        )
