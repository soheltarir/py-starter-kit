import uuid
from typing import Optional

import bcrypt
from pydantic import BaseModel, Field, EmailStr, PrivateAttr, computed_field
from src.domain.users.value_objects import UserAddress


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), salt=bcrypt.gensalt())


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    first_name: str
    last_name: str
    email: EmailStr
    password_hash: Optional[bytes] = Field(exclude=True, default=None)
    addresses: list[UserAddress] = []

    def set_password(self, password: str):
        pwd_hash = bcrypt.hashpw(password.encode("utf-8"), salt=bcrypt.gensalt())
        self.password_hash = pwd_hash

    def check_password(self, password: str) -> bool:
        if self.password_hash is None:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash)
