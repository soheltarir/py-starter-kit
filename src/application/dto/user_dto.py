from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from src.domain.users.value_objects import UserAddress


class UserCreateDTO(BaseModel):
    """Data transfer object for user creation."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    addresses: list[UserAddress] = []


class UserReadDTO(BaseModel):
    """Data transfer object for user reading."""

    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    addresses: list[UserAddress] = []
