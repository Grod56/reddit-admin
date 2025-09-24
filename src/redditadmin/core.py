import logging
import os
import signal
import sys
import time
from abc import ABC, abstractmethod
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import List

from src.redditadmin.utility.botcredentials import BotCredentials
from src.redditadmin.utility.exceptions import BotInitializationError, InvalidBotCredentialsError
from src.redditadmin.plugin.asynchronouspluginsexecutor import AsynchronousPluginsExecutor
from src.redditadmin.plugin.exceptions import PluginsExecutorInitializationError
from src.redditadmin.plugin.plugin import Plugin
from src.redditadmin.plugin.pluginsexecutor import PluginsExecutor
from src.redditadmin.plugin.redditinterfacefactory import RedditInterfaceFactory


class RedditAdmin(ABC):
    """Type encapsulating a RedditAdmin instance"""

    def __init__(self, *args):
        pass

    @abstractmethod
    def run(self, bot_credentials: BotCredentials, listen: bool = False):
        """Run the bot"""

        raise NotImplementedError

    @abstractmethod
    def stop(self):
        """Shutdown the bot"""

        raise NotImplementedError


class RedditAdminImplementation(RedditAdmin):
    """Reddit Admin Bot"""

    __plugins: List[Plugin]
    __pluginsExecutor: PluginsExecutor
    __mainLogger: logging.Logger
    __defaultConsoleLoggingLevel: int

    __RESOURCES_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'resources'
    )

    # Bot initialization commands
    # -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------

    def __init__(self, plugins: List[Plugin]):
        super().__init__(self)
        self.__plugins = plugins

    def __initialize_logging(self, log_file_name: str):
        """Initialize the bot's logging apparatus"""

        # Disabling any 3rd party loggers
        for _ in logging.root.manager.loggerDict:
            logging.getLogger(_).setLevel(logging.CRITICAL)

        # Initializing the root logger
        logging.basicConfig(level=logging.DEBUG)
        root_logger = logging.getLogger()

        # Initializing the core bot application logger
        self.__mainLogger = logging.getLogger(__name__)

        # Clearing any existing log handlers for program loggers
        for logger in [root_logger, self.__mainLogger]:
            if len(logger.handlers):
                logger.handlers.clear()

        # Setting up log handlers
        log_file_handler = TimedRotatingFileHandler(
            filename=log_file_name,
            when='D',
            utc=True
        )
        console_handler = logging.StreamHandler()
        log_file_handler.set_name('log_file')
        console_handler.set_name('console')
        log_file_handler.setFormatter(
            logging.Formatter(
                '[%(asctime)s] %(name)-16s : '
                '%(levelname)-8s - %(message)s'
            )
        )
        console_handler.setFormatter(
            logging.Formatter(
                '%(name)-16s : %(message)s'
            )
        )
        log_file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)

        # Adding the handlers to the root logger
        root_logger.addHandler(log_file_handler)
        root_logger.addHandler(console_handler)

        # Setting the default console logging level global variable
        self.__defaultConsoleLoggingLevel = console_handler.level

    def ___get_new_bot_credentials(self) -> BotCredentials:
        """Convenience method to retrieve bot credentials from user input"""

        try:
            # Prompt for new valid credentials
            while True:

                # Pause console logging while listening for input
                self.__pause_console_logging()

                user_agent = input("Enter User Agent: ")
                client_id = input("Enter Client ID: ")
                client_secret = input("Enter Client Secret: ")
                username = input("Enter Username: ")
                password = input("Enter Password: ")

                # Resume console logging
                self.__resume_console_logging()

                return BotCredentials(
                    user_agent, client_id,
                    client_secret, username,
                    password
                )

        # Handle if listening interrupted
        except (KeyboardInterrupt, EOFError) as ex:
            self.__resume_console_logging()
            raise ex

    def __get_reddit_interface_factory(self, bot_credentials: BotCredentials) \
            -> RedditInterfaceFactory:
        """ Initialize Reddit Interface Factory"""

        # Attempting to retrieve a valid RedditInterfaceFactory
        # instance from provided credentials

        try:
            reddit_interface_factory = RedditInterfaceFactory(
                bot_credentials
            )
        # Handle if credential authentication fails
        except InvalidBotCredentialsError:
            self.__mainLogger.error(
                "The provided credentials are invalid. "
                "Please enter new valid credentials"
            )
            try:
                new_bot_credentials = self.___get_new_bot_credentials()
                reddit_interface_factory = self.__get_reddit_interface_factory(new_bot_credentials)
            except (KeyboardInterrupt, EOFError):
                raise BotInitializationError(
                    "Retrieval of bot credentials from user input "
                    "aborted"
                )

        return reddit_interface_factory

    def __initialize_plugins_executor(self, bot_credentials: BotCredentials) \
            -> PluginsExecutor:
        """Initialize the Plugins Executor"""

        # Initializing the Plugins Executor

        reddit_interface_factory = self.__get_reddit_interface_factory(bot_credentials)

        try:
            plugins_executor = AsynchronousPluginsExecutor(
                plugins=self.__plugins,
                reddit_interface_factory=reddit_interface_factory
            )

        # Handle if there is an error initializing the Programs Executor
        except PluginsExecutorInitializationError as ex:
            raise BotInitializationError(
                "An error occurred while initializing "
                "the Programs Executor.", ex
            )

        return plugins_executor

    def __initialize_bot(self, bot_credentials: BotCredentials):
        """Initialize the bot"""

        log_file = Path(os.path.join(
            self.__RESOURCES_PATH, 'logs', 'reddit-admin.log'
        ))
        log_file.parent.mkdir(exist_ok=True, parents=True)

        # Setting up logging apparatus
        self.__initialize_logging(str(log_file.resolve()))

        self.__mainLogger.info("Initializing the bot")

        try:

            # Initializing the Programs Executor
            self.__pluginsExecutor = self.__initialize_plugins_executor(
                bot_credentials
            )

            # -------------------------------------------------------------------------------

        # Handle if an initialization error occurs
        except BotInitializationError as er:
            self.__mainLogger.critical(
                "A fatal error occurred during the "
                "bot's initialization. The application "
                "will now exit. Error(s): " + str(er),
                exc_info=True
            )
            sys.exit(2)  # TODO: May need future cleaning up

        self.__mainLogger.info("Bot successfully initialized")

    # -------------------------------------------------------------------------------

    # Bot runtime commands
    # -------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------

    def __pause_console_logging(self):
        """Pause console logging across entire application"""

        for handler in logging.getLogger().handlers:
            if handler.name == "console":
                handler.setLevel(logging.CRITICAL)
                return
        self.__mainLogger.warning(
            "Failed to pause logging because "
            "the console logger was not found"
        )

    def __resume_console_logging(self):
        """Resume console logging across entire application"""

        for handler in logging.getLogger().handlers:
            if handler.name == "console":
                handler.setLevel(self.__defaultConsoleLoggingLevel)
                return
        self.__mainLogger.warning(
            "Failed to resume logging because "
            "the console logger was not found"
        )

    def __start_command_listener(self):
        """Start the bot command listener"""

        try:
            while not self.__is_bot_shut_down():
                # Pause console logging while bot is
                # listening for commands
                self.__pause_console_logging()

                command = input('Enter bot command: ')

                # Resume console logging once command
                # entered
                self.__resume_console_logging()

                self.__process_bot_command(command)

        except BaseException as ex:
            self.__resume_console_logging()
            raise ex

    def __process_bot_command(self, command: str):
        """Process a bot command"""

        # For blank command
        if command == '' or command == '\n':
            return

        # For program command
        elif command.startswith('run '):
            self.__pluginsExecutor.execute_program(command.split('run ', 1)[1])

        # For program status request
        elif command == 'status':

            print('\nPrograms status:')

            # Printing all program statuses
            for _program, status in self.__pluginsExecutor \
                    .get_program_statuses() \
                    .items():
                print('{}\t\t: {}'.format(
                    _program, status
                ))
            print()

        # For shutdown command
        elif (
                command == 'shutdown' or
                command == 'quit' or
                command == 'exit'
        ):
            self.__shut_down_bot()

        else:
            self.__mainLogger.debug(
                "'{}' is not a valid bot command".format(command)
            )

    @staticmethod
    def __kill_bot():
        """Forcefully shut down the bot"""

        # Windows kill command
        if (
                sys.platform.startswith('win32') or
                sys.platform.startswith('cygwin')
        ):
            os.kill(os.getpid(), signal.CTRL_BREAK_EVENT)

        # Linux kill command
        os.kill(os.getpid(), signal.SIGKILL)

    def __shut_down_bot(self, wait=True, shutdown_exit_code=0):
        """Shut down the bot"""

        if wait:
            self.__mainLogger.info(
                'Shutting down the bot. Please wait a bit while the '
                'remaining tasks ({}) are being finished off'.format(
                    ", ".join(
                        {
                            _program: status
                            for (_program, status) in self.__pluginsExecutor
                            .get_program_statuses()
                            .items()
                            if status != "DONE"
                        }.keys()
                    )
                )
            )
            try:
                self.__pluginsExecutor.shut_down(True)
                self.__mainLogger.info('Bot successfully shut down')
                if shutdown_exit_code != 0:
                    sys.exit(shutdown_exit_code)

            # Handle keyboard interrupt midway through graceful shutdown
            except KeyboardInterrupt:

                self.__mainLogger.warning(
                    'Graceful shutdown aborted.'
                )
                self.__pluginsExecutor.shut_down(False)
                self.__mainLogger.info('Bot shut down')

                # Killing the process (only way to essentially stop all threads)
                self.__kill_bot()

        else:
            self.__pluginsExecutor.shut_down(False)
            self.__mainLogger.info('Bot shut down')

            self.__kill_bot()

    def __is_bot_shut_down(self):
        """Check if bot is shutdown"""

        return self.__pluginsExecutor and self.__pluginsExecutor.is_shut_down()

    def __start_bot(self, bot_credentials: BotCredentials, listen: bool):
        """Start up the bot"""

        # Initializing the bot
        self.__initialize_bot(bot_credentials)
        self.__mainLogger.info('The bot is now running')

        try:
            if listen:
                self.__start_command_listener()

        # Handle forced shutdown request
        except (KeyboardInterrupt, EOFError):
            self.__mainLogger.warning(
                'Forced bot shutdown requested. Please wait a bit wait while '
                'a graceful shutdown is attempted or press '
                'Ctrl+C to exit immediately'
            )
            self.__shut_down_bot(True, 1)

        # Handle unknown exception while bot is running
        except BaseException as ex:
            self.__mainLogger.critical(
                "A fatal error just occurred while the bot was "
                "running. Please wait a bit wait while "
                "a graceful shutdown is attempted or press "
                "Ctrl+C to exit immediately: " + str(ex.args), exc_info=True
            )
            self.__shut_down_bot(True, 2)

    def run(self, bot_credentials: BotCredentials, listen: bool = False):

        # Setting up interrupt signal handlers
        signal.signal(signal.SIGINT, signal.default_int_handler)
        signal.signal(signal.SIGTERM, signal.default_int_handler)

        # Start bot
        self.__start_bot(bot_credentials, listen)

        try:
            # Wait for tasks to complete before shutdown
            while True:
                if not (
                    "RUNNING" in self.__pluginsExecutor
                    .get_program_statuses().values()
                ):
                    break
                time.sleep(1)
        # Handle shutdown by Keyboard interrupt
        except KeyboardInterrupt:
            pass
        finally:
            # Shut bot down if not already
            if not self.__is_bot_shut_down():
                self.__shut_down_bot()

    def stop(self):

        self.__shut_down_bot()

    # -------------------------------------------------------------------------------


def get_reddit_admin(plugins: List[Plugin]) -> RedditAdmin:
    """Get a Reddit Admin instance"""

    return RedditAdminImplementation(plugins=plugins)
