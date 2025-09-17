from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser

from plugins.databasetools.databaseconnectionfactories.DatabaseConnectionFactory import \
    DatabaseConnectionFactory
from plugins.ProgramFactory import ProgramFactory
from plugins.scheduledcrossposter.tools.CompletedCrosspostDAO import CompletedCrosspostDAO
from plugins.scheduledcrossposter.tools.ScheduledCrosspostDAO import ScheduledCrosspostDAO
from plugins.scheduledcrossposter.tools.ScheduledCrossposter import ScheduledCrossposter
from plugins.scheduledcrossposter.tools.ScheduledCrossposterStorage import ScheduledCrossposterStorage
from botapplicationtools.program.streamprocessingprogram.SubmissionStreamFactory import SubmissionStreamFactory


class ScheduledCrossposterFactory(ProgramFactory[ScheduledCrossposter]):
    """
    Class responsible for running multiple
    Scheduled Crossposter program instances
    """

    __subreddit: str

    __databaseConnectionFactory: DatabaseConnectionFactory

    def __init__(
            self,
            databaseConnectionFactory: DatabaseConnectionFactory,
            configReader: ConfigParser
    ):
        super().__init__(
            "scheduledcrossposter"
        )
        self.__databaseConnectionFactory = databaseConnectionFactory
        self.__initializeProgramRunner(configReader)

    def __initializeProgramRunner(self, configReader: ConfigParser):
        """Initialize the Scheduled Crossposter Factory"""

        section = "ScheduledCrossposter"
        subreddit = configReader.get(
            section, "subreddit"
        )

        # Initialization of instance variables
        self.__subreddit = subreddit

    def getProgram(self, redditInterface):

        prawReddit = redditInterface.getPrawReddit

        submissionStreamFactory = SubmissionStreamFactory(
            prawReddit.subreddit(
                self.__subreddit
            )
        )

        connection = self.__databaseConnectionFactory.getConnection()    
        scheduledCrossposterStorage = ScheduledCrossposterStorage(
            ScheduledCrosspostDAO(connection),
            CompletedCrosspostDAO(connection)
        )

        return ScheduledCrossposter(
            submissionStreamFactory,
            scheduledCrossposterStorage,
            ThreadPoolExecutor(),
            self.isShutDown
        )
