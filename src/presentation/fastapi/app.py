from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.presentation.fastapi.v1.router import router as api_v1_router
from ...config import Settings
from ...containers import Container


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    container = Container()
    container.config.from_pydantic(Settings())
    container.init_resources()
    # Initialize database
    await container.db().initialize()
    # Wire the container to the application modules
    container.wire(modules=[
        "src.presentation.fastapi.v1.users",
    ])

    yield

    # Shutdown event

    # Close DB connection
    await container.db().close()


def create_app() -> FastAPI:

    # Create the FastAPI app
    _app = FastAPI(title="DDD FastAPI Application", lifespan=lifespan)
    # Include API router
    _app.include_router(api_v1_router)
    return _app


app = create_app()

__all__ = ("app",)
