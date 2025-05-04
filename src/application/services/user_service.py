import uuid

import structlog

from src.application.dto.user_dto import UserCreateDTO, UserReadDTO
from src.domain.background_task.adaptor import BackgroundTaskProcessor, BackgroundTask
from src.domain.users.entities import User
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.domain.users.repositories import UserRepository

logger = structlog.get_logger()


class WelcomeEmailTask(BackgroundTask):
    task_name = "welcome_email"

    user_id: uuid.UUID

    def logic(self):
        logger.info("Sending welcome email", user_id=self.user_id)


class UserService:
    def __init__(
        self, user_repository: UserRepository, task_processor: BackgroundTaskProcessor
    ):
        self.user_repository = user_repository
        self.task_processor = task_processor

    async def register(self, user_dto: UserCreateDTO) -> UserReadDTO:
        # Check if a user already exists
        existing_user = await self.user_repository.get_by_email(user_dto.email)
        if existing_user:
            raise UserAlreadyExistsError(user_dto.email)

        # Create a user entity
        user = User(
            email=user_dto.email,
            first_name=user_dto.first_name or "",
            last_name=user_dto.last_name or "",
            addresses=user_dto.addresses,
        )
        user.set_password(user_dto.password)

        # Save user
        created_user = await self.user_repository.save(user)

        # Send a welcome email
        await self.task_processor.execute_task(
            WelcomeEmailTask(user_id=created_user.id)
        )

        # Return user DTO
        return UserReadDTO(
            id=created_user.id,
            email=created_user.email,
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            addresses=created_user.addresses,
        )

    async def get_user(self, user_id: uuid.UUID) -> UserReadDTO:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return UserReadDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            addresses=user.addresses,
        )
