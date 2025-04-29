import logging
import sys

import click
import structlog
import uvicorn
from uvicorn.config import LOGGING_CONFIG

from src.containers import get_container

logger = structlog.get_logger()


def configure_uvicorn_logging():
    # Remove default uvicorn logging configuration
    LOGGING_CONFIG.clear()
    logging.getLogger("uvicorn").handlers.clear()

@click.command()
@click.option("--host", default="0.0.0.0", help="Host to run the server on")
@click.option("--port", default=5000, help="Port to run the server on")
@click.option("--workers", default=1, help="Number of workers to run the server with")
def run_rest_server(host: str, port: int, workers: int):
    try:
        configure_uvicorn_logging()
        container = get_container()

        config = uvicorn.Config(
            app="src.presentation.fastapi.app:app",
            host=host, port=port,
            log_config=None,    # Disable uvicorn default logging
            log_level=container.config.log_level(),
            access_log=False,
            reload=True if container.config.environment() == "development" else False,
            workers=workers
        )

        server = uvicorn.Server(config)
        server.run()

    except Exception as e:
        logger.error("Failed to start uvicorn server", exc_info=e)
        sys.exit(1)


@click.group()
def cli():
    pass


cli.add_command(run_rest_server, name="run_rest_server")


if __name__ == "__main__":
    cli()
