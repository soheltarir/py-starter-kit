import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from kink import di
from starlette import status

from src.application.dto.user_dto import UserReadDTO
from src.application.services.user_service import UserService
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.presentation.fastapi.v1.users import router

# Create a test app instance
app = FastAPI()
app.include_router(router)


# Setup fixtures
@pytest.fixture
def setup_di():
    """Setup dependency injection container with mocks for testing."""
    # Clear any existing bindings
    di.clear_cache()

    # Create mock for UserService
    mock_user_service = AsyncMock(spec=UserService)

    # Register mock in DI container
    di[UserService] = mock_user_service

    yield mock_user_service

    # Clean up after test
    di.clear_cache()


@pytest.fixture
def test_client(setup_di):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


# Test data fixtures
@pytest.fixture
def sample_user_id():
    """Generate a sample UUID for testing."""
    return uuid.uuid4()


@pytest.fixture
def sample_user_data():
    """Create sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "securepassword",
        "first_name": "Test",
        "last_name": "User",
        "addresses": []
    }


@pytest.fixture
def sample_user_response(sample_user_id):
    """Create a sample user response DTO."""
    return {
        "id": str(sample_user_id),
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "addresses": []
    }


# Tests for register_user endpoint
def test_register_user_success(test_client, setup_di, sample_user_data, sample_user_response):
    """Test successful user registration."""
    # Configure mock to return a successful response
    user_service_mock = setup_di
    user_dto = UserReadDTO(**sample_user_response)
    user_service_mock.register.return_value = user_dto

    # Make the request
    response = test_client.post("/", json=sample_user_data)

    # Assert response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == sample_user_response

    # Verify service was called with correct data
    user_service_mock.register.assert_called_once()


def test_register_user_already_exists(test_client, setup_di, sample_user_data):
    """Test registration with an existing email."""
    # Configure mock to raise UserAlreadyExistsError
    user_service_mock = setup_di
    user_service_mock.register.side_effect = UserAlreadyExistsError("User with this email already exists")

    # Make the request
    response = test_client.post("/", json=sample_user_data)

    # Assert response
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "User with this email already exists" in response.json()["detail"]


def test_register_user_invalid_data(test_client):
    """Test registration with invalid data (missing required fields)."""
    # Make request with missing email
    response = test_client.post("/", json={"password": "test", "first_name": "Test"})

    # Assert response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Tests for get_user endpoint
def test_get_user_success(test_client, setup_di, sample_user_id, sample_user_response):
    """Test successfully getting a user by ID."""
    # Configure mock to return a user
    user_service_mock = setup_di
    user_dto = UserReadDTO(**sample_user_response)
    user_service_mock.get_user.return_value = user_dto

    # Make the request
    response = test_client.get(f"/{sample_user_id}")

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == sample_user_response

    # Verify that service was called with correct ID
    user_service_mock.get_user.assert_called_once_with(sample_user_id)


def test_get_user_not_found(test_client, setup_di, sample_user_id):
    """Test getting a non-existent user."""
    # Configure mock to raise UserNotFoundError
    user_service_mock = setup_di
    user_service_mock.get_user.side_effect = UserNotFoundError(f"User with ID {sample_user_id} not found")

    # Make the request
    response = test_client.get(f"/{sample_user_id}")

    # Assert response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert f"User with ID {sample_user_id} not found" in response.json()["detail"]


def test_get_user_invalid_id(test_client):
    """Test getting a user with an invalid UUID format."""
    # Make request with invalid UUID
    response = test_client.get("/invalid-uuid")

    # Assert response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
