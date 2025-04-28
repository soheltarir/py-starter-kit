import uuid
from abc import ABC, abstractmethod

from pydantic import EmailStr

from src.domain.users.entities import User


class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User:
        pass

    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> User:
        pass
