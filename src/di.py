from kink import di
from taskiq import AsyncBroker
from taskiq_aio_pika import AioPikaBroker

from src.application.services.user_service import UserService
from src.config import Settings
from src.domain.background_task.repositories import BackgroundTaskProcessor
from src.domain.users.repositories import UserRepository
from src.infrastructure.mongodb.config import BeanieClient
from src.infrastructure.mongodb.repositories.user import BeanieUserRepository

from src.observability.logging import AppLogger
from src.presentation.taskiq.app import TaskiqProcessor


def setup_di_container(settings: Settings = None):
    """Initialize the dependency injection container."""
    if settings is None:
        settings = Settings()

    # Register configuration
    di[Settings] = settings

    # Taskiq Broker
    taskiq_broker = AioPikaBroker(settings.taskiq.broker_url)
    di[AsyncBroker] = taskiq_broker

    # Register MongoDB
    di[BeanieClient] = lambda _di: BeanieClient(
        mongo_uri=_di[Settings].mongo.uri, mongo_database=_di[Settings].mongo.database
    )

    # Register repositories
    register_repositories()

    # Register services
    register_services()

    return di


def register_repositories():
    """Register all repositories in the DI container."""
    di[UserRepository] = lambda _di: BeanieUserRepository()


def register_services():
    """Register all application services."""
    di[BackgroundTaskProcessor] = lambda _di: TaskiqProcessor(_di[AsyncBroker])

    di[UserService] = lambda _di: UserService(
        user_repository=_di[UserRepository], task_processor=_di[BackgroundTaskProcessor]
    )


async def handle_startup():
    setup_di_container()

    settings = di[Settings]
    # Initialize logger
    AppLogger(
        service_name=settings.service.name,
        log_level=settings.log_level,
        environment=settings.environment,
        service_version=settings.service.version,
        service_namespace=settings.service.namespace,
    )

    # Initialize Mongo
    await di[BeanieClient].initialize()

    # Start broker
    await di[AsyncBroker].startup()

    # Register background tasks
    await di[BackgroundTaskProcessor].register_tasks()


async def handle_shutdown():
    # Stop broker
    await di[AsyncBroker].shutdown()

    await di[BeanieClient].close()
    # Clear DI container cache
    di.clear_cache()
