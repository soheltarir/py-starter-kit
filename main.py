import logging
import sys

import asyncclick as click
import structlog
import uvicorn
from kink import di
from uvicorn.config import LOGGING_CONFIG

from src.config import Settings

logger = structlog.get_logger()


def configure_uvicorn_logging():
    # Remove default uvicorn logging configuration
    LOGGING_CONFIG.clear()
    logging.getLogger("uvicorn").handlers.clear()

@click.command()
@click.option("--host", default="0.0.0.0", help="Host to run the server on")
@click.option("--port", default=5000, help="Port to run the server on")
@click.option("--workers", default=1, help="Number of workers to run the server with")
async def run_rest_server(host: str, port: int, workers: int):
    try:
        configure_uvicorn_logging()
        settings = di[Settings]

        config = uvicorn.Config(
            app="src.presentation.fastapi.app:app",
            host=host, port=port,
            log_config=None,    # Disable uvicorn default logging
            log_level=settings.log_level,
            access_log=False,
            reload=True if settings.environment == "development" else False,
            workers=workers
        )

        server = uvicorn.Server(config)
        await server.serve()

    except Exception as e:
        logger.error("Failed to start uvicorn server", exc_info=e)
        sys.exit(1)


@click.command()
async def run_celery_worker():
    container = get_container()
    await container.init_resources()
    celery_processor = await container.task_processor()
    celery_app = celery_processor.celery_app
    celery_app.worker_main(["worker", "-l", "info"])

@click.group()
def cli():
    pass


cli.add_command(run_rest_server, name="run_rest_server")
cli.add_command(run_celery_worker, name="run_celery_worker")


if __name__ == "__main__":
    cli()
