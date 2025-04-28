import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.application.dto.user_dto import UserCreateDTO, UserReadDTO
from src.application.services.user_service import UserService
from src.domain.users.entities import User
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.domain.users.repositories import UserRepository


@pytest.fixture
def mock_repository():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def user_service(mock_repository):
    return UserService(mock_repository)


@pytest.fixture
def user_create_dto():
    return UserCreateDTO(
        email="test@example.com",
        password="secure_password123",
        first_name="John",
        last_name="Doe"
    )


@pytest.fixture
def user_entity():
    user = User(
        email="test@example.com",
        first_name="John",
        last_name="Doe"
    )
    user.set_password("secure_password123")
    return user


async def test_register_success(user_service, mock_repository, user_create_dto, user_entity):
    # Setup
    mock_repository.get_by_email.return_value = None
    mock_repository.save.return_value = user_entity

    # Execute
    result = await user_service.register(user_create_dto)

    # Assert
    assert isinstance(result, UserReadDTO)
    assert result.email == user_create_dto.email
    assert result.first_name == user_create_dto.first_name
    assert result.last_name == user_create_dto.last_name
    mock_repository.get_by_email.assert_called_once_with(user_create_dto.email)
    mock_repository.save.assert_called_once()


async def test_register_user_already_exists(user_service, mock_repository, user_create_dto, user_entity):
    # Setup
    mock_repository.get_by_email.return_value = user_entity

    # Execute & Assert
    with pytest.raises(UserAlreadyExistsError):
        await user_service.register(user_create_dto)


async def test_get_user_success(user_service, mock_repository, user_entity):
    # Setup
    user_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = user_entity

    # Execute
    result = await user_service.get_user(user_id)

    # Assert
    assert isinstance(result, UserReadDTO)
    assert result.email == user_entity.email
    assert result.first_name == user_entity.first_name
    assert result.last_name == user_entity.last_name
    mock_repository.get_by_id.assert_called_once_with(user_id)


async def test_get_user_not_found(user_service, mock_repository):
    # Setup
    user_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    # Execute & Assert
    with pytest.raises(UserNotFoundError):
        await user_service.get_user(user_id) 