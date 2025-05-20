from typing import Callable

from src.presentation.taskiq.tasks.user import send_welcome_email_task

TASK_REGISTRY: dict[str, Callable] = {
    "send_welcome_email": send_welcome_email_task
}

__all__ = ("TASK_REGISTRY",)
