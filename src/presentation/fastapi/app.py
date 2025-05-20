from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.presentation.fastapi.v1.router import router as api_v1_router
from ...di import handle_startup, handle_shutdown


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await handle_startup()
    yield
    await handle_shutdown()


def create_app() -> FastAPI:

    # Create the FastAPI app
    _app = FastAPI(title="DDD FastAPI Application", lifespan=lifespan)
    # Include API router
    _app.include_router(api_v1_router)

    return _app


app = create_app()

__all__ = ("app",)
