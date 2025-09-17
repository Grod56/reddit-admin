import logging
import os
import signal
import sys
import time
from logging.handlers import TimedRotatingFileHandler

from botapplicationtools.general.botcredentials.InvalidBotCredentialsError import InvalidBotCredentialsError
from botapplicationtools.general.exceptions.BotInitializationError import \
    BotInitializationError
from botapplicationtools.programsexecutor.AsynchronousProgramsExecutor \
    import AsynchronousProgramsExecutor
from botapplicationtools.programsexecutor.ProgramsExecutor import ProgramsExecutor
from botapplicationtools.programsexecutor.exceptions \
    .ProgramsExecutorInitializationError import ProgramsExecutorInitializationError
from botapplicationtools.programsexecutor.programsexecutortools.RedditInterfaceFactory \
    import RedditInterfaceFactory

from botapplicationtools.general.botcredentials.BotCredentials import BotCredentials

class RedditAdmin:
    """Reddit Admin Bot"""

    global __mainLogger
    global __defaultConsoleLoggingLevel
    global __programsExecutor
    global __RESOURCES_PATH
    global __resumeConsoleLogging
    global __pauseConsoleLogging
    global __initializeLogging
    global __initializeBot
    global __initializeProgramsExecutor
    global __getRedditInterfaceFactory
    global ___getNewBotCredentials
    global __processBotCommand
    global __killBot
    global __startCommandListener
    global __shutDownBot
    global __isBotShutDown
    global __startBot

    __RESOURCES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
        'resources'
    )

    # Bot initialization commands
    # -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------

    def __initializeLogging(logFileName: str):
        """Initialize the bot's logging apparatus"""

        global __mainLogger
        global __defaultConsoleLoggingLevel

        # Disabling any 3rd party loggers
        for _ in logging.root.manager.loggerDict:
            logging.getLogger(_).setLevel(logging.CRITICAL)

        # Initializing the root logger
        logging.basicConfig(level=logging.DEBUG)
        rootLogger = logging.getLogger()

        # Initializing the main bot application logger
        __mainLogger = logging.getLogger(__name__)

        # Clearing any existing log handlers for program loggers
        for logger in [rootLogger, __mainLogger]:
            if len(logger.handlers):
                logger.handlers.clear()

        # Setting up log handlers
        logFileHandler = TimedRotatingFileHandler(
            filename=logFileName,
            when='D',
            utc=True
        )
        consoleHandler = logging.StreamHandler()
        logFileHandler.set_name('log_file')
        consoleHandler.set_name('console')
        logFileHandler.setFormatter(
            logging.Formatter(
                '[%(asctime)s] %(name)-16s : '
                '%(levelname)-8s - %(message)s'
            )
        )
        consoleHandler.setFormatter(
            logging.Formatter(
                '%(name)-16s : %(message)s'
            )
        )
        logFileHandler.setLevel(logging.DEBUG)
        consoleHandler.setLevel(logging.DEBUG)

        # Adding the handlers to the root logger
        rootLogger.addHandler(logFileHandler)
        rootLogger.addHandler(consoleHandler)

        # Setting the default console logging level global variable
        __defaultConsoleLoggingLevel = consoleHandler.level


    def ___getNewBotCredentials() -> BotCredentials:
        """Convenience method to retrieve bot credentials from user input"""

        try:
            # Prompt for new valid credentials
            while True:

                # Pause console logging while listening for input
                __pauseConsoleLogging()

                user_agent = input("Enter User Agent: ")
                client_id = input("Enter Client ID: ")
                client_secret = input("Enter Client Secret: ")
                username = input("Enter Username: ")
                password = input("Enter Password: ")

                # Resume console logging
                __resumeConsoleLogging()

                return BotCredentials(
                    user_agent, client_id,
                    client_secret, username,
                    password
                )

        # Handle if listening interrupted
        except (KeyboardInterrupt, EOFError) as ex:
            __resumeConsoleLogging()
            raise ex


    def __getRedditInterfaceFactory(botCredentials) \
            -> RedditInterfaceFactory:
        """ Initialize Reddit Interface Factory"""

        # Attempting to retrieve a valid RedditInterfaceFactory
        # instance from provided credentials

        try:
            redditInterfaceFactory = RedditInterfaceFactory(
                botCredentials
            )
        # Handle if credential authentication fails
        except InvalidBotCredentialsError:
            __mainLogger.error(
                "The provided credentials are invalid. "
                "Please enter new valid credentials"
            )
            try:
                redditInterfaceFactory = __getRedditInterfaceFactory(
                    ___getNewBotCredentials()
                )
            except (KeyboardInterrupt, EOFError):
                raise BotInitializationError(
                    "Retrieval of bot credentials from user input "
                    "aborted"
                )

        return redditInterfaceFactory


    def __initializeProgramsExecutor(botCredentials, programFactories) \
            -> ProgramsExecutor:
        """Initialize the Programs Executor"""

        # Initializing the Programs Executor

        redditInterfaceFactory = RedditInterfaceFactory(botCredentials)

        try:
            programsExecutor = AsynchronousProgramsExecutor(
                programFactories=programFactories,
                redditInterfaceFactory=redditInterfaceFactory
            )

        # Handle if there is an error initializing the Programs Executor
        except ProgramsExecutorInitializationError as ex:
            raise BotInitializationError(
                "An error occurred while initializing "
                "the Programs Executor.", ex
            )

        return programsExecutor


    def __initializeBot(botCredentials, programFactories):
        """Initialize the bot"""

        global __programsExecutor

        # Setting up logging apparatus
        __initializeLogging(os.path.join(
            __RESOURCES_PATH, 'logs', 'reddit-admin.log'
        ))

        __mainLogger.info("Initializing the bot")

        try:

            # Initializing the Programs Executor
            __programsExecutor = __initializeProgramsExecutor(
                botCredentials, programFactories
            )

            # -------------------------------------------------------------------------------

        # Handle if an initialization error occurs
        except BotInitializationError as er:
            __mainLogger.critical(
                "A fatal error occurred during the "
                "bot's initialization. The application "
                "will now exit. Error(s): " + str(er),
                exc_info=True
            )
            sys.exit(2)  # TODO: May need future cleaning up

        __mainLogger.info("Bot successfully initialized")

    # -------------------------------------------------------------------------------


    # Bot runtime commands
    # -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------

    def __pauseConsoleLogging():
        """Pause console logging across entire application"""

        for handler in logging.getLogger().handlers:
            if handler.name == "console":
                handler.setLevel(logging.CRITICAL)
                return
        __mainLogger.warning(
            "Failed to pause logging because "
            "the console logger was not found"
        )

    def __resumeConsoleLogging():
        """Resume console logging across entire application"""

        for handler in logging.getLogger().handlers:
            if handler.name == "console":
                handler.setLevel(__defaultConsoleLoggingLevel)
                return
        __mainLogger.warning(
            "Failed to resume logging because "
            "the console logger was not found"
        )


    def __startCommandListener():
        """Start the bot command listener"""

        try:
            while not __isBotShutDown():
                # Pause console logging while bot is
                # listening for commands
                __pauseConsoleLogging()

                command = input('Enter bot command: ')

                # Resume console logging once command
                # entered
                __resumeConsoleLogging()

                __processBotCommand(command)

        except BaseException as ex:
            __resumeConsoleLogging()
            raise ex


    def __processBotCommand(command):
        """Process a bot command"""

        # For blank command
        if command == '' or command == '\n':
            return

        # For program command
        elif command.startswith('run '):
            __programsExecutor.executeProgram(command.split('run ', 1)[1])

        # For program status request
        elif command == 'status':

            print('\nPrograms status:')

            # Printing all program statuses
            for program, status in __programsExecutor \
                    .getProgramStatuses() \
                    .items():
                print('{}\t\t: {}'.format(
                    program, status
                ))
            print()

        # For shutdown command
        elif (
                command == 'shutdown' or
                command == 'quit' or
                command == 'exit'
        ):
            __shutDownBot()

        else:
            __mainLogger.debug(
                "'{}' is not a valid bot command".format(command)
            )


    def __killBot():
        """Forcefully shut down the bot"""

        # Windows kill command
        if (
                sys.platform.startswith('win32') or
                sys.platform.startswith('cygwin')
        ):
            os.kill(os.getpid(), signal.CTRL_BREAK_EVENT)

        # Linux kill command
        os.kill(os.getpid(), signal.SIGKILL)


    def __shutDownBot(wait=True, shutdownExitCode=0):
        """Shut down the bot"""

        if wait:
            __mainLogger.info(
                'Shutting down the bot. Please wait a bit while the '
                'remaining tasks ({}) are being finished off'.format(
                    ", ".join(
                        {
                            program: status
                            for (program, status) in __programsExecutor
                            .getProgramStatuses()
                            .items()
                            if status != "DONE"
                        }.keys()
                    )
                )
            )
            try:
                __programsExecutor.shutDown(True)
                __mainLogger.info('Bot successfully shut down')
                if shutdownExitCode != 0:
                    sys.exit(shutdownExitCode)

            # Handle keyboard interrupt midway through graceful shutdown
            except KeyboardInterrupt:

                __mainLogger.warning(
                    'Graceful shutdown aborted.'
                )
                __programsExecutor.shutDown(False)
                __mainLogger.info('Bot shut down')

                # Killing the process (only way to essentially stop all threads)
                __killBot()

        else:
            __programsExecutor.shutDown(False)
            __mainLogger.info('Bot shut down')

            __killBot()


    def __isBotShutDown():
        """Check if bot is shutdown"""

        return __programsExecutor and __programsExecutor.isShutDown()


    def __startBot(botCredentials, programFactories, args=None):
        """Start up the bot"""

        # Initializing the bot
        if args is None:
            args = []
        __initializeBot(botCredentials, programFactories)

        try:
            # Retrieve additional bot instructions if present
            if len(args) > 0:

                botCommand = ''

                # Retrieve and execute bot command if present
                if len(args) > 2:
                    botCommand = " ".join(args[2:])

                __processBotCommand(botCommand)
                __mainLogger.info('The bot is now running')

                try:
                    # Command listening setting
                    listen = int(args[1]) if len(args) > 1 else None

                    # Check if command listening is set
                    if listen:
                        __startCommandListener()

                # Handle if provided listen argument is invalid
                except ValueError:
                    __mainLogger.error(
                        "The provided 'listen' argument, \"{}\", is invalid. "
                        "The bot will therefore shutdown once all of its tasks"
                        " are completed.".format(args[1])
                    )

            else:
                # Default to listening for commands if
                # no additional instructions specified
                __mainLogger.info('The bot is now running')
                __startCommandListener()

        # Handle forced shutdown request
        except (KeyboardInterrupt, EOFError):
            __mainLogger.warning(
                'Forced bot shutdown requested. Please wait a bit wait while '
                'a graceful shutdown is attempted or press '
                'Ctrl+C to exit immediately'
            )
            __shutDownBot(True, 1)

        # Handle unknown exception while bot is running
        except BaseException as ex:
            __mainLogger.critical(
                "A fatal error just occurred while the bot was "
                "running. Please wait a bit wait while "
                "a graceful shutdown is attempted or press "
                "Ctrl+C to exit immediately: " + ex.args, exc_info=True
            )
            __shutDownBot(True, 2)

    def run(botCredentials: BotCredentials, programFactories):
        """Run the bot"""

        # Setting up interrupt signal handlers
        signal.signal(signal.SIGINT, signal.default_int_handler)
        signal.signal(signal.SIGTERM, signal.default_int_handler)

        # Start bot
        if len(sys.argv) == 1:
            __startBot(botCredentials, programFactories)
        else:
            __startBot(botCredentials, programFactories, sys.argv)

        try:
            # Wait for tasks to complete before shutdown
            while True:
                if not (
                    "RUNNING" in __programsExecutor
                    .getProgramStatuses().values()
                ):
                    break
                time.sleep(1)
        # Handle shutdown by Keyboard interrupt
        except KeyboardInterrupt:
            pass
        finally:
            # Shut bot down if not already
            if not __isBotShutDown():
                __shutDownBot()

    

    def stop():
        """Shutdown the bot"""

        __shutDownBot()

    # -------------------------------------------------------------------------------