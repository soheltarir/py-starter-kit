import uuid
from unittest.mock import AsyncMock

import pytest
from mongomock_motor import AsyncMongoMockClient
from pydantic import EmailStr

from src.domain.users.entities import User
from src.infrastructure.mongodb.config import BeanieClient
from src.infrastructure.mongodb.repositories.user import BeanieUserRepository


@pytest.fixture(scope="session")
async def beanie_client():
    mock_client = AsyncMongoMockClient()
    beanie_client = BeanieClient(
        mongo_uri="mongodb://localhost:27017",
        mongo_database="test_db",
        client=mock_client
    )
    await beanie_client.initialize()
    yield beanie_client
    await beanie_client.close()


@pytest.fixture
def repository(beanie_client):
    return BeanieUserRepository()


@pytest.fixture
def user_entity():
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        first_name="John",
        last_name="Doe"
    )
    user.set_password("secure_password123")
    return user


async def test_save_user(repository, user_entity):
    # Execute
    saved_user = await repository.save(user_entity)

    # Assert
    assert saved_user.id == user_entity.id
    assert saved_user.email == user_entity.email
    assert saved_user.first_name == user_entity.first_name
    assert saved_user.last_name == user_entity.last_name
    assert saved_user.password_hash == user_entity.password_hash


async def test_get_user_by_id(repository, user_entity):
    # Setup
    await repository.save(user_entity)

    # Execute
    found_user = await repository.get_by_id(user_entity.id)

    # Assert
    assert found_user is not None
    assert found_user.id == user_entity.id
    assert found_user.email == user_entity.email
    assert found_user.first_name == user_entity.first_name
    assert found_user.last_name == user_entity.last_name


async def test_get_user_by_id_not_found(repository):
    # Execute
    found_user = await repository.get_by_id(uuid.uuid4())

    # Assert
    assert found_user is None


async def test_get_user_by_email(repository, user_entity):
    # Setup
    await repository.save(user_entity)

    # Execute
    found_user = await repository.get_by_email(user_entity.email)

    # Assert
    assert found_user is not None
    assert found_user.id == user_entity.id
    assert found_user.email == user_entity.email
    assert found_user.first_name == user_entity.first_name
    assert found_user.last_name == user_entity.last_name


async def test_get_user_by_email_not_found(repository):
    # Execute
    found_user = await repository.get_by_email("nonexistent@example.com")

    # Assert
    assert found_user is None 