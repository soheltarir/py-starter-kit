import uuid
from typing import Optional

from pydantic import EmailStr

from src.domain.users.entities import User
from src.domain.users.repositories import UserRepository
from src.infrastructure.mongodb.models.user import UserDocument


class BeanieUserRepository(UserRepository):
    async def save(self, user: User) -> User:
        user_document = UserDocument(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=True,
            email=user.email,
            password_hash=user.password_hash,
            addresses=user.addresses,
        )
        await UserDocument.insert_one(user_document)
        return self._document_to_entity(user_document)

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        user_document = await UserDocument.find_one(UserDocument.id == user_id)
        if not user_document:
            return None
        return self._document_to_entity(user_document)

    async def get_by_email(self, email: EmailStr) -> Optional[User]:
        user_document = await UserDocument.find_one(UserDocument.email == email)
        if not user_document:
            return None
        return self._document_to_entity(user_document)

    @staticmethod
    def _document_to_entity(document: UserDocument) -> User:
        """Convert a Beanie document to a domain entity."""
        return User(
            id=document.id,
            email=document.email,
            first_name=document.first_name or "",
            last_name=document.last_name or "",
            addresses=document.addresses,
            password_hash=document.password_hash,
        )
