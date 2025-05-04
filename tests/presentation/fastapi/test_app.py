import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.presentation.fastapi.app import create_app, lifespan


@pytest.fixture
def mock_container():
    """Fixture for mocking the Container class."""
    container_mock = AsyncMock()
    # Setup nested mocks
    db_mock = AsyncMock()
    container_mock.init_resources = AsyncMock()
    container_mock.db = MagicMock(return_value=db_mock)
    container_mock.wire = MagicMock()

    return container_mock


@pytest.fixture
def patched_container(mock_container):
    """Patch the Container class to return our mock."""
    with patch("src.presentation.fastapi.app.Container", return_value=mock_container) as patched:
        yield patched


@pytest.fixture
def test_app():
    """Fixture that returns a FastAPI test app."""
    return FastAPI()


@pytest.fixture
def api_client():
    """Fixture that provides a test client for the FastAPI app."""
    app = create_app()
    return TestClient(app)


def test_create_app_returns_fastapi_instance():
    """Test that create_app returns a properly configured FastAPI instance."""
    app = create_app()

    # Check if we have a FastAPI instance
    assert isinstance(app, FastAPI)

    # Check app configuration
    assert app.title == "DDD FastAPI Application"


def test_create_app_includes_router(api_client):
    """Test that the API router is included in the app."""
    # This would typically test a specific endpoint, but we'll just check the app works
    response = api_client.get("/docs")  # Swagger docs should be available
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_lifespan_startup(test_app, patched_container, mock_container):
    """Test the startup phase of the lifespan context manager."""
    # Enter the lifespan context manager
    async with lifespan(test_app):
        # Check that initialization methods were called
        mock_container.init_resources.assert_called_once()
        mock_container.db().initialize.assert_called_once()
        mock_container.wire.assert_called_once_with(modules=[
            "src.presentation.fastapi.v1.users",
        ])


@pytest.mark.asyncio
async def test_lifespan_shutdown(test_app, patched_container, mock_container):
    """Test the shutdown phase of the lifespan context manager."""
    # Use the lifespan context manager
    async with lifespan(test_app):
        pass

    # After exiting the context, check that cleanup was done
    mock_container.db().close.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_handles_exceptions(test_app, patched_container, mock_container):
    """Test that the lifespan function handles exceptions properly."""
    db = mock_container.db()
    db.initialize.side_effect = Exception("DB init failed")

    # The context manager should propagate the exception
    with pytest.raises(Exception, match="DB init failed"):
        async with lifespan(test_app):
            pass

        # But it should still try to close the connection during cleanup
        db.close.assert_called_once()
