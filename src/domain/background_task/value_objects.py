import abc

from pydantic import BaseModel


class BackgroundTaskPayload(BaseModel, abc.ABC):
    """
    Represents the payload for a background task.
    All payloads sent to background task processors must inherit from this class.

    Example:
        class EmailTaskPayload(BackgroundTaskPayload):
            subject: str
            recipients: list[str]
            cc: list[str] = []
    """
    pass
