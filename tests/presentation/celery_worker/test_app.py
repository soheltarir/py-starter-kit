from unittest.mock import patch, Mock

import pytest

from src.domain.background_task.adaptor import BackgroundTask
from src.presentation.celery_worker.app import CeleryTaskProcessor


@pytest.fixture
def mock_celery_app():
    """Mock Celery app for testing"""
    mock_app = Mock()
    mock_app.task = Mock()
    mock_app.send_task = Mock()
    mock_app.send_task.return_value.id = "test-task-id"
    return mock_app


@pytest.fixture
def sample_task():
    """Create a sample BackgroundTask for testing"""

    class TestTask(BackgroundTask):
        task_name = "test_task"

        data: str

        async def logic(self):
            return f"Processed {self.data}"

    return TestTask(data="test data")


@pytest.fixture
def disabled_task():
    """Create a disabled BackgroundTask for testing"""

    class DisabledTask(BackgroundTask):
        task_name = "disabled_task"
        enabled = False

        data: str

        async def logic(self):
            return f"Processed {self.data}"

    return DisabledTask(data="test data")


@pytest.fixture
def invalid_task():
    """Create an invalid BackgroundTask without task_name for testing"""

    class InvalidTask(BackgroundTask):
        # No task_name defined

        data: str

        async def logic(self):
            return f"Processed {self.data}"

    return InvalidTask(data="test data")


@pytest.fixture
def celery_processor(mock_celery_app):
    """Create a CeleryTaskProcessor with a mocked Celery app"""
    with patch('src.presentation.celery_worker.app.Celery', return_value=mock_celery_app):
        processor = CeleryTaskProcessor(broker="redis://localhost:6379/0", app_name="test_app")
        return processor


@pytest.mark.asyncio
async def test_init_creates_celery_app():
    """Test that init creates a Celery app with correct parameters"""
    with patch('src.presentation.celery_worker.app.Celery') as mock_celery:
        processor = CeleryTaskProcessor(
            broker="redis://localhost:6379/0",
            app_name="test_app"
        )

        mock_celery.assert_called_once_with(
            "test_app", broker="redis://localhost:6379/0"
        )
        assert processor.celery_app == mock_celery.return_value

        # Check that Celery is configured correctly
        processor.celery_app.conf.update.assert_called_once()
        conf_args = processor.celery_app.conf.update.call_args[1]
        assert conf_args['task_serializer'] == 'pickle'
        assert 'UTC' in conf_args['timezone']


@pytest.mark.asyncio
async def test_create_factory_method():
    """Test the create factory method"""
    with patch('src.presentation.celery_worker.app.CeleryTaskProcessor.__init__', return_value=None) as mock_init:
        with patch('src.presentation.celery_worker.app.CeleryTaskProcessor.register_tasks') as mock_register:
            mock_register.return_value = None

            processor = await CeleryTaskProcessor.create(
                tasks=[],
                broker="redis://localhost:6379/0",
                app_name="test_app"
            )

            mock_init.assert_called_once_with("redis://localhost:6379/0", "test_app")
            mock_register.assert_called_once_with([])
            assert isinstance(processor, CeleryTaskProcessor)


@pytest.mark.asyncio
async def test_register_tasks(celery_processor, sample_task, disabled_task):
    """Test registering tasks with the processor"""
    # Create task classes (not instances)
    task_classes = [sample_task.__class__, disabled_task.__class__]

    await celery_processor.register_tasks(task_classes)

    # Should register only enabled tasks
    assert celery_processor.celery_app.task.call_count == 1

    # Verify the first task was registered correctly
    call_args = celery_processor.celery_app.task.call_args_list[0]
    registered_fn = call_args[0][0]
    registered_name = call_args[1]['name']
    assert registered_name == "test_task"
    assert 'pydantic' in call_args[1]


@pytest.mark.asyncio
async def test_register_invalid_task(celery_processor, invalid_task):
    """Test that registering a task without a name raises ValueError"""
    with pytest.raises(ValueError, match="Task name is not set"):
        await celery_processor.register_tasks([invalid_task.__class__])


@pytest.mark.asyncio
async def test_execute_task(celery_processor, sample_task):
    """Test executing a task"""
    task_id = await celery_processor.execute_task(sample_task)

    # Check that the task was executed with the correct parameters
    celery_processor.celery_app.send_task.assert_called_once_with(
        sample_task.task_name, args=(sample_task,)
    )
    assert task_id == "test-task-id"
