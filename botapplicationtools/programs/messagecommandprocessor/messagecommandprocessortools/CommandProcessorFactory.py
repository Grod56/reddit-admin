from typing import List, Dict

from botapplicationtools.programs.messagecommandprocessor.commandprocessors.CommandProcessor import CommandProcessor



class CommandProcessorFactory:
    """Class responsible for generating CommandProcessors"""

    @classmethod
    def getCommandProcessor(cls, command: str, databaseConnection) \
            -> CommandProcessor:
        """Retrieve the command processor for the corresponding command"""

        # Handle for unknown command
        return None

    @classmethod
    def getCommandProcessors(cls, commands: List[str], databaseConnection) \
            -> Dict[str, CommandProcessor]:
        """Retrieve the command processors for the provided commands"""

        commandProcessors = {}
        for command in commands:
            # Return the command processor for each
            # provided command
            commandProcessor = cls.getCommandProcessor(
                command, databaseConnection
            )
            if commandProcessor is not None:
                # Append to collection of command processors
                # if command processor returned
                commandProcessors[command] = commandProcessor

        return commandProcessors
