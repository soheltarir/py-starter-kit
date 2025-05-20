from unittest.mock import AsyncMock, MagicMock

import pytest
from kink import di

from src.application.dto.user_dto import WelcomeEmailTaskPayload
from src.application.services.user_service import UserService
from src.domain.background_task.repositories import BackgroundTaskProcessor
from src.domain.users.repositories import UserRepository

USER_ID = "test-user-id"

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

    # Configure a mock service to return a mock user
    mock_user = MagicMock()
    mock_user.id = USER_ID
    mock_service = AsyncMock(spec=UserService)
    mock_service.get_user_by_email.return_value = mock_user

    # Register the service using the mocks
    di[UserService] = mock_service

    yield {
        "user_repository": mock_user_repo,
        "task_processor": mock_task_processor,
        "user_service": di[UserService]
    }

    # Clean up after test
    di.clear_cache()


@pytest.mark.asyncio
async def test_send_welcome_email_task(setup_di, capsys):
    """Test that send_welcome_email_task calls the service and logs correctly."""
    # Import the function here to ensure it uses our mocked DI
    from src.presentation.taskiq.tasks.user import send_welcome_email_task

    # Get mock service from fixture
    mock_service = setup_di['user_service']

    # Create test data
    email = "test@example.com"
    user_id = "test-user-id"
    payload = WelcomeEmailTaskPayload(recipients=[email])

    await send_welcome_email_task(payload, svc=mock_service)
    captured = capsys.readouterr()
    assert f"Sending welcome email to {user_id}" in captured.out
