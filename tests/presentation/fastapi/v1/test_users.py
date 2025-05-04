import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient

from src.application.dto.user_dto import UserCreateDTO, UserReadDTO
from src.application.services.user_service import UserService
from src.config import Settings, MongoDBSettings
from src.containers import Container
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.infrastructure.mongodb.config import BeanieClient
from src.presentation.fastapi.v1.users import router


@pytest.fixture(scope='session')
def test_settings():
    return Settings(
        mongo=MongoDBSettings(
            uri="mongodb://localhost:27017",
            database="test_db"
        )
    )


@pytest.fixture(scope="session")
async def beanie_client(test_settings):
    mock_client = AsyncMongoMockClient()
    beanie_client = BeanieClient(
        mongo_uri=test_settings.mongo.uri,
        mongo_database=test_settings.mongo.database,
        client=mock_client
    )
    await beanie_client.initialize()
    yield beanie_client
    await beanie_client.close()


@pytest.fixture(scope='session')
def mock_user_service():
    return AsyncMock(spec=UserService)


@pytest.fixture(scope='session')
def app(mock_user_service, beanie_client, test_settings):
    container = Container()
    container.config.from_pydantic(test_settings)
    container.db.override(beanie_client)
    container.user_svc.override(mock_user_service)
    app = FastAPI()
    app.container = container
    app.include_router(router)
    return app


@pytest.fixture(scope='session')
def client(app):
    return TestClient(app)


@pytest.fixture(scope='session')
def user_create_dto():
    return UserCreateDTO(
        email="test@example.com",
        password="secure_password123",
        first_name="John",
        last_name="Doe"
    )


@pytest.fixture(scope='session')
def user_read_dto():
    return UserReadDTO(
        id=uuid.uuid4(),
        email="test@example.com",
        first_name="John",
        last_name="Doe"
    )


@pytest.mark.asyncio
async def test_register_user_success(app, client, mock_user_service, user_create_dto, user_read_dto):
    # Setup
    mock_user_service.register.return_value = user_read_dto

    # Execute
    response = client.post("/", json=user_create_dto.model_dump())

    # Assert
    assert response.status_code == 201
    assert response.json() == user_read_dto.model_dump(mode='json')


@pytest.mark.asyncio
async def test_register_user_already_exists(client, mock_user_service, user_create_dto):
    # Setup
    mock_user_service.register.side_effect = UserAlreadyExistsError(user_create_dto.email)

    # Execute
    response = client.post("/", json=user_create_dto.model_dump())

    # Assert
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_success(client, mock_user_service, user_read_dto):
    # Setup
    mock_user_service.get_user.return_value = user_read_dto

    # Execute
    response = client.get(f"/{user_read_dto.id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == user_read_dto.model_dump(mode='json')


@pytest.mark.asyncio
async def test_get_user_not_found(client, mock_user_service):
    # Setup
    user_id = uuid.uuid4()
    mock_user_service.get_user.side_effect = UserNotFoundError(user_id)

    # Execute
    response = client.get(f"/{user_id}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"] 