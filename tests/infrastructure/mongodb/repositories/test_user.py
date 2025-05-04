import uuid

import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient

from src.domain.users.entities import User
from src.infrastructure.mongodb.config import BeanieClient
from src.infrastructure.mongodb.repositories.user import BeanieUserRepository


@pytest.fixture(scope="session")
def mock_mongo_client():
    return AsyncMongoMockClient()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def repository(mock_mongo_client):
    # Initialise mock beanie client
    beanie_client = BeanieClient(
        mongo_uri="mongodb://localhost:27017",
        mongo_database="test_db",
        client=mock_mongo_client
    )
    await beanie_client.initialize()
    yield BeanieUserRepository()


@pytest.fixture
def user_entity():
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        first_name="John",
        last_name="Doe"
    )
    user.set_password("secure_password123")
    return user


@pytest.mark.asyncio
async def test_save_user(repository, user_entity):
    # Execute
    saved_user = await repository.save(user_entity)

    # Assert
    assert saved_user.id == user_entity.id
    assert saved_user.email == user_entity.email
    assert saved_user.first_name == user_entity.first_name
    assert saved_user.last_name == user_entity.last_name
    assert saved_user.password_hash == user_entity.password_hash


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(repository):
    # Execute
    found_user = await repository.get_by_id(uuid.uuid4())

    # Assert
    assert found_user is None


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(repository):
    # Execute
    found_user = await repository.get_by_email("nonexistent@example.com")

    # Assert
    assert found_user is None 