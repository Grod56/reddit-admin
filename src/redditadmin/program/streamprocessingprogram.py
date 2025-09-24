from abc import ABC, abstractmethod
from typing import Generator, Callable

from praw.models import Subreddit, ListingGenerator
from praw.models.util import stream_generator

from .program import RecurringProgram
from ..utility.decorators import consumestransientapierrors


class StreamFactory(ABC):
    """
    Class responsible for producing
    new Reddit Object streams at request
    """

    @abstractmethod
    def get_new_stream(self) -> Generator:
        """Produce new stream"""

        raise NotImplementedError()


class StreamProcessingProgram(RecurringProgram, ABC):
    """
    Class encapsulating a stream processing
    program
    """

    def __init__(
            self,
            stream_factory: StreamFactory,
            stop_condition: Callable[..., bool],
            program_name: str
    ):
        super().__init__(program_name, stop_condition)
        self.__streamFactory = stream_factory

    @consumestransientapierrors
    def execute(self, *args, **kwargs):

        # In case we somehow run out of
        # new items in the stream (IYKYK)
        while not self._stopCondition():

            stream = self.__streamFactory.get_new_stream()

            # "New item listener" loop
            for streamItem in stream:

                # Handle "pause" token
                if streamItem is None:

                    # Exit the loop if stop condition satisfied
                    if self._stopCondition():
                        break

                    self._run_pause_handler()
                    continue

                self._run_nature_core(streamItem)

    def _run_pause_handler(self, *args):
        """Execute when stream is paused"""
        pass


class SubmissionStreamFactory(StreamFactory):
    """
    Class responsible for producing
    new Submission streams at request
    """

    def __init__(
            self,
            subreddit: Subreddit,
            pause_after: int = 0,
            skip_existing: bool = False
    ):
        super().__init__()
        self.__subreddit = subreddit
        self.__pause_after = pause_after
        self.__skip_existing = skip_existing

    def get_new_stream(self) -> Generator:
        return self.__subreddit.stream.submissions(
            pause_after=self.__pause_after,
            skip_existing=self.__skip_existing
        )


class CommentStreamFactory(StreamFactory):
    """
    Class responsible for producing
    new Comment streams at request
    """

    def __init__(
            self,
            subreddit: Subreddit,
            pause_after: int = 0,
            skip_existing: bool = False
    ):
        super().__init__()
        self.__subreddit = subreddit
        self.__pause_after = pause_after
        self.__skip_existing = skip_existing

    def get_new_stream(self) -> Generator:
        return self.__subreddit.stream.comments(
            pause_after=self.__pause_after,
            skip_existing=self.__skip_existing
        )


class CustomStreamFactory(StreamFactory):
    """
    Class responsible for producing new
    stream of custom Reddit objects according to
    the provided Listing Generator
    """

    def __init__(
            self,
            listing_generator_callback: Callable[..., ListingGenerator],
            pause_after: int = 0,
            skip_existing: bool = False
    ):
        super().__init__()
        self.__listingGeneratorCallback = listing_generator_callback
        self.__pause_after = pause_after
        self.__skip_existing = skip_existing

    def get_new_stream(self) -> Generator:
        return stream_generator(
            self.__listingGeneratorCallback,
            pause_after=self.__pause_after,
            skip_existing=self.__skip_existing
        )
