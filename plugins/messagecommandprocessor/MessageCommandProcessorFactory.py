import json
from configparser import ConfigParser
from typing import List

from plugins.databasetools.databaseconnectionfactories.DatabaseConnectionFactory import \
    DatabaseConnectionFactory
from plugins.ProgramFactory import ProgramFactory
from plugins.messagecommandprocessor.tools.MessageCommandProcessor import MessageCommandProcessor
from plugins.messagecommandprocessor.tools.messagecommandprocessortools.CommandProcessorFactory import CommandProcessorFactory
from plugins.messagecommandprocessor.tools.messagecommandprocessortools.testfeaturetools.FeatureTesterDAO import FeatureTesterDAO


class MessageCommandProcessorFactory(ProgramFactory[MessageCommandProcessor]):
    """
    Class responsible for running multiple
    Message Command Processor instances
    """

    __commands: List[str]
    __databaseConnectionFactory: DatabaseConnectionFactory

    def __init__(
            self,
            databaseConnectionFactory: DatabaseConnectionFactory,
            configReader: ConfigParser
    ):
        super().__init__(
            "msgcommandprocessor"
        )
        self.__databaseConnectionFactory = databaseConnectionFactory
        self.__initializeProgramRunner(configReader)

    def __initializeProgramRunner(self, configReader: ConfigParser):
        """Initialize the Message Command Processor Factory"""

        # Retrieving initial variable values from the config. reader
        section = "MessageCommandProcessor"
        commands = json.loads(
            configReader.get(
                section, "commands"
            )
        )

        # Instance variable initialization
        self.__commands = commands

    def getProgram(self, redditInterface):

        connection = self.__databaseConnectionFactory.getConnection()
        commandProcessors = CommandProcessorFactory.getCommandProcessors(
            self.__commands, connection
        )
        prawReddit = redditInterface.getPrawReddit
        featureTesterDAO = FeatureTesterDAO(connection)

        return MessageCommandProcessor(
            commandProcessors,
            prawReddit,
            featureTesterDAO,
            self.isShutDown
        )
