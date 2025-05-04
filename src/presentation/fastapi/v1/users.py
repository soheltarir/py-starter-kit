from uuid import UUID

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.application.services.user_service import UserService
from src.application.dto.user_dto import UserReadDTO, UserCreateDTO
from src.containers import Container
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError

router = APIRouter()


@router.post(
    "/",
    response_model=UserReadDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email and password",
)
@inject
async def register_user(
    data: UserCreateDTO, svc: UserService = Depends(Provide[Container.user_svc])
):
    try:
        return await svc.register(data)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/{user_id}",
    response_model=UserReadDTO,
    summary="Get a user by ID",
    description="Get a user by their ID.",
)
@inject
async def get_user(
    user_id: UUID, svc: UserService = Depends(Provide[Container.user_svc])
):
    """Get a user by ID."""
    try:
        return await svc.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
