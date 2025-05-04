from fastapi import APIRouter
from . import users

router = APIRouter()

router.include_router(users.router, prefix="/v1/users", tags=["users"])

__all__ = ("router",)
