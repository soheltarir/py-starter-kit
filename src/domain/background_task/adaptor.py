import abc
import inspect
from typing import ClassVar, Type, TypeVar

from pydantic import BaseModel


class BackgroundTask(BaseModel, abc.ABC):
    task_name: ClassVar[str]
    enabled: ClassVar[bool] = True

    @abc.abstractmethod
    async def logic(self):
        pass


def get_background_task_implementations() -> list[Type[BackgroundTask]]:
    # Get direct subclasses
    all_subclasses = BackgroundTask.__subclasses__()

    concrete_subclasses = [cls for cls in all_subclasses if not inspect.isabstract(cls)]

    return concrete_subclasses


T = TypeVar("T", bound="BackgroundTaskProcessor")


class BackgroundTaskProcessor(abc.ABC):
    """
    Abstract base class for background task processing.
    Use the create() factory method to instantiate implementations of this class.
    """

    def __init__(self):
        """
        Initialize a new BackgroundTaskProcessor.
        Note: This constructor does not perform any asynchronous operations.
        Use the create() factory method for creating and initializing instances.
        """
        pass

    @classmethod
    async def create(cls: Type[T], tasks: list[Type[BackgroundTask]]) -> T:
        """
        Factory method to create and initialize a BackgroundTaskProcessor.

        :return: An initialized instance of BackgroundTaskProcessor
        """
        instance = cls()
        await instance.register_tasks(tasks)
        return instance

    @staticmethod
    def get_get_background_tasks() -> list[Type[BackgroundTask]]:
        return get_background_task_implementations()

    @abc.abstractmethod
    async def register_tasks(self, tasks: list[Type[BackgroundTask]]) -> None:
        """
        Registers a list of background task adaptors for asynchronous processing.

        :param tasks: A list of tasks
        """
        pass

    @abc.abstractmethod
    async def execute_task(self, task: BackgroundTask) -> str:
        """
        :return: The task id for a background task to be used for tracking.
        """
        pass
