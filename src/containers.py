from typing import Optional

from dependency_injector import containers, providers

from src.application.services.user_service import UserService
from src.config import Settings
from src.domain.background_task.adaptor import get_background_task_implementations
from src.infrastructure.mongodb.config import BeanieClient
from src.infrastructure.mongodb.repositories.user import BeanieUserRepository
from src.observability.logging import AppLogger
from src.presentation.celery_worker.app import CeleryTaskProcessor


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src"])

    # Configuration.
    config = providers.Configuration(pydantic_settings=[Settings()])

    # Setup logging
    logger = providers.Resource(
        AppLogger,
        config.service.name,
        config.log_level,
        config.environment,
        service_namespace=config.service.namespace,
        service_version=config.service.version,
    )

    # Database clients
    db = providers.Singleton(
        BeanieClient, mongo_uri=config.mongo.uri, mongo_database=config.mongo.database
    )

    user_repository = providers.Factory(BeanieUserRepository)

    background_tasks = providers.Resource(get_background_task_implementations)

    task_processor = providers.Resource(
        CeleryTaskProcessor.create,
        tasks=background_tasks,
        app_name=config.service.name,
        broker=config.celery.broker,
    )

    # Application Services
    user_svc = providers.Factory(
        UserService,
        user_repository=user_repository,
        task_processor=task_processor,
    )


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    global _container
    if _container is None:
        _container = Container()
    return _container


__all__ = (
    "Container",
    "get_container",
)
