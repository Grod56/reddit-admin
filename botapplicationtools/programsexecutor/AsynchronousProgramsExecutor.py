# -*- coding: utf-8 -*-

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, List

from plugins \
    import ProgramFactory
from botapplicationtools.programsexecutor.ProgramsExecutor import \
    ProgramsExecutor
from botapplicationtools.programsexecutor.exceptions \
    .ProgramsExecutorInitializationError import \
    ProgramsExecutorInitializationError
from botapplicationtools.programsexecutor.programsexecutortools.RedditInterfaceFactory import RedditInterfaceFactory


class AsynchronousProgramsExecutor(ProgramsExecutor):
    """
    Class responsible for asynchronously executing
    multiple program in different threads
    """

    __executor: ThreadPoolExecutor
    __programFactories: Dict[str, ProgramFactory]
    __executedPrograms: Dict[str, Future]
    __redditInterfaceFactory: RedditInterfaceFactory

    def __init__(
            self,
            programFactories: List[ProgramFactory],
            redditInterfaceFactory: RedditInterfaceFactory,
            executor=ThreadPoolExecutor(),
    ):
        super().__init__("Asynchronous Programs Executor")
        self.__executor = executor
        self.__programFactories = dict(
            map(
                lambda programFactory: (programFactory.getProgramCommand(), programFactory), programFactories
            )
        )
        self.__executedPrograms = {}
        self.__redditInterfaceFactory = redditInterfaceFactory
        self.__initializeProgramsExecutor(programFactories)

    def __initializeProgramsExecutor(self, programFactories):
        """Initialize the program executor"""

        self._programsExecutorLogger.debug('Initializing Programs Executor')

        try: 
            # Retrieving initial program commands
            self._programsExecutorLogger.debug(
                "Retrieving initial program commands"
            )

            # Executing initial program commands 
            self._programsExecutorLogger.debug(
                "Executing initial program commands"
            )
            self.executePrograms(programFactories)
        
        # Handle in case the program executor fails to initialize
        except ProgramsExecutorInitializationError as ex:
            self._programsExecutorLogger.critical(
                "A terminal error occurred while initializing the Programs "
                "Executor. Error(s): " + str(ex)
            )
            raise ex

        self._isProgramsExecutorShutDown = False
        self._programsExecutorLogger.info(
            "Programs Executor initialized"
        )


    def executeProgram(self, programCommand):

        # Confirm if shut down first
        if self._informIfShutDown():
            return

        # Checking if there are duplicate running program
        if programCommand in self.__executedPrograms.keys():
            if not self.__executedPrograms[programCommand].done():
                self._programsExecutorLogger.warning(
                    "Did not run the '{}' program command "
                    "because an identical command is"
                    " still running".format(programCommand)
                )
                return

        # Generating an asynchronous worker thread for the program
        try:
            task = self.__executor.submit(
                self.__processProgram,
                programCommand
            )
        except RuntimeError:
            self._programsExecutorLogger.error(
                "Failed to execute '{}' because the executor is "
                "shutting down or is shut down".format(programCommand)
            )
            return

        try:

            raise task.exception(0.1)

        # Add to running program if task was started successfully
        except concurrent.futures.TimeoutError:

            self.__executedPrograms[programCommand] = task

        # Handle if provided program could not be parsed
        except ValueError as ex:
            self._programsExecutorLogger.error(
                "Did not run the '{}' program command "
                "because there was an error parsing the "
                "program command. Error(s): {}".format(
                    programCommand, str(ex.args)
                )
            )

    def executePrograms(self, programFactories: List[ProgramFactory]):
        """Execute multiple program"""

        # Confirm if shut down first
        if self._informIfShutDown():
            return

        for programFactory in programFactories:
            self.executeProgram(programFactory.getProgramCommand())
            

    def __processProgram(self, programCommand):
        """Synthesize the provided program"""

        programCommandBreakdown = programCommand.split()
        programName = programCommandBreakdown[0]

        try:

            if programName in self.__programFactories.keys():
                redditInterface = self.__redditInterfaceFactory.getRedditInterface()
                self._programsExecutorLogger.info(
                    "Running program '{}'".format(programName)
                )
                self.__programFactories[programName].getProgram(redditInterface).execute()

                # Completion message determination
                if self.isShutDown():
                    self._programsExecutorLogger.info(
                        "{} program instance successfully shut down".format(
                            programName
                        )
                    )
                else:
                    self._programsExecutorLogger.info(
                        "{} program instance completed".format(
                            programName
                        )
                    )
                

            # Raise error if provided program does not exist
            else:
                raise ValueError(
                    "Program '{}' is not recognized".format(programName)
                )

        # Handle if provided program not found
        except ValueError as ex:
            raise ex

        # Handle if unexpected exception crashes a program
        except Exception as ex:
            self._programsExecutorLogger.error(
                "An unexpected error just caused the '{}' "
                "program to crash. Error: {}".format(
                    programName, str(ex.args)
                ), exc_info=True
            )

    def getProgramStatuses(self):
        """Get the executed program statuses"""

        programStatuses = \
            {
                program: ("RUNNING" if not task.done() else "DONE")
                for (program, task) in self.__executedPrograms.items()
            }
        return programStatuses

    def shutDown(self, wait):
        """Shut down the program executor"""

        super().shutDown()
        for programFactory in self.__programFactories.values():
            programFactory.shutDown()
        self.__executor.shutdown(wait)
        self._programsExecutorLogger.info(
            "Programs executor successfully shut down"
        )
