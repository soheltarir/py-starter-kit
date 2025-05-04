from celery import Celery

from src.domain.background_task.adaptor import BackgroundTaskProcessor, BackgroundTask


class CeleryTaskProcessor(BackgroundTaskProcessor):
    def __init__(self, broker: str, app_name: str):
        super().__init__()

        self.celery_app = Celery(
            app_name,
            broker=broker,
        )

        # Optional configurations
        self.celery_app.conf.update(
            task_serializer="pickle",
            accept_content=["application/json", "application/x-python-serialize"],
            result_accept_content=[
                "application/json",
                "application/x-python-serialize",
            ],
            result_serializer="pickle",
            timezone="UTC",
            enable_utc=True,
        )

    @classmethod
    async def create(
        cls, tasks: list[BackgroundTask], broker: str = None, app_name: str = None
    ):
        """
        Create and initialize a new CeleryTaskProcessor.

        :param tasks: List of background tasks to register
        :param broker: Celery broker URL
        :param app_name: Name of the Celery application
        :return: An initialized CeleryTaskProcessor
        """
        instance = cls(broker, app_name)
        await instance.register_tasks(tasks)
        return instance

    async def register_tasks(self, tasks: list[BackgroundTask]) -> None:
        for task in tasks:
            if not task.enabled:
                continue
            # Validate if the task name is set or not
            if not hasattr(task, "task_name") or not task.task_name:
                raise ValueError(f"Task name is not set for task {task}")
            fn = getattr(task, "logic")
            self.celery_app.task(fn, name=task.task_name, pydantic=True)

    async def execute_task(self, task: BackgroundTask) -> str:
        task_id = self.celery_app.send_task(task.task_name, args=(task,)).id
        return task_id
