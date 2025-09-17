from configparser import ConfigParser

from plugins.databasetools.databaseconnectionfactories.DatabaseConnectionFactory import \
    DatabaseConnectionFactory
from plugins.ProgramFactory import ProgramFactory
from plugins.adminupdater.tools.AdminUpdateDAO import AdminUpdateDAO
from plugins.adminupdater.tools.AdminUpdater import AdminUpdater
from plugins.adminupdater.tools.FormattingTools import FormattingTools
from plugins.adminupdater.tools.RedditTools import RedditTools


class AdminUpdaterFactory(ProgramFactory[AdminUpdater]):
    """
    Class responsible for running multiple
    Admin Updater instances
    """

    __databaseConnectionFactory: DatabaseConnectionFactory

    def __init__(
            self,
            databaseConnectionFactory: DatabaseConnectionFactory,
            configReader: ConfigParser
    ):
        super().__init__(
            "adminupdater"
        )
        self.__databaseConnectionFactory = databaseConnectionFactory
        self.__initializeProgramRunner(configReader)

    def __initializeProgramRunner(self, configReader: ConfigParser):

        # Retrieving values from config. file
        section = "AdminUpdater"
        subredditName = configReader.get(
            section, "subredditName"
        )
        wikiPageName = configReader.get(
            section, "wikiPageName"
        )
        widgetID = configReader.get(
            section, "widgetID"
        )
        wikiUpdateFormat = configReader.get(
            section, "wikiUpdateFormat"
        )
        widgetUpdateFormat = configReader.get(
            section, "widgetUpdateFormat"
        )
        dateFormat = configReader.get(
            section, "dateFormat"
        )
        maxWidgetLines = configReader.getint(
            section, "maxWidgetLines"
        )
        widgetFooter = configReader.get(
            section, "widgetFooter"
        )

        # Instance variable processing and assignment
        self.__subredditName = subredditName
        self.__wikiPageName = wikiPageName
        self.__widgetID = widgetID
        self.__formattingTools = FormattingTools(
            bytes(
                wikiUpdateFormat,
                "utf-8"
            ).decode("unicode_escape"),
            bytes(
                widgetUpdateFormat,
                "utf-8"
            ).decode("unicode_escape"),
            dateFormat,
            maxWidgetLines,
            bytes(
                widgetFooter,
                "utf-8"
            ).decode("unicode_escape"),
        )

    def getProgram(self, redditInterface) -> AdminUpdater:
        connection = self.__databaseConnectionFactory.getConnection()
        # Setting up program parameters
        subreddit = redditInterface.getPrawReddit.subreddit(
            self.__subredditName
        )
        redditTools = RedditTools(
            subreddit,
            self.__wikiPageName,
            self.__widgetID
        )

        # Executing the program
        return AdminUpdater(
            AdminUpdateDAO(connection),
            redditTools,
            self.__formattingTools,
            self.isShutDown
        )