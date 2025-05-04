import uuid
from unittest.mock import AsyncMock

import pytest

from src.application.dto.user_dto import UserCreateDTO, UserReadDTO
from src.application.services.user_service import UserService, WelcomeEmailTask
from src.domain.background_task.adaptor import BackgroundTaskProcessor
from src.domain.users.entities import User, UserAddress
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.domain.users.repositories import UserRepository
from src.domain.users.value_objects import AddressType


@pytest.fixture
def mock_repository():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_task_processor():
    return AsyncMock(spec=BackgroundTaskProcessor)


@pytest.fixture
def user_service(mock_repository, mock_task_processor):
    mock_task_processor.execute_task.return_value = "task-123"
    return UserService(mock_repository, mock_task_processor)


@pytest.fixture
def user_create_dto():
    return UserCreateDTO(
        email="test@example.com",
        password="secure_password123",
        first_name="John",
        last_name="Doe"
    )


@pytest.fixture
def address_dto():
    return UserAddress(
        type=AddressType.Home,
        street="123 Main St",
        city="New York",
        state="NY",
        zipcode=10001,
        country="USA"
    )


@pytest.fixture
def user_create_dto_with_address(user_create_dto, address_dto):
    user_create_dto.addresses = [address_dto]
    return user_create_dto


@pytest.fixture
def user_entity():
    user = User(
        email="test@example.com",
        first_name="John",
        last_name="Doe"
    )
    user.set_password("secure_password123")
    return user


@pytest.fixture
def user_entity_with_address(user_entity):
    address = UserAddress(
        type=AddressType.Home,
        street="123 Main St",
        city="New York",
        state="NY",
        zipcode=10001,
        country="USA"
    )
    user_entity.addresses.append(address)
    return user_entity


@pytest.mark.asyncio
async def test_register_success(user_service, mock_repository, mock_task_processor, user_create_dto, user_entity):
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
    
    # Verify welcome email task was triggered with the correct user ID
    mock_task_processor.execute_task.assert_called_once()
    task_call = mock_task_processor.execute_task.call_args[0][0]
    assert isinstance(task_call, WelcomeEmailTask)
    assert task_call.user_id == user_entity.id


@pytest.mark.asyncio
async def test_register_with_address(user_service, mock_repository, user_create_dto_with_address, user_entity_with_address):
    # Setup
    mock_repository.get_by_email.return_value = None
    mock_repository.save.return_value = user_entity_with_address

    # Execute
    result = await user_service.register(user_create_dto_with_address)

    # Assert
    assert isinstance(result, UserReadDTO)
    assert result.email == user_create_dto_with_address.email
    assert len(result.addresses) == 1
    assert result.addresses[0].street == "123 Main St"
    assert result.addresses[0].city == "New York"


@pytest.mark.asyncio
async def test_register_user_already_exists(user_service, mock_repository, user_create_dto, user_entity):
    # Setup
    mock_repository.get_by_email.return_value = user_entity

    # Execute & Assert
    with pytest.raises(UserAlreadyExistsError) as excinfo:
        await user_service.register(user_create_dto)
    
    assert user_create_dto.email in str(excinfo.value)
    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_register_with_empty_name_fields(user_service, mock_repository, user_entity):
    # Setup
    dto = UserCreateDTO(
        email="test@example.com",
        password="secure_password123",
        first_name=None,  # Test with None values
        last_name=None
    )
    user_entity.first_name = ""  # Service should convert None to empty string
    user_entity.last_name = ""
    
    mock_repository.get_by_email.return_value = None
    mock_repository.save.return_value = user_entity

    # Execute
    result = await user_service.register(dto)

    # Assert
    assert result.first_name == ""
    assert result.last_name == ""
    
    # Verify the user entity was created correctly
    mock_repository.save.assert_called_once()
    saved_user = mock_repository.save.call_args[0][0]
    assert saved_user.first_name == ""
    assert saved_user.last_name == ""


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_user_with_address(user_service, mock_repository, user_entity_with_address):
    # Setup
    user_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = user_entity_with_address

    # Execute
    result = await user_service.get_user(user_id)

    # Assert
    assert isinstance(result, UserReadDTO)
    assert len(result.addresses) == 1
    assert result.addresses[0].street == "123 Main St"
    assert result.addresses[0].city == "New York"
    assert result.addresses[0].type == AddressType.Home


@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_repository):
    # Setup
    user_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    # Execute & Assert
    with pytest.raises(UserNotFoundError) as excinfo:
        await user_service.get_user(user_id)
    
    assert str(user_id) in str(excinfo.value)
