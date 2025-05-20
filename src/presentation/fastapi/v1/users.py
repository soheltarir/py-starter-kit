from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from kink import di, inject
from starlette import status

from src.application.dto.user_dto import UserReadDTO, UserCreateDTO
from src.application.services.user_service import UserService
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError

router = APIRouter()

def get_user_service():
    return di[UserService]


@router.post(
    "/",
    response_model=UserReadDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email and password",
)
@inject
async def register_user(
    data: UserCreateDTO, svc: UserService = Depends(get_user_service)
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
    user_id: UUID, svc: UserService = Depends(get_user_service)
):
    """Get a user by ID."""
    try:
        return await svc.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
