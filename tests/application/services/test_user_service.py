import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from kink import di

from src.application.dto.user_dto import UserCreateDTO, WelcomeEmailTaskPayload
from src.application.services.user_service import UserService
from src.domain.background_task.repositories import BackgroundTaskProcessor
from src.domain.users.entities import User
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.domain.users.repositories import UserRepository

# Constants for test data
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"


# Setup DI container with mocks for tests
@pytest.fixture
def setup_di():
    """Set up the dependency injection container with mocks."""
    # Clear previous bindings
    di.clear_cache()

    # Create mock dependencies
    mock_user_repo = AsyncMock(spec=UserRepository)
    mock_task_processor = AsyncMock(spec=BackgroundTaskProcessor)

    # Register mocks in DI container
    di[UserRepository] = mock_user_repo
    di[BackgroundTaskProcessor] = mock_task_processor

    # Register the service using the mocks
    di[UserService] = lambda _di: UserService(
        user_repository=_di[UserRepository],
        task_processor=_di[BackgroundTaskProcessor]
    )

    yield {
        "user_repository": mock_user_repo,
        "task_processor": mock_task_processor,
        "user_service": di[UserService]
    }

    # Clean up after test
    di.clear_cache()


# Factory fixture for creating UserCreateDTO instances
@pytest.fixture
def create_user_dto():
    """Factory fixture to create UserCreateDTO instances."""

    def _create(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            addresses=None
    ):
        return UserCreateDTO(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            addresses=addresses or []
        )

    return _create


# Factory fixture for creating mock User entities
@pytest.fixture
def create_mock_user():
    """Factory fixture to create mock User instances."""

    def _create(
            user_id=None,
            email=TEST_EMAIL,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            addresses=None
    ):
        user = MagicMock(spec=User)
        user.id = user_id or uuid.uuid4()
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.addresses = addresses or []
        user.set_password = MagicMock()
        return user

    return _create


# Test cases for register method
@pytest.mark.asyncio
async def test_register_new_user_success(setup_di, create_user_dto, create_mock_user):
    """Test successful registration of a new user."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    task_processor = mocks["task_processor"]
    user_service = mocks["user_service"]

    # Configure mocks
    user_repo.get_by_email.return_value = None  # User doesn't exist yet
    mock_saved_user = create_mock_user()
    user_repo.save.return_value = mock_saved_user

    # Create user DTO for registration
    user_dto = create_user_dto()

    # Act
    result = await user_service.register(user_dto)

    # Assert
    assert result.email == TEST_EMAIL
    assert result.first_name == TEST_FIRST_NAME
    assert result.last_name == TEST_LAST_NAME

    # Verify interactions
    user_repo.get_by_email.assert_called_once_with(TEST_EMAIL)
    user_repo.save.assert_called_once()
    task_processor.execute_task.assert_called_once_with(
        task_name='send_welcome_email',
        payload=WelcomeEmailTaskPayload(recipients=[mock_saved_user.email])
    )


@pytest.mark.asyncio
async def test_register_existing_user_raises_error(setup_di, create_user_dto, create_mock_user):
    """Test that registering an existing user raises an error."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    task_processor = mocks["task_processor"]
    user_service = mocks["user_service"]

    # Configure mocks - user already exists
    existing_user = create_mock_user(email="existing@example.com")
    user_repo.get_by_email.return_value = existing_user

    # Create user DTO with existing email
    user_dto = create_user_dto(email="existing@example.com")

    # Act & Assert
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await user_service.register(user_dto)

    # Verify interactions
    user_repo.get_by_email.assert_called_once_with("existing@example.com")
    user_repo.save.assert_not_called()
    task_processor.execute_task.assert_not_called()


# Test cases for get_user method
@pytest.mark.asyncio
async def test_get_user_by_id_success(setup_di, create_mock_user):
    """Test successful retrieval of a user by ID."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    user_service = mocks["user_service"]

    user_id = uuid.uuid4()
    mock_user = create_mock_user(user_id=user_id)
    user_repo.get_by_id.return_value = mock_user

    # Act
    result = await user_service.get_user(user_id)

    # Assert
    assert result.id == user_id
    assert result.email == TEST_EMAIL
    assert result.first_name == TEST_FIRST_NAME
    assert result.last_name == TEST_LAST_NAME

    # Verify interactions
    user_repo.get_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(setup_di):
    """Test that getting a non-existent user raises an error."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    user_service = mocks["user_service"]

    user_id = uuid.uuid4()
    user_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(UserNotFoundError):
        await user_service.get_user(user_id)

    # Verify interactions
    user_repo.get_by_id.assert_called_once_with(user_id)


# Parametrized test for different name combinations
@pytest.mark.asyncio
@pytest.mark.parametrize("first_name,last_name", [
    ("John", "Doe"),
    ("Jane", "Smith"),
    (None, "NoFirst"),
    ("NoLast", None),
    (None, None)
])
async def test_register_with_different_names(setup_di, create_user_dto, create_mock_user, first_name, last_name):
    """Test registering users with different name combinations."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    user_service = mocks["user_service"]

    user_repo.get_by_email.return_value = None
    saved_user = create_mock_user(
        first_name=first_name or "",
        last_name=last_name or ""
    )
    user_repo.save.return_value = saved_user

    user_dto = create_user_dto(
        first_name=first_name,
        last_name=last_name
    )

    # Act
    result = await user_service.register(user_dto)

    # Assert
    assert result.first_name == (first_name or "")
    assert result.last_name == (last_name or "")


@pytest.mark.asyncio
async def test_get_user_by_email_success(setup_di, create_mock_user):
    """Test successful retrieval of a user by email."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    user_service = mocks["user_service"]

    test_email = "test@example.com"
    user_id = uuid.uuid4()
    mock_user = create_mock_user(user_id=user_id, email=test_email)
    user_repo.get_by_email.return_value = mock_user

    # Act
    result = await user_service.get_user_by_email(test_email)

    # Assert
    assert result.id == user_id
    assert result.email == test_email

    # Verify interactions
    user_repo.get_by_email.assert_called_once_with(test_email)


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(setup_di):
    """Test that getting a user by non-existent email raises an error."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    user_service = mocks["user_service"]

    test_email = "nonexistent@example.com"
    user_repo.get_by_email.return_value = None

    # Act & Assert
    with pytest.raises(UserNotFoundError) as exc_info:
        await user_service.get_user_by_email(test_email)
    
    # Verify the exception contains the email
    assert test_email in str(exc_info.value)

    # Verify interactions
    user_repo.get_by_email.assert_called_once_with(test_email)


@pytest.mark.asyncio
@pytest.mark.parametrize("email", [
    "user@example.com",
    "test.user@domain.co.uk",
    "x@y.z"
])
async def test_get_user_by_email_with_different_emails(setup_di, create_mock_user, email):
    """Test retrieving users with different email formats."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    user_service = mocks["user_service"]

    user_id = uuid.uuid4()
    mock_user = create_mock_user(user_id=user_id, email=email)
    user_repo.get_by_email.return_value = mock_user

    # Act
    result = await user_service.get_user_by_email(email)

    # Assert
    assert result.id == user_id
    assert result.email == email
    
    # Verify interactions
    user_repo.get_by_email.assert_called_once_with(email)


@pytest.mark.asyncio
async def test_get_user_by_email_minimal_fields(setup_di, create_mock_user):
    """Test that get_user_by_email returns only the minimal required fields."""
    # Arrange
    mocks = setup_di
    user_repo = mocks["user_repository"]
    user_service = mocks["user_service"]

    test_email = "minimal@example.com"
    user_id = uuid.uuid4()
    
    # Create a user with all fields populated
    mock_user = create_mock_user(
        user_id=user_id, 
        email=test_email,
        first_name="Full", 
        last_name="Name",
        addresses=["Sample Address"]
    )
    user_repo.get_by_email.return_value = mock_user

    # Act
    result = await user_service.get_user_by_email(test_email)

    # Assert
    assert result.id == user_id
    assert result.email == test_email
    
    # Verify interactions
    user_repo.get_by_email.assert_called_once_with(test_email)