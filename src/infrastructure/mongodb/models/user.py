import uuid
from typing import Optional, Annotated
from uuid import UUID

from beanie import Document, Indexed
from pydantic import Field, EmailStr

from src.domain.users.value_objects import UserAddress
from src.utils.datetime_utils import DateTimeMixin


class UserDocument(DateTimeMixin, Document):
    id: UUID = Field(default_factory=uuid.uuid4)
    email: Annotated[EmailStr, Indexed(unique=True)]
    password_hash: Optional[bytes]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    addresses: list[UserAddress] = []
