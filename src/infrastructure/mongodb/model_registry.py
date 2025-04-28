from beanie import Document

from src.infrastructure.mongodb.models.user import UserDocument

MONGODB_MODELS: list[type[Document]] = [UserDocument]

__all__ = ("MONGODB_MODELS",)
