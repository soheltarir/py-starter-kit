import uuid

import structlog
from taskiq import AsyncTaskiqDecoratedTask, AsyncBroker

from src.domain.background_task.repositories import BackgroundTaskProcessor
from src.domain.background_task.value_objects import BackgroundTaskPayload
from src.presentation.taskiq.tasks.registry import TASK_REGISTRY

logger = structlog.get_logger()


class TaskiqProcessor(BackgroundTaskProcessor):
    def __init__(self, broker: AsyncBroker):
        self.broker = broker
        self.registered_tasks: dict[str, AsyncTaskiqDecoratedTask] = {}

    async def register_tasks(self) -> None:
        logger.info("Registering tasks...")
        for task_name, fn in TASK_REGISTRY.items():
            self.registered_tasks[task_name] = self.broker.register_task(fn, task_name=task_name)
            logger.info(f"Registered task '{task_name}'")

    async def execute_task(self, task_name: str, payload: BackgroundTaskPayload) -> str:
        # Fetch task from registry
        task = self.registered_tasks.get(task_name)
        if not task:
            raise ValueError(f"Task '{task_name}' is not registered.")

        task = await task.kicker().with_labels(task_id=str(uuid.uuid4())).kiq(payload=payload)
        return task.task_id
