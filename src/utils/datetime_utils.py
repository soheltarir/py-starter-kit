from datetime import datetime, UTC
from typing import Annotated

from pydantic import Field, ConfigDict, AfterValidator


def _get_utc_now() -> datetime:
    return datetime.now(UTC)


def _set_updated_at(_: datetime) -> datetime:
    return _get_utc_now()


class DateTimeMixin:
    """
    Created and updated at mixin that automatically
    updates the updated_at field
    """

    created_at: datetime = Field(default_factory=_get_utc_now)
    updated_at: Annotated[datetime, AfterValidator(_set_updated_at)] = Field(
        default_factory=_get_utc_now
    )

    model_config = ConfigDict(validate_assignment=True)


__all__ = ("DateTimeMixin",)
