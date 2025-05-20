import abc
from typing import TypeVar

from src.domain.background_task.value_objects import BackgroundTaskPayload

T = TypeVar("T", bound="BackgroundTaskProcessor")


class BackgroundTaskProcessor(abc.ABC):
    """
    Abstract base class for background task processing.
    """

    @abc.abstractmethod
    async def register_tasks(self):
        pass

    @abc.abstractmethod
    async def execute_task(
            self,
            task_name: str,
            payload: BackgroundTaskPayload
    ) -> str:
        """
        Abstract method that executes a specific background task identified by its name and utilizes
        the provided payload to perform that task. This method should be implemented in subclasses,
        and it should detail how each particular task is executed based on unique requirements.
        The method is expected to return the result of the task execution as a string.

        :param task_name: The unique identifier or name of the specific task to be executed.
        :param payload: An instance of BackgroundTaskPayload containing the data or parameters
            needed to execute the specified task.
        :return: A string representing the result or outcome of the executed task.
        """
        pass
