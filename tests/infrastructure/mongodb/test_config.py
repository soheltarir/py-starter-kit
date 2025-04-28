import pytest
from mongomock_motor import AsyncMongoMockClient

from src.infrastructure.mongodb.config import BeanieClient


@pytest.fixture
def beanie_client():
    return BeanieClient(
        mongo_uri="mongodb://localhost:27017",
        mongo_database="test_db"
    )


@pytest.fixture
def mock_motor_client():
    return AsyncMongoMockClient()


async def test_initialize_success(beanie_client, mock_motor_client):
    # Setup
    beanie_client.client = mock_motor_client

    # Execute
    await beanie_client.initialize()

    # Assert
    assert beanie_client.client is not None
    assert beanie_client.db is not None
    assert beanie_client.db.name == "test_db"


async def test_close_success(beanie_client, mock_motor_client):
    # Setup
    beanie_client.client = mock_motor_client
    await beanie_client.initialize()

    # Execute
    await beanie_client.close()

    # Assert
    assert beanie_client.client is None
    assert beanie_client.db is None


async def test_close_without_initialization(beanie_client):
    # Execute
    await beanie_client.close()

    # Assert
    assert beanie_client.client is None
    assert beanie_client.db is None 